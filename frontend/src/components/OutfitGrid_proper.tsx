"use client";

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Heart, HeartOff, Eye, Edit, Trash2, RefreshCw, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

// Import the established pattern components
import useOutfits from '@/lib/hooks/useOutfits_proper';
import { Outfit, OutfitFilters } from '@/lib/services/outfitService';

// ===== COMPONENT INTERFACES =====
interface OutfitGridProps {
  showFilters?: boolean;
  showSearch?: boolean;
  maxOutfits?: number;
  className?: string;
}

interface OutfitCardProps {
  outfit: Outfit;
  onFavorite: (id: string) => void;
  onWear: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

// ===== OUTFIT CARD COMPONENT =====
function OutfitCard({ outfit, onFavorite, onWear, onEdit, onDelete }: OutfitCardProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  const handleFavorite = () => onFavorite(outfit.id);
  const handleWear = () => onWear(outfit.id);
  const handleEdit = () => onEdit(outfit.id);
  const handleDeleteClick = () => setDeleteDialogOpen(true);
  
  const handleDeleteConfirm = () => {
    console.log(`🔍 [OutfitCard] Confirmed delete for outfit ${outfit.id}`);
    onDelete(outfit.id);
    setDeleteDialogOpen(false);
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-200">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-2">
            {outfit.name}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleFavorite}
            className="text-gray-400 hover:text-red-500 transition-colors"
          >
            {outfit.isFavorite ? (
              <Heart className="h-5 w-5 fill-red-500 text-red-500" />
            ) : (
              <HeartOff className="h-5 w-5" />
            )}
          </Button>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary" className="text-xs">
            {outfit.occasion}
          </Badge>
          <Badge variant="outline" className="text-xs">
            {outfit.style}
          </Badge>
          {outfit.mood && (
            <Badge variant="outline" className="text-xs">
              {outfit.mood}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Outfit Items Preview */}
        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">Items ({outfit.items.length}):</p>
          <div className="grid grid-cols-2 gap-2">
            {outfit.items.slice(0, 4).map((item, index) => (
              <div key={index} className="relative group">
                {item.imageUrl ? (
                  <div className="aspect-square rounded-lg overflow-hidden border border-gray-200">
                    <img
                      src={item.imageUrl}
                      alt={item.name}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-200"
                      onError={(e) => {
                        // Fallback to text if image fails to load
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                        const fallback = target.nextElementSibling as HTMLElement;
                        if (fallback) fallback.style.display = 'block';
                      }}
                    />
                    <div 
                      className="hidden text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded absolute inset-0 flex items-center justify-center"
                      style={{ display: 'none' }}
                    >
                      {item.name}
                    </div>
                  </div>
                ) : (
                  <div className="text-xs text-gray-500 bg-gray-50 px-2 py-1 rounded aspect-square flex items-center justify-center text-center">
                    {item.name}
                  </div>
                )}
              </div>
            ))}
            {outfit.items.length > 4 && (
              <div className="text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded aspect-square flex items-center justify-center">
                +{outfit.items.length - 4} more
              </div>
            )}
          </div>
        </div>

        {/* Outfit Stats */}
        <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
          <div className="flex flex-col gap-1">
            <span>Worn {outfit.wearCount || 0} times</span>
            <span>Created: {
              outfit.createdAt ? 
                (outfit.createdAt instanceof Date ? 
                  outfit.createdAt.toLocaleDateString() : 
                  typeof outfit.createdAt === 'string' ? 
                    new Date(outfit.createdAt).toLocaleDateString() :
                    new Date(outfit.createdAt.seconds * 1000).toLocaleDateString()
                ) : 'Unknown'
            }</span>
          </div>
          {outfit.lastWorn && (
            <span>Last: {outfit.lastWorn instanceof Date ? outfit.lastWorn.toLocaleDateString() : new Date(outfit.lastWorn.seconds * 1000).toLocaleDateString()}</span>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleWear}
            className="flex-1 text-xs"
          >
            <Eye className="h-3 w-3 mr-1" />
            Mark Worn
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleEdit}
            className="text-xs"
          >
            <Edit className="h-3 w-3" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs text-red-600 hover:text-red-700"
            onClick={handleDeleteClick}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>

        {/* Confidence Score */}
        {outfit.confidenceScore && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Confidence:</span>
              <span className={cn(
                "font-medium",
                outfit.confidenceScore >= 0.8 ? "text-green-600" :
                outfit.confidenceScore >= 0.6 ? "text-yellow-600" : "text-red-600"
              )}>
                {Math.round(outfit.confidenceScore * 100)}%
              </span>
            </div>
          </div>
        )}
      </CardContent>
      
      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Outfit</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{outfit.name}"? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeleteDialogOpen(false)}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-red-600 hover:bg-red-700"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}

// ===== FILTERS COMPONENT =====
interface OutfitFiltersProps {
  filters: OutfitFilters;
  onFiltersChange: (filters: OutfitFilters) => void;
  onSearch: (query: string) => void;
  onClear: () => void;
  sortBy: 'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least';
  onSortChange: (sortBy: 'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least') => void;
}

function OutfitFiltersComponent({ filters, onFiltersChange, onSearch, onClear, sortBy, onSortChange }: OutfitFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    onSearch(searchQuery);
  };

