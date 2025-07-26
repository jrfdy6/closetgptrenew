import { motion } from "framer-motion";
import Image from "next/image";
import type { OutfitGeneratedOutfit, ClothingItem } from "../shared/types";

interface OutfitVisualizationProps {
  outfit: OutfitGeneratedOutfit;
  onItemClick?: (item: ClothingItem) => void;
  className?: string;
}

export function OutfitVisualization({ outfit, onItemClick, className = "" }: OutfitVisualizationProps) {  // Filter out string IDs and only keep ClothingItem objects
  const outfitItems = outfit.items.filter((item): item is ClothingItem => 
    typeof item !== 'string' && 'id' in item && 'imageUrl' in item
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`grid grid-cols-2 gap-4 ${className}`}
    >
      {outfitItems.map((item, i) => (
        <motion.div
          key={item.id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.1 }}
          className="relative aspect-square overflow-hidden rounded-lg"
          onClick={() => onItemClick?.(item)}
        >
          <Image
            src={item.imageUrl}
            alt={item.name}
            fill
            className="object-cover"
          />
        </motion.div>
      ))}
    </motion.div>
  );
} 
