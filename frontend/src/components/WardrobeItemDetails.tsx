"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { 
  Heart, 
  Sparkles, 
  Trash2, 
  Edit3, 
  Save, 
  X, 
  Calendar,
  Shirt,
  Palette,
  Tag
} from "lucide-react";
import { formatLastWorn } from "@/lib/utils/dateUtils";

interface WardrobeItem {
  id: string;
  name: string;
  type: string;
  color: string;
  imageUrl: string;
  backgroundRemovedUrl?: string;  // Stealth-mode: auto-upgraded by worker
  wearCount: number;
  favorite: boolean;
  style?: string[];
  season?: string[];
  occasion?: string[];
  lastWorn?: Date;
  description?: string;
  brand?: string;
  size?: string;
  material?: string[];
  sleeveLength?: string;
  fit?: string;
  neckline?: string;
  length?: string;
  purchaseDate?: Date;
  purchasePrice?: number;
}

interface WardrobeItemDetailsProps {
  item: WardrobeItem | null;
  isOpen: boolean;
  onClose: () => void;
  onUpdate: (itemId: string, updates: Partial<WardrobeItem>) => Promise<void>;
  onDelete: (itemId: string) => Promise<void>;
  onToggleFavorite: (itemId: string) => Promise<void>;
  onIncrementWear: (itemId: string) => Promise<void>;
  onGenerateOutfit: (item: WardrobeItem) => void;
}

const ITEM_TYPES = [
  'shirt', 't-shirt', 'blouse', 'tank-top', 'polo', 'sweater', 'hoodie', 'pants', 'jeans', 'shorts', 'skirt', 'dress', 'jacket', 'blazer', 'coat', 'shoes', 'sneakers', 'boots', 'sandals', 'heels', 'accessory', 'underwear', 'socks', 'hat', 'bag', 'belt', 'scarf', 'jewelry'
];

const COLORS = [
  'black', 'white', 'blue', 'red', 'green', 'yellow', 'purple', 'pink', 'brown', 'gray', 'beige', 'navy', 'burgundy', 'camel'
];

const SEASONS = ['spring', 'summer', 'fall', 'winter'];

const OCCASIONS = ['casual', 'work', 'formal', 'party', 'date', 'gym', 'travel', 'home'];

const STYLES = [
  'classic', 'modern', 'vintage', 'bohemian', 'minimalist', 'edgy', 'romantic', 'athletic', 'preppy', 'artistic'
];

const SLEEVE_LENGTHS = [
  'sleeveless', 'short-sleeve', 'long-sleeve', 'three-quarter-sleeve', 'cap-sleeve', 'off-shoulder'
];

const MATERIALS = [
  'cotton', 'polyester', 'wool', 'silk', 'linen', 'denim', 'leather', 'suede', 'cashmere', 'spandex', 'rayon', 'viscose', 'nylon', 'acrylic', 'bamboo', 'hemp', 'modal', 'elastane', 'lycra'
];

const FITS = [
  'slim', 'regular', 'loose', 'oversized', 'fitted', 'relaxed', 'tapered', 'straight', 'skinny', 'wide-leg'
];

const NECKLINES = [
  'crew-neck', 'v-neck', 'scoop-neck', 'boat-neck', 'off-shoulder', 'halter', 'turtleneck', 'cowl-neck', 'sweetheart', 'square-neck'
];

const LENGTHS = [
  'mini', 'midi', 'maxi', 'knee-length', 'ankle-length', 'crop', 'regular', 'long', 'short'
];

// Phase 1 new constants for gender-inclusive outfit generation
const TRANSPARENCIES = ['opaque', 'semi-sheer', 'sheer', 'textured-opaque'];
const COLLAR_TYPES = ['button-down', 'spread', 'point', 'band', 'mandarin', 'camp', 'shawl', 'peter-pan', 'none'];
const EMBELLISHMENTS = ['none', 'minimal', 'moderate', 'heavy'];
const PRINT_TYPES = ['none', 'logo', 'text', 'graphic', 'abstract', 'geometric', 'floral', 'animal'];
const RISE_TYPES = ['high-rise', 'mid-rise', 'low-rise'];
const LEG_OPENINGS = ['straight', 'tapered', 'wide', 'flared', 'bootcut', 'skinny'];
const HEEL_HEIGHTS = ['flat', 'low', 'mid', 'high', 'very-high', 'platform'];

