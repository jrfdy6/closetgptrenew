import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

const OCCASIONS = ["casual", "formal", "business", "athletic", "party"];
const MOODS = ["energetic", "relaxed", "confident", "playful", "elegant"];
const STYLES = ["classic", "modern", "vintage", "streetwear", "bohemian"];

// Helper function to convert wardrobe items for backend compatibility
function convertWardrobeForBackend(wardrobe: any[]): any[] {
  return wardrobe.map(item => {
    const now = Math.floor(Date.now() / 1000);
    
    // Ensure dominantColors are proper Color objects
    const dominantColors = Array.isArray(item.dominantColors) 
      ? item.dominantColors.map((color: any) => {
          if (typeof color === 'string') {
            // Convert string color to Color object
            return { 
              name: color, 
              hex: "#000000", // Default hex
              rgb: [0, 0, 0]  // Default RGB
            };
          } else if (color && typeof color === 'object' && color.name) {
            // Ensure it has the required structure
            return {
              name: color.name,
              hex: color.hex || "#000000",
              rgb: color.rgb || [0, 0, 0]
            };
          } else {
            // Fallback
            return { name: "Unknown", hex: "#000000", rgb: [0, 0, 0] };
          }
        })
      : [];

    // Ensure matchingColors are proper Color objects
    const matchingColors = Array.isArray(item.matchingColors) 
      ? item.matchingColors.map((color: any) => {
          if (typeof color === 'string') {
            return { 
              name: color, 
              hex: "#000000", 
              rgb: [0, 0, 0] 
            };
          } else if (color && typeof color === 'object' && color.name) {
            return {
              name: color.name,
              hex: color.hex || "#000000",
              rgb: color.rgb || [0, 0, 0]
            };
          } else {
            return { name: "Unknown", hex: "#000000", rgb: [0, 0, 0] };
          }
        })
      : [];

    // Ensure all required fields are present
    return {
      id: item.id || item.itemId || `item-${Date.now()}-${Math.random()}`,
      name: item.name || "Unknown Item",
      type: item.type || "other",
      color: item.color || item.colorName || "Unknown",
      season: Array.isArray(item.season) ? item.season : ["spring", "summer", "fall", "winter"],
      imageUrl: item.imageUrl || item.image || "",
      tags: Array.isArray(item.tags) ? item.tags : [],
      style: Array.isArray(item.style) ? item.style : [],
      userId: item.userId || "default-user",
      dominantColors: dominantColors,
      matchingColors: matchingColors,
      occasion: Array.isArray(item.occasion) ? item.occasion : ["Casual"],
      createdAt: typeof item.createdAt === 'object' && item.createdAt?.seconds 
        ? item.createdAt.seconds 
        : typeof item.createdAt === 'number' 
          ? item.createdAt 
          : now,
      updatedAt: typeof item.updatedAt === 'object' && item.updatedAt?.seconds 
        ? item.updatedAt.seconds 
        : typeof item.updatedAt === 'number' 
          ? item.updatedAt 
          : now,
      subType: item.subType || null,
      brand: item.brand || null,
      colorName: item.colorName || item.color || null,
      metadata: item.metadata || {
        visualAttributes: {
          material: item.material || null,
          pattern: null,
          textureStyle: null,
          fabricWeight: null,
          fit: null,
          silhouette: null,
          length: null,
          genderTarget: null,
          sleeveLength: null,
          hangerPresent: null,
          backgroundRemoved: null,
          wearLayer: null,
          formalLevel: null
        },
        itemMetadata: {
          priceEstimate: null,
          careInstructions: null,
          tags: Array.isArray(item.tags) ? item.tags : []
        },
        colorAnalysis: {
          dominant: dominantColors,
          matching: matchingColors
        },
        originalType: item.type || "other",
        analysisTimestamp: now,
        naturalDescription: null
      },
      embedding: Array.isArray(item.embedding) ? item.embedding : undefined,
      backgroundRemoved: typeof item.backgroundRemoved === 'boolean' ? item.backgroundRemoved : undefined
    };
  });
}

