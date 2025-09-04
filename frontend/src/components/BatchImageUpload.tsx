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
  status: 'pending' | 'analyzing' | 'uploading' | 'analyzed' | 'success' | 'error';
  progress: number;
  error?: string;
  analysisResult?: any;
}

const fileToBase64 = (file: File): Promise<string> => new Promise((resolve, reject) => {
  const reader = new FileReader();
  reader.onload = () => resolve(reader.result as string);
  reader.onerror = reject;
  reader.readAsDataURL(file);
});

export default function BatchImageUpload({ onUploadComplete, onError, userId }: BatchImageUploadProps) {
  
  const { user } = useFirebase();
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
    let completedItems = 0;
    const clothingItems: any[] = [];

    try {
      // Step 1: Analyze all items first
      console.log(`🤖 Analyzing ${totalItems} items with AI...`);
      
      for (let i = 0; i < uploadItems.length; i++) {
        const item = uploadItems[i];
        
        try {
          // Update status to uploading
          setUploadItems(prev => prev.map(prevItem => 
            prevItem.id === item.id 
              ? { ...prevItem, status: 'uploading' }
              : prevItem
          ));

          // Convert file to base64 once for both analysis and storage
          const base64Image = await fileToBase64(item.file);
          
          // Call backend directly for AI analysis
          const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
          const payload = { url: base64Image };
          
          console.log(`🤖 Analyzing item ${i + 1}/${totalItems} with AI...`);
          
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
            throw new Error(errorData.error || 'Analysis failed');
          }

          const result = await response.json();
          console.log(`✅ Item ${i + 1} analyzed successfully:`, result);

          if (result.analysis) {
            // Extract the actual analysis data from the nested structure
            const analysis = result.analysis.analysis || result.analysis;
            
            // Create a proper clothing item from the analysis result
            const clothingItem = {
              name: analysis.name || 'Analyzed Item',
              type: analysis.type || 'unknown',
              color: analysis.dominantColors && analysis.dominantColors.length > 0 
                ? analysis.dominantColors[0].name 
                : 'unknown',
              imageUrl: base64Image, // Reuse the base64 image
              style: analysis.style || [],
              occasion: analysis.occasion || [],
              season: analysis.season || ['all'],
              dominantColors: analysis.dominantColors || [],
              matchingColors: analysis.matchingColors || [],
              tags: analysis.tags || [],
              metadata: {
                analysisTimestamp: Date.now(),
                originalType: analysis.type || 'clothing',
                styleTags: analysis.style || [],
                occasionTags: analysis.occasion || [],
                colorAnalysis: {
                  dominant: analysis.dominantColors || [],
                  matching: analysis.matchingColors || []
                },
                visualAttributes: analysis.metadata?.visualAttributes || {},
                itemMetadata: {
                  tags: analysis.tags || [],
                  careInstructions: "Check care label"
                }
              },
              favorite: false,
              wearCount: 0,
              lastWorn: null
            };
            
            clothingItems.push(clothingItem);
            console.log(`🔍 DEBUG: Added item ${i + 1} to clothingItems array. Total items: ${clothingItems.length}`);

            // Update status to analyzed
            setUploadItems(prev => prev.map(prevItem => 
              prevItem.id === item.id 
                ? { ...prevItem, status: 'analyzed', progress: 50, analysisResult: result.analysis }
                : prevItem
            ));
          } else {
            throw new Error('No analysis result from server');
          }

          completedItems++;
          setOverallProgress((completedItems / totalItems) * 50); // First half for analysis

        } catch (error) {
          console.error(`❌ Analysis failed for item ${i + 1}:`, error);
          
          // Update status to error
          setUploadItems(prev => prev.map(prevItem => 
            prevItem.id === item.id 
              ? { ...prevItem, status: 'error', progress: 0, error: error.message }
              : prevItem
          ));
        }
      }

      // Step 2: Save all items in batch
      console.log(`🔍 DEBUG: clothingItems array length: ${clothingItems.length}`);
      console.log(`🔍 DEBUG: clothingItems content:`, clothingItems);
      
      if (clothingItems.length > 0) {
        console.log(`💾 Saving ${clothingItems.length} items to database in batch...`);
        
        try {
          const batchResponse = await fetch('/api/wardrobe/batch', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${await user.getIdToken()}`,
            },
            body: JSON.stringify(clothingItems),
          });

          if (!batchResponse.ok) {
            const errorData = await batchResponse.json();
            throw new Error(errorData.detail || `Batch save failed: ${batchResponse.statusText}`);
          }

          const batchResult = await batchResponse.json();
          console.log(`✅ Batch save completed:`, batchResult);
          
          // Update all analyzed items to success status
          setUploadItems(prev => prev.map(item => 
            item.status === 'analyzed' 
              ? { ...item, status: 'success', progress: 100 }
              : item
          ));
          
          setOverallProgress(100);
          
          // Show success toast
          toast({
            title: "Batch upload completed! ✨",
            description: `${batchResult.successful_items} items added successfully`,
            variant: "default",
          });
          
          // Call completion callback with successful items
          onUploadComplete?.(batchResult.successful_items_data || []);
          
        } catch (batchError) {
          console.error(`❌ Batch save failed:`, batchError);
          toast({
            title: "Batch save failed",
            description: batchError.message,
            variant: "destructive",
          });
        }
      } else {
        toast({
          title: "No items analyzed",
          description: "No items were successfully analyzed",
          variant: "destructive",
        });
      }
      
    } catch (error) {
      console.error('❌ Batch upload failed:', error);
      toast({
        title: "Upload failed",
        description: error.message,
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
      case 'analyzed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <ImageIcon className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusText = (status: UploadItem['status']) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'analyzing':
        return 'Analyzing...';
      case 'uploading':
        return 'Uploading...';
      case 'analyzed':
        return 'Analyzed';
      case 'success':
        return 'Success';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${isUploading ? 'pointer-events-none opacity-50' : ''}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-semibold mb-2">
          {isDragActive ? 'Drop images here' : 'Upload Images'}
        </h3>
        <p className="text-gray-600 mb-4">
          Drag and drop images here, or click to select files
        </p>
        <p className="text-sm text-gray-500">
          Supports: JPG, PNG, GIF, WebP (max 10MB each)
        </p>
      </div>

      {/* Progress Bar */}
      {isUploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span>{Math.round(overallProgress)}%</span>
          </div>
          <Progress value={overallProgress} className="w-full" />
        </div>
      )}

      {/* Upload Items */}
      {uploadItems.length > 0 && (
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="text-lg font-semibold">
              Upload Queue ({uploadItems.length} items)
            </h4>
            <div className="space-x-2">
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
                    Processing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Start Batch Upload
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {uploadItems.map((item) => (
              <Card key={item.id} className="relative">
                <CardContent className="p-4">
                  <div className="space-y-3">
                    {/* Image Preview */}
                    <div className="relative">
                      <img
                        src={item.preview}
                        alt="Upload preview"
                        className="w-full h-32 object-cover rounded-lg"
                      />
                      <Button
                        variant="destructive"
                        size="sm"
                        className="absolute top-2 right-2 h-6 w-6 p-0"
                        onClick={() => removeItem(item.id)}
                        disabled={isUploading}
                      >
                        <X className="w-3 h-3" />
                      </Button>
                    </div>

                    {/* Status */}
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(item.status)}
                      <span className="text-sm font-medium">
                        {getStatusText(item.status)}
                      </span>
                      {item.status === 'error' && (
                        <Badge variant="destructive" className="text-xs">
                          Error
                        </Badge>
                      )}
                    </div>

                    {/* Progress Bar */}
                    {item.status === 'uploading' && (
                      <Progress value={item.progress} className="w-full" />
                    )}

                    {/* Error Message */}
                    {item.status === 'error' && item.error && (
                      <p className="text-xs text-red-600">{item.error}</p>
                    )}

                    {/* Analysis Result */}
                    {item.analysisResult && (
                      <div className="text-xs space-y-1">
                        <p><strong>Name:</strong> {item.analysisResult.name}</p>
                        <p><strong>Type:</strong> {item.analysisResult.type}</p>
                        <p><strong>Color:</strong> {item.analysisResult.color}</p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
