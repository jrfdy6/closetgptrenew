"use client";

import { Heart } from "lucide-react";

interface WardrobeItem {
  id: string;
  name: string;
  type: string;
  color: string;
  imageUrl: string;
  wearCount?: number;
  favorite: boolean;
  style?: string[];
  season?: string[];
  occasion?: string[];
  lastWorn?: Date | string;
  tags?: string[];
}

interface WardrobeGridSimpleProps {
  items: WardrobeItem[];
  loading: boolean;
  onItemClick: (item: WardrobeItem) => void;
}

export default function WardrobeGridSimple({
  items,
  loading,
  onItemClick
}: WardrobeGridSimpleProps) {

  if (loading) {
    // Skeleton grid
    return (
      <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-5">
        {[...Array(12)].map((_, i) => (
          <div key={i} className="aspect-square bg-gray-200 dark:bg-[#3D2F24] rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-body text-gray-600 dark:text-[#C4BCB4]">
          No items found
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3 md:gap-5">
      {items.map((item) => (
        <div
          key={item.id}
          className="group cursor-pointer"
          onClick={() => onItemClick(item)}
        >
          {/* Image Container - Clean, Premium */}
          <div className="relative aspect-square overflow-hidden rounded-xl bg-gray-100 dark:bg-[#3D2F24] transition-transform duration-200 hover:scale-102">
            <img
              src={item.imageUrl}
              alt={item.name}
              className="w-full h-full object-cover"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = '/placeholder.jpg';
              }}
              loading="lazy"
            />

            {/* Simple overlay on hover - just shows name + wear count */}
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent p-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <div className="text-white text-[11px] font-medium truncate">
                {item.name}
              </div>
              {(item.wearCount ?? 0) > 0 && (
                <div className="text-white/70 text-[10px]">
                  Worn {item.wearCount}×
                </div>
              )}
            </div>

            {/* Favorite indicator - small, clean */}
            {item.favorite && (
              <div className="absolute top-2 right-2 w-6 h-6 bg-red-500/90 backdrop-blur-sm rounded-full flex items-center justify-center shadow-lg">
                <Heart className="w-3.5 h-3.5 text-white fill-current" />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

