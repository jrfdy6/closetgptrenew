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
  Calendar, 
  TrendingUp,
  AlertCircle,
  CheckCircle,
  XCircle
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { useFirebase } from "@/lib/firebase-context";
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
  const [processingItem, setProcessingItem] = useState<string | null>(null);
  const { toast } = useToast();
  const { user } = useFirebase();

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

  const handleItemAction = async (itemId: string, action: 'rediscover' | 'declutter') => {
    try {
      if (!user) {
        toast({
          title: "Authentication Error",
          description: "Please sign in again",
          variant: "destructive",
        });
        return;
      }

      setProcessingItem(itemId);
      
      const token = await user.getIdToken();
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please sign in again",
          variant: "destructive",
        });
        return;
      }

      const response = await fetch('/api/wardrobe/forgotten-gems', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: itemId, action }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      toast({
        title: action === 'rediscover' ? "Item Rediscovered!" : "Item Decluttered",
        description: result.message || `Successfully ${action}ed item`,
        variant: "default",
      });

      // Refresh the data
      fetchForgottenGems();
    } catch (err) {
      console.error(`Error ${action}ing item:`, err);
      toast({
        title: "Error",
        description: `Failed to ${action} item: ${err instanceof Error ? err.message : 'Unknown error'}`,
        variant: "destructive",
      });
    } finally {
      setProcessingItem(null);
    }
  };

  const formatDaysAgo = (days: number) => {
    if (days === 0) return "Today";
    if (days === 1) return "Yesterday";
    if (days < 7) return `${days} days ago`;
    if (days < 30) return `${Math.floor(days / 7)} weeks ago`;
    if (days < 365) return `${Math.floor(days / 30)} months ago`;
    return `${Math.floor(days / 365)} years ago`;
  };

  const getRediscoveryColor = (potential: number) => {
    if (potential >= 80) return "text-emerald-600 bg-emerald-100 dark:bg-emerald-900/20";
    if (potential >= 60) return "text-blue-600 bg-blue-100 dark:bg-blue-900/20";
    if (potential >= 40) return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20";
    return "text-gray-600 bg-gray-100 dark:bg-gray-900/20";
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
          <Button onClick={fetchForgottenGems} variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            {data ? "Refresh Analysis" : "Check Again"}
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Stats */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Forgotten Gems</h2>
          <p className="text-gray-600 dark:text-gray-400">
            Rediscover {data.rediscoveryOpportunities} items with high potential
          </p>
        </div>
        <Button onClick={fetchForgottenGems} variant="outline">
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh Analysis
        </Button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Unworn</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.totalUnwornItems}</div>
            <p className="text-xs text-muted-foreground">Items not worn recently</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rediscovery Potential</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{data.rediscoveryOpportunities}</div>
            <p className="text-xs text-muted-foreground">High-potential items</p>
          </CardContent>
        </Card>
      </div>

      {/* High Potential Carousel */}
      {highPotentialItems.length > 0 && (
        <Card className="border border-amber-200 dark:border-amber-800/60 bg-amber-50/60 dark:bg-amber-900/10">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-lg text-amber-700 dark:text-amber-300 flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  Premium Rediscovery Spotlight
                </CardTitle>
                <CardDescription className="text-amber-700/80 dark:text-amber-200/70">
                  Highlighted pieces with the highest rediscovery potential
                </CardDescription>
              </div>
              <Badge variant="outline" className="text-xs text-amber-700 border-amber-300 dark:text-amber-200 dark:border-amber-700">
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
                  <Card className="h-full shadow-lg border border-amber-200/80 dark:border-amber-800/60 bg-white dark:bg-stone-950">
                    <CardHeader className="pb-3">
                      <div className="flex justify-between items-start mb-2">
                        <Badge variant="outline" className="text-xs">
                          {item.type}
                        </Badge>
                        <Badge className={`text-xs ${getRediscoveryColor(item.rediscoveryPotential)}`}>
                          {item.rediscoveryPotential}% potential
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{item.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {formatDaysAgo(item.daysSinceWorn)} • Worn {item.usageCount} times
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="relative aspect-[4/5] bg-gradient-to-br from-amber-100 via-white to-white dark:from-amber-900/30 dark:via-stone-950 dark:to-stone-950 rounded-xl overflow-hidden">
                        <img
                          src={item.imageUrl || '/placeholder.jpg'}
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-3 right-3">
                          <Badge variant="secondary" className="text-xs bg-white/80 dark:bg-stone-900/70">
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
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleItemAction(item.id, 'rediscover')}
                          disabled={processingItem === item.id}
                          className="flex-1 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white"
                          size="sm"
                        >
                          {processingItem === item.id ? (
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <CheckCircle className="w-4 h-4 mr-2" />
                          )}
                          Rediscover
                        </Button>
                        <Button
                          onClick={() => handleItemAction(item.id, 'declutter')}
                          disabled={processingItem === item.id}
                          variant="outline"
                          size="sm"
                          className="flex-1 border-amber-200 hover:bg-amber-50 dark:border-amber-800/60"
                        >
                          {processingItem === item.id ? (
                            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          ) : (
                            <XCircle className="w-4 h-4 mr-2" />
                          )}
                          Declutter
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </CarouselSlide>
              ))}
            </Carousel>
          </CardContent>
        </Card>
      )}

      {/* Forgotten Items Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.forgottenItems.map((item) => (
          <Card key={item.id} className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start mb-2">
                <Badge variant="outline" className="text-xs">
                  {item.type}
                </Badge>
                <Badge className={`text-xs ${getRediscoveryColor(item.rediscoveryPotential)}`}>
                  {item.rediscoveryPotential}% potential
                </Badge>
              </div>
              <CardTitle className="text-lg">{item.name}</CardTitle>
              <CardDescription className="text-sm">
                {formatDaysAgo(item.daysSinceWorn)} • Worn {item.usageCount} times
              </CardDescription>
            </CardHeader>
            
            <CardContent className="space-y-4">
              {/* Item Image */}
              <div className="relative aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
                <img
                  src={item.imageUrl || '/placeholder.jpg'}
                  alt={item.name}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-2 right-2">
                  <Badge variant="secondary" className="text-xs">
                    {item.color}
                  </Badge>
                </div>
              </div>

              {/* Style Tags */}
              {item.style && safeSlice(item.style, 0, 3).length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {safeSlice(item.style, 0, 3).map((style, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {style}
                    </Badge>
                  ))}
                  {safeSlice(item.style, 0).length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{safeSlice(item.style, 0).length - 3}
                    </Badge>
                  )}
                </div>
              )}

              {/* Suggested Outfits */}
              {item.suggestedOutfits && Array.isArray(item.suggestedOutfits) && item.suggestedOutfits.length > 0 && (
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300">
                    Try these combinations:
                  </p>
                  <div className="space-y-1">
                    {item.suggestedOutfits.slice(0, 2).map((suggestion, index) => (
                      <p key={index} className="text-xs text-gray-600 dark:text-gray-400">
                        💡 {suggestion}
                      </p>
                    ))}
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-2">
                <Button
                  onClick={() => handleItemAction(item.id, 'rediscover')}
                  disabled={processingItem === item.id}
                  className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                  size="sm"
                >
                  {processingItem === item.id ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <CheckCircle className="w-4 h-4 mr-2" />
                  )}
                  Rediscover
                </Button>
                
                <Button
                  onClick={() => handleItemAction(item.id, 'declutter')}
                  disabled={processingItem === item.id}
                  variant="outline"
                  size="sm"
                  className="flex-1"
                >
                  {processingItem === item.id ? (
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  ) : (
                    <XCircle className="w-4 h-4 mr-2" />
                  )}
                  Declutter
                </Button>
              </div>

              {/* Declutter Reason */}
              {item.declutterReason && (
                <div className="text-xs text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-900/20 p-2 rounded">
                  <AlertCircle className="w-3 h-3 inline mr-1" />
                  {item.declutterReason}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Last Updated */}
      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Last analyzed: {new Date(data.analysis_timestamp).toLocaleString()}
      </div>
    </div>
  );
}
