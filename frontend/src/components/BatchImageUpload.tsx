'use client';

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, X, Trash2 } from "lucide-react";
import { useWardrobe } from "@/lib/hooks/useWardrobe";
import { checkForDuplicateImages } from "@/lib/firebase/wardrobeService";
import { createClothingItemFromAnalysis } from "@/lib/utils/itemProcessing";
import type { ClothingItem } from "@/types/wardrobe";
import type { OpenAIClothingAnalysis } from "@/shared/types";
import { Button } from "@/components/ui/button";
import { Progress } from '@/components/ui/progress';

interface BatchImageUploadProps {
  onUploadComplete: (items: ClothingItem[]) => void;
  onError: (message: string) => void;
  userId: string;
}

export default function BatchImageUpload({ onUploadComplete, onError, userId }: BatchImageUploadProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const { processImages } = useWardrobe();

  const convertHeicToJpeg = async (file: File): Promise<File> => {
    try {
      const heic2any = (await import('heic2any')).default;
      const jpegBlob = await heic2any({
        blob: file,
        toType: 'image/jpeg',
        quality: 0.8
      });
      // Handle both single blob and array of blobs
      const blob = Array.isArray(jpegBlob) ? jpegBlob[0] : jpegBlob;
      return new File([blob], file.name.replace(/\.heic$/i, '.jpg'), { type: 'image/jpeg' });
    } catch (error) {
      console.error('Error converting HEIC to JPEG:', error);
      throw new Error('Failed to convert HEIC image');
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      // Convert HEIC files to JPEG and keep other files as is
      const processedFiles = await Promise.all(
        acceptedFiles.map(async (file) => {
          if (file.type === 'image/heic' || file.name.toLowerCase().endsWith('.heic')) {
            return await convertHeicToJpeg(file);
          }
          return file;
        })
      );
      
      setFiles(prev => [...prev, ...processedFiles]);
      
      // Create previews for all files
      const newPreviews = await Promise.all(
        processedFiles.map(file => {
          return new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onload = () => {
              resolve(reader.result as string);
            };
            reader.readAsDataURL(file);
          });
        })
      );
      
      setPreviews(prev => [...prev, ...newPreviews]);
    } catch (error) {
      console.error('Error processing dropped files:', error);
      onError('Failed to process dropped files');
    }
  }, [onError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.heic']
    },
    multiple: true
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setPreviews(prev => prev.filter((_, i) => i !== index));
  };

  const clearAllFiles = () => {
    setFiles([]);
    setPreviews([]);
    setUploadProgress(0);
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      onError("Please select at least one image to upload");
      return;
    }

    setUploading(true);
    try {
      // Check for duplicates first
      const duplicateCheck = await checkForDuplicateImages(
        userId,
        files,
        { similarityThreshold: 0.95 }
      );

      if (!duplicateCheck.success || !duplicateCheck.data) {
        onError(duplicateCheck.error || "Failed to check for duplicates");
        setUploading(false);
        return;
      }

      const { uniqueImages, duplicateHashes, similarImages } = duplicateCheck.data;

      // Show warning about duplicates but continue with unique images
      if (duplicateHashes.length > 0 || similarImages.length > 0) {
        const messages = [];
        if (duplicateHashes.length > 0) {
          messages.push(`${duplicateHashes.length} duplicate images were found`);
        }
        if (similarImages.length > 0) {
          messages.push(`${similarImages.length} similar images were found`);
        }
        onError(messages.join('. ') + '. Processing remaining unique images...');
      }

      // Process unique images if any exist
      if (!uniqueImages || uniqueImages.length === 0) {
        onError("No unique images to process");
        setUploading(false);
        return;
      }

      try {
        const response = await processImages(uniqueImages);
        if (response.success && response.data?.newItems && response.data.newItems.length > 0) {
          onUploadComplete(response.data.newItems);
          clearAllFiles(); // Clear files after successful upload
        } else {
          onError(response.error || "No items were created from the images");
        }
      } catch (error: unknown) {
        console.error('Error processing images:', error);
        onError(error instanceof Error ? error.message : "Failed to upload images");
      }
    } catch (error: unknown) {
      console.error('Error in handleUpload:', error);
      onError(error instanceof Error ? error.message : "Failed to upload images");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'}`}
      >
        <input {...getInputProps()} />
        {isDragActive ? (
          <p>Drop the images here...</p>
        ) : (
          <p>Drag and drop images here, or click to select files</p>
        )}
      </div>

      {previews.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium">Selected Images ({previews.length})</h3>
            <Button
              onClick={clearAllFiles}
              variant="ghost"
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear All
            </Button>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
            {previews.map((preview, index) => (
              <div key={index} className="relative group">
                <div className="relative w-full h-48">
                  <img
                    src={preview}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-full object-cover rounded-lg"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-opacity rounded-lg flex items-center justify-center">
                    <Button
                      onClick={() => removeFile(index)}
                      variant="destructive"
                      size="icon"
                      className="opacity-0 group-hover:opacity-100"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                <p className="mt-1 text-sm text-gray-500 truncate">
                  {files[index].name}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {previews.length > 0 && (
        <div className="flex justify-end gap-4">
          <Button
            onClick={clearAllFiles}
            variant="outline"
          >
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            disabled={uploading}
          >
            {uploading ? "Processing..." : "Add to Wardrobe"}
          </Button>
        </div>
      )}

      {uploading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h3 className="text-xl font-semibold mb-2">Processing Your Images</h3>
            <p className="text-gray-600 mb-4">We're analyzing your clothing items and getting everything ready. This might take a moment...</p>
            <p className="text-sm text-gray-500">
              {files.length} image{files.length !== 1 ? 's' : ''} being processed
            </p>
          </div>
        </div>
      )}

      {uploading && (
        <div className="mt-4">
          <Progress value={uploadProgress} className="w-full" />
        </div>
      )}
    </div>
  );
} 