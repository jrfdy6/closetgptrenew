import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
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
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Outfits</h1>
            <p className="text-gray-600">
              View and manage your curated outfits. Each outfit is tailored to your style preferences and occasion needs.
            </p>
          </div>
          <Link 
            href="/outfits/generate"
            className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors duration-200 shadow-sm hover:shadow-md cursor-pointer"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Generate Outfit
          </Link>
        </div>
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
        maxOutfits={1000}
      />
    </div>
  );
}
