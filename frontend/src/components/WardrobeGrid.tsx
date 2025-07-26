"use client";

import { useState } from "react";
import Image from "next/image";
import { ClothingItem } from "@/shared/types";
import { WardrobeItem } from "@/types/wardrobe";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HoverCard, InteractiveButton, hapticFeedback } from "@/components/ui/micro-interactions";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  Heart, 
  Share2, 
  MoreHorizontal, 
  Image as ImageIcon,
  AlertCircle,
  RefreshCw 
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useToast } from "@/components/ui/use-toast";
import { getFirebaseIdToken } from "@/lib/utils/auth";

interface WardrobeGridProps {
  items: (ClothingItem | WardrobeItem)[];
  loading?: boolean;
  error?: string | null;
  onItemClick?: (item: ClothingItem | WardrobeItem) => void;
  onGenerateOutfit?: (item: ClothingItem | WardrobeItem) => void;
  onDeleteItem?: (item: ClothingItem | WardrobeItem) => void;
  onEditItem?: (item: ClothingItem | WardrobeItem) => void;
  showActions?: boolean;
}

// Skeleton component for loading state
const WardrobeItemSkeleton = () => (
  <Card className="overflow-hidden min-h-[320px]">
    <div className="relative aspect-square min-h-[220px]">
      <Skeleton className="w-full h-full" />
    </div>
    <CardContent className="p-4">
      <Skeleton className="h-5 w-3/4 mb-3" />
      <Skeleton className="h-4 w-1/2 mb-2" />
      <Skeleton className="h-4 w-2/3" />
    </CardContent>
  </Card>
);

// Empty state component
const EmptyState = ({ message }: { message: string }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
      <ImageIcon className="w-8 h-8 text-muted-foreground" />
    </div>
    <h3 className="text-lg font-semibold mb-2">No items found</h3>
    <p className="text-muted-foreground mb-4 max-w-sm">{message}</p>
    <Button variant="outline" size="sm">
      Add your first item
    </Button>
  </div>
);

// Error state component
const ErrorState = ({ error, onRetry }: { error: string; onRetry?: () => void }) => (
  <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
    <div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center mb-4">
      <AlertCircle className="w-8 h-8 text-destructive" />
    </div>
    <h3 className="text-lg font-semibold mb-2">Something went wrong</h3>
    <p className="text-muted-foreground mb-4 max-w-sm">{error}</p>
    {onRetry && (
      <Button onClick={onRetry} variant="outline" size="sm">
        <RefreshCw className="w-4 h-4 mr-2" />
        Try again
      </Button>
    )}
  </div>
);

