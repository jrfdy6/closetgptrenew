import { NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

const FALLBACK_WEATHER = {
  temperature: 72.0,
  condition: "Clear",
  humidity: 65,
  wind_speed: 5.0,
  precipitation: 0.0,
};

function createFallbackResponse(
  location: string | undefined,
  error: string
) {
  const responsePayload = {
    ...FALLBACK_WEATHER,
    location: location || "Fallback Location",
    fallback: true,
    error,
  };

  return NextResponse.json(responsePayload, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

export async function POST(request: Request) {
  try {
    console.log("🌤️ Frontend weather API route called");
    const requestBody = await request.json();
    console.log("🌤️ Frontend weather API called with:", requestBody);

    // Forward the request to the backend server
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app'}/api/weather`;
    console.log("🌤️ Forwarding to backend:", backendUrl);
    
    console.log("🌤️ About to make fetch request to backend");
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
      // Add timeout
      signal: AbortSignal.timeout(15000), // 15 second timeout
    });

    console.log("🌤️ Backend response status:", response.status);

    if (!response.ok) {
      let parsedError: any = null;
      let rawError = "";
      try {
        rawError = await response.text();
        parsedError = rawError ? JSON.parse(rawError) : null;
      } catch (parseError) {
        console.warn("🌤️ Backend returned non-JSON error payload", parseError);
      }

      const reason =
        parsedError?.detail ||
        parsedError?.message ||
        parsedError?.error ||
        rawError ||
        `Backend weather error ${response.status}`;

      console.error("🌤️ Backend error:", reason, { status: response.status });

      // Always return a graceful fallback for non-OK responses
      return createFallbackResponse(requestBody.location, reason);
    }

    const weatherData = await response.json();
    console.log("🌤️ Backend weather data received:", weatherData);
    
    // Return with CORS headers
    return NextResponse.json(weatherData, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  } catch (error) {
    console.error("🌤️ Error fetching weather:", error);
    
    const message =
      error instanceof Error ? error.message : "Unknown weather fetch error";
    console.log("🌤️ Backend unavailable or unexpected error, providing fallback weather data");
    return createFallbackResponse(undefined, message);
  }
}

// Handle OPTIONS requests for CORS
export async function OPTIONS(request: Request) {
  return NextResponse.json({}, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
} 