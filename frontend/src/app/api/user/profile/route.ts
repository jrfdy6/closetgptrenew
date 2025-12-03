import { NextResponse } from 'next/server';

// 🔥 ENHANCEMENT #3: In-memory cache for profile data (5-minute TTL)
const profileCache = new Map<string, { data: any; timestamp: number }>();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

// 🔥 ENHANCEMENT #4: Retry logic with exponential backoff
async function fetchWithRetry(
  url: string, 
  options: RequestInit, 
  maxRetries = 3
): Promise<Response> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const startTime = Date.now();
      const response = await fetch(url, options);
      const duration = Date.now() - startTime;
      
      // 🔥 ENHANCEMENT #1: Detailed logging
      console.log(`🔍 PROFILE PROXY: Attempt ${attempt + 1}/${maxRetries}`, {
        url,
        status: response.status,
        duration: `${duration}ms`,
        ok: response.ok
      });
      
      // Don't retry on successful responses or client errors (4xx)
      if (response.ok || (response.status >= 400 && response.status < 500)) {
        return response;
      }
      
      // Log server errors before retry
      console.warn(`🔍 PROFILE PROXY: Server error ${response.status}, will retry...`);
      
    } catch (error: any) {
      lastError = error;
      console.error(`🔍 PROFILE PROXY: Attempt ${attempt + 1} failed:`, {
        error: error.message,
        name: error.name,
        willRetry: attempt < maxRetries - 1
      });
      
      // Don't retry on abort/timeout errors on last attempt
      if (error.name === 'AbortError' && attempt === maxRetries - 1) {
        throw error;
      }
    }
    
    // Exponential backoff: 100ms, 200ms, 400ms
    if (attempt < maxRetries - 1) {
      const delay = Math.pow(2, attempt) * 100;
      console.log(`🔍 PROFILE PROXY: Waiting ${delay}ms before retry...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  throw lastError || new Error('All retry attempts failed');
}

export async function GET(request: Request) {
  const requestStartTime = Date.now();
  
  try {
    console.log('🔍 PROFILE PROXY: Request received');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    if (!authHeader) {
      console.log('🔍 PROFILE PROXY: No auth header - returning 401');
      return NextResponse.json(
        { error: 'Not authenticated' },
        { status: 401 }
      );
    }
    
    // Extract user ID from token for caching (simple approach)
    const cacheKey = authHeader.substring(0, 50); // Use partial token as cache key
    
    // 🔥 ENHANCEMENT #3: Check cache first
    const cached = profileCache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      const cacheAge = Date.now() - cached.timestamp;
      console.log(`🔍 PROFILE PROXY: Cache hit! Age: ${cacheAge}ms`);
      return NextResponse.json({
        ...cached.data,
        _cached: true,
        _cacheAge: cacheAge
      });
    }
    
    // Call the production backend
    const backendUrl = 'https://closetgptrenew-production.up.railway.app';
    const fullBackendUrl = `${backendUrl}/api/auth/profile`;
    console.log('🔍 PROFILE PROXY: Calling backend:', fullBackendUrl);
    
    // Add timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => {
      console.error('🔍 PROFILE PROXY: Request timeout after 10s');
      controller.abort();
    }, 10000); // 10 second timeout
    
    try {
      // 🔥 ENHANCEMENT #4: Use retry logic
      const response = await fetchWithRetry(
        fullBackendUrl,
        {
          method: 'GET',
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
          },
          signal: controller.signal,
        },
        3 // Max 3 retries
      );
      
      clearTimeout(timeoutId);
      
      const totalDuration = Date.now() - requestStartTime;
      console.log(`🔍 PROFILE PROXY: Total request duration: ${totalDuration}ms`);
      
      if (!response.ok) {
        // 🔥 ENHANCEMENT #1: Enhanced error logging
        let errorDetails;
        try {
          errorDetails = await response.text();
          console.error('🔍 PROFILE PROXY: Backend error details:', {
            status: response.status,
            statusText: response.statusText,
            body: errorDetails.substring(0, 500), // Log first 500 chars
            duration: `${totalDuration}ms`
          });
          
          try {
            errorDetails = JSON.parse(errorDetails);
          } catch {
            // Keep as text if not JSON
          }
        } catch (e) {
          errorDetails = response.statusText;
        }
        
        // If it's a 502/503, return a helpful error
        if (response.status === 502 || response.status === 503) {
          return NextResponse.json({ 
            error: 'Backend service unavailable', 
            details: 'The backend service may be starting up or experiencing issues. Please try again in a moment.',
            status: response.status,
            duration: `${totalDuration}ms`
          }, { status: 503 });
        }
        
        return NextResponse.json({ 
          error: 'Backend request failed', 
          details: errorDetails || `Status: ${response.status} ${response.statusText}`,
          duration: `${totalDuration}ms`
        }, { status: response.status });
      }
      
      const profileData = await response.json();
      
      // 🔥 ENHANCEMENT #1: Detailed success logging
      console.log('🔍 PROFILE PROXY: Success!', {
        hasProfile: !!profileData.profile || !!profileData.user_id,
        profileId: profileData.profile?.id || profileData.user_id,
        duration: `${totalDuration}ms`
      });
      
      // 🔥 ENHANCEMENT #3: Cache the successful response
      profileCache.set(cacheKey, {
        data: profileData,
        timestamp: Date.now()
      });
      
      // Clean up old cache entries (simple LRU)
      if (profileCache.size > 100) {
        const oldestKey = profileCache.keys().next().value;
        profileCache.delete(oldestKey);
      }
      
      return NextResponse.json({
        ...profileData,
        _cached: false,
        _duration: `${totalDuration}ms`
      });
      
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      
      const totalDuration = Date.now() - requestStartTime;
      
      // 🔥 ENHANCEMENT #1: Enhanced error logging
      console.error('🔍 PROFILE PROXY: Fetch error details:', {
        name: fetchError.name,
        message: fetchError.message,
        duration: `${totalDuration}ms`,
        isAbortError: fetchError.name === 'AbortError'
      });
      
      if (fetchError.name === 'AbortError') {
        return NextResponse.json({ 
          error: 'Backend request timeout', 
          details: 'The backend service took too long to respond (>10s). Please try again.',
          duration: `${totalDuration}ms`
        }, { status: 504 });
      }
      
      return NextResponse.json(
        { 
          error: 'Failed to fetch user profile', 
          details: fetchError.message || 'Network error connecting to backend',
          duration: `${totalDuration}ms`
        },
        { status: 500 }
      );
    }
    
  } catch (error) {
    const totalDuration = Date.now() - requestStartTime;
    
    // 🔥 ENHANCEMENT #1: Enhanced error logging
    console.error('🔍 PROFILE PROXY: Unexpected error:', {
      error: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      duration: `${totalDuration}ms`
    });
    
    return NextResponse.json(
      { 
        error: 'Failed to fetch user profile', 
        details: error instanceof Error ? error.message : 'Unknown error',
        duration: `${totalDuration}ms`
      },
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