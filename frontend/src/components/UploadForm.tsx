"use client";

import { useState, useCallback, useEffect } from "react";
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
  AlertCircle,
  Sparkles,
  Brain
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { processImageForAnalysis } from "@/lib/services/clothingImageAnalysis";
import { useFirebase } from "@/lib/firebase-context";

interface UploadFormProps {
  onUploadComplete?: (item: any) => void;
  onCancel?: () => void;
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

// Helper function to upload image to Firebase Storage
const uploadImageToFirebaseStorage = async (file: File, userId: string, user: any): Promise<string> => {
  // Create FormData for the upload
  const formData = new FormData();
  formData.append('file', file);
  formData.append('userId', userId);
  formData.append('category', 'clothing');
  formData.append('name', file.name || 'uploaded-item');

  // Upload to Firebase Storage via our simple API route
  const response = await fetch('/api/image/upload-simple', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Upload failed');
  }

  const result = await response.json();
  return result.image_url;
};

export default function UploadForm({ onUploadComplete, onCancel }: UploadFormProps) {
  const { toast } = useToast();
  const { user } = useFirebase();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  
  // AI Analysis states
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [autoPopulated, setAutoPopulated] = useState(false);
  
  // Form fields
  const [itemName, setItemName] = useState("");
  const [itemType, setItemType] = useState("");
  const [itemColor, setItemColor] = useState("");
  const [itemDescription, setItemDescription] = useState("");
  const [selectedSeasons, setSelectedSeasons] = useState<string[]>([]);
  const [selectedOccasions, setSelectedOccasions] = useState<string[]>([]);
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);

