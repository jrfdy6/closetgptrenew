"use client";

import { useState } from "react";
import { ClothingItem } from "@/types/wardrobe";
import BottomSheet from "./BottomSheet";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Sparkles, 
  Heart, 
  Calendar, 
  Edit, 
  Trash2,
  ShoppingBag,
  Palette,
  Sun
} from "lucide-react";
import { cn } from "@/lib/utils";

interface WardrobeItemBottomSheetProps {
  item: ClothingItem | null;
  isOpen: boolean;
  onClose: () => void;
  onGenerateOutfit: (item: ClothingItem) => void;
  onToggleFavorite: (itemId: string) => void;
  onIncrementWear: (itemId: string) => void;
  onEdit?: (item: ClothingItem) => void;
  onDelete?: (itemId: string) => void;
}

export default function WardrobeItemBottomSheet({
  item,
  isOpen,
  onClose,
  onGenerateOutfit,
  onToggleFavorite,
  onIncrementWear,
  onEdit,
  onDelete
}: WardrobeItemBottomSheetProps) {
  const [imageLoaded, setImageLoaded] = useState(false);

  if (!item) return null;

  const handleGenerateOutfit = () => {
    onGenerateOutfit(item);
    onClose();
  };

  const handleToggleFavorite = () => {
    onToggleFavorite(item.id);
  };

  const handleIncrementWear = () => {
    onIncrementWear(item.id);
  };

  return (
    <BottomSheet
      isOpen={isOpen}
      onClose={onClose}
      className="md:left-1/2 md:right-auto md:w-full md:max-w-xl md:translate-x-[-50%]"
    >
      <div className="p-6 space-y-6 max-w-2xl mx-auto">
        {/* Image Section */}
        <div className="relative w-full max-w-xs md:max-w-sm mx-auto aspect-[3/4] bg-gray-100 dark:bg-[#262626] rounded-2xl overflow-hidden">
          {!imageLoaded && (
            <div className="absolute inset-0 animate-pulse bg-gray-200 dark:bg-[#8A827A]" />
          )}
          <img
            src={item.imageUrl}
            alt={item.name}
            className="w-full h-full object-cover"
            onLoad={() => setImageLoaded(true)}
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = '/placeholder.jpg';
            }}
          />
          
          {/* Favorite indicator */}
          {item.favorite && (
            <div className="absolute top-4 right-4 w-10 h-10 bg-red-500 rounded-full flex items-center justify-center shadow-lg">
              <Heart className="w-5 h-5 text-white fill-current" />
            </div>
          )}
        </div>

        {/* Title & Type */}
        <div>
          <h3 className="heading-lg mb-2 text-gray-900 dark:text-[#F8F5F1]">
            {item.name}
          </h3>
          <p className="text-body text-gray-600 dark:text-[#C4BCB4] capitalize">
            {item.type}
          </p>
        </div>

        {/* Metadata Tags */}
        <div className="flex flex-wrap gap-2">
          {item.color && (
            <Badge variant="secondary" className="text-body-sm">
              <Palette className="w-3 h-3 mr-1" />
              {item.color}
            </Badge>
          )}
          {item.season && (
            <Badge variant="secondary" className="text-body-sm">
              <Sun className="w-3 h-3 mr-1" />
              {item.season}
            </Badge>
          )}
          {item.brand && (
            <Badge variant="secondary" className="text-body-sm">
              <ShoppingBag className="w-3 h-3 mr-1" />
              {item.brand}
            </Badge>
          )}
        </div>

        {/* Stats */}
        <div className="flex gap-4 p-4 bg-[#F5F0E8]/80 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-xl">
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-[#F8F5F1]">
              {item.wearCount || 0}
            </div>
            <div className="text-caption text-[#57534E] dark:text-[#C4BCB4]">
              Times worn
            </div>
          </div>
          <div className="w-px bg-[#F5F0E8] dark:bg-[#262626]" />
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-[#F8F5F1]">
              {item.lastWorn 
                ? new Date(item.lastWorn).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                : 'Never'}
            </div>
            <div className="text-caption text-[#57534E] dark:text-[#C4BCB4]">
              Last worn
            </div>
          </div>
        </div>

        {/* Primary Action */}
        <Button
          onClick={handleGenerateOutfit}
          className={cn(
            "w-full h-14 text-button font-semibold rounded-2xl",
            "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white",
            "hover:from-[#FFB84C] hover:to-[#FF7700] transition-transform duration-200 hover:scale-[1.01]",
            "shadow-lg shadow-amber-500/20"
          )}
          size="lg"
        >
          <Sparkles className="w-5 h-5 mr-2" />
          Use in outfit
        </Button>

        {/* Secondary Actions */}
        <div className="grid grid-cols-3 gap-3">
          <Button
            variant="outline"
            onClick={handleToggleFavorite}
            className={cn(
              "flex-col h-20 gap-1 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]",
              item.favorite && "border-[#FF6F61] bg-[#FFF0EC] dark:bg-[#3D211F] text-[#FF6F61]"
            )}
          >
            <Heart 
              className={cn(
                "w-5 h-5",
                item.favorite && "fill-[#FF6F61] text-[#FF6F61]"
              )} 
            />
            <span className="text-caption">
              {item.favorite ? 'Favorited' : 'Favorite'}
            </span>
          </Button>

          <Button
            variant="outline"
            onClick={handleIncrementWear}
            className="flex-col h-20 gap-1 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
          >
            <Calendar className="w-5 h-5" />
            <span className="text-caption">Wore it</span>
          </Button>

          {onEdit && (
            <Button
              variant="outline"
              onClick={() => {
                onEdit(item);
              }}
              className="flex-col h-20 gap-1 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <Edit className="w-5 h-5" />
              <span className="text-caption">Edit</span>
            </Button>
          )}
        </div>

        {/* Delete Button */}
        {onDelete && (
          <Button
            variant="ghost"
            onClick={() => {
              if (confirm(`Delete "${item.name}"?`)) {
                onDelete(item.id);
                onClose();
              }
            }}
            className="w-full text-[#FF6F61] hover:text-[#FF4A3A] hover:bg-[#FFF0EC] dark:hover:bg-[#3D211F] rounded-2xl"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Item
          </Button>
        )}
      </div>
    </BottomSheet>
  );
}

