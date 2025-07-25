import { describe, it, expect } from 'vitest';
import { transformColorArray, transformItemColors, transformWardrobe } from './transformations';
import { ClothingItem } from '@/types/wardrobe';

describe('transformations', () => {
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

  describe('transformItemColors', () => {
    const baseItem: ClothingItem = {
      id: '1',
      userId: 'user1',
      name: 'Test Item',
      type: 'shirt',
      color: 'Blue',
      season: ['summer'],
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
        }
      }
    };

    it('should transform item colors correctly', () => {
      const result = transformItemColors(baseItem);
      expect(result.metadata.colorAnalysis).toEqual({
        dominant: ['Blue', 'White'],
        matching: ['Gray']
      });
    });

    it('should handle items with only root-level colors', () => {
      const item = {
        ...baseItem,
        metadata: undefined
      };
      const result = transformItemColors(item);
      expect(result.metadata.colorAnalysis).toEqual({
        dominant: ['Blue', 'White'],
        matching: ['Gray']
      });
    });

    it('should handle items with only metadata colors', () => {
      const item = {
        ...baseItem,
        dominantColors: [],
        matchingColors: []
      };
      const result = transformItemColors(item);
      expect(result.metadata.colorAnalysis).toEqual({
        dominant: ['Blue', 'White'],
        matching: ['Gray']
      });
    });
  });

  describe('transformWardrobe', () => {
    const baseItem: ClothingItem = {
      id: '1',
      userId: 'user1',
      name: 'Test Item',
      type: 'shirt',
      color: 'Blue',
      season: ['summer'],
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
        }
      }
    };

    it('should transform multiple items correctly', () => {
      const wardrobe = [
        baseItem,
        {
          ...baseItem,
          id: '2',
          dominantColors: [{ name: 'Red', hex: '#FF0000', rgb: [255, 0, 0] }],
          matchingColors: [{ name: 'Black', hex: '#000000', rgb: [0, 0, 0] }]
        }
      ];

      const result = transformWardrobe(wardrobe);
      expect(result).toHaveLength(2);
      expect(result[0].metadata.colorAnalysis).toEqual({
        dominant: ['Blue', 'White'],
        matching: ['Gray']
      });
      expect(result[1].metadata.colorAnalysis).toEqual({
        dominant: ['Red'],
        matching: ['Black']
      });
    });

    it('should handle empty wardrobe', () => {
      const result = transformWardrobe([]);
      expect(result).toEqual([]);
    });
  });
}); 