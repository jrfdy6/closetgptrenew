import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const outfitId = params.id;

    const authHeader = request.headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return NextResponse.json(
        {
          success: false,
          error: 'Unauthorized',
          details: 'No authorization token provided'
        },
        { status: 401 }
      );
    }

    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      'https://closetgptrenew-production.up.railway.app';

    console.log(`❤️ [API] Toggling favorite for outfit ${outfitId}`);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000);

    try {
      const baseUrl = backendUrl.replace(/\/$/, '');

      const outfitResponse = await fetch(
        `${baseUrl}/api/outfits/${outfitId}`,
        {
          method: 'GET',
          headers: {
            Authorization: authHeader
          },
          signal: controller.signal
        }
      );

      if (!outfitResponse.ok) {
        clearTimeout(timeoutId);
        const errorPayload = await outfitResponse.json().catch(() => ({}));
        console.error(
          `❌ [API] Failed to load outfit ${outfitId} before toggling favorite`,
          errorPayload
        );
        return NextResponse.json(
          {
            success: false,
            error: errorPayload.detail || 'Failed to load outfit before update',
            details: errorPayload.detail || 'Unknown backend error'
          },
          { status: outfitResponse.status }
        );
      }

      const outfitJson = await outfitResponse.json();
      const existingOutfit = outfitJson?.data ?? outfitJson ?? {};
      const currentFavorite =
        existingOutfit.isFavorite ?? existingOutfit.favorite ?? false;
      const nextFavorite = !currentFavorite;

      const backendResponse = await fetch(
        `${baseUrl}/api/outfits/${outfitId}`,
        {
          method: 'PUT',
          headers: {
            Authorization: authHeader,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ isFavorite: nextFavorite }),
          signal: controller.signal
        }
      );

      clearTimeout(timeoutId);

      const data = await backendResponse.json().catch(() => ({}));

      if (!backendResponse.ok) {
        console.error(
          `❌ [API] Backend error toggling favorite for outfit ${outfitId}:`,
          data
        );
        return NextResponse.json(
          {
            success: false,
            error: data.detail || 'Backend request failed',
            details: data.detail || 'Unknown backend error'
          },
          { status: backendResponse.status }
        );
      }

      console.log(
        `✅ [API] Successfully toggled favorite for outfit ${outfitId}`,
        data
      );
      return NextResponse.json(
        data ?? {
          success: true,
          message: 'Outfit favorite status toggled successfully',
          data: { id: outfitId, isFavorite: nextFavorite }
        }
      );
    } catch (fetchError: any) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error(
          `⏰ [API] Timeout toggling favorite for outfit ${outfitId}`
        );
        return NextResponse.json(
          {
            success: false,
            error: 'Backend request timeout',
            details: 'Backend took too long to respond'
          },
          { status: 504 }
        );
      }

      console.error(
        `❌ [API] Error toggling favorite for outfit ${outfitId}:`,
        fetchError
      );
      return NextResponse.json(
        {
          success: false,
          error: 'Failed to forward request',
          details: fetchError.message || 'Unknown error'
        },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error(
      `❌ [API] Unexpected error in toggle favorite route for outfit ${params.id}:`,
      error
    );
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to toggle outfit favorite',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return NextResponse.json({}, { status: 204 });
}

