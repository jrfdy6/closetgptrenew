import {
  collection,
  doc,
  getDocs,
  getDoc,
  addDoc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  writeBatch,
  setDoc
} from "firebase/firestore";
import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import { typedDb as db } from './index';
import { storage } from './config';
import { analyzeClothingImage } from '../services/clothingImageAnalysis';
import {
  ClothingItem,
  ClothingItemSchema,
  OpenAIClothingAnalysis,
  OpenAIClothingAnalysisSchema
} from '@shared/types';
import { ApiResponse } from '@shared/types/responses';
import {
  validateOpenAIAnalysis,
  convertOpenAIAnalysisToClothingItem,
  createSuccessResponse,
  createErrorResponse,
  validateClothingItem,
  validateClothingItems
} from '@/lib/utils/validation';
import { uploadMultipleImages, deleteMultipleImages, UploadedImage, uploadImage } from "./storageService";
import { createHash } from 'crypto';
import { z } from 'zod';
import { createClothingItemFromAnalysis } from '@/lib/utils/itemProcessing';
import { wardrobeApi } from '../api/wardrobeApi';
import { v4 as uuidv4 } from 'uuid';
import { convertToWebP } from '../utils/imageProcessing';
import { getAuth } from 'firebase/auth';

// Collection reference
const WARDROBE_COLLECTION = "wardrobe";

// Type definitions
type ProcessImagesResult = {
  success: boolean;
  data?: {
    newItems: ClothingItem[];
    totalProcessed: number;
    successfulUploads: number;
  };
  error?: string;
};

type ProcessImagesResponse = ApiResponse<{
  newItems: ClothingItem[];
  totalProcessed: number;
  successfulUploads: number;
} | null>;

type WardrobeItemResponse = ApiResponse<ClothingItem | null>;
type WardrobeItemsResponse = ApiResponse<ClothingItem[] | null>;
type ImageAnalysisResult = OpenAIClothingAnalysis;
type ImageAnalysisResponse = ApiResponse<ImageAnalysisResult | null>;

function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

interface DuplicateCheckResult {
  success: boolean;
  data?: {
    uniqueImages: File[];
    duplicateHashes: string[];
    similarImages: Array<{
      file: File;
      existingItem: ClothingItem;
      similarity: number;
    }>;
  };
  error?: string;
}

// Calculate SHA-256 hash of a file
const calculateFileHash = async (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const buffer = e.target?.result as ArrayBuffer;
        const hash = createHash('sha256').update(Buffer.from(buffer)).digest('hex');
        resolve(hash);
      } catch (error) {
        reject(error);
      }
    };
    reader.onerror = (error) => reject(error);
    reader.readAsArrayBuffer(file);
  });
};

// Calculate image similarity using perceptual hash
const calculateImageSimilarity = async (file1: File, file2Url: string): Promise<number> => {
  try {
    // Fetch the second image from URL
    const response = await fetch(file2Url);
    const blob = await response.blob();
    const file2 = new File([blob], 'existing-image', { type: blob.type });

    // Calculate hashes
    const hash1 = await calculateFileHash(file1);
    const hash2 = await calculateFileHash(file2);
    
    // Calculate Hamming distance between hashes
    let distance = 0;
    for (let i = 0; i < hash1.length; i++) {
      if (hash1[i] !== hash2[i]) distance++;
    }
    
    // Convert to similarity score (0-1)
    return 1 - (distance / hash1.length);
  } catch (error) {
    console.error('Error calculating image similarity:', error);
    return 0; // Return 0 similarity on error
  }
};

