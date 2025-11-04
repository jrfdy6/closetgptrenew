import React from 'react';
import { Metadata } from 'next';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import OutfitGrid from '@/components/OutfitGrid';

// ===== METADATA =====
export const metadata: Metadata = {
  title: 'My Outfits | Easy Outfit App',
  description: 'View and manage your curated outfits',
};

// ===== MAIN PAGE COMPONENT =====
export default function OutfitsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-stone-950 dark:via-neutral-950 dark:to-stone-950">
      <Navigation />
      
      {/* Header with Glass Effect */}
      <div className="glass-navbar px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6">
            <div>
              <h1 className="text-4xl font-serif font-bold text-stone-900 dark:text-stone-100 mb-4">My Outfits</h1>
              <p className="text-stone-600 dark:text-stone-400 font-light text-lg leading-relaxed max-w-2xl">
                View and manage your curated outfits. Each outfit is tailored to your style preferences and occasion needs. Create custom outfits or generate AI-powered combinations.
              </p>
            </div>
            
            <div className="flex gap-4">
              <Link 
                href="/outfits/generate"
                className="group inline-flex items-center px-8 py-4 glass-button-primary font-medium rounded-full glass-transition shadow-lg hover:shadow-xl hover:scale-105 cursor-pointer"
              >
                <svg className="w-5 h-5 mr-3 group-hover:rotate-12 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate Outfit
              </Link>
              
              <Link 
                href="/outfits/create"
                className="group inline-flex items-center px-8 py-4 glass-button-secondary text-stone-900 dark:text-stone-100 font-medium rounded-full glass-transition hover:scale-105 cursor-pointer"
              >
                <svg className="w-5 h-5 mr-3 group-hover:rotate-90 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
          
          NOTE: Fast outfit system is ready but waiting for backend deployment
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
