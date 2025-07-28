import { NextResponse } from 'next/server';

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

export async function GET() {
  console.log("🔍 Returning mock outfit traces data");
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