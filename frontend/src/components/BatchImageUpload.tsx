"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  X, 
  Camera, 
  CheckCircle, 
  AlertCircle, 
  Loader2,
  Trash2,
  Image as ImageIcon,
  Sparkles,
  Brain
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useFirebase } from "@/lib/firebase-context";

interface BatchImageUploadProps {
  onUploadComplete?: (items: any[]) => void;
  onError?: (message: string) => void;
  userId: string;
  quickMode?: boolean; // When true, uploads are async (don't wait for analysis)
  requireStaging?: boolean; // When true, user must stage all items before analysis starts
  requiredCount?: number; // Number of items required before allowing analysis (used with requireStaging)
}

interface UploadItem {
  id: string;
  file: File;
  preview: string;
  status: 'pending' | 'analyzing' | 'uploading' | 'success' | 'error' | 'duplicate';
  progress: number;
  error?: string;
  analysisResult?: any;
  isDuplicate?: boolean;
}

// Helper function to convert file to base64
const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

// Helper function to create a preview URL, converting HEIC files if needed
const createPreviewUrl = async (file: File): Promise<string> => {
  try {
    // Check if the file is HEIC/HEIF format
    const isHeic = file.type === 'image/heic' || 
                   file.type === 'image/heif' || 
                   file.name.toLowerCase().endsWith('.heic') || 
                   file.name.toLowerCase().endsWith('.heif');
    
    if (isHeic) {
      console.log('🔄 Converting HEIC file to JPEG for preview:', file.name);
      
      // Dynamically import heic2any to avoid SSR issues
      const heic2any = (await import('heic2any')).default;
      
      // Convert HEIC to JPEG blob
      const convertedBlob = await heic2any({
        blob: file,
        toType: 'image/jpeg',
        quality: 0.9
      });
      
      // heic2any can return an array of blobs, so handle both cases
      const blob = Array.isArray(convertedBlob) ? convertedBlob[0] : convertedBlob;
      
      console.log('✅ HEIC conversion successful');
      return URL.createObjectURL(blob);
    }
    
    // For non-HEIC files, create preview URL directly
    return URL.createObjectURL(file);
  } catch (error) {
    console.error('❌ Failed to create preview for file:', file.name, error);
    // Fallback to trying to create a URL anyway
    return URL.createObjectURL(file);
  }
};

// Helper function to compress image for AI analysis
const compressImageForAnalysis = (file: File, maxWidth: number = 800, quality: number = 0.8): Promise<string> => {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
      // Calculate new dimensions
      const ratio = Math.min(maxWidth / img.width, maxWidth / img.height);
      canvas.width = img.width * ratio;
      canvas.height = img.height * ratio;
      
      // Draw and compress
      ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);
      const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);
      resolve(compressedDataUrl);
    };
    
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
};

