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
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/auth/profile`;
    console.log('🔍 DEBUG: Calling backend URL:', fullBackendUrl);
    
    // Add timeout and better error handling
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    try {
      const response = await fetch(fullBackendUrl, {
        method: 'GET',
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      console.log('🔍 DEBUG: Backend response status:', response.status);
      
      if (!response.ok) {
        // Try to get error details from response
        let errorDetails;
        try {
          errorDetails = await response.text();
          console.error('🔍 DEBUG: Backend error response:', errorDetails);
          try {
            errorDetails = JSON.parse(errorDetails);
          } catch {
            // Keep as text if not JSON
          }
        } catch (e) {
          errorDetails = response.statusText;
        }
        
        console.error('🔍 DEBUG: Backend response not ok:', response.status, response.statusText, errorDetails);
        
        // If it's a 502, return a more helpful error
        if (response.status === 502) {
          return NextResponse.json({ 
            error: 'Backend service unavailable', 
            details: 'The backend service may be starting up or experiencing issues. Please try again in a moment.',
            status: 502
          }, { status: 503 }); // Return 503 instead of 502 to indicate temporary issue
        }
        
        return NextResponse.json({ 
          error: 'Backend request failed', 
          details: errorDetails || `Status: ${response.status} ${response.statusText}`
        }, { status: response.status });
      }
      
      const profileData = await response.json();
      console.log('🔍 DEBUG: Backend profile data received:', {
        success: profileData.success,
        hasProfile: !!profileData.profile,
        profileId: profileData.profile?.id || profileData.id
      });
      
      return NextResponse.json(profileData);
      
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      if (fetchError.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timeout after 10 seconds');
        return NextResponse.json({ 
          error: 'Backend request timeout', 
          details: 'The backend service took too long to respond. Please try again.'
        }, { status: 504 });
      }
      
      console.error('🔍 DEBUG: Fetch error in profile route:', fetchError);
      return NextResponse.json(
        { 
          error: 'Failed to fetch user profile', 
          details: fetchError.message || 'Network error connecting to backend'
        },
        { status: 500 }
      );
    }
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in profile route:', error);
    return NextResponse.json(
      { error: 'Failed to fetch user profile', details: error instanceof Error ? error.message : 'Unknown error' },
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
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
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