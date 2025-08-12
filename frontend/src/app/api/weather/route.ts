import { NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    console.log("🌤️ Frontend weather API route called");
    const requestBody = await request.json();
    console.log("🌤️ Frontend weather API called with:", requestBody);

    // Forward the request to the backend server
    const backendUrl = `${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001'}/api/weather`;
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
      const errorData = await response.json();
      console.error("🌤️ Backend error:", errorData);
      
      // If backend returns 404 (Not Found), provide fallback data
      if (response.status === 404) {
        console.log("🌤️ Weather endpoint not available, providing fallback data");
        return NextResponse.json(
          { 
            temperature: 72.0,
            condition: "Clear",
            humidity: 65,
            wind_speed: 5.0,
            location: requestBody.location || "Default Location",
            precipitation: 0.0,
            fallback: true
          },
          { 
            status: 200,
            headers: {
              'Access-Control-Allow-Origin': '*',
              'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
          }
        );
      }
      
      throw new Error(errorData.detail || errorData.message || 'Failed to fetch weather data');
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
    
    // Provide fallback weather data if backend is unavailable
    if (error instanceof Error && (error.message.includes('fetch') || error.message.includes('timeout'))) {
      console.log("🌤️ Backend unavailable, providing fallback weather data");
      return NextResponse.json(
        { 
          temperature: 72.0,
          condition: "Clear",
          humidity: 65,
          wind_speed: 5.0,
          location: "Default Location",
          precipitation: 0.0,
          fallback: true
        },
        { 
          status: 200,
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          },
        }
      );
    }
    
    return NextResponse.json(
      { 
        error: "Failed to fetch weather data", 
        details: error instanceof Error ? error.message : "Unknown error",
        stack: process.env.NODE_ENV === 'development' ? error instanceof Error ? error.stack : undefined : undefined
      },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
      }
    );
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