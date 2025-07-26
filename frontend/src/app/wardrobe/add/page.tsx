"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { useWardrobe } from "@/hooks/useWardrobe";
import { uploadImage } from "@/lib/firebase/storageService";
import { analyzeClothingImage } from "@/lib/openai/analysis";
import { createClothingItemFromAnalysis } from "@/lib/utils/itemProcessing";
import { addWardrobeItem } from "@/lib/firebase/wardrobeService";
import type { ClothingItem } from "@/types/wardrobe";
import type { OpenAIClothingAnalysis } from '@/shared/types';
import type { ProcessImagesResult } from '@/shared/types';
import ProtectedRoute from "@/components/ProtectedRoute";
import ImageUpload from "@/components/ImageUpload";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";

export default function AddItemPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const isAuthenticated = !!user;
  const { processImages } = useWardrobe();
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<OpenAIClothingAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleImageSelect = (file: File) => {
    setImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleAnalyze = async () => {
    if (!image || !user) return;

    setLoading(true);
    setError(null);

    try {
      // First upload the image
      const uploadedImage = await uploadImage(image, user.uid);
      
      // Then analyze it
      const analysisResult = await analyzeClothingImage(uploadedImage.url);
      setAnalysis(analysisResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to analyze image");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Submit button clicked'); // Debug log

    if (authLoading) {
      toast.error('Please wait while we verify your authentication');
      return;
    }

    if (!isAuthenticated || !user) {
      toast.error('Please sign in to add items');
      return;
    }

    if (!image || !analysis) {
      toast.error('Please select an image and analyze it first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      console.log('Processing image...'); // Debug log
      
      // First upload the image
      const uploadResult = await uploadImage(image, user.uid);
      if (!uploadResult) {
        throw new Error('Failed to upload image');
      }

      // Create clothing item from analysis
      const newItem = createClothingItemFromAnalysis(analysis, user.uid, uploadResult.url);
      console.log('Created item:', newItem); // Debug log

      // Add the item to Firestore
      const result = await addWardrobeItem(newItem);
      console.log('Added item:', result); // Debug log

      toast.success("Item added successfully!");
      router.push("/wardrobe");
    } catch (err) {
      console.error('Error adding item:', err);
      setError(err instanceof Error ? err.message : "Failed to add item");
      toast.error(err instanceof Error ? err.message : "Failed to add item");
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (files: File[]) => {
    if (authLoading) {
      toast.error('Please wait while we verify your authentication');
      return;
    }

    if (!isAuthenticated || !user) {
      toast.error('Please sign in to upload images');
      return;
    }

    setUploading(true);
    setUploadProgress(0);

    try {
      const newItems = await processImages(files);
      
      if (!Array.isArray(newItems) || newItems.length === 0) {
        throw new Error("No items were added");
      }

      toast.success(`Successfully processed ${newItems.length} new item(s)`);
      router.push('/wardrobe');
    } catch (error) {
      console.error('Error uploading images:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to upload images');
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Add New Item</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <ImageUpload
              onImageSelect={handleImageSelect}
              preview={preview}
              loading={loading}
            />
          </div>

          <div>
            {analysis ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="name">Name</Label>
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
                  <Label htmlFor="color">Color</Label>
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
                  <Label htmlFor="season">Season</Label>
                  <Select
                    value={analysis.season?.[0] || ""}
                    onValueChange={(value) => setAnalysis({ ...analysis, season: [value as "spring" | "summer" | "fall" | "winter"] })}
                  >
                    <SelectTrigger id="season">
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
                    value={analysis.metadata?.itemMetadata?.careInstructions || ""}
                    onChange={(e) => setAnalysis({
                      ...analysis,
                      metadata: {
                        ...analysis.metadata,
                        itemMetadata: {
                          ...analysis.metadata?.itemMetadata,
                          careInstructions: e.target.value
                        }
                      }
                    })}
                  />
                </div>

                <div className="flex gap-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => router.push("/wardrobe")}
                  >
                    Cancel
                  </Button>
                  <Button 
                    type="submit" 
                    disabled={loading}
                  >
                    {loading ? "Adding..." : "Add Item"}
                  </Button>
                </div>
              </form>
            ) : (
              <div className="text-center">
                <Button
                  onClick={handleAnalyze}
                  disabled={!image || loading}
                  className="w-full"
                >
                  {loading ? "Analyzing..." : "Analyze Image"}
                </Button>
                {!image && (
                  <p className="mt-2 text-sm text-gray-500">
                    Please select an image first
                  </p>
                )}
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
            {error}
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
} 