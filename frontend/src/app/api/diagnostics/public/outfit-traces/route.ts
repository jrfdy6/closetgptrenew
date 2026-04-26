import { NextResponse } from 'next/server';
import { serverDebugLog } from '@/lib/server/debug';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET() {
  serverDebugLog('🔍 Returning mock outfit traces data');
  return NextResponse.json({
    success: true,
    data: {
      traces: [],
      total_traces: 0,
      last_trace_timestamp: Math.floor(Date.now() / 1000),
      message: "Mock outfit traces data (backend not available during build)"
    }
  });
} 