// Helper function to upload image to Firebase Storage via backend
const uploadImageToFirebaseStorage = async (file: File, userId: string, user: any): Promise<string> => {
  try {
    console.log('🚀 Uploading image to backend Firebase Storage...');
    
    // Create FormData for the upload
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', 'clothing');
    formData.append('name', file.name || 'uploaded-item');

    // Upload to backend Firebase Storage (secure)
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    const response = await fetch(`${backendUrl}/api/image/upload`, {
      method: 'POST',
      body: formData,
      headers: {
        'Authorization': `Bearer ${await user.getIdToken()}`,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || errorData.error || 'Upload failed');
    }

    const result = await response.json();
    console.log('✅ Image uploaded successfully:', result.image_url);
    return result.image_url;
  } catch (error) {
    console.error('❌ Backend Firebase Storage upload failed:', error);
    throw error;
  }
};

// Helper function to generate image hash and metadata using backend
const generateImageHashAndMetadata = async (file: File, user: any): Promise<{
  imageHash: string;
  metadata: {
    width: number;
    height: number;
    aspectRatio: number;
    fileSize: number;
    lastModified: number;
    type: string;
  };
}> => {
  try {
    // First upload the file to get a URL
    const imageUrl = await uploadImageToFirebaseStorage(file, user.uid, user);
    
    // Then call backend to generate hash and metadata
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    const response = await fetch(`${backendUrl}/generate-image-hash`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await user.getIdToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate image hash');
    }

    const result = await response.json();
    
    // Add client-side metadata
    const clientMetadata = {
      width: result.metadata.width,
      height: result.metadata.height,
      aspectRatio: result.metadata.aspectRatio,
      fileSize: file.size,
      lastModified: file.lastModified,
      type: file.type
    };

    return {
      imageHash: result.imageHash,
      metadata: clientMetadata
    };
  } catch (error) {
    console.error('Failed to generate image hash via backend, falling back to client-side:', error);
    
    // Fallback to client-side generation
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();
      
      img.onload = () => {
        // Create a small thumbnail for hashing
        const size = 32;
        canvas.width = size;
        canvas.height = size;
        
        // Draw image to canvas
        ctx?.drawImage(img, 0, 0, size, size);
        
        // Get image data
        const imageData = ctx?.getImageData(0, 0, size, size);
        if (!imageData) {
          reject(new Error('Could not get image data'));
          return;
        }
        
        // Simple hash based on pixel data
        let hash = '';
        const data = imageData.data;
        for (let i = 0; i < data.length; i += 4) {
          // Use only RGB values, skip alpha
          const r = data[i];
          const g = data[i + 1];
          const b = data[i + 2];
          // Create a simple hash from RGB values
          hash += ((r + g + b) % 16).toString(16);
        }
        
        resolve({
          imageHash: hash,
          metadata: {
            width: img.width,
            height: img.height,
            aspectRatio: img.width / img.height,
            fileSize: file.size,
            lastModified: file.lastModified,
            type: file.type
          }
        });
      };
      
      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  }
};

const GENERIC_FILENAME_TOKENS = new Set([
  "img",
  "image",
  "picture",
  "photo",
  "screenshot",
  "file",
  "download",
  "processed",
  "tmp",
  "untitled",
  "scan"
]);

const normalizeFileName = (rawName: string): string => {
  if (!rawName) {
    return "";
  }

  const withoutExtension = rawName.split(".").slice(0, -1).join(".") || rawName;

  return withoutExtension
    .toLowerCase()
    .replace(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/gi, "")
    .replace(/[0-9]{13,}/g, "")
    .replace(/[_\-\s]+/g, "")
    .trim();
};

const isMeaningfulFileName = (normalizedName: string): boolean => {
  if (!normalizedName) {
    return false;
  }

  if (normalizedName.length < 4) {
    return false;
  }

  return !GENERIC_FILENAME_TOKENS.has(normalizedName);
};

type CachedHashInfo = {
  imageHash: string | null;
  metadata?: {
    width?: number;
    height?: number;
    aspectRatio?: number;
    fileSize?: number;
    type?: string;
  } | null;
};

const existingItemHashCache = new Map<string, CachedHashInfo>();

const getExistingItemCacheKey = (item: any): string => {
  return item?.id || item?.imageUrl || item?.image_url || JSON.stringify({ name: item?.name, url: item?.imageUrl });
};

const generateHashForExistingImageUrl = async (imageUrl: string, user: any): Promise<CachedHashInfo> => {
  if (!imageUrl || !user?.getIdToken) {
    return { imageHash: null, metadata: null };
  }

  try {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
    const response = await fetch(`${backendUrl}/generate-image-hash`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await user.getIdToken()}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ image_url: imageUrl })
    });

    if (!response.ok) {
      throw new Error('Failed to generate hash for existing item');
    }

    const result = await response.json();
    return {
      imageHash: result?.imageHash || null,
      metadata: result?.metadata
        ? {
            width: result.metadata.width,
            height: result.metadata.height,
            aspectRatio: result.metadata.aspectRatio,
            fileSize: result.metadata.fileSize,
            type: result.metadata.format || result.metadata.type,
          }
        : null,
    };
  } catch (error) {
    console.error('🔍 Failed to generate hash for existing image url:', error);
    return { imageHash: null, metadata: null };
  }
};

const ensureExistingItemHashInfo = async (item: any, user: any): Promise<CachedHashInfo> => {
  if (!item) {
    return { imageHash: null, metadata: null };
  }

  if (item.imageHash) {
    return {
      imageHash: item.imageHash,
      metadata: item.metadata ?? null,
    };
  }

  const cacheKey = getExistingItemCacheKey(item);
  if (existingItemHashCache.has(cacheKey)) {
    return existingItemHashCache.get(cacheKey)!;
  }

  const info = await generateHashForExistingImageUrl(item.imageUrl || item.image_url, user);
  existingItemHashCache.set(cacheKey, info);
  return info;
};

