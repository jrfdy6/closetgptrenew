import { NextRequest, NextResponse } from 'next/server';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  try {
    // Get the host from the request
    const host = req.headers.get('host') || 'unknown';
    
    // Check environment variables
    const config = {
      host: host,
      timestamp: new Date().toISOString(),
      environment: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'NOT SET',
        NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'NOT SET',
        NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'NOT SET',
        NEXT_PUBLIC_FIREBASE_PROJECT_ID: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'NOT SET',
        NODE_ENV: process.env.NODE_ENV || 'NOT SET'
      },
      isCustomDomain: host.includes('easyoutfitapp.com'),
      isVercelDomain: host.includes('vercel.app')
    };

    return NextResponse.json({
      success: true,
      config
    });

  } catch (error) {
    console.error('Error checking config:', error);
    return NextResponse.json(
      { 
        success: false,
        error: 'Failed to check configuration'
      },
      { status: 500 }
    );
  }
}

