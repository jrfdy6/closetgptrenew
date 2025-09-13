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
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Header */}
      <div className="bg-stone-100 dark:bg-stone-800/50 border-b border-stone-200 dark:border-stone-700 px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-6 mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.back()}
              className="text-stone-700 hover:text-stone-900 dark:text-stone-300 dark:hover:text-stone-100 px-6 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105"
            >
              <ArrowLeft className="h-5 w-5 mr-3" />
              Back
            </Button>
          </div>
          <div className="flex items-center gap-6">
            <div className="p-4 bg-stone-900 dark:bg-stone-100 rounded-full">
              <Plus className="h-8 w-8 text-white dark:text-stone-900" />
            </div>
            <div>
              <h1 className="text-4xl font-serif font-bold text-stone-900 dark:text-stone-100">Create Outfit</h1>
              <p className="text-stone-600 dark:text-stone-400 font-light text-lg mt-2">
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
          <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl font-serif text-stone-900 dark:text-stone-100">
                <Sparkles className="h-6 w-6 text-stone-600 dark:text-stone-400" />
                Outfit Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-3">
                  <Label htmlFor="name" className="text-stone-700 dark:text-stone-300 font-medium">Outfit Name *</Label>
                  <Input
                    id="name"
                    placeholder="e.g., Summer Casual Look"
                    value={outfitName}
                    onChange={(e) => setOutfitName(e.target.value)}
                    className="border-stone-300 dark:border-stone-600 focus:border-stone-500 focus:ring-stone-500 rounded-lg"
                  />
                </div>
                <div className="space-y-3">
                  <Label htmlFor="occasion" className="text-stone-700 dark:text-stone-300 font-medium">Occasion</Label>
                  <Select value={occasion} onValueChange={setOccasion}>
                    <SelectTrigger className="border-stone-300 dark:border-stone-600 focus:border-stone-500 focus:ring-stone-500 rounded-lg">
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
              
              <div className="space-y-3">
                <Label htmlFor="style" className="text-stone-700 dark:text-stone-300 font-medium">Style</Label>
                <Select value={style} onValueChange={setStyle}>
                  <SelectTrigger className="border-stone-300 dark:border-stone-600 focus:border-stone-500 focus:ring-stone-500 rounded-lg">
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((sty) => (
                      <SelectItem key={sty} value={sty}>{sty}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <Label htmlFor="description" className="text-stone-700 dark:text-stone-300 font-medium">Description (Optional)</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your outfit..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  rows={3}
                  className="border-stone-300 dark:border-stone-600 focus:border-stone-500 focus:ring-stone-500 rounded-lg"
                />
              </div>

              <div className="space-y-3">
                <Label htmlFor="notes" className="text-stone-700 dark:text-stone-300 font-medium">Notes (Optional)</Label>
                <Textarea
                  id="notes"
                  placeholder="Add any notes about this outfit..."
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={2}
                  className="border-stone-300 dark:border-stone-600 focus:border-stone-500 focus:ring-stone-500 rounded-lg"
                />
              </div>
            </CardContent>
          </Card>

          {/* Selected Items */}
          {selectedItems.length > 0 && (
            <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center gap-3 text-xl font-serif text-stone-900 dark:text-stone-100">
                  <Shirt className="h-6 w-6 text-stone-600 dark:text-stone-400" />
                  Selected Items ({selectedItems.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedItems.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-center gap-4 p-4 bg-stone-50 dark:bg-stone-800/50 rounded-lg border border-stone-200 dark:border-stone-700"
                    >
                      <div className="flex-shrink-0">
                        {item.imageUrl ? (
                          <img
                            src={item.imageUrl}
                            alt={item.name}
                            className="w-12 h-12 rounded-lg object-cover"
                            onError={(e) => {
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                        ) : (
                          <div className="w-12 h-12 bg-stone-200 dark:bg-stone-700 rounded-lg flex items-center justify-center">
                            {getItemIcon(item.type)}
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-stone-900 dark:text-stone-100 truncate">
                          {item.name}
                        </p>
                        <p className="text-xs text-stone-500 dark:text-stone-400">
                          {item.type} • {item.color}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveItem(item.id)}
                        className="text-stone-400 hover:text-red-600 h-8 w-8 p-0 rounded-full"
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
          <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-xl font-serif text-stone-900 dark:text-stone-100">
                <Plus className="h-6 w-6 text-stone-600 dark:text-stone-400" />
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
          <div className="flex justify-end gap-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
              disabled={saving}
              className="border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 px-8 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={saving || !outfitName.trim() || selectedItems.length === 0}
              className="bg-stone-900 hover:bg-stone-800 text-white px-8 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105 shadow-lg"
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
