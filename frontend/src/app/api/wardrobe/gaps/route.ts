import { NextRequest, NextResponse } from "next/server";
import { getUserIdFromRequest } from '@/lib/utils/server-auth';

// Force dynamic rendering since we use request.url
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    console.log('🔍 Frontend API: Wardrobe gaps endpoint called');
    
    const backendUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.BACKEND_URL ||
      'https://closetgptrenew-backend-production.up.railway.app';
    
    // Get gender from URL query parameters
    const { searchParams } = new URL(request.url);
    const gender = searchParams.get('gender');
    console.log('🔍 Frontend API: Gender from URL params:', gender);
    
    // Get user's gender from their profile (fallback)
    let userGender = gender;
    let authHeaders = {};
    
    try {
      console.log('🔍 Frontend API: Verifying user authentication...');
      const userId = await getUserIdFromRequest(request);
      console.log('🔍 Frontend API: User ID:', userId);
      
      if (userId) {
        // Get the authorization header from the request
        const authHeader = request.headers.get('authorization');
        authHeaders = {
          'Authorization': authHeader || '',
          'Content-Type': 'application/json',
        };
        
        // If no gender from URL, try to get from profile
        if (!userGender) {
          console.log('🔍 Frontend API: No gender from URL, fetching from profile...');
          const profileResponse = await fetch(`${backendUrl}/api/user/profile`, {
            method: 'GET',
            headers: authHeaders,
          });
          
          console.log('🔍 Frontend API: Profile response status:', profileResponse.status);
          
          if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            console.log('🔍 Frontend API: Profile data received');
            userGender = profileData.data?.gender;
            console.log('🔍 Frontend API: Gender from profile:', userGender);
          } else {
            console.log('❌ Frontend API: Profile fetch failed:', profileResponse.status, profileResponse.statusText);
          }
        }
        
        // Call backend with gender parameter
        console.log('🔍 Frontend API: Calling backend with gender:', userGender);
        const backendResponse = await fetch(`${backendUrl}/api/wardrobe/gaps?gender=${userGender || ''}`, {
          method: 'GET',
          headers: authHeaders,
        });
        
        console.log('🔍 Frontend API: Backend response status:', backendResponse.status);
        
        if (backendResponse.ok) {
          const data = await backendResponse.json();
          console.log('🔍 Frontend API: Backend data received successfully');
          return NextResponse.json(data);
        } else {
          console.log('❌ Frontend API: Backend call failed:', backendResponse.status, backendResponse.statusText);
          const errorText = await backendResponse.text();
          console.log('❌ Frontend API: Backend error response:', errorText);
          return NextResponse.json(
            { error: 'Backend service unavailable' },
            { status: backendResponse.status }
          );
        }
      } else {
        console.log('❌ Frontend API: No authenticated user found');
        return NextResponse.json(
          { error: 'Authentication required' },
          { status: 401 }
        );
      }
    } catch (error) {
      console.log('❌ Frontend API: Error in main flow:', error);
      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error("❌ Frontend API: Error:", error);
    return NextResponse.json(
      { 
        error: "Failed to fetch wardrobe gaps",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 