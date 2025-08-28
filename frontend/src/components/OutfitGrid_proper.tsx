"use client";

import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Heart, HeartOff, Eye, Edit, Trash2, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';

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

interface OutfitFiltersProps {
  filters: OutfitFilters;
  onFiltersChange: (filters: OutfitFilters) => void;
  onSearch: (query: string) => void;
  onClear: () => void;
}

// ===== OUTFIT CARD COMPONENT =====
function OutfitCard({ outfit, onFavorite, onWear, onEdit, onDelete }: OutfitCardProps) {
  const handleFavorite = () => onFavorite(outfit.id);
  const handleWear = () => onWear(outfit.id);
  const handleEdit = () => onEdit(outfit.id);
  const handleDelete = () => onDelete(outfit.id);

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
          <span>Worn {outfit.wearCount || 0} times</span>
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
            onClick={handleDelete}
            className="text-xs text-red-600 hover:text-red-700"
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
    </Card>
  );
}

// ===== FILTERS COMPONENT =====
function OutfitFiltersComponent({ filters, onFiltersChange, onSearch, onClear }: OutfitFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    onSearch(searchQuery);
  };

  const handleClear = () => {
    setSearchQuery('');
    onClear();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search Input */}
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
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
          <label className="block text-sm font-medium text-gray-700 mb-2">
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
          <label className="block text-sm font-medium text-gray-700 mb-2">
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
      </div>

      {/* Action Buttons */}
      <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-500">
          {filters.occasion && filters.occasion !== 'all' && `Occasion: ${filters.occasion}`}
          {filters.style && filters.style !== 'all' && ` Style: ${filters.style}`}
          {((filters.occasion && filters.occasion !== 'all') || (filters.style && filters.style !== 'all')) && ' • '}
          <span>Showing filtered results</span>
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
  maxOutfits = 50,
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
    error, 
    fetchOutfits, 
    markAsWorn, 
    toggleFavorite, 
    updateOutfit, 
    deleteOutfit, 
    clearError, 
    refresh 
  } = useOutfits();

  // ===== LOCAL STATE =====
  const [filters, setFilters] = useState<OutfitFilters>({ limit: maxOutfits });
  const [searchResults, setSearchResults] = useState<Outfit[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // ===== COMPUTED VALUES =====
  const filteredOutfits = useMemo(() => {
    if (isSearching && searchResults.length > 0) {
      return searchResults;
    }
    return outfits;
  }, [outfits, searchResults, isSearching]);

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
          <Button onClick={refresh} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
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

      {/* Loading More Indicator */}
      {loading && outfits.length > 0 && (
        <div className="text-center py-4">
          <RefreshCw className="h-6 w-6 animate-spin text-gray-400 mx-auto" />
          <p className="text-gray-500 text-sm mt-2">Loading more outfits...</p>
        </div>
      )}
    </div>
  );
}
