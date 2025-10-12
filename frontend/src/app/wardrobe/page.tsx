"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  Upload,
  X,
  Shirt,
  Sparkles,
  TrendingUp,
  Heart,
  Calendar,
  Zap,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { useFirebase } from "@/lib/firebase-context";
import BodyPositiveMessage from "@/components/BodyPositiveMessage";
import DiverseStyleInspiration from "@/components/DiverseStyleInspiration";
import { useWardrobe, type ClothingItem } from "@/lib/hooks/useWardrobe";
import { formatLastWorn } from "@/lib/utils/dateUtils";
import WardrobeItemDetails from "@/components/WardrobeItemDetails";
import dynamic from 'next/dynamic';

// Dynamically import components to avoid SSR issues
const WardrobeGrid = dynamic(() => import('@/components/WardrobeGrid'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading wardrobe...</div>
});

const BatchImageUpload = dynamic(() => import('@/components/BatchImageUpload'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading batch upload...</div>
});



export default function WardrobePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const {
    items: wardrobeItems,
    loading: wardrobeLoading,
    error: wardrobeError,
    filters,
    getFilteredItems,
    getUniqueValues,
    getFavorites,
    getRecentlyWorn,
    getUnwornItems,
    applyFilters,
    clearFilters,
    toggleFavorite,
    incrementWearCount,
    deleteItem,
    addItem,
    updateItem,
    refetch
  } = useWardrobe();

  const [activeTab, setActiveTab] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("all");
  const [selectedColor, setSelectedColor] = useState<string>("all");
  const [selectedSeason, setSelectedSeason] = useState<string>("all");
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  const [selectedItem, setSelectedItem] = useState<ClothingItem | null>(null);
  const [showItemDetails, setShowItemDetails] = useState(false);

  // Apply filters when they change
  useEffect(() => {
    const newFilters = {
      type: selectedType !== 'all' ? selectedType : undefined,
      color: selectedColor !== 'all' ? selectedColor : undefined,
      season: selectedSeason !== 'all' ? selectedSeason : undefined,
      search: searchQuery || undefined
    };
    applyFilters(newFilters);
  }, [selectedType, selectedColor, selectedSeason, searchQuery, applyFilters]);

  // Listen for outfit marked as worn events to refresh wardrobe data
  useEffect(() => {
    const handleOutfitMarkedAsWorn = (event: CustomEvent) => {
      refetch();
    };

    window.addEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    
    return () => {
      window.removeEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    };
  }, [refetch]);

  // Get filtered items based on active tab
  const getCurrentItems = () => {
    const filtered = getFilteredItems();
    
    switch (activeTab) {
      case 'favorites':
        return filtered.filter(item => item.favorite);
      case 'recent':
        return getRecentlyWorn().filter(item => 
          filtered.some(f => f.id === item.id)
        );
      case 'unworn':
        return getUnwornItems().filter(item => 
          filtered.some(f => f.id === item.id)
        );
      default:
        return filtered;
    }
  };

  const currentItems = getCurrentItems();

  // Handle search
  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  // Handle type filter
  const handleTypeFilter = (type: string) => {
    setSelectedType(type);
  };

  // Handle color filter
  const handleColorFilter = (color: string) => {
    setSelectedColor(color);
  };

  // Handle season filter
  const handleSeasonFilter = (season: string) => {
    setSelectedSeason(season);
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSearchQuery("");
    setSelectedType("all");
    setSelectedColor("all");
    setSelectedSeason("all");
    clearFilters();
  };

  // Handle favorite toggle
  const handleToggleFavorite = async (itemId: string) => {
    try {
      await toggleFavorite(itemId);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  // Test button click

  // Handle wear count increment
  const handleWearIncrement = async (itemId: string) => {
    try {
      await incrementWearCount(itemId);
    } catch (error) {
      console.error('Failed to increment wear count:', error);
    }
  };

  // Handle item deletion
  const handleDeleteItem = async (itemId: string) => {
    if (confirm('Are you sure you want to delete this item?')) {
      try {
        await deleteItem(itemId);
        setShowItemDetails(false);
        setSelectedItem(null);
      } catch (error) {
        console.error('Failed to delete item:', error);
      }
    }
  };

  // Handle item update
  const handleUpdateItem = async (itemId: string, updates: Partial<ClothingItem>) => {
    try {
      console.log('Updating item:', itemId, updates);
      await updateItem(itemId, updates);
      console.log('Item updated successfully');
    } catch (error) {
      console.error('Failed to update item:', error);
      throw error;
    }
  };

  // Handle item click to show details
  const handleItemClick = (item: ClothingItem) => {
    console.log('🔍 [WardrobePage] Item clicked:', item);
    setSelectedItem(item);
    setShowItemDetails(true);
  };

  // Handle outfit generation with base item - ID-based approach
  const handleGenerateOutfitWithBaseItem = (baseItem: any) => {
    
    // Pass only the ID - much cleaner and scalable
    router.push(`/outfits/generate?baseItemId=${baseItem.id}`);
  };

  // Get type icon
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'jacket': return '🧥';
      case 'shirt': return '👕';
      case 'pants': return '👖';
      case 'dress': return '👗';
      case 'shoes': return '👟';
      case 'accessory': return '💍';
      default: return '👕';
    }
  };

  // Get color badge styling
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
      'gray': 'bg-gray-500 text-white'
    };
    
    return colorMap[color] || 'bg-gray-200 text-gray-700';
  };

  // Loading state
  if (authLoading || wardrobeLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-4" />
            <p className="text-gray-600 dark:text-gray-400">Loading your wardrobe...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (wardrobeError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <AlertCircle className="w-8 h-8 text-red-600 mx-auto mb-4" />
            <p className="text-red-600 mb-4">Error loading wardrobe</p>
            <p className="text-gray-600 dark:text-gray-400 mb-4">{wardrobeError}</p>
            <Button onClick={refetch} variant="outline">
              <RefreshCw className="w-4 h-4 mr-2" />
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Header with Glass Effect */}
      <div className="glass-navbar px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
            <div>
              <h1 className="text-4xl font-serif font-bold text-stone-900 dark:text-stone-100 mb-4">My Wardrobe</h1>
              <p className="text-stone-600 dark:text-stone-400 font-light text-lg">
                {wardrobeItems.length} items • {getFavorites().length} favorites
              </p>
              <BodyPositiveMessage variant="wardrobe" className="mt-6" />
            </div>
            
            <div className="flex gap-4">
              <Button 
                onClick={() => setShowBatchUpload(true)}
                className="glass-button-primary px-8 py-3 rounded-full font-medium glass-transition hover:scale-105"
              >
                <Upload className="w-5 h-5 mr-3" />
                Add Items with AI
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        

        {/* Filters and Search */}
        <Card className="mb-8 glass-card">
          <CardContent className="pt-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search items..."
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Type Filter */}
              <Select value={selectedType} onValueChange={handleTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {getUniqueValues('type').map(type => (
                    <SelectItem key={type} value={type}>
                      {getTypeIcon(type)} {type.charAt(0).toUpperCase() + type.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Color Filter */}
              <Select value={selectedColor} onValueChange={handleColorFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Colors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Colors</SelectItem>
                  {getUniqueValues('color').map(color => (
                    <SelectItem key={color} value={color}>
                      <span className={`inline-block w-3 h-3 rounded-full mr-2 ${getColorBadge(color)}`}></span>
                      {color.charAt(0).toUpperCase() + color.slice(1)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Season Filter */}
              <Select value={selectedSeason} onValueChange={handleSeasonFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="All Seasons" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Seasons</SelectItem>
                  <SelectItem value="spring">🌸 Spring</SelectItem>
                  <SelectItem value="summer">☀️ Summer</SelectItem>
                  <SelectItem value="fall">🍂 Fall</SelectItem>
                  <SelectItem value="winter">❄️ Winter</SelectItem>
                </SelectContent>
              </Select>

              {/* View Mode Toggle */}
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === "grid" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                >
                  <Grid3X3 className="w-4 h-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                >
                  <List className="w-4 h-4" />
                </Button>
              </div>

              {/* Clear Filters */}
              {(selectedType !== 'all' || selectedColor !== 'all' || selectedSeason !== 'all' || searchQuery) && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClearFilters}
                  className="text-gray-600 hover:text-gray-800"
                >
                  <X className="w-4 h-4 mr-2" />
                  Clear
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">All Items</TabsTrigger>
            <TabsTrigger value="favorites">
              <Heart className="w-4 h-4 mr-2" />
              Favorites
            </TabsTrigger>
            <TabsTrigger value="recent">
              <Calendar className="w-4 h-4 mr-2" />
              Recently Worn
            </TabsTrigger>
            <TabsTrigger value="unworn">
              <TrendingUp className="w-4 h-4 mr-2" />
              Unworn
            </TabsTrigger>
            <TabsTrigger value="inspiration">
              <Sparkles className="w-4 h-4 mr-2" />
              Style Inspiration
            </TabsTrigger>
          </TabsList>

          <TabsContent value="all" className="mt-6">
            {currentItems.length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <Shirt className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No items found</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    {wardrobeItems.length === 0 
                      ? "Your wardrobe is empty. Add your first item to get started!"
                      : "Try adjusting your filters or add some new items to your wardrobe"
                    }
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Showing {currentItems.length} of {wardrobeItems.length} items
                  </p>
        <div className="flex gap-3">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push('/outfits/generate')}
            className="group hover:bg-purple-50 hover:border-purple-300 hover:text-purple-700 transition-all duration-200"
          >
            <Zap className="w-4 h-4 mr-2 group-hover:animate-pulse" />
            Generate Outfit
          </Button>
        </div>
                </div>
                
                {viewMode === "grid" ? (
                  <WardrobeGrid 
                    items={currentItems}
                    loading={false}
                    onItemClick={handleItemClick}
                    onGenerateOutfit={(item) => handleGenerateOutfitWithBaseItem(item)}
                    onToggleFavorite={handleToggleFavorite}
                    onDeleteItem={deleteItem}
                    showActions={true}
                  />
                ) : (
                  <div className="space-y-3">
                    {currentItems.map((item) => (
                      <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleItemClick(item)}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                              <img
                                src={item.imageUrl}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                                  {item.name}
                                </h3>
                                {item.favorite && (
                                  <Heart className="w-4 h-4 text-red-500 fill-current" />
                                )}
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <span>{getTypeIcon(item.type)} {item.type}</span>
                                <span>•</span>
                                <Badge className={`text-xs ${getColorBadge(item.color)}`}>
                                  {item.color}
                                </Badge>
                                <span>•</span>
                                <span>Worn {item.wearCount} times</span>
                              </div>
                              
                              {item.style && item.style.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {item.style.map((style, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {style}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex gap-2 flex-shrink-0">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleWearIncrement(item.id)}
                              >
                                <Sparkles className="w-4 h-4 mr-2" />
                                Worn
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleToggleFavorite(item.id)}
                              >
                                <Heart className={`w-4 h-4 mr-2 ${item.favorite ? 'text-red-500 fill-current' : ''}`} />
                                {item.favorite ? 'Unfavorite' : 'Favorite'}
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleDeleteItem(item.id)}
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="favorites" className="mt-6">
            {getFavorites().length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <Heart className="w-16 h-16 text-red-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No favorites yet</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Start favoriting items you love to see them here
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {getFavorites().length} favorite items
                  </p>
                </div>
                {viewMode === "grid" ? (
                  <WardrobeGrid 
                    items={getFavorites()}
                    loading={false}
                    onItemClick={handleItemClick}
                    onGenerateOutfit={(item) => handleGenerateOutfitWithBaseItem(item)}
                    onToggleFavorite={handleToggleFavorite}
                    onDeleteItem={deleteItem}
                    showActions={true}
                  />
                ) : (
                  <div className="space-y-3">
                    {getFavorites().map((item) => (
                      <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleItemClick(item)}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                              <img
                                src={item.imageUrl}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                                  {item.name}
                                </h3>
                                <Heart className="w-4 h-4 text-red-500 fill-current" />
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <span>{getTypeIcon(item.type)} {item.type}</span>
                                <span>•</span>
                                <Badge className={`text-xs ${getColorBadge(item.color)}`}>
                                  {item.color}
                                </Badge>
                                <span>•</span>
                                <span>Worn {item.wearCount} times</span>
                              </div>
                              
                              {item.style && item.style.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {item.style.map((style, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {style}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex gap-2 flex-shrink-0">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleWearIncrement(item.id)}
                              >
                                <Sparkles className="w-4 h-4 mr-2" />
                                Worn
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleToggleFavorite(item.id)}
                              >
                                <Heart className="w-4 h-4 mr-2 text-red-500 fill-current" />
                                Unfavorite
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="recent" className="mt-6">
            {getRecentlyWorn().length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <Calendar className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No recently worn items</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Start wearing your clothes to see them appear here
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {getRecentlyWorn().length} recently worn items
                  </p>
                </div>
                {viewMode === "grid" ? (
                  <WardrobeGrid 
                    items={getRecentlyWorn()}
                    loading={false}
                    onItemClick={handleItemClick}
                    onGenerateOutfit={(item) => handleGenerateOutfitWithBaseItem(item)}
                    onToggleFavorite={handleToggleFavorite}
                    onDeleteItem={deleteItem}
                    showActions={true}
                  />
                ) : (
                  <div className="space-y-3">
                    {getRecentlyWorn().map((item) => (
                      <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleItemClick(item)}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                              <img
                                src={item.imageUrl}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                                  {item.name}
                                </h3>
                                {item.favorite && (
                                  <Heart className="w-4 h-4 text-red-500 fill-current" />
                                )}
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <span>{getTypeIcon(item.type)} {item.type}</span>
                                <span>•</span>
                                <Badge className={`text-xs ${getColorBadge(item.color)}`}>
                                  {item.color}
                                </Badge>
                                <span>•</span>
                                <span>Worn {item.wearCount} times</span>
                                {item.lastWorn && (
                                  <>
                                    <span>•</span>
                                    <span>Last: {formatLastWorn(item.lastWorn)}</span>
                                  </>
                                )}
                              </div>
                              
                              {item.style && item.style.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {item.style.map((style, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {style}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex gap-2 flex-shrink-0">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleWearIncrement(item.id)}
                              >
                                <Sparkles className="w-4 h-4 mr-2" />
                                Worn Again
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleToggleFavorite(item.id)}
                              >
                                <Heart className={`w-4 h-4 mr-2 ${item.favorite ? 'text-red-500 fill-current' : ''}`} />
                                {item.favorite ? 'Unfavorite' : 'Favorite'}
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="unworn" className="mt-6">
            {getUnwornItems().length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <TrendingUp className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No unworn items</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Great job! You're wearing all your clothes
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {getUnwornItems().length} unworn items
                  </p>
                </div>
                {viewMode === "grid" ? (
                  <WardrobeGrid 
                    items={getUnwornItems()}
                    loading={false}
                    onItemClick={handleItemClick}
                    onGenerateOutfit={(item) => handleGenerateOutfitWithBaseItem(item)}
                    onDeleteItem={deleteItem}
                    showActions={true}
                  />
                ) : (
                  <div className="space-y-3">
                    {getUnwornItems().map((item) => (
                      <Card key={item.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleItemClick(item)}>
                        <CardContent className="p-4">
                          <div className="flex items-center gap-4">
                            <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                              <img
                                src={item.imageUrl}
                                alt={item.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                                  {item.name}
                                </h3>
                                {item.favorite && (
                                  <Heart className="w-4 h-4 text-red-500 fill-current" />
                                )}
                              </div>
                              
                              <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 mb-2">
                                <span>{getTypeIcon(item.type)} {item.type}</span>
                                <span>•</span>
                                <Badge className={`text-xs ${getColorBadge(item.color)}`}>
                                  {item.color}
                                </Badge>
                                <span>•</span>
                                <span>Never worn</span>
                              </div>
                              
                              {item.style && item.style.length > 0 && (
                                <div className="flex flex-wrap gap-1">
                                  {item.style.map((style, index) => (
                                    <Badge key={index} variant="outline" className="text-xs">
                                      {style}
                                    </Badge>
                                  ))}
                                </div>
                              )}
                            </div>
                            
                            <div className="flex gap-2 flex-shrink-0">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleWearIncrement(item.id)}
                              >
                                <Sparkles className="w-4 h-4 mr-2" />
                                Wear Now
                              </Button>
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => handleToggleFavorite(item.id)}
                              >
                                <Heart className={`w-4 h-4 mr-2 ${item.favorite ? 'text-red-500 fill-current' : ''}`} />
                                {item.favorite ? 'Unfavorite' : 'Favorite'}
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="inspiration" className="mt-6">
            <DiverseStyleInspiration />
          </TabsContent>
        </Tabs>
      </main>

      {/* Item Details Modal */}
      <WardrobeItemDetails
        item={selectedItem}
        isOpen={showItemDetails}
        onClose={() => {
          setShowItemDetails(false);
          setSelectedItem(null);
        }}
        onUpdate={handleUpdateItem}
        onDelete={handleDeleteItem}
        onToggleFavorite={handleToggleFavorite}
        onIncrementWear={handleWearIncrement}
        onGenerateOutfit={handleGenerateOutfitWithBaseItem}
      />

      {/* Batch Upload Modal */}
      {showBatchUpload && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-2xl font-serif text-gray-900 dark:text-white">Add Items with AI</h2>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowBatchUpload(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
            <div className="p-6">
              <BatchImageUpload 
                onUploadComplete={async (items) => {
                  setShowBatchUpload(false);
                  refetch();
                }}
                onError={(message) => {
                  // Handle batch upload error silently
                }}
                userId={user?.uid || ''}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
