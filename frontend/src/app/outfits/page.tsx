'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import OutfitGrid from '@/components/OutfitGrid';
import MinimalOutfitDefault from '@/components/outfits/MinimalOutfitDefault';
import { useRouter } from 'next/navigation';
import { useAutoWeather } from '@/hooks/useWeather';

type OutfitsPageProps = {
  searchParams?: {
    view?: string;
    favorites?: string;
  };
};

// ===== MAIN PAGE COMPONENT =====
export default function OutfitsPage({ searchParams }: OutfitsPageProps) {
  const router = useRouter();
  const { weather } = useAutoWeather();
  const initialFavoritesOnly =
    searchParams?.view === 'favorites' ||
    searchParams?.favorites === 'true';
  const [generating, setGenerating] = useState(false);

  const handleShuffle = () => {
    // Navigate to generate page with shuffle params
    router.push('/outfits/generate?shuffle=true');
  };

  const handleExpand = (options: {
    occasion: string;
    mood?: string;
    style?: string;
    baseItemId?: string;
  }) => {
    // Navigate to generate page with options
    const params = new URLSearchParams({
      occasion: options.occasion,
    });
    if (options.mood) params.append('mood', options.mood);
    if (options.style) params.append('style', options.style);
    if (options.baseItemId) params.append('baseItem', options.baseItemId);
    
    router.push(`/outfits/generate?${params.toString()}`);
  };

  const weatherData = weather ? {
    temperature: Math.round(weather.temperature),
    condition: weather.condition || 'Clear',
    location: weather.location,
  } : undefined;

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
          </div>
        </div>
      </div>
      
      {/* Main Content - Bottom padding for nav */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pb-24">
        {/* Minimal Default State - Phase 2 Blueprint */}
        <div className="mb-8">
          <MinimalOutfitDefault
            onShuffle={handleShuffle}
            onExpand={handleExpand}
            weather={weatherData}
            generating={generating}
          />
        </div>

        {/* Saved Outfits Grid */}
        <div className="mt-12">
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
