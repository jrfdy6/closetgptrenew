// Simple test script to verify outfit generation
const API_URL = 'http://localhost:3001';

async function testOutfitGeneration() {
  try {
    console.log('Testing outfit generation...');
    
    const testPayload = {
      occasion: 'casual',
      mood: 'confident',
      style: 'streetwear',
      description: 'Test outfit',
      wardrobe: [
        {
          id: 'test-1',
          name: 'Test Shirt',
          type: 'shirt',
          color: 'blue',
          season: ['spring', 'summer'],
          imageUrl: 'https://example.com/shirt.jpg',
          tags: ['casual'],
          style: ['streetwear'],
          userId: 'test-user',
          dominantColors: [{ name: 'blue', hex: '#0000FF', rgb: [0, 0, 255] }],
          matchingColors: [{ name: 'white', hex: '#FFFFFF', rgb: [255, 255, 255] }],
          occasion: ['casual'],
          brand: 'Test Brand',
          createdAt: Math.floor(Date.now() / 1000),
          updatedAt: Math.floor(Date.now() / 1000),
          subType: null,
          colorName: null,
          backgroundRemoved: false,
          embedding: null,
          metadata: null
        }
      ],
      weather: {
        temperature: 70,
        condition: 'sunny',
        location: 'default',
        humidity: 50,
        wind_speed: 5,
        precipitation: 0
      },
      user_profile: {
        id: 'test-user',
        name: 'Test User',
        email: 'test@example.com',
        gender: null,
        preferences: {
          style: ['streetwear'],
          colors: [],
          occasions: []
        },
        measurements: {
          height: 0,
          weight: 0,
          bodyType: 'athletic',
          skinTone: null
        },
        stylePreferences: ['streetwear'],
        bodyType: 'athletic',
        skinTone: null,
        fitPreference: null,
        createdAt: Math.floor(Date.now() / 1000),
        updatedAt: Math.floor(Date.now() / 1000)
      },
      likedOutfits: [],
      trendingStyles: []
    };

    const response = await fetch(`${API_URL}/api/outfit/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testPayload),
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Backend error:', errorData);
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(errorData)}`);
    }

    const data = await response.json();
    console.log('✅ Outfit generation successful!');
    console.log('Generated outfit:', {
      id: data.id,
      name: data.name,
      occasion: data.occasion,
      style: data.style,
      pieces: data.pieces?.length || 0
    });
    
  } catch (error) {
    console.error('❌ Outfit generation failed:', error.message);
  }
}

testOutfitGeneration(); 