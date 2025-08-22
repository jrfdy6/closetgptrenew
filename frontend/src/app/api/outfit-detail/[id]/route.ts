import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    // Await params for Next.js 15 compatibility
    const { id } = await params;
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3001';
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    const response = await fetch(`${apiUrl}/api/outfit/${id}`, {
      method: 'GET',
      headers,
    });

    if (!response.ok) {
      console.error('Backend response not OK:', response.status, response.statusText);
      throw new Error('Failed to fetch outfit from backend');
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching outfit:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfit' },
      { status: 500 }
    );
  }
} 