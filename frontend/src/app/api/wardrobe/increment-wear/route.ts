import { NextRequest, NextResponse } from 'next/server';
import { getFirebaseIdToken } from '@/lib/utils/auth';

export async function POST(req: NextRequest) {
  try {
    // Get the authorization header
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

    // Extract token from header
    const token = authHeader.replace('Bearer ', '');

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
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:3001';
    const response = await fetch(`${backendUrl}/api/wardrobe/${itemId}/increment-wear`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
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