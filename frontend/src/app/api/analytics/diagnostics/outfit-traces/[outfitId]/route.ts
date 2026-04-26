import { NextRequest, NextResponse } from 'next/server';
import { authenticatedFetch } from '@/lib/utils/auth';
import { getBackendUrl } from '@/lib/server/backendUrl';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ outfitId: string }> }
) {
  try {
    const { outfitId } = await params;
    
    const backendUrl = getBackendUrl();
    const response = await authenticatedFetch(
      `${backendUrl}/analytics/diagnostics/outfit-traces/${outfitId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching outfit trace detail:', error);
    return NextResponse.json(
      { error: 'Failed to fetch outfit trace detail' },
      { status: 500 }
    );
  }
} 
