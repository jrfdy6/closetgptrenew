import { NextRequest, NextResponse } from 'next/server';
import { getUserIdFromRequest } from '@/lib/utils/server-auth';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:3001';
    
    // Get user's gender from their profile
    let userGender = null;
    try {
      const userId = await getUserIdFromRequest(request);
      if (userId) {
        // Get the authorization header from the request
        const authHeader = request.headers.get('authorization');
        
        // Get user profile to determine gender
        const profileResponse = await fetch(`${backendUrl}/api/user/profile`, {
          method: 'GET',
          headers: {
            'Authorization': authHeader || '',
            'Content-Type': 'application/json',
          },
        });
        
        if (profileResponse.ok) {
          const profileData = await profileResponse.json();
          userGender = profileData.data?.gender;
        }
      }
    } catch (error) {
      console.log('Could not get user gender, will show unisex trends:', error);
    }
    
    // Build URL with gender parameter if available
    const url = new URL(`${backendUrl}/api/wardrobe/trending-styles`);
    if (userGender) {
      url.searchParams.set('gender', userGender);
    }
    
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching trending styles:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch trending styles' },
      { status: 500 }
    );
  }
} 