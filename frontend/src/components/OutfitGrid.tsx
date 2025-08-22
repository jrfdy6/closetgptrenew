import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Heart, Star, Calendar, Filter, Search, RefreshCw } from 'lucide-react';
import useOutfits, { Outfit, OutfitFilters } from '@/lib/hooks/useOutfits';
import { cn } from '@/lib/utils';

// ===== COMPONENT INTERFACE =====
interface OutfitGridProps {
  className?: string;
  showFilters?: boolean;
  showSearch?: boolean;
  maxOutfits?: number;
}

// ===== OUTFIT CARD COMPONENT =====
interface OutfitCardProps {
  outfit: Outfit;
  onFavorite: (id: string) => void;
  onWear: (id: string) => void;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

function OutfitCard({ outfit, onFavorite, onWear, onEdit, onDelete }: OutfitCardProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getOccasionColor = (occasion: string) => {
    const colors: Record<string, string> = {
      'Casual': 'bg-blue-100 text-blue-800',
      'Formal': 'bg-purple-100 text-purple-800',
      'Business': 'bg-green-100 text-green-800',
      'Athletic': 'bg-orange-100 text-orange-800',
      'Party': 'bg-pink-100 text-pink-800',
      'Work': 'bg-gray-100 text-gray-800',
      'School': 'bg-indigo-100 text-indigo-800',
      'Gala': 'bg-red-100 text-red-800',
      'Beach': 'bg-yellow-100 text-yellow-800',
      'Travel': 'bg-teal-100 text-teal-800',
    };
    return colors[occasion] || 'bg-gray-100 text-gray-800';
  };

  const getStyleColor = (style: string) => {
    const colors: Record<string, string> = {
      'Classic': 'bg-slate-100 text-slate-800',
      'Modern': 'bg-cyan-100 text-cyan-800',
      'Vintage': 'bg-amber-100 text-amber-800',
      'Streetwear': 'bg-emerald-100 text-emerald-800',
      'Bohemian': 'bg-rose-100 text-rose-800',
      'Minimalist': 'bg-neutral-100 text-neutral-800',
      'Artsy': 'bg-violet-100 text-violet-800',
      'Dark Academia': 'bg-stone-100 text-stone-800',
    };
    return colors[style] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card 
      className={cn(
        "group relative overflow-hidden transition-all duration-300 hover:shadow-lg",
        isHovered && "ring-2 ring-primary/20"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Favorite Button */}
      <Button
        variant="ghost"
        size="sm"
        className={cn(
          "absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity",
          outfit.isFavorite && "opacity-100 text-red-500"
        )}
        onClick={() => onFavorite(outfit.id)}
      >
        <Heart className={cn("h-4 w-4", outfit.isFavorite && "fill-current")} />
      </Button>

      {/* Outfit Image Placeholder */}
      <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div className="text-2xl mb-2">👕</div>
          <div className="text-sm font-medium">{outfit.name}</div>
        </div>
      </div>

      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold truncate">{outfit.name}</CardTitle>
        
        {/* Badges */}
        <div className="flex flex-wrap gap-1">
          <Badge className={getOccasionColor(outfit.occasion)} variant="secondary">
            {outfit.occasion}
          </Badge>
          <Badge className={getStyleColor(outfit.style)} variant="secondary">
            {outfit.style}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Stats */}
        <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{outfit.wearCount || 0} wears</span>
          </div>
          {outfit.confidenceScore && (
            <div className="flex items-center gap-1">
              <Star className="h-3 w-3" />
              <span>{Math.round(outfit.confidenceScore * 100)}%</span>
            </div>
          )}
        </div>

        {/* Items Count */}
        <div className="text-sm text-gray-500 mb-3">
          {outfit.items.length} items
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={() => onWear(outfit.id)}
          >
            Wear
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onEdit(outfit.id)}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="ghost"
            className="text-red-600 hover:text-red-700"
            onClick={() => onDelete(outfit.id)}
          >
            Delete
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// ===== FILTERS COMPONENT =====
interface OutfitFiltersProps {
  filters: OutfitFilters;
  onFiltersChange: (filters: OutfitFilters) => void;
  onSearch: (query: string) => void;
  onClear: () => void;
}

function OutfitFilters({ filters, onFiltersChange, onSearch, onClear }: OutfitFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = () => {
    onSearch(searchQuery);
  };

  const handleClear = () => {
    setSearchQuery('');
    onClear();
  };

  return (
    <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-4">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Filter className="h-5 w-5" />
          Filters & Search
        </h3>
        <Button variant="outline" size="sm" onClick={handleClear}>
          Clear All
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Search */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Search</label>
          <div className="flex gap-2">
            <Input
              placeholder="Search outfits..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
            <Button size="sm" onClick={handleSearch}>
              <Search className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Occasion Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Occasion</label>
          <Select
            value={filters.occasion || ''}
            onValueChange={(value) => onFiltersChange({ ...filters, occasion: value || undefined })}
          >
            <SelectTrigger>
              <SelectValue placeholder="All occasions" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All occasions</SelectItem>
              <SelectItem value="Casual">Casual</SelectItem>
              <SelectItem value="Formal">Formal</SelectItem>
              <SelectItem value="Business">Business</SelectItem>
              <SelectItem value="Athletic">Athletic</SelectItem>
              <SelectItem value="Party">Party</SelectItem>
              <SelectItem value="Work">Work</SelectItem>
              <SelectItem value="School">School</SelectItem>
              <SelectItem value="Gala">Gala</SelectItem>
              <SelectItem value="Beach">Beach</SelectItem>
              <SelectItem value="Travel">Travel</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Style Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Style</label>
          <Select
            value={filters.style || ''}
            onValueChange={(value) => onFiltersChange({ ...filters, style: value || undefined })}
          >
            <SelectTrigger>
              <SelectValue placeholder="All styles" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All styles</SelectItem>
              <SelectItem value="Classic">Classic</SelectItem>
              <SelectItem value="Modern">Modern</SelectItem>
              <SelectItem value="Vintage">Vintage</SelectItem>
              <SelectItem value="Streetwear">Streetwear</SelectItem>
              <SelectItem value="Bohemian">Bohemian</SelectItem>
              <SelectItem value="Minimalist">Minimalist</SelectItem>
              <SelectItem value="Artsy">Artsy</SelectItem>
              <SelectItem value="Dark Academia">Dark Academia</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Limit Filter */}
        <div className="space-y-2">
          <label className="text-sm font-medium">Show</label>
          <Select
            value={String(filters.limit || 50)}
            onValueChange={(value) => onFiltersChange({ ...filters, limit: parseInt(value) })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="20">20 outfits</SelectItem>
              <SelectItem value="50">50 outfits</SelectItem>
              <SelectItem value="100">100 outfits</SelectItem>
              <SelectItem value="1000">All outfits</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}

// ===== MAIN COMPONENT =====
export default function OutfitGrid({ 
  className, 
  showFilters = true, 
  showSearch = true, 
  maxOutfits 
}: OutfitGridProps) {
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

  const [filters, setFilters] = useState<OutfitFilters>({
    limit: maxOutfits || 50
  });

  const [searchResults, setSearchResults] = useState<Outfit[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  // Apply filters
  const filteredOutfits = searchResults.length > 0 ? searchResults : outfits;

  // Handle filter changes
  const handleFiltersChange = (newFilters: OutfitFilters) => {
    setFilters(newFilters);
    setSearchResults([]); // Clear search results when filters change
    fetchOutfits(newFilters);
  };

  // Handle search
  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      // Simple client-side search for now
      const results = outfits.filter(outfit => 
        outfit.name.toLowerCase().includes(query.toLowerCase()) ||
        outfit.occasion.toLowerCase().includes(query.toLowerCase()) ||
        outfit.style.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  // Handle clear
  const handleClear = () => {
    setFilters({ limit: maxOutfits || 50 });
    setSearchResults([]);
    fetchOutfits({ limit: maxOutfits || 50 });
  };

  // Handle actions
  const handleFavorite = async (id: string) => {
    await toggleFavorite(id);
  };

  const handleWear = async (id: string) => {
    await markAsWorn(id);
  };

  const handleEdit = (id: string) => {
    // TODO: Implement edit modal/form
    console.log('Edit outfit:', id);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this outfit?')) {
      await deleteOutfit(id);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-lg font-medium">Loading your outfits...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="text-red-500 text-lg mb-4">❌ Error loading outfits</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-2">
            <Button onClick={clearError}>Clear Error</Button>
            <Button onClick={refresh} variant="outline">Try Again</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">My Outfits</h2>
          <p className="text-gray-600">
            {filteredOutfits.length} outfit{filteredOutfits.length !== 1 ? 's' : ''} found
          </p>
        </div>
        <Button onClick={refresh} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Filters */}
      {showFilters && (
        <OutfitFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onSearch={handleSearch}
          onClear={handleClear}
        />
      )}

      {/* Search Results Indicator */}
      {searchResults.length > 0 && (
        <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
          <span className="text-blue-800">
            🔍 Showing {searchResults.length} search results
          </span>
          <Button 
            variant="ghost" 
            size="sm" 
            onClick={() => setSearchResults([])}
            className="text-blue-600 hover:text-blue-700"
          >
            Clear Search
          </Button>
        </div>
      )}

      {/* Outfits Grid */}
      {filteredOutfits.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">👕</div>
          <h3 className="text-xl font-medium text-gray-600 mb-2">No outfits found</h3>
          <p className="text-gray-500">
            {searchResults.length > 0 
              ? "Try adjusting your search terms or filters"
              : "Create your first outfit to get started!"
            }
          </p>
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
    </div>
  );
}
