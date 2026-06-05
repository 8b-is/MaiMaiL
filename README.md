# maimail: dockerized - 🐮 + 🐋 = 💕

[![Translation status](https://translate.maimail.email/widgets/maimail-dockerized/-/translation/svg-badge.svg)](https://translate.maimail.email/engage/maimail-dockerized/)
[![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/maimail_email.svg?style=social&label=Follow%20%40maimail_email)](https://twitter.com/maimail_email)
![Mastodon Follow](https://img.shields.io/mastodon/follow/109388212176073348?domain=https%3A%2F%2Fmaimail.social&label=Follow%20%40doncow%40maimail.social&link=https%3A%2F%2Fmaimail.social%2F%40doncow)

**Current Version:** 0.1.0

## Multi-tenant domain-keyed architecture

- Single server, multiple domains.
- Tenant context is resolved from incoming `Host`/domain.
- The dashboard now has tenant context extension points for branding and runtime config hooks (`window.__MMAIL_TENANT_CONFIG__` and `window.__MMAIL_TENANT_RESOLVER__`).
- Requests include tenant metadata headers (`X-Tenant-Domain`, `X-Tenant-Id`) for downstream isolation controls.

## Rust reverse proxy (`/rust-proxy`)

- Domain-keyed reverse proxy implemented in stable Rust.
- Supports HTTP by default and optional HTTPS (set `MMAIL_PROXY_TLS_CERT` + `MMAIL_PROXY_TLS_KEY`).
- Tenant-aware routing:
  - resolves tenant by domain/host,
  - supports per-tenant backend and route-prefix overrides,
  - injects tenant headers for downstream services,
  - logs host/tenant/backend/status context for each proxied request.
- Config sources:
  - file: `rust-proxy/config/proxy.toml` (default),
  - env override: `MMAIL_PROXY_CONFIG`,
  - server/env overrides: `MMAIL_PROXY_BIND`, `MMAIL_PROXY_MODE`, `MMAIL_PROXY_DEFAULT_BACKEND`, `MMAIL_PROXY_LOG_LEVEL`, `MMAIL_PROXY_TIMEOUT_SECS`, `MMAIL_PROXY_TRUST_X_FORWARDED_HOST`, `MMAIL_PROXY_TLS_CERT`, `MMAIL_PROXY_TLS_KEY`.

## Repository management script (`/scripts/manage.sh`)

```bash
# show help
./scripts/manage.sh --help

# clean artifacts
./scripts/manage.sh clean

# build (default dev) or release
./scripts/manage.sh build
./scripts/manage.sh build release

# run modes
./scripts/manage.sh run dev
./scripts/manage.sh run prod
./scripts/manage.sh run proxy-dev
./scripts/manage.sh run proxy-prod
./scripts/manage.sh run web-dev

# release build
./scripts/manage.sh release

# semantic versioning
./scripts/manage.sh version bump
./scripts/manage.sh version minor
./scripts/manage.sh version major
```

`manage.sh` prefers `pnpm` for Node-based tasks and falls back to `npm` only when `pnpm` is unavailable.


## Want to support maimail?

Please [consider a support contract with Servercow](https://www.servercow.de/maimail?lang=en#support) to support further development. _We_ support _you_ while _you_ support _us_. :)

You can also [get a SAL](https://www.servercow.de/maimail?lang=en#sal) which is a one-time payment with no liabilities or returning fees.

Or just spread the word: moo.

## Many thanks to our GitHub Sponsors ❤️
A big thank you to everyone supporting us on GitHub Sponsors—your contributions mean the world to us! Special thanks to the following amazing supporters:

### 100$/Month Sponsors
  <a href="https://www.colba.net/" target=_blank><img
    src="https://avatars.githubusercontent.com/u/204464723" height="58"
  /></a>
  <a href="https://www.maehdros.com/" target=_blank><img
    src="https://avatars.githubusercontent.com/u/173894712" height="58"
  /></a>

### 50$/Month Sponsors
  <a href="https://github.com/vnukhr" target=_blank><img
    src="https://avatars.githubusercontent.com/u/7805987?s=52&v=4" height="58"
  /></a>

## Info, documentation and support

Please see [the official documentation](https://docs.maimail.email/) for installation and support instructions. 🐄

🐛 **If you found a critical security issue, please mail us to [info at servercow.de](mailto:info@servercow.de).**

## Cowmunity

[maimail community](https://community.maimail.email)

[Telegram maimail channel](https://telegram.me/maimail)

[Telegram maimail Off-Topic channel](https://t.me/maimailOfftopic)

[Official 𝕏 (Twitter) Account](https://twitter.com/maimail_email)

[Official Mastodon Account](https://maimail.social/@doncow)

Telegram desktop clients are available for [multiple platforms](https://desktop.telegram.org). You can search the groups history for keywords.

## Misc

**Important**: maimail makes use of various open-source software. Please assure you agree with their license before using maimail.
Any part of maimail itself is released under **GNU General Public License, Version 3**.

maimail is a registered word mark of The Infrastructure Company GmbH, Parkstr. 42, 47877 Willich, Germany.

The project is managed and maintained by The Infrastructure Company GmbH.

Originated from @andryyy (André)
