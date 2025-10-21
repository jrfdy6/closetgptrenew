import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const outfitId = params.id;
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    // Get the backend URL with fallbacks
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 
                      process.env.NEXT_PUBLIC_BACKEND_URL || 
                      'https://closetgptrenew-production.up.railway.app';

    console.log(`👕 [API] Marking outfit ${outfitId} as worn`);

    // Prepare request body with required fields
    const requestBody = {
      outfitId: outfitId,
      dateWorn: new Date().toISOString().split('T')[0], // YYYY-MM-DD format
      occasion: 'Daily',
      mood: 'Confident',
      weather: {},
      notes: '',
      tags: []
    };

    console.log(`🔍 [API] Request body:`, requestBody);

    // Forward request to backend with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

    try {
      const backendResponse = await fetch(`${backendUrl}/api/outfit-history/mark-worn`, {
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const data = await backendResponse.json();

      if (!backendResponse.ok) {
        console.error(`❌ [API] Backend error marking outfit ${outfitId} as worn:`, data);
        return NextResponse.json(
          { 
            success: false,
            error: data.detail || 'Backend request failed',
            details: data.detail || 'Unknown backend error'
          },
          { status: backendResponse.status }
        );
      }

      console.log(`✅ [API] Successfully marked outfit ${outfitId} as worn:`, data);
      return NextResponse.json(data);

    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error(`⏰ [API] Timeout marking outfit ${outfitId} as worn`);
        return NextResponse.json(
          { 
            success: false,
            error: 'Backend request timeout',
            details: 'Backend took too long to respond'
          },
          { status: 504 }
        );
      }
      console.error(`❌ [API] Error marking outfit ${outfitId} as worn:`, fetchError);
      return NextResponse.json(
        { 
          success: false,
          error: 'Failed to forward request',
          details: fetchError.message
        },
        { status: 500 }
      );
    }

  } catch (error) {
    console.error(`❌ [API] Error in mark outfit ${params.id} as worn route:`, error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to mark outfit as worn',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