  const handleClear = () => {
    setSearchQuery('');
    onClear();
  };

  return (
    <div className="bg-transparent p-6 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {/* Search Input */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Search Outfits
          </label>
          <div className="flex gap-2">
            <Input
              placeholder="Search by name, occasion, style..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} size="sm">
              Search
            </Button>
          </div>
        </div>

        {/* Occasion Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Occasion
          </label>
          <Select
            value={filters.occasion || 'all'}
            onValueChange={(value) => onFiltersChange({ ...filters, occasion: value === 'all' ? undefined : value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="All occasions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All occasions</SelectItem>
              <SelectItem value="casual">Casual</SelectItem>
              <SelectItem value="business">Business</SelectItem>
              <SelectItem value="formal">Formal</SelectItem>
              <SelectItem value="athletic">Athletic</SelectItem>
              <SelectItem value="evening">Evening</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Style Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Style
          </label>
          <Select
            value={filters.style || 'all'}
            onValueChange={(value) => onFiltersChange({ ...filters, style: value === 'all' ? undefined : value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="All styles" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All styles</SelectItem>
              <SelectItem value="classic">Classic</SelectItem>
              <SelectItem value="modern">Modern</SelectItem>
              <SelectItem value="vintage">Vintage</SelectItem>
              <SelectItem value="bohemian">Bohemian</SelectItem>
              <SelectItem value="minimalist">Minimalist</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Sort By */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Sort By
          </label>
          <Select
            value={sortBy}
            onValueChange={onSortChange}
          >
            <SelectTrigger>
              <SelectValue placeholder="Sort by..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="date-newest">Newest First</SelectItem>
              <SelectItem value="date-oldest">Oldest First</SelectItem>
              <SelectItem value="wear-most">Most Worn</SelectItem>
              <SelectItem value="wear-least">Least Worn</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-500">
          {filters.occasion && filters.occasion !== 'all' && `Occasion: ${filters.occasion}`}
          {filters.style && filters.style !== 'all' && ` Style: ${filters.style}`}
          {((filters.occasion && filters.occasion !== 'all') || (filters.style && filters.style !== 'all')) && ' • '}
          <span>Sort: {
            sortBy === 'date-newest' ? 'Newest First' :
            sortBy === 'date-oldest' ? 'Oldest First' :
            sortBy === 'wear-most' ? 'Most Worn' :
            'Least Worn'
          }</span>
        </div>
        <Button variant="outline" onClick={handleClear} size="sm">
          Clear Filters
        </Button>
      </div>
    </div>
  );
}

// ===== MAIN OUTFIT GRID COMPONENT =====
export default function OutfitGrid({ 
  showFilters = true, 
  showSearch = true, 
  maxOutfits = 1000,
  className 
}: OutfitGridProps) {
  // ===== HOOK USAGE =====
  // This follows the established wardrobe service architecture pattern:
  // - useOutfits_proper provides data and actions
  // - outfitService_proper handles API calls
  // - Proper TypeScript interfaces for data contracts
  const { 
    outfits, 
    loading, 
    loadingMore,
    hasMore,
    error, 
    fetchOutfits, 
    loadMoreOutfits,
    markAsWorn, 
    toggleFavorite, 
    updateOutfit, 
    deleteOutfit, 
    clearError, 
    refresh 
  } = useOutfits();

  // ===== LOCAL STATE =====
  const [filters, setFilters] = useState<OutfitFilters>({});
  const [searchResults, setSearchResults] = useState<Outfit[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [sortBy, setSortBy] = useState<'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least'>('date-newest');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Intersection observer for infinite scroll
  const loadMoreRef = useRef<HTMLDivElement>(null);
  
  // Debounced refresh function to prevent multiple simultaneous refreshes
  const debouncedRefresh = useCallback(() => {
    if (isRefreshing) {
      console.log('🔄 [OutfitGrid] Refresh already in progress, skipping...');
      return;
    }
    
    setIsRefreshing(true);
    console.log('🔄 [OutfitGrid] Starting debounced refresh...');
    
    refresh().finally(() => {
      setTimeout(() => {
        setIsRefreshing(false);
        console.log('✅ [OutfitGrid] Refresh completed');
      }, 1000); // Small delay to prevent rapid successive refreshes
    });
  }, [refresh, isRefreshing]);

  // ===== COMPUTED VALUES =====
  const filteredOutfits = useMemo(() => {
    let baseOutfits = outfits;
    
    if (isSearching && searchResults.length > 0) {
      baseOutfits = searchResults;
    }
    
    // Apply sorting based on selected option
    const sorted = [...baseOutfits].sort((a, b) => {
      switch (sortBy) {
        case 'date-newest':
          const dateA = new Date(a.createdAt);
          const dateB = new Date(b.createdAt);
          return dateB.getTime() - dateA.getTime(); // Newest first
        
        case 'date-oldest':
          const dateAOld = new Date(a.createdAt);
          const dateBOld = new Date(b.createdAt);
          return dateAOld.getTime() - dateBOld.getTime(); // Oldest first
        
        case 'wear-most':
          const wearCountA = a.wearCount || 0;
          const wearCountB = b.wearCount || 0;
          return wearCountB - wearCountA; // Most worn first
        
        case 'wear-least':
          const wearCountALeast = a.wearCount || 0;
          const wearCountBLeast = b.wearCount || 0;
          return wearCountALeast - wearCountBLeast; // Least worn first
        
        default:
          return 0;
      }
    });
    
    if (sorted.length > 0) {
      console.log('🔄 [OutfitGrid] Sorted outfits:', {
        total: sorted.length,
        sortBy: sortBy,
        first: {
          name: sorted[0]?.name,
          createdAt: sorted[0]?.createdAt,
          wearCount: sorted[0]?.wearCount || 0
        },
        last: {
          name: sorted[sorted.length - 1]?.name,
          createdAt: sorted[sorted.length - 1]?.createdAt,
          wearCount: sorted[sorted.length - 1]?.wearCount || 0
        }
      });
      
      // DEBUG: Show first 3 outfit dates explicitly
      console.log('🔍 [OutfitGrid] First 3 outfit dates:', sorted.slice(0, 3).map(o => `${o.name}: ${o.createdAt}`));
    }
    
    return sorted;
  }, [outfits, searchResults, isSearching, sortBy]);

  // ===== EFFECTS =====
  /**
   * Refresh outfits when component mounts to catch newly generated outfits
   */
  useEffect(() => {
    if (!loading && outfits.length === 0) {
      console.log('🔄 [OutfitGrid] Component mounted with no outfits, triggering refresh');
      refresh();
    }
  }, [refresh, loading, outfits.length]);

  /**
   * Check for refresh parameter in URL and trigger refresh
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const refreshParam = urlParams.get('refresh');
    
    if (refreshParam) {
      console.log('🔄 [OutfitGrid] Refresh parameter detected, triggering immediate refresh');
      refresh();
      
      // Clean up URL without refresh param
      const newUrl = window.location.pathname;
      window.history.replaceState({}, '', newUrl);
    }
  }, [refresh]);

  /**
   * Refresh outfits when page becomes visible (for new outfits from generation page)
   * DEBOUNCED to prevent infinite refresh loops
   */
  useEffect(() => {
    let debounceTimer: NodeJS.Timeout;
    
    const handleVisibilityChange = () => {
      if (!document.hidden && !isRefreshing) { // Only refresh if not already refreshing
        console.log('🔄 [OutfitGrid] Page became visible, debounced refresh in 3s');
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          debouncedRefresh();
        }, 3000); // 3 second debounce
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      clearTimeout(debounceTimer);
    };
  }, [debouncedRefresh, isRefreshing]);

  /**
   * Refresh outfits when user navigates to this page (for new outfits from generation page)  
   * DEBOUNCED to prevent infinite refresh loops
   */
  useEffect(() => {
    let debounceTimer: NodeJS.Timeout;
    
    const handleFocus = () => {
      if (!isRefreshing) { // Only refresh if not already refreshing
        console.log('🔄 [OutfitGrid] Window focused, debounced refresh in 5s');
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          debouncedRefresh();
        }, 5000); // 5 second debounce
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
      clearTimeout(debounceTimer);
    };
  }, [debouncedRefresh, isRefreshing]);

