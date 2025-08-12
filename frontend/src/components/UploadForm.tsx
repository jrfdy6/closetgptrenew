"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { 
  Upload, 
  X, 
  Camera, 
  Image as ImageIcon,
  Loader2,
  CheckCircle,
  AlertCircle
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

interface UploadFormProps {
  onUploadComplete?: (item: any) => void;
  onCancel?: () => void;
}

export default function UploadForm({ onUploadComplete, onCancel }: UploadFormProps) {
  const { toast } = useToast();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  // Form fields
  const [itemName, setItemName] = useState("");
  const [itemType, setItemType] = useState("");
  const [itemColor, setItemColor] = useState("");
  const [itemDescription, setItemDescription] = useState("");
  const [selectedSeasons, setSelectedSeasons] = useState<string[]>([]);
  const [selectedOccasions, setSelectedOccasions] = useState<string[]>([]);
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setUploadedFile(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  });

  const removeFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setUploadedFile(null);
    setPreviewUrl("");
  };

  const handleSeasonToggle = (season: string) => {
    setSelectedSeasons(prev => 
      prev.includes(season) 
        ? prev.filter(s => s !== season)
        : [...prev, season]
    );
  };

  const handleOccasionToggle = (occasion: string) => {
    setSelectedOccasions(prev => 
      prev.includes(occasion) 
        ? prev.filter(o => o !== occasion)
        : [...prev, occasion]
    );
  };

  const handleStyleToggle = (style: string) => {
    setSelectedStyles(prev => 
      prev.includes(style) 
        ? prev.filter(s => s !== style)
        : [...prev, style]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!uploadedFile) {
      toast({
        title: "No file selected",
        description: "Please select an image to upload",
        variant: "destructive",
      });
      return;
    }

    if (!itemName.trim() || !itemType || !itemColor) {
      toast({
        title: "Missing information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      // Create FormData for file upload
      const formData = new FormData();
      formData.append('image', uploadedFile);
      formData.append('name', itemName);
      formData.append('type', itemType);
      formData.append('color', itemColor);
      formData.append('description', itemDescription);
      formData.append('seasons', JSON.stringify(selectedSeasons));
      formData.append('occasions', JSON.stringify(selectedOccasions));
      formData.append('styles', JSON.stringify(selectedStyles));

      // Simulate API call - replace with actual upload endpoint
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Mock successful response
      const mockItem = {
        id: Date.now().toString(),
        name: itemName,
        type: itemType,
        color: itemColor,
        description: itemDescription,
        seasons: selectedSeasons,
        occasions: selectedOccasions,
        styles: selectedStyles,
        imageUrl: previewUrl,
        wearCount: 0,
        favorite: false,
        createdAt: new Date().toISOString()
      };

      setUploadSuccess(true);
      toast({
        title: "Upload successful!",
        description: `${itemName} has been added to your wardrobe`,
      });

      // Call callback if provided
      if (onUploadComplete) {
        onUploadComplete(mockItem);
      }

      // Reset form after a delay
      setTimeout(() => {
        resetForm();
      }, 2000);

    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload failed",
        description: "There was an error uploading your item. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const resetForm = () => {
    setItemName("");
    setItemType("");
    setItemColor("");
    setItemDescription("");
    setSelectedSeasons([]);
    setSelectedOccasions([]);
    setSelectedStyles([]);
    removeFile();
    setUploadSuccess(false);
  };

  const handleCancel = () => {
    resetForm();
    if (onCancel) {
      onCancel();
    }
  };

  if (uploadSuccess) {
    return (
      <div className="text-center py-8">
        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
          Item uploaded successfully!
        </h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Your item has been added to your wardrobe
        </p>
        <Button onClick={resetForm} variant="outline">
          Add Another Item
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* File Upload Area */}
      <div>
        <Label htmlFor="image-upload" className="text-sm font-medium">
          Clothing Image *
        </Label>
        <div className="mt-2">
          {!uploadedFile ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? "border-emerald-500 bg-emerald-50 dark:bg-emerald-950/20"
                  : "border-gray-300 dark:border-gray-600 hover:border-emerald-400 dark:hover:border-emerald-500"
              }`}
            >
              <input {...getInputProps()} />
              <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {isDragActive
                  ? "Drop the image here..."
                  : "Drag & drop an image, or click to select"}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                Supports JPG, PNG, GIF, WebP (max 10MB)
              </p>
            </div>
          ) : (
            <div className="relative">
              <div className="w-full h-48 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                <img
                  src={previewUrl}
                  alt="Preview"
                  className="w-full h-full object-cover"
                />
              </div>
              <Button
                type="button"
                variant="destructive"
                size="sm"
                className="absolute top-2 right-2"
                onClick={removeFile}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Basic Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Label htmlFor="item-name" className="text-sm font-medium">
            Item Name *
          </Label>
          <Input
            id="item-name"
            value={itemName}
            onChange={(e) => setItemName(e.target.value)}
            placeholder="e.g., Blue Denim Jacket"
            className="mt-1"
            required
          />
        </div>

        <div>
          <Label htmlFor="item-type" className="text-sm font-medium">
            Item Type *
          </Label>
          <Select value={itemType} onValueChange={setItemType} required>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="shirt">👕 Shirt</SelectItem>
              <SelectItem value="pants">👖 Pants</SelectItem>
              <SelectItem value="jacket">🧥 Jacket</SelectItem>
              <SelectItem value="dress">👗 Dress</SelectItem>
              <SelectItem value="shoes">👟 Shoes</SelectItem>
              <SelectItem value="accessory">💍 Accessory</SelectItem>
              <SelectItem value="outerwear">🧥 Outerwear</SelectItem>
              <SelectItem value="underwear">🩲 Underwear</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="item-color" className="text-sm font-medium">
            Color *
          </Label>
          <Select value={itemColor} onValueChange={setItemColor} required>
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select color" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="black">⚫ Black</SelectItem>
              <SelectItem value="white">⚪ White</SelectItem>
              <SelectItem value="blue">🔵 Blue</SelectItem>
              <SelectItem value="red">🔴 Red</SelectItem>
              <SelectItem value="green">🟢 Green</SelectItem>
              <SelectItem value="yellow">🟡 Yellow</SelectItem>
              <SelectItem value="purple">🟣 Purple</SelectItem>
              <SelectItem value="pink">🩷 Pink</SelectItem>
              <SelectItem value="brown">🟤 Brown</SelectItem>
              <SelectItem value="gray">⚪ Gray</SelectItem>
              <SelectItem value="multi">🌈 Multi-color</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="item-description" className="text-sm font-medium">
            Description
          </Label>
          <Textarea
            id="item-description"
            value={itemDescription}
            onChange={(e) => setItemDescription(e.target.value)}
            placeholder="Describe your item..."
            className="mt-1"
            rows={3}
          />
        </div>
      </div>

      {/* Seasons */}
      <div>
        <Label className="text-sm font-medium">Seasons</Label>
        <div className="mt-2 flex flex-wrap gap-2">
          {['spring', 'summer', 'fall', 'winter'].map((season) => (
            <div key={season} className="flex items-center space-x-2">
              <Checkbox
                id={`season-${season}`}
                checked={selectedSeasons.includes(season)}
                onCheckedChange={() => handleSeasonToggle(season)}
              />
              <Label htmlFor={`season-${season}`} className="text-sm">
                {season.charAt(0).toUpperCase() + season.slice(1)}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Occasions */}
      <div>
        <Label className="text-sm font-medium">Occasions</Label>
        <div className="mt-2 flex flex-wrap gap-2">
          {['casual', 'work', 'formal', 'party', 'date', 'sport', 'daily'].map((occasion) => (
            <div key={occasion} className="flex items-center space-x-2">
              <Checkbox
                id={`occasion-${occasion}`}
                checked={selectedOccasions.includes(occasion)}
                onCheckedChange={() => handleOccasionToggle(occasion)}
              />
              <Label htmlFor={`occasion-${occasion}`} className="text-sm">
                {occasion.charAt(0).toUpperCase() + occasion.slice(1)}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Styles */}
      <div>
        <Label className="text-sm font-medium">Styles</Label>
        <div className="mt-2 flex flex-wrap gap-2">
          {['casual', 'formal', 'streetwear', 'vintage', 'minimalist', 'bohemian', 'classic', 'trendy', 'artistic', 'sporty'].map((style) => (
            <div key={style} className="flex items-center space-x-2">
              <Checkbox
                id={`style-${style}`}
                checked={selectedStyles.includes(style)}
                onCheckedChange={() => handleStyleToggle(style)}
              />
              <Label htmlFor={`style-${style}`} className="text-sm">
                {style.charAt(0).toUpperCase() + style.slice(1)}
              </Label>
            </div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={isUploading}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          disabled={!uploadedFile || isUploading}
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
              Add to Wardrobe
            </>
          )}
        </Button>
      </div>
    </form>
  );
} 