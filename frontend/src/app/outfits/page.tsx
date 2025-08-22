import React from 'react';
import { Metadata } from 'next';
import OutfitGrid from '@/components/OutfitGrid_proper';

// ===== METADATA =====
export const metadata: Metadata = {
  title: 'My Outfits | ClosetGPT',
  description: 'View and manage your curated outfits',
};

// ===== MAIN PAGE COMPONENT =====
export default function OutfitsPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Outfits</h1>
        <p className="text-gray-600">
          View and manage your curated outfits. Each outfit is tailored to your style preferences and occasion needs.
        </p>
      </div>
      
      {/* 
        OutfitGrid Component: Handles UI rendering and user interactions
        This follows the established wardrobe service architecture pattern:
        - Routes: This page handles routing and basic layout
        - Components: OutfitGrid handles UI rendering and user interactions
        - Hooks: useOutfits_proper provides data and actions
        - Services: outfitService_proper handles API calls
        - Types: Proper TypeScript interfaces for data contracts
      */}
      <OutfitGrid 
        showFilters={true}
        showSearch={true}
        maxOutfits={100}
      />
    </div>
  );
}
