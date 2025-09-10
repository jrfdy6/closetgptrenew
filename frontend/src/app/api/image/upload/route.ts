export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();

    const authHeader = request.headers.get('authorization') || '';

    const backendFormData = new FormData();
    for (const [key, value] of formData.entries()) {
      backendFormData.append(key, value as any);
    }

    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';

    const response = await fetch(`${backendUrl}/api/image/upload`, {
      method: 'POST',
      body: backendFormData,
      headers: authHeader ? { Authorization: authHeader } : undefined,
    });

    if (!response.ok) {
      const errorText = await response.text();
      return new Response(errorText || 'Upload failed', { status: response.status });
    }

    const data = await response.json();
    return new Response(JSON.stringify(data), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Failed to upload image' }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

