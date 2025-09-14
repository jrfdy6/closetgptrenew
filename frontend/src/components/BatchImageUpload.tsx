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
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
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

// Helper function to check for duplicate items
const checkForDuplicates = async (file: File, existingItems: any[]): Promise<boolean> => {
  // Simple duplicate detection based on file name and size
  // In a more sophisticated implementation, you could use image hashing
  const fileName = file.name.toLowerCase();
  const fileSize = file.size;
  
  console.log('🔍 Checking for duplicates:', {
    fileName,
    fileSize,
    existingItemsCount: existingItems.length,
    existingItems: existingItems.map(item => ({
      id: item.id,
      name: item.name,
      imageUrl: item.imageUrl,
      hasImageUrl: !!item.imageUrl
    }))
  });
  
  // Extract base filename once outside the callback
  const baseFileName = fileName.split('.')[0];
  
  const isDuplicate = existingItems.some(item => {
    // Check if the item has an imageUrl (from Firebase Storage)
    if (item.imageUrl) {
      // Extract filename from Firebase Storage URL
      const urlParts = item.imageUrl.split('/');
      const existingFileName = urlParts[urlParts.length - 1].split('?')[0].toLowerCase();
      
      // Compare filenames (without extension) and file sizes
      const baseExistingFileName = existingFileName.split('.')[0];
      
      // Check if the original filename is in the URL (Firebase might preserve it)
      const urlContainsOriginalName = item.imageUrl.toLowerCase().includes(baseFileName);
      
      // More flexible name matching - check if the base filename is contained in the existing filename
      const nameMatch = baseFileName === baseExistingFileName || 
                       urlContainsOriginalName ||
                       baseExistingFileName.includes(baseFileName) ||
                       baseFileName.includes(baseExistingFileName);
      
      // More flexible size matching - allow up to 5KB difference for compression
      const sizeMatch = Math.abs((item.fileSize || 0) - fileSize) < 5000;
      
      console.log('🔍 Comparing with existing item:', {
        itemName: item.name,
        existingFileName,
        baseFileName,
        baseExistingFileName,
        urlContainsOriginalName,
        nameMatch,
        sizeMatch,
        itemFileSize: item.fileSize,
        newFileSize: fileSize,
        imageUrl: item.imageUrl
      });
      
      return nameMatch && sizeMatch;
    }
    
    // Fallback: check by item name if no imageUrl
    if (item.name) {
      const itemNameMatch = item.name.toLowerCase().includes(baseFileName) || 
                           baseFileName.includes(item.name.toLowerCase());
      
      console.log('🔍 Fallback comparison by name:', {
        itemName: item.name,
        baseFileName,
        itemNameMatch
      });
      
      return itemNameMatch;
    }
    
    return false;
  });
  
  console.log('🔍 Duplicate check result:', isDuplicate);
  return isDuplicate;
};

export default function BatchImageUpload({ onUploadComplete, onError, userId }: BatchImageUploadProps) {
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
        }
      } catch (error) {
        console.error('Failed to fetch items for duplicate check:', error);
      }
    }

    const newItems: UploadItem[] = [];
    
    for (const file of acceptedFiles) {
      const isDuplicate = await checkForDuplicates(file, itemsToCheck);
      
      newItems.push({
        id: `${Date.now()}-${Math.random()}`,
        file,
        preview: URL.createObjectURL(file),
        status: isDuplicate ? 'duplicate' : 'pending',
        progress: 0,
        isDuplicate
      });
    }

    setUploadItems(prev => [...prev, ...newItems]);
  }, [existingItems, fetchExistingItems, user]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
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

          // 2️⃣ Send URL to backend for analysis
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
          const payload = { image: { url: imageUrl } };
          
          console.log("POSTing to backend:", backendUrl + "/analyze-image");
          console.log("Payload:", JSON.stringify(payload));
          
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

          const result = await response.json();
          console.log(`✅ Item ${i + 1} analyzed successfully:`, result);

          if (result.analysis) {
            // Create a proper clothing item from the analysis result
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

            const clothingItem = {
              id: `item-${Date.now()}-${i}`,
              name: result.analysis.name || result.analysis.clothing_type || 'Analyzed Item',
              type: result.analysis.type || result.analysis.clothing_type || 'unknown',
              color: result.analysis.color || result.analysis.primary_color || 'unknown',
              imageUrl: imageUrl, // Use Firebase Storage URL
              userId: user.uid,
              createdAt: new Date().toISOString(),
              analysis: result.analysis,
              // Add other required fields
              brand: result.analysis.brand || '',
              style: result.analysis.style || '',
              material: result.analysis.material || '',
              season: result.analysis.season || [],
              occasion: result.analysis.occasion || [],
              subType: result.analysis.subType || '',
              gender: result.analysis.gender || 'unisex',
              backgroundRemoved: false,
              favorite: false,
              wearCount: 0,
              lastWorn: null
            };
            
            // Save to database via the wardrobe API
            try {
              console.log(`💾 Saving item ${i + 1} to database...`);
              console.log('🔍 DEBUG: Clothing item being saved:', clothingItem);
              console.log('🔍 DEBUG: About to call /api/wardrobe with:', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${await user.getIdToken()}`,
                },
                body: JSON.stringify(clothingItem)
              });
              
              const saveResponse = await fetch('/api/wardrobe', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${await user.getIdToken()}`,
                },
                body: JSON.stringify(clothingItem),
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
        
        toast({
          title: "Batch upload completed! ✨",
          description: `Successfully uploaded ${successfulItems.length} items with AI analysis${duplicateCount > 0 ? ` (${duplicateCount} duplicates skipped)` : ''}`,
        });

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
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'uploading':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'success':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
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
            Supports JPG, PNG, GIF, WebP (max 10MB per file)
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
                  disabled={isUploading || uploadItems.length === 0}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  {isUploading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Uploading with AI...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-4 h-4 mr-2" />
                      Upload All with AI ({uploadItems.length})
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