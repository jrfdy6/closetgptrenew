"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useWardrobe } from '@/hooks/useWardrobe';
import { PageLoadingSkeleton } from '@/components/ui/loading-states';
import { ClothingItem } from '../../types/wardrobe';
import { useToast } from '@/components/ui/use-toast';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, RefreshCw, Trash2, Plus, X, Search, Filter, Upload, Image as ImageIcon, Sparkles, Target, Palette, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { migrateWardrobeItems } from '@/lib/firebase/wardrobeService';

import Image from 'next/image';
import { ref, getDownloadURL, deleteObject } from 'firebase/storage';
import { storage } from '@/lib/firebase/config';
import { useRouter } from 'next/navigation';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { deleteDoc } from 'firebase/firestore';
import { doc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { authenticatedFetch } from '@/lib/utils/auth';
import { useWeather } from "@/hooks/useWeather";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WardrobeItem } from '@/types/wardrobe';
import WardrobeGrid from '@/components/WardrobeGrid';
import { 
  SkeletonLoader,
  TextSkeleton,
  InlineLoading 
} from '@/components/ui/loading-states';
import {
  EmptyState,
  ErrorState,
  NoResults
} from '@/components/ui/fallback-states';
import {
  Heading,
  Text,
  Container
} from '@/components/ui/typography';

const OCCASIONS = [
  "Casual",
  "Business Casual",
  "Formal",
  "Gala",
  "Party",
  "Date Night",
  "Work",
  "Interview",
  "Brunch",
  "Wedding Guest",
  "Cocktail",
  "Travel",
  "Airport",
  "Loungewear",
  "Beach",
  "Vacation",
  "Festival",
  "Rainy Day",
  "Snow Day",
  "Hot Weather",
  "Cold Weather",
  "Night Out",
  "Athletic / Gym",
  "School",
  "Holiday",
  "Concert",
  "Errands",
  "Chilly Evening",
  "Museum / Gallery",
  "First Date",
  "Business Formal",
  "Funeral / Memorial",
  "Fashion Event",
  "Outdoor Gathering"
];

const MOODS = ["energetic", "relaxed", "confident", "playful", "elegant"];

const STYLES = [
  "Dark Academia",
  "Old Money",
  "Streetwear",
  "Y2K",
  "Minimalist",
  "Boho",
  "Preppy",
  "Grunge",
  "Classic",
  "Techwear",
  "Androgynous",
  "Coastal Chic",
  "Business Casual",
  "Avant-Garde",
  "Cottagecore",
  "Edgy",
  "Athleisure",
  "Casual Cool",
  "Romantic",
  "Artsy"
];

