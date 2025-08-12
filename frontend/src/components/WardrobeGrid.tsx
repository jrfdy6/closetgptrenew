"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Heart, Sparkles, MoreVertical, Eye } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface WardrobeItem {
  id: string;
  name: string;
  type: string;
  color: string;
  imageUrl: string;
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
  showActions?: boolean;
}

export default function WardrobeGrid({ 
  items, 
  loading, 
  onItemClick, 
  onGenerateOutfit, 
  showActions = true 
}: WardrobeGridProps) {
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  const getColorBadge = (color: string) => {
    const colorMap: Record<string, string> = {
      'black': 'bg-gray-900 text-white',
      'white': 'bg-gray-100 text-gray-900 border border-gray-300',
      'blue': 'bg-blue-500 text-white',
      'red': 'bg-red-500 text-white',
      'green': 'bg-green-500 text-white',
      'yellow': 'bg-yellow-500 text-white',
      'purple': 'bg-purple-500 text-white',
      'pink': 'bg-pink-500 text-white',
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

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      {items.map((item) => (
        <Card
          key={item.id}
          className={`group cursor-pointer transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${
            hoveredItem === item.id ? 'ring-2 ring-emerald-500 ring-offset-2' : ''
          }`}
          onMouseEnter={() => setHoveredItem(item.id)}
          onMouseLeave={() => setHoveredItem(null)}
          onClick={() => onItemClick(item)}
        >
          {/* Image Container */}
          <div className="relative aspect-square overflow-hidden rounded-t-lg">
            <div className="w-full h-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
              <img
                src={item.imageUrl}
                alt={item.name}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.jpg';
                }}
              />
            </div>
            
            {/* Overlay with actions */}
            {showActions && (
              <div className={`absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center gap-2`}>
                <Button
                  size="sm"
                  variant="secondary"
                  className="bg-white/90 text-gray-900 hover:bg-white"
                  onClick={(e) => {
                    e.stopPropagation();
                    onGenerateOutfit(item);
                  }}
                >
                  <Sparkles className="w-4 h-4 mr-1" />
                  Outfit
                </Button>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      size="sm"
                      variant="secondary"
                      className="bg-white/90 text-gray-900 hover:bg-white"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={(e) => e.stopPropagation()}>
                      <Eye className="w-4 h-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={(e) => e.stopPropagation()}>
                      <Heart className="w-4 h-4 mr-2" />
                      {item.favorite ? 'Remove from Favorites' : 'Add to Favorites'}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            )}
            
            {/* Favorite indicator */}
            {item.favorite && (
              <div className="absolute top-2 right-2">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center shadow-lg">
                  <Heart className="w-4 h-4 text-white fill-current" />
                </div>
              </div>
            )}
            
            {/* Wear count badge */}
            <div className="absolute bottom-2 left-2">
              <Badge variant="secondary" className="bg-white/90 text-gray-900 text-xs">
                {item.wearCount} wears
              </Badge>
            </div>
          </div>

          {/* Item Info */}
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
                
                {item.style && item.style.length > 0 && (
                  <div className="flex gap-1">
                    {item.style.slice(0, 2).map((style, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {style}
                      </Badge>
                    ))}
                    {item.style.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{item.style.length - 2}
                      </Badge>
                    )}
                  </div>
                )}
              </div>

              {/* Season and Occasion */}
              {(item.season || item.occasion) && (
                <div className="flex flex-wrap gap-1">
                  {item.season?.slice(0, 2).map((season, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {season}
                    </Badge>
                  ))}
                  {item.occasion?.slice(0, 1).map((occasion, index) => (
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
  );
} 