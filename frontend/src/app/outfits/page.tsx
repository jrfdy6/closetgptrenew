'use client';

import React from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import OutfitGrid from '@/components/OutfitGrid';
import { Button } from '@/components/ui/button';
import { Sparkles, Plus } from 'lucide-react';

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
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#0D0D0D]">
      <Navigation />
      
      {/* Header */}
      <div className="px-4 py-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 bg-white/85 dark:bg-[#1A1A1A]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-lg">
            <div>
              <h1 className="text-4xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-3">My looks</h1>
              <p className="text-[#57534E] dark:text-[#C4BCB4] text-base leading-relaxed max-w-2xl">
                Save the fits you love, remix them for new occasions, and generate fresh looks whenever inspiration hits.
              </p>
            </div>
            
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 w-full sm:w-auto">
              <Link href="/outfits/generate">
                <Button className="w-full sm:w-auto h-12 px-6 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] hover:shadow-lg hover:shadow-[#FFB84C]/30 transition-all">
                  <Sparkles className="w-5 h-5 mr-2" />
                  Generate Outfit
                </Button>
              </Link>
              
              <Link href="/outfits/create">
                <Button variant="outline" className="w-full sm:w-auto h-12 px-6 border-2 border-[#3D2F24] text-[#1C1917] dark:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2E2E2E] transition-all">
                  <Plus className="w-5 h-5 mr-2" />
                  Create Outfit
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main Content - Bottom padding for nav */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
        {/* Saved Outfits Grid */}
        <div>
          <h2 className="text-2xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-6">
            Saved Outfits
          </h2>
          <OutfitGrid 
            showFilters={true}
            showSearch={true}
            maxOutfits={1000}
            initialFavoritesOnly={initialFavoritesOnly}
          />
        </div>
      </main>
      
      {/* Client-Only Navigation - No Props to Avoid Serialization */}
      <ClientOnlyNav />
    </div>
  );
}
