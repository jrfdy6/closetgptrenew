"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import { 
  Filter, 
  Search, 
  X, 
  RefreshCw,
  Shirt,
  Palette,
  Calendar,
  Star,
  TrendingUp,
  Clock
} from "lucide-react";

interface WardrobeFiltersProps {
  onFiltersChange: (filters: WardrobeFilters) => void;
  onReset: () => void;
  className?: string;
}

export interface WardrobeFilters {
  search: string;
  types: string[];
  colors: string[];
  seasons: string[];
  occasions: string[];
  styles: string[];
  minWearCount: number;
  maxWearCount: number;
  favoritesOnly: boolean;
  unwornOnly: boolean;
  sortBy: 'name' | 'type' | 'color' | 'wearCount' | 'lastWorn' | 'createdAt';
  sortOrder: 'asc' | 'desc';
}

const defaultFilters: WardrobeFilters = {
  search: '',
  types: [],
  colors: [],
  seasons: [],
  occasions: [],
  styles: [],
  minWearCount: 0,
  maxWearCount: 100,
  favoritesOnly: false,
  unwornOnly: false,
  sortBy: 'name',
  sortOrder: 'asc'
};

const itemTypes = [
  { value: 'shirt', label: '👕 Shirt', icon: '👕' },
  { value: 'pants', label: '👖 Pants', icon: '👖' },
  { value: 'jacket', label: '🧥 Jacket', icon: '🧥' },
  { value: 'dress', label: '👗 Dress', icon: '👗' },
  { value: 'shoes', label: '👟 Shoes', icon: '👟' },
  { value: 'accessory', label: '💍 Accessory', icon: '💍' },
  { value: 'outerwear', label: '🧥 Outerwear', icon: '🧥' },
  { value: 'underwear', label: '🩲 Underwear', icon: '🩲' }
];

const colors = [
  { value: 'black', label: '⚫ Black', icon: '⚫' },
  { value: 'white', label: '⚪ White', icon: '⚪' },
  { value: 'blue', label: '🔵 Blue', icon: '🔵' },
  { value: 'red', label: '🔴 Red', icon: '🔴' },
  { value: 'green', label: '🟢 Green', icon: '🟢' },
  { value: 'yellow', label: '🟡 Yellow', icon: '🟡' },
  { value: 'purple', label: '🟣 Purple', icon: '🟣' },
  { value: 'pink', label: '🩷 Pink', icon: '🩷' },
  { value: 'brown', label: '🟤 Brown', icon: '🟤' },
  { value: 'gray', label: '⚪ Gray', icon: '⚪' },
  { value: 'multi', label: '🌈 Multi-color', icon: '🌈' }
];

const seasons = [
  { value: 'spring', label: '🌸 Spring', icon: '🌸' },
  { value: 'summer', label: '☀️ Summer', icon: '☀️' },
  { value: 'fall', label: '🍂 Fall', icon: '🍂' },
  { value: 'winter', label: '❄️ Winter', icon: '❄️' }
];

const occasions = [
  { value: 'casual', label: 'Casual', icon: '😊' },
  { value: 'work', label: 'Work', icon: '💼' },
  { value: 'formal', label: 'Formal', icon: '🎩' },
  { value: 'party', label: 'Party', icon: '🎉' },
  { value: 'date', label: 'Date', icon: '💕' },
  { value: 'sport', label: 'Sport', icon: '🏃' },
  { value: 'daily', label: 'Daily', icon: '📅' }
];

const styles = [
  { value: 'casual', label: 'Casual', icon: '😊' },
  { value: 'formal', label: 'Formal', icon: '🎩' },
  { value: 'streetwear', label: 'Streetwear', icon: '🛹' },
  { value: 'vintage', label: 'Vintage', icon: '📻' },
  { value: 'minimalist', label: 'Minimalist', icon: '⚪' },
  { value: 'bohemian', label: 'Bohemian', icon: '🌿' },
  { value: 'classic', label: 'Classic', icon: '👔' },
  { value: 'trendy', label: 'Trendy', icon: '🔥' },
  { value: 'artistic', label: 'Artistic', icon: '🎨' },
  { value: 'sporty', label: 'Sporty', icon: '🏃' }
];

const sortOptions = [
  { value: 'name', label: 'Name', icon: '📝' },
  { value: 'type', label: 'Type', icon: '👕' },
  { value: 'color', label: 'Color', icon: '🎨' },
  { value: 'wearCount', label: 'Wear Count', icon: '📊' },
  { value: 'lastWorn', label: 'Last Worn', icon: '📅' },
  { value: 'createdAt', label: 'Date Added', icon: '➕' }
];

export default function WardrobeFilters({ onFiltersChange, onReset, className }: WardrobeFiltersProps) {
  const [filters, setFilters] = useState<WardrobeFilters>(defaultFilters);
  const [isExpanded, setIsExpanded] = useState(false);

  const updateFilters = (newFilters: Partial<WardrobeFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    onFiltersChange(updatedFilters);
  };

  const handleReset = () => {
    setFilters(defaultFilters);
    onReset();
  };

  const toggleFilter = (filterType: keyof WardrobeFilters, value: string) => {
    const currentValues = filters[filterType] as string[];
    const newValues = currentValues.includes(value)
      ? currentValues.filter(v => v !== value)
      : [...currentValues, value];
    
    updateFilters({ [filterType]: newValues });
  };

  const clearFilter = (filterType: keyof WardrobeFilters) => {
    updateFilters({ [filterType]: filterType === 'search' ? '' : [] });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.search) count++;
    if (filters.types.length > 0) count++;
    if (filters.colors.length > 0) count++;
    if (filters.seasons.length > 0) count++;
    if (filters.occasions.length > 0) count++;
    if (filters.styles.length > 0) count++;
    if (filters.minWearCount > 0 || filters.maxWearCount < 100) count++;
    if (filters.favoritesOnly) count++;
    if (filters.unwornOnly) count++;
    return count;
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            <CardTitle className="text-lg">Filters</CardTitle>
            {activeFiltersCount > 0 && (
              <Badge variant="secondary" className="ml-2">
                {activeFiltersCount}
              </Badge>
            )}
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? 'Collapse' : 'Expand'}
            </Button>
            {activeFiltersCount > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
              >
                <RefreshCw className="w-4 h-4 mr-1" />
                Reset
              </Button>
            )}
          </div>
        </div>
        <CardDescription>
          Filter and sort your wardrobe items
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Search */}
        <div className="space-y-2">
          <Label htmlFor="search">Search Items</Label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              id="search"
              placeholder="Search by name, type, color..."
              value={filters.search}
              onChange={(e) => updateFilters({ search: e.target.value })}
              className="pl-10"
            />
            {filters.search && (
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                onClick={() => clearFilter('search')}
              >
                <X className="w-3 h-3" />
              </Button>
            )}
          </div>
        </div>

        {/* Quick Filters */}
        <div className="space-y-3">
          <Label>Quick Filters</Label>
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filters.favoritesOnly ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilters({ favoritesOnly: !filters.favoritesOnly })}
            >
              <Star className="w-4 h-4 mr-1" />
              Favorites Only
            </Button>
            <Button
              variant={filters.unwornOnly ? "default" : "outline"}
              size="sm"
              onClick={() => updateFilters({ unwornOnly: !filters.unwornOnly })}
            >
              <Clock className="w-4 h-4 mr-1" />
              Unworn Only
            </Button>
          </div>
        </div>

        {/* Sort Options */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Sort By</Label>
            <Select
              value={filters.sortBy}
              onValueChange={(value: WardrobeFilters['sortBy']) => 
                updateFilters({ sortBy: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {sortOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    <span className="mr-2">{option.icon}</span>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Order</Label>
            <Select
              value={filters.sortOrder}
              onValueChange={(value: 'asc' | 'desc') => 
                updateFilters({ sortOrder: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="asc">Ascending</SelectItem>
                <SelectItem value="desc">Descending</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Expanded Filters */}
        {isExpanded && (
          <>
            {/* Item Types */}
            <div className="space-y-3">
              <Label>Item Types</Label>
              <div className="grid grid-cols-2 gap-2">
                {itemTypes.map((type) => (
                  <div key={type.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`type-${type.value}`}
                      checked={filters.types.includes(type.value)}
                      onCheckedChange={() => toggleFilter('types', type.value)}
                    />
                    <Label htmlFor={`type-${type.value}`} className="text-sm">
                      {type.icon} {type.label.split(' ')[1]}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Colors */}
            <div className="space-y-3">
              <Label>Colors</Label>
              <div className="grid grid-cols-2 gap-2">
                {colors.map((color) => (
                  <div key={color.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`color-${color.value}`}
                      checked={filters.colors.includes(color.value)}
                      onCheckedChange={() => toggleFilter('colors', color.value)}
                    />
                    <Label htmlFor={`color-${color.value}`} className="text-sm">
                      {color.icon} {color.label.split(' ')[1]}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Seasons */}
            <div className="space-y-3">
              <Label>Seasons</Label>
              <div className="grid grid-cols-2 gap-2">
                {seasons.map((season) => (
                  <div key={season.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`season-${season.value}`}
                      checked={filters.seasons.includes(season.value)}
                      onCheckedChange={() => toggleFilter('seasons', season.value)}
                    />
                    <Label htmlFor={`season-${season.value}`} className="text-sm">
                      {season.icon} {season.label.split(' ')[1]}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Occasions */}
            <div className="space-y-3">
              <Label>Occasions</Label>
              <div className="grid grid-cols-2 gap-2">
                {occasions.map((occasion) => (
                  <div key={occasion.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`occasion-${occasion.value}`}
                      checked={filters.occasions.includes(occasion.value)}
                      onCheckedChange={() => toggleFilter('occasions', occasion.value)}
                    />
                    <Label htmlFor={`occasion-${occasion.value}`} className="text-sm">
                      {occasion.icon} {occasion.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Styles */}
            <div className="space-y-3">
              <Label>Styles</Label>
              <div className="grid grid-cols-2 gap-2">
                {styles.map((style) => (
                  <div key={style.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={`style-${style.value}`}
                      checked={filters.styles.includes(style.value)}
                      onCheckedChange={() => toggleFilter('styles', style.value)}
                    />
                    <Label htmlFor={`style-${style.value}`} className="text-sm">
                      {style.icon} {style.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Wear Count Range */}
            <div className="space-y-3">
              <Label>Wear Count Range</Label>
              <div className="space-y-4">
                <div className="flex items-center justify-between text-sm">
                  <span>Min: {filters.minWearCount}</span>
                  <span>Max: {filters.maxWearCount}</span>
                </div>
                <Slider
                  value={[filters.minWearCount, filters.maxWearCount]}
                  onValueChange={([min, max]) => 
                    updateFilters({ minWearCount: min, maxWearCount: max })
                  }
                  max={100}
                  step={1}
                  className="w-full"
                />
              </div>
            </div>
          </>
        )}

        {/* Active Filters Display */}
        {activeFiltersCount > 0 && (
          <div className="space-y-3">
            <Label>Active Filters</Label>
            <div className="flex flex-wrap gap-2">
              {filters.search && (
                <Badge variant="secondary" className="gap-1">
                  Search: "{filters.search}"
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1"
                    onClick={() => clearFilter('search')}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              )}
              {filters.types.map((type) => (
                <Badge key={type} variant="secondary" className="gap-1">
                  Type: {type}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1"
                    onClick={() => toggleFilter('types', type)}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              ))}
              {filters.colors.map((color) => (
                <Badge key={color} variant="secondary" className="gap-1">
                  Color: {color}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1"
                    onClick={() => toggleFilter('colors', color)}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              ))}
              {filters.favoritesOnly && (
                <Badge variant="secondary" className="gap-1">
                  Favorites Only
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1"
                    onClick={() => updateFilters({ favoritesOnly: false })}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              )}
              {filters.unwornOnly && (
                <Badge variant="secondary" className="gap-1">
                  Unworn Only
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-4 w-4 p-0 ml-1"
                    onClick={() => updateFilters({ unwornOnly: false })}
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </Badge>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