  /**
   * Listen for outfit marked as worn events to refresh outfit data
   */
  useEffect(() => {
    const handleOutfitMarkedAsWorn = (event: CustomEvent) => {
      console.log('🔄 [OutfitGrid] Outfit marked as worn, refreshing outfit data...', event.detail);
      debouncedRefresh();
    };

    window.addEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    
    return () => {
      window.removeEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    };
  }, [debouncedRefresh]);

  /**
   * Check for refresh parameter in URL (from outfit generation page)
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const refreshParam = urlParams.get('refresh');
    
    if (refreshParam && !isRefreshing) {
      console.log('🔄 [OutfitGrid] Refresh parameter detected, refreshing outfits...');
      debouncedRefresh();
      
      // Clean up URL by removing the refresh parameter
      const newUrl = new URL(window.location.href);
      newUrl.searchParams.delete('refresh');
      window.history.replaceState({}, '', newUrl.toString());
    }
  }, [debouncedRefresh, isRefreshing]);

  /**
   * Intersection observer for automatic infinite scroll
   */
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting && hasMore && !loadingMore) {
          console.log('🔄 [OutfitGrid] Load more trigger reached, loading more outfits');
          loadMoreOutfits();
        }
      },
      { threshold: 0.1 }
    );

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, [hasMore, loadingMore, loadMoreOutfits]);

  // ===== EVENT HANDLERS =====
  const handleFiltersChange = (newFilters: OutfitFilters) => {
    setFilters(newFilters);
    setIsSearching(false);
    fetchOutfits(newFilters);
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await fetchOutfits({ ...filters, limit: 1000 });
      // Note: In a real implementation, this would use a dedicated search endpoint
      // For now, we're using the existing fetchOutfits with client-side filtering
      const filtered = outfits.filter(outfit => {
        const searchText = `${outfit.name} ${outfit.occasion} ${outfit.style} ${outfit.mood || ''}`.toLowerCase();
        return searchText.includes(query.toLowerCase());
      });
      setSearchResults(filtered);
    } catch (error) {
      console.error('Search failed:', error);
    }
  };

  const handleClear = () => {
    setIsSearching(false);
    setSearchResults([]);
    setFilters({ limit: maxOutfits });
    fetchOutfits({ limit: maxOutfits });
  };

  const handleFavorite = async (id: string) => {
    try {
      await toggleFavorite(id);
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleWear = async (id: string) => {
    try {
      await markAsWorn(id);
    } catch (error) {
      console.error('Failed to mark as worn:', error);
    }
  };

  const handleEdit = (id: string) => {
    // TODO: Implement edit functionality
    console.log('Edit outfit:', id);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this outfit?')) {
      try {
        await deleteOutfit(id);
      } catch (error) {
        console.error('Failed to delete outfit:', error);
      }
    }
  };

  // ===== RENDER STATES =====
  if (loading && outfits.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Loading your outfits...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <div className="flex gap-2 justify-center">
          <Button onClick={clearError} variant="outline" size="sm">
            Dismiss
          </Button>
          <Button onClick={refresh} size="sm">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // ===== MAIN RENDER =====
  return (
    <div className={cn("space-y-6", className)}>
      {/* Header with Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            {isSearching ? 'Search Results' : 'All Outfits'}
          </h2>
          <p className="text-gray-600">
            {isSearching 
              ? `Found ${searchResults.length} outfits matching your search`
              : `Showing ${filteredOutfits.length} of ${outfits.length} total outfits`
            }
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            onClick={() => {
              console.log('🔄 [OutfitGrid] Manual refresh triggered by user');
              refresh();
            }} 
            variant="outline" 
            size="sm"
            disabled={loading}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      {showFilters && (
        <OutfitFiltersComponent
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onSearch={handleSearch}
          onClear={handleClear}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />
      )}

      {/* Search Results Indicator */}
      {isSearching && searchResults.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800 text-sm">
            🔍 Showing {searchResults.length} search results. 
            <button 
              onClick={handleClear}
              className="text-blue-600 hover:text-blue-800 underline ml-2"
            >
              Clear search
            </button>
          </p>
        </div>
      )}

      {/* Outfits Grid */}
      {filteredOutfits.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isSearching ? 'No outfits found' : 'No outfits yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {isSearching 
              ? 'Try adjusting your search terms or filters'
              : 'Create your first outfit to get started'
            }
          </p>
          {!isSearching && (
            <Button onClick={refresh} variant="outline">
              Refresh
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredOutfits.map((outfit) => (
            <OutfitCard
              key={outfit.id}
              outfit={outfit}
              onFavorite={handleFavorite}
              onWear={handleWear}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Load More Section */}
      {hasMore && (
        <div ref={loadMoreRef} className="text-center py-8">
          {loadingMore ? (
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
              <p className="text-gray-500 text-sm">Loading more outfits...</p>
            </div>
          ) : (
            <Button 
              onClick={loadMoreOutfits}
              variant="outline" 
              className="flex items-center gap-2"
              disabled={loadingMore}
            >
              <ChevronDown className="h-4 w-4" />
              Load More Outfits
            </Button>
          )}
        </div>
      )}

      {/* End of Results */}
      {!hasMore && outfits.length > 0 && (
        <div className="text-center py-6">
          <p className="text-gray-500 text-sm">
            That's all your outfits! You have {outfits.length} total outfits.
          </p>
        </div>
      )}
    </div>
  );
}
