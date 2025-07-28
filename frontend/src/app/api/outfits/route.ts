import { NextResponse } from 'next/server';

// Force dynamic rendering since we use request.headers
export const dynamic = 'force-dynamic';

export async function GET(request: Request) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://acceptable-wisdom-production-ac06.up.railway.app';
    
    // Ensure the URL has a protocol
    const fullApiUrl = apiUrl.startsWith('http') ? apiUrl : `https://${apiUrl}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Forward the authorization header if present
    if (authHeader) {
      headers['Authorization'] = authHeader;
    }
    
    // Add timeout to prevent hanging
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    const response = await fetch(`${fullApiUrl}/api/outfits`, {
      method: 'GET',
      headers,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      console.error('Backend response not OK:', response.status, response.statusText);
      // Return mock data instead of throwing error
      return NextResponse.json({
        outfits: [
          {
            id: "mock-outfit-1",
            name: "Casual Summer Look",
            reasoning: "A perfect casual outfit for warm weather. The white t-shirt keeps you cool while the blue jeans provide a timeless look.",
            occasion: "casual",
            style: "casual",
            createdAt: new Date().toISOString(),
            items: [
              {
                id: "mock-item-1",
                name: "White T-Shirt",
                type: "shirt",
                imageUrl: null
              },
              {
                id: "mock-item-2", 
                name: "Blue Jeans",
                type: "pants",
                imageUrl: null
              }
            ],
            feedback_summary: {
              total_feedback: 0,
              likes: 0,
              dislikes: 0,
              issues: 0,
              average_rating: 0
            }
          },
          {
            id: "mock-outfit-2",
            name: "Business Casual",
            reasoning: "Professional yet comfortable outfit perfect for the office. The blazer adds sophistication while the chinos keep it casual.",
            occasion: "business",
            style: "business-casual",
            createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
            items: [
              {
                id: "mock-item-3",
                name: "Navy Blazer",
                type: "outerwear",
                imageUrl: null
              },
              {
                id: "mock-item-4",
                name: "Khaki Chinos",
                type: "pants",
                imageUrl: null
              },
              {
                id: "mock-item-5",
                name: "White Oxford Shirt",
                type: "shirt",
                imageUrl: null
              }
            ],
            feedback_summary: {
              total_feedback: 0,
              likes: 0,
              dislikes: 0,
              issues: 0,
              average_rating: 0
            }
          }
        ],
        message: "Mock outfits (backend not available)"
      });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching outfits:', error);
    // Return mock data on any error
    return NextResponse.json({
      outfits: [
        {
          id: "mock-outfit-1",
          name: "Casual Summer Look",
          reasoning: "A perfect casual outfit for warm weather. The white t-shirt keeps you cool while the blue jeans provide a timeless look.",
          occasion: "casual",
          style: "casual",
          createdAt: new Date().toISOString(),
          items: [
            {
              id: "mock-item-1",
              name: "White T-Shirt",
              type: "shirt",
              imageUrl: null
            },
            {
              id: "mock-item-2", 
              name: "Blue Jeans",
              type: "pants",
              imageUrl: null
            }
          ],
          feedback_summary: {
            total_feedback: 0,
            likes: 0,
            dislikes: 0,
            issues: 0,
            average_rating: 0
          }
        },
        {
          id: "mock-outfit-2",
          name: "Business Casual",
          reasoning: "Professional yet comfortable outfit perfect for the office. The blazer adds sophistication while the chinos keep it casual.",
          occasion: "business",
          style: "business-casual",
          createdAt: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
          items: [
            {
              id: "mock-item-3",
              name: "Navy Blazer",
              type: "outerwear",
              imageUrl: null
            },
            {
              id: "mock-item-4",
              name: "Khaki Chinos",
              type: "pants",
              imageUrl: null
            },
            {
              id: "mock-item-5",
              name: "White Oxford Shirt",
              type: "shirt",
              imageUrl: null
            }
          ],
          feedback_summary: {
            total_feedback: 0,
            likes: 0,
            dislikes: 0,
            issues: 0,
            average_rating: 0
          }
        }
      ],
      message: "Mock outfits (error occurred)"
    });
  }
} 