import { NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Error reporting endpoint called');
    
    const errorData = await request.json();
    console.log('🔍 DEBUG: Error data received:', errorData);
    
    // Log the error for debugging purposes
    console.error('🚨 Frontend Error Report:', {
      timestamp: errorData.timestamp,
      code: errorData.code,
      message: errorData.message,
      severity: errorData.severity,
      context: errorData.context
    });
    
    // For now, just acknowledge receipt
    return NextResponse.json({
      success: true,
      message: 'Error report received',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('🔍 DEBUG: Error in error reporting endpoint:', error);
    return NextResponse.json(
      { error: 'Failed to process error report' },
      { status: 500 }
    );
  }
}
