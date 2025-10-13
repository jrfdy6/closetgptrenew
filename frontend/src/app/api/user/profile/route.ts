import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: User profile API route called - CONNECTING TO PRODUCTION BACKEND v2');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/auth/profile`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      return NextResponse.json({ 
        error: 'Backend request failed', 
        details: `Status: ${response.status} ${response.statusText}`
      }, { status: response.status });
    }
    
    const profileData = await response.json();
    console.log('🔍 DEBUG: Backend profile data received:', {
      success: profileData.success,
      hasProfile: !!profileData.profile,
      profileId: profileData.profile?.id || profileData.id
    });
    
    return NextResponse.json(profileData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in profile route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user profile' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Creating/updating user profile - CONNECTING TO PRODUCTION BACKEND');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    const body = await request.json();
    console.log('🔍 DEBUG: Profile data:', body);
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/auth/profile`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    const response = await fetch(fullBackendUrl, {
      method: 'PUT',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText);
      return NextResponse.json({ 
        error: 'Backend request failed', 
        details: `Status: ${response.status} ${response.statusText}`
      }, { status: response.status });
    }
    
    const profileData = await response.json();
    console.log('🔍 DEBUG: Backend profile data received:', {
      success: profileData.success,
      hasProfile: !!profileData.profile,
      profileId: profileData.profile?.id || profileData.id
    });
    
    return NextResponse.json(profileData);
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in profile POST:', error);
    return NextResponse.json(
      { error: 'Failed to create/update user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 