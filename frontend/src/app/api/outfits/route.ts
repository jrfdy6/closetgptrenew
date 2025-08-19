import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(req: NextRequest) {
  const url = `${BACKEND_URL}/api/outfits${req.nextUrl.search}`;
  
  console.log(`[Proxy] Forwarding GET → ${url}`);
  
  try {
    const res = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        // Forward cookies/auth headers if needed
        Authorization: req.headers.get("authorization") || "",
      },
    });

    const data = await res.json();
    console.log(`[Proxy] Backend response: ${res.status} - ${Array.isArray(data) ? data.length : 'Not array'} items`);
    
    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error(`[Proxy] Error forwarding to backend:`, error);
    return new Response(
      JSON.stringify({ error: 'Backend connection failed', details: error instanceof Error ? error.message : 'Unknown error' }), 
      { 
        status: 503,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const url = `${BACKEND_URL}/api/outfits`;

  console.log(`[Proxy] Forwarding POST → ${url}`);
  
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: req.headers.get("authorization") || "",
      },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    console.log(`[Proxy] Backend response: ${res.status}`);
    
    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error(`[Proxy] Error forwarding to backend:`, error);
    return new Response(
      JSON.stringify({ error: 'Backend connection failed', details: error instanceof Error ? error.message : 'Unknown error' }), 
      { 
        status: 503,
        headers: { "Content-Type": "application/json" }
      }
    );
  }
} 