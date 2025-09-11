'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  SortAsc,
  SortDesc,
  RefreshCw,
  ChevronDown,
  X
} from 'lucide-react';
import EnhancedOutfitCard from './enhanced-outfit-card';

interface Outfit {
  id: string;
  name: string;
  occasion: string;
  style: string;
  mood?: string;
  confidence_score?: number;
  rating?: number;
  isFavorite?: boolean;
  isWorn?: boolean;
  lastWorn?: string;
  wearCount?: number;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    color: string;
  }>;
  createdAt: string;
}

interface OutfitFilters {
  occasion?: string;
  style?: string;
  mood?: string;
  isFavorite?: boolean;
  isWorn?: boolean;
  search?: string;
}

interface ResponsiveOutfitGridProps {
  outfits: Outfit[];
  loading?: boolean;
  onFavorite: (id: string) => void;
  onWear: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
  onView?: (id: string) => void;
  onShare?: (id: string) => void;
  onRefresh?: () => void;
  className?: string;
}

export default function ResponsiveOutfitGrid({
  outfits,
  loading = false,
  onFavorite,
  onWear,
  onEdit,
  onDelete,
  onView,
  onShare,
  onRefresh,
  className = ""
}: ResponsiveOutfitGridProps) {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [sortBy, setSortBy] = useState<'newest' | 'oldest' | 'name' | 'rating' | 'worn'>('newest');
  const [filters, setFilters] = useState<OutfitFilters>({});
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Get unique values for filter options
  const occasions = useMemo(() => {
    const unique = [...new Set(outfits.map(o => o.occasion))];
    return unique.sort();
  }, [outfits]);

  const styles = useMemo(() => {
    const unique = [...new Set(outfits.map(o => o.style))];
    return unique.sort();
  }, [outfits]);

  const moods = useMemo(() => {
    const unique = [...new Set(outfits.map(o => o.mood).filter(Boolean))];
    return unique.sort();
  }, [outfits]);

  // Filter and sort outfits
  const filteredAndSortedOutfits = useMemo(() => {
    let filtered = outfits.filter(outfit => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesSearch = 
          outfit.name.toLowerCase().includes(query) ||
          outfit.occasion.toLowerCase().includes(query) ||
          outfit.style.toLowerCase().includes(query) ||
          (outfit.mood && outfit.mood.toLowerCase().includes(query)) ||
          outfit.items.some(item => 
            item.name.toLowerCase().includes(query) ||
            item.type.toLowerCase().includes(query)
          );
        if (!matchesSearch) return false;
      }

      // Other filters
      if (filters.occasion && outfit.occasion !== filters.occasion) return false;
      if (filters.style && outfit.style !== filters.style) return false;
      if (filters.mood && outfit.mood !== filters.mood) return false;
      if (filters.isFavorite !== undefined && outfit.isFavorite !== filters.isFavorite) return false;
      if (filters.isWorn !== undefined && outfit.isWorn !== filters.isWorn) return false;

      return true;
    });

    // Sort outfits
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'oldest':
          return new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime();
        case 'name':
          return a.name.localeCompare(b.name);
        case 'rating':
          return (b.rating || 0) - (a.rating || 0);
        case 'worn':
          return (b.wearCount || 0) - (a.wearCount || 0);
        default:
          return 0;
      }
    });

    return filtered;
  }, [outfits, searchQuery, filters, sortBy]);

  const clearFilters = () => {
    setFilters({});
    setSearchQuery('');
  };

  const activeFiltersCount = Object.values(filters).filter(Boolean).length + (searchQuery ? 1 : 0);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4">
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  <div className="grid grid-cols-2 gap-2">
                    <div className="aspect-square bg-gray-200 rounded"></div>
                    <div className="aspect-square bg-gray-200 rounded"></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Search and Controls */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search outfits..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Controls */}
        <div className="flex gap-2">
          {/* Filter Button */}
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="relative"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
            {activeFiltersCount > 0 && (
              <Badge variant="destructive" className="absolute -top-2 -right-2 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs">
                {activeFiltersCount}
              </Badge>
            )}
          </Button>

          {/* Sort */}
          <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest</SelectItem>
              <SelectItem value="oldest">Oldest</SelectItem>
              <SelectItem value="name">Name</SelectItem>
              <SelectItem value="rating">Rating</SelectItem>
              <SelectItem value="worn">Most Worn</SelectItem>
            </SelectContent>
          </Select>

          {/* View Mode */}
          <div className="flex border rounded-md">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('grid')}
              className="rounded-r-none"
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setViewMode('list')}
              className="rounded-l-none"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          {/* Refresh */}
          {onRefresh && (
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card>
          <CardContent className="p-4">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Filters</h3>
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  Clear All
                </Button>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Occasion Filter */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Occasion</label>
                  <Select 
                    value={filters.occasion || ''} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, occasion: value || undefined }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All occasions" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All occasions</SelectItem>
                      {occasions.map(occasion => (
                        <SelectItem key={occasion} value={occasion}>
                          {occasion}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Style Filter */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Style</label>
                  <Select 
                    value={filters.style || ''} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, style: value || undefined }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All styles" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All styles</SelectItem>
                      {styles.map(style => (
                        <SelectItem key={style} value={style}>
                          {style}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Mood Filter */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Mood</label>
                  <Select 
                    value={filters.mood || ''} 
                    onValueChange={(value) => setFilters(prev => ({ ...prev, mood: value || undefined }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All moods" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All moods</SelectItem>
                      {moods.map(mood => (
                        <SelectItem key={mood} value={mood}>
                          {mood}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Status Filter */}
                <div>
                  <label className="text-sm font-medium mb-1 block">Status</label>
                  <Select 
                    value={filters.isFavorite !== undefined ? (filters.isFavorite ? 'favorite' : 'not-favorite') : ''} 
                    onValueChange={(value) => {
                      if (value === 'favorite') {
                        setFilters(prev => ({ ...prev, isFavorite: true }));
                      } else if (value === 'not-favorite') {
                        setFilters(prev => ({ ...prev, isFavorite: false }));
                      } else {
                        setFilters(prev => ({ ...prev, isFavorite: undefined }));
                      }
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All outfits" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All outfits</SelectItem>
                      <SelectItem value="favorite">Favorites only</SelectItem>
                      <SelectItem value="not-favorite">Not favorites</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {filteredAndSortedOutfits.length} outfit{filteredAndSortedOutfits.length !== 1 ? 's' : ''} found
        </p>
        {activeFiltersCount > 0 && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="h-4 w-4 mr-1" />
            Clear filters
          </Button>
        )}
      </div>

      {/* Outfits Grid/List */}
      {filteredAndSortedOutfits.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="text-gray-400 mb-4">
              <Grid3X3 className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No outfits found</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {activeFiltersCount > 0 
                ? "Try adjusting your filters or search terms"
                : "Start by generating your first outfit!"
              }
            </p>
            {activeFiltersCount > 0 && (
              <Button onClick={clearFilters}>
                Clear filters
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className={
          viewMode === 'grid' 
            ? "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4"
            : "space-y-4"
        }>
          {filteredAndSortedOutfits.map((outfit) => (
            <EnhancedOutfitCard
              key={outfit.id}
              outfit={outfit}
              onFavorite={onFavorite}
              onWear={onWear}
              onEdit={onEdit}
              onDelete={onDelete}
              onView={onView}
              onShare={onShare}
              className={viewMode === 'list' ? 'flex flex-row' : ''}
            />
          ))}
        </div>
      )}
    </div>
  );
}
