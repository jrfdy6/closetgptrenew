import { generateOutfit } from '../app/services/outfitGenerationService';
import { OutfitGenerationContext } from '../src/types/outfit';
import { ClothingItem } from '../src/types/wardrobe';
import { WeatherData } from '../src/types/weather';
import { OutfitContext } from '../src/types/outfit_context';

// Mock OpenAI client
jest.mock('openai', () => {
  return {
    OpenAI: jest.fn().mockImplementation(() => ({
      chat: {
        completions: {
          create: jest.fn().mockResolvedValue({
            choices: [{
              message: {
                content: JSON.stringify({
                  name: "Test Outfit",
                  description: "A test outfit description",
                  items: ["item1", "item2"],
                  metadata: {
                    colorHarmony: "Neutral color palette with complementary accents",
                    styleNotes: "Minimalist and clean",
                    styleCompliance: "High compliance with minimalist style",
                    contextCompliance: "Appropriate for casual occasion",
                    weatherAppropriateness: "Suitable for mild weather"
                  }
                })
              }
            }]
          })
        }
      }
    }))
  };
});

describe('Outfit Generation Service', () => {
  const sampleWardrobe: ClothingItem[] = [
    {
      id: 'item1',
      name: 'Black Blazer',
      type: 'outerwear',
      color: 'black',
      style: ['classic', 'minimalist'],
      occasion: ['Business Casual', 'Business Formal', 'Office'],
      metadata: {
        visualAttributes: {
          material: 'wool',
          fit: 'tailored',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item2',
      name: 'White Button-Up Shirt',
      type: 'top',
      color: 'white',
      style: ['classic', 'minimalist'],
      occasion: ['Business Casual', 'Business Formal', 'Office'],
      metadata: {
        visualAttributes: {
          material: 'cotton',
          fit: 'fitted',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item3',
      name: 'Black Slacks',
      type: 'bottom',
      color: 'black',
      style: ['classic', 'minimalist'],
      occasion: ['Business Casual', 'Business Formal', 'Office'],
      metadata: {
        visualAttributes: {
          material: 'wool',
          fit: 'tailored',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item4',
      name: 'Blue Jeans',
      type: 'bottom',
      color: 'blue',
      style: ['casual'],
      occasion: ['Casual', 'Errand-Running'],
      metadata: {
        visualAttributes: {
          material: 'denim',
          fit: 'relaxed',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item5',
      name: 'White Sneakers',
      type: 'footwear',
      color: 'white',
      style: ['casual', 'minimalist'],
      occasion: ['Casual', 'Errand-Running'],
      metadata: {
        visualAttributes: {
          material: 'leather',
          fit: 'standard',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item6',
      name: 'Black Leather Jacket',
      type: 'outerwear',
      color: 'black',
      style: ['grunge', 'bold'],
      occasion: ['Evening / Night Out', 'Date Night'],
      metadata: {
        visualAttributes: {
          material: 'leather',
          fit: 'fitted',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item7',
      name: 'Red Dress',
      type: 'dress',
      color: 'red',
      style: ['bold', 'playful'],
      occasion: ['Date Night', 'Evening / Night Out'],
      metadata: {
        visualAttributes: {
          material: 'silk',
          fit: 'fitted',
          pattern: 'solid'
        }
      }
    },
    {
      id: 'item8',
      name: 'Black Heels',
      type: 'footwear',
      color: 'black',
      style: ['classic', 'bold'],
      occasion: ['Business Formal', 'Evening / Night Out', 'Date Night'],
      metadata: {
        visualAttributes: {
          material: 'leather',
          fit: 'standard',
          pattern: 'solid'
        }
      }
    }
  ];

  const testContext: OutfitGenerationContext = {
    wardrobe: sampleWardrobe,
    weather: {
      condition: 'Sunny',
      temperature: 22,
      location: 'New York'
    },
    occasion: 'Date Night',
    userProfile: {
      stylePreferences: ['classic', 'bold'],
      measurements: {
        bodyType: 'average'
      }
    }
  };

  const mockWardrobe: ClothingItem[] = [
    {
      id: '1',
      name: 'White T-shirt',
      type: 'top',
      color: 'white',
      style: ['minimalist'],
      occasion: ['casual'],
      metadata: {
        visualAttributes: {
          material: 'cotton',
          fit: 'regular'
        }
      }
    },
    {
      id: '2',
      name: 'Blue Jeans',
      type: 'bottom',
      color: 'blue',
      style: ['minimalist'],
      occasion: ['casual'],
      metadata: {
        visualAttributes: {
          material: 'denim',
          fit: 'slim'
        }
      }
    }
  ];

  const mockWeather: WeatherData = {
    condition: 'sunny',
    temperature: 22,
    location: 'New York'
  };

  const mockContext: OutfitContext = {
    formalityLevel: 'Casual',
    activityContext: 'Office',
    weatherContext: 'Hot Weather',
    moodContext: 'Confident',
    culturalSeasonalContext: 'Summer in the City'
  };

  it('should generate an outfit for a date night', async () => {
    const outfit = await generateOutfit(testContext);
    
    // Basic validation
    expect(outfit).toBeDefined();
    expect(outfit.name).toBeDefined();
    expect(outfit.description).toBeDefined();
    expect(outfit.items).toBeInstanceOf(Array);
    expect(outfit.items.length).toBeGreaterThan(0);
    
    // Metadata validation
    expect(outfit.metadata).toBeDefined();
    expect(outfit.metadata.colorHarmony).toBeDefined();
    expect(outfit.metadata.styleNotes).toBeDefined();
    expect(outfit.metadata.styleCompliance).toBeDefined();
    expect(outfit.metadata.contextCompliance).toBeDefined();
    expect(outfit.metadata.weatherAppropriateness).toBeDefined();

    // Log the generated outfit for inspection
    console.log('Generated Outfit:', JSON.stringify(outfit, null, 2));
  });

  it('should generate different outfits with different random seeds', async () => {
    const outfit1 = await generateOutfit({
      ...testContext,
      randomSeed: 0.1
    });
    
    const outfit2 = await generateOutfit({
      ...testContext,
      randomSeed: 0.2
    });

    // The outfits should be different
    expect(outfit1.items).not.toEqual(outfit2.items);
  });

  it('should respect style preferences', async () => {
    const outfit = await generateOutfit(testContext);
    
    // Check if the selected items match the user's style preferences
    const selectedItems = sampleWardrobe.filter(item => 
      outfit.items.includes(item.id)
    );

    const hasPreferredStyle = selectedItems.some(item =>
      item.style.some(style => 
        testContext.userProfile.stylePreferences.includes(style)
      )
    );

    expect(hasPreferredStyle).toBe(true);
  });

  it('should respect occasion requirements', async () => {
    const outfit = await generateOutfit(testContext);
    
    // Check if the selected items are appropriate for the occasion
    const selectedItems = sampleWardrobe.filter(item => 
      outfit.items.includes(item.id)
    );

    const isAppropriateForOccasion = selectedItems.every(item =>
      item.occasion.includes(testContext.occasion)
    );

    expect(isAppropriateForOccasion).toBe(true);
  });

  it('should generate an outfit based on wardrobe items and context', async () => {
    const result = await generateOutfit({
      wardrobe: mockWardrobe,
      weather: mockWeather,
      occasion: 'casual',
      userProfile: {
        stylePreferences: ['minimalist'],
        measurements: {
          bodyType: 'average'
        }
      }
    });

    expect(result).toBeDefined();
    expect(result.name).toBe('Test Outfit');
    expect(result.items).toHaveLength(2);
    expect(result.metadata.styleCompliance).toBeDefined();
  });

  it('should handle empty wardrobe gracefully', async () => {
    const result = await generateOutfit({
      wardrobe: [],
      weather: mockWeather,
      occasion: 'casual',
      userProfile: {
        stylePreferences: ['minimalist'],
        measurements: {
          bodyType: 'average'
        }
      }
    });

    expect(result).toBeDefined();
    expect(result.items).toHaveLength(0);
  });

  it('should respect user style preferences', async () => {
    const result = await generateOutfit({
      wardrobe: mockWardrobe,
      weather: mockWeather,
      occasion: 'casual',
      userProfile: {
        stylePreferences: ['minimalist'],
        measurements: {
          bodyType: 'average'
        }
      }
    });

    expect(result.metadata.styleCompliance).toContain('minimalist');
  });
}); 