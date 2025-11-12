import React from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import OutfitGrid from '@/components/OutfitGrid';

type OutfitsPageProps = {
  searchParams?: {
    view?: string;
    favorites?: string;
  };
};

// ===== MAIN PAGE COMPONENT =====
export default function OutfitsPage({ searchParams }: OutfitsPageProps) {
  const initialFavoritesOnly =
    searchParams?.view === 'favorites' ||
    searchParams?.favorites === 'true';

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
      <Navigation />
      
      {/* Header */}
      <div className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 bg-white/85 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-lg">
            <div>
              <h1 className="text-4xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-3">My looks</h1>
              <p className="text-[#57534E] dark:text-[#C4BCB4] text-base leading-relaxed max-w-2xl">
                Save the fits you love, remix them for new occasions, and generate fresh looks whenever inspiration hits.
              </p>
            </div>
            
            <div className="flex gap-4">
              <Link 
                href="/outfits/generate"
                className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white rounded-2xl font-semibold shadow-lg shadow-amber-500/20 transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]"
              >
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Generate outfit
              </Link>
              
              <Link 
                href="/outfits/create"
                className="inline-flex items-center px-6 py-3 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] rounded-2xl font-semibold transition-colors duration-200 hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
              >
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Create outfit
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content - Bottom padding for nav */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
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
          initialFavoritesOnly={initialFavoritesOnly}
        />
      </main>
      
      {/* Client-Only Navigation - No Props to Avoid Serialization */}
      <ClientOnlyNav />
    </div>
  );
}
