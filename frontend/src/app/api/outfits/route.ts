import { NextRequest, NextResponse } from 'next/server';

// Mock outfits endpoint - returns data directly without calling backend
export async function GET(req: NextRequest) {
  console.log("🔍 DEBUG: Outfits GET route called - MOCK VERSION");
  
  try {
    // Return mock outfits data
    const mockOutfits = [
      {
        id: 'outfit_1',
        name: 'Dark Academia Confident Look',
        occasion: 'Casual',
        style: 'Dark Academia',
        mood: 'Confident',
        items: [
          {
            id: 'item_1',
            name: 'Dark Academia Blazer',
            type: 'blazer',
            color: 'charcoal',
            brand: 'The Savile Row Company'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive',
            brand: 'Dockers'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown',
            brand: 'Unknown'
          }
        ],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        matchScore: 86
      },
      {
        id: 'outfit_2',
        name: 'Old Money Dynamic Interview',
        occasion: 'Interview',
        style: 'Old Money',
        mood: 'Dynamic',
        items: [
          {
            id: 'item_2',
            name: 'Statement T-Shirt',
            type: 't-shirt',
            color: 'white',
            brand: 'Celine'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive',
            brand: 'Dockers'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown',
            brand: 'Unknown'
          }
        ],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
        matchScore: 82
      }
    ];
    
    const response = NextResponse.json(mockOutfits);
    response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    response.headers.set('Pragma', 'no-cache');
    response.headers.set('Expires', '0');
    response.headers.set('Surrogate-Control', 'no-store');
    
    return response;
  } catch (err) {
    console.error('❌ MOCK: /api/outfits GET failed:', err);
    return NextResponse.json({ 
      error: 'Failed to fetch outfits', 
      details: err instanceof Error ? err.message : 'Unknown error'
    }, { status: 500 });
  }
}

export const runtime = 'edge';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const timestamp = new Date().toISOString();
  console.log(`🔍 DEBUG: Outfits POST route called - MOCK VERSION [${timestamp}]`);
  
  try {
    const body = await req.text();
    console.log("🔍 DEBUG: Request body length:", body.length);
    console.log("🔍 DEBUG: Request body preview:", body.substring(0, 200) + "...");
    
    const requestData = JSON.parse(body);
    
    // Determine if this is outfit creation (has 'items' field) or generation (has 'mood' field)
    const isCreation = requestData.items && Array.isArray(requestData.items);
    console.log("🔍 DEBUG: Request type detected:", isCreation ? "outfit creation" : "outfit generation");
    
    if (isCreation) {
      // Mock outfit creation response
      const mockCreatedOutfit = {
        id: `outfit_${Date.now()}`,
        name: requestData.name || 'Generated Outfit',
        occasion: requestData.occasion || 'Casual',
        style: requestData.style || 'Dark Academia',
        mood: requestData.mood || 'Confident',
        items: requestData.items || [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        matchScore: 85
      };
      
      return NextResponse.json(mockCreatedOutfit);
    } else {
      // Mock outfit generation response
      const mockGeneratedOutfit = {
        id: `outfit_${Date.now()}`,
        name: 'Dark Academia Confident Look',
        occasion: requestData.occasion || 'Casual',
        style: requestData.style || 'Dark Academia',
        mood: requestData.mood || 'Confident',
        items: [
          {
            id: 'item_1',
            name: 'Dark Academia Blazer',
            type: 'blazer',
            color: 'charcoal',
            brand: 'The Savile Row Company'
          },
          {
            id: 'item_3',
            name: 'Slim Fit Pants',
            type: 'pants',
            color: 'olive',
            brand: 'Dockers'
          },
          {
            id: 'item_4',
            name: 'Oxford Shoes',
            type: 'shoes',
            color: 'brown',
            brand: 'Unknown'
          }
        ],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        matchScore: 86,
        aiReasoning: 'Generated 3 items forming a complete Casual outfit with Dark Academia style. Includes required categories: top, bottom, shoes'
      };
      
      return NextResponse.json(mockGeneratedOutfit);
    }
  } catch (err) {
    console.error('❌ MOCK: /api/outfits POST failed:', err);
    return NextResponse.json({ 
      error: 'Failed to process outfit request', 
      details: err instanceof Error ? err.message : 'Unknown error' 
    }, { status: 500 });
  }
}
