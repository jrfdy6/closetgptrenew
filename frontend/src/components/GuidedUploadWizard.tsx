"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Upload, 
  CheckCircle, 
  Sparkles,
  TrendingUp,
  ShoppingBag,
  Shirt,
  ArrowRight,
  Camera
} from "lucide-react";
import BatchImageUpload from "./BatchImageUpload";

interface GuidedUploadWizardProps {
  userId: string;
  targetCount?: number;
  onComplete: (itemCount: number) => void;
  stylePersona?: string;
  gender?: string;
}

interface CategorySuggestion {
  category: string;
  count: number;
  icon: any;
  description: string;
  examples: string[];
}

const PERSONA_SUGGESTIONS: Record<string, CategorySuggestion[]> = {
  architect: [
    { category: "Tops", count: 2, icon: Shirt, description: "Neutral basics", examples: ["White T-shirt", "Gray sweater"] },
    { category: "Bottoms", count: 1, icon: ShoppingBag, description: "Classic fits", examples: ["Dark jeans", "Chinos"] },
    { category: "Outerwear", count: 1, icon: Upload, description: "Structured pieces", examples: ["Blazer", "Jacket"] },
    { category: "Shoes", count: 1, icon: TrendingUp, description: "Versatile footwear", examples: ["White sneakers", "Leather shoes"] },
  ],
  innovator: [
    { category: "Tops", count: 2, icon: Shirt, description: "Statement pieces", examples: ["Bold graphic tee", "Unique shirt"] },
    { category: "Bottoms", count: 1, icon: ShoppingBag, description: "Creative fits", examples: ["Colored pants", "Unique cut jeans"] },
    { category: "Outerwear", count: 1, icon: Upload, description: "Standout pieces", examples: ["Statement jacket", "Unique coat"] },
    { category: "Accessories", count: 1, icon: Sparkles, description: "Bold accessories", examples: ["Hat", "Unique bag"] },
  ],
  default: [
    { category: "Tops", count: 2, icon: Shirt, description: "Your favorite tops", examples: ["T-shirts", "Shirts", "Sweaters"] },
    { category: "Bottoms", count: 1, icon: ShoppingBag, description: "Go-to bottoms", examples: ["Jeans", "Pants", "Skirts"] },
    { category: "Outerwear", count: 1, icon: Upload, description: "Jackets & coats", examples: ["Jacket", "Coat", "Cardigan"] },
    { category: "Shoes", count: 1, icon: TrendingUp, description: "Everyday shoes", examples: ["Sneakers", "Boots", "Flats"] },
  ],
};

export default function GuidedUploadWizard({
  userId,
  targetCount = 5,
  onComplete,
  stylePersona = "default",
  gender = "Male"
}: GuidedUploadWizardProps) {
  const [uploadedCount, setUploadedCount] = useState(0);
  const [showUpload, setShowUpload] = useState(false);
  const [isComplete, setIsComplete] = useState(false);

  const suggestions = PERSONA_SUGGESTIONS[stylePersona] || PERSONA_SUGGESTIONS.default;
  const progressPercentage = (uploadedCount / targetCount) * 100;

  const handleUploadComplete = (items: any[]) => {
    const newCount = uploadedCount + items.length;
    setUploadedCount(newCount);

    if (newCount >= targetCount) {
      setIsComplete(true);
      setTimeout(() => {
        onComplete(newCount);
      }, 2000);
    }
  };

  const getEncouragementMessage = () => {
    if (uploadedCount === 0) {
      return "Let's get started! Add your first item.";
    } else if (uploadedCount < targetCount / 2) {
      return `Great start! Keep going.`;
    } else if (uploadedCount < targetCount) {
      return `Almost there! Just ${targetCount - uploadedCount} more.`;
    } else {
      return "🎉 Amazing! Your wardrobe is ready!";
    }
  };

  if (isComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
              <CheckCircle className="h-12 w-12 text-green-600 dark:text-green-400" />
            </div>
            <CardTitle className="text-3xl">🎉 Wardrobe Ready!</CardTitle>
            <CardDescription className="text-lg mt-4">
              You've added {uploadedCount} items. Now let's create your first amazing outfit!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-6 text-center">
              <Sparkles className="h-8 w-8 mx-auto mb-3 text-purple-600 dark:text-purple-400" />
              <p className="text-gray-700 dark:text-gray-300 font-medium">
                Our AI is now ready to generate personalized outfits just for you!
              </p>
            </div>
            <div className="text-center text-sm text-gray-500 dark:text-gray-400">
              <p>Redirecting to outfit generator...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (showUpload) {
    return (
      <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510] p-4">
        <div className="max-w-6xl mx-auto">
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Build Your Digital Wardrobe</CardTitle>
                  <CardDescription>
                    {getEncouragementMessage()}
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="text-lg px-4 py-2">
                  {uploadedCount} / {targetCount}
                </Badge>
              </div>
              <Progress value={progressPercentage} className="mt-4" />
            </CardHeader>
          </Card>

          <BatchImageUpload
            userId={userId}
            onUploadComplete={handleUploadComplete}
            onError={(message) => console.error(message)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 dark:from-blue-900/20 dark:via-purple-900/20 dark:to-pink-900/20 flex items-center justify-center p-4">
      <Card className="max-w-4xl w-full">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
            <Camera className="h-10 w-10 text-white" />
          </div>
          <CardTitle className="text-3xl md:text-4xl">Let's Build Your Digital Wardrobe!</CardTitle>
          <CardDescription className="text-lg mt-4">
            We need {targetCount} items to start creating amazing outfits for you.
          </CardDescription>
          <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            ⏱️ This takes about 5 minutes
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Value Props */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/30 dark:to-blue-800/30 rounded-lg p-4 text-center">
              <Sparkles className="h-8 w-8 mx-auto mb-2 text-blue-600 dark:text-blue-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">AI-Powered Analysis</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Automatic categorization & style detection
              </p>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/30 dark:to-purple-800/30 rounded-lg p-4 text-center">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 text-purple-600 dark:text-purple-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Smart Suggestions</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Get outfit ideas instantly
              </p>
            </div>
            <div className="bg-gradient-to-br from-pink-50 to-pink-100 dark:from-pink-900/30 dark:to-pink-800/30 rounded-lg p-4 text-center">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-pink-600 dark:text-pink-400" />
              <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Quick & Easy</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Background removal included
              </p>
            </div>
          </div>

          {/* Personalized Suggestions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 border-2 border-purple-200 dark:border-purple-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Sparkles className="h-5 w-5 mr-2 text-purple-600 dark:text-purple-400" />
              Recommended Items for You
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Based on your style profile, we recommend starting with:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {suggestions.map((suggestion, index) => {
                const Icon = suggestion.icon;
                return (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                    <div className="flex-shrink-0">
                      <Icon className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-semibold text-gray-900 dark:text-white">
                          {suggestion.category}
                        </p>
                        <Badge variant="secondary">{suggestion.count}</Badge>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400 mb-1">
                        {suggestion.description}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-500">
                        e.g., {suggestion.examples.join(", ")}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center space-y-4">
            <Button
              size="lg"
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white font-semibold px-8 py-6 text-lg"
              onClick={() => setShowUpload(true)}
            >
              <Camera className="h-6 w-6 mr-2" />
              Start Adding Items
              <ArrowRight className="h-6 w-6 ml-2" />
            </Button>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              You can always add more items later
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

