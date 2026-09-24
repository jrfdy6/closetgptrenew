export const dynamic = 'force-dynamic';
const MAX_IMAGE_BYTES = 4 * 1024 * 1024;
const privateHeaders = { 'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff' };
const fail = (status: number, error: string) => Response.json({ error }, { status, headers: privateHeaders });

export async function GET(request: Request) {
  const bucket = process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET?.trim();
  if (!bucket || !/^[a-z0-9][a-z0-9._-]*$/.test(bucket)) return fail(503, 'Image service is unavailable.');
  let source: URL;
  try {
    source = new URL(new URL(request.url).searchParams.get('url') || '');
    if (source.protocol !== 'https:' || source.username || source.password || source.port || source.hash ||
        !['storage.googleapis.com', 'firebasestorage.googleapis.com'].includes(source.hostname)) throw new Error();
    const path = decodeURIComponent(source.pathname);
    const prefix = source.hostname === 'storage.googleapis.com' ? `/${bucket}/` : `/v0/b/${bucket}/o/`;
    if (!path.startsWith(prefix) || path.length <= prefix.length || /[\\\x00-\x1f]/.test(path) || path.split('/').includes('..')) throw new Error();
  } catch { return fail(400, 'Invalid image URL.'); }

  try {
    const response = await fetch(source.toString(), { cache: 'no-store', redirect: 'error', signal: AbortSignal.timeout(15_000) });
    if (!response.ok) return fail(response.status === 404 ? 404 : 502, 'The image could not be loaded. Please try again.');
    const type = response.headers.get('content-type')?.split(';')[0].trim().toLowerCase();
    if (!type || !['image/png', 'image/jpeg', 'image/webp', 'image/avif'].includes(type)) return fail(502, 'The image response was invalid.');
    if (Number(response.headers.get('content-length')) > MAX_IMAGE_BYTES) { await response.body?.cancel(); return fail(413, 'The image is too large to download here.'); }
    if (!response.body) return fail(502, 'The image response was empty.');
    const reader = response.body.getReader();
    const chunks: Uint8Array[] = [];
    let size = 0;
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > MAX_IMAGE_BYTES) { await reader.cancel(); return fail(413, 'The image is too large to download here.'); }
        chunks.push(value);
      }
    } finally { reader.releaseLock(); }
    if (!size) return fail(502, 'The image response was empty.');
    const bytes = new Uint8Array(size);
    let offset = 0;
    for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
    return new Response(bytes, { headers: { ...privateHeaders, 'Content-Type': type, 'Content-Length': String(size) } });
  } catch { return fail(502, 'The image could not be loaded. Please try again.'); }
}
