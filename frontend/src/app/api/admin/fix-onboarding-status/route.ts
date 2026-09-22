/** Retired decoded-token repair path; verified completion is derived on Railway. */
export async function POST() {
  return Response.json({ error: 'This legacy endpoint is no longer available.' }, {
    status: 410, headers: { 'Cache-Control': 'private, no-store' },
  });
}