// Helper function to convert user profile for backend compatibility
function convertUserProfileForBackend(userProfile: any): any {
  const now = Math.floor(Date.now() / 1000);
  return {
    id: userProfile?.id || 'default-user',
    name: userProfile?.name || userProfile?.displayName || 'User',
    email: userProfile?.email || 'user@example.com',
    gender: userProfile?.gender || null,
    preferences: {
      style: userProfile?.stylePreferences || [],
      colors: userProfile?.colorPreferences || [],
      occasions: userProfile?.occasionPreferences || []
    },
    measurements: {
      height: userProfile?.measurements?.height || 0,
      weight: userProfile?.measurements?.weight || 0,
      bodyType: userProfile?.bodyType || 'athletic',
      skinTone: userProfile?.skinTone || null
    },
    stylePreferences: userProfile?.stylePreferences || [],
    bodyType: userProfile?.bodyType || 'athletic',
    skinTone: userProfile?.skinTone || null,
    fitPreference: userProfile?.fitPreference || null,
    createdAt: now,
    updatedAt: now
  };
}

export async function POST(request: Request) {
  try {
    console.log('🔍 DEBUG: Outfit generation API called');
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      console.error('❌ DEBUG: No valid authorization header');
      return NextResponse.json(
        { 
          error: "Authentication required",
          details: "No valid authorization token provided"
        },
        { status: 401 }
      );
    }

    console.log('✅ DEBUG: Authorization header present');

    const body = await request.json();
    console.log('🔍 DEBUG: Request body received:', {
      hasOccasion: !!body.occasion,
      hasMood: !!body.mood,
      hasStyle: !!body.style,
      hasWardrobe: !!body.wardrobe,
      wardrobeLength: body.wardrobe?.length || 0,
      hasUserProfile: !!body.userProfile,
      hasWeather: !!body.weather
    });

    let { 
      occasion, 
      mood, 
      style, 
      description,
      wardrobe,
      weather,
      userProfile,
      likedOutfits,
      trendingStyles,
      baseItem
    } = body;

    // If any field is empty, randomize it
    occasion = occasion || OCCASIONS[Math.floor(Math.random() * OCCASIONS.length)];
    mood = mood || MOODS[Math.floor(Math.random() * MOODS.length)];
    style = style || STYLES[Math.floor(Math.random() * STYLES.length)];

    console.log('🔍 DEBUG: Processed parameters:', {
      occasion,
      mood,
      style,
      wardrobeLength: wardrobe?.length || 0
    });

    // Convert wardrobe items for backend compatibility
    const convertedWardrobe = convertWardrobeForBackend(wardrobe || []);
    
    // DEBUG: Log wardrobe conversion
    console.log('🔍 DEBUG: Original wardrobe length:', wardrobe?.length || 0);
    console.log('🔍 DEBUG: Converted wardrobe length:', convertedWardrobe.length);
    console.log('🔍 DEBUG: First 3 converted items:', convertedWardrobe.slice(0, 3).map(item => ({
      id: item.id,
      name: item.name,
      type: item.type,
      dominantColors: item.dominantColors?.length || 0,
      matchingColors: item.matchingColors?.length || 0
    })));
    
    // NEW: More detailed debugging
    console.log('🔍 DEBUG: Original wardrobe sample:', wardrobe?.slice(0, 2).map((item: any) => ({
      id: item.id,
      name: item.name,
      type: item.type,
      style: item.style,
      occasion: item.occasion,
      dominantColors: item.dominantColors,
      matchingColors: item.matchingColors
    })));
    
    console.log('🔍 DEBUG: Converted wardrobe sample:', convertedWardrobe.slice(0, 2).map((item: any) => ({
      id: item.id,
      name: item.name,
      type: item.type,
      style: item.style,
      occasion: item.occasion,
      dominantColors: item.dominantColors,
      matchingColors: item.matchingColors
    })));

    // Convert base item for backend compatibility if provided
    const convertedBaseItem = baseItem ? convertWardrobeForBackend([baseItem])[0] : null;

    // NEW: Retrieve recent outfit history for diversity
    let outfitHistory = [];
    try {
      console.log('🔍 DEBUG: Fetching outfit history from backend...');
      const historyResponse = await fetch(`${API_URL}/api/outfits`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": authHeader,
        },
      });
      
      console.log('🔍 DEBUG: History response status:', historyResponse.status);
      
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        // Get the last 10 outfits for diversity filtering
        outfitHistory = historyData.slice(0, 10).map((outfit: any) => ({
          id: outfit.id,
          items: outfit.items || [],
          createdAt: outfit.createdAt || Date.now(),
          occasion: outfit.occasion,
          style: outfit.style
        }));
        console.log(`📚 Retrieved ${outfitHistory.length} recent outfits for diversity`);
      } else {
        console.warn('🔍 DEBUG: Failed to get outfit history, status:', historyResponse.status);
        // Don't fail the entire request - just continue without history
        outfitHistory = [];
      }
    } catch (error) {
      console.warn('Failed to retrieve outfit history for diversity:', error);
      // Continue without history if retrieval fails
      outfitHistory = [];
    }

    // Log the payload for debugging
    console.log('🔍 DEBUG: Outfit Generation Payload:', {
      occasion,
      mood,
      style,
      description,
      wardrobeSize: convertedWardrobe?.length,
      baseItem: convertedBaseItem ? convertedBaseItem.name : 'None',
      weather,
      userProfile: {
        id: userProfile?.id,
        stylePreferences: userProfile?.stylePreferences,
        bodyType: userProfile?.bodyType
      },
      outfitHistoryCount: outfitHistory.length
    });
    
    // DEBUG: Log the actual payload being sent to backend
    const backendPayload = {
      occasion,
      mood,  // Add mood parameter
      style,  // Add style parameter
      weather: weather,  // Use weather instead of weather_conditions
      wardrobe: convertedWardrobe,  // Add wardrobe
      user_profile: convertUserProfileForBackend(userProfile),  // Add user profile
      likedOutfits: likedOutfits || [],
      trendingStyles: trendingStyles || [],
      outfitHistory: outfitHistory,  // NEW: Add outfit history for diversity
      baseItem: convertedBaseItem  // Add base item
    };
    
    console.log('🔍 DEBUG: Backend payload wardrobe length:', backendPayload.wardrobe.length);
    console.log('🔍 DEBUG: Backend payload first item:', backendPayload.wardrobe[0] ? {
      id: backendPayload.wardrobe[0].id,
      name: backendPayload.wardrobe[0].name,
      type: backendPayload.wardrobe[0].type,
      dominantColors: backendPayload.wardrobe[0].dominantColors?.length || 0,
      matchingColors: backendPayload.wardrobe[0].matchingColors?.length || 0
    } : 'No items');

    console.log('🔍 DEBUG: Making backend API call to:', `${API_URL}/api/outfit/generate`);

    // Forward the request to the backend with authentication header
    const response = await fetch(`${API_URL}/api/outfit/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": authHeader, // Forward the Firebase ID token
      },
      body: JSON.stringify({
        occasion,
        mood,  // Add mood parameter
        style,  // Add style parameter
        weather: weather,  // Use weather instead of weather_conditions
        wardrobe: convertedWardrobe,  // Add wardrobe
        user_profile: convertUserProfileForBackend(userProfile),  // Add user profile
        likedOutfits: likedOutfits || [],
        trendingStyles: trendingStyles || [],
        outfitHistory: outfitHistory,  // NEW: Add outfit history for diversity
        baseItem: convertedBaseItem  // Add base item
      }),
    });

    console.log('🔍 DEBUG: Backend response status:', response.status);
    console.log('🔍 DEBUG: Backend response ok:', response.ok);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Failed to parse error response' }));
      console.error("❌ DEBUG: Backend error:", errorData);
      throw new Error(errorData.detail || errorData.message || 'Failed to generate outfit');
    }

    const data = await response.json();
    
    // Log the response for debugging
    console.log('✅ DEBUG: Generated Outfit:', {
      id: data.id,
      name: data.name,
      occasion: data.occasion,
      style: data.style,
      itemsCount: data.items?.length || 0,
      wasSuccessful: data.wasSuccessful,
      validationErrors: data.validationErrors?.length || 0,
      warnings: data.warnings?.length || 0,
      items: data.items?.map((item: any) => ({
        name: item.name,
        type: item.type,
        style: item.style
      }))
    });

    // NEW: Log warnings and validation details for debugging
    if (data.warnings && data.warnings.length > 0) {
      console.log('⚠️ DEBUG: Outfit Generation Warnings:', data.warnings);
    }
    
    if (data.validation_details) {
      console.log('🔍 DEBUG: Validation Details:', {
        errors: data.validation_details.errors?.length || 0,
        warnings: data.validation_details.warnings?.length || 0,
        fixes: data.validation_details.fixes?.length || 0
      });
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error("Error generating outfit:", error);
    return NextResponse.json(
      { 
        error: "Failed to generate outfit",
        details: error instanceof Error ? error.message : "Unknown error"
      },
      { status: 500 }
    );
  }
} 