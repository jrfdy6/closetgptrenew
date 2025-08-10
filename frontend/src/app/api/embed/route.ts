import { NextResponse } from "next/server";

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const image = formData.get('image') as File;
    const itemId = formData.get('item_id') as string;

    if (!image || !itemId) {
      return NextResponse.json(
        { error: "Image and item_id are required" },
        { status: 400 }
      );
    }

    // Forward the request to the backend server
    const backendFormData = new FormData();
    backendFormData.append('image', image);
    backendFormData.append('item_id', itemId);

    const baseUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://acceptable-wisdom-production-ac06.up.railway.app';
    const response = await fetch(`${baseUrl}/api/embed`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error("Backend error:", errorData);
      throw new Error(errorData.detail || errorData.message || 'Failed to generate embedding');
    }

    const result = await response.json();
    return NextResponse.json(result);
  } catch (error) {
    console.error("Error generating embedding:", error);
    return NextResponse.json(
      { 
        error: "Failed to generate embedding", 
        details: error instanceof Error ? error.message : "Unknown error",
        stack: process.env.NODE_ENV === 'development' ? error instanceof Error ? error.stack : undefined : undefined
      },
      { status: 500 }
    );
  }
} 