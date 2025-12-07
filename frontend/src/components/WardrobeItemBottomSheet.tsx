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
        <div className="relative w-full max-w-xs md:max-w-sm mx-auto aspect-[3/4] bg-secondary dark:bg-muted rounded-2xl overflow-hidden">
          {!imageLoaded && (
            <div className="absolute inset-0 animate-pulse bg-muted dark:bg-muted" />
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
          <h3 className="heading-lg mb-2 text-card-foreground">
            {item.name}
          </h3>
          <p className="text-body text-muted-foreground capitalize">
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
        <div className="flex gap-4 p-4 bg-secondary/80 dark:bg-card/85 border border-border/60 dark:border-border/70 rounded-xl">
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-card-foreground">
              {item.wearCount || 0}
            </div>
            <div className="text-caption text-muted-foreground">
              Times worn
            </div>
          </div>
          <div className="w-px bg-border dark:bg-border" />
          <div className="flex-1 text-center">
            <div className="text-2xl font-bold text-card-foreground">
              {item.lastWorn 
                ? new Date(item.lastWorn).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
                : 'Never'}
            </div>
            <div className="text-caption text-muted-foreground">
              Last worn
            </div>
          </div>
        </div>

        {/* Primary Action */}
        <Button
          onClick={handleGenerateOutfit}
          className={cn(
            "w-full h-14 text-button font-semibold rounded-2xl",
            "bg-gradient-to-r from-primary to-accent text-primary-foreground",
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
              "flex-col h-20 gap-1 border-border/60 dark:border-border/70 text-muted-foreground hover:text-foreground hover:bg-secondary",
              item.favorite && "border-destructive bg-destructive/10 dark:bg-destructive/20 text-destructive"
            )}
          >
            <Heart 
              className={cn(
                "w-5 h-5",
                item.favorite && "fill-destructive text-destructive"
              )} 
            />
            <span className="text-caption">
              {item.favorite ? 'Favorited' : 'Favorite'}
            </span>
          </Button>

          <Button
            variant="outline"
            onClick={handleIncrementWear}
            className="flex-col h-20 gap-1 border-border/60 dark:border-border/70 text-muted-foreground hover:text-foreground hover:bg-secondary"
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
              className="flex-col h-20 gap-1 border-border/60 dark:border-border/70 text-muted-foreground hover:text-foreground hover:bg-secondary"
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
            className="w-full text-destructive hover:text-destructive/90 hover:bg-destructive/10 dark:hover:bg-destructive/20 rounded-2xl"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Item
          </Button>
        )}
      </div>
    </BottomSheet>
  );
}

