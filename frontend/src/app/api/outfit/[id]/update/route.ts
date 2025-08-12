import { NextResponse } from "next/server";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_BACKEND_URL ||
  "http://localhost:3001";

export async function PUT(
  request: Request,
  context: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await context.params;
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    // Get the request body
    const body = await request.json();
    
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    // Forward the request to the backend
    const response = await fetch(`${API_URL}/api/outfit/${id}/update`, {
      method: 'PUT',
      headers,
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { error: errorData.detail || errorData.error || "Failed to update outfit" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Error updating outfit:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 