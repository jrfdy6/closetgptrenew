import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import OutfitGrid from '@/components/OutfitGrid';

// ===== METADATA =====
export const metadata: Metadata = {
  title: 'My Outfits | ClosetGPT',
  description: 'View and manage your curated outfits',
};

// ===== MAIN PAGE COMPONENT =====
export default function OutfitsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 border-b border-purple-200 dark:border-purple-700 px-4 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Outfits</h1>
              <p className="text-purple-700 dark:text-purple-300 mt-1">
                View and manage your curated outfits. Each outfit is tailored to your style preferences and occasion needs.
              </p>
            </div>
            
            <div className="flex gap-3">
              <Link 
                href="/outfits/generate"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-pink-700 transition-colors duration-200 shadow-sm hover:shadow-md cursor-pointer"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Outfit
              </Link>
              
              <Link 
                href="/outfits/create"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-semibold rounded-lg hover:from-emerald-700 hover:to-teal-700 transition-colors duration-200 shadow-sm hover:shadow-md cursor-pointer"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create Outfit
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
      </main>
    </div>
  );
}
