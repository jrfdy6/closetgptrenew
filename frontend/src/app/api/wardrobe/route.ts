import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Use the correct backend URL
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3001';
    console.log('🔍 DEBUG: Using apiUrl:', apiUrl);
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    } else {
      console.warn('🔍 DEBUG: No authorization header provided');
    }
    
    console.log('🔍 DEBUG: Calling backend wardrobe endpoint:', `${fullApiUrl}/api/wardrobe/`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // Increased to 15 seconds
    
    try {
      console.log('🔍 DEBUG: Starting fetch request to backend...');
      const response = await fetch(`${fullApiUrl}/api/wardrobe/`, {
        method: 'GET',
        headers,
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      console.log('🔍 DEBUG: Backend response received!');
      console.log('🔍 DEBUG: Backend response status:', response.status);

      if (!response.ok) {
        console.error('🔍 DEBUG: Backend response not OK:', response.status, response.statusText);
        let errorText = '';
        try {
          errorText = await response.text();
          console.error('🔍 DEBUG: Backend error response:', errorText);
        } catch (textError) {
          console.error('🔍 DEBUG: Failed to read error response text:', textError);
          errorText = 'Unable to read error details';
        }
        
        // Handle specific error cases
        if (response.status === 401) {
          return NextResponse.json(
            { error: 'Authentication required', details: 'Please sign in to access your wardrobe' },
            { status: 401 }
          );
        }
        
        if (response.status === 403) {
          return NextResponse.json(
            { error: 'Access denied', details: 'You do not have permission to access this resource' },
            { status: 403 }
          );
        }
        
        // Instead of throwing, return the error response
        return NextResponse.json(
          { 
            error: 'Backend error', 
            details: `Backend responded with ${response.status}: ${errorText.substring(0, 200)}`,
            status: response.status
          },
          { status: response.status }
        );
      }

      console.log('🔍 DEBUG: About to parse response as JSON...');
      let data;
      try {
        data = await response.json();
        console.log('🔍 DEBUG: Successfully parsed JSON response');
        console.log('🔍 DEBUG: Response data keys:', Object.keys(data));
        console.log('🔍 DEBUG: Response data type:', typeof data);
      } catch (parseError) {
        console.error('🔍 DEBUG: Failed to parse JSON response:', parseError);
        return NextResponse.json(
          { error: 'Invalid response format', details: 'Backend returned invalid JSON' },
          { status: 500 }
        );
      }

      console.log('🔍 DEBUG: About to return response...');
      return NextResponse.json(data);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 15 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 15 seconds' },
          { status: 504 }
        );
      }
      
      // Log the specific error
      console.error('🔍 DEBUG: Fetch error details:', {
        name: error instanceof Error ? error.name : 'Unknown',
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace'
      });
      
      // Return error response instead of throwing
      return NextResponse.json(
        { 
          error: 'Network error', 
          details: error instanceof Error ? error.message.substring(0, 200) : 'Unknown network error'
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('🔍 DEBUG: Unexpected error in wardrobe API route:', error);
    console.error('🔍 DEBUG: Error type:', typeof error);
    console.error('🔍 DEBUG: Error constructor:', error?.constructor?.name);
    
    // Safely extract error message
    let errorMessage = 'Unknown error occurred';
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      errorMessage = JSON.stringify(error).substring(0, 200);
    }
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: errorMessage.substring(0, 200)
      },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Wardrobe POST API route called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    console.log('🔍 DEBUG: Authorization header present:', !!authHeader);
    
    // Use the correct backend URL
    const apiUrl =
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'http://localhost:3001';
    console.log('🔍 DEBUG: Using apiUrl:', apiUrl);
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    console.log('🔍 DEBUG: Full API URL:', fullApiUrl);
    
    // Get the request body
    let requestBody;
    try {
      requestBody = await request.json();
      console.log('🔍 DEBUG: Request body:', requestBody);
    } catch (bodyError) {
      console.error('🔍 DEBUG: Failed to parse request body:', bodyError);
      return NextResponse.json(
        { error: 'Invalid request body', details: 'Request body must be valid JSON' },
        { status: 400 }
      );
    }
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    } else {
      console.warn('🔍 DEBUG: No authorization header provided');
    }
    
    console.log('🔍 DEBUG: Calling backend wardrobe endpoint:', `${fullApiUrl}/api/wardrobe/`);
    console.log('🔍 DEBUG: Headers:', headers);
    
    // Create an AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // Increased to 15 seconds
    
    try {
      console.log('🔍 DEBUG: Starting fetch request to backend...');
      const response = await fetch(`${fullApiUrl}/api/wardrobe/`, {
        method: 'POST',
        headers,
        body: JSON.stringify(requestBody),
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      console.log('🔍 DEBUG: Backend response received!');
      console.log('🔍 DEBUG: Backend response status:', response.status);

      if (!response.ok) {
        console.error('🔍 DEBUG: Backend response not OK:', response.status, response.statusText);
        let errorText = '';
        try {
          errorText = await response.text();
          console.error('🔍 DEBUG: Backend error response:', errorText);
        } catch (textError) {
          console.error('🔍 DEBUG: Failed to read error response text:', textError);
          errorText = 'Unable to read error details';
        }
        
        // Handle specific error cases
        if (response.status === 401) {
          return NextResponse.json(
            { error: 'Authentication required', details: 'Please sign in to add items to your wardrobe' },
            { status: 401 }
          );
        }
        
        if (response.status === 403) {
          return NextResponse.json(
            { error: 'Access denied', details: 'You do not have permission to add items' },
            { status: 403 }
          );
        }
        
        if (response.status === 400) {
          return NextResponse.json(
            { error: 'Invalid request', details: errorText.substring(0, 200) },
            { status: 400 }
          );
        }
        
        // Return error response instead of throwing
        return NextResponse.json(
          { 
            error: 'Backend error', 
            details: `Backend responded with ${response.status}: ${errorText.substring(0, 200)}`,
            status: response.status
          },
          { status: response.status }
        );
      }

      let data;
      try {
        data = await response.json();
        console.log('🔍 DEBUG: Backend response data:', data);
      } catch (parseError) {
        console.error('🔍 DEBUG: Failed to parse backend response:', parseError);
        return NextResponse.json(
          { error: 'Invalid response format', details: 'Backend returned invalid JSON' },
          { status: 500 }
        );
      }
      
      return NextResponse.json(data);
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        console.error('🔍 DEBUG: Request timed out after 15 seconds');
        return NextResponse.json(
          { error: 'Request timed out', details: 'Backend did not respond within 15 seconds' },
          { status: 504 }
        );
      }
      
      // Log the specific error
      console.error('🔍 DEBUG: Fetch error details:', {
        name: error instanceof Error ? error.name : 'Unknown',
        message: error instanceof Error ? error.message : 'Unknown error',
        stack: error instanceof Error ? error.stack : 'No stack trace'
      });
      
      // Return error response instead of throwing
      return NextResponse.json(
        { 
          error: 'Network error', 
          details: error instanceof Error ? error.message.substring(0, 200) : 'Unknown network error'
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('🔍 DEBUG: Unexpected error in wardrobe POST API route:', error);
    console.error('🔍 DEBUG: Error type:', typeof error);
    console.error('🔍 DEBUG: Error constructor:', error?.constructor?.name);
    
    // Safely extract error message
    let errorMessage = 'Unknown error occurred';
    if (error instanceof Error) {
      errorMessage = error.message;
    } else if (typeof error === 'string') {
      errorMessage = error;
    } else if (error && typeof error === 'object') {
      errorMessage = JSON.stringify(error).substring(0, 200);
    }
    
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        details: errorMessage.substring(0, 200)
      },
      { status: 500 }
    );
  }
} 