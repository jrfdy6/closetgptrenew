"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { Upload, X, ArrowLeft, Save, Image as ImageIcon } from "lucide-react";
import { useWardrobe } from "@/hooks/useWardrobe";
import type { ClothingItem } from "@/types/wardrobe";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/components/ui/use-toast";
import { Container } from "@/components/ui/typography";

// Constants
const CLOTHING_TYPES = [
  "shirt",
  "pants",
  "dress",
  "jacket",
  "shoes",
  "accessory",
] as const;

const SEASONS = ["spring", "summer", "fall", "winter"] as const;

const COLORS = [
  "Black",
  "White",
  "Gray",
  "Red",
  "Blue",
  "Green",
  "Yellow",
  "Purple",
  "Pink",
  "Brown",
  "Beige",
  "Orange",
];

export default function EditItemPage() {
  const router = useRouter();
  const params = useParams();
  const { wardrobe, loading, error: wardrobeError, updateItem } = useWardrobe();
  const itemId = params?.id as string;
  const [image, setImage] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [name, setName] = useState("");
  const [type, setType] = useState<ClothingItem['type']>(CLOTHING_TYPES[0]);
  const [color, setColor] = useState(COLORS[0]);
  const [selectedSeasons, setSelectedSeasons] = useState<ClothingItem['season']>([]);
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!loading && wardrobe.length > 0 && itemId) {
      const item = wardrobe.find(item => item.id === itemId);
      if (!item) {
        router.push("/wardrobe");
        return;
      }

      setName(item.name || "");
      setType(item.type || CLOTHING_TYPES[0]);
      setColor(item.color || COLORS[0]);
      setSelectedSeasons(item.season || []);
      setTags(item.tags || []);
      setPreview(item.imageUrl || "");
      setIsLoading(false);
    }
  }, [loading, wardrobe, itemId, router]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSeasonToggle = (season: ClothingItem['season'][0]) => {
    setSelectedSeasons((prev) =>
      prev.includes(season)
        ? prev.filter((s) => s !== season)
        : [...prev, season]
    );
  };

  const handleAddTag = () => {
    if (newTag && !tags.includes(newTag)) {
      setTags([...tags, newTag]);
      setNewTag("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((tag) => tag !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setIsSubmitting(true);
      setError(null);

      // TODO: Upload image to storage and get URL if changed
      const imageUrl = preview; // Replace with actual upload if image changed

      const updates: Partial<ClothingItem> = {
        name,
        type,
        color,
        season: selectedSeasons,
        imageUrl,
        tags,
      };

      await updateItem(itemId, updates);
      router.push("/wardrobe");
    } catch (err) {
      setError("Failed to update item");
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const { toast } = useToast();

  if (isLoading) {
    return (
      <Container maxWidth="full" padding="lg">
        <div className="space-y-6">
          <div className="flex items-center gap-4">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-8 w-24" />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Skeleton className="h-64 w-full" />
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-20 w-full" />
            </div>
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container maxWidth="full" padding="lg">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => router.back()}
              className="shadow-sm"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-foreground">Edit Item</h1>
              <p className="text-muted-foreground">Update your wardrobe item details</p>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Image Upload */}
            <Card className="card-enhanced">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ImageIcon className="w-5 h-5" />
                  Item Image
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="relative">
                    <label htmlFor="image" className="cursor-pointer">
                      {preview ? (
                        <div className="relative aspect-square rounded-lg overflow-hidden border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors">
                          <img
                            src={preview}
                            alt="Preview"
                            className="w-full h-full object-cover"
                          />
                          <div className="absolute inset-0 bg-black/0 hover:bg-black/20 transition-colors flex items-center justify-center">
                            <Upload className="w-8 h-8 text-white opacity-0 hover:opacity-100 transition-opacity" />
                          </div>
                        </div>
                      ) : (
                        <div className="aspect-square rounded-lg border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors flex flex-col items-center justify-center bg-gray-50">
                          <Upload className="w-12 h-12 text-gray-400 mb-2" />
                          <p className="text-sm text-gray-600 font-medium">Click to upload an image</p>
                          <p className="text-xs text-gray-500 mt-1">JPG, PNG, or WebP</p>
                        </div>
                      )}
                      <input
                        id="image"
                        type="file"
                        accept="image/*"
                        onChange={handleImageChange}
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Basic Info */}
            <div className="space-y-6">
              <Card className="card-enhanced">
                <CardHeader>
                  <CardTitle>Basic Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Enter item name"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="type">Type</Label>
                      <Select value={type} onValueChange={(value) => setType(value as ClothingItem['type'])}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          {CLOTHING_TYPES.map((t) => (
                            <SelectItem key={t} value={t}>
                              {t.charAt(0).toUpperCase() + t.slice(1)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="color">Color</Label>
                      <Select value={color} onValueChange={setColor}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select color" />
                        </SelectTrigger>
                        <SelectContent>
                          {COLORS.map((c) => (
                            <SelectItem key={c} value={c}>
                              {c}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Seasons */}
              <Card className="card-enhanced">
                <CardHeader>
                  <CardTitle>Seasons</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {SEASONS.map((season) => (
                      <Button
                        key={season}
                        type="button"
                        variant={selectedSeasons.includes(season) ? "default" : "outline"}
                        size="sm"
                        onClick={() => handleSeasonToggle(season)}
                        className="capitalize"
                      >
                        {season}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Tags */}
              <Card className="card-enhanced">
                <CardHeader>
                  <CardTitle>Tags</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-2">
                    <Input
                      type="text"
                      value={newTag}
                      onChange={(e) => setNewTag(e.target.value)}
                      placeholder="Add a tag"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddTag())}
                    />
                    <Button type="button" onClick={handleAddTag} variant="outline" size="sm">
                      Add
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {tags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="gap-1">
                        {tag}
                        <button
                          type="button"
                          onClick={() => handleRemoveTag(tag)}
                          className="ml-1 hover:text-destructive"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <Card className="card-enhanced border-destructive">
              <CardContent className="pt-6">
                <p className="text-destructive text-sm">{error}</p>
              </CardContent>
            </Card>
          )}

          {/* Submit Button */}
          <div className="flex justify-end gap-4">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="shadow-sm"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </div>
    </Container>
  );
} 