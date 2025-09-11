'use client';

import React, { useState, useMemo } from 'react';
import { Search, Plus, X, Shirt, Watch, Filter, Footprints, ShoppingBag } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { ClothingItem } from '@/lib/services/outfitService';
import { cn } from '@/lib/utils';
import { getInvalidItems } from '@/lib/adapters/itemAdapter';

interface OutfitItemSelectorProps {
  selectedItems: ClothingItem[];
  onItemsChange: (items: ClothingItem[]) => void;
  wardrobeItems: ClothingItem[];
  error?: string;
  maxItems?: number;
  showValidation?: boolean; // New prop to enable validation display
}

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

const ITEM_TYPES = [
  'top',
  'bottom', 
  'shoes',
  'accessories',
  'bag',
  'outerwear',
  'underwear',
  'jewelry',
  'other'
];

export default function OutfitItemSelector({
  selectedItems,
  onItemsChange,
  wardrobeItems,
  error,
  maxItems = 10,
  showValidation = false
}: OutfitItemSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string>('all');
  const [showAddItems, setShowAddItems] = useState(false);

  // Filter wardrobe items based on search and type
  const filteredItems = useMemo(() => {
    return wardrobeItems.filter(item => {
      const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.color?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           item.brand?.toLowerCase().includes(searchQuery.toLowerCase());
      
      const matchesType = selectedType === 'all' || item.type === selectedType;
      
      // Don't show items that are already selected
      const notSelected = !selectedItems.some(selected => selected.id === item.id);
      
      return matchesSearch && matchesType && notSelected;
    });
  }, [wardrobeItems, searchQuery, selectedType, selectedItems]);

  // Group items by type for better organization
  const groupedItems = useMemo(() => {
    const groups: Record<string, ClothingItem[]> = {};
    filteredItems.forEach(item => {
      if (!groups[item.type]) {
        groups[item.type] = [];
      }
      groups[item.type].push(item);
    });
    return groups;
  }, [filteredItems]);

  const handleAddItem = (item: ClothingItem) => {
    if (selectedItems.length >= maxItems) {
      return;
    }
    onItemsChange([...selectedItems, item]);
  };

  const handleRemoveItem = (itemId: string) => {
    onItemsChange(selectedItems.filter(item => item.id !== itemId));
  };

  const getItemIcon = (type: string) => {
    const IconComponent = ITEM_TYPE_ICONS[type as keyof typeof ITEM_TYPE_ICONS] || ITEM_TYPE_ICONS.other;
    return <IconComponent className="h-4 w-4" />;
  };

  const getItemTypeCount = (type: string) => {
    return selectedItems.filter(item => item.type === type).length;
  };

  // Check which selected items are no longer in wardrobe using adapter
  const invalidItems = showValidation ? getInvalidItems(selectedItems, wardrobeItems) : [];

  return (
    <div className="space-y-4">
      {/* Selected Items Display */}
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">
            Selected Items ({selectedItems.length}/{maxItems})
          </Label>
          {selectedItems.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => onItemsChange([])}
              className="h-7 px-2 text-xs"
            >
              Clear All
            </Button>
          )}
        </div>
        
        {selectedItems.length === 0 ? (
          <div className="text-center py-8 text-gray-500 border-2 border-dashed border-gray-200 rounded-lg">
            <Shirt className="h-8 w-8 mx-auto mb-2 text-gray-400" />
            <p className="text-sm">No items selected</p>
            <p className="text-xs text-gray-400">Add items from your wardrobe below</p>
          </div>
        ) : (
          <div className="space-y-2">
            {/* Validation warning for invalid items */}
            {showValidation && invalidItems.length > 0 && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600 font-medium mb-1">
                  ⚠️ Some items are no longer in your wardrobe
                </p>
                <p className="text-xs text-red-500">
                  Remove these items or add them back to your wardrobe before saving
                </p>
              </div>
            )}
            
            <div className="grid grid-cols-2 gap-2">
              {selectedItems.map((item) => {
                const isInvalid = invalidItems.some(invalid => invalid.id === item.id);
                return (
                  <div
                    key={item.id}
                    className={cn(
                      "flex items-center gap-2 p-2 rounded-lg border",
                      isInvalid 
                        ? "bg-red-50 border-red-200" 
                        : "bg-gray-50 border-gray-200"
                    )}
                  >
                    <div className="flex-shrink-0">
                      {item.imageUrl ? (
                        <img
                          src={item.imageUrl}
                          alt={item.name}
                          className="w-8 h-8 rounded object-cover"
                        />
                      ) : (
                        <div className="w-8 h-8 bg-gray-200 rounded flex items-center justify-center">
                          {getItemIcon(item.type)}
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={cn(
                        "text-xs font-medium truncate",
                        isInvalid ? "text-red-700" : "text-gray-900"
                      )}>
                        {item.name}
                        {isInvalid && " (Not in wardrobe)"}
                      </p>
                      <p className={cn(
                        "text-xs capitalize",
                        isInvalid ? "text-red-500" : "text-gray-500"
                      )}>
                        {item.type} • {item.color}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveItem(item.id)}
                      className={cn(
                        "h-6 w-6 p-0",
                        isInvalid 
                          ? "text-red-400 hover:text-red-600" 
                          : "text-gray-400 hover:text-red-600"
                      )}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  </div>
                );
              })}
            </div>
          </div>
        )}
        
        {error && (
          <p className="text-sm text-red-600">{error}</p>
        )}
      </div>

      {/* Add Items Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <Label className="text-sm font-medium">Add Items from Wardrobe</Label>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAddItems(!showAddItems)}
            className="h-7 px-2 text-xs"
          >
            <Plus className="h-3 w-3 mr-1" />
            {showAddItems ? 'Hide' : 'Show'} Items
          </Button>
        </div>

        {showAddItems && (
          <div className="space-y-3">
            {/* Search and Filter */}
            <div className="space-y-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search items..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              
              <div className="flex flex-wrap gap-1">
                <Button
                  variant={selectedType === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedType('all')}
                  className="h-7 text-xs"
                >
                  All
                </Button>
                {ITEM_TYPES.map((type) => {
                  const count = getItemTypeCount(type);
                  return (
                    <Button
                      key={type}
                      variant={selectedType === type ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setSelectedType(type)}
                      className="h-7 text-xs capitalize"
                    >
                      {type}
                      {count > 0 && (
                        <Badge variant="secondary" className="ml-1 h-4 px-1 text-xs">
                          {count}
                        </Badge>
                      )}
                    </Button>
                  );
                })}
              </div>
            </div>

            {/* Items List */}
            <div className="max-h-64 overflow-y-auto border rounded-lg">
              {Object.keys(groupedItems).length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Shirt className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                  <p className="text-sm">No items found</p>
                  <p className="text-xs text-gray-400">
                    {searchQuery ? 'Try a different search term' : 'Add items to your wardrobe first'}
                  </p>
                </div>
              ) : (
                <div className="divide-y">
                  {Object.entries(groupedItems).map(([type, items]) => (
                    <div key={type} className="p-2">
                      <div className="flex items-center gap-2 mb-2">
                        {getItemIcon(type)}
                        <span className="text-xs font-medium text-gray-700 capitalize">
                          {type} ({items.length})
                        </span>
                      </div>
                      <div className="grid grid-cols-1 gap-1">
                        {items.map((item) => (
                          <Button
                            key={item.id}
                            variant="ghost"
                            size="sm"
                            onClick={() => handleAddItem(item)}
                            disabled={selectedItems.length >= maxItems}
                            className="h-auto p-2 justify-start text-left"
                          >
                            <div className="flex items-center gap-2 w-full">
                              <div className="flex-shrink-0">
                                {item.imageUrl ? (
                                  <img
                                    src={item.imageUrl}
                                    alt={item.name}
                                    className="w-6 h-6 rounded object-cover"
                                  />
                                ) : (
                                  <div className="w-6 h-6 bg-gray-200 rounded flex items-center justify-center">
                                    {getItemIcon(item.type)}
                                  </div>
                                )}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-xs font-medium text-gray-900 truncate">
                                  {item.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {item.color} • {item.brand}
                                </p>
                              </div>
                              <Plus className="h-3 w-3 text-gray-400 flex-shrink-0" />
                            </div>
                          </Button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