// Get wardrobe items
export const getWardrobeItems = async (userId: string): Promise<WardrobeItemsResponse> => {
  try {
    console.log('getWardrobeItems called with userId:', userId);
    
    if (!userId) {
      console.error('getWardrobeItems: No userId provided');
      return {
        success: false,
        error: 'User ID is required',
        data: null
      };
    }

    if (!db) {
      console.error('getWardrobeItems: Firestore is not initialized');
      return {
        success: false,
        error: 'Database is not initialized',
        data: null
      };
    }

    // Check authentication
    const auth = getAuth();
    const currentUser = auth.currentUser;
    
    if (!currentUser) {
      console.error('getWardrobeItems: No authenticated user');
      return {
        success: false,
        error: 'User not authenticated',
        data: null
      };
    }

    if (currentUser.uid !== userId) {
      console.error('getWardrobeItems: User ID mismatch', {
        currentUser: currentUser.uid,
        requestedUser: userId
      });
      return {
        success: false,
        error: 'User ID mismatch',
        data: null
      };
    }

    console.log('getWardrobeItems: Querying Firestore...');
    
    // Try different query approaches
    let snapshot;
    let queryMethod = 'default';
    
    try {
      // Method 1: Standard query
      const itemsRef = collection(db, WARDROBE_COLLECTION);
      const q = query(itemsRef, where('userId', '==', userId));
      console.log('getWardrobeItems: Query constructed:', {
        collection: WARDROBE_COLLECTION,
        filter: { field: 'userId', operator: '==', value: userId }
      });
      
      snapshot = await getDocs(q);
      queryMethod = 'standard';
      console.log('getWardrobeItems: Standard query successful');
      
    } catch (error) {
      console.warn('getWardrobeItems: Standard query failed, trying fallback:', error);
      
      try {
        // Method 2: Simple collection query without where clause
        const itemsRef = collection(db, WARDROBE_COLLECTION);
        snapshot = await getDocs(itemsRef);
        queryMethod = 'simple';
        console.log('getWardrobeItems: Simple query successful');
        
        // Filter results in memory
        const filteredDocs = snapshot.docs.filter(doc => {
          const data = doc.data();
          return data.userId === userId;
        });
        
        // Create a new snapshot-like object
        snapshot = {
          docs: filteredDocs,
          empty: filteredDocs.length === 0,
          size: filteredDocs.length,
          forEach: (callback: any) => filteredDocs.forEach(callback)
        };
        
      } catch (fallbackError) {
        console.error('getWardrobeItems: All query methods failed:', fallbackError);
        return {
          success: false,
          error: `Failed to query wardrobe: ${fallbackError instanceof Error ? fallbackError.message : 'Unknown error'}`,
          data: null
        };
      }
    }
    
    console.log('getWardrobeItems: Firestore query complete. Found', snapshot.docs.length, 'documents using method:', queryMethod);
    
    // Process items with better error handling
    const items: ClothingItem[] = [];
    const errors: string[] = [];
    
    for (const doc of snapshot.docs) {
      try {
        console.log('getWardrobeItems: Processing document', doc.id);
        const data = doc.data();
        
        // Validate that this document belongs to the user
        if (data.userId !== userId) {
          console.warn('getWardrobeItems: Skipping document with mismatched userId:', {
            docId: doc.id,
            docUserId: data.userId,
            requestedUserId: userId
          });
          continue;
        }
        
        // Safely handle timestamp conversion
        let createdAt: number;
        let updatedAt: number;
        
        try {
          createdAt = data.createdAt || Date.now();
          if (typeof createdAt === 'string') {
            createdAt = new Date(createdAt).getTime();
          } else if (typeof createdAt === 'object' && createdAt && 'seconds' in createdAt) {
            // Handle Firestore Timestamp objects
            createdAt = (createdAt as any).seconds * 1000;
          } else if (typeof createdAt === 'number') {
            // Already a number
          } else {
            createdAt = Date.now();
          }
        } catch (error) {
          console.warn('Invalid createdAt timestamp for item', doc.id, 'using current time');
          createdAt = Date.now();
        }
        
        try {
          updatedAt = data.updatedAt || Date.now();
          if (typeof updatedAt === 'string') {
            updatedAt = new Date(updatedAt).getTime();
          } else if (typeof updatedAt === 'object' && updatedAt && 'seconds' in updatedAt) {
            // Handle Firestore Timestamp objects
            updatedAt = (updatedAt as any).seconds * 1000;
          } else if (typeof updatedAt === 'number') {
            // Already a number
          } else {
            updatedAt = Date.now();
          }
        } catch (error) {
          console.warn('Invalid updatedAt timestamp for item', doc.id, 'using current time');
          updatedAt = Date.now();
        }

        // Safely handle arrays and objects with better validation
        const style = Array.isArray(data.style) ? data.style : (data.style ? [data.style] : []);
        const occasion = Array.isArray(data.occasion) ? data.occasion : (data.occasion ? [data.occasion] : []);
        const season = Array.isArray(data.season) ? data.season : (data.season ? [data.season] : ['all']);
        const tags = Array.isArray(data.tags) ? data.tags : [];
        const dominantColors = Array.isArray(data.dominantColors) ? data.dominantColors : [];
        const matchingColors = Array.isArray(data.matchingColors) ? data.matchingColors : [];

        // Create a safe clothing item object
        const item: ClothingItem = {
          id: doc.id,
          userId: data.userId || userId,
          name: data.name || 'Unknown Item',
          type: data.type || 'other',
          color: data.color || 'unknown',
          style,
          occasion,
          season,
          tags,
          imageUrl: data.imageUrl || '',
          dominantColors,
          matchingColors,
          createdAt,
          updatedAt,
          metadata: data.metadata || {},
          favorite: data.favorite || false,
          wearCount: data.wearCount || 0,
          lastWorn: data.lastWorn || null,
          backgroundRemoved: data.backgroundRemoved || false
        };

        items.push(item);
        console.log('getWardrobeItems: Successfully processed item', doc.id);
        
      } catch (error) {
        console.error('getWardrobeItems: Error processing document', doc.id, error);
        errors.push(`Failed to process item ${doc.id}: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    // Sort items by creation date (newest first)
    items.sort((a, b) => b.createdAt - a.createdAt);
    
    console.log('getWardrobeItems: Successfully processed', items.length, 'items');
    if (errors.length > 0) {
      console.warn('getWardrobeItems: Errors encountered:', errors);
    }

    return {
      success: true,
      data: items,
      error: errors.length > 0 ? `Processed ${items.length} items with ${errors.length} errors` : undefined
    };

  } catch (error) {
    console.error('getWardrobeItems: Unexpected error:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to load wardrobe items',
      data: null
    };
  }
};

// Check for duplicate images using hash comparison and similarity
export const checkForDuplicateImages = async (
  userId: string, 
  images: File[], 
  options: { 
    forceUpload?: boolean;
    similarityThreshold?: number;
  } = {}
): Promise<DuplicateCheckResult> => {
  try {
    if (!userId) {
      console.error('No userId provided to checkForDuplicateImages');
      return { 
        success: false, 
        error: 'No userId provided'
      };
    }

    if (!images || !Array.isArray(images) || images.length === 0) {
      console.error('No images provided to checkForDuplicateImages');
      return { 
        success: false, 
        error: 'No images provided'
      };
    }

    const { forceUpload = false, similarityThreshold = 0.95 } = options;
    
    // Get all existing wardrobe items for the user
    const existingItems = await getWardrobeItems(userId);
    if (!existingItems.success) {
      console.error('Failed to fetch existing items:', existingItems.error);
      return { 
        success: false, 
        error: existingItems.error || 'Failed to fetch existing wardrobe items'
      };
    }

    // If no existing items or data is undefined/null, all images are unique
    if (!existingItems.data || !Array.isArray(existingItems.data)) {
      console.log('No existing items found or invalid data format:', existingItems.data);
      return { 
        success: true, 
        data: { 
          uniqueImages: images,
          duplicateHashes: [],
          similarImages: []
        } 
      };
    }

    // Calculate hashes for new images
    const imageHashes = await Promise.all(
      images.map(async (file) => ({
        file,
        hash: await calculateFileHash(file)
      }))
    );

    // Filter out duplicates and find similar images
    const uniqueImages: File[] = [];
    const duplicateHashes: string[] = [];
    const similarImages: Array<{ file: File; existingItem: ClothingItem; similarity: number }> = [];

    // Process each image
    for (const { file, hash } of imageHashes) {
      let isDuplicate = false;

      // Check for exact hash matches
      for (const item of existingItems.data) {
        if (!item || !item.metadata) continue;
        if (item.metadata.basicMetadata && item.metadata.basicMetadata.imageHash === hash) {
          if (forceUpload) {
            uniqueImages.push(file);
          } else {
            duplicateHashes.push(hash);
          }
          isDuplicate = true;
          break;
        }
      }

      if (isDuplicate) continue;

      // Check for similar images
      let isSimilar = false;
      for (const item of existingItems.data) {
        if (!item || !item.imageUrl) continue;
        
        const similarity = await calculateImageSimilarity(file, item.imageUrl);
        if (similarity >= similarityThreshold) {
          similarImages.push({
            file,
            existingItem: item,
            similarity
          });
          isSimilar = true;
          break;
        }
      }

      if (!isSimilar) {
        uniqueImages.push(file);
      }
    }

    return { 
      success: true, 
      data: { 
        uniqueImages, 
        duplicateHashes, 
        similarImages 
      } 
    };
  } catch (error) {
    console.error("Error checking for duplicates:", error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to check for duplicates' 
    };
  }
};

// Get wardrobe item by ID
export async function getWardrobeItem(
  userId: string,
  itemId: string
): Promise<ClothingItem | undefined> {
  const docRef = doc(db, WARDROBE_COLLECTION, itemId);
  const docSnap = await getDoc(docRef);
  if (!docSnap.exists()) return undefined;
  const data = docSnap.data();
  return validateClothingItem({
    id: docSnap.id,
    userId,
    name: data.name,
    type: data.type,
    subType: data.subType || undefined,
    dominantColors: data.dominantColors || [],
    matchingColors: data.matchingColors || [],
    style: data.style || [],
    brand: data.brand || undefined,
    season: data.season || [],
    occasion: data.occasion || [],
    imageUrl: data.imageUrl,
    tags: data.tags || [],
    color: data.color,
    colorName: data.colorName || undefined,
    createdAt: data.createdAt,
    updatedAt: data.updatedAt,
    backgroundRemoved: data.backgroundRemoved || false,
    embedding: data.embedding || undefined,
    metadata: data.metadata || {
      brand: data.brand || undefined,
      analysisTimestamp: Date.now(),
      originalType: data.type,
      originalSubType: data.subType || undefined,
      styleTags: data.style || [],
      occasionTags: data.occasion || [],
      imageHash: undefined,
      colorAnalysis: {
        dominant: data.dominantColors || [],
        matching: data.matchingColors || []
      },
      basicMetadata: undefined,
      visualAttributes: undefined,
      itemMetadata: undefined,
      naturalDescription: undefined
    }
  });
}

// Add a new wardrobe item
export const addWardrobeItem = async (item: Omit<ClothingItem, 'id' | 'userId' | 'createdAt' | 'updatedAt'>): Promise<WardrobeItemResponse> => {
  try {
    const auth = getAuth();
    const user = auth.currentUser;

    if (!user) {
      return {
        success: false,
        error: 'User not authenticated',
        data: null
      };
    }

    const metadata: any = {
      originalType: item.type,
      analysisTimestamp: Date.now(),
      colorAnalysis: {
        dominant: item.metadata?.colorAnalysis?.dominant ?? [],
        matching: item.metadata?.colorAnalysis?.matching ?? []
      },
      basicMetadata: item.metadata?.basicMetadata ? {
        width: item.metadata.basicMetadata.width ?? null,
        height: item.metadata.basicMetadata.height ?? null,
        orientation: item.metadata.basicMetadata.orientation ?? null,
        dateTaken: item.metadata.basicMetadata.dateTaken ?? null,
        deviceModel: item.metadata.basicMetadata.deviceModel ?? null,
        gps: item.metadata.basicMetadata.gps ? {
          latitude: item.metadata.basicMetadata.gps.latitude,
          longitude: item.metadata.basicMetadata.gps.longitude
        } : null,
        flashUsed: item.metadata.basicMetadata.flashUsed ?? null,
        imageHash: item.metadata.basicMetadata.imageHash ?? null
      } : undefined,
      visualAttributes: item.metadata?.visualAttributes ? {
        material: item.metadata.visualAttributes.material ?? null,
        pattern: item.metadata.visualAttributes.pattern ?? null,
        textureStyle: item.metadata.visualAttributes.textureStyle ?? null,
        fabricWeight: item.metadata.visualAttributes.fabricWeight ?? null,
        fit: item.metadata.visualAttributes.fit ?? null,
        silhouette: item.metadata.visualAttributes.silhouette ?? null,
        length: item.metadata.visualAttributes.length ?? null,
        genderTarget: item.metadata.visualAttributes.genderTarget ?? null,
        sleeveLength: item.metadata.visualAttributes.sleeveLength ?? null,
        hangerPresent: item.metadata.visualAttributes.hangerPresent ?? null,
        backgroundRemoved: item.metadata.visualAttributes.backgroundRemoved ?? null,
        wearLayer: item.metadata.visualAttributes.wearLayer ?? null,
        formalLevel: item.metadata.visualAttributes.formalLevel ?? null
      } : undefined,
      itemMetadata: item.metadata?.itemMetadata ? {
        priceEstimate: item.metadata.itemMetadata.priceEstimate ?? null,
        careInstructions: item.metadata.itemMetadata.careInstructions ?? null,
        tags: item.metadata.itemMetadata.tags ?? [],
        brand: item.metadata.itemMetadata.brand ?? null
      } : undefined,
      naturalDescription: item.metadata?.naturalDescription ?? null
    };

    const newItem: ClothingItem = {
      ...item,
      id: generateId(),
      userId: user.uid,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      backgroundRemoved: item.backgroundRemoved ?? false,
      brand: item.brand ?? null,
      subType: item.subType ?? null,
      colorName: item.colorName ?? null,
      dominantColors: item.dominantColors ?? [],
      matchingColors: item.matchingColors ?? [],
      style: item.style ?? [],
      season: item.season ?? [],
      occasion: item.occasion ?? [],
      tags: item.tags ?? [],
      wearCount: 0, // Initialize wear count to 0
      lastWorn: null, // Initialize last worn to null
      metadata
    };

    // Validate the item before saving
    const validatedItem = validateClothingItem(newItem);

    const docRef = doc(db, WARDROBE_COLLECTION, validatedItem.id);
    await setDoc(docRef, validatedItem);

    return {
      success: true,
      data: validatedItem
    };
  } catch (error) {
    console.error('Error adding wardrobe item:', error);
    return {
      success: false,
      error: 'Failed to add wardrobe item',
      data: null
    };
  }
};

// Add multiple wardrobe items
export const addMultipleWardrobeItems = async (
  userId: string,
  items: Array<Omit<ClothingItem, 'id' | 'userId'>>
): Promise<ApiResponse<ClothingItem[]>> => {
  try {
    const batch = writeBatch(db);
    const newItems: ClothingItem[] = [];
    
    for (const item of items) {
      const docRef = doc(collection(db, WARDROBE_COLLECTION));
      const metadata: any = {
        originalType: item.type,
        analysisTimestamp: Date.now(),
        colorAnalysis: {
          dominant: item.dominantColors || [],
          matching: item.matchingColors || []
        },
        basicMetadata: item.metadata?.basicMetadata ? {
          width: item.metadata.basicMetadata.width ?? null,
          height: item.metadata.basicMetadata.height ?? null,
          orientation: item.metadata.basicMetadata.orientation ?? null,
          dateTaken: item.metadata.basicMetadata.dateTaken ?? null,
          deviceModel: item.metadata.basicMetadata.deviceModel ?? null,
          gps: item.metadata.basicMetadata.gps ? {
            latitude: item.metadata.basicMetadata.gps.latitude,
            longitude: item.metadata.basicMetadata.gps.longitude
          } : null,
          flashUsed: item.metadata.basicMetadata.flashUsed ?? null,
          imageHash: item.metadata.basicMetadata.imageHash ?? null
        } : undefined,
        visualAttributes: item.metadata?.visualAttributes ? {
          material: item.metadata.visualAttributes.material ?? null,
          pattern: item.metadata.visualAttributes.pattern ?? null,
          textureStyle: item.metadata.visualAttributes.textureStyle ?? null,
          fabricWeight: item.metadata.visualAttributes.fabricWeight ?? null,
          fit: item.metadata.visualAttributes.fit ?? null,
          silhouette: item.metadata.visualAttributes.silhouette ?? null,
          length: item.metadata.visualAttributes.length ?? null,
          genderTarget: item.metadata.visualAttributes.genderTarget ?? null,
          sleeveLength: item.metadata.visualAttributes.sleeveLength ?? null,
          hangerPresent: item.metadata.visualAttributes.hangerPresent ?? null,
          backgroundRemoved: item.metadata.visualAttributes.backgroundRemoved ?? null,
          wearLayer: item.metadata.visualAttributes.wearLayer ?? null,
          formalLevel: item.metadata.visualAttributes.formalLevel ?? null
        } : undefined,
        itemMetadata: item.metadata?.itemMetadata ? {
          priceEstimate: item.metadata.itemMetadata.priceEstimate ?? null,
          careInstructions: item.metadata.itemMetadata.careInstructions ?? null,
          tags: item.metadata.itemMetadata.tags ?? [],
          brand: item.metadata.itemMetadata.brand ?? null
        } : undefined,
        naturalDescription: item.metadata?.naturalDescription ?? null
      };
      
      const newItem: ClothingItem = {
        ...item,
        id: docRef.id,
        userId,
        subType: item.subType || undefined,
        colorName: item.colorName || undefined,
        backgroundRemoved: item.backgroundRemoved || false,
        embedding: item.embedding || undefined,
        wearCount: 0, // Initialize wear count to 0
        lastWorn: null, // Initialize last worn to null
        metadata
      };
      
      batch.set(docRef, newItem);
      newItems.push(newItem);
    }
    
    await batch.commit();
    return {
      success: true,
      data: newItems
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to add items',
      data: null
    };
  }
};

// Update a wardrobe item
export const updateWardrobeItem = async (itemId: string, updates: Partial<ClothingItem>): Promise<WardrobeItemResponse> => {
  try {
    const auth = getAuth();
    const user = auth.currentUser;

    if (!user) {
      return {
        success: false,
        error: 'User not authenticated',
        data: null
      };
    }

    const docRef = doc(db, WARDROBE_COLLECTION, itemId);
    const docSnap = await getDoc(docRef);

    if (!docSnap.exists()) {
      return {
        success: false,
        error: 'Item not found',
        data: null
      };
    }

    const item = docSnap.data() as ClothingItem;
    if (item.userId !== user.uid) {
      return {
        success: false,
        error: 'Unauthorized to update this item',
        data: null
      };
    }

    const metadata: any = {
      originalType: item.type,
      analysisTimestamp: Date.now(),
      colorAnalysis: {
        dominant: item.metadata?.colorAnalysis?.dominant ?? [],
        matching: item.metadata?.colorAnalysis?.matching ?? []
      },
      basicMetadata: item.metadata?.basicMetadata ? {
        width: item.metadata.basicMetadata.width ?? null,
        height: item.metadata.basicMetadata.height ?? null,
        orientation: item.metadata.basicMetadata.orientation ?? null,
        dateTaken: item.metadata.basicMetadata.dateTaken ?? null,
        deviceModel: item.metadata.basicMetadata.deviceModel ?? null,
        gps: item.metadata.basicMetadata.gps ? {
          latitude: item.metadata.basicMetadata.gps.latitude,
          longitude: item.metadata.basicMetadata.gps.longitude
        } : null,
        flashUsed: item.metadata.basicMetadata.flashUsed ?? null,
        imageHash: item.metadata.basicMetadata.imageHash ?? null
      } : undefined,
      visualAttributes: item.metadata?.visualAttributes ? {
        material: item.metadata.visualAttributes.material ?? null,
        pattern: item.metadata.visualAttributes.pattern ?? null,
        textureStyle: item.metadata.visualAttributes.textureStyle ?? null,
        fabricWeight: item.metadata.visualAttributes.fabricWeight ?? null,
        fit: item.metadata.visualAttributes.fit ?? null,
        silhouette: item.metadata.visualAttributes.silhouette ?? null,
        length: item.metadata.visualAttributes.length ?? null,
        genderTarget: item.metadata.visualAttributes.genderTarget ?? null,
        sleeveLength: item.metadata.visualAttributes.sleeveLength ?? null,
        hangerPresent: item.metadata.visualAttributes.hangerPresent ?? null,
        backgroundRemoved: item.metadata.visualAttributes.backgroundRemoved ?? null,
        wearLayer: item.metadata.visualAttributes.wearLayer ?? null,
        formalLevel: item.metadata.visualAttributes.formalLevel ?? null
      } : undefined,
      itemMetadata: item.metadata?.itemMetadata ? {
        priceEstimate: item.metadata.itemMetadata.priceEstimate ?? null,
        careInstructions: item.metadata.itemMetadata.careInstructions ?? null,
        tags: item.metadata.itemMetadata.tags ?? [],
        brand: item.metadata.itemMetadata.brand ?? null
      } : undefined,
      naturalDescription: item.metadata?.naturalDescription ?? null
    };

    const updatedItem = {
      ...item,
      ...updates,
      updatedAt: Date.now(),
      backgroundRemoved: updates.backgroundRemoved ?? item.backgroundRemoved ?? false,
      metadata
    };

    await updateDoc(docRef, updatedItem);

    return {
      success: true,
      data: updatedItem
    };
  } catch (error) {
    console.error('Error updating wardrobe item:', error);
    return {
      success: false,
      error: 'Failed to update wardrobe item',
      data: null
    };
  }
};

// Delete a wardrobe item
export const deleteWardrobeItem = async (itemId: string): Promise<ApiResponse<undefined>> => {
  try {
    const auth = getAuth();
    const user = auth.currentUser;

    if (!user) {
      return {
        success: false,
        error: 'User not authenticated',
        data: undefined
      };
    }

    const docRef = doc(db, WARDROBE_COLLECTION, itemId);
    const docSnap = await getDoc(docRef);

    if (!docSnap.exists()) {
      return {
        success: false,
        error: 'Item not found',
        data: undefined
      };
    }

    const item = docSnap.data() as ClothingItem;
    if (item.userId !== user.uid) {
      return {
        success: false,
        error: 'Unauthorized to delete this item',
        data: undefined
      };
    }

    await deleteDoc(docRef);

    return {
      success: true,
      data: undefined
    };
  } catch (error) {
    console.error('Error deleting wardrobe item:', error);
    return {
      success: false,
      error: 'Failed to delete wardrobe item',
      data: undefined
    };
  }
};

// Delete multiple wardrobe items
export const deleteMultipleWardrobeItems = async (
  userId: string,
  itemIds: string[]
): Promise<ApiResponse<void>> => {
  try {
    const batch = writeBatch(db);
    itemIds.forEach(itemId => {
      const itemRef = doc(db, WARDROBE_COLLECTION, itemId);
      batch.delete(itemRef);
    });
    await batch.commit();
    return {
      success: true,
      data: undefined
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Failed to delete items',
      data: undefined
    };
  }
};

// Get wardrobe items by category
export async function getWardrobeItemsByCategory(
  userId: string,
  category: string
): Promise<ClothingItem[]> {
  const wardrobeRef = collection(db, WARDROBE_COLLECTION);
  const q = query(
    wardrobeRef,
    where("userId", "==", userId),
    where("type", "==", category),
    orderBy("createdAt", "desc")
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((doc) => {
    const data = doc.data();
    return validateClothingItem({
      id: doc.id,
      userId,
      name: data.name,
      type: data.type,
      subType: data.subType || undefined,
      dominantColors: data.dominantColors || [],
      matchingColors: data.matchingColors || [],
      style: data.style || [],
      brand: data.brand || undefined,
      season: data.season || [],
      occasion: data.occasion || [],
      imageUrl: data.imageUrl,
      tags: data.tags || [],
      color: data.color,
      colorName: data.colorName || undefined,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      backgroundRemoved: data.backgroundRemoved || false,
      embedding: data.embedding || undefined,
      metadata: data.metadata || {
        brand: data.brand || undefined,
        analysisTimestamp: Date.now(),
        originalType: data.type,
        originalSubType: data.subType || undefined,
        styleTags: data.style || [],
        occasionTags: data.occasion || [],
        imageHash: undefined,
        colorAnalysis: {
          dominant: data.dominantColors || [],
          matching: data.matchingColors || []
        },
        basicMetadata: undefined,
        visualAttributes: undefined,
        itemMetadata: undefined,
        naturalDescription: undefined
      }
    });
  });
}

// Get wardrobe items by season
export async function getWardrobeItemsBySeason(
  userId: string,
  season: string
): Promise<ClothingItem[]> {
  try {
    const wardrobeRef = collection(db, WARDROBE_COLLECTION);
    const q = query(
      wardrobeRef,
      where("userId", "==", userId),
      where("season", "array-contains", season),
      orderBy("createdAt", "desc")
    );
    const snapshot = await getDocs(q);
    const items = snapshot.docs.map((doc) => {
      const data = doc.data();
      return validateClothingItem({
        id: doc.id,
        userId,
        name: data.name,
        type: data.type,
        subType: data.subType || undefined,
        dominantColors: data.dominantColors || [],
        matchingColors: data.matchingColors || [],
        style: data.style || [],
        brand: data.brand || undefined,
        season: data.season || [],
        occasion: data.occasion || [],
        imageUrl: data.imageUrl,
        tags: data.tags || [],
        color: data.color,
        colorName: data.colorName || undefined,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
        backgroundRemoved: data.backgroundRemoved || false,
        embedding: data.embedding || undefined,
        metadata: data.metadata || {
          brand: data.brand || undefined,
          analysisTimestamp: Date.now(),
          originalType: data.type,
          originalSubType: data.subType || undefined,
          styleTags: data.style || [],
          occasionTags: data.occasion || [],
          imageHash: undefined,
          colorAnalysis: {
            dominant: data.dominantColors || [],
            matching: data.matchingColors || []
          },
          basicMetadata: undefined,
          visualAttributes: undefined,
          itemMetadata: undefined,
          naturalDescription: undefined
        }
      });
    });
    return validateClothingItems(items);
  } catch (error) {
    console.error('Error getting wardrobe items by season:', error);
    throw error;
  }
}

interface ProcessImagesParams {
  userId: string;
  files: File[];
  onProgress?: (progress: number) => void;
}

export async function processAndAddImages({ userId, files, onProgress }: ProcessImagesParams): Promise<ApiResponse<{
  newItems: ClothingItem[];
  totalProcessed: number;
  successfulUploads: number;
}>> {
  try {
    if (!files || !Array.isArray(files) || files.length === 0) {
      return {
        success: false,
        error: 'No files provided',
        data: null
      };
    }

    const newItems: ClothingItem[] = [];
    let totalProcessed = 0;
    let successfulUploads = 0;

    for (const file of files) {
      try {
        // Upload image to storage
        const uploadedImage = await uploadImage(file, userId);
        const imageUrl = uploadedImage.url;
        
        // Analyze image
        const analysis = await analyzeClothingImage(imageUrl);
        if (!analysis) {
          console.error('Image analysis failed: No response received');
          continue;
        }
        
        // Create clothing item from analysis
        const item = createClothingItemFromAnalysis({
          ...analysis,
          metadata: {
            ...analysis.metadata,
            basicMetadata: analysis.metadata?.basicMetadata ? {
              ...analysis.metadata.basicMetadata,
              gps: analysis.metadata.basicMetadata.gps
            } : undefined,
            visualAttributes: analysis.metadata?.visualAttributes ? {
              ...analysis.metadata.visualAttributes,
              genderTarget: analysis.metadata.visualAttributes.genderTarget ?? 'unisex',
              wearLayer: analysis.metadata.visualAttributes.wearLayer ?? 'outer',
              formalLevel: analysis.metadata.visualAttributes.formalLevel ?? 'casual'
            } : undefined
          }
        }, userId, imageUrl);
        
        // Add to database
        const addedItem = await addWardrobeItem(item);
        if (addedItem.success && addedItem.data) {
          newItems.push(addedItem.data);
          successfulUploads++;
        }
      } catch (error) {
        console.error('Error processing image:', error);
      }
      totalProcessed++;
      if (onProgress) {
        onProgress((totalProcessed / files.length) * 100);
      }
    }

    if (newItems.length === 0) {
      return {
        success: false,
        error: 'No items were created successfully',
        data: null
      };
    }

    return {
      success: true,
      data: {
        newItems,
        totalProcessed,
        successfulUploads
      }
    };
  } catch (error) {
    console.error('Error in processAndAddImages:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      data: null
    };
  }
}

export async function getWardrobe(userId: string): Promise<ClothingItem[]> {
  const q = query(
    collection(db, "wardrobe"),
    where("userId", "==", userId)
  );
  const snapshot = await getDocs(q);
  const items = snapshot.docs.map(doc => {
    const data = doc.data();
    return validateClothingItem({
      id: doc.id,
      userId,
      name: data.name,
      type: data.type,
      subType: data.subType || null,
      dominantColors: data.dominantColors || [],
      matchingColors: data.matchingColors || [],
      style: data.style || [],
      brand: data.brand || null,
      season: data.season || [],
      occasion: data.occasion || [],
      imageUrl: data.imageUrl,
      tags: data.tags || [],
      color: data.color,
      colorName: data.colorName || null,
      createdAt: data.createdAt,
      updatedAt: data.updatedAt,
      backgroundRemoved: data.backgroundRemoved || false,
      embedding: data.embedding || null,
      metadata: data.metadata || {
        brand: data.brand || null,
        analysisTimestamp: Date.now(),
        originalType: data.type,
        originalSubType: data.subType || null,
        styleTags: data.style || [],
        occasionTags: data.occasion || [],
        imageHash: null,
        colorAnalysis: {
          dominant: data.dominantColors || [],
          matching: data.matchingColors || []
        },
        basicMetadata: null,
        visualAttributes: null,
        itemMetadata: null,
        naturalDescription: null
      }
    });
  });
  return items;
}

export async function addClothingItem(item: Omit<ClothingItem, "id">): Promise<ClothingItem> {
  const validatedItem = validateClothingItem({
    ...item,
    backgroundRemoved: item.backgroundRemoved || false,
    metadata: item.metadata || {
      brand: item.brand || null,
      analysisTimestamp: Date.now(),
      originalType: item.type,
      originalSubType: item.subType || null,
      styleTags: item.style || [],
      occasionTags: item.occasion || [],
      imageHash: null,
      colorAnalysis: {
        dominant: item.dominantColors || [],
        matching: item.matchingColors || []
      },
      basicMetadata: null,
      visualAttributes: null,
      itemMetadata: null,
      naturalDescription: null
    }
  });
  const docRef = await addDoc(collection(db, "wardrobe"), validatedItem);
  return { ...validatedItem, id: docRef.id };
}

export async function updateClothingItem(id: string, item: Partial<ClothingItem>): Promise<ClothingItem> {
  const docRef = doc(db, "wardrobe", id);
  const validatedItem = validateClothingItem(item);
  await updateDoc(docRef, validatedItem);
  return { ...validatedItem, id };
}

export async function deleteClothingItem(id: string): Promise<void> {
  const docRef = doc(db, "wardrobe", id);
  await deleteDoc(docRef);
}

export async function getWardrobeItemsByType(
  userId: string,
  type: string
): Promise<ClothingItem[]> {
  try {
    const wardrobeRef = collection(db, WARDROBE_COLLECTION);
    const q = query(
      wardrobeRef,
      where("userId", "==", userId),
      where("type", "==", type),
      orderBy("createdAt", "desc")
    );
    const snapshot = await getDocs(q);
    const items = snapshot.docs.map((doc) => {
      const data = doc.data();
      return validateClothingItem({
        id: doc.id,
        userId,
        name: data.name,
        type: data.type,
        subType: data.subType || undefined,
        dominantColors: data.dominantColors || [],
        matchingColors: data.matchingColors || [],
        style: data.style || [],
        brand: data.brand || undefined,
        season: data.season || [],
        occasion: data.occasion || [],
        imageUrl: data.imageUrl,
        tags: data.tags || [],
        color: data.color,
        colorName: data.colorName || undefined,
        createdAt: data.createdAt,
        updatedAt: data.updatedAt,
        backgroundRemoved: data.backgroundRemoved || false,
        embedding: data.embedding || undefined,
        metadata: data.metadata || {
          brand: data.brand || undefined,
          analysisTimestamp: Date.now(),
          originalType: data.type,
          originalSubType: data.subType || undefined,
          styleTags: data.style || [],
          occasionTags: data.occasion || [],
          imageHash: undefined,
          colorAnalysis: {
            dominant: data.dominantColors || [],
            matching: data.matchingColors || []
          },
          basicMetadata: undefined,
          visualAttributes: undefined,
          itemMetadata: undefined,
          naturalDescription: undefined
        }
      });
    });
    return validateClothingItems(items);
  } catch (error) {
    console.error('Error getting wardrobe items by type:', error);
    return [];
  }
}

export const migrateWardrobeItems = async (userId: string): Promise<ApiResponse<void>> => {
  try {
    if (!userId) {
      return { 
        success: false, 
        error: 'No userId provided',
        data: undefined
      };
    }

    const items = await wardrobeApi.getItems(userId);
    if (!items || !Array.isArray(items)) {
      return { 
        success: false, 
        error: 'Invalid response format from wardrobe API',
        data: undefined
      };
    }

    // Update each item to ensure it has the required fields
    const batch = writeBatch(db);
    const wardrobeRef = collection(db, WARDROBE_COLLECTION);

    for (const item of items) {
      const updatedItem = {
        ...item,
        style: Array.isArray(item.style) ? item.style : [],
        dominantColors: Array.isArray(item.dominantColors) ? item.dominantColors : [],
        matchingColors: Array.isArray(item.matchingColors) ? item.matchingColors : [],
        season: Array.isArray(item.season) ? item.season : [],
        occasion: Array.isArray(item.occasion) ? item.occasion : [],
        tags: Array.isArray(item.tags) ? item.tags : [],
        metadata: {
          ...item.metadata,
          visualAttributes: {
            ...item.metadata?.visualAttributes,
            genderTarget: item.metadata?.visualAttributes?.genderTarget || 'unisex',
            wearLayer: item.metadata?.visualAttributes?.wearLayer || 'outer',
            formalLevel: item.metadata?.visualAttributes?.formalLevel || 'casual',
            fabricWeight: item.metadata?.visualAttributes?.fabricWeight || null,
            fit: item.metadata?.visualAttributes?.fit || null,
            material: item.metadata?.visualAttributes?.material || null,
            pattern: item.metadata?.visualAttributes?.pattern || null,
            textureStyle: item.metadata?.visualAttributes?.textureStyle || null,
            silhouette: item.metadata?.visualAttributes?.silhouette || null,
            length: item.metadata?.visualAttributes?.length || null,
            sleeveLength: item.metadata?.visualAttributes?.sleeveLength || null,
            hangerPresent: item.metadata?.visualAttributes?.hangerPresent || null,
            backgroundRemoved: item.metadata?.visualAttributes?.backgroundRemoved || null
          }
        },
        updatedAt: Date.now()
      };

      const docRef = doc(wardrobeRef, item.id);
      batch.update(docRef, updatedItem);
    }

    await batch.commit();
    return { success: true, data: undefined };
  } catch (error) {
    console.error('Error migrating wardrobe items:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Failed to migrate items',
      data: undefined
    };
  }
};

export const updateAllWardrobeItemNames = async (userId: string): Promise<ApiResponse<void>> => {
  try {
    // Get all wardrobe items
    const itemsResponse = await getWardrobeItems(userId);
    if (!itemsResponse.success || !itemsResponse.data) {
      return {
        success: false,
        error: 'Failed to fetch wardrobe items',
        data: undefined
      };
    }

    const items = itemsResponse.data;
    const batch = writeBatch(db);
    const itemNameCounts = new Map<string, number>();

    // Process each item
    for (const item of items) {
      const parts: string[] = [];
      
      // Add color with fancy adjective
      if (item.color) {
        const colorAdjective = getColorAdjective(item.color);
        parts.push(colorAdjective);
      }
      
      // Add material with fancy adjective
      if (item.metadata?.visualAttributes?.material) {
        const materialAdjective = getMaterialAdjective(item.metadata.visualAttributes.material);
        parts.push(materialAdjective);
      }
      
      // Add subType if available, otherwise use type
      if (item.subType) {
        parts.push(item.subType);
      } else {
        parts.push(item.type);
      }
      
      // Add brand if available
      if (item.brand) {
        parts.push(`by ${item.brand}`);
      }
      
      // Join all parts with spaces and capitalize first letter
      let name = parts.join(' ');
      name = name.charAt(0).toUpperCase() + name.slice(1);

      // Check if this name already exists
      const count = itemNameCounts.get(name) || 0;
      if (count > 0) {
        // Add a subtle numeric suffix
        name = `${name} (${count + 1})`;
      }
      
      // Increment the count for this base name
      itemNameCounts.set(name.split(' (')[0], count + 1);

      // Update the item in the batch
      const itemRef = doc(db, WARDROBE_COLLECTION, item.id);
      batch.update(itemRef, { name });
    }

    // Commit all updates
    await batch.commit();

    return {
      success: true,
      data: undefined
    };
  } catch (error) {
    console.error('Error updating wardrobe item names:', error);
    return {
      success: false,
      error: 'Failed to update wardrobe item names',
      data: undefined
    };
  }
};

// Helper functions for name generation
function getColorAdjective(color: string): string {
  const colorMap: Record<string, string> = {
    'black': 'Ebony',
    'white': 'Ivory',
    'red': 'Crimson',
    'blue': 'Azure',
    'green': 'Emerald',
    'yellow': 'Amber',
    'purple': 'Royal',
    'pink': 'Rose',
    'brown': 'Mahogany',
    'gray': 'Silver',
    'grey': 'Silver',
    'orange': 'Amber',
    'beige': 'Cream',
    'navy': 'Navy',
    'burgundy': 'Burgundy',
    'maroon': 'Maroon',
    'teal': 'Teal',
    'olive': 'Olive',
    'tan': 'Tan',
    'gold': 'Golden',
    'silver': 'Silver'
  };
  return colorMap[color.toLowerCase()] || color;
}

function getMaterialAdjective(material: string): string {
  const materialMap: Record<string, string> = {
    'leather': 'Leather',
    'cotton': 'Cotton',
    'denim': 'Denim',
    'silk': 'Silk',
    'wool': 'Wool',
    'linen': 'Linen',
    'polyester': 'Polyester',
    'nylon': 'Nylon',
    'velvet': 'Velvet',
    'suede': 'Suede',
    'cashmere': 'Cashmere',
    'fleece': 'Fleece',
    'canvas': 'Canvas',
    'tweed': 'Tweed',
    'lace': 'Lace',
    'satin': 'Satin',
    'chiffon': 'Chiffon',
    'knit': 'Knit',
    'mesh': 'Mesh',
    'vinyl': 'Vinyl'
  };
  return materialMap[material.toLowerCase()] || material;
}

interface ItemMetadata {
  priceEstimate?: number | null;
  careInstructions?: string | null;
  tags?: string[];
}

/**
 * Utility: Print all wardrobe item metadata for a user (for copy-paste)
 */
export async function printAllWardrobeMetadata(userId: string): Promise<void> {
  const result = await getWardrobeItems(userId);
  if (!result.success || !result.data) {
    console.error('Failed to fetch wardrobe items:', result.error);
    return;
  }
  result.data.forEach(item => {
    // Print only the metadata field as formatted JSON
    console.log(JSON.stringify(item.metadata, null, 2));
  });
} 