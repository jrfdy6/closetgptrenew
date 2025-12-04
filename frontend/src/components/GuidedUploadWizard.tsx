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

  const handleUploadComplete = async (items: any[]) => {
    const newCount = uploadedCount + items.length;
    setUploadedCount(newCount);

    if (newCount >= targetCount) {
      setIsComplete(true);
      
      // Trigger Cold Start Quest check for badge unlocks
      try {
        // Get Firebase user for auth token
        const { auth } = await import('@/lib/firebase/config');
        const { getAuth } = await import('firebase/auth');
        const firebaseAuth = getAuth(auth);
        const currentUser = firebaseAuth.currentUser;
        
        if (currentUser) {
          const token = await currentUser.getIdToken();
          
          // Call the cold-start-check endpoint to unlock badges
          const response = await fetch('/api/gamification/cold-start-check', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (response.ok) {
            const result = await response.json();
            console.log('✅ Cold Start Quest checked:', result);
            
            if (result.milestone_reached) {
              console.log('🏆 Badge unlocked!', result.data);
            }
          }
        }
      } catch (error) {
        console.warn('⚠️ Could not check Cold Start Quest:', error);
      }
      
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
      <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510] flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60 bg-white/85 dark:bg-[#2C2119]/85">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gradient-to-br from-[#FFB84C]/30 to-[#FF9400]/30 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 flex items-center justify-center">
              <CheckCircle className="h-12 w-12 text-[#FF9400] dark:text-[#FFB84C]" />
            </div>
            <CardTitle className="text-3xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">🎉 Wardrobe Ready!</CardTitle>
            <CardDescription className="text-lg mt-4 text-[#57534E] dark:text-[#C4BCB4]">
              You've added {uploadedCount} items. Now let's create your first amazing outfit!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gradient-to-r from-[#FFB84C]/10 to-[#FF9400]/10 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 rounded-lg p-6 text-center border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
              <Sparkles className="h-8 w-8 mx-auto mb-3 text-[#FF9400] dark:text-[#FFB84C]" />
              <p className="text-[#57534E] dark:text-[#C4BCB4] font-medium">
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
          <Card className="mb-6 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60 bg-white/85 dark:bg-[#2C2119]/85">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-[#1C1917] dark:text-[#F8F5F1]">Build Your Digital Wardrobe</CardTitle>
                  <CardDescription className="text-[#57534E] dark:text-[#C4BCB4]">
                    {getEncouragementMessage()}
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="text-lg px-4 py-2 bg-[#FFB84C]/20 dark:bg-[#FF9400]/20 text-[#FF9400] dark:text-[#FFB84C]">
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
            quickMode={false}
            requireStaging={true}
            requiredCount={targetCount}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510] flex items-center justify-center p-4">
      <Card className="max-w-4xl w-full border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60 bg-white/85 dark:bg-[#2C2119]/85">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gradient-to-br from-[#FFB84C]/30 to-[#FF9400]/30 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 flex items-center justify-center">
            <Camera className="h-10 w-10 text-[#FF9400] dark:text-[#FFB84C]" />
          </div>
          <CardTitle className="text-3xl md:text-4xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">Let's Build Your Digital Wardrobe!</CardTitle>
          <CardDescription className="text-lg mt-4 text-[#57534E] dark:text-[#C4BCB4]">
            We need {targetCount} items to start creating amazing outfits for you.
          </CardDescription>
          <div className="mt-2 text-sm text-[#57534E] dark:text-[#C4BCB4]">
            ⏱️ This takes about 5 minutes
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Value Props */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gradient-to-br from-[#FFCC66]/35 to-[#FF9400]/35 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 rounded-lg p-4 text-center border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
              <Sparkles className="h-8 w-8 mx-auto mb-2 text-[#FF9400] dark:text-[#FFB84C]" />
              <h3 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-1">AI-Powered Analysis</h3>
              <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                Automatic categorization & style detection
              </p>
            </div>
            <div className="bg-gradient-to-br from-[#FFB84C]/30 to-[#FF9400]/30 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 rounded-lg p-4 text-center border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
              <TrendingUp className="h-8 w-8 mx-auto mb-2 text-[#FF9400] dark:text-[#FFB84C]" />
              <h3 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-1">Smart Suggestions</h3>
              <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                Get outfit ideas instantly
              </p>
            </div>
            <div className="bg-gradient-to-br from-[#FFE08F]/40 to-[#FFB84C]/35 dark:from-[#FFD27F]/25 dark:to-[#FFB84C]/20 rounded-lg p-4 text-center border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-[#FF9400] dark:text-[#FFB84C]" />
              <h3 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-1">Quick & Easy</h3>
              <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                Background removal included
              </p>
            </div>
          </div>

          {/* Personalized Suggestions */}
          <div className="bg-white/85 dark:bg-[#2C2119]/85 rounded-lg p-6 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
            <h3 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-4 flex items-center">
              <Sparkles className="h-5 w-5 mr-2 text-[#FF9400] dark:text-[#FFB84C]" />
              Recommended Items for You
            </h3>
            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-4">
              Based on your style profile, we recommend starting with:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {suggestions.map((suggestion, index) => {
                const Icon = suggestion.icon;
                return (
                  <div key={index} className="flex items-start space-x-3 p-3 bg-[#F5F0E8]/30 dark:bg-[#3D2F24]/30 rounded-lg border border-[#F5F0E8]/60 dark:border-[#3D2F24]/60">
                    <div className="flex-shrink-0">
                      <Icon className="h-6 w-6 text-[#FF9400] dark:text-[#FFB84C]" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
                          {suggestion.category}
                        </p>
                        <Badge variant="secondary" className="bg-[#FFB84C]/20 dark:bg-[#FF9400]/20 text-[#FF9400] dark:text-[#FFB84C]">{suggestion.count}</Badge>
                      </div>
                      <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mb-1">
                        {suggestion.description}
                      </p>
                      <p className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
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
              className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] hover:from-[#FFB84C] hover:to-[#FF7700] text-[#1A1510] dark:text-white font-semibold px-8 py-6 text-lg shadow-lg shadow-amber-500/25"
              onClick={() => setShowUpload(true)}
            >
              <Camera className="h-6 w-6 mr-2" />
              Start Adding Items
              <ArrowRight className="h-6 w-6 ml-2" />
            </Button>
            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
              You can always add more items later
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

