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
  Image as ImageIcon
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface BatchImageUploadProps {
  onUploadComplete?: (items: any[]) => void;
  onError?: (message: string) => void;
  userId: string;
}

interface UploadItem {
  id: string;
  file: File;
  preview: string;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
}

export default function BatchImageUpload({ onUploadComplete, onError, userId }: BatchImageUploadProps) {
  const { toast } = useToast();
  const [uploadItems, setUploadItems] = useState<UploadItem[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newItems: UploadItem[] = acceptedFiles.map(file => ({
      id: `${Date.now()}-${Math.random()}`,
      file,
      preview: URL.createObjectURL(file),
      status: 'pending',
      progress: 0
    }));

    setUploadItems(prev => [...prev, ...newItems]);
  }, []);

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
    if (uploadItems.length === 0) {
      toast({
        title: "No files selected",
        description: "Please add some images to upload",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);
    setOverallProgress(0);

    const totalItems = uploadItems.length;
    let completedItems = 0;
    const successfulItems: any[] = [];

    try {
      // Process each item sequentially to avoid overwhelming the server
      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        
        // Update status to uploading
        setUploadItems(prev => prev.map(prevItem => 
          prevItem.id === item.id 
            ? { ...prevItem, status: 'uploading' }
            : prevItem
        ));

        try {
          // Simulate upload with progress updates
          for (let progress = 0; progress <= 100; progress += 10) {
            setUploadItems(prev => prev.map(prevItem => 
              prevItem.id === item.id 
                ? { ...prevItem, progress }
                : prevItem
            ));
            
            setOverallProgress(((completedItems * 100) + progress) / totalItems);
            await new Promise(resolve => setTimeout(resolve, 100));
          }

          // Simulate successful upload
          const mockItem = {
            id: item.id,
            name: `Item ${i + 1}`,
            type: 'clothing',
            color: 'unknown',
            imageUrl: item.preview,
            wearCount: 0,
            favorite: false,
            createdAt: new Date().toISOString()
          };

          successfulItems.push(mockItem);

          // Update status to success
          setUploadItems(prev => prev.map(prevItem => 
            prevItem.id === item.id 
              ? { ...prevItem, status: 'success', progress: 100 }
              : prevItem
          ));

          completedItems++;

        } catch (error) {
          // Update status to error
          setUploadItems(prev => prev.map(prevItem => 
            prevItem.id === item.id 
              ? { 
                  ...prevItem, 
                  status: 'error', 
                  error: 'Upload failed',
                  progress: 0 
                }
              : prevItem
          ));
        }

        // Small delay between uploads
        await new Promise(resolve => setTimeout(resolve, 200));
      }

      // All uploads completed
      setOverallProgress(100);
      
      if (successfulItems.length > 0) {
        toast({
          title: "Batch upload completed!",
          description: `Successfully uploaded ${successfulItems.length} items`,
        });

        if (onUploadComplete) {
          onUploadComplete(successfulItems);
        }
      }

      if (successfulItems.length < totalItems) {
        toast({
          title: "Some uploads failed",
          description: `${totalItems - successfulItems.length} items failed to upload`,
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
      case 'uploading':
        return <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <ImageIcon className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: UploadItem['status']) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200';
      case 'uploading':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'success':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
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
            Batch Upload Clothing Items
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Upload multiple clothing items at once to quickly build your wardrobe
          </p>
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
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Upload All ({uploadItems.length})
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
                  <span className="font-medium">{uploadItems.length} items</span>
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