const hasDetailedMetadata = (metadata: any): boolean => {
  if (!metadata) {
    return false;
  }
  const { width, height, aspectRatio } = metadata;
  return typeof width === 'number' && typeof height === 'number' && typeof aspectRatio === 'number';
};

// Helper function to check for duplicate items using multiple methods
const checkForDuplicates = async (file: File, existingItems: any[], user: any): Promise<boolean> => {
  const fileName = file.name.toLowerCase();
  const fileSize = file.size;
  
  console.log('🔍 Checking for duplicates:', {
    fileName,
    fileSize,
    existingItemsCount: existingItems.length
  });
  
  try {
    // Generate image hash and metadata for the new file using backend
    const { imageHash, metadata } = await generateImageHashAndMetadata(file, user);
    
    console.log('🔍 Generated hash and metadata:', {
      imageHash: imageHash.substring(0, 16) + '...',
      metadata
    });
    
    const normalizedBaseName = normalizeFileName(file.name);
    const hasMeaningfulNewName = isMeaningfulFileName(normalizedBaseName);

    const isDuplicate = await (async () => {
      for (const item of existingItems) {
        // Method 1: Strict filename matching (exact match only when both names are meaningful)
        let filenameMatch = false;
        let existingBaseName = '';

        if (item.imageUrl) {
          try {
            const lastSegment = item.imageUrl.split('/').pop() || '';
            const decodedName = decodeURIComponent(lastSegment.split('?')[0].toLowerCase());
            existingBaseName = normalizeFileName(decodedName);
          } catch (error) {
            console.warn('🔍 Failed to normalize existing filename:', error);
          }
        }

        const hasMeaningfulExistingName = isMeaningfulFileName(existingBaseName);
        if (hasMeaningfulNewName && hasMeaningfulExistingName) {
          filenameMatch = normalizedBaseName === existingBaseName;
        }

        let effectiveMetadata = item.metadata || {};
        let effectiveHash: string | undefined = item.imageHash || undefined;

        if (filenameMatch && (!effectiveHash || !hasDetailedMetadata(effectiveMetadata))) {
          const hashInfo = await ensureExistingItemHashInfo(item, user);
          if (!effectiveHash && hashInfo.imageHash) {
            effectiveHash = hashInfo.imageHash;
          }
          if (!hasDetailedMetadata(effectiveMetadata) && hashInfo.metadata) {
            effectiveMetadata = hashInfo.metadata;
            if (!item.metadata) {
              item.metadata = hashInfo.metadata;
            }
          }
        }

        // Method 2: File size matching (tighter tolerance, using effective metadata if needed)
        const existingFileSize = typeof item.fileSize === 'number'
          ? item.fileSize
          : typeof effectiveMetadata?.fileSize === 'number'
            ? effectiveMetadata.fileSize
            : undefined;
        const sizeDifference = typeof existingFileSize === 'number'
          ? Math.abs(existingFileSize - fileSize)
          : Number.POSITIVE_INFINITY;
        const sizeMatch = Number.isFinite(sizeDifference) && sizeDifference <= 2048; // 2KB tolerance

        // Method 3: Image metadata matching (stricter tolerances)
        const widthMatch = typeof effectiveMetadata?.width === 'number' && Math.abs(effectiveMetadata.width - metadata.width) <= 5;
        const heightMatch = typeof effectiveMetadata?.height === 'number' && Math.abs(effectiveMetadata.height - metadata.height) <= 5;
        const aspectRatioMatch = typeof effectiveMetadata?.aspectRatio === 'number' && Math.abs(effectiveMetadata.aspectRatio - metadata.aspectRatio) <= 0.01;
        const typeMatch = effectiveMetadata?.type && metadata.type ? effectiveMetadata.type === metadata.type : false;
        const metadataMatches = [widthMatch, heightMatch, aspectRatioMatch, typeMatch].filter(Boolean).length;
        const metadataMatch = metadataMatches >= 3;

        // Method 4: Image hash matching (strict - full hash only)
        let hashMatch = false;
        if (effectiveHash && imageHash) {
          hashMatch = effectiveHash === imageHash;
        }

        console.log('🔍 Comparing with existing item:', {
          itemName: item.name,
          itemImageUrl: item.imageUrl ? item.imageUrl.substring(0, 50) + '...' : 'none',
          filenameMatch,
          sizeMatch,
          sizeDifference,
          metadataMatch,
          hashMatch,
          existingHash: effectiveHash ? effectiveHash.substring(0, 16) + '...' : 'none',
          newHash: imageHash.substring(0, 16) + '...',
          normalizedBaseName,
          existingBaseName
        });

        // Consider it a duplicate only when confidence is high
        if (hashMatch) {
          console.log('🔍 DUPLICATE DETECTED:', { method: 'hash', itemName: item.name });
          return true;
        }

        if (filenameMatch && (sizeMatch || metadataMatch)) {
          console.log('🔍 DUPLICATE DETECTED:', {
            method: 'filename+auxiliary',
            itemName: item.name
          });
          return true;
        }
      }

      return false;
    })();
    
    console.log('🔍 Duplicate check result:', isDuplicate);
    return isDuplicate;
    
  } catch (error) {
    console.error('🔍 Error during duplicate check:', error);
    // Fallback to simple filename matching if hash generation fails
    const fallbackNormalized = normalizeFileName(file.name);
    const fallbackMeaningful = isMeaningfulFileName(fallbackNormalized);
    
    return existingItems.some(item => {
      if (!item.imageUrl) {
        return false;
      }

      const lastSegment = item.imageUrl.split('/').pop() || '';
      const decodedName = decodeURIComponent(lastSegment.split('?')[0].toLowerCase());
      const existingNormalized = normalizeFileName(decodedName);
      const existingMeaningful = isMeaningfulFileName(existingNormalized);

      if (!fallbackMeaningful || !existingMeaningful) {
        return false;
      }

      return fallbackNormalized === existingNormalized;
    });
  }
};

