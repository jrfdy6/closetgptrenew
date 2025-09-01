import { NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    // Accept both { image } and { imageUrl }
    const body = await request.json();
    const image = body.image || body.imageUrl;

    if (!image || typeof image !== "string") {
      return NextResponse.json(
        { error: "No image provided" },
        { status: 400 }
      );
    }

    // Accept both URLs and base64 images
    const isUrl = image.startsWith("http://") || image.startsWith("https://");
    const isBase64 = image.startsWith("data:image/");

    if (!isUrl && !isBase64) {
      return NextResponse.json(
        { error: "Invalid image format. Must be a URL or base64 image." },
        { status: 400 }
      );
    }

    // Debug: Log the environment variable and constructed URL
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://closetgpt-backend-production.up.railway.app';
    const fullUrl = `${backendUrl}/api/analyze-image`;
    console.log('🔍 Debug - Backend URL:', backendUrl);
    console.log('🔍 Debug - Full URL:', fullUrl);

    // Pull through Authorization header if provided by the client
    const authHeader = request.headers.get('authorization');

    // Forward the request to the real backend server with robust fallbacks
    const candidateBaseUrls = Array.from(new Set([
      backendUrl,
              process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgpt-backend-production.up.railway.app',
        process.env.NEXT_PUBLIC_API_URL || 'https://closetgpt-backend-production.up.railway.app',
              'https://closetgpt-backend-production.up.railway.app',
    ].filter(Boolean))) as string[];

    const candidatePaths = [
      '/api/analyze-image',
      '/api/analyze-image-legacy',
      '/api/analyze-image-clip-only',
      '/analyze-image',
    ];

    const candidateBodies = [
      { image: { url: image } },
      { image },
    ];

    const attempts: Array<{ url: string; body: any }> = [];
    for (const base of candidateBaseUrls) {
      for (const path of candidatePaths) {
        for (const body of candidateBodies) {
          attempts.push({ url: `${base}${path}`, body });
        }
      }
    }

    let lastError: any = null;
    for (const attempt of attempts) {
      try {
        console.log('🔁 Trying backend endpoint:', attempt.url);
        const resp = await fetch(attempt.url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authHeader ? { 'Authorization': authHeader } : {}),
          },
          body: JSON.stringify(attempt.body),
        });
        if (resp.ok) {
          const data = await resp.json();
          return NextResponse.json(data);
        }
        // Capture error body text/json for diagnostics
        let errorText = '';
        try {
          const errJson = await resp.json();
          errorText = JSON.stringify(errJson);
        } catch (_) {
          errorText = await resp.text();
        }
        console.error(`Attempt failed ${resp.status} at ${attempt.url}:`, errorText);
        lastError = { status: resp.status, details: errorText || 'Unknown error' };
        // If 404, continue to next attempt; otherwise break (e.g., 401/500 likely consistent across attempts)
        if (resp.status !== 404) break;
      } catch (err) {
        console.error('Network error calling backend:', err);
        lastError = { status: 500, details: err instanceof Error ? err.message : 'Network error' };
      }
    }

    return NextResponse.json(
      { error: 'Failed to analyze image', details: lastError?.details || 'Unknown error' },
      { status: lastError?.status || 500 }
    );
  } catch (error) {
    console.error("Error analyzing image:", error);
    return NextResponse.json(
      { 
        error: "Failed to analyze image", 
        details: error instanceof Error ? error.message : "Unknown error",
        stack: process.env.NODE_ENV === 'development' ? error instanceof Error ? error.stack : undefined : undefined
      },
      { status: 500 }
    );
  }
}
