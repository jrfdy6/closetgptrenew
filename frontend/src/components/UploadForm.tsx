"use client";

import { useState } from "react";
import { useStorage } from "@/lib/hooks/useStorage";
import { useFirebase } from "@/lib/firebase-context";
import { uploadImage } from "@/lib/firebase/storageService";
import { analyzeClothingImage } from "@/lib/services/clothingImageAnalysis";
import { createClothingItemFromAnalysis } from "@/lib/utils/itemProcessing";
import { addWardrobeItem } from "@/lib/firebase/wardrobeService";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Upload, Sparkles, Loader2, CheckCircle, AlertCircle } from "lucide-react";
import type { OpenAIClothingAnalysis } from '@/shared/types';

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [analysis, setAnalysis] = useState<OpenAIClothingAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useFirebase();
  const router = useRouter();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
      setAnalysis(null); // Reset analysis when new file is selected
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file || !user) {
      toast.error('Please select an image and ensure you are signed in');
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      // First upload the image
      const uploadedImage = await uploadImage(file, user.uid);
      
      // Then analyze it
      const analysisResult = await analyzeClothingImage(uploadedImage.url);
      setAnalysis(analysisResult);
      toast.success('Image analyzed successfully!');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to analyze image";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!user) {
      toast.error('Please sign in to add items');
      return;
    }

    if (!file || !analysis) {
      toast.error('Please select an image and analyze it first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Upload the image
      const uploadResult = await uploadImage(file, user.uid);
      if (!uploadResult) {
        throw new Error('Failed to upload image');
      }

      // Create clothing item from analysis
      const newItem = createClothingItemFromAnalysis(analysis, user.uid, uploadResult.url);

      // Add the item to Firestore
      const result = await addWardrobeItem(newItem);
      
      if (result.success) {
        toast.success("Item added successfully!");
        router.push("/wardrobe");
      } else {
        throw new Error(result.error || 'Failed to add item');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to add item";
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* File Upload Section */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="text-center">
            <Label htmlFor="photo" className="text-lg font-semibold">
              Upload Clothing Item
            </Label>
            <p className="text-sm text-muted-foreground mt-1">
              Upload a photo of your clothing item for AI analysis
            </p>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <label htmlFor="photo" className="cursor-pointer block">
              {preview ? (
                <div className="text-center">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-w-xs mx-auto rounded-lg shadow-md"
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    Click to change image
                  </p>
                </div>
              ) : (
                <div className="text-center">
                  <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-lg font-medium">
                    <span className="text-blue-600">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    PNG, JPG or JPEG (MAX. 10MB)
                  </p>
                </div>
              )}
              <input
                id="photo"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          {file && !analysis && (
            <div className="text-center">
              <Button
                onClick={handleAnalyze}
                disabled={analyzing}
                className="w-full max-w-xs"
              >
                {analyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Analyze with AI
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
      </Card>

      {/* Analysis Results Section */}
      {analysis && (
        <Card className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h3 className="text-lg font-semibold">Analysis Complete</h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <Label htmlFor="name">Item Name</Label>
                <Input
                  id="name"
                  value={analysis.name || analysis.type || ""}
                  onChange={(e) => {
                    const newName = e.target.value;
                    setAnalysis({ ...analysis, name: newName });
                  }}
                  required
                />
              </div>

              <div>
                <Label htmlFor="type">Type</Label>
                <Select
                  value={analysis.type || ""}
                  onValueChange={(value) => setAnalysis({ ...analysis, type: value })}
                >
                  <SelectTrigger id="type">
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
                  value={analysis.dominantColors?.[0]?.name || ""}
                  onChange={(e) => setAnalysis({ 
                    ...analysis, 
                    dominantColors: [{ 
                      name: e.target.value,
                      hex: analysis.dominantColors?.[0]?.hex || "#000000",
                      rgb: analysis.dominantColors?.[0]?.rgb || [0, 0, 0]
                    }]
                  })}
                  required
                />
              </div>

              <div>
                <Label htmlFor="style">Style</Label>
                <Textarea
                  id="style"
                  value={analysis.style?.join(", ") || ""}
                  onChange={(e) => setAnalysis({ 
                    ...analysis, 
                    style: e.target.value.split(", ").filter(s => s.trim())
                  })}
                  placeholder="e.g., casual, formal, vintage"
                />
              </div>

              <div>
                <Label htmlFor="occasion">Occasion</Label>
                <Textarea
                  id="occasion"
                  value={analysis.occasion?.join(", ") || ""}
                  onChange={(e) => setAnalysis({ 
                    ...analysis, 
                    occasion: e.target.value.split(", ").filter(s => s.trim())
                  })}
                  placeholder="e.g., work, casual, formal"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setFile(null);
                    setPreview("");
                    setAnalysis(null);
                  }}
                >
                  Start Over
                </Button>
                <Button 
                  type="submit" 
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Adding to Wardrobe...
                    </>
                  ) : (
                    "Add to Wardrobe"
                  )}
                </Button>
              </div>
            </form>
          </div>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <p className="text-red-700">{error}</p>
          </div>
        </Card>
      )}
    </div>
  );
} 