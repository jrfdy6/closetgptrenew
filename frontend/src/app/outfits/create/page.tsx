'use client';

import { useState, useEffect, useMemo } from 'react';
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
  Sparkles,
  Search,
  Check,
  Loader2,
  ChevronRight,
  Info,
  Filter,
  Grid3x3,
  LayoutGrid
} from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';
import { useWardrobe } from '@/lib/hooks/useWardrobe';
import { useOutfits } from '@/lib/hooks/useOutfits_proper';
import { ClothingItem } from '@/lib/services/outfitService';
import Navigation from '@/components/Navigation';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/ui/use-toast';
import { cn } from '@/lib/utils';

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
  
  // Outfit state
  const [selectedItems, setSelectedItems] = useState<ClothingItem[]>([]);
  const [currentStep, setCurrentStep] = useState<'build' | 'details'>('build');
  
  // Details state (collected after building outfit)
  const [outfitName, setOutfitName] = useState('');
  const [occasion, setOccasion] = useState('');
  const [style, setStyle] = useState('');
  const [description, setDescription] = useState('');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  
  // UI state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedColor, setSelectedColor] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'grid' | 'compact'>('grid');

  // Group items by category
  const itemsByCategory = useMemo(() => {
    const groups: Record<string, ClothingItem[]> = {
      'top': [],
      'bottom': [],
      'shoes': [],
      'outerwear': [],
      'accessories': [],
      'bag': [],
      'jewelry': [],
      'other': []
    };
    
    wardrobeItems.forEach(item => {
      if (groups[item.type]) {
        groups[item.type].push(item);
      } else {
        groups['other'].push(item);
      }
    });
    
    return groups;
  }, [wardrobeItems]);

  // Get all unique colors
  const availableColors = useMemo(() => {
    const colors = new Set<string>();
    wardrobeItems.forEach(item => {
      if (item.color) colors.add(item.color.toLowerCase());
    });
    return Array.from(colors).sort();
  }, [wardrobeItems]);

  // Filter items based on search, category, and color
  const filteredItems = useMemo(() => {
    return wardrobeItems.filter(item => {
      // Already selected
      if (selectedItems.some(selected => selected.id === item.id)) return false;
      
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          item.name.toLowerCase().includes(query) ||
          item.color?.toLowerCase().includes(query) ||
          item.brand?.toLowerCase().includes(query) ||
          item.type.toLowerCase().includes(query);
        if (!matchesSearch) return false;
      }
      
      // Category filter
      if (selectedCategory !== 'all' && item.type !== selectedCategory) return false;
      
      // Color filter
      if (selectedColor !== 'all' && item.color?.toLowerCase() !== selectedColor) return false;
      
      // Filter out invalid images
      const hasValidImage = !item.imageUrl || 
        (!item.imageUrl.includes('via.placeholder.com') && 
         !(item.imageUrl.startsWith('data:image/') && item.imageUrl.length < 100));
      
      return hasValidImage;
    });
  }, [wardrobeItems, selectedItems, searchQuery, selectedCategory, selectedColor]);

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

  const handleProceedToDetails = () => {
    if (selectedItems.length === 0) {
      toast({
        title: "Add items first",
        description: "Please add at least one item to your outfit.",
        variant: "destructive"
      });
      return;
    }
    setCurrentStep('details');
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

    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please sign in to save your outfit.",
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
        user_id: user.uid,
        items: selectedItems.map(item => ({
          id: item.id,
          name: item.name,
          category: item.type,
          color: item.color,
          imageUrl: item.imageUrl,
          user_id: item.user_id
        }))
      };

      console.log('🎨 [CreateOutfit] Saving outfit:', { 
        name: outfitData.name, 
        itemCount: outfitData.items.length,
        user_id: outfitData.user_id 
      });

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

  const getCategoryCount = (category: string) => {
    return selectedItems.filter(item => item.type === category).length;
  };

  // Step 1: Build Outfit - Visual item selection
  if (currentStep === 'build') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-stone-950 dark:via-neutral-950 dark:to-stone-950">
        <Navigation />
        
        {/* Header */}
        <div className="sticky top-0 z-40 glass-navbar px-4 py-4 border-b border-stone-200 dark:border-stone-700">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.back()}
                className="text-stone-700 hover:text-stone-900 dark:text-stone-300 dark:hover:text-stone-100"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="h-8 w-px bg-stone-300 dark:bg-stone-600" />
              <div>
                <h1 className="text-xl font-serif font-bold text-stone-900 dark:text-stone-100">
                  Build Your Outfit
                </h1>
                <p className="text-xs text-stone-600 dark:text-stone-400">
                  Select items from your wardrobe
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="text-sm text-stone-600 dark:text-stone-400">
                {selectedItems.length} / 10 items
              </div>
              <Button
                onClick={handleProceedToDetails}
                disabled={selectedItems.length === 0}
                className="bg-stone-900 hover:bg-stone-800 text-white rounded-full font-medium shadow-lg"
              >
                Continue
                <ChevronRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Sidebar: Outfit Preview */}
            <div className="lg:col-span-1">
              <div className="sticky top-24">
                <Card className="glass-card">
                  <CardHeader>
                    <CardTitle className="text-lg font-serif">Your Outfit</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {selectedItems.length === 0 ? (
                      <div className="text-center py-12 text-stone-500">
                        <Sparkles className="h-12 w-12 mx-auto mb-3 text-stone-300" />
                        <p className="text-sm font-medium mb-1">Start Building</p>
                        <p className="text-xs">Select items to create your outfit</p>
                      </div>
                    ) : (
                      <>
                        {/* Outfit Canvas - Organized by Category */}
                        <div className="space-y-3">
                          {(() => {
                            const mainCategories = ['outerwear', 'top', 'bottom', 'shoes', 'accessories', 'bag', 'jewelry'];
                            const displayedItemIds = new Set<string>();
                            
                            return (
                              <>
                                {/* Main categories */}
                                {mainCategories.map(category => {
                                  const categoryItems = selectedItems.filter(item => item.type === category);
                                  if (categoryItems.length === 0) return null;
                                  
                                  categoryItems.forEach(item => displayedItemIds.add(item.id));
                                  
                                  return (
                                    <div key={category} className="space-y-2">
                                      <div className="flex items-center gap-2 text-xs font-medium text-stone-600 dark:text-stone-400 uppercase">
                                        {getItemIcon(category)}
                                        <span>{category}</span>
                                      </div>
                                      <div className="space-y-2">
                                        {categoryItems.map(item => (
                                          <div
                                            key={item.id}
                                            className="group relative flex items-center gap-3 p-3 bg-white dark:bg-stone-800 rounded-lg border-2 border-stone-200 dark:border-stone-700 hover:border-stone-900 dark:hover:border-stone-400 transition-all"
                                          >
                                            {item.imageUrl ? (
                                              <img
                                                src={item.imageUrl}
                                                alt={item.name}
                                                className="w-16 h-16 rounded-lg object-cover"
                                              />
                                            ) : (
                                              <div className="w-16 h-16 bg-stone-100 dark:bg-stone-700 rounded-lg flex items-center justify-center">
                                                {getItemIcon(item.type)}
                                              </div>
                                            )}
                                            <div className="flex-1 min-w-0">
                                              <p className="text-sm font-medium text-stone-900 dark:text-stone-100 truncate">
                                                {item.name}
                                              </p>
                                              <p className="text-xs text-stone-500 capitalize">
                                                {item.color}
                                              </p>
                                            </div>
                                            <Button
                                              variant="ghost"
                                              size="sm"
                                              onClick={() => handleRemoveItem(item.id)}
                                              className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 text-stone-400 hover:text-red-600"
                                            >
                                              <X className="h-4 w-4" />
                                            </Button>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  );
                                })}
                                
                                {/* Other categories (catch-all for items not in main categories) */}
                                {(() => {
                                  const otherItems = selectedItems.filter(item => !displayedItemIds.has(item.id));
                                  if (otherItems.length === 0) return null;
                                  
                                  return (
                                    <div className="space-y-2">
                                      <div className="flex items-center gap-2 text-xs font-medium text-stone-600 dark:text-stone-400 uppercase">
                                        {getItemIcon('other')}
                                        <span>Other Items</span>
                                      </div>
                                      <div className="space-y-2">
                                        {otherItems.map(item => (
                                          <div
                                            key={item.id}
                                            className="group relative flex items-center gap-3 p-3 bg-white dark:bg-stone-800 rounded-lg border-2 border-stone-200 dark:border-stone-700 hover:border-stone-900 dark:hover:border-stone-400 transition-all"
                                          >
                                            {item.imageUrl ? (
                                              <img
                                                src={item.imageUrl}
                                                alt={item.name}
                                                className="w-16 h-16 rounded-lg object-cover"
                                              />
                                            ) : (
                                              <div className="w-16 h-16 bg-stone-100 dark:bg-stone-700 rounded-lg flex items-center justify-center">
                                                {getItemIcon(item.type)}
                                              </div>
                                            )}
                                            <div className="flex-1 min-w-0">
                                              <p className="text-sm font-medium text-stone-900 dark:text-stone-100 truncate">
                                                {item.name}
                                              </p>
                                              <p className="text-xs text-stone-500 capitalize">
                                                {item.type} • {item.color}
                                              </p>
                                            </div>
                                            <Button
                                              variant="ghost"
                                              size="sm"
                                              onClick={() => handleRemoveItem(item.id)}
                                              className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8 p-0 text-stone-400 hover:text-red-600"
                                            >
                                              <X className="h-4 w-4" />
                                            </Button>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  );
                                })()}
                              </>
                            );
                          })()}
                        </div>

                        {/* Quick Actions */}
                        <div className="pt-4 border-t border-stone-200 dark:border-stone-700">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setSelectedItems([])}
                            className="w-full text-stone-600 hover:text-red-600"
                          >
                            <X className="h-3 w-3 mr-2" />
                            Clear All
                          </Button>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>

                {/* Quick Tip */}
                <Card className="glass-card mt-4">
                  <CardContent className="p-4">
                    <div className="flex gap-3">
                      <Info className="h-5 w-5 text-stone-400 flex-shrink-0 mt-0.5" />
                      <div className="text-xs text-stone-600 dark:text-stone-400">
                        <p className="font-medium mb-1">Pro Tip</p>
                        <p>Build a complete outfit by selecting items from different categories. Mix and match to find your perfect look!</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Right Content: Item Browser */}
            <div className="lg:col-span-2">
              <Card className="glass-card">
                <CardHeader className="space-y-4">
                  {/* Search and Filters */}
                  <div className="space-y-3">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-stone-400" />
                      <Input
                        placeholder="Search your wardrobe..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10 bg-white dark:bg-stone-800"
                      />
                    </div>

                    {/* Category Filter Pills */}
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant={selectedCategory === 'all' ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setSelectedCategory('all')}
                        className="h-8 px-3 text-xs rounded-full"
                      >
                        All Items
                        <Badge variant="secondary" className="ml-2 h-5 px-2">
                          {filteredItems.length}
                        </Badge>
                      </Button>
                      {Object.entries(itemsByCategory).map(([category, items]) => {
                        if (items.length === 0) return null;
                        const count = getCategoryCount(category);
                        return (
                          <Button
                            key={category}
                            variant={selectedCategory === category ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setSelectedCategory(category)}
                            className="h-8 px-3 text-xs rounded-full capitalize"
                          >
                            {getItemIcon(category)}
                            <span className="ml-1">{category}</span>
                            {count > 0 && (
                              <Badge variant="secondary" className="ml-2 h-5 px-2 bg-green-100 text-green-700">
                                {count}
                              </Badge>
                            )}
                          </Button>
                        );
                      })}
                    </div>

                    {/* Color Filter */}
                    {availableColors.length > 0 && (
                      <div className="flex items-center gap-2 overflow-x-auto pb-2">
                        <Filter className="h-4 w-4 text-stone-400 flex-shrink-0" />
                        <Button
                          variant={selectedColor === 'all' ? 'default' : 'outline'}
                          size="sm"
                          onClick={() => setSelectedColor('all')}
                          className="h-7 px-2 text-xs flex-shrink-0"
                        >
                          All Colors
                        </Button>
                        {availableColors.slice(0, 10).map(color => (
                          <Button
                            key={color}
                            variant={selectedColor === color ? 'default' : 'outline'}
                            size="sm"
                            onClick={() => setSelectedColor(color)}
                            className="h-7 px-2 text-xs capitalize flex-shrink-0"
                          >
                            {color}
                          </Button>
                        ))}
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent>
                  {wardrobeLoading ? (
                    <div className="flex items-center justify-center py-20">
                      <Loader2 className="h-8 w-8 animate-spin text-stone-400" />
                    </div>
                  ) : filteredItems.length === 0 ? (
                    <div className="text-center py-20 text-stone-500">
                      <Shirt className="h-12 w-12 mx-auto mb-3 text-stone-300" />
                      <p className="text-sm font-medium mb-1">No items found</p>
                      <p className="text-xs">
                        {searchQuery || selectedCategory !== 'all' || selectedColor !== 'all'
                          ? 'Try adjusting your filters'
                          : 'Add items to your wardrobe first'}
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                      {filteredItems.map(item => (
                        <button
                          key={item.id}
                          onClick={() => handleAddItem(item)}
                          disabled={selectedItems.length >= 10}
                          className="group relative bg-white dark:bg-stone-800 rounded-lg border-2 border-stone-200 dark:border-stone-700 hover:border-stone-900 dark:hover:border-stone-400 transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden"
                        >
                          {/* Image */}
                          <div className="aspect-square relative bg-stone-100 dark:bg-stone-700">
                            {item.imageUrl ? (
                              <img
                                src={item.imageUrl}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center">
                                {getItemIcon(item.type)}
                              </div>
                            )}
                            {/* Hover Overlay */}
                            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all flex items-center justify-center">
                              <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-white dark:bg-stone-900 rounded-full p-2 shadow-lg">
                                <Plus className="h-5 w-5 text-stone-900 dark:text-white" />
                              </div>
                            </div>
                          </div>
                          
                          {/* Info */}
                          <div className="p-2 text-left">
                            <p className="text-xs font-medium text-stone-900 dark:text-stone-100 truncate">
                              {item.name}
                            </p>
                            <p className="text-xs text-stone-500 capitalize">
                              {item.color}
                            </p>
                          </div>
                        </button>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Add Details
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-stone-950 dark:via-neutral-950 dark:to-stone-950">
      <Navigation />
      
      {/* Header */}
      <div className="glass-navbar px-4 py-6">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setCurrentStep('build')}
              className="text-stone-700 hover:text-stone-900 dark:text-stone-300 dark:hover:text-stone-100"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Building
            </Button>
          </div>
          <div className="flex items-center gap-4">
            <div className="p-3 bg-stone-900 dark:bg-stone-100 rounded-full">
              <Sparkles className="h-6 w-6 text-white dark:text-stone-900" />
            </div>
            <div>
              <h1 className="text-3xl font-serif font-bold text-stone-900 dark:text-stone-100">
                Name Your Outfit
              </h1>
              <p className="text-stone-600 dark:text-stone-400 text-sm mt-1">
                Add details to help you find and remember this outfit later
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Outfit Preview (Compact) */}
          <div className="lg:col-span-1">
            <Card className="glass-card sticky top-24">
              <CardHeader>
                <CardTitle className="text-sm font-medium text-stone-600">Your Outfit</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {selectedItems.slice(0, 4).map(item => (
                    <div key={item.id} className="aspect-square rounded-lg overflow-hidden bg-stone-100 dark:bg-stone-700">
                      {item.imageUrl ? (
                        <img
                          src={item.imageUrl}
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          {getItemIcon(item.type)}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                {selectedItems.length > 4 && (
                  <p className="text-xs text-stone-500 text-center mt-2">
                    +{selectedItems.length - 4} more items
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Details Form */}
          <div className="lg:col-span-2">
            <Card className="glass-card">
              <CardContent className="pt-6 space-y-6">
                {/* Outfit Name */}
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-base font-medium">
                    Outfit Name <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="name"
                    placeholder="e.g., Summer Casual Look, Date Night Outfit..."
                    value={outfitName}
                    onChange={(e) => setOutfitName(e.target.value)}
                    className="text-lg"
                    autoFocus
                  />
                </div>

                {/* Occasion & Style */}
                <div className="grid grid-cols-2 gap-4">
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
                </div>

                {/* Description */}
                <div className="space-y-2">
                  <Label htmlFor="description">Description (Optional)</Label>
                  <Textarea
                    id="description"
                    placeholder="What makes this outfit special? When would you wear it?"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                  />
                </div>

                {/* Notes */}
                <div className="space-y-2">
                  <Label htmlFor="notes">Notes (Optional)</Label>
                  <Textarea
                    id="notes"
                    placeholder="Any additional notes or styling tips..."
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    rows={2}
                  />
                </div>

                {/* Actions */}
                <div className="flex justify-end gap-3 pt-4">
                  <Button
                    variant="outline"
                    onClick={() => setCurrentStep('build')}
                    disabled={saving}
                  >
                    Back
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={saving || !outfitName.trim()}
                    className="bg-stone-900 hover:bg-stone-800 text-white px-8"
                  >
                    {saving ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Save Outfit
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
