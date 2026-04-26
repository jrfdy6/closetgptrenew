const DEFAULT_DEVELOPMENT_BACKEND_URL = 'http://localhost:8080';

function normalizeBackendUrl(url: string): string {
  const trimmed = url.replace(/\/+$/, '');
  return trimmed.endsWith('/api') ? trimmed.slice(0, -4) : trimmed;
}

export function getBackendUrl(): string {
  const configuredUrl =
    process.env.BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_API_URL;

  if (configuredUrl) {
    return normalizeBackendUrl(configuredUrl);
  }

  if (process.env.NODE_ENV === 'development') {
    return DEFAULT_DEVELOPMENT_BACKEND_URL;
  }

  throw new Error(
    'Backend URL is not configured. Set BACKEND_URL, NEXT_PUBLIC_BACKEND_URL, or NEXT_PUBLIC_API_URL.'
  );
}
