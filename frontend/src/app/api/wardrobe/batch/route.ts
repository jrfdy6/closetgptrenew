import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe batch API route called');
    
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);

    if (!authHeader) {
      return NextResponse.json(
        { error: 'Authorization header required' },
        { status: 401 }
      );
    }

    const body = await request.json();
    console.log('🔍 DEBUG: Batch request body items count:', body.length);

    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
    console.log('🔍 DEBUG: Backend URL:', backendUrl);

    const fullBackendUrl = `${backendUrl}/api/wardrobe/batch`;
    console.log('🔍 DEBUG: Forwarding batch request to backend:', fullBackendUrl);

    const backendRes = await fetch(fullBackendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
      },
      body: JSON.stringify(body),
    });

    console.log('🔍 DEBUG: Backend batch response status:', backendRes.status);

    if (!backendRes.ok) {
      const errorDetails = await backendRes.text();
      console.error('❌ DEBUG: Backend batch request failed:', errorDetails);
      return NextResponse.json(
        { error: `Failed to process batch request from backend`, details: errorDetails },
        { status: backendRes.status }
      );
    }

    const result = await backendRes.json();
    console.log('✅ DEBUG: Batch request processed successfully:', result);
    
    return NextResponse.json(result);
  } catch (err) {
    console.error('❌ DEBUG: Wardrobe batch API route error:', err);
    return NextResponse.json(
      { error: 'Wardrobe batch request failed in API route', details: String(err) },
      { status: 500 }
    );
  }
}
