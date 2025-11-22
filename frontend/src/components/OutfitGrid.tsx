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
import OutfitEditModal from './OutfitEditModal';
import { OutfitUpdate } from '@/lib/services/outfitService';

// ===== COMPONENT INTERFACES =====
interface OutfitGridProps {
  showFilters?: boolean;
  showSearch?: boolean;
  maxOutfits?: number;
  className?: string;
  initialFavoritesOnly?: boolean;
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
    <Card className="group bg-white/85 dark:bg-[#1A1510]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-2xl hover:shadow-xl transition-transform duration-200 hover:scale-[1.01]">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-lg font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] line-clamp-2">
            {outfit.name}
          </CardTitle>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleFavorite}
            className="text-[#8A827A] hover:text-[#FF6F61] transition-colors"
          >
            {outfit.isFavorite ? (
              <Heart className="h-5 w-5 fill-[#FF6F61] text-[#FF6F61]" />
            ) : (
              <HeartOff className="h-5 w-5" />
            )}
          </Button>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Badge variant="secondary" className="text-xs uppercase tracking-wide">
            {outfit.occasion}
          </Badge>
          <Badge variant="outline" className="text-xs border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
            {outfit.style}
          </Badge>
          {outfit.mood && (
            <Badge variant="outline" className="text-xs border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
              {outfit.mood}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Outfit Preview - Flat Lay or Items */}
        <div className="mb-4">
          {/* Check for flatlay URL in metadata or direct property */}
          {(outfit as any).metadata?.flat_lay_url || (outfit as any).metadata?.flatLayUrl || (outfit as any).flat_lay_url || (outfit as any).flatLayUrl ? (
            // Show flatlay image if available
            <div className="mb-3">
              <div className="aspect-[9/16] bg-[#F5F0E8] dark:bg-[#2C2119] border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-2xl overflow-hidden">
                {(() => {
                  const flatLayUrl = (outfit as any).metadata?.flat_lay_url || (outfit as any).metadata?.flatLayUrl || (outfit as any).flat_lay_url || (outfit as any).flatLayUrl;
                  const useProxy = flatLayUrl?.includes('storage.googleapis.com') || flatLayUrl?.includes('firebasestorage.googleapis.com');
                  return (
                    <img
                      src={useProxy ? `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}` : flatLayUrl}
                      alt={outfit.name}
                      className="w-full h-full object-contain hover:scale-105 transition-transform duration-200"
                    />
                  );
                })()}
              </div>
              <div className="flex items-center justify-between mt-2">
                <Badge variant="secondary" className="text-xs">
                  <Eye className="h-3 w-3 mr-1" />
                  Flat Lay View
                </Badge>
              </div>
            </div>
          ) : (
            // Fallback: Show item grid preview
            <>
              <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">Items ({outfit.items.length}):</p>
              <div className="grid grid-cols-2 gap-2">
                {outfit.items.slice(0, 4).map((item, index) => (
                  <div key={index} className="relative group">
                    {item.imageUrl ? (
                      <div className="aspect-square rounded-xl overflow-hidden border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-[#F5F0E8]/60 dark:bg-[#2C2119]/70">
                        <img
                          src={item.thumbnailUrl || item.backgroundRemovedUrl || item.imageUrl}
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
                          className="hidden text-xs text-[#57534E] dark:text-[#C4BCB4] bg-white/80 dark:bg-[#2C2119]/80 px-2 py-1 rounded absolute inset-0 flex items-center justify-center"
                          style={{ display: 'none' }}
                        >
                          {item.name}
                        </div>
                      </div>
                    ) : (
                      <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] bg-[#F5F0E8]/60 dark:bg-[#2C2119]/70 px-2 py-1 rounded-xl aspect-square flex items-center justify-center text-center">
                        {item.name}
                      </div>
                    )}
                  </div>
                ))}
                {outfit.items.length > 4 && (
                  <div className="text-xs text-[#8A827A] bg-[#F5F0E8]/60 dark:bg-[#2C2119]/70 px-2 py-1 rounded-xl aspect-square flex items-center justify-center">
                    +{outfit.items.length - 4} more
                  </div>
                )}
              </div>
            </>
          )}
        </div>

        {/* Outfit Stats */}
        <div className="flex items-center justify-between text-sm text-[#57534E] dark:text-[#C4BCB4] mb-4">
          <div className="flex flex-col gap-1">
            <span>Worn {outfit.wearCount || 0} times</span>
            <span>Created: {
              outfit.createdAt ? 
                (outfit.createdAt instanceof Date ? 
                  outfit.createdAt.toLocaleDateString() : 
                  typeof outfit.createdAt === 'number' ?
                    new Date(outfit.createdAt).toLocaleDateString() :
                  typeof outfit.createdAt === 'string' ? 
                    new Date(outfit.createdAt).toLocaleDateString() :
                    outfit.createdAt.seconds ?
                      new Date(outfit.createdAt.seconds * 1000).toLocaleDateString() :
                      'Invalid Date'
                ) : 'Unknown'
            }</span>
          </div>
          {outfit.lastWorn && (
            <span>Last: {
              outfit.lastWorn instanceof Date ? 
                outfit.lastWorn.toLocaleDateString() : 
                typeof outfit.lastWorn === 'number' ?
                  new Date(outfit.lastWorn).toLocaleDateString() :
                typeof outfit.lastWorn === 'string' ? 
                  new Date(outfit.lastWorn).toLocaleDateString() :
                  outfit.lastWorn.seconds ? 
                    new Date(outfit.lastWorn.seconds * 1000).toLocaleDateString() :
                    'Invalid Date'
            }</span>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleWear}
            className="flex-1 text-xs border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
          >
            <Eye className="h-3 w-3 mr-1" />
            Mark worn
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleEdit}
            className="text-xs border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
          >
            <Edit className="h-3 w-3" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs text-[#FF6F61] border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 hover:text-[#FF4A3A]"
            onClick={handleDeleteClick}
          >
            <Trash2 className="h-3 w-3" />
          </Button>
        </div>

        {/* Confidence Score */}
        {outfit.confidenceScore && (
          <div className="mt-3 pt-3 border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
            <div className="flex items-center justify-between text-xs text-[#57534E] dark:text-[#C4BCB4]">
              <span>Confidence:</span>
              <span className={cn(
                "font-medium",
                outfit.confidenceScore >= 0.8 ? "text-[#10B981]" :
                outfit.confidenceScore >= 0.6 ? "text-[#F59E0B]" : "text-[#EF4444]"
              )}>
                {Math.round(outfit.confidenceScore * 100)}%
              </span>
            </div>
          </div>
        )}
      </CardContent>
      
      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="bg-white/90 dark:bg-[#1A1510]/90 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-2xl">
          <AlertDialogHeader>
            <AlertDialogTitle className="text-[#1C1917] dark:text-[#F8F5F1]">Delete outfit</AlertDialogTitle>
            <AlertDialogDescription className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
              This will remove “{outfit.name}” permanently.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setDeleteDialogOpen(false)} className="border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]">
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              className="bg-[#FF6F61] hover:bg-[#FF4A3A]"
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
    <div className="bg-white/85 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-3xl p-6 sm:p-8 mb-6 backdrop-blur-xl shadow-lg">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {/* Search Input */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-[#57534E] dark:text-[#C4BCB4] mb-2">
            Search outfits
          </label>
          <div className="flex gap-2">
            <Input
              placeholder="Search by name, occasion, style..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button onClick={handleSearch} size="sm" className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-4">
              Search
            </Button>
          </div>
        </div>

        {/* Occasion Filter */}
        <div>
          <label className="block text-sm font-medium text-[#57534E] dark:text-[#C4BCB4] mb-2">
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
          <label className="block text-sm font-medium text-[#57534E] dark:text-[#C4BCB4] mb-2">
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
          <label className="block text-sm font-medium text-[#57534E] dark:text-[#C4BCB4] mb-2">
            Sort by
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
      <div className="flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center mt-6 pt-4 border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
        <div className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
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
        <Button variant="outline" onClick={handleClear} size="sm" className="self-start sm:self-auto border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] rounded-2xl">
          Clear filters
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
  className,
  initialFavoritesOnly = false,
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
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(initialFavoritesOnly);
  const [isSearching, setIsSearching] = useState(false);
  const [sortBy, setSortBy] = useState<'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least'>('date-newest');
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingOutfit, setEditingOutfit] = useState<Outfit | null>(null);

  // Intersection observer for infinite scroll
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const refreshQueryHandledRef = useRef(false);
  
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
  }, [refresh]); // Removed isRefreshing from dependencies

  // ===== HELPER FUNCTIONS =====
  const safeToDate = (dateValue: any): Date => {
    if (dateValue instanceof Date) {
      return dateValue;
    }
    if (dateValue && typeof dateValue.toDate === 'function') {
      return dateValue.toDate();
    }
    if (typeof dateValue === 'string' || typeof dateValue === 'number') {
      return new Date(dateValue);
    }
    return new Date(); // Fallback to current date
  };

  // ===== COMPUTED VALUES =====
  const totalFavorites = useMemo(
    () => outfits.filter(outfit => outfit.isFavorite).length,
    [outfits]
  );

  const filteredOutfits = useMemo(() => {
    let baseOutfits = outfits;
    
    if (isSearching && searchResults.length > 0) {
      baseOutfits = searchResults;
    }

    if (showFavoritesOnly) {
      baseOutfits = baseOutfits.filter(outfit => outfit.isFavorite);
    }
    
    // Apply sorting based on selected option
    const sorted = [...baseOutfits].sort((a, b) => {
      switch (sortBy) {
        case 'date-newest':
          const dateA = safeToDate(a.createdAt);
          const dateB = safeToDate(b.createdAt);
          return dateB.getTime() - dateA.getTime(); // Newest first
        
        case 'date-oldest':
          const dateAOld = safeToDate(a.createdAt);
          const dateBOld = safeToDate(b.createdAt);
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
  }, [outfits, searchResults, isSearching, sortBy, showFavoritesOnly]);

  // ===== EFFECTS =====
  // Removed problematic useEffect that was causing infinite refresh loop
  // The useOutfits hook already handles initial data fetching

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
   * Handle refresh query parameter once to avoid repeated reload loops.
   * Ensures the outfits grid only reacts a single time even if the callback identities change.
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const refreshParam = urlParams.get('refresh');
    
    if (!refreshParam) {
      return;
    }

    if (!refreshQueryHandledRef.current) {
      refreshQueryHandledRef.current = true;
      console.log('🔄 [OutfitGrid] Refresh parameter detected, triggering debounced refresh');
      debouncedRefresh();
    } else {
      console.log('🔄 [OutfitGrid] Refresh parameter already handled, skipping duplicate refresh');
    }

    urlParams.delete('refresh');
    const remainingQuery = urlParams.toString();
    const cleanUrl = remainingQuery
      ? `${window.location.pathname}?${remainingQuery}`
      : window.location.pathname;
    window.history.replaceState({}, '', cleanUrl);
  }, [debouncedRefresh]);

  /**
   * Intersection observer for automatic infinite scroll
   */
  useEffect(() => {
    // Don't set up observer if there's no more to load or we're already loading
    if (!hasMore || loadingMore) {
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        // Only trigger if:
        // 1. Element is intersecting
        // 2. We have more to load
        // 3. We're not currently loading
        // 4. We're not refreshing
        if (first.isIntersecting && hasMore && !loadingMore && !isRefreshing) {
          console.log('🔄 [OutfitGrid] Load more trigger reached, loading more outfits');
          loadMoreOutfits();
        }
      },
      { threshold: 0.1, rootMargin: '100px' } // Add rootMargin to trigger slightly before element is visible
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
  }, [hasMore, loadingMore, loadMoreOutfits, isRefreshing]);

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
      
      // Dispatch event to notify dashboard of outfit being marked as worn
      const outfit = outfits.find(o => o.id === id);
      const event = new CustomEvent('outfitMarkedAsWorn', {
        detail: {
          outfitId: id,
          outfitName: outfit?.name || 'Unknown Outfit',
          timestamp: new Date().toISOString()
        }
      });
      window.dispatchEvent(event);
      console.log('🔄 [OutfitGrid] Dispatched outfitMarkedAsWorn event for dashboard refresh');
      
    } catch (error) {
      console.error('Failed to mark as worn:', error);
    }
  };

  const handleEdit = (id: string) => {
    const outfit = outfits.find(o => o.id === id);
    if (outfit) {
      setEditingOutfit(outfit);
      setEditModalOpen(true);
    }
  };

  const handleSaveEdit = async (updates: OutfitUpdate) => {
    if (!editingOutfit) return;
    
    try {
      const result = await updateOutfit(editingOutfit.id, updates);
      if (result) {
        setEditModalOpen(false);
        setEditingOutfit(null);
      }
    } catch (error) {
      console.error('Failed to update outfit:', error);
    }
  };

  const handleCloseEdit = () => {
    setEditModalOpen(false);
    setEditingOutfit(null);
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
            {isSearching ? 'Search Results' : showFavoritesOnly ? 'Favorite Outfits' : 'All Outfits'}
          </h2>
          <p className="text-gray-600">
            {(() => {
              const displayCount = filteredOutfits.length;
              const searchLabel = displayCount === 1 ? 'outfit' : 'outfits';
              
              if (isSearching) {
                return `Found ${displayCount} ${showFavoritesOnly ? 'favorite ' : ''}${searchLabel} matching your search`;
              }
              
              if (showFavoritesOnly) {
                return `Showing ${displayCount} of ${totalFavorites} favorite ${totalFavorites === 1 ? 'outfit' : 'outfits'}`;
              }
              
              return `Showing ${displayCount} of ${outfits.length} total ${outfits.length === 1 ? 'outfit' : 'outfits'}`;
            })()}
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            onClick={() => setShowFavoritesOnly(prev => !prev)}
            variant={showFavoritesOnly ? 'default' : 'outline'}
            size="sm"
            className={cn(
              "flex items-center gap-2 border",
              showFavoritesOnly
                ? "bg-red-100 text-red-600 border-red-200 hover:bg-red-200"
                        : "text-[#57534E] border-[#F5F0E8]/60 hover:bg-[#F5F0E8] dark:border-[#3D2F24]/70 dark:hover:bg-[#2C2119]"
            )}
          >
            <Heart className={cn("h-4 w-4", showFavoritesOnly ? "fill-current" : "")} />
            {showFavoritesOnly ? 'Favorites Only' : 'Favorites'}
          </Button>
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
            {isSearching
              ? showFavoritesOnly ? 'No favorite outfits found' : 'No outfits found'
              : showFavoritesOnly ? 'No favorite outfits yet' : 'No outfits yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {isSearching 
              ? 'Try adjusting your search terms or filters'
              : showFavoritesOnly
                ? 'Tap the heart icon on outfits you love to collect them here.'
                : 'Create your first outfit to get started'}
          </p>
          {!isSearching && showFavoritesOnly && (
            <Button onClick={() => setShowFavoritesOnly(false)} variant="outline">
              View all outfits
            </Button>
          )}
          {!isSearching && !showFavoritesOnly && (
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

      {/* Edit Modal */}
      {editingOutfit && (
        <OutfitEditModal
          outfit={editingOutfit}
          isOpen={editModalOpen}
          onClose={handleCloseEdit}
          onSave={handleSaveEdit}
        />
      )}
    </div>
  );
}
