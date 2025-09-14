"use client";

import { useState, useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
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
  wearCount: number;
  favorite: boolean;
  style?: string[];
  season?: string[];
  occasion?: string[];
  lastWorn?: Date;
  description?: string;
  brand?: string;
  size?: string;
  material?: string;
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
  'shirt', 'pants', 'dress', 'jacket', 'shoes', 'accessory', 'underwear', 'socks', 'hat', 'bag'
];

const COLORS = [
  'black', 'white', 'blue', 'red', 'green', 'yellow', 'purple', 'pink', 'brown', 'gray', 'beige', 'navy', 'burgundy', 'camel'
];

const SEASONS = ['spring', 'summer', 'fall', 'winter'];

const OCCASIONS = ['casual', 'work', 'formal', 'party', 'date', 'gym', 'travel', 'home'];

const STYLES = [
  'classic', 'modern', 'vintage', 'bohemian', 'minimalist', 'edgy', 'romantic', 'athletic', 'preppy', 'artistic'
];

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
  const [isEditing, setIsEditing] = useState(false);
  const [editedItem, setEditedItem] = useState<Partial<WardrobeItem>>({});
  const [isSaving, setIsSaving] = useState(false);

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
        material: item.material || '',
        purchasePrice: item.purchasePrice || 0
      });
    }
  }, [item]);

  const handleSave = async () => {
    if (!item) return;
    
    setIsSaving(true);
    try {
      await onUpdate(item.id, editedItem);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update item:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setEditedItem({
      name: item?.name || '',
      type: item?.type || '',
      color: item?.color || '',
      style: item?.style || [],
      season: item?.season || [],
      occasion: item?.occasion || [],
      description: item?.description || '',
      brand: item?.brand || '',
      size: item?.size || '',
      material: item?.material || '',
      purchasePrice: item?.purchasePrice || 0
    });
    setIsEditing(false);
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
      'blue': 'bg-blue-500 text-white',
      'red': 'bg-red-500 text-white',
      'green': 'bg-green-500 text-white',
      'yellow': 'bg-yellow-500 text-white',
      'purple': 'bg-purple-500 text-white',
      'pink': 'bg-pink-500 text-white',
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

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">
              {isEditing ? 'Edit Item' : 'Item Details'}
            </DialogTitle>
            <div className="flex gap-2">
              {!isEditing ? (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                    className="text-stone-700 hover:text-stone-900"
                  >
                    <Edit3 className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={onClose}
                    className="text-stone-600 hover:text-stone-900"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCancel}
                    disabled={isSaving}
                    className="text-stone-700 hover:text-stone-900"
                  >
                    <X className="w-4 h-4 mr-2" />
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleSave}
                    disabled={isSaving}
                    className="bg-stone-900 hover:bg-stone-800 text-white"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {isSaving ? 'Saving...' : 'Save'}
                  </Button>
                </>
              )}
            </div>
          </div>
        </DialogHeader>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image Section */}
          <div className="space-y-4">
            <div className="aspect-square bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden">
              <img
                src={item.imageUrl}
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
            {isEditing ? (
              /* Edit Form */
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
                  <div>
                    <Label htmlFor="size" className="text-stone-700 dark:text-stone-300 font-medium">Size</Label>
                    <Input
                      id="size"
                      value={editedItem.size || ''}
                      onChange={(e) => setEditedItem({ ...editedItem, size: e.target.value })}
                      className="mt-1"
                    />
                  </div>
                  <div>
                    <Label htmlFor="material" className="text-stone-700 dark:text-stone-300 font-medium">Material</Label>
                    <Input
                      id="material"
                      value={editedItem.material || ''}
                      onChange={(e) => setEditedItem({ ...editedItem, material: e.target.value })}
                      className="mt-1"
                    />
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
            ) : (
              /* View Mode */
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-serif text-stone-900 dark:text-stone-100 mb-2">{item.name}</h2>
                  <div className="flex items-center gap-2 text-stone-600 dark:text-stone-400">
                    <span>{getTypeIcon(item.type)}</span>
                    <span className="capitalize">{item.type}</span>
                    {item.brand && (
                      <>
                        <span>•</span>
                        <span>{item.brand}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Card className="border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800/50">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Palette className="w-4 h-4 text-stone-600" />
                        <span className="font-medium text-stone-900 dark:text-stone-100">Color</span>
                      </div>
                      <Badge className={`${getColorBadge(item.color)}`}>
                        {item.color}
                      </Badge>
                    </CardContent>
                  </Card>

                  <Card className="border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800/50">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-4 h-4 text-stone-600" />
                        <span className="font-medium text-stone-900 dark:text-stone-100">Wear Count</span>
                      </div>
                      <span className="text-2xl font-bold text-stone-900 dark:text-stone-100">{item.wearCount}</span>
                    </CardContent>
                  </Card>
                </div>

                {item.description && (
                  <div>
                    <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-2">Description</h3>
                    <p className="text-stone-600 dark:text-stone-400">{item.description}</p>
                  </div>
                )}

                {(item.size || item.material) && (
                  <div className="grid grid-cols-2 gap-4">
                    {item.size && (
                      <div>
                        <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-1">Size</h3>
                        <p className="text-stone-600 dark:text-stone-400">{item.size}</p>
                      </div>
                    )}
                    {item.material && (
                      <div>
                        <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-1">Material</h3>
                        <p className="text-stone-600 dark:text-stone-400">{item.material}</p>
                      </div>
                    )}
                  </div>
                )}

                {item.style && item.style.length > 0 && (
                  <div>
                    <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-2">Styles</h3>
                    <div className="flex flex-wrap gap-2">
                      {item.style.map((style, index) => (
                        <Badge key={index} variant="outline">
                          {style}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {item.season && item.season.length > 0 && (
                  <div>
                    <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-2">Seasons</h3>
                    <div className="flex flex-wrap gap-2">
                      {item.season.map((season, index) => (
                        <Badge key={index} variant="outline">
                          {season}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {item.occasion && item.occasion.length > 0 && (
                  <div>
                    <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-2">Occasions</h3>
                    <div className="flex flex-wrap gap-2">
                      {item.occasion.map((occasion, index) => (
                        <Badge key={index} variant="outline">
                          {occasion}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {item.lastWorn && (
                  <div>
                    <h3 className="font-medium text-stone-900 dark:text-stone-100 mb-1">Last Worn</h3>
                    <p className="text-stone-600 dark:text-stone-400">{formatLastWorn(item.lastWorn)}</p>
                  </div>
                )}
              </div>
            )}
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