export default function WardrobeItemDetails({
  item,
  isOpen,
  onClose,
  onUpdate,
  onDelete,
  onToggleFavorite,
  onIncrementWear,
  onGenerateOutfit
}: WardrobeItemDetailsProps) {
  const [editedItem, setEditedItem] = useState<Partial<WardrobeItem>>({});
  const [isSaving, setIsSaving] = useState(false);

  // Debug logging
  console.log('🔍 [WardrobeItemDetails] Component rendered with:', { item, isOpen });

  useEffect(() => {
    if (item) {
      setEditedItem({
        name: item.name,
        type: item.type,
        color: item.color,
        style: item.style || [],
        season: item.season || [],
        occasion: item.occasion || [],
        description: item.description || '',
        brand: item.brand || '',
        size: item.size || '',
        material: item.material || [],
        sleeveLength: item.sleeveLength || '',
        fit: item.fit || '',
        neckline: item.neckline || '',
        length: item.length || '',
        purchasePrice: item.purchasePrice || 0
      });
    }
  }, [item]);

  const handleSave = async () => {
    if (!item) return;
    
    setIsSaving(true);
    try {
      await onUpdate(item.id, editedItem);
    } catch (error) {
      console.error('Failed to update item:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!item) return;
    
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
      try {
        await onDelete(item.id);
        onClose();
      } catch (error) {
        console.error('Failed to delete item:', error);
      }
    }
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
      'gray': 'bg-gray-500 text-white',
      'beige': 'bg-amber-100 text-amber-900 border border-amber-300',
      'navy': 'bg-blue-900 text-white',
      'burgundy': 'bg-red-900 text-white',
      'camel': 'bg-amber-200 text-amber-900 border border-amber-400'
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
      case 'underwear': return '🩲';
      case 'socks': return '🧦';
      case 'hat': return '🧢';
      case 'bag': return '👜';
      default: return '👕';
    }
  };

  if (!item) return null;

  // Helper function to determine if a field is relevant for this item type
  const isFieldRelevant = (fieldName: string): boolean => {
    const itemType = item.type?.toLowerCase() || '';
    
    // Define item categories
    const tops = ['shirt', 'blouse', 't-shirt', 'tshirt', 'sweater', 'hoodie', 'jacket', 'coat', 'cardigan', 'vest', 'top', 'tank'];
    const bottoms = ['pants', 'shorts', 'skirt', 'jeans', 'trousers', 'leggings'];
    const dresses = ['dress', 'gown', 'jumpsuit', 'romper'];
    const shoes = ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'flats'];
    const accessories = ['hat', 'bag', 'belt', 'scarf', 'gloves', 'tie', 'watch', 'jewelry', 'sunglasses'];
    
    const isTop = tops.some(t => itemType.includes(t));
    const isBottom = bottoms.some(b => itemType.includes(b));
    const isDress = dresses.some(d => itemType.includes(d));
    const isShoe = shoes.some(s => itemType.includes(s));
    const isAccessory = accessories.some(a => itemType.includes(a));
    
    switch(fieldName) {
      case 'sleeveLength':
        return isTop || isDress; // Only tops and dresses have sleeves
      case 'neckline':
      case 'collarType':
        return isTop || isDress; // Only tops and dresses have necklines/collars
      case 'transparency':
        return isTop || isBottom || isDress; // Clothing items can be transparent
      case 'rise':
        return isBottom; // Only pants/shorts/skirts have rise
      case 'legOpening':
        return itemType.includes('pants') || itemType.includes('jeans'); // Only pants have leg openings
      case 'heelHeight':
        return isShoe; // Only shoes have heel height
      case 'embellishments':
      case 'printSpecificity':
        return !isAccessory; // All clothing items can have embellishments/prints
      case 'statementLevel':
        return true; // All items have a statement level
      case 'fit':
        return !isShoe && !isAccessory; // Most items except shoes and accessories
      case 'length':
        return isTop || isBottom || isDress; // Clothing items have length
      case 'size':
      case 'material':
        return true; // Always relevant
      default:
        return true;
    }
  };

  // Helper function to get visual attributes from nested AI analysis or top-level
  const getVisualAttribute = (field: string, defaultValue: any = null) => {
    // First check top-level
    if (item[field]) return item[field];
    // Then check nested in analysis.metadata.visualAttributes (camelCase)
    const visualAttrs = item.analysis?.metadata?.visualAttributes;
    if (visualAttrs && visualAttrs[field]) return visualAttrs[field];
    // Also check snake_case version (visual_attributes)
    const visualAttrsSnake = item.analysis?.metadata?.visual_attributes;
    if (visualAttrsSnake && visualAttrsSnake[field]) return visualAttrsSnake[field];
    return defaultValue;
  };

  // Get description from multiple possible sources
  const getDescription = () => {
    if (item.description) return item.description;
    // Check camelCase version
    if (item.analysis?.metadata?.naturalDescription) return item.analysis.metadata.naturalDescription;
    // Check snake_case version
    if (item.analysis?.metadata?.natural_description) return item.analysis.metadata.natural_description;
    return null;
  };

  // Get material as array
  const getMaterials = () => {
    // Check top-level material field
    if (item.material) {
      return Array.isArray(item.material) ? item.material : [item.material];
    }
    // Check nested visual attributes
    const material = getVisualAttribute('material');
    if (material) {
      return Array.isArray(material) ? material : [material];
    }
    return [];
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="relative max-w-4xl max-h-[90vh] overflow-y-auto [&>button]:hidden">
        <DialogClose asChild>
          <Button
            variant="ghost"
            size="icon"
            className="absolute top-6 right-6 text-stone-600 hover:text-stone-900"
            aria-label="Close"
            disabled={isSaving}
          >
            <X className="w-4 h-4" />
          </Button>
        </DialogClose>
        <DialogHeader className="pr-16">
          <div className="flex items-center justify-between gap-4">
            <DialogTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">
              Edit Item
            </DialogTitle>
            <Button
              size="sm"
              onClick={handleSave}
              disabled={isSaving}
              className="bg-stone-900 hover:bg-stone-800 text-white"
            >
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Section */}
          <div className="space-y-4">
            <div className="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
              <img
                src={item.backgroundRemovedUrl ?? item.imageUrl}
                alt={item.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.jpg';
                }}
              />
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                onClick={() => onGenerateOutfit(item)}
                className="flex-1 bg-stone-900 hover:bg-stone-800 text-white"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Outfit
              </Button>
              <Button
                variant="outline"
                onClick={() => onToggleFavorite(item.id)}
                className={`${item.favorite ? 'bg-red-50 border-red-200 text-red-700' : ''}`}
              >
                <Heart className={`w-4 h-4 ${item.favorite ? 'fill-current' : ''}`} />
              </Button>
              <Button
                variant="outline"
                onClick={() => onIncrementWear(item.id)}
                className="text-stone-700 hover:text-stone-900"
              >
                <Calendar className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Details Section */}
          <div className="space-y-6">
            {/* Edit Form */}
            <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name" className="text-stone-700 dark:text-stone-300 font-medium">Name</Label>
                    <Input
                      id="name"
                      value={editedItem.name || ''}
                      onChange={(e) => setEditedItem({ ...editedItem, name: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="type" className="text-stone-700 dark:text-stone-300 font-medium">Type</Label>
                    <Select
                      value={editedItem.type || ''}
                      onValueChange={(value) => setEditedItem({ ...editedItem, type: value })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        {ITEM_TYPES.map(type => (
                          <SelectItem key={type} value={type}>
                            {getTypeIcon(type)} {type.charAt(0).toUpperCase() + type.slice(1)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="color" className="text-stone-700 dark:text-stone-300 font-medium">Color</Label>
                    <Select
                      value={editedItem.color || ''}
                      onValueChange={(value) => setEditedItem({ ...editedItem, color: value })}
                    >
                      <SelectTrigger className="mt-1">
                        <SelectValue placeholder="Select color" />
                      </SelectTrigger>
                      <SelectContent>
                        {COLORS.map(color => (
                          <SelectItem key={color} value={color}>
                            <div className="flex items-center gap-2">
                              <span className={`inline-block w-3 h-3 rounded-full ${getColorBadge(color)}`}></span>
                              {color.charAt(0).toUpperCase() + color.slice(1)}
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="brand" className="text-stone-700 dark:text-stone-300 font-medium">Brand</Label>
                    <Input
                      id="brand"
                      value={editedItem.brand || ''}
                      onChange={(e) => setEditedItem({ ...editedItem, brand: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {isFieldRelevant('size') && (
                    <div>
                      <Label htmlFor="size" className="text-stone-700 dark:text-stone-300 font-medium">Size</Label>
                      <Input
                        id="size"
                        value={editedItem.size || ''}
                        onChange={(e) => setEditedItem({ ...editedItem, size: e.target.value })}
                        className="mt-1"
                      />
                    </div>
                  )}
                  {isFieldRelevant('sleeveLength') && (
                    <div>
                      <Label htmlFor="sleeveLength" className="text-stone-700 dark:text-stone-300 font-medium">Sleeve Length</Label>
                      <Select
                        value={editedItem.sleeveLength || ''}
                        onValueChange={(value) => setEditedItem({ ...editedItem, sleeveLength: value })}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select sleeve length" />
                        </SelectTrigger>
                        <SelectContent>
                          {SLEEVE_LENGTHS.map(length => (
                            <SelectItem key={length} value={length}>
                              {length.charAt(0).toUpperCase() + length.slice(1).replace('-', ' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {isFieldRelevant('fit') && (
                    <div>
                      <Label htmlFor="fit" className="text-stone-700 dark:text-stone-300 font-medium">Fit</Label>
                      <Select
                        value={editedItem.fit || ''}
                        onValueChange={(value) => setEditedItem({ ...editedItem, fit: value })}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select fit" />
                        </SelectTrigger>
                        <SelectContent>
                          {FITS.map(fit => (
                            <SelectItem key={fit} value={fit}>
                              {fit.charAt(0).toUpperCase() + fit.slice(1)}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                  {isFieldRelevant('neckline') && (
                    <div>
                      <Label htmlFor="neckline" className="text-stone-700 dark:text-stone-300 font-medium">Neckline</Label>
                      <Select
                        value={editedItem.neckline || ''}
                        onValueChange={(value) => setEditedItem({ ...editedItem, neckline: value })}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select neckline" />
                        </SelectTrigger>
                        <SelectContent>
                          {NECKLINES.map(neckline => (
                            <SelectItem key={neckline} value={neckline}>
                              {neckline.charAt(0).toUpperCase() + neckline.slice(1).replace('-', ' ')}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {isFieldRelevant('length') && (
                    <div>
                      <Label htmlFor="length" className="text-stone-700 dark:text-stone-300 font-medium">Length</Label>
                      <Select
                        value={editedItem.length || ''}
                        onValueChange={(value) => setEditedItem({ ...editedItem, length: value })}
                      >
                        <SelectTrigger className="mt-1">
                          <SelectValue placeholder="Select length" />
                        </SelectTrigger>
                        <SelectContent>
                          {LENGTHS.map(length => (
                            <SelectItem key={length} value={length}>
                              {length.charAt(0).toUpperCase() + length.slice(1)}
                            </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  )}
                  <div>
                    <Label htmlFor="purchasePrice" className="text-stone-700 dark:text-stone-300 font-medium">Purchase Price</Label>
                    <Input
                      id="purchasePrice"
                      type="number"
                      value={editedItem.purchasePrice || ''}
                      onChange={(e) => setEditedItem({ ...editedItem, purchasePrice: parseFloat(e.target.value) || 0 })}
                      className="mt-1"
                      placeholder="0.00"
                    />
                  </div>
                </div>

                <div>
                  <Label className="text-stone-700 dark:text-stone-300 font-medium">Materials</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {MATERIALS.map(material => (
                      <Badge
                        key={material}
                        variant={editedItem.material?.includes(material) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => {
                          const currentMaterials = editedItem.material || [];
                          const newMaterials = currentMaterials.includes(material)
                            ? currentMaterials.filter(m => m !== material)
                            : [...currentMaterials, material];
                          setEditedItem({ ...editedItem, material: newMaterials });
                        }}
                      >
                        {material}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label htmlFor="description" className="text-stone-700 dark:text-stone-300 font-medium">Description</Label>
                  <Textarea
                    id="description"
                    value={editedItem.description || ''}
                    onChange={(e) => setEditedItem({ ...editedItem, description: e.target.value })}
                    className="mt-1"
                    rows={3}
                  />
                </div>

                <div>
                  <Label className="text-stone-700 dark:text-stone-300 font-medium">Styles</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {STYLES.map(style => (
                      <Badge
                        key={style}
                        variant={editedItem.style?.includes(style) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => {
                          const currentStyles = editedItem.style || [];
                          const newStyles = currentStyles.includes(style)
                            ? currentStyles.filter(s => s !== style)
                            : [...currentStyles, style];
                          setEditedItem({ ...editedItem, style: newStyles });
                        }}
                      >
                        {style}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-stone-700 dark:text-stone-300 font-medium">Seasons</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {SEASONS.map(season => (
                      <Badge
                        key={season}
                        variant={editedItem.season?.includes(season) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => {
                          const currentSeasons = editedItem.season || [];
                          const newSeasons = currentSeasons.includes(season)
                            ? currentSeasons.filter(s => s !== season)
                            : [...currentSeasons, season];
                          setEditedItem({ ...editedItem, season: newSeasons });
                        }}
                      >
                        {season}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div>
                  <Label className="text-stone-700 dark:text-stone-300 font-medium">Occasions</Label>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {OCCASIONS.map(occasion => (
                      <Badge
                        key={occasion}
                        variant={editedItem.occasion?.includes(occasion) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => {
                          const currentOccasions = editedItem.occasion || [];
                          const newOccasions = currentOccasions.includes(occasion)
                            ? currentOccasions.filter(o => o !== occasion)
                            : [...currentOccasions, occasion];
                          setEditedItem({ ...editedItem, occasion: newOccasions });
                        }}
                      >
                        {occasion}
                      </Badge>
                    ))}
                  </div>
                </div>
            </div>
          </div>
        </div>

        {/* Delete Button */}
        <div className="flex justify-end pt-6 border-t border-stone-200 dark:border-stone-700">
          <Button
            variant="outline"
            onClick={handleDelete}
            className="text-red-600 hover:text-red-700 hover:bg-red-50 border-red-200"
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Item
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
