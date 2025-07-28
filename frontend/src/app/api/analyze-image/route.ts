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
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app';
    
    // Ensure the URL has a protocol and proper formatting
    const fullBackendUrl = backendUrl.startsWith('http') ? backendUrl : `https://${backendUrl}`;
    const cleanBackendUrl = fullBackendUrl.endsWith('/') ? fullBackendUrl.slice(0, -1) : fullBackendUrl;
    const fullUrl = `${cleanBackendUrl}/api/analyze-image`;
    
    console.log('🔍 Debug - Backend URL:', backendUrl);
    console.log('🔍 Debug - Clean Backend URL:', cleanBackendUrl);
    console.log('🔍 Debug - Full URL:', fullUrl);

    // Forward the request to the real backend server
    const response = await fetch(fullUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Backend error:", errorData);
      return NextResponse.json(
        { 
          error: "Failed to analyze image",
          details: errorData.detail || errorData.message || 'Unknown error'
        },
        { status: response.status }
      );
    }

    const analysis = await response.json();
    return NextResponse.json(analysis);
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