export default function WardrobeGrid({
  items,
  loading = false,
  error = null,
  onItemClick,
  onGenerateOutfit,
  onDeleteItem,
  onEditItem,
  showActions = true
}: WardrobeGridProps) {
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [favoriteStates, setFavoriteStates] = useState<Record<string, boolean>>({});
  const [togglingFavorites, setTogglingFavorites] = useState<Record<string, boolean>>({});
  const { toast } = useToast();

  // Initialize favorite states from items
  useState(() => {
    const initialFavorites: Record<string, boolean> = {};
    items.forEach(item => {
      initialFavorites[item.id] = item.favorite || false;
    });
    setFavoriteStates(initialFavorites);
  });

  const handleImageError = (itemId: string) => {
    setImageErrors(prev => ({ ...prev, [itemId]: true }));
  };

  const handleImageLoad = (itemId: string) => {
    setImageErrors(prev => ({ ...prev, [itemId]: false }));
  };

  const handleToggleFavorite = async (item: ClothingItem | WardrobeItem, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (togglingFavorites[item.id]) return; // Prevent multiple clicks
    
    setTogglingFavorites(prev => ({ ...prev, [item.id]: true }));
    
    try {
      const token = await getFirebaseIdToken();
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please log in to favorite items.",
          variant: "destructive",
        });
        return;
      }

      const response = await fetch('/api/item-analytics/favorites/toggle', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ item_id: item.id }),
      });

      if (!response.ok) {
        throw new Error('Failed to toggle favorite');
      }

      const data = await response.json();
      
      // Update local state
      setFavoriteStates(prev => ({ 
        ...prev, 
        [item.id]: data.is_favorite 
      }));

      toast({
        title: data.is_favorite ? "Added to favorites" : "Removed from favorites",
        description: data.message,
      });

    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast({
        title: "Error",
        description: "Failed to update favorite status. Please try again.",
        variant: "destructive",
      });
    } finally {
      setTogglingFavorites(prev => ({ ...prev, [item.id]: false }));
    }
  };

  const handleMarkAsWorn = async (item: ClothingItem | WardrobeItem, e: React.MouseEvent) => {
    e.stopPropagation();
    
    try {
      // Use test token for development
      const token = 'test';

      const response = await fetch('/api/wardrobe/increment-wear', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ itemId: item.id }),
      });

      if (!response.ok) {
        throw new Error('Failed to mark as worn');
      }

      const data = await response.json();
      
      toast({
        title: "Marked as Worn",
        description: `Wear count updated to ${data.data.newWearCount}`,
      });

      // Trigger a refresh of the wardrobe data instead of reloading the page
      // This will be handled by the parent component
      if (typeof window !== 'undefined') {
        // Dispatch a custom event to notify parent components
        window.dispatchEvent(new CustomEvent('wardrobeDataChanged'));
      }

    } catch (error) {
      console.error('Error marking as worn:', error);
      toast({
        title: "Error",
        description: "Failed to mark item as worn. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
        {Array.from({ length: 12 }).map((_, index) => (
          <WardrobeItemSkeleton key={index} />
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    return <ErrorState error={error} />;
  }

  // Empty state
  if (!items || items.length === 0) {
    return (
      <EmptyState 
        message="Your wardrobe is empty. Start by adding some clothing items to see them here." 
      />
    );
  }

  // Debug: Log first few items to see wear count data
  console.log('WardrobeGrid items sample:', items.slice(0, 3).map(item => ({
    id: item.id,
    name: item.name,
    wearCount: item.wearCount,
    hasWearCount: 'wearCount' in item,
    type: typeof item.wearCount,
    allKeys: Object.keys(item)
  })));

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
      {items.map((item) => (
        <HoverCard key={item.id} intensity={3}>
          <Card 
            className="group overflow-hidden hover:shadow-lg transition-all duration-200 cursor-pointer border-2 border-gray-200 hover:border-gray-300 dark:border-gray-700 dark:hover:border-gray-600 min-h-[320px]"
            onClick={() => onItemClick?.(item)}
          >
          <div className="relative aspect-square min-h-[220px] bg-gray-50 dark:bg-gray-800">
            {imageErrors[item.id] || !item.imageUrl || item.imageUrl === "" ? (
              // Fallback for failed images or missing imageUrl
              <div className="w-full h-full bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center">
                <div className="text-center p-4">
                  <ImageIcon className="w-12 h-12 text-gray-400 dark:text-gray-500 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">No Image</p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">{item.type || 'Clothing'}</p>
                </div>
              </div>
            ) : (
              <Image
                src={item.imageUrl}
                alt={item.name || "Clothing item"}
                fill
                className="object-cover transition-transform duration-200 group-hover:scale-105"
                onError={() => handleImageError(item.id)}
                onLoad={() => handleImageLoad(item.id)}
                sizes="(max-width: 640px) 100vw, (max-width: 768px) 50vw, (max-width: 1024px) 33vw, (max-width: 1280px) 25vw, (max-width: 1536px) 20vw, 14vw"
                unoptimized={item.imageUrl.includes('example.com')}
              />
            )}
            
            {/* Overlay with actions */}
            {showActions && (
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors duration-200">
                <div className="absolute top-2 right-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button 
                        variant="secondary" 
                        size="sm" 
                        className="h-8 w-8 p-0 bg-gray-800/80 hover:bg-gray-800 text-white shadow-md"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      {onGenerateOutfit && (
                        <DropdownMenuItem onClick={(e) => {
                          e.stopPropagation();
                          onGenerateOutfit(item);
                        }}>
                          Generate outfit
                        </DropdownMenuItem>
                      )}
                      {onEditItem && (
                        <DropdownMenuItem onClick={(e) => {
                          e.stopPropagation();
                          onEditItem(item);
                        }}>
                          Edit item
                        </DropdownMenuItem>
                      )}
                      {onDeleteItem && (
                        <DropdownMenuItem 
                          onClick={(e) => {
                            e.stopPropagation();
                            onDeleteItem(item);
                          }}
                          className="text-destructive"
                        >
                          Delete item
                        </DropdownMenuItem>
                      )}
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
                
                {/* Quick action buttons */}
                <div className="absolute bottom-2 left-2">
                  <div className="flex gap-1">
                    <InteractiveButton
                      variant="outline"
                      size="sm"
                      className={`h-7 w-7 p-0 bg-gray-800/80 hover:bg-gray-800 text-white shadow-md transition-all duration-200 flex items-center justify-center ${
                        favoriteStates[item.id] ? 'bg-red-500 hover:bg-red-600' : ''
                      }`}
                      onClick={() => {
                        hapticFeedback.success();
                        handleToggleFavorite(item, {} as React.MouseEvent);
                      }}
                      disabled={togglingFavorites[item.id]}
                      hapticType="success"
                    >
                      <Heart className={`h-3 w-3 ${favoriteStates[item.id] ? 'fill-current' : ''}`} />
                    </InteractiveButton>
                    <InteractiveButton
                      variant="outline"
                      size="sm"
                      className="h-7 w-7 p-0 bg-green-600/80 hover:bg-green-600 text-white shadow-md flex items-center justify-center"
                      onClick={() => {
                        hapticFeedback.success();
                        handleMarkAsWorn(item, {} as React.MouseEvent);
                      }}
                      hapticType="success"
                    >
                      <span className="text-xs font-bold">W</span>
                    </InteractiveButton>
                  </div>
                </div>
              </div>
            )}
          </div>
          
          <CardContent className="p-3">
            <div className="space-y-2">
              <h3 className="font-medium text-sm text-foreground min-h-[1.25rem] leading-tight">
                {item.name || "Untitled Item"}
              </h3>
              
              {/* Single badge for type or color - whichever is more useful */}
              <div className="flex items-center justify-between">
                {(item.type || item.color) && (
                  <Badge variant="secondary" className="text-xs">
                    {item.type || item.color}
                  </Badge>
                )}
                
                {/* Wear count indicator - subtle dot instead of badge */}
                {item.wearCount !== undefined && item.wearCount > 0 && (
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <span className="text-xs text-muted-foreground">{item.wearCount}</span>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
        </HoverCard>
      ))}
    </div>
  );
} 