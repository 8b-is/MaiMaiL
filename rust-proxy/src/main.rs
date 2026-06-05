use std::{
    collections::HashMap,
    env,
    net::SocketAddr,
    path::Path,
    sync::Arc,
    time::{Duration, Instant},
};

use anyhow::{Context, Result};
use axum::{
    body::{to_bytes, Body},
    extract::State,
    http::{header::HOST, HeaderMap, HeaderName, HeaderValue, Request, Response, StatusCode},
    routing::any,
    Router,
};
use reqwest::Client;
use serde::Deserialize;
use tracing::{error, info, warn};
use tracing_subscriber::{fmt, EnvFilter};

const MAX_BODY_BYTES: usize = 10 * 1024 * 1024;

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
struct ProxyConfig {
    server: ServerConfig,
    tenants: Vec<TenantConfig>,
}

impl Default for ProxyConfig {
    fn default() -> Self {
        Self {
            server: ServerConfig::default(),
            tenants: Vec::new(),
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
struct ServerConfig {
    bind: String,
    mode: String,
    default_backend: String,
    log_level: String,
    request_timeout_secs: u64,
    trust_x_forwarded_host: bool,
    tls_cert_path: Option<String>,
    tls_key_path: Option<String>,
}

impl Default for ServerConfig {
    fn default() -> Self {
        Self {
            bind: "0.0.0.0:8088".to_string(),
            mode: "development".to_string(),
            default_backend: "http://127.0.0.1:8080".to_string(),
            log_level: "info".to_string(),
            request_timeout_secs: 30,
            trust_x_forwarded_host: true,
            tls_cert_path: None,
            tls_key_path: None,
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
struct TenantConfig {
    id: Option<String>,
    domain: String,
    backend: Option<String>,
    routes: HashMap<String, String>,
    branding: Option<TenantBranding>,
}

impl Default for TenantConfig {
    fn default() -> Self {
        Self {
            id: None,
            domain: String::new(),
            backend: None,
            routes: HashMap::new(),
            branding: None,
        }
    }
}

#[derive(Debug, Clone, Deserialize)]
#[serde(default)]
struct TenantBranding {
    display_name: Option<String>,
    primary_color: Option<String>,
}

impl Default for TenantBranding {
    fn default() -> Self {
        Self {
            display_name: None,
            primary_color: None,
        }
    }
}

#[derive(Clone)]
struct AppState {
    config: Arc<ProxyConfig>,
    client: Client,
}

#[tokio::main]
async fn main() -> Result<()> {
    let config_path = env::var("MMAIL_PROXY_CONFIG")
        .unwrap_or_else(|_| "rust-proxy/config/proxy.toml".to_string());
    let mut config = load_config(&config_path)
        .await
        .with_context(|| format!("failed to load config from {config_path}"))?;

    apply_env_overrides(&mut config);
    init_tracing(&config.server.log_level)?;

    let addr: SocketAddr = config
        .server
        .bind
        .parse()
        .with_context(|| format!("invalid bind address: {}", config.server.bind))?;

    let client = Client::builder()
        .timeout(Duration::from_secs(config.server.request_timeout_secs))
        .build()
        .context("failed to initialize HTTP client")?;

    let shared_state = Arc::new(AppState {
        config: Arc::new(config.clone()),
        client,
    });

    let app = Router::new()
        .route("/", any(proxy_handler))
        .route("/*path", any(proxy_handler))
        .with_state(shared_state);

    info!(
        mode = %config.server.mode,
        bind = %addr,
        tenants = config.tenants.len(),
        "starting maimail rust proxy"
    );

    let tls_enabled = match (&config.server.tls_cert_path, &config.server.tls_key_path) {
        (Some(cert), Some(key)) if !cert.is_empty() && !key.is_empty() => true,
        _ => false,
    };

    if tls_enabled {
        let cert_path = config.server.tls_cert_path.clone().unwrap();
        let key_path = config.server.tls_key_path.clone().unwrap();
        info!(cert = %cert_path, key = %key_path, "starting in https mode");
        let tls = axum_server::tls_rustls::RustlsConfig::from_pem_file(cert_path, key_path)
            .await
            .context("failed to load TLS certificate/key")?;
        axum_server::bind_rustls(addr, tls)
            .serve(app.into_make_service())
            .await
            .context("HTTPS server failed")?;
    } else {
        if config.server.mode.eq_ignore_ascii_case("production") {
            warn!("production mode is active without TLS; terminate HTTPS upstream or configure cert/key");
        }
        let listener = tokio::net::TcpListener::bind(addr)
            .await
            .context("failed to bind TCP listener")?;
        axum::serve(listener, app)
            .await
            .context("HTTP server failed")?;
    }

    Ok(())
}

async fn proxy_handler(State(state): State<Arc<AppState>>, req: Request<Body>) -> Response<Body> {
    let started_at = Instant::now();
    let (parts, body) = req.into_parts();
    let request_method = parts.method.clone();
    let request_path = parts
        .uri
        .path_and_query()
        .map(|pq| pq.as_str())
        .unwrap_or(parts.uri.path())
        .to_string();

    let incoming_host =
        get_effective_host(&parts.headers, state.config.server.trust_x_forwarded_host)
            .unwrap_or_else(|| "unknown".to_string());
    let tenant = resolve_tenant(&state.config.tenants, &incoming_host);

    let tenant_domain = tenant
        .map(|t| t.domain.clone())
        .unwrap_or_else(|| incoming_host.clone());
    let backend = select_backend(
        &state.config.server.default_backend,
        tenant,
        parts.uri.path(),
    );
    let upstream_url = build_upstream_url(&backend, &request_path);

    let body_bytes = match to_bytes(body, MAX_BODY_BYTES).await {
        Ok(bytes) => bytes,
        Err(err) => {
            warn!(error = %err, host = %incoming_host, "request body exceeded limit");
            return status_response(StatusCode::PAYLOAD_TOO_LARGE, "request body too large");
        }
    };

    let mut upstream = state.client.request(request_method.clone(), &upstream_url);
    upstream = copy_request_headers(upstream, &parts.headers);

    upstream = upstream.header("x-tenant-domain", &tenant_domain);
    if let Some(id) = tenant.and_then(|t| t.id.clone()) {
        upstream = upstream.header("x-tenant-id", id);
    }
    if let Some(display_name) = tenant
        .and_then(|t| t.branding.as_ref())
        .and_then(|b| b.display_name.clone())
    {
        upstream = upstream.header("x-tenant-branding", display_name);
    }

    let upstream_response = match upstream.body(body_bytes).send().await {
        Ok(resp) => resp,
        Err(err) => {
            error!(
                error = %err,
                host = %incoming_host,
                backend = %backend,
                path = %request_path,
                "failed to contact upstream"
            );
            return status_response(StatusCode::BAD_GATEWAY, "upstream request failed");
        }
    };

    let status = upstream_response.status();
    let response_headers = upstream_response.headers().clone();
    let response_body = match upstream_response.bytes().await {
        Ok(bytes) => bytes,
        Err(err) => {
            error!(error = %err, host = %incoming_host, path = %request_path, "failed reading upstream response body");
            return status_response(StatusCode::BAD_GATEWAY, "upstream response read failed");
        }
    };

    let mut response_builder = Response::builder().status(status);
    if let Some(headers) = response_builder.headers_mut() {
        copy_response_headers(headers, &response_headers);
    }

    let response = response_builder
        .body(Body::from(response_body))
        .unwrap_or_else(|_| {
            status_response(StatusCode::INTERNAL_SERVER_ERROR, "response build failed")
        });

    info!(
        host = %incoming_host,
        tenant = %tenant_domain,
        tenant_id = %tenant.and_then(|t| t.id.clone()).unwrap_or_default(),
        method = %request_method,
        path = %request_path,
        backend = %backend,
        status = %status.as_u16(),
        elapsed_ms = %started_at.elapsed().as_millis(),
        "proxied request"
    );

    response
}

async fn load_config(path: &str) -> Result<ProxyConfig> {
    if Path::new(path).exists() {
        let raw = tokio::fs::read_to_string(path)
            .await
            .with_context(|| format!("unable to read config file: {path}"))?;
        let parsed: ProxyConfig = toml::from_str(&raw).context("invalid TOML configuration")?;
        Ok(parsed)
    } else {
        Ok(ProxyConfig::default())
    }
}

fn apply_env_overrides(config: &mut ProxyConfig) {
    if let Ok(value) = env::var("MMAIL_PROXY_BIND") {
        config.server.bind = value;
    }
    if let Ok(value) = env::var("MMAIL_PROXY_MODE") {
        config.server.mode = value;
    }
    if let Ok(value) = env::var("MMAIL_PROXY_DEFAULT_BACKEND") {
        config.server.default_backend = value;
    }
    if let Ok(value) = env::var("MMAIL_PROXY_LOG_LEVEL") {
        config.server.log_level = value;
    }
    if let Ok(value) = env::var("MMAIL_PROXY_TIMEOUT_SECS") {
        if let Ok(timeout) = value.parse::<u64>() {
            config.server.request_timeout_secs = timeout;
        }
    }
    if let Ok(value) = env::var("MMAIL_PROXY_TRUST_X_FORWARDED_HOST") {
        if let Ok(parsed) = value.parse::<bool>() {
            config.server.trust_x_forwarded_host = parsed;
        }
    }
    if let Ok(value) = env::var("MMAIL_PROXY_TLS_CERT") {
        config.server.tls_cert_path = Some(value);
    }
    if let Ok(value) = env::var("MMAIL_PROXY_TLS_KEY") {
        config.server.tls_key_path = Some(value);
    }
}

fn init_tracing(level: &str) -> Result<()> {
    let filter = EnvFilter::try_new(level).unwrap_or_else(|_| EnvFilter::new("info"));
    let _ = fmt().with_env_filter(filter).with_target(false).try_init();
    Ok(())
}

fn get_effective_host(headers: &HeaderMap, trust_x_forwarded_host: bool) -> Option<String> {
    if trust_x_forwarded_host {
        if let Some(value) = headers.get("x-forwarded-host").and_then(header_to_string) {
            let normalized = normalize_host(&value);
            if !normalized.is_empty() {
                return Some(normalized);
            }
        }
    }

    headers
        .get(HOST)
        .and_then(header_to_string)
        .map(|value| normalize_host(&value))
        .filter(|host| !host.is_empty())
}

fn header_to_string(value: &HeaderValue) -> Option<String> {
    value.to_str().ok().map(|s| s.to_string())
}

fn normalize_host(raw_host: &str) -> String {
    let first = raw_host
        .split(',')
        .next()
        .unwrap_or_default()
        .trim()
        .to_ascii_lowercase();

    if first.starts_with('[') {
        if let Some(end) = first.find(']') {
            return first[1..end].to_string();
        }
    }

    if let Some((candidate, port)) = first.rsplit_once(':') {
        if !candidate.contains(':') && port.chars().all(|c| c.is_ascii_digit()) {
            return candidate.to_string();
        }
    }

    first
}

fn resolve_tenant<'a>(tenants: &'a [TenantConfig], host: &str) -> Option<&'a TenantConfig> {
    tenants
        .iter()
        .find(|tenant| tenant.domain.eq_ignore_ascii_case(host))
}

fn select_backend(default_backend: &str, tenant: Option<&TenantConfig>, path: &str) -> String {
    if let Some(tenant) = tenant {
        if !tenant.routes.is_empty() {
            if let Some((_, backend)) = tenant
                .routes
                .iter()
                .filter(|(prefix, _)| path.starts_with(prefix.as_str()))
                .max_by_key(|(prefix, _)| prefix.len())
            {
                return backend.clone();
            }
        }
        if let Some(backend) = tenant.backend.as_ref() {
            return backend.clone();
        }
    }

    default_backend.to_string()
}

fn build_upstream_url(backend: &str, path_and_query: &str) -> String {
    let backend = backend.trim_end_matches('/');
    if path_and_query.starts_with('/') {
        format!("{backend}{path_and_query}")
    } else {
        format!("{backend}/{path_and_query}")
    }
}

fn copy_request_headers(
    mut builder: reqwest::RequestBuilder,
    incoming: &HeaderMap,
) -> reqwest::RequestBuilder {
    for (name, value) in incoming {
        if should_skip_request_header(name) {
            continue;
        }
        builder = builder.header(name, value);
    }
    builder
}

fn copy_response_headers(outgoing: &mut HeaderMap, incoming: &HeaderMap) {
    for (name, value) in incoming {
        if should_skip_response_header(name) {
            continue;
        }
        outgoing.append(name, value.clone());
    }
}

fn should_skip_request_header(name: &HeaderName) -> bool {
    let lower = name.as_str().to_ascii_lowercase();
    lower == "host" || HOP_BY_HOP_HEADERS.contains(&lower.as_str())
}

fn should_skip_response_header(name: &HeaderName) -> bool {
    let lower = name.as_str().to_ascii_lowercase();
    HOP_BY_HOP_HEADERS.contains(&lower.as_str())
}

fn status_response(status: StatusCode, message: &'static str) -> Response<Body> {
    Response::builder()
        .status(status)
        .body(Body::from(message))
        .unwrap_or_else(|_| Response::new(Body::from("internal error")))
}

const HOP_BY_HOP_HEADERS: [&str; 8] = [
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
];

#[cfg(test)]
mod tests {
    use super::{build_upstream_url, normalize_host, select_backend, TenantConfig};
    use std::collections::HashMap;

    #[test]
    fn normalizes_host_with_port_and_case() {
        assert_eq!(
            normalize_host("Tenant.Example.com:8443"),
            "tenant.example.com"
        );
        assert_eq!(normalize_host("tenant.example.com"), "tenant.example.com");
        assert_eq!(
            normalize_host("tenant.example.com:443, proxy.example.com"),
            "tenant.example.com"
        );
    }

    #[test]
    fn route_prefix_overrides_tenant_backend() {
        let mut tenant = TenantConfig::default();
        tenant.backend = Some("http://tenant-backend".to_string());
        tenant.routes = HashMap::from([
            ("/api".to_string(), "http://api-backend".to_string()),
            ("/api/v2".to_string(), "http://api-v2-backend".to_string()),
        ]);

        assert_eq!(
            select_backend("http://default", Some(&tenant), "/api/health"),
            "http://api-backend"
        );
        assert_eq!(
            select_backend("http://default", Some(&tenant), "/api/v2/users"),
            "http://api-v2-backend"
        );
        assert_eq!(
            select_backend("http://default", Some(&tenant), "/mail"),
            "http://tenant-backend"
        );
    }

    #[test]
    fn builds_upstream_url_without_double_slashes() {
        assert_eq!(
            build_upstream_url(
                "http://127.0.0.1:8080/",
                "/json_api.php?query=get/domain/all"
            ),
            "http://127.0.0.1:8080/json_api.php?query=get/domain/all"
        );
    }
}
