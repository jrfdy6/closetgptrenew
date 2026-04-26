const DEFAULT_DEVELOPMENT_BACKEND_URL = 'http://localhost:8080';

function normalizeBackendUrl(url: string): string {
  const trimmed = url.replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed.slice(0, -4) : trimmed;
}

export function getConfiguredPublicBackendUrl(): string | null {
  const configuredUrl =
    process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;

  return configuredUrl ? normalizeBackendUrl(configuredUrl) : null;
}

export function getPublicBackendUrl(): string {
  const configuredUrl = getConfiguredPublicBackendUrl();
  if (configuredUrl) {
    return configuredUrl;
  }

  return process.env.NODE_ENV === 'development'
    ? DEFAULT_DEVELOPMENT_BACKEND_URL
    : '';
}

export function buildPublicBackendUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const baseUrl = getPublicBackendUrl();

  return baseUrl ? `${baseUrl}${normalizedPath}` : normalizedPath;
}
