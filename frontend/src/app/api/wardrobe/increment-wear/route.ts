import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest } from '@/lib/utils/server-auth';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    // Verify user authentication
    const userId = await getUserIdFromRequest(req);
    if (!userId) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Unauthorized',
          details: 'No valid authorization token provided'
        },
        { status: 401 }
      );
    }

    // Get the authorization header to forward to backend
    const authHeader = req.headers.get('authorization');
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

    // Get request body
    const body = await req.json();
    const { itemId } = body;

    if (!itemId) {
      return NextResponse.json(
        { 
          success: false,
          error: 'Missing itemId',
          details: 'Item ID is required'
        },
        { status: 400 }
      );
    }

    // Forward request to backend
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001';
    const response = await fetch(`${backendUrl}/api/wardrobe/${itemId}/increment-wear`, {
      method: 'POST',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(
        { 
          success: false,
          error: errorData.detail || 'Failed to increment wear count',
          details: 'Backend request failed'
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
      success: true,
      message: 'Wear count incremented successfully',
      data: {
        itemId,
        ...data
      }
    });

  } catch (error) {
    console.error('Error incrementing wear count:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to increment wear count',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 