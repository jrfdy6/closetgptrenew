'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { X, Save, RotateCcw, Palette, Calendar, Tag, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Outfit, OutfitUpdate, OutfitItem } from '@/lib/services/outfitService';
import { ClothingItem } from '@/lib/services/outfitService';
import { useWardrobe } from '@/lib/hooks/useWardrobe';
import { useOutfits } from '@/lib/hooks/useOutfits';
import { toClothingItem, toOutfitItem, filterValidItems, getInvalidItems } from '@/lib/adapters/itemAdapter';
import OutfitItemSelector from './OutfitItemSelector';

interface OutfitEditModalProps {
  outfit: Outfit;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updates: OutfitUpdate) => Promise<void>;
}

const OCCASIONS = [
  'casual',
  'work',
  'formal',
  'party',
  'date',
  'gym',
  'travel',
  'home',
  'outdoor',
  'special'
];

const STYLES = [
  'classic',
  'modern',
  'vintage',
  'bohemian',
  'minimalist',
  'edgy',
  'romantic',
  'sporty',
  'preppy',
  'streetwear'
];

export default function OutfitEditModal({ 
  outfit, 
  isOpen, 
  onClose, 
  onSave 
}: OutfitEditModalProps) {
  const { items: wardrobeItems } = useWardrobe();
  const { updateOutfit, fetchOutfit } = useOutfits();
  
  const [formData, setFormData] = useState({
    name: outfit.name || '',
    occasion: outfit.occasion || '',
    style: outfit.style || '',
    description: outfit.description || '',
    notes: outfit.notes || ''
  });
  
  const [selectedItems, setSelectedItems] = useState<ClothingItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Note: Conversion functions are now handled by the itemAdapter

  // Check if any changes were made to the outfit
  const hasChanges = useCallback(() => {
    if (!outfit) return false;
    
    // Check form data changes
    const formChanged = 
      formData.name !== (outfit.name || '') ||
      formData.occasion !== (outfit.occasion || '') ||
      formData.style !== (outfit.style || '') ||
      formData.description !== (outfit.description || '') ||
      formData.notes !== (outfit.notes || '');
    
    // Check items changes
    const currentItems = (outfit.items || []).map(toClothingItem);
    const itemsChanged = 
      selectedItems.length !== currentItems.length ||
      !selectedItems.every(item => 
        currentItems.some(currentItem => currentItem.id === item.id)
      );
    
    return formChanged || itemsChanged;
  }, [outfit, formData, selectedItems]);

  // Reset form state with fresh data from server
  const resetFormWithFreshData = useCallback(async () => {
    try {
      console.log('🔄 [OutfitEditModal] Re-fetching outfit data for error recovery');
      await fetchOutfit(outfit.id);
      
      // The form will be reset by the useEffect when the outfit prop changes
      // This ensures we have the latest data from the server
    } catch (error) {
      console.error('❌ [OutfitEditModal] Failed to re-fetch outfit data:', error);
      setErrors({ 
        general: 'Failed to refresh outfit data. Please close and reopen the modal.' 
      });
    }
  }, [fetchOutfit, outfit.id]);

  // Reset form when outfit changes
  useEffect(() => {
    if (outfit) {
      setFormData({
        name: outfit.name || '',
        occasion: outfit.occasion || '',
        style: outfit.style || '',
        description: outfit.description || '',
        notes: outfit.notes || ''
      });
      // Convert OutfitItem[] to ClothingItem[] using adapter
      const clothingItems = (outfit.items || []).map(toClothingItem);
      setSelectedItems(clothingItems);
      setErrors({});
    }
  }, [outfit]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleItemChange = (newItems: ClothingItem[]) => {
    setSelectedItems(newItems);
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Outfit name is required';
    }
    
    if (!formData.occasion) {
      newErrors.occasion = 'Occasion is required';
    }
    
    if (!formData.style) {
      newErrors.style = 'Style is required';
    }
    
    if (selectedItems.length === 0) {
      newErrors.items = 'At least one item is required';
    }
    
    // Validate that all selected items still exist in wardrobe using adapter
    const invalidItems = getInvalidItems(selectedItems, wardrobeItems);
    
    if (invalidItems.length > 0) {
      newErrors.items = `The following items are no longer in your wardrobe: ${invalidItems.map(item => item.name).join(', ')}. Please remove them or add them back to your wardrobe.`;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = async () => {
    // Check if there are any changes to save
    if (!hasChanges()) {
      setErrors({ general: 'No changes were made to save.' });
      return;
    }

    if (!validateForm()) {
      return;
    }

    // Additional safety: filter out any items that are no longer in wardrobe using adapter
    const validItems = filterValidItems(selectedItems, wardrobeItems);

    // If we filtered out items, update the selected items and show a warning
    if (validItems.length !== selectedItems.length) {
      const removedItems = getInvalidItems(selectedItems, wardrobeItems);
      setSelectedItems(validItems);
      setErrors({ 
        general: `Removed ${removedItems.length} item(s) that are no longer in your wardrobe: ${removedItems.map(item => item.name).join(', ')}` 
      });
      return; // Let user review the changes before saving again
    }

    setIsLoading(true);
    try {
      const updates: OutfitUpdate = {
        name: formData.name.trim(),
        occasion: formData.occasion,
        style: formData.style,
        description: formData.description.trim() || undefined,
        notes: formData.notes.trim() || undefined,
        items: validItems.map(toOutfitItem)
        // updatedAt will be set by the backend
      };

      await onSave(updates);
      onClose();
    } catch (error) {
      console.error('Failed to save outfit:', error);
      setErrors({ 
        general: 'Failed to save outfit. Refreshing data from server...' 
      });
      
      // Re-fetch the original outfit data to reset form state
      await resetFormWithFreshData();
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setFormData({
      name: outfit.name || '',
      occasion: outfit.occasion || '',
      style: outfit.style || '',
      description: outfit.description || '',
      notes: outfit.notes || ''
    });
    const clothingItems = (outfit.items || []).map(toClothingItem);
    setSelectedItems(clothingItems);
    setErrors({});
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-xl flex items-center justify-center z-50 p-4">
      <div className="bg-white/90 dark:bg-[#0D0D0D]/90 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 bg-white/60 dark:bg-[#1A1A1A]/40 backdrop-blur">
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
              Edit outfit
            </h2>
            {hasChanges() && (
              <div className="flex items-center gap-1 px-2 py-1 bg-[#FFF7E6] text-[#B45309] text-xs font-semibold rounded-full border border-[#FFB84C]/30">
                <div className="w-2 h-2 bg-[#FF9400] rounded-full"></div>
                Unsaved changes
              </div>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="h-9 w-9 p-0 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-152px)] bg-white/40 dark:bg-[#0D0D0D]/40 backdrop-blur-sm">
          {errors.general && (
            <div className="mb-4 p-4 bg-[#FFF0EC] border border-[#FF6F61]/40 rounded-2xl">
              <div className="flex items-start gap-2">
                <span className="text-[#FF6F61] text-lg">⚠️</span>
                <div>
                  <p className="text-sm font-semibold text-[#7F1D1D]">Something needs attention</p>
                  <p className="text-sm text-[#B42318] mt-1">{errors.general}</p>
                </div>
              </div>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column - Basic Info */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] flex items-center gap-2">
                <FileText className="h-5 w-5 text-[#FFB84C]" />
                Basic information
              </h3>
              
              {/* Name */}
              <div className="space-y-2">
                <Label htmlFor="name" className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                  Outfit name *
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  placeholder="Enter outfit name"
                  className={cn(
                    "bg-white/80 dark:bg-[#0D0D0D]/80 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 focus:border-[#FFB84C] focus:ring-[#FFB84C]/20",
                    errors.name && 'border-[#FF6F61] focus:border-[#FF6F61] focus:ring-[#FF6F61]/20'
                  )}
                />
                {errors.name && (
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-[#FF6F61] text-sm">⚠️</span>
                    <p className="text-sm text-[#B42318] font-medium">{errors.name}</p>
                  </div>
                )}
              </div>

              {/* Occasion */}
              <div className="space-y-2">
                <Label htmlFor="occasion" className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                  Occasion *
                </Label>
                <Select
                  value={formData.occasion}
                  onValueChange={(value) => handleInputChange('occasion', value)}
                >
                  <SelectTrigger className={cn(
                    "border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 bg-white/80 dark:bg-[#0D0D0D]/80 focus:border-[#FFB84C] focus:ring-[#FFB84C]/20",
                    errors.occasion && 'border-[#FF6F61] focus:border-[#FF6F61] focus:ring-[#FF6F61]/20'
                  )}>
                    <SelectValue placeholder="Select occasion" />
                  </SelectTrigger>
                  <SelectContent>
                    {OCCASIONS.map((occasion) => (
                      <SelectItem key={occasion} value={occasion}>
                        {occasion.charAt(0).toUpperCase() + occasion.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.occasion && (
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-[#FF6F61] text-sm">⚠️</span>
                    <p className="text-sm text-[#B42318] font-medium">{errors.occasion}</p>
                  </div>
                )}
              </div>

              {/* Style */}
              <div className="space-y-2">
                <Label htmlFor="style" className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                  Style *
                </Label>
                <Select
                  value={formData.style}
                  onValueChange={(value) => handleInputChange('style', value)}
                >
                  <SelectTrigger className={cn(
                    "border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 bg-white/80 dark:bg-[#0D0D0D]/80 focus:border-[#FFB84C] focus:ring-[#FFB84C]/20",
                    errors.style && 'border-[#FF6F61] focus:border-[#FF6F61] focus:ring-[#FF6F61]/20'
                  )}>
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((style) => (
                      <SelectItem key={style} value={style}>
                        {style.charAt(0).toUpperCase() + style.slice(1)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.style && (
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-[#FF6F61] text-sm">⚠️</span>
                    <p className="text-sm text-[#B42318] font-medium">{errors.style}</p>
                  </div>
                )}
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                  Description
                </Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  placeholder="Describe this outfit..."
                  rows={3}
                  className="bg-white/80 dark:bg-[#0D0D0D]/80 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 focus:border-[#FFB84C] focus:ring-[#FFB84C]/20"
                />
              </div>

              {/* Notes */}
              <div className="space-y-2">
                <Label htmlFor="notes" className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">
                  Personal notes
                </Label>
                <Textarea
                  id="notes"
                  value={formData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="Add personal notes about this outfit..."
                  rows={2}
                  className="bg-white/80 dark:bg-[#0D0D0D]/80 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 focus:border-[#FFB84C] focus:ring-[#FFB84C]/20"
                />
              </div>
            </div>

            {/* Right Column - Items */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1] flex items-center gap-2">
                <Palette className="h-5 w-5 text-[#FFB84C]" />
                Outfit items
              </h3>
              
              <OutfitItemSelector
                selectedItems={selectedItems}
                onItemsChange={handleItemChange}
                wardrobeItems={wardrobeItems}
                error={errors.items}
                showValidation={true}
              />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 bg-white/60 dark:bg-[#1A1A1A]/60 backdrop-blur">
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={isLoading}
              className="flex items-center gap-2 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <RotateCcw className="h-4 w-4" />
              Reset
            </Button>
            <Button
              variant="outline"
              onClick={resetFormWithFreshData}
              disabled={isLoading}
              className="flex items-center gap-2 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              <RotateCcw className="h-4 w-4" />
              Refresh data
            </Button>
          </div>
          
          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={onClose}
              disabled={isLoading}
              className="px-5 rounded-2xl border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={isLoading || !hasChanges()}
              className="flex items-center gap-2 px-5 rounded-2xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white shadow-lg shadow-amber-500/20 hover:scale-[1.02] transition-transform"
            >
              <Save className="h-4 w-4" />
              {isLoading ? 'Saving...' : hasChanges() ? 'Save changes' : 'No changes'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
