import 'server-only';
import { getBackendUrl } from './backendUrl';

type ProxyOptions = {
  method?: string;
  body?: BodyInit | null;
  headers?: Record<string, string>;
  timeoutMs?: number;
  forwardIdempotencyKey?: boolean;
};

const failure = (status: number, error: string) => Response.json({ success: false, error }, {
  status, headers: { 'Cache-Control': 'private, no-store' },
});

/** For fixed application routes only. Identity is verified by Railway. */
export async function proxyToBackend(request: Request, path: string, options: ProxyOptions = {}): Promise<Response> {
  const authorization = request.headers.get('authorization') || '';
  if (!/^Bearer\s+\S+$/i.test(authorization) || /^Bearer\s+test$/i.test(authorization)) {
    return failure(401, 'Please sign in to continue.');
  }
  try {
    const base = new URL(getBackendUrl());
    const local = ['localhost', '127.0.0.1', '[::1]'].includes(base.hostname);
    if ((base.protocol !== 'https:' && !(process.env.NODE_ENV !== 'production' && local && base.protocol === 'http:')) ||
        base.username || base.password || base.search || base.hash || base.pathname !== '/') {
      return failure(503, 'The service is temporarily unavailable. Please retry.');
    }
    // A route handler chooses this path; request URL/Host/forwarded headers do
    // not influence the destination. Reject path forms that could change it.
    if (!path.startsWith('/api/') || /[\\#]/.test(path) || /(^|\/)\.\.(\/|\?|$)/.test(path)) {
      return failure(503, 'The service is temporarily unavailable. Please retry.');
    }
    const target = new URL(path, base);
    if (target.origin !== base.origin) return failure(503, 'The service is temporarily unavailable. Please retry.');
    const method = (options.method || request.method).toUpperCase();
    const headers = new Headers({ Authorization: authorization, Accept: 'application/json' });
    const contentType = options.headers?.['Content-Type'] || options.headers?.['content-type'] || request.headers.get('content-type');
    if (contentType) headers.set('Content-Type', contentType);
    if (options.forwardIdempotencyKey) {
      const key = request.headers.get('Idempotency-Key');
      if (key && /^[a-zA-Z0-9:_-]{8,200}$/.test(key)) headers.set('Idempotency-Key', key);
    }
    // Never forward cookies, forwarded-host, UID, role or Admin assertion headers.
    const body = ['GET', 'HEAD'].includes(method) ? undefined :
      options.body !== undefined ? options.body : await request.arrayBuffer();
    if (body instanceof FormData) headers.delete('Content-Type');
    const response = await fetch(target.toString(), {
      method, headers, body, cache: 'no-store', redirect: 'manual',
      signal: AbortSignal.timeout(options.timeoutMs ?? 50_000),
    });
    if (response.status >= 300 && response.status < 400) {
      return failure(502, 'The service returned an unexpected redirect. Please retry.');
    }
    const responseType = response.headers.get('content-type') || '';
    if (!responseType.toLowerCase().includes('application/json')) {
      return failure(502, 'The service returned an unexpected response. Please retry.');
    }
    const payload = await response.json();
    return Response.json(payload, { status: response.status, headers: { 'Cache-Control': 'private, no-store' } });
  } catch (error) {
    const timeout = error instanceof Error && ['TimeoutError', 'AbortError'].includes(error.name);
    return failure(timeout ? 504 : 503, timeout
      ? 'The request timed out. Your changes may have been saved; retry to confirm.'
      : 'The service is temporarily unavailable. Your changes may have been saved; retry to confirm.');
  }
}
