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
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full border border-border/60 dark:border-border/60 bg-card/85 dark:bg-card/85">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gradient-to-br from-primary/30 to-accent/30 dark:from-primary/20 dark:to-accent/20 flex items-center justify-center">
              <CheckCircle className="h-12 w-12 text-accent dark:text-primary" />
            </div>
            <CardTitle className="text-3xl bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">🎉 Wardrobe Ready!</CardTitle>
            <CardDescription className="text-lg mt-4 text-muted-foreground">
              You've added {uploadedCount} items. Now let's create your first amazing outfit!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gradient-to-r from-primary/10 to-accent/10 dark:from-primary/20 dark:to-accent/20 rounded-lg p-6 text-center border border-border/60 dark:border-border/60">
              <Sparkles className="h-8 w-8 mx-auto mb-3 text-accent dark:text-primary" />
              <p className="text-muted-foreground font-medium">
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
      <div className="min-h-screen bg-background p-4">
        <div className="max-w-6xl mx-auto">
          <Card className="mb-6 border border-border/60 dark:border-border/60 bg-card/85 dark:bg-card/85">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-card-foreground">Build Your Digital Wardrobe</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    {getEncouragementMessage()}
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="text-lg px-4 py-2 bg-primary/20 dark:bg-accent/20 text-accent dark:text-primary">
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
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="max-w-4xl w-full border border-border/60 dark:border-border/60 bg-card/85 dark:bg-card/85">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 h-20 w-20 rounded-full bg-gradient-to-br from-[#FFB84C]/30 to-[#FF9400]/30 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 flex items-center justify-center">
            <Camera className="h-10 w-10 text-accent dark:text-primary" />
          </div>
          <CardTitle className="text-3xl md:text-4xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">Let's Build Your Digital Wardrobe!</CardTitle>
          <CardDescription className="text-lg mt-4 text-muted-foreground">
            We need {targetCount} items to start creating amazing outfits for you.
          </CardDescription>
          <div className="mt-2 text-sm text-muted-foreground">
            ⏱️ This takes about 5 minutes
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Photo Best Practices */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Camera className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              📸 Best Practices for Quality Photos
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>Use hangers</strong> - Hang items on a door or clothing rack
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>Good lighting</strong> - Natural light works best, avoid shadows
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>Flat, not folded</strong> - Lay items flat or hang them fully extended
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>Plain background</strong> - White wall or door preferred
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>Full item visible</strong> - Capture the entire garment in frame
                </span>
              </div>
              <div className="flex items-start gap-2">
                <CheckCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="text-gray-700 dark:text-gray-300">
                  <strong>No blurry photos</strong> - Hold steady for clear, sharp shots
                </span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-blue-200 dark:border-blue-800">
              <p className="text-xs text-blue-700 dark:text-blue-300 italic flex items-center gap-1">
                <Sparkles className="w-4 h-4" />
                Better photos = more accurate AI analysis & recommendations!
              </p>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center space-y-4">
            <Button
              size="lg"
              className="bg-gradient-to-r from-primary to-accent hover:from-primary hover:to-accent/90 text-primary-foreground font-semibold px-8 py-6 text-lg shadow-lg shadow-amber-500/25"
              onClick={() => setShowUpload(true)}
            >
              <Camera className="h-6 w-6 mr-2" />
              Start Adding Items
              <ArrowRight className="h-6 w-6 ml-2" />
            </Button>
            <p className="text-sm text-muted-foreground">
              You can always add more items later
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