  const analyzeImage = async (file: File) => {
    console.log('🚀 analyzeImage called with file:', file.name, file.size);
    setIsAnalyzing(true);
    setAnalysisError(null);
    
    try {
      console.log('🤖 Starting AI analysis for:', file.name);
      const analysis = await processImageForAnalysis(file);
      console.log('✅ AI analysis completed:', analysis);
      
      setAnalysisResult(analysis);
      
      // Auto-populate form fields
      populateFormFromAnalysis(analysis);
      
      toast({
        title: "AI Analysis Complete! ✨",
        description: "Form has been auto-populated with detected clothing details",
      });
      
    } catch (error) {
      console.error('❌ AI analysis failed:', error);
      setAnalysisError(error instanceof Error ? error.message : 'Analysis failed');
      
      toast({
        title: "AI Analysis Failed",
        description: "Could not analyze the image. You can still fill the form manually.",
        variant: "destructive",
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    console.log('📁 onDrop called with files:', acceptedFiles.length);
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      console.log('📄 Processing file:', file.name, file.size, file.type);
      setUploadedFile(file);
      
      // Create preview URL
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      
      // Reset analysis state
      setAnalysisResult(null);
      setAnalysisError(null);
      setAutoPopulated(false);
      
      // Start AI analysis
      console.log('🔄 Starting AI analysis...');
      await analyzeImage(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDropAccepted: (files) => {
      console.log('✅ Dropzone accepted files:', files.length);
    },
    onDropRejected: (fileRejections) => {
      console.log('❌ Dropzone rejected files:', fileRejections);
    },
    onError: (error) => {
      console.error('❌ Dropzone error:', error);
    }
  });

  const removeFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setUploadedFile(null);
    setPreviewUrl("");
    setAnalysisResult(null);
    setAnalysisError(null);
    setAutoPopulated(false);
  };

  const populateFormFromAnalysis = (analysis: any) => {
    try {
      // Populate basic fields
      if (analysis.name) {
        setItemName(analysis.name);
      }
      
      if (analysis.type) {
        setItemType(analysis.type);
      }
      
      if (analysis.subType && !analysis.name) {
        setItemName(analysis.subType);
      }
      
      // Populate colors (use first dominant color)
      if (analysis.dominantColors && analysis.dominantColors.length > 0) {
        const firstColor = analysis.dominantColors[0];
        if (firstColor.name) {
          setItemColor(firstColor.name.toLowerCase());
        }
      }
      
      // Populate seasons
      if (analysis.season && Array.isArray(analysis.season)) {
        setSelectedSeasons(analysis.season);
      }
      
      // Populate occasions
      if (analysis.occasion && Array.isArray(analysis.occasion)) {
        setSelectedOccasions(analysis.occasion);
      }
      
      // Populate styles
      if (analysis.style && Array.isArray(analysis.style)) {
        setSelectedStyles(analysis.style);
      }
      
      // Create description from analysis
      const descriptionParts = [];
      if (analysis.material) descriptionParts.push(`Material: ${analysis.material}`);
      if (analysis.pattern) descriptionParts.push(`Pattern: ${analysis.pattern}`);
      if (analysis.brand) descriptionParts.push(`Brand: ${analysis.brand}`);
      
      if (descriptionParts.length > 0) {
        setItemDescription(descriptionParts.join(', '));
      }
      
      setAutoPopulated(true);
      
    } catch (error) {
      console.error('Error populating form from analysis:', error);
    }
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
    
    if (!uploadedFile || !user) {
      toast({
        title: "Missing requirements",
        description: "Please select an image and ensure you're logged in",
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
      // Create FormData for the AI-powered upload
      const formData = new FormData();
      formData.append('file', uploadedFile);
      formData.append('userId', user.uid);

      console.log('🚀 Uploading with AI analysis to backend directly');
      
      // Call backend directly for AI analysis
      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-backend-production.up.railway.app';
      const payload = { image: { url: await compressImageForAnalysis(uploadedFile) } };
      
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
      console.log('✅ Analysis successful:', result);

      if (result.analysis) {
        // Create a proper clothing item from the analysis result
        const clothingItem = {
          id: `item-${Date.now()}`,
          name: result.analysis.name || result.analysis.clothing_type || itemName || 'Analyzed Item',
          type: result.analysis.type || result.analysis.clothing_type || itemType || 'unknown',
          color: result.analysis.color || result.analysis.primary_color || itemColor || 'unknown',
          imageUrl: await uploadImageToFirebaseStorage(uploadedFile, user.uid, user), // Upload to Firebase Storage
          userId: user.uid,
          createdAt: new Date().toISOString(),
          analysis: result.analysis,
          style: result.analysis.style || [],
          occasion: result.analysis.occasion || [],
          season: result.analysis.season || ['all'],
          material: result.analysis.material || 'unknown',
          brand: result.analysis.brand || 'unknown',
          size: result.analysis.size || 'unknown',
          condition: result.analysis.condition || 'good',
          price: result.analysis.price || null,
          purchaseDate: result.analysis.purchaseDate || null,
          tags: result.analysis.tags || [],
          notes: result.analysis.notes || '',
          favorite: false,
          wearCount: 0,
          lastWorn: null
        };

        console.log('💾 Saving item to database...');
        console.log('🔍 DEBUG: Clothing item being saved:', clothingItem);

        // Save to database via the wardrobe API
        const saveResponse = await fetch('/api/wardrobe', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${await user.getIdToken()}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(clothingItem),
        });

        if (!saveResponse.ok) {
          const errorData = await saveResponse.json();
          throw new Error(errorData.error || 'Failed to save item to database');
        }

        const saveResult = await saveResponse.json();
        console.log('✅ Item saved to database:', saveResult);
        
        setUploadSuccess(true);
        toast({
          title: "Item saved successfully! ✨",
          description: `${clothingItem.name} has been analyzed and saved to your wardrobe`,
        });

        // Call callback if provided
        if (onUploadComplete) {
          onUploadComplete(clothingItem);
        }

        // Reset form after a delay
        setTimeout(() => {
          resetForm();
        }, 2000);
      } else {
        throw new Error('No analysis result from server');
      }

    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : "There was an error uploading your item. Please try again.",
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
    setAnalysisResult(null);
    setAnalysisError(null);
    setAutoPopulated(false);
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
        <div className="mb-2 p-2 bg-green-50 dark:bg-green-950/20 rounded-lg">
          <p className="text-xs text-green-700 dark:text-green-300">
            <strong>Edit mode:</strong> Review and edit AI-detected details before saving to your wardrobe.
          </p>
          <button 
            type="button" 
            onClick={() => console.log('🧪 Test button clicked - component is working!')}
            className="mt-1 text-xs text-blue-600 hover:text-blue-800 underline"
          >
            🧪 Test: Click to verify component is working
          </button>
        </div>
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

      {/* AI Analysis Status */}
      {uploadedFile && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-500" />
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                AI Analysis Status
              </span>
            </div>
            {!isAnalyzing && !analysisResult && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => uploadedFile && analyzeImage(uploadedFile)}
                className="text-xs"
              >
                <Brain className="w-3 h-3 mr-1" />
                Analyze Now
              </Button>
            )}
          </div>
          
          {isAnalyzing && (
            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span className="text-sm">Analyzing clothing item with AI...</span>
            </div>
          )}
          
          {analysisError && (
            <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">Analysis failed: {analysisError}</span>
            </div>
          )}
          
          {analysisResult && autoPopulated && (
            <div className="flex items-center gap-2 text-green-600 dark:text-green-400">
              <CheckCircle className="w-4 h-4" />
              <span className="text-sm">Form auto-populated with AI analysis ✨</span>
            </div>
          )}
          
          {analysisResult && autoPopulated && (
            <div className="mt-2 p-2 bg-green-50 dark:bg-green-950/20 rounded-lg border border-green-200 dark:border-green-800">
              <p className="text-xs text-green-700 dark:text-green-300">
                <strong>Ready to edit:</strong> Review the AI-detected details below and make any changes before saving to your wardrobe.
              </p>
            </div>
          )}
          
          {analysisResult && (
            <div className="mt-2 text-xs text-gray-600 dark:text-gray-400">
              <p>Detected: {analysisResult.type} {analysisResult.subType && `(${analysisResult.subType})`}</p>
              {analysisResult.dominantColors && analysisResult.dominantColors.length > 0 && (
                <p>Colors: {analysisResult.dominantColors.map((c: any) => c.name).join(', ')}</p>
              )}
              {analysisResult.style && analysisResult.style.length > 0 && (
                <p>Styles: {analysisResult.style.join(', ')}</p>
              )}
            </div>
          )}
        </div>
      )}

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
          disabled={!uploadedFile || isUploading || isAnalyzing}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
        >
          {isUploading ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Uploading with AI...
            </>
          ) : isAnalyzing ? (
            <>
              <Brain className="w-4 h-4 mr-2 animate-pulse" />
              Analyzing...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4 mr-2" />
              {analysisResult ? 'Save to Wardrobe' : 'Add to Wardrobe with AI'}
            </>
          )}
        </Button>
      </div>
    </form>
  );
} 