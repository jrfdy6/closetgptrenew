import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    // Check if we're in build time or if backend is not available
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.BACKEND_URL || 'http://localhost:3001';
    
    // Add timeout to prevent hanging during build
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${backendUrl}/api/wardrobe/validation-errors`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      // Return mock data if backend is not available
      return NextResponse.json({
        success: true,
        data: {
          validation_errors: [],
          outfit_failures: [],
          error_patterns: {},
          total_errors: 0,
          failure_rate: 0
        },
        message: "Mock validation errors (backend not available)"
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching validation errors:', error);
    
    // Return mock data on any error to prevent build failures
    return NextResponse.json({
      success: true,
      data: {
        validation_errors: [],
        outfit_failures: [],
        error_patterns: {},
        total_errors: 0,
        failure_rate: 0
      },
      message: "Mock validation errors (error occurred)"
    });
  }
} 