import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useOutfitGenerator, transformColorArray } from './useOutfitGenerator';
import { vi } from 'vitest';

// Mock fetch globally
global.fetch = vi.fn();

describe('useOutfitGenerator', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('transformColorArray', () => {
    it('should transform string colors correctly', () => {
      const colors = ['Red', 'Blue', 'Green'];
      const result = transformColorArray(colors);
      expect(result).toEqual(['Red', 'Blue', 'Green']);
    });

    it('should transform color objects correctly', () => {
      const colors = [
        { name: 'Red', hex: '#FF0000', rgb: [255, 0, 0] },
        { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] }
      ];
      const result = transformColorArray(colors);
      expect(result).toEqual(['Red', 'Blue']);
    });

    it('should handle color objects with empty names', () => {
      const colors = [
        { name: '', hex: '#FF0000', rgb: [255, 0, 0] },
        { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] }
      ];
      const result = transformColorArray(colors);
      expect(result).toEqual(['Blue']);
    });

    it('should handle color objects with missing name properties', () => {
      const colors = [
        { hex: '#FF0000', rgb: [255, 0, 0] },
        { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] }
      ];
      const result = transformColorArray(colors);
      expect(result).toEqual(['Blue']);
    });

    it('should handle mixed input types', () => {
      const colors = [
        'Red',
        { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] },
        'Green'
      ];
      const result = transformColorArray(colors);
      expect(result).toEqual(['Red', 'Blue', 'Green']);
    });

    it('should handle empty or invalid input', () => {
      expect(transformColorArray([])).toEqual([]);
      expect(transformColorArray(null as any)).toEqual([]);
      expect(transformColorArray(undefined as any)).toEqual([]);
    });
  });

  describe('wardrobe transformation', () => {
    const baseItem = {
      id: '1',
      userId: 'user1',
      name: 'Test Item',
      type: 'shirt' as const,
      color: 'Blue',
      season: ['summer' as const],
      imageUrl: 'test.jpg',
      style: ['casual'],
      occasion: ['everyday'],
      tags: [],
      dominantColors: [
        { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] },
        { name: 'White', hex: '#FFFFFF', rgb: [255, 255, 255] }
      ],
      matchingColors: [
        { name: 'Gray', hex: '#808080', rgb: [128, 128, 128] }
      ],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      metadata: {
        analysisTimestamp: Date.now(),
        originalType: 'shirt',
        styleTags: ['casual'],
        occasionTags: ['everyday'],
        colorAnalysis: {
          dominant: [
            { name: 'Blue', hex: '#0000FF', rgb: [0, 0, 255] },
            { name: 'White', hex: '#FFFFFF', rgb: [255, 255, 255] }
          ],
          matching: [
            { name: 'Gray', hex: '#808080', rgb: [128, 128, 128] }
          ]
        },
        basicMetadata: {
          width: 800,
          height: 600,
          orientation: 'portrait',
          dateTaken: new Date().toISOString(),
          deviceModel: 'iPhone 12',
          flashUsed: false
        },
        visualAttributes: {
          material: 'cotton',
          pattern: 'solid',
          textureStyle: 'smooth',
          fabricWeight: 'medium',
          fit: 'slim',
          silhouette: 'regular',
          length: 'regular',
          genderTarget: 'unisex',
          sleeveLength: 'short',
          hangerPresent: false,
          backgroundRemoved: true,
          wearLayer: 'base',
          formalLevel: 'casual'
        },
        itemMetadata: {
          priceEstimate: '50',
          careInstructions: 'Machine wash cold',
          tags: ['casual', 'everyday']
        }
      }
    };

    it('should transform wardrobe items correctly', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve({ data: { wardrobe: [{ metadata: { colorAnalysis: { dominant: ['Blue', 'White'], matching: ['Gray'] } } }] } }) };
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useOutfitGenerator());
      const transformedWardrobe = await result.current.generateOutfit({
        occasion: 'casual',
        weather: {
          temperature: 20,
          condition: 'sunny',
          humidity: 50,
          wind_speed: 10,
          location: 'New York',
          precipitation: 0
        },
        wardrobe: [baseItem],
        userProfile: {
          id: 'user1',
          name: 'Test User',
          email: 'test@example.com',
          preferences: {},
          stylePreferences: [],
          favoriteColors: [],
          favoriteSeasons: [],
          createdAt: Date.now(),
          updatedAt: Date.now()
        },
        likedOutfits: [],
        trendingStyles: [],
        preferences: {},
        outfitHistory: [],
        randomSeed: 123
      });
      
      // The wardrobe should be transformed with string colors
      expect(transformedWardrobe.data.wardrobe[0].metadata.colorAnalysis).toEqual({
        dominant: ['Blue', 'White'],
        matching: ['Gray']
      });
    });
  });
}); 