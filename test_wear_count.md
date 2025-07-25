# Wear Count Testing Guide

## Overview
The wear count feature tracks how many times each wardrobe item has been worn. This is automatically incremented when users click "Mark as Worn" on outfit pages.

## Features Implemented

### 1. Database Schema Updates
- Added `wearCount` field to ClothingItem schema (default: 0)
- Added `lastWorn` field to track when item was last worn (default: null)

### 2. Backend Updates
- Modified `/api/outfit-history/mark-worn` endpoint to increment wear counts for all items in an outfit
- Uses Firestore batch updates for efficiency

### 3. Frontend Updates
- Updated WardrobeGrid to display wear count badges
- Added wear count filtering options
- Added wear count statistics to wardrobe header
- Added manual "Mark as Worn" button for testing

### 4. API Endpoints
- `/api/wardrobe/increment-wear` - Manual wear count increment for testing

## Testing Steps

### 1. Test Manual Wear Count Increment
1. Go to `/wardrobe` page
2. Find any item in your wardrobe
3. Click the green "W" button (Mark as Worn)
4. Verify the wear count badge appears/updates
5. Check the wardrobe header shows updated statistics

### 2. Test Outfit Wear Tracking
1. Go to `/outfits` page
2. Find an outfit and click "Mark as Worn"
3. Go back to `/wardrobe` page
4. Verify all items in that outfit have incremented wear counts

### 3. Test Wear Count Filtering
1. Go to `/wardrobe` page
2. Click the "Filter" button
3. Select different wear count options:
   - "Never Worn" (wearCount = 0)
   - "Worn Once" (wearCount = 1)
   - "Worn 2+ Times" (wearCount >= 2)
   - "Worn 5+ Times" (wearCount >= 5)
   - "Worn 10+ Times" (wearCount >= 10)
4. Verify items are filtered correctly

### 4. Test Wear Count Display
1. Items with wearCount > 0 show a blue badge: "Worn X time(s)"
2. Wardrobe header shows total wears and items worn
3. Wear counts persist after page refresh

## Expected Behavior

### Wear Count Badge
- Only appears when wearCount > 0
- Shows "Worn 1 time" for single wears
- Shows "Worn X times" for multiple wears
- Blue background with white text

### Statistics Display
- Shows total wear count across all items
- Shows number of items that have been worn at least once
- Format: "X items in your collection • Y total wears • Z items worn"

### Filtering
- "Never Worn" shows only items with wearCount = 0
- "Worn Once" shows only items with wearCount = 1
- "Worn X+ Times" shows items with wearCount >= X

## Database Structure

### ClothingItem Fields
```typescript
{
  // ... existing fields
  wearCount: number; // Default: 0
  lastWorn: number | null; // Default: null
}
```

### Outfit History Entry
When marking an outfit as worn, the system:
1. Extracts all item IDs from the outfit
2. Increments wearCount for each item
3. Updates lastWorn timestamp for each item
4. Creates outfit history entry
5. Logs analytics event

## Troubleshooting

### Wear Count Not Updating
1. Check browser console for errors
2. Verify Firebase authentication
3. Check network tab for API call failures
4. Verify item exists in wardrobe collection

### Filter Not Working
1. Check that wearCount field exists on items
2. Verify filter logic in wardrobe page
3. Check browser console for JavaScript errors

### Badge Not Showing
1. Verify wearCount > 0
2. Check WardrobeGrid component rendering
3. Verify CSS classes are applied correctly 