export default function BatchImageUpload({ 
  onUploadComplete, 
  onError, 
  userId, 
  quickMode = false,
  requireStaging = false,
  requiredCount = 5
}: BatchImageUploadProps) {
  const { toast } = useToast();
  const { user } = useFirebase();
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [existingItems, setExistingItems] = useState<any[]>([]);

  // Fetch existing wardrobe items for duplicate detection
  const fetchExistingItems = useCallback(async () => {
    try {
      console.log('🔍 Fetching existing items for duplicate detection...');
      const response = await fetch('/api/wardrobe', {
        headers: {
          'Authorization': `Bearer ${await user?.getIdToken()}`,
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('🔍 Fetched existing items:', {
          success: data.success,
          count: data.count,
          itemsCount: data.items?.length,
          sampleItems: data.items?.slice(0, 3).map(item => ({
            id: item.id,
            name: item.name,
            imageUrl: item.imageUrl,
            hasImageUrl: !!item.imageUrl
          }))
        });
        setExistingItems(data.items || []);
      } else {
        console.error('🔍 Failed to fetch existing items:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('Failed to fetch existing items:', error);
    }
  }, [user]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (!user) {
      console.error('User not authenticated for duplicate check');
      return;
    }

    // Fetch existing items if not already loaded
    let itemsToCheck = existingItems;
    if (existingItems.length === 0) {
      console.log('🔍 No existing items in state, fetching...');
      await fetchExistingItems();
      // Wait a bit for state to update, then fetch again
      await new Promise(resolve => setTimeout(resolve, 100));
      // Try to get the items directly from the API
      try {
        const response = await fetch('/api/wardrobe', {
          headers: {
            'Authorization': `Bearer ${await user?.getIdToken()}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          itemsToCheck = data.items || [];
          console.log('🔍 Fetched items directly for duplicate check:', itemsToCheck.length);
          
          // Debug: Log sample of existing items for analysis
          console.log('🔍 Sample existing items for duplicate analysis:', 
            itemsToCheck.slice(0, 3).map(item => ({
              name: item.name,
              imageUrl: item.imageUrl ? item.imageUrl.substring(0, 50) + '...' : 'none',
              hasImageHash: !!item.imageHash,
              hasMetadata: !!item.metadata,
              fileSize: item.fileSize
            }))
          );
        }
      } catch (error) {
        console.error('Failed to fetch items for duplicate check:', error);
      }
    }

    const newItems: UploadItem[] = [];
    
    console.log(`🔍 Starting duplicate check for ${acceptedFiles.length} files against ${itemsToCheck.length} existing items`);
    
    for (const file of acceptedFiles) {
      console.log(`🔍 Checking file: ${file.name} (${file.size} bytes)`);
      const isDuplicate = await checkForDuplicates(file, itemsToCheck, user);
      
      // Create preview URL (handles HEIC conversion if needed)
      const previewUrl = await createPreviewUrl(file);
      
      newItems.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        preview: previewUrl,
        status: isDuplicate ? 'duplicate' : 'pending',
        progress: 0,
        isDuplicate
      });
    }

    const duplicateCount = newItems.filter(item => item.isDuplicate).length;
    console.log(`🔍 Duplicate check complete: ${duplicateCount}/${newItems.length} duplicates detected`);

    setUploadItems(prev => [...prev, ...newItems]);
  }, [existingItems, fetchExistingItems, user]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp', '.heic', '.heif']
    },
    maxSize: 10 * 1024 * 1024, // 10MB per file
    multiple: true
  });

  const removeItem = (id: string) => {
    setUploadItems(prev => {
      const item = prev.find(item => item.id === id);
      if (item?.preview) {
        URL.revokeObjectURL(item.preview);
      }
      return prev.filter(item => item.id !== id);
    });
  };

  const clearAll = () => {
    uploadItems.forEach(item => {
      if (item.preview) {
        URL.revokeObjectURL(item.preview);
      }
    });
    setUploadItems([]);
    setOverallProgress(0);
  };

  const startBatchUpload = async () => {
    if (uploadItems.length === 0 || !user) {
      toast({
        title: "Missing requirements",
        description: "Please add some images and ensure you're logged in",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setOverallProgress(0);

    const totalItems = uploadItems.length;
    const nonDuplicateItems = uploadItems.filter(item => !item.isDuplicate);
    const duplicateCount = uploadItems.filter(item => item.isDuplicate).length;
    
    console.log(`🚀 Starting batch upload of ${totalItems} items (${duplicateCount} duplicates will be skipped)`);
    
    let completedItems = 0;
    const successfulItems: any[] = [];

    try {
      // Process each item sequentially to avoid overwhelming the server
      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        
        // Skip duplicate items
        if (item.isDuplicate) {
          console.log(`⏭️ Skipping duplicate item: ${item.file.name}`);
          completedItems++;
          setOverallProgress((completedItems / totalItems) * 100);
          continue;
        }
        
        // Update status to uploading
        setUploadItems(prev => prev.map(prevItem => 
          prevItem.id === item.id 
            ? { ...prevItem, status: 'uploading' }
            : prevItem
        ));

        try {
          console.log(`📤 Uploading item ${i + 1}/${totalItems}: ${item.file.name}`);

          // 1️⃣ Upload file to Firebase Storage first
          const imageUrl = await uploadImageToFirebaseStorage(item.file, user.uid, user);
          console.log(`✅ Uploaded to storage: ${imageUrl}`);

          // 2️⃣ Trigger backend analysis
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app';
          const payload = { image: { url: imageUrl } };
          
          console.log("POSTing to backend:", backendUrl + "/analyze-image");
          console.log("Payload:", JSON.stringify(payload));
          
          if (quickMode) {
            // QUICK MODE: Fire-and-forget - trigger analysis but don't wait
            console.log(`🚀 Quick mode: Triggering async analysis for item ${i + 1}`);
            
            fetch(`${backendUrl}/analyze-image`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${await user.getIdToken()}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(payload),
            }).then(response => {
              if (response.ok) {
                console.log(`✅ Background analysis started for item ${i + 1}`);
              } else {
                console.warn(`⚠️ Background analysis may have failed for item ${i + 1}`);
              }
            }).catch(err => {
              console.warn(`⚠️ Background analysis error for item ${i + 1}:`, err);
            });
            
            // Create minimal item record - mark as pending for worker
            const result = { analysis: null }; // Will be processed by background worker
            console.log(`✅ Item ${i + 1} queued for background analysis`);
          } else {
            // NORMAL MODE: Wait for full analysis (blocking)
            const response = await fetch(`${backendUrl}/analyze-image`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${await user.getIdToken()}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(payload),
            });

            if (!response.ok) {
              const errorData = await response.json();
              throw new Error(errorData.error || 'Upload failed');
            }

            var result = await response.json();
            console.log(`✅ Item ${i + 1} analyzed successfully:`, result);
          }

          if (quickMode) {
            // QUICK MODE: Create minimal item, skip full metadata
            console.log(`🚀 Quick mode: Creating minimal item ${i + 1} for background processing`);
            
            // Generate hash for the uploaded item
            const { imageHash, metadata } = await generateImageHashAndMetadata(item.file, user);
            
            const minimalItem = {
              id: `item-${Date.now()}-${i}`,
              name: item.file.name.replace(/\.[^/.]+$/, ""), // Filename without extension
              type: 'unknown',
              color: 'unknown',
              imageUrl: imageUrl,
              userId: user.uid,
              createdAt: new Date().toISOString(),
              processing_status: 'pending', // Mark for background worker
              imageHash: imageHash,
              metadata: metadata,
              fileSize: item.file.size,
              backgroundRemoved: false,
              favorite: false,
              wearCount: 0,
            };
            
            successfulItems.push(minimalItem);
            
            // Update UI
            setUploadItems(prev => prev.map(prevItem => 
              prevItem.id === item.id 
                ? { ...prevItem, status: 'success' }
                : prevItem
            ));
            
          } else if (result.analysis) {
            // NORMAL MODE: Create a proper clothing item from the analysis result
            console.log('🔍 DEBUG: AI Analysis result:', result.analysis);
            console.log('🔍 DEBUG: Analysis fields:', {
              name: result.analysis.name,
              clothing_type: result.analysis.clothing_type,
              type: result.analysis.type,
              color: result.analysis.color,
              primary_color: result.analysis.primary_color,
              style: result.analysis.style,
              occasion: result.analysis.occasion,
              season: result.analysis.season
            });
            
            // Upload image to Firebase Storage
            console.log(`📤 Uploading image ${i + 1} to Firebase Storage...`);
            const imageUrl = await uploadImageToFirebaseStorage(item.file, user.uid, user);
            console.log(`✅ Image uploaded to Firebase Storage: ${imageUrl}`);

            // Generate hash and metadata for the uploaded item
            const { imageHash, metadata } = await generateImageHashAndMetadata(item.file, user);
            
            // Extract GPT-4 analysis data and properly structure it
            const analysisData = result.analysis || {};
            const metadataFromAnalysis = analysisData.metadata || {};
            const visualAttributesFromAnalysis = metadataFromAnalysis.visualAttributes || {};
            
            // Check if analysis data is flat (old format) or nested (new format)
            const isNestedFormat = metadataFromAnalysis.visualAttributes !== undefined;
            
            // If flat format, wrap it in metadata.visualAttributes structure
            const structuredAnalysis = isNestedFormat ? analysisData : {
              ...analysisData,
              metadata: {
                visualAttributes: {
                  // Extract all fields from flat analysis
                  material: analysisData.material || 'cotton',
                  pattern: analysisData.pattern || 'solid',
                  fit: analysisData.fit || 'regular',
                  formalLevel: analysisData.formalLevel || 'casual',
                  sleeveLength: analysisData.sleeveLength || 'unknown',
                  fabricWeight: analysisData.fabricWeight || 'medium',
                  silhouette: analysisData.silhouette || 'regular',
                  genderTarget: analysisData.genderTarget || 'unisex',
                  wearLayer: analysisData.wearLayer || 'Mid',
                  textureStyle: analysisData.textureStyle || 'smooth',
                  length: analysisData.length || 'regular',
                  // Phase 1 new fields
                  neckline: analysisData.neckline || 'none',
                  transparency: analysisData.transparency || 'opaque',
                  collarType: analysisData.collarType || 'none',
                  embellishments: analysisData.embellishments || 'none',
                  printSpecificity: analysisData.printSpecificity || 'none',
                  rise: analysisData.rise || 'none',
                  legOpening: analysisData.legOpening || 'none',
                  heelHeight: analysisData.heelHeight || 'none',
                  statementLevel: analysisData.statementLevel || 5,
                  waistbandType: analysisData.waistbandType || 'none',
                  backgroundRemoved: analysisData.backgroundRemoved || false,
                  hangerPresent: analysisData.hangerPresent || false
                },
                naturalDescription: analysisData.naturalDescription || ''
              }
            };
            
            const clothingItem = {
              id: `item-${Date.now()}-${i}`,
              name: analysisData.name || analysisData.clothing_type || 'Analyzed Item',
              type: analysisData.type || analysisData.clothing_type || 'unknown',
              color: analysisData.color || analysisData.primary_color || 'unknown',
              imageUrl: imageUrl, // Use Firebase Storage URL
              userId: user.uid,
              createdAt: new Date().toISOString(),
              analysis: structuredAnalysis,  // Send properly structured analysis
              // Add duplicate detection fields
              imageHash: imageHash,
              metadata: metadata,  // Keep image file metadata
              fileSize: item.file.size,
              // Add other required fields
              brand: analysisData.brand || '',
              style: analysisData.style || '',
              material: analysisData.material || '',
              season: analysisData.season || [],
              occasion: analysisData.occasion || [],
              subType: analysisData.subType || '',
              gender: analysisData.gender || 'unisex',
              backgroundRemoved: false,
              favorite: false,
              wearCount: 0,
              lastWorn: null,
              mood: analysisData.mood || []
            };
            
            // Normalize the item metadata before saving
            const { normalizeItemMetadata } = await import('../../lib/normalization');
            const normalizedItem = normalizeItemMetadata(clothingItem);
            
            // Save to database via the wardrobe API
            try {
              console.log(`💾 Saving item ${i + 1} to database...`);
              console.log('🔍 DEBUG: Clothing item being saved:', normalizedItem);
              console.log('🔍 DEBUG: About to call /api/wardrobe with:', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${await user.getIdToken()}`,
                },
                body: JSON.stringify(normalizedItem)
              });
              
              const saveResponse = await fetch('/api/wardrobe', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${await user.getIdToken()}`,
                },
                body: JSON.stringify(normalizedItem),
              });
              
              console.log('🔍 DEBUG: Save response status:', saveResponse.status);
              console.log('🔍 DEBUG: Save response ok:', saveResponse.ok);

              if (!saveResponse.ok) {
                throw new Error(`Failed to save item: ${saveResponse.statusText}`);
              }

              const savedItem = await saveResponse.json();
              console.log(`✅ Item ${i + 1} saved to database:`, savedItem);
              
              successfulItems.push(savedItem);
            } catch (saveError) {
              console.error(`❌ Failed to save item ${i + 1} to database:`, saveError);
              // Still add to successful items but mark as not saved
              successfulItems.push({ ...clothingItem, saveError: saveError.message });
            }

            // Update status to success
            setUploadItems(prev => prev.map(prevItem => 
              prevItem.id === item.id 
                ? { ...prevItem, status: 'success', progress: 100, analysisResult: result.analysis }
                : prevItem
            ));
          } else {
            throw new Error('No analysis result from server');
          }

          completedItems++;
          setOverallProgress((completedItems / totalItems) * 100);

        } catch (error) {
          console.error(`❌ Upload failed for item ${i + 1}:`, error);
          
          // Update status to error
          setUploadItems(prev => prev.map(prevItem => 
            prevItem.id === item.id 
              ? { 
                  ...prevItem, 
                  status: 'error', 
                  error: error instanceof Error ? error.message : 'Upload failed',
                  progress: 0 
                }
              : prevItem
          ));
        }

        // Small delay between uploads to avoid overwhelming the server
        await new Promise(resolve => setTimeout(resolve, 500));
      }

      // All uploads completed
      setOverallProgress(100);
      
      if (successfulItems.length > 0) {
        const duplicateCount = uploadItems.filter(item => item.isDuplicate).length;
        const totalProcessed = successfulItems.length + duplicateCount;
        
        if (quickMode) {
          // Quick mode: Show background processing message
          toast({
            title: "Analyzing your items in background... ✨",
            description: `${successfulItems.length} items uploaded! AI is analyzing them now while you continue.`,
            duration: 3000,
          });
        } else {
          // Normal mode: Show completion message
          toast({
            title: "Batch upload completed! ✨",
            description: `Successfully uploaded ${successfulItems.length} items with AI analysis${duplicateCount > 0 ? ` (${duplicateCount} duplicates skipped)` : ''}`,
          });
        }

        if (onUploadComplete) {
          onUploadComplete(successfulItems);
        }
      }

      const expectedNonDuplicates = uploadItems.filter(item => !item.isDuplicate).length;
      if (successfulItems.length < expectedNonDuplicates) {
        toast({
          title: "Some uploads failed",
          description: `${expectedNonDuplicates - successfulItems.length} items failed to upload`,
          variant: "destructive",
        });
      }

    } catch (error) {
      console.error('Batch upload error:', error);
      const errorMessage = 'Failed to complete batch upload';
      
      if (onError) {
        onError(errorMessage);
      }
      
      toast({
        title: "Upload failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const getStatusIcon = (status: UploadItem['status']) => {
    switch (status) {
      case 'pending':
        return <ImageIcon className="w-4 h-4 text-gray-400" />;
      case 'analyzing':
        return <Brain className="w-4 h-4 text-purple-500 animate-pulse" />;
      case 'uploading':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'duplicate':
        return <AlertCircle className="w-4 h-4 text-orange-500" />;
      default:
        return <ImageIcon className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: UploadItem['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'analyzing':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
      case 'uploading':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
      case 'success':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'duplicate':
        return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div>
        <div className="text-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Batch Upload with AI ✨
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Upload multiple clothing items at once. AI will automatically analyze and save each item to your wardrobe.
          </p>
          <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
            <p className="text-xs text-blue-700 dark:text-blue-300">
              <strong>Auto-save mode:</strong> Items are automatically saved with AI analysis - no manual editing required.
            </p>
          </div>
        </div>

        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/20"
              : "border-gray-300 dark:border-gray-600 hover:border-emerald-400 dark:hover:border-emerald-500"
          }`}
        >
          <input {...getInputProps()} />
          <Camera className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {isDragActive
              ? "Drop the images here..."
              : "Drag & drop multiple images, or click to select"}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Supports JPG, PNG, GIF, WebP, HEIC (max 10MB per file)
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500">
            You can select multiple files or drag them in batches
          </p>
        </div>
      </div>

      {/* File List */}
      {uploadItems.length > 0 && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Selected Files ({uploadItems.length})</CardTitle>
                <CardDescription>
                  Review your selected images before uploading
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearAll}
                  disabled={isUploading}
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Clear All
                </Button>
                <Button
                  onClick={startBatchUpload}
                  disabled={
                    isUploading || 
                    uploadItems.length === 0 || 
                    (requireStaging && uploadItems.length < requiredCount)
                  }
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Analyzing item {Math.round(overallProgress / (100 / uploadItems.length))} of {uploadItems.length}...
                    </>
                  ) : requireStaging && uploadItems.length < requiredCount ? (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Select {requiredCount} items to begin ({uploadItems.length}/{requiredCount})
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Upload & Analyze All ({uploadItems.length} {uploadItems.length === 1 ? 'item' : 'items'})
                    </>
                  )}
                </Button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent>
            {/* Overall Progress */}
            {isUploading && (
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span>Overall Progress</span>
                  <span>{Math.round(overallProgress)}%</span>
                </div>
                <Progress value={overallProgress} className="h-2" />
              </div>
            )}

            {/* File Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {uploadItems.map((item) => (
                <div
                  key={item.id}
                  className="relative border rounded-lg overflow-hidden group"
                >
                  {/* Image Preview */}
                  <div className="aspect-square bg-gray-100 dark:bg-gray-800">
                    <img
                      src={item.preview}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                  </div>

                  {/* Status Overlay */}
                  <div className="absolute top-2 right-2">
                    <Badge className={getStatusColor(item.status)}>
                      {getStatusIcon(item.status)}
                    </Badge>
                  </div>

                  {/* Remove Button */}
                  {!isUploading && (
                    <Button
                      variant="destructive"
                      size="sm"
                      className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => removeItem(item.id)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}

                  {/* Progress Bar */}
                  {item.status === 'uploading' && (
                    <div className="absolute bottom-0 left-0 right-0">
                      <Progress value={item.progress} className="h-1 rounded-none" />
                    </div>
                  )}

                  {/* Error Message */}
                  {item.status === 'error' && item.error && (
                    <div className="absolute bottom-0 left-0 right-0 bg-red-500 text-white text-xs p-1 text-center">
                      {item.error}
                    </div>
                  )}

                  {/* Duplicate Message */}
                  {item.status === 'duplicate' && (
                    <div className="absolute bottom-0 left-0 right-0 bg-orange-500 text-white text-xs p-1 text-center">
                      Already exists
                    </div>
                  )}

                  {/* File Info */}
                  <div className="p-2 bg-white dark:bg-gray-900">
                    <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                      {item.file.name}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {(item.file.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {/* Upload Summary */}
            {!isUploading && uploadItems.length > 0 && (
              <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <div className="flex items-center justify-between text-sm">
                  <span>Ready to upload:</span>
                  <span className="font-medium">
                    {uploadItems.filter(item => !item.isDuplicate).length} items
                    {uploadItems.filter(item => item.isDuplicate).length > 0 && (
                      <span className="text-orange-600 ml-2">
                        ({uploadItems.filter(item => item.isDuplicate).length} duplicates skipped)
                      </span>
                    )}
                  </span>
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Total size: {(uploadItems.reduce((acc, item) => acc + item.file.size, 0) / 1024 / 1024).toFixed(1)} MB
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
} 