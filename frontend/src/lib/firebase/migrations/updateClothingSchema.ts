import { config } from 'dotenv';
import { resolve } from 'path';
import { readFileSync } from 'fs';

// Load environment variables from .env.local
const envPath = resolve(__dirname, '../../../../.env.local');
console.log('Loading environment from:', envPath);
config({ path: envPath });

// Debug: Check if environment variables are loaded
console.log('Firebase API Key loaded:', process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? 'Yes' : 'No');
console.log('Firebase Project ID loaded:', process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ? 'Yes' : 'No');

// --- ADMIN SDK SETUP ---
import admin from 'firebase-admin';

const serviceAccountPath = resolve(__dirname, '../../../../serviceAccountKey.json');
const serviceAccount = JSON.parse(readFileSync(serviceAccountPath, 'utf8'));

if (!admin.apps.length) {
  admin.initializeApp({
    credential: admin.credential.cert(serviceAccount),
    databaseURL: `https://${process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID}.firebaseio.com`,
  });
}

const db = admin.firestore();

import { ClothingItem, ClothingTypeEnum, SeasonEnum, MaterialEnum, BodyTypeEnum, SkinToneEnum } from '@shared/types';
import { z } from 'zod';

// Define the material type directly from the enum values
type Material = 'cotton' | 'wool' | 'silk' | 'linen' | 'denim' | 'leather' | 'synthetic' | 'knit' | 'fleece' | 'other';
type Season = 'winter' | 'summer' | 'spring' | 'fall';
type BodyType = 'hourglass' | 'pear' | 'apple' | 'rectangle' | 'inverted_triangle';
type SkinTone = 'warm' | 'cool' | 'neutral';

interface OldClothingItem {
  id: string;
  type: string;
  subType?: string;
  color?: string;
  season?: string[];
  imageUrl?: string;
  tags?: string[];
  style?: string[];
  dominantColors?: Array<{ name: string; hex: string; rgb: [number, number, number] }>;
  matchingColors?: Array<{ name: string; hex: string; rgb: [number, number, number] }>;
  occasion?: string[];
  metadata?: {
    basicMetadata?: Record<string, any>;
    visualAttributes?: Record<string, any>;
    itemMetadata?: {
      tags?: string[];
      brand?: string | null;
      priceEstimate?: number | null;
      careInstructions?: string | null;
      outfitScoring?: {
        versatility: number;
        seasonality: number;
        formality: number;
        trendiness: number;
        quality: number;
      };
    };
  };
}

// Temperature range definitions with material types
const TEMPERATURE_RANGES = {
  FREEZING: { min: -Infinity, max: 32, layers: ['wool', 'fleece', 'knit'] as Material[] },
  COLD: { min: 32, max: 50, layers: ['wool', 'knit'] as Material[] },
  CHILLY: { min: 50, max: 65, layers: ['cotton'] as Material[] },
  MILD: { min: 65, max: 75, layers: ['cotton', 'linen'] as Material[] },
  WARM: { min: 75, max: 85, layers: ['cotton', 'linen', 'silk'] as Material[] },
  HOT: { min: 85, max: Infinity, layers: ['cotton', 'linen'] as Material[] }
} as const;

// Material compatibility rules
const MATERIAL_COMPATIBILITY: Record<Material, Material[]> = {
  cotton: ['denim', 'linen', 'wool', 'silk'] as Material[],
  denim: ['cotton', 'leather', 'wool'] as Material[],
  wool: ['cotton', 'silk', 'knit'] as Material[],
  silk: ['cotton', 'wool', 'knit'] as Material[],
  leather: ['denim', 'cotton', 'wool'] as Material[],
  linen: ['cotton', 'silk'] as Material[],
  synthetic: ['cotton', 'denim'] as Material[],
  knit: ['wool', 'silk', 'cotton'] as Material[],
  fleece: ['cotton', 'wool'] as Material[],
  other: ['cotton', 'denim'] as Material[]
};

// Weather-appropriate materials
const WEATHER_MATERIALS: Record<Season, Material[]> = {
  winter: ['wool', 'knit', 'leather', 'fleece'] as Material[],
  summer: ['cotton', 'linen', 'silk'] as Material[],
  spring: ['cotton', 'linen', 'knit'] as Material[],
  fall: ['wool', 'cotton', 'denim', 'leather'] as Material[]
};

// Skin tone color compatibility
const SKIN_TONE_COLORS: Record<SkinTone, string[]> = {
  warm: ['coral', 'peach', 'gold', 'olive', 'terracotta', 'warm_red'],
  cool: ['blue', 'purple', 'pink', 'silver', 'cool_red', 'emerald'],
  neutral: ['navy', 'gray', 'white', 'black', 'beige', 'mauve']
};

// Body type fit recommendations
const BODY_TYPE_FITS = {
  recommendedFits: {
    hourglass: ['fitted', 'relaxed'],
    pear: ['fitted_top', 'relaxed_bottom'],
    apple: ['relaxed_top', 'fitted_bottom'],
    rectangle: ['fitted', 'oversized'],
    inverted_triangle: ['relaxed_top', 'fitted_bottom']
  } as Record<BodyType, string[]>,
  styleRecommendations: {
    hourglass: ['balanced', 'defined_waist'],
    pear: ['balance_top', 'accentuate_waist'],
    apple: ['elongate', 'define_waist'],
    rectangle: ['create_curves', 'add_dimension'],
    inverted_triangle: ['balance_shoulders', 'create_waist']
  } as Record<BodyType, string[]>
};

export async function migrateClothingItems(): Promise<void> {
  console.log('Starting clothing items migration...');
  
  try {
    // Get all wardrobe items
    const wardrobeRef = db.collection('wardrobe');
    const snapshot = await wardrobeRef.get();
    
    if (snapshot.empty) {
      console.log('No items to migrate');
      return;
    }
    
    console.log(`Found ${snapshot.size} items to migrate`);
    
    // Create a batch for efficient updates
    const batch = db.batch();
    let count = 0;
    
    // Process each item
    for (const doc of snapshot.docs) {
      const oldItem = doc.data() as OldClothingItem;
      const now = Date.now();
      
      // Determine temperature compatibility based on item type and material
      const material = (oldItem.metadata?.visualAttributes?.material?.toLowerCase() || 'cotton') as Material;
      const type = oldItem.type.toLowerCase();
      
      // Set temperature ranges based on item type and material
      let minTemp = 32;
      let maxTemp = 75;
      let recommendedLayers: Material[] = ['cotton'];
      
      if (type.includes('jacket') || type.includes('coat')) {
        minTemp = -Infinity;
        maxTemp = 50;
        recommendedLayers = ['wool', 'fleece', 'knit'];
      } else if (type.includes('sweater')) {
        minTemp = 32;
        maxTemp = 65;
        recommendedLayers = ['wool', 'knit'];
      }
      
      // Get material preferences based on temperature
      const materialPreferences = Object.entries(TEMPERATURE_RANGES)
        .filter(([_, range]) => minTemp <= range.max && maxTemp >= range.min)
        .flatMap(([_, range]) => range.layers);
      
      // Create new item with updated schema
      const newItem: Partial<ClothingItem> = {
        id: oldItem.id,
        name: oldItem.id,
        type: oldItem.type as any,
        subType: oldItem.subType || '',
        color: oldItem.color || '',
        season: oldItem.season?.map(s => s as any) || [],
        imageUrl: oldItem.imageUrl || '',
        tags: oldItem.tags || [],
        style: oldItem.style || [],
        dominantColors: oldItem.dominantColors || [],
        matchingColors: oldItem.matchingColors || [],
        occasion: oldItem.occasion || [],
        createdAt: now,
        updatedAt: now,
        metadata: {
          originalType: oldItem.type,
          analysisTimestamp: now,
          colorAnalysis: {
            dominant: oldItem.dominantColors || [],
            matching: oldItem.matchingColors || []
          },
          basicMetadata: oldItem.metadata?.basicMetadata || {},
          visualAttributes: {
            ...oldItem.metadata?.visualAttributes,
            temperatureCompatibility: {
              minTemp,
              maxTemp,
              recommendedLayers,
              materialPreferences
            },
            materialCompatibility: {
              compatibleMaterials: MATERIAL_COMPATIBILITY[material] || [],
              weatherAppropriate: WEATHER_MATERIALS
            },
            bodyTypeCompatibility: BODY_TYPE_FITS,
            skinToneCompatibility: {
              compatibleColors: SKIN_TONE_COLORS,
              recommendedPalettes: {
                warm: ['warm_autumn', 'warm_spring'],
                cool: ['cool_winter', 'cool_summer'],
                neutral: ['neutral_autumn', 'neutral_spring']
              }
            },
            outfitScoring: {
              versatility: 5,
              seasonality: 5,
              formality: 5,
              trendiness: 5,
              quality: 5
            }
          },
          itemMetadata: {
            ...oldItem.metadata?.itemMetadata,
            tags: oldItem.metadata?.itemMetadata?.tags || []
          }
        }
      };
      
      // Update the document
      batch.update(doc.ref, newItem);
      count++;
      
      // Commit every 500 items to avoid batch size limits
      if (count % 500 === 0) {
        await batch.commit();
        console.log(`Migrated ${count} items`);
      }
    }
    
    // Commit any remaining items
    if (count % 500 !== 0) {
      await batch.commit();
    }
    
    console.log(`Successfully migrated ${count} items`);
    
  } catch (error) {
    console.error('Error during migration:', error);
    throw error;
  }
} 