export default function WardrobePage() {
  const { user, loading: authLoading } = useAuth();
  const { wardrobe, loading, error, removeItem, loadItems } = useWardrobe();
  const { weather, loading: weatherLoading } = useWeather();
  const [searchQuery, setSearchQuery] = useState('');
  const { toast } = useToast();
  const [isMigrating, setIsMigrating] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [itemToDelete, setItemToDelete] = useState<WardrobeItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const MAX_RETRIES = 3;
  const [newTag, setNewTag] = useState<string>('');
  const [itemTags, setItemTags] = useState<Record<string, string[]>>({});
  const router = useRouter();
  
  // Outfit generation modal state
  const [showOutfitModal, setShowOutfitModal] = useState(false);
  const [selectedBaseItem, setSelectedBaseItem] = useState<WardrobeItem | null>(null);
  const [outfitFormData, setOutfitFormData] = useState({
    occasion: "",
    mood: "",
    style: "",
  });
  const [isGeneratingOutfit, setIsGeneratingOutfit] = useState(false);

  // Add after other useState hooks
  const [retryCount, setRetryCount] = useState<Record<string, number>>({});

  // Filter state
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [filters, setFilters] = useState({
    type: '',
    color: '',
    season: '',
    style: '',
    occasion: '',
    wearCount: ''
  });

  useEffect(() => {
    console.log('WardrobePage state:', {
      authLoading,
      loading,
      user: user?.uid,
      itemsCount: wardrobe?.length,
      error
    });
  }, [authLoading, loading, user, wardrobe, error]);

  // Listen for wardrobe data changes and refresh
  useEffect(() => {
    const handleWardrobeDataChanged = () => {
      console.log('Wardrobe data changed event received, refreshing...');
      if (user) {
        loadItems();
      }
    };

    window.addEventListener('wardrobeDataChanged', handleWardrobeDataChanged);
    
    return () => {
      window.removeEventListener('wardrobeDataChanged', handleWardrobeDataChanged);
    };
  }, [user, loadItems]);

  const handleMigrate = async () => {
    if (!user) return;

    setIsMigrating(true);
    try {
      await migrateWardrobeItems(user.uid);
      toast({
        title: 'Success',
        description: 'Wardrobe items have been updated to the new schema.',
      });
    } catch (err) {
      console.error('Error migrating wardrobe items:', err);
      toast({
        title: 'Error',
        description: 'Failed to update wardrobe items. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsMigrating(false);
    }
  };

  const handleRefresh = async () => {
    if (!user) return;

    setIsRefreshing(true);
    try {
      await loadItems();
      toast({
        title: 'Success',
        description: 'Wardrobe refreshed successfully.',
      });
    } catch (err) {
      console.error('Error refreshing wardrobe:', err);
      toast({
        title: 'Error',
        description: 'Failed to refresh wardrobe. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleImageError = (itemId: string, itemName: string, e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    const target = e.target as HTMLImageElement;
    const currentRetries = retryCount[itemId] || 0;
    
    console.log(`Image load error for ${itemName}:`, {
      itemId,
      currentSource: target.src,
      naturalWidth: target.naturalWidth,
      naturalHeight: target.naturalHeight,
      retryCount: currentRetries,
      timestamp: new Date().toISOString()
    });

    if (currentRetries < MAX_RETRIES) {
      // Increment retry count
      setRetryCount(prev => ({ ...prev, [itemId]: currentRetries + 1 }));
      // Clear the error state to trigger a retry
      setImageErrors(prev => ({ ...prev, [itemId]: false }));
      
      // Force a re-render of the image with a cache-busting parameter
      const img = target as HTMLImageElement;
      if (img.src && storage && user?.uid) {
        try {
          // Extract the path from the current image URL
          const url = new URL(img.src);
          const pathMatch = url.pathname.match(/\/o\/(.+?)(?:\?|$)/);
          if (!pathMatch) {
            throw new Error('Could not extract path from image URL');
          }
          const decodedPath = decodeURIComponent(pathMatch[1]);
          
          // Get a fresh download URL using the extracted path
          const storageRef = ref(storage, decodedPath);
          getDownloadURL(storageRef).then(newUrl => {
            // Update the image source with the fresh URL
            img.src = newUrl;
          }).catch(err => {
            console.error('Failed to get fresh download URL:', err);
            setImageErrors(prev => ({ ...prev, [itemId]: true }));
          });
        } catch (err) {
          console.error('Error processing image retry:', err);
          setImageErrors(prev => ({ ...prev, [itemId]: true }));
        }
      } else {
        setImageErrors(prev => ({ ...prev, [itemId]: true }));
      }
    } else {
      console.log(`Max retries reached for ${itemName}, marking as error`);
      setImageErrors(prev => ({ ...prev, [itemId]: true }));
    }
  };

  const handleDeleteItem = async (item: WardrobeItem) => {
    if (!user) return;

    console.log('Starting deletion for item:', {
      id: item.id,
      name: item.name,
      type: item.type,
      wardrobeLength: wardrobe?.length
    });
    
    setIsDeleting(true);
    try {
      // Use the removeItem function from useWardrobe hook
      const result = await removeItem(item.id);
      
      console.log('Remove item result:', result);
      console.log('Wardrobe after deletion:', wardrobe?.length);
      
      if (result.success) {
        console.log('Item successfully deleted from database');
        // Force refresh the wardrobe data
        await loadItems();
        toast({
          title: 'Success',
          description: 'Item deleted successfully.',
        });
      } else {
        console.error('Failed to delete item:', result.error);
        throw new Error(result.error || 'Failed to delete item');
      }
    } catch (err) {
      console.error('Error deleting item:', err);
      toast({
        title: 'Error',
        description: 'Failed to delete item. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsDeleting(false);
      setItemToDelete(null);
    }
  };

  const handleAddTag = (itemId: string) => {
    if (!newTag.trim()) return;
    
    setItemTags(prev => ({
      ...prev,
      [itemId]: [...(prev[itemId] || []), newTag.trim()]
    }));
    setNewTag('');
  };

  const handleRemoveTag = (itemId: string, tagToRemove: string) => {
    setItemTags(prev => ({
      ...prev,
      [itemId]: (prev[itemId] || []).filter(tag => tag !== tagToRemove)
    }));
  };

  const handleGenerateOutfit = (baseItem: WardrobeItem) => {
    console.log('🔍 DEBUG: handleGenerateOutfit called with baseItem:', {
      id: baseItem.id,
      name: baseItem.name,
      type: baseItem.type,
      color: baseItem.color,
      hasImageUrl: !!baseItem.imageUrl,
      hasTags: !!baseItem.tags,
      hasSeason: !!baseItem.season,
      hasStyle: !!baseItem.style,
      hasMetadata: !!baseItem.metadata,
      fullItem: baseItem
    });
    
    setSelectedBaseItem(baseItem);
    setShowOutfitModal(true);
  };

  const handleOutfitGeneration = async () => {
    console.log('🔍 DEBUG: handleOutfitGeneration called');
    console.log('🔍 DEBUG: selectedBaseItem:', selectedBaseItem);
    console.log('🔍 DEBUG: outfitFormData:', outfitFormData);
    
    if (!selectedBaseItem) {
      console.error('❌ DEBUG: No selectedBaseItem found');
      return;
    }

    setIsGeneratingOutfit(true);
    try {
      // Validate base item has required fields
      const requiredFields = ['id', 'name', 'type', 'color', 'imageUrl'];
      const missingFields = requiredFields.filter(field => !selectedBaseItem[field as keyof WardrobeItem]);
      
      if (missingFields.length > 0) {
        console.warn('⚠️ DEBUG: Base item missing required fields:', missingFields);
        console.log('🔍 DEBUG: Base item structure:', selectedBaseItem);
      } else {
        console.log('✅ DEBUG: Base item has all required fields');
      }

      // Store the base item and form data in sessionStorage for the outfit generation page
      const baseItemString = JSON.stringify(selectedBaseItem);
      const formDataString = JSON.stringify(outfitFormData);
      
      console.log('🔍 DEBUG: Storing in sessionStorage:');
      console.log('  - baseItem length:', baseItemString.length);
      console.log('  - formData length:', formDataString.length);
      
      sessionStorage.setItem('baseItem', baseItemString);
      sessionStorage.setItem('outfitFormData', formDataString);
      
      console.log('✅ DEBUG: Successfully stored data in sessionStorage');
      console.log('🔍 DEBUG: Navigating to /outfits/generate');
      
      // Navigate to outfit generation page
      router.push('/outfits/generate');
    } catch (err) {
      console.error('❌ DEBUG: Error in handleOutfitGeneration:', err);
      toast({
        title: 'Error',
        description: 'Failed to navigate to outfit generation.',
        variant: 'destructive',
      });
    } finally {
      setIsGeneratingOutfit(false);
      setShowOutfitModal(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setFilters({ type: '', color: '', season: '', style: '', occasion: '', wearCount: '' });
  };

  // Filter items based on search query and filters
  const filteredItems = wardrobe?.filter(item => {
    // Search query filter
    const matchesSearch = !searchQuery || 
      item.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.type?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.color?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.metadata?.brand?.toLowerCase().includes(searchQuery.toLowerCase());

    // Type filter
    const matchesType = !filters.type || item.type === filters.type;

    // Color filter
    const matchesColor = !filters.color || 
      item.color?.toLowerCase().includes(filters.color.toLowerCase());

    // Season filter
    const matchesSeason = !filters.season || 
      item.season?.includes(filters.season as any);

    // Style filter
    const matchesStyle = !filters.style || 
      item.style?.some((s: string) => s.toLowerCase().includes(filters.style.toLowerCase()));

    // Occasion filter
    const matchesOccasion = !filters.occasion || 
      item.occasion?.some((o: string) => o.toLowerCase().includes(filters.occasion.toLowerCase()));

    // Wear count filter
    const matchesWearCount = !filters.wearCount || (() => {
      const wearCount = item.wearCount || 0;
      const filterValue = parseInt(filters.wearCount);
      
      if (filters.wearCount === '0') {
        return wearCount === 0;
      } else if (filters.wearCount === '1') {
        return wearCount === 1;
      } else if (filters.wearCount === '2') {
        return wearCount >= 2;
      } else if (filters.wearCount === '5') {
        return wearCount >= 5;
      } else if (filters.wearCount === '10') {
        return wearCount >= 10;
      }
      
      return true;
    })();

    return matchesSearch && matchesType && matchesColor && matchesSeason && matchesStyle && matchesOccasion && matchesWearCount;
  }) || [];

  // Loading state
  if (authLoading || loading) {
    return (
      <div className="container-readable space-section py-8">
        <PageLoadingSkeleton 
          showHero={true}
          showStats={false}
          showContent={true}
        />
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <Container maxWidth="full" padding="lg">
        <ErrorState 
          error={error} 
          onRetry={() => window.location.reload()}
        />
      </Container>
    );
  }

  // Empty state
  if (!wardrobe || wardrobe.length === 0) {
    return (
      <Container maxWidth="full" padding="lg">
        <EmptyState
          icon={ImageIcon}
          title="Your wardrobe is empty"
          description="Start building your digital wardrobe by adding your favorite clothing items. We'll help you organize and create amazing outfits."
          actionText="Add your first item"
          onAction={() => router.push('/wardrobe/add')}
          secondaryActionText="Learn how it works"
          onSecondaryAction={() => window.open('/help', '_blank')}
        />
      </Container>
    );
  }

  return (
    <Container maxWidth="full" padding="lg">
      <div className="container-readable space-section py-8">
        {/* Hero Header */}
        <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Palette className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h1 className="text-2xl sm:text-hero text-foreground">My Wardrobe</h1>
            </div>
            <p className="text-secondary text-base sm:text-lg">
              {wardrobe.length} item{wardrobe.length !== 1 ? 's' : ''} in your collection
              {(() => {
                const totalWears = wardrobe.reduce((sum, item) => sum + (item.wearCount || 0), 0);
                const wornItems = wardrobe.filter(item => (item.wearCount || 0) > 0).length;
                return totalWears > 0 ? ` • ${totalWears} total wears • ${wornItems} items worn` : '';
              })()}
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
            <Button
              onClick={() => router.push('/wardrobe/add')}
              className="shadow-md hover:shadow-lg w-full sm:w-auto"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Item
            </Button>
            <Button
              onClick={() => router.push('/wardrobe/batch-upload')}
              variant="outline"
              className="shadow-md hover:shadow-lg w-full sm:w-auto"
            >
              <Upload className="w-4 h-4 mr-2" />
              Batch Upload
            </Button>
            <Button
              onClick={handleRefresh}
              disabled={isRefreshing}
              variant="outline"
              className="shadow-md hover:shadow-lg w-full sm:w-auto"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>

          </div>
        </div>
      </div>

        {/* Search and Filters */}
        <Card className="card-enhanced animate-fade-in stagger-2">
          <CardContent className="p-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search your wardrobe..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 shadow-sm"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="shadow-md hover:shadow-lg"
                  onClick={() => setShowFilterModal(true)}
                >
                  <Filter className="w-4 h-4 mr-2" />
                  Filter
                  {Object.values(filters).some(filter => filter !== '') && (
                    <span className="ml-2 w-2 h-2 bg-yellow-500 rounded-full"></span>
                  )}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>



        {/* Wardrobe Grid */}
        {searchQuery && filteredItems.length === 0 ? (
          <NoResults 
            searchQuery={searchQuery}
            onClearFilters={handleClearFilters}
            suggestions={['casual', 'formal', 'business', 'party']}
          />
        ) : (
          <WardrobeGrid
            items={filteredItems}
            loading={loading}
            error={error}
            onItemClick={(item) => router.push(`/wardrobe/edit/${item.id}`)}
            onGenerateOutfit={(item) => handleGenerateOutfit(item)}
            onDeleteItem={(item) => setItemToDelete(item)}
            onEditItem={(item) => router.push(`/wardrobe/edit/${item.id}`)}
            showActions={true}
          />
        )}

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={!!itemToDelete} onOpenChange={() => setItemToDelete(null)}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Delete Item</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to delete "{itemToDelete?.name}"? This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction
                onClick={() => itemToDelete && handleDeleteItem(itemToDelete)}
                disabled={isDeleting}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                {isDeleting ? (
                  <>
                    <InlineLoading message="Deleting..." />
                  </>
                ) : (
                  'Delete'
                )}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        {/* Outfit Generation Modal */}
        <Dialog open={showOutfitModal} onOpenChange={() => setShowOutfitModal(false)}>
          <DialogContent className="sm:max-w-[425px]">
            <DialogHeader>
              <DialogTitle>Generate Outfit</DialogTitle>
              <DialogDescription>
                Generate an outfit starting with "{selectedBaseItem?.name}".
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="occasion">Occasion</Label>
                <Select
                  value={outfitFormData.occasion}
                  onValueChange={(value) => setOutfitFormData(prev => ({ ...prev, occasion: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select an occasion" />
                  </SelectTrigger>
                  <SelectContent>
                    {OCCASIONS.map((occasion) => (
                      <SelectItem key={occasion} value={occasion}>
                        {occasion}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="mood">Mood</Label>
                <Select
                  value={outfitFormData.mood}
                  onValueChange={(value) => setOutfitFormData(prev => ({ ...prev, mood: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="How do you want to feel?" />
                  </SelectTrigger>
                  <SelectContent>
                    {MOODS.map((mood) => (
                      <SelectItem key={mood} value={mood}>
                        {mood.charAt(0).toUpperCase() + mood.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="style">Style</Label>
                <Select
                  value={outfitFormData.style}
                  onValueChange={(value) => setOutfitFormData(prev => ({ ...prev, style: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a style" />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((style) => (
                      <SelectItem key={style} value={style}>
                        {style}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowOutfitModal(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleOutfitGeneration}
                disabled={isGeneratingOutfit || !outfitFormData.occasion}
              >
                {isGeneratingOutfit ? (
                  <>
                    <InlineLoading message="Generating..." />
                  </>
                ) : (
                  'Generate Outfit'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        {/* Filter Modal */}
        <Dialog open={showFilterModal} onOpenChange={() => setShowFilterModal(false)}>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Filter Wardrobe</DialogTitle>
              <DialogDescription>
                Filter your wardrobe items by type, color, season, style, and occasion.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="type">Type</Label>
                <Select
                  value={filters.type}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, type: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Types</SelectItem>
                    <SelectItem value="shirt">Shirt</SelectItem>
                    <SelectItem value="pants">Pants</SelectItem>
                    <SelectItem value="dress">Dress</SelectItem>
                    <SelectItem value="jacket">Jacket</SelectItem>
                    <SelectItem value="sweater">Sweater</SelectItem>
                    <SelectItem value="shoes">Shoes</SelectItem>
                    <SelectItem value="accessory">Accessory</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="color">Color</Label>
                <Input
                  placeholder="Enter color (e.g., blue, red, black)"
                  value={filters.color}
                  onChange={(e) => setFilters(prev => ({ ...prev, color: e.target.value }))}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="season">Season</Label>
                <Select
                  value={filters.season}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, season: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a season" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Seasons</SelectItem>
                    <SelectItem value="spring">Spring</SelectItem>
                    <SelectItem value="summer">Summer</SelectItem>
                    <SelectItem value="fall">Fall</SelectItem>
                    <SelectItem value="winter">Winter</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Style</Label>
                <Select
                  value={filters.style}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, style: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Styles</SelectItem>
                    {STYLES.map((style) => (
                      <SelectItem key={style} value={style}>
                        {style}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="occasion">Occasion</Label>
                <Select
                  value={filters.occasion}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, occasion: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select an occasion" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Occasions</SelectItem>
                    {OCCASIONS.map((occasion) => (
                      <SelectItem key={occasion} value={occasion}>
                        {occasion}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="wearCount">Wear Count</Label>
                <Select
                  value={filters.wearCount}
                  onValueChange={(value) => setFilters(prev => ({ ...prev, wearCount: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Filter by wear count" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">All Items</SelectItem>
                    <SelectItem value="0">Never Worn</SelectItem>
                    <SelectItem value="1">Worn Once</SelectItem>
                    <SelectItem value="2">Worn 2+ Times</SelectItem>
                    <SelectItem value="5">Worn 5+ Times</SelectItem>
                    <SelectItem value="10">Worn 10+ Times</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button 
                variant="outline" 
                onClick={() => {
                  setFilters({ type: '', color: '', season: '', style: '', occasion: '', wearCount: '' });
                  setShowFilterModal(false);
                }}
              >
                Clear All
              </Button>
              <Button onClick={() => setShowFilterModal(false)}>
                Apply Filters
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </Container>
  );
} 