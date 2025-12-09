"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { safeSlice } from "@/lib/utils/arrayUtils";
import { 
  RefreshCw, 
  Heart, 
  Sparkles, 
  AlertCircle,
  CheckCircle,
  XCircle,
  Shirt
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useFirebase } from "@/lib/firebase-context";
import { useRouter } from "next/navigation";
import Carousel from "@/components/ui/carousel/Carousel";
import CarouselSlide from "@/components/ui/carousel/CarouselSlide";

interface ForgottenItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  color: string;
  style: string[];
  lastWorn?: number;
  daysSinceWorn: number;
  usageCount: number;
  favoriteScore: number;
  suggestedOutfits: string[];
  declutterReason?: string;
  rediscoveryPotential: number;
}

interface ForgottenGemsData {
  forgottenItems: ForgottenItem[];
  totalUnwornItems: number;
  potentialSavings: number;
  rediscoveryOpportunities: number;
  analysis_timestamp: string;
}

export default function ForgottenGems() {
  const [data, setData] = useState<ForgottenGemsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useFirebase();
  const router = useRouter();

  useEffect(() => {
    if (user) {
      fetchForgottenGems();
    }
  }, [user]);

  const fetchForgottenGems = async () => {
    try {
      if (!user) {
        setError("Authentication required");
        return;
      }

      setLoading(true);
      setError(null);
      
      const token = await user.getIdToken();
      if (!token) {
        setError("Authentication required");
        return;
      }

      const response = await fetch('/api/wardrobe/forgotten-gems', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setData(result.data);
    } catch (err) {
      console.error('Error fetching forgotten gems:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch forgotten gems');
    } finally {
      setLoading(false);
    }
  };

  const handleUseInOutfit = (item: ForgottenItem) => {
    // Navigate to outfit generation page with this item as the base item
    // Same pattern as wardrobe page: /outfits/generate?baseItemId=${item.id}
    router.push(`/outfits/generate?baseItemId=${item.id}`);
  };

  const formatDaysAgo = (days: number) => {
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
  };

  const highPotentialItems = data?.forgottenItems
    ? data.forgottenItems.filter((item) => item.rediscoveryPotential >= 70)
    : [];

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-6">
              <Skeleton className="h-48 w-full mb-4" />
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-1/2 mb-4" />
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <AlertCircle className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Error Loading Forgotten Gems</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <Button onClick={fetchForgottenGems} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!data || !data.forgottenItems || data.forgottenItems.length === 0) {
    return (
      <Card className="text-center py-12">
        <CardContent>
          <Sparkles className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Forgotten Gems Found</h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {data ? 
              "Great job! You're wearing all your clothes regularly." :
              "Backend data endpoints are still being configured. This is normal for new deployments."
            }
          </p>
          <Button onClick={fetchForgottenGems} variant="outline" className="border-2 border-[var(--copper-dark)] text-[var(--copper-dark)] dark:text-[var(--copper-light)] hover:bg-[var(--copper-dark)] hover:text-white dark:hover:bg-[var(--copper-light)] dark:hover:text-primary-foreground transition-all">
            <RefreshCw className="w-4 h-4 mr-2" />
            {data ? "Refresh Analysis" : "Check Again"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* High Potential Carousel */}
      {highPotentialItems.length > 0 && (
        <Card className="border border-[var(--copper-light)]/40 dark:border-[var(--copper-dark)]/60 bg-[var(--copper-light)]/10 dark:bg-[var(--copper-dark)]/10">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg text-[var(--copper-dark)] dark:text-[var(--copper-light)] flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  Forgotten Gems
                </CardTitle>
                <CardDescription className="text-[var(--copper-dark)]/80 dark:text-[var(--copper-light)]/70">
                  Highlighted pieces with the highest rediscovery potential
                </CardDescription>
              </div>
              <Badge variant="outline" className="text-xs text-[var(--copper-dark)] border-[var(--copper-light)]/60 dark:text-[var(--copper-light)] dark:border-[var(--copper-dark)]/60">
                {highPotentialItems.length} featured
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="pb-6">
            <Carousel
              className="w-full"
              slidesPerView={{
                base: 1,
                md: 1.5,
                lg: 2.5,
              }}
              spaceBetween={24}
              showControls
              showIndicators
              autoPlay
              autoPlayInterval={7000}
            >
              {highPotentialItems.map((item) => (
                <CarouselSlide key={item.id}>
                  <Card className="h-full max-w-sm mx-auto shadow-lg border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 bg-card dark:bg-card">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start mb-2">
                        <Badge variant="outline" className="text-xs">
                          {item.type}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{item.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {formatDaysAgo(item.daysSinceWorn)} • Worn {item.usageCount} times
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="relative aspect-[4/5] bg-gradient-to-br from-[#E8C8A0]/30 via-white to-white dark:from-[#B8860B]/20 dark:via-[#0D0D0D] dark:to-[#0D0D0D] rounded-xl overflow-hidden">
                        <img
                          src={item.imageUrl || '/placeholder.jpg'}
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-3 right-3">
                          <Badge variant="secondary" className="text-xs bg-card/80 dark:bg-card/70">
                            {item.color}
                          </Badge>
                        </div>
                      </div>
                      {item.style && safeSlice(item.style, 0, 4).length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {safeSlice(item.style, 0, 4).map((style, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {style}
                            </Badge>
                          ))}
                          {safeSlice(item.style, 0).length > 4 && (
                            <Badge variant="outline" className="text-xs">
                              +{safeSlice(item.style, 0).length - 4}
                            </Badge>
                          )}
                        </div>
                      )}
                      {item.suggestedOutfits && Array.isArray(item.suggestedOutfits) && item.suggestedOutfits.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs font-medium text-gray-700 dark:text-gray-300 uppercase tracking-wide">
                            Rediscovery ideas
                          </p>
                          <div className="space-y-1">
                            {item.suggestedOutfits.slice(0, 2).map((suggestion, index) => (
                              <p key={index} className="text-xs text-gray-600 dark:text-gray-400">
                                ✨ {suggestion}
                              </p>
                            ))}
                          </div>
                        </div>
                      )}
                        <Button
                        onClick={() => handleUseInOutfit(item)}
                        className="w-full bg-gradient-to-r from-[#D4A574] to-[#C9956F] hover:from-[#C9956F] hover:to-[#B8860B] text-white"
                          size="sm"
                        >
                        <Shirt className="w-4 h-4 mr-2" />
                        Use in outfit
                        </Button>
                    </CardContent>
                  </Card>
                </CarouselSlide>
              ))}
            </Carousel>
          </CardContent>
        </Card>
      )}

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Last analyzed: {new Date(data.analysis_timestamp).toLocaleString()}
      </div>
    </div>
  );
}
