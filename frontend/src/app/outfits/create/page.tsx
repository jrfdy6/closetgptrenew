'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Plus, 
  X, 
  Save, 
  ArrowLeft,
  Shirt,
  Watch,
  Footprints,
  ShoppingBag,
  Sparkles
} from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useWardrobe } from '@/lib/hooks/useWardrobe';
import { useOutfits } from '@/lib/hooks/useOutfits_proper';
import { ClothingItem } from '@/lib/services/outfitService';
import Navigation from '@/components/Navigation';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ui/use-toast';
import OutfitItemSelector from '@/components/OutfitItemSelector';

const ITEM_TYPE_ICONS = {
  'top': Shirt,
  'bottom': Shirt,
  'shoes': Footprints,
  'accessories': Watch,
  'bag': ShoppingBag,
  'outerwear': Shirt,
  'underwear': Shirt,
  'jewelry': Watch,
  'other': Shirt
};

const OCCASIONS = [
  'Casual',
  'Work',
  'Formal',
  'Party',
  'Date',
  'Gym',
  'Travel',
  'Home',
  'Outdoor',
  'Special Event'
];

const STYLES = [
  'Classic',
  'Modern',
  'Vintage',
  'Bohemian',
  'Minimalist',
  'Edgy',
  'Romantic',
  'Athletic',
  'Preppy',
  'Artistic'
];

export default function CreateOutfitPage() {
  const router = useRouter();
  const { user } = useAuthContext();
  const { items: wardrobeItems, loading: wardrobeLoading } = useWardrobe();
  const { createOutfit } = useOutfits();
  const { toast } = useToast();
  
  const [outfitName, setOutfitName] = useState('');
  const [occasion, setOccasion] = useState('');
  const [style, setStyle] = useState('');
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [selectedItems, setSelectedItems] = useState<ClothingItem[]>([]);
  const [saving, setSaving] = useState(false);

  const handleAddItem = (item: ClothingItem) => {
    if (selectedItems.length >= 10) {
      toast({
        title: "Maximum items reached",
        description: "You can add up to 10 items to an outfit.",
        variant: "destructive"
      });
      return;
    }
    setSelectedItems([...selectedItems, item]);
  };

  const handleRemoveItem = (itemId: string) => {
    setSelectedItems(selectedItems.filter(item => item.id !== itemId));
  };

  const handleSave = async () => {
    if (!outfitName.trim()) {
      toast({
        title: "Name required",
        description: "Please enter a name for your outfit.",
        variant: "destructive"
      });
      return;
    }

    if (selectedItems.length === 0) {
      toast({
        title: "Items required",
        description: "Please add at least one item to your outfit.",
        variant: "destructive"
      });
      return;
    }

    setSaving(true);
    try {
      const outfitData = {
        name: outfitName,
        occasion: occasion || 'Casual',
        style: style || 'Classic',
        description: description || undefined,
        notes: notes || undefined,
        items: selectedItems.map(item => ({
          id: item.id,
          name: item.name,
          category: item.type,
          color: item.color,
          imageUrl: item.imageUrl,
          user_id: item.user_id
        }))
      };

      await createOutfit(outfitData);
      
      toast({
        title: "Outfit created!",
        description: "Your outfit has been saved successfully.",
      });

      router.push('/outfits');
    } catch (error) {
      console.error('Error creating outfit:', error);
      toast({
        title: "Error",
        description: "Failed to create outfit. Please try again.",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const getItemIcon = (type: string) => {
    const IconComponent = ITEM_TYPE_ICONS[type as keyof typeof ITEM_TYPE_ICONS] || ITEM_TYPE_ICONS.other;
    return <IconComponent className="h-4 w-4" />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Header */}
      <div className="bg-gradient-to-r from-emerald-100 to-teal-100 dark:from-emerald-900/20 dark:to-teal-900/20 border-b border-emerald-200 dark:border-emerald-700 px-4 py-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="text-emerald-700 hover:text-emerald-800"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-600 rounded-lg">
              <Plus className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Create Outfit</h1>
              <p className="text-emerald-700 dark:text-emerald-300 mt-1">
                Manually create a custom outfit by selecting items from your wardrobe
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          {/* Outfit Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-emerald-600" />
                Outfit Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Outfit Name *</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Summer Casual Look"
                    value={outfitName}
                    onChange={(e) => setOutfitName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="occasion">Occasion</Label>
                  <Select value={occasion} onValueChange={setOccasion}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      {OCCASIONS.map((occ) => (
                        <SelectItem key={occ} value={occ}>{occ}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="style">Style</Label>
                <Select value={style} onValueChange={setStyle}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((sty) => (
                      <SelectItem key={sty} value={sty}>{sty}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your outfit..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Add any notes about this outfit..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                />
              </div>
            </CardContent>
          </Card>

          {/* Selected Items */}
          {selectedItems.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shirt className="h-5 w-5 text-emerald-600" />
                  Selected Items ({selectedItems.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {selectedItems.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border"
                    >
                      <div className="flex-shrink-0">
                        {item.imageUrl ? (
                          <img
                            src={item.imageUrl}
                            alt={item.name}
                            className="w-10 h-10 rounded object-cover"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                            {getItemIcon(item.type)}
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {item.type} • {item.color}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveItem(item.id)}
                        className="text-gray-400 hover:text-red-600 h-8 w-8 p-0"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Item Selector */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5 text-emerald-600" />
                Add Items from Wardrobe
              </CardTitle>
            </CardHeader>
            <CardContent>
              <OutfitItemSelector
                selectedItems={selectedItems}
                onItemsChange={setSelectedItems}
                wardrobeItems={wardrobeItems}
                maxItems={10}
                showValidation={true}
              />
            </CardContent>
          </Card>

          {/* Save Button */}
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => router.back()}
              disabled={saving}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving || !outfitName.trim() || selectedItems.length === 0}
              className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Create Outfit
                </>
              )}
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
