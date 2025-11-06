"use client";

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Heart, 
  HeartOff, 
  Eye, 
  Edit, 
  Trash2, 
  RefreshCw, 
  Search, 
  Filter,
  X,
  Zap,
  TrendingUp,
  Calendar
} from 'lucide-react';
import { cn } from '@/lib/utils';
import useOutfitsFast from '@/lib/hooks/useOutfitsFast';
import { OutfitMetadata, OutfitFilters } from '@/lib/services/outfitServiceFast';

// ===== INTERFACES =====
interface OutfitGridFastProps {
  showFilters?: boolean;
  showSearch?: boolean;
  showSummary?: boolean;
  className?: string;
}

interface OutfitCardProps {
  outfit: OutfitMetadata;
  onFavorite: (id: string) => void;
  onView: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

// ===== OUTFIT CARD COMPONENT =====
function OutfitCard({ outfit, onFavorite, onView, onEdit, onDelete }: OutfitCardProps) {
  const formatDate = (dateValue: any): string => {
    try {
      let date: Date;
      
      if (dateValue instanceof Date) {
        date = dateValue;
      } else if (typeof dateValue === 'number') {
        // Handle Unix timestamp in milliseconds
        date = new Date(dateValue);
      } else if (typeof dateValue === 'string') {
        date = new Date(dateValue);
      } else if (dateValue?.toDate && typeof dateValue.toDate === 'function') {
        // Firestore Timestamp with toDate method
        date = dateValue.toDate();
      } else if (dateValue?.seconds) {
        // Firestore Timestamp with seconds field
        date = new Date(dateValue.seconds * 1000);
      } else {
        return 'Unknown date';
      }
      
      // Validate the parsed date
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      return date.toLocaleDateString();
    } catch (error) {
      return 'Invalid date';
    }
  };

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 bg-white/80 dark:bg-stone-900/80 backdrop-blur-sm border border-stone-200 dark:border-stone-700">
      <div className="relative">
        {/* Outfit Image/Preview */}
        <div className="aspect-square bg-stone-100 dark:bg-stone-800 rounded-t-lg relative overflow-hidden">
          {outfit.thumbnailUrl ? (
            <img 
              src={outfit.thumbnailUrl} 
              alt={outfit.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center text-stone-400">
              {/* Show item previews if no main thumbnail */}
              {outfit.itemPreviews.length > 0 ? (
                <div className="grid grid-cols-2 gap-1 p-2 w-full h-full">
                  {outfit.itemPreviews.slice(0, 4).map((item, index) => (
                    <div key={index} className="bg-stone-200 dark:bg-stone-700 rounded flex items-center justify-center overflow-hidden">
                      {item.imageUrl ? (
                        <img 
                          src={item.thumbnailUrl || item.backgroundRemovedUrl || item.imageUrl} 
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="text-xs text-center p-1">
                          {item.name || item.type}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <>
                  <Zap className="w-8 h-8 mb-2" />
                  <span className="text-sm">No Preview</span>
                </>
              )}
            </div>
          )}
          
          {/* Favorite Button */}
          <button
            onClick={() => onFavorite(outfit.id)}
            className="absolute top-2 right-2 p-2 rounded-full bg-white/80 dark:bg-stone-900/80 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:scale-110"
          >
            {outfit.isFavorite ? (
              <Heart className="w-4 h-4 text-red-500 fill-red-500" />
            ) : (
              <HeartOff className="w-4 h-4 text-stone-600 dark:text-stone-400" />
            )}
          </button>

          {/* Wear Count Badge */}
          {outfit.wearCount > 0 && (
            <div className="absolute top-2 left-2 px-2 py-1 rounded-full bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300 text-xs font-medium">
              Worn {outfit.wearCount}x
            </div>
          )}
        </div>

        {/* Outfit Info */}
        <CardContent className="p-4">
          <div className="space-y-2">
            <h3 className="font-semibold text-stone-900 dark:text-stone-100 line-clamp-1">
              {outfit.name}
            </h3>
            
            <div className="flex flex-wrap gap-1">
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

            <div className="flex items-center justify-between text-xs text-stone-500 dark:text-stone-400">
              <span>{outfit.itemCount} items</span>
              <span>{formatDate(outfit.createdAt)}</span>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              <Button
                size="sm"
                variant="outline"
                onClick={() => onView(outfit.id)}
                className="flex-1"
              >
                <Eye className="w-3 h-3 mr-1" />
                View
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onEdit(outfit.id)}
              >
                <Edit className="w-3 h-3" />
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => onDelete(outfit.id)}
                className="text-red-600 hover:text-red-700"
              >
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </CardContent>
      </div>
    </Card>
  );
}

// ===== SUMMARY STATS COMPONENT =====
function SummaryStats({ summary, loading }: { summary: any; loading: boolean }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[1, 2, 3].map(i => (
          <Card key={i} className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-4 bg-stone-200 dark:bg-stone-700 rounded mb-2"></div>
              <div className="h-8 bg-stone-200 dark:bg-stone-700 rounded mb-2"></div>
              <div className="h-3 bg-stone-200 dark:bg-stone-700 rounded"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!summary) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-amber-600 dark:text-amber-400 mb-1">Total Outfits</p>
              <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                {summary.total_outfits.toLocaleString()}
              </p>
              <p className="text-xs text-blue-500 dark:text-blue-400">Your complete collection</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-800/50 rounded-full flex items-center justify-center">
              <Zap className="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-emerald-50 to-emerald-100 dark:from-emerald-900/20 dark:to-emerald-800/20 border-emerald-200 dark:border-emerald-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-emerald-600 dark:text-emerald-400 mb-1">This Week</p>
              <p className="text-3xl font-bold text-emerald-900 dark:text-emerald-100">
                {summary.outfits_this_week}
              </p>
              <p className="text-xs text-emerald-500 dark:text-emerald-400">Outfits created</p>
            </div>
            <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-800/50 rounded-full flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-amber-600 dark:text-amber-400 mb-1">Recent</p>
              <p className="text-3xl font-bold text-purple-900 dark:text-purple-100">
                {summary.recent_outfits?.length || 0}
              </p>
              <p className="text-xs text-purple-500 dark:text-purple-400">Latest additions</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 dark:bg-purple-800/50 rounded-full flex items-center justify-center">
              <Calendar className="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// ===== MAIN COMPONENT =====
export default function OutfitGridFast({ 
  showFilters = true, 
  showSearch = true, 
  showSummary = true,
  className 
}: OutfitGridFastProps) {
  
  // ===== HOOKS =====
  const {
    summary,
    summaryLoading,
    outfits,
    loading,
    loadingMore,
    hasMore,
    filterOptions,
    filtersLoading,
    currentFilters,
    searchQuery,
    filteredOutfits,
    error,
    setFilters,
    setSearchQuery,
    loadMoreOutfits,
    clearError,
    refresh
  } = useOutfitsFast();

  // ===== LOCAL STATE =====
  const [showFiltersPanel, setShowFiltersPanel] = useState(false);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // ===== INTERSECTION OBSERVER FOR INFINITE SCROLL =====
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        if (first.isIntersecting && hasMore && !loadingMore && !loading) {
          console.log('🔄 [OutfitGridFast] Load more trigger reached');
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
  }, [hasMore, loadingMore, loading, loadMoreOutfits]);

  // ===== EVENT HANDLERS =====
  const handleFilterChange = (key: keyof OutfitFilters, value: any) => {
    const newFilters = { ...currentFilters, [key]: value };
    if (value === '' || value === null || value === undefined) {
      delete newFilters[key];
    }
    setFilters(newFilters);
  };

  const clearAllFilters = () => {
    setFilters({});
    setSearchQuery('');
    setShowFiltersPanel(false);
  };

  const handleOutfitAction = (action: string, id: string) => {
    console.log(`🔄 [OutfitGridFast] ${action} outfit:`, id);
    // TODO: Implement outfit actions (favorite, view, edit, delete)
  };

  // ===== COMPUTED VALUES =====
  const activeFiltersCount = Object.keys(currentFilters).length + (searchQuery ? 1 : 0);

  // ===== RENDER =====
  return (
    <div className={cn("space-y-6", className)}>
      {/* Summary Stats */}
      {showSummary && (
        <SummaryStats summary={summary} loading={summaryLoading} />
      )}

      {/* Search and Filters */}
      {(showSearch || showFilters) && (
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          {/* Search */}
          {showSearch && (
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-stone-400 w-4 h-4" />
              <Input
                placeholder="Search outfits..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-stone-400 hover:text-stone-600"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>
          )}

          {/* Filter Controls */}
          {showFilters && (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => setShowFiltersPanel(!showFiltersPanel)}
                className="relative"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
                {activeFiltersCount > 0 && (
                  <Badge className="ml-2 px-1.5 py-0.5 text-xs">
                    {activeFiltersCount}
                  </Badge>
                )}
              </Button>

              <Button
                variant="outline"
                onClick={refresh}
                disabled={loading}
              >
                <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Filters Panel */}
      {showFiltersPanel && filterOptions && (
        <Card className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Select
              value={currentFilters.occasion || ''}
              onValueChange={(value) => handleFilterChange('occasion', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Occasion" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Occasions</SelectItem>
                {filterOptions.occasions.map(occasion => (
                  <SelectItem key={occasion} value={occasion}>
                    {occasion}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={currentFilters.style || ''}
              onValueChange={(value) => handleFilterChange('style', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Style" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Styles</SelectItem>
                {filterOptions.styles.map(style => (
                  <SelectItem key={style} value={style}>
                    {style}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={currentFilters.is_favorite?.toString() || ''}
              onValueChange={(value) => handleFilterChange('is_favorite', value === 'true' ? true : value === 'false' ? false : undefined)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Favorites" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Outfits</SelectItem>
                <SelectItem value="true">Favorites Only</SelectItem>
                <SelectItem value="false">Non-Favorites</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={currentFilters.sort_by || 'date-newest'}
              onValueChange={(value) => handleFilterChange('sort_by', value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sort By" />
              </SelectTrigger>
              <SelectContent>
                {filterOptions.sort_options.map(option => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {activeFiltersCount > 0 && (
            <div className="flex justify-between items-center mt-4 pt-4 border-t">
              <span className="text-sm text-stone-500">
                {activeFiltersCount} filter{activeFiltersCount > 1 ? 's' : ''} applied
              </span>
              <Button variant="ghost" size="sm" onClick={clearAllFilters}>
                Clear All
              </Button>
            </div>
          )}
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50 dark:bg-red-900/10 dark:border-red-800">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="text-red-600 dark:text-red-400">
                  <X className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-sm font-medium text-red-800 dark:text-red-200">
                    Error loading outfits
                  </p>
                  <p className="text-xs text-red-600 dark:text-red-400">
                    {error}
                  </p>
                </div>
              </div>
              <Button variant="outline" size="sm" onClick={clearError}>
                Dismiss
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Loading State */}
      {loading && filteredOutfits.length === 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <div className="aspect-square bg-stone-200 dark:bg-stone-700 rounded-t-lg"></div>
              <CardContent className="p-4 space-y-2">
                <div className="h-4 bg-stone-200 dark:bg-stone-700 rounded"></div>
                <div className="h-3 bg-stone-200 dark:bg-stone-700 rounded w-2/3"></div>
                <div className="h-3 bg-stone-200 dark:bg-stone-700 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Outfit Grid */}
      {filteredOutfits.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredOutfits.map((outfit) => (
            <OutfitCard
              key={outfit.id}
              outfit={outfit}
              onFavorite={(id) => handleOutfitAction('favorite', id)}
              onView={(id) => handleOutfitAction('view', id)}
              onEdit={(id) => handleOutfitAction('edit', id)}
              onDelete={(id) => handleOutfitAction('delete', id)}
            />
          ))}
        </div>
      )}

      {/* Load More Trigger */}
      {hasMore && (
        <div ref={loadMoreRef} className="flex justify-center py-8">
          {loadingMore ? (
            <div className="flex items-center space-x-2 text-stone-500">
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Loading more outfits...</span>
            </div>
          ) : (
            <div className="text-stone-400 text-sm">
              Scroll down to load more
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredOutfits.length === 0 && !error && (
        <Card className="text-center py-12">
          <CardContent>
            <Zap className="w-12 h-12 text-stone-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-stone-900 dark:text-stone-100 mb-2">
              No outfits found
            </h3>
            <p className="text-stone-500 dark:text-stone-400 mb-4">
              {searchQuery || activeFiltersCount > 0 
                ? "Try adjusting your search or filters"
                : "Start creating your first outfit!"
              }
            </p>
            {(searchQuery || activeFiltersCount > 0) && (
              <Button variant="outline" onClick={clearAllFilters}>
                Clear Filters
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
