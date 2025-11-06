"use client";
// Force deploy - stealth mode background removal Nov 6 2025

import { useState } from "react";
import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Heart, Sparkles, MoreVertical, Eye, Trash2 } from "lucide-react";
import { safeSlice } from "@/lib/utils/arrayUtils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface WardrobeItem {
  id: string;
  name: string;
  type: string;
  color: string;
  imageUrl: string;
  backgroundRemovedUrl?: string;  // Stealth-mode: auto-upgraded by worker
  thumbnailUrl?: string;  // Fast preview thumbnail
  processing_status?: string;  // "pending" | "processing" | "done" | "failed"
  wearCount: number;
  favorite: boolean;
  style?: string[];
  season?: string[];
  occasion?: string[];
  lastWorn?: Date;
}

interface WardrobeGridProps {
  items: WardrobeItem[];
  loading: boolean;
  onItemClick: (item: WardrobeItem) => void;
  onGenerateOutfit: (item: WardrobeItem) => void;
  onToggleFavorite?: (itemId: string) => void;
  onDeleteItem?: (itemId: string) => void;
  showActions?: boolean;
}

export default function WardrobeGrid({ 
  items, 
  loading, 
  onItemClick, 
  onGenerateOutfit, 
  onToggleFavorite,
  onDeleteItem,
  showActions = true 
}: WardrobeGridProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<string | null>(null);

  // Filter out items with broken image URLs (truncated base64 or broken placeholder)
  const validItems = items.filter(item => {
    if (!item.imageUrl) return false;
    // Check for truncated base64 URLs
    if (item.imageUrl.startsWith('data:image/') && item.imageUrl.length < 100) {
      return false;
    }
    // Check for broken placeholder URLs
    if (item.imageUrl.includes('via.placeholder.com')) {
      return false;
    }
    return true;
  });

  // Debug logging for component props (disabled to reduce noise)
  // console.log(`🔍 [WardrobeGrid] Component rendered with:`, {
  //   itemsCount: items.length,
  //   loading,
  //   showActions,
  //   hasOnDeleteItem: !!onDeleteItem,
  //   hasOnToggleFavorite: !!onToggleFavorite
  // });

  const handleDeleteClick = (itemId: string) => {
    setItemToDelete(itemId);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (itemToDelete && onDeleteItem) {
      try {
        await onDeleteItem(itemToDelete);
      } catch (error) {
        console.error(`❌ [WardrobeGrid] Delete operation failed for item ${itemToDelete}:`, error);
        // Keep dialog open on error so user can try again
        return;
      }
    }
    setDeleteDialogOpen(false);
    setItemToDelete(null);
  };

  const getColorBadge = (color: string) => {
    const colorMap: Record<string, string> = {
      'black': 'bg-gray-900 text-white',
      'white': 'bg-gray-100 text-gray-900 border border-gray-300',
      'blue': 'bg-orange-500 text-white',
      'red': 'bg-red-500 text-white',
      'green': 'bg-amber-500 text-white',
      'yellow': 'bg-yellow-500 text-white',
      'purple': 'bg-amber-600 text-white',
      'pink': 'bg-orange-500 text-white',
      'brown': 'bg-amber-700 text-white',
      'gray': 'bg-gray-500 text-white'
    };
    
    return colorMap[color] || 'bg-gray-200 text-gray-700';
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'jacket': return '🧥';
      case 'shirt': return '👕';
      case 'pants': return '👖';
      case 'dress': return '👗';
      case 'shoes': return '👟';
      case 'accessory': return '💍';
      default: return '👕';
    }
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {Array.from({ length: 10 }).map((_, index) => (
          <Card key={index} className="animate-pulse">
            <div className="aspect-square bg-gray-200 dark:bg-gray-700 rounded-t-lg" />
            <CardContent className="p-4">
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
          <Eye className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No items found</h3>
        <p className="text-gray-600 dark:text-gray-400">
          Try adjusting your filters or add some new items to your wardrobe
        </p>
      </div>
    );
  }

  const filteredCount = items.length - validItems.length;

  return (
    <div>
      {filteredCount > 0 && (
        <div className="mb-4 p-3 bg-yellow-50 dark:bg-yellow-950/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            ⚠️ {filteredCount} item{filteredCount > 1 ? 's' : ''} with broken images hidden from display
          </p>
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        {validItems.map((item) => (
        <Card
          key={item.id}
          className="group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
          onClick={() => onItemClick(item)}
        >
          {/* Image Container */}
          <div className="relative aspect-square overflow-hidden rounded-t-lg">
            <div className="relative w-full h-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <Image
                src={item.thumbnailUrl || item.backgroundRemovedUrl || item.imageUrl}
                alt={item.name || "Wardrobe item"}
                fill
                sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, 20vw"
                className="object-cover transition-all duration-300 group-hover:scale-105"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.jpg';
                }}
              />
            </div>
            
            {/* Favorite indicator */}
            {item.favorite && (
              <div className="absolute top-2 right-2 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center z-20">
                <Heart className="w-4 h-4 text-white fill-current" />
              </div>
            )}
          </div>

          {/* Card Content */}
          <CardContent className="p-3">
            <div className="space-y-2">
              {/* Name and Type */}
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white text-sm line-clamp-1 group-hover:text-emerald-600 transition-colors">
                  {item.name}
                </h3>
                <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mt-1">
                  <span>{getTypeIcon(item.type)}</span>
                  <span className="capitalize">{item.type}</span>
                </div>
              </div>

              {/* Color and Style */}
              <div className="flex items-center justify-between">
                <Badge className={`text-xs ${getColorBadge(item.color)}`}>
                  {item.color}
                </Badge>
                
                {item.style && safeSlice(item.style, 0, 2).length > 0 && (
                  <div className="flex gap-1">
                    {safeSlice(item.style, 0, 2).map((style, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {style}
                      </Badge>
                    ))}
                    {safeSlice(item.style, 0).length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{safeSlice(item.style, 0).length - 2}
                      </Badge>
                    )}
                  </div>
                )}
              </div>

              {/* Season and Occasion */}
              {(item.season || item.occasion) && (
                <div className="flex flex-wrap gap-1">
                  {safeSlice(item.season, 0, 2).map((season, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {season}
                    </Badge>
                  ))}
                  {safeSlice(item.occasion, 0, 1).map((occasion, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {occasion}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
      </div>
      
      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Wardrobe Item</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{items.find(item => item.id === itemToDelete)?.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeleteDialogOpen(false)}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
} 