import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: User profile API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Call the real backend API
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const response = await fetch(`${backendUrl}/api/auth/profile`, {
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend responded with status:', response.status);
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend error response:', errorText);
      
      if (response.status === 401) {
        return NextResponse.json(
          { error: 'Authentication failed' },
          { status: 401 }
        );
      } else if (response.status === 404) {
        return NextResponse.json(
          { error: 'Profile not found' },
          { status: 404 }
        );
      } else {
        return NextResponse.json(
          { error: 'Backend server error' },
          { status: response.status }
        );
      }
    }
    
    const backendData = await response.json();
    console.log('🔍 DEBUG: Backend profile data:', backendData);
    
    // Transform backend data to match frontend expectations
    const profile = {
      id: backendData.user_id || 'unknown',
      userId: backendData.user_id || 'unknown',
      name: backendData.name || 'Unknown User',
      email: backendData.email || 'unknown@email.com',
      onboardingCompleted: true, // Assume completed if profile exists
      stylePreferences: {
        gender: 'unisex', // Default, can be enhanced later
        style: 'casual',  // Default, can be enhanced later
        colors: ['blue', 'black', 'white'], // Default, can be enhanced later
        brands: [] // Default, can be enhanced later
      },
      createdAt: backendData.created_at || new Date().toISOString(),
      updatedAt: backendData.updated_at || new Date().toISOString(),
      // Add backend-specific fields
      avatarUrl: backendData.avatar_url,
      backendData: backendData // Include full backend response for debugging
    };
    
    return NextResponse.json({
      success: true,
      profile: profile
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error fetching user profile:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Creating/updating user profile');
    
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
    
    // Call the real backend API to update profile
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const response = await fetch(`${backendUrl}/api/auth/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: body.name,
        email: body.email,
        // Add more fields as needed
      }),
    });
    
    if (!response.ok) {
      console.error('🔍 DEBUG: Backend update responded with status:', response.status);
      const errorText = await response.text();
      console.error('🔍 DEBUG: Backend error response:', errorText);
      
      if (response.status === 401) {
        return NextResponse.json(
          { error: 'Authentication failed' },
          { status: 401 }
        );
      } else {
        return NextResponse.json(
          { error: 'Failed to update profile' },
          { status: response.status }
        );
      }
    }
    
    const backendData = await response.json();
    console.log('🔍 DEBUG: Backend update response:', backendData);
    
    // Return success with updated profile
    return NextResponse.json({
      success: true,
      profile: {
        id: backendData.user_id || 'unknown',
        userId: backendData.user_id || 'unknown',
        name: backendData.name || body.name,
        email: backendData.email || body.email,
        onboardingCompleted: true,
        stylePreferences: body.stylePreferences || {
          gender: 'unisex',
          style: 'casual',
          colors: ['blue', 'black', 'white'],
          brands: []
        },
        createdAt: body.createdAt || new Date().toISOString(),
        updatedAt: backendData.updated_at || new Date().toISOString(),
        avatarUrl: backendData.avatar_url,
        backendData: backendData
      }
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error creating/updating user profile:', error);
    return NextResponse.json(
      { error: 'Failed to create/update user profile', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
} 