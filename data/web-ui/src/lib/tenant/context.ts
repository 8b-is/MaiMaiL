export interface TenantBranding {
  displayName: string;
  primaryColor: string;
}

export interface TenantContext {
  domain: string;
  tenantId?: string;
  branding: TenantBranding;
  config: Record<string, string>;
}

type TenantResolverHook = (domain: string) => Partial<TenantContext> | undefined;

declare global {
  interface Window {
    __MMAIL_TENANT_CONFIG__?: Record<string, Partial<TenantContext>>;
    __MMAIL_TENANT_RESOLVER__?: TenantResolverHook;
  }
}

const DEFAULT_BRANDING: TenantBranding = {
  displayName: 'MaiMaiL',
  primaryColor: '#2563eb',
};

function normalizeDomain(host: string): string {
  return host.split(':')[0].trim().toLowerCase();
}

export function buildTenantContext(domain: string): TenantContext {
  const normalizedDomain = normalizeDomain(domain || 'localhost');
  const fromConfig = typeof window !== 'undefined' ? window.__MMAIL_TENANT_CONFIG__?.[normalizedDomain] : undefined;
  const fromResolver = typeof window !== 'undefined' ? window.__MMAIL_TENANT_RESOLVER__?.(normalizedDomain) : undefined;
  const merged = { ...fromConfig, ...fromResolver };

  return {
    domain: normalizedDomain,
    tenantId: merged.tenantId,
    branding: {
      displayName: merged.branding?.displayName || normalizedDomain,
      primaryColor: merged.branding?.primaryColor || DEFAULT_BRANDING.primaryColor,
    },
    config: merged.config || {},
  };
}

export function getTenantContext(): TenantContext {
  if (typeof window === 'undefined') {
    return {
      domain: 'localhost',
      branding: DEFAULT_BRANDING,
      config: {},
    };
  }

  return buildTenantContext(window.location.host);
}

export function applyTenantBranding(context: TenantContext): void {
  if (typeof document === 'undefined') {
    return;
  }

  document.documentElement.style.setProperty('--tenant-primary-color', context.branding.primaryColor);
}
