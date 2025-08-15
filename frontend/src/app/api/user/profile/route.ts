import { NextResponse } from 'next/server';

// Force Vercel redeploy - Updated profile endpoint to return full data - VERSION 2.0
export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: User profile API route called - VERSION 2.0');
    console.log('🔍 DEBUG: Request URL:', request.url);
    console.log('🔍 DEBUG: Request method:', request.method);
    console.log('🔍 DEBUG: Request headers:', Object.fromEntries(request.headers.entries()));
    console.log('🔍 DEBUG: Request referer:', request.headers.get('referer'));
    console.log('🔍 DEBUG: Request user-agent:', request.headers.get('user-agent'));
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    if (!authHeader) {
      console.log('🔍 DEBUG: No auth header - likely prefetch or unauthorized access');
      console.log('🔍 DEBUG: This is expected for prefetching - returning 401 silently');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Call the real backend API
    const backendUrl = 'https://closetgptrenew-backend-production.up.railway.app';
    const profileUrl = `${backendUrl}/api/auth/profile`;
    console.log('🔍 DEBUG: Calling backend URL:', profileUrl);
    console.log('🔍 DEBUG: Auth header present:', !!authHeader);
    console.log('🔍 DEBUG: Auth header type:', authHeader?.startsWith('Bearer ') ? 'Bearer' : 'Other');
    
    const response = await fetch(profileUrl, {
      method: 'GET',
      headers: {
        'Authorization': authHeader,
        'Content-Type': 'application/json',
      },
    });
    
    console.log('🔍 DEBUG: Backend response status:', response.status);
    console.log('🔍 DEBUG: Backend response URL:', response.url);
    console.log('🔍 DEBUG: Backend response headers:', Object.fromEntries(response.headers.entries()));
    
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
      id: backendData.id || backendData.user_id || 'unknown',
      userId: backendData.id || backendData.user_id || 'unknown',
      name: backendData.name || 'Unknown User',
      email: backendData.email || 'unknown@email.com',
      gender: backendData.gender || 'Not specified',
      onboardingCompleted: backendData.onboardingCompleted || true,
      
      // Style Preferences
      stylePreferences: backendData.stylePreferences || [],
      preferences: backendData.preferences || {},
      
      // Measurements & Sizes
      measurements: {
        height: backendData.measurements?.height || 0,
        heightFeetInches: backendData.measurements?.heightFeetInches || backendData.heightFeetInches || 'Not specified',
        weight: backendData.measurements?.weight || backendData.weight || 'Not specified',
        bodyType: backendData.measurements?.bodyType || backendData.bodyType || 'Not specified',
        skinTone: backendData.measurements?.skinTone || backendData.skinTone || 'Not specified',
        topSize: backendData.measurements?.topSize || backendData.topSize || 'Not specified',
        bottomSize: backendData.measurements?.bottomSize || backendData.bottomSize || 'Not specified',
        shoeSize: backendData.measurements?.shoeSize || backendData.shoeSize || 'Not specified',
        dressSize: backendData.measurements?.dressSize || backendData.dressSize || 'Not specified',
        jeanWaist: backendData.measurements?.jeanWaist || backendData.jeanWaist || 'Not specified',
        braSize: backendData.measurements?.braSize || backendData.braSize || 'Not specified',
        inseam: backendData.measurements?.inseam || 'Not specified',
        waist: backendData.measurements?.waist || 'Not specified',
        chest: backendData.measurements?.chest || 'Not specified'
      },
      
      // Fit Preferences
      fitPreference: backendData.fitPreference || 'Not specified',
      fitPreferences: backendData.fitPreferences || {},
      
      // Color Palette
      colorPalette: backendData.colorPalette || {},
      
      // Quiz Responses
      quizResponses: backendData.quizResponses || [],
      
      // Additional Info
      budget: backendData.budget || 'Not specified',
      hybridStyleName: backendData.hybridStyleName || 'Not specified',
      alignmentScore: backendData.alignmentScore || 0,
      wardrobeCount: backendData.wardrobeCount || 0,
      
      // Timestamps
      createdAt: backendData.createdAt || backendData.created_at || new Date().toISOString(),
      updatedAt: backendData.updatedAt || backendData.updated_at || new Date().toISOString(),
      
      // Backend-specific fields
      avatarUrl: backendData.avatar_url || backendData.selfieUrl || '',
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