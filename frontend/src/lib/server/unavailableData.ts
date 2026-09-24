import 'server-only';

/** Unsupported analytics must not masquerade as a measured empty result. */
export function unavailableData(request: Request, label: string): Response {
  const authorization = request.headers.get('authorization') || '';
  const authenticated = /^Bearer\s+\S+$/i.test(authorization) && !/^Bearer\s+test$/i.test(authorization);
  return Response.json({ success: false, available: false, error: authenticated
    ? `${label} is currently unavailable. Your saved wardrobe is unchanged.`
    : 'Please sign in to continue.' }, { status: authenticated ? 503 : 401, headers: { 'Cache-Control': 'private, no-store' } });
}
