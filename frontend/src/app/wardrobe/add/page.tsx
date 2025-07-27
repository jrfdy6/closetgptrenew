"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { uploadImage } from "@/lib/firebase/storageService";
import { analyzeClothingImage } from "@/lib/services/clothingImageAnalysis";
import { createClothingItemFromAnalysis } from "@/lib/utils/itemProcessing";
import { addWardrobeItem } from "@/lib/firebase/wardrobeService";
import type { OpenAIClothingAnalysis } from '@/shared/types';
import ProtectedRoute from "@/components/ProtectedRoute";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { Upload, Sparkles, Loader2, CheckCircle, AlertCircle, ArrowLeft } from "lucide-react";

type ProcessingStep = 'idle' | 'uploading' | 'analyzing' | 'saving' | 'complete' | 'error';

export default function AddItemPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<OpenAIClothingAnalysis | null>(null);
  const [currentStep, setCurrentStep] = useState<ProcessingStep>('idle');
  const [error, setError] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);

  const isAuthenticated = !!user;

  const handleImageSelect = useCallback((file: File) => {
    setImage(file);
    setAnalysis(null);
    setError(null);
    setCurrentStep('idle');
    setProgress(0);
    
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  }, []);

  const processImage = useCallback(async () => {
    if (!image || !user) {
      toast.error('Please select an image and ensure you are signed in');
      return;
    }

    setCurrentStep('uploading');
    setProgress(10);
    setError(null);

    try {
      // Upload image to storage
      const uploadedImage = await uploadImage(image, user.uid);
      setProgress(40);

      // Analyze the image
      setCurrentStep('analyzing');
      setProgress(60);
      const analysisResult = await analyzeClothingImage(uploadedImage.url);
      setAnalysis(analysisResult);
      setProgress(80);

      // Create clothing item from analysis
      setCurrentStep('saving');
      setProgress(90);
      const newItem = createClothingItemFromAnalysis(analysisResult, user.uid, uploadedImage.url);
      
      // Add to database
      const result = await addWardrobeItem(newItem);
      if (!result.success) {
        throw new Error(result.error || 'Failed to add item to wardrobe');
      }

      setCurrentStep('complete');
      setProgress(100);
      toast.success("Item added successfully!");
      
      // Navigate back to wardrobe after a short delay
      setTimeout(() => {
        router.push("/wardrobe");
      }, 1500);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to process image";
      setError(errorMessage);
      setCurrentStep('error');
      toast.error(errorMessage);
    }
  }, [image, user, router]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (authLoading) {
      toast.error('Please wait while we verify your authentication');
      return;
    }

    if (!isAuthenticated || !user) {
      toast.error('Please sign in to add items');
      return;
    }

    if (!image) {
      toast.error('Please select an image first');
      return;
    }

    await processImage();
  }, [authLoading, isAuthenticated, user, image, processImage]);

  const resetForm = useCallback(() => {
    setImage(null);
    setPreview(null);
    setAnalysis(null);
    setCurrentStep('idle');
    setError(null);
    setProgress(0);
  }, []);

  const getStepProgress = (step: ProcessingStep) => {
    if (currentStep === 'error') return 0;
    if (currentStep === 'complete') return 100;
    
    const steps: ProcessingStep[] = ['idle', 'uploading', 'analyzing', 'saving', 'complete'];
    const currentIndex = steps.indexOf(currentStep);
    const stepIndex = steps.indexOf(step);
    
    if (stepIndex < currentIndex) return 100;
    if (stepIndex === currentIndex) return progress;
    return 0;
  };

  if (authLoading) {
    return (
      <ProtectedRoute>
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading...</p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.back()}
            className="mb-4 flex items-center text-gray-600 hover:text-gray-900 transition-colors"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </button>
          <h1 className="text-3xl font-bold">Add New Item</h1>
          <p className="text-gray-600 mt-2">
            Upload a photo of your clothing item and let AI analyze it for you
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Upload Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Upload Image
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Upload Area */}
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                    currentStep === 'idle' && !preview
                      ? 'border-gray-300 hover:border-blue-500 hover:bg-blue-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                  onClick={() => {
                    if (currentStep === 'idle') {
                      document.getElementById('image-upload')?.click();
                    }
                  }}
                >
                  <input
                    id="image-upload"
                    type="file"
                    accept="image/*"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) handleImageSelect(file);
                    }}
                    className="hidden"
                  />
                  
                  {preview ? (
                    <div className="space-y-4">
                      <img
                        src={preview}
                        alt="Preview"
                        className="max-w-xs mx-auto rounded-lg shadow-md"
                      />
                      <p className="text-sm text-gray-600">
                        Click to change image
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Upload className="w-12 h-12 mx-auto text-gray-400" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          <span className="text-blue-600">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-sm text-gray-500 mt-1">
                          PNG, JPG or JPEG (MAX. 10MB)
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Progress Indicator */}
                {currentStep !== 'idle' && currentStep !== 'complete' && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Processing...</span>
                      <span>{progress}%</span>
                    </div>
                    <Progress value={progress} className="w-full" />
                    <div className="flex justify-between text-xs text-gray-500">
                      <span className={getStepProgress('uploading') === 100 ? 'text-green-600' : ''}>
                        Uploading
                      </span>
                      <span className={getStepProgress('analyzing') === 100 ? 'text-green-600' : ''}>
                        Analyzing
                      </span>
                      <span className={getStepProgress('saving') === 100 ? 'text-green-600' : ''}>
                        Saving
                      </span>
                    </div>
                  </div>
                )}

                {/* Success State */}
                {currentStep === 'complete' && (
                  <div className="flex items-center gap-2 text-green-600 bg-green-50 p-3 rounded-lg">
                    <CheckCircle className="w-5 h-5" />
                    <span>Item added successfully!</span>
                  </div>
                )}

                {/* Error State */}
                {currentStep === 'error' && error && (
                  <div className="flex items-center gap-2 text-red-600 bg-red-50 p-3 rounded-lg">
                    <AlertCircle className="w-5 h-5" />
                    <span>{error}</span>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-2">
                  {currentStep === 'idle' && image && (
                    <Button
                      onClick={processImage}
                      className="flex-1"
                      disabled={!image}
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      Analyze & Add Item
                    </Button>
                  )}
                  
                  {currentStep === 'error' && (
                    <Button
                      onClick={resetForm}
                      variant="outline"
                      className="flex-1"
                    >
                      Try Again
                    </Button>
                  )}
                  
                  {currentStep === 'complete' && (
                    <Button
                      onClick={() => router.push("/wardrobe")}
                      className="flex-1"
                    >
                      View Wardrobe
                    </Button>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Analysis Results */}
          {analysis && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  AI Analysis Results
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={analysis.type || ""}
                      onChange={(e) => {
                        const newType = e.target.value;
                        setAnalysis({ ...analysis, type: newType });
                      }}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="type">Type</Label>
                    <Select
                      value={analysis.type || ""}
                      onValueChange={(value) => setAnalysis({ ...analysis, type: value })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="shirt">Shirt</SelectItem>
                        <SelectItem value="pants">Pants</SelectItem>
                        <SelectItem value="dress">Dress</SelectItem>
                        <SelectItem value="skirt">Skirt</SelectItem>
                        <SelectItem value="jacket">Jacket</SelectItem>
                        <SelectItem value="sweater">Sweater</SelectItem>
                        <SelectItem value="shoes">Shoes</SelectItem>
                        <SelectItem value="belt">Belt</SelectItem>
                        <SelectItem value="accessory">Accessory</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="color">Primary Color</Label>
                    <Input
                      id="color"
                      value={analysis.dominantColors?.[0] || ""}
                      onChange={(e) => setAnalysis({ 
                        ...analysis, 
                        dominantColors: [e.target.value]
                      })}
                      className="mt-1"
                    />
                  </div>

                  <div>
                    <Label htmlFor="style">Style</Label>
                    <Input
                      id="style"
                      value={analysis.style?.join(", ") || ""}
                      onChange={(e) => setAnalysis({ 
                        ...analysis, 
                        style: e.target.value.split(", ").filter(Boolean)
                      })}
                      className="mt-1"
                      placeholder="e.g., casual, minimalist"
                    />
                  </div>

                  <div>
                    <Label htmlFor="season">Season</Label>
                    <Select
                      value={analysis.season || ""}
                      onValueChange={(value) => setAnalysis({ 
                        ...analysis, 
                        season: value 
                      })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select season" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="spring">Spring</SelectItem>
                        <SelectItem value="summer">Summer</SelectItem>
                        <SelectItem value="fall">Fall</SelectItem>
                        <SelectItem value="winter">Winter</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Textarea
                      id="notes"
                      className="mt-1"
                      placeholder="Add any notes about this item..."
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
} 