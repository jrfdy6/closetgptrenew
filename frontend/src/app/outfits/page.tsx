'use client';

import React from 'react';
import Link from 'next/link';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import OutfitGrid from '@/components/OutfitGrid';
import { Button } from '@/components/ui/button';
import { Sparkles, Plus, ArrowRight } from 'lucide-react';
import { useOnboardingState } from '@/lib/hooks/useOnboardingState';

type OutfitsPageProps = {
  searchParams?: { view?: string; favorites?: string };
};

export default function OutfitsPage({ searchParams }: OutfitsPageProps) {
  const initialFavoritesOnly = searchParams?.view === 'favorites' || searchParams?.favorites === 'true';
  const { state, loading, error, refresh } = useOnboardingState();
  const needsStyle = state?.stage === 'style';
  const needsCapsule = state && !state.capsule.ready;

  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="mx-auto max-w-7xl px-4 pb-28 pt-6 sm:px-6 sm:pt-10 lg:px-8">
        <header className="mb-7 flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="font-display text-3xl font-semibold text-card-foreground sm:text-4xl">My looks</h1>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted-foreground sm:text-base">
              Your outfits, ready to revisit. Open a look to see every piece, create a flatlay, or record a wear.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button asChild className="motion-reduce:transform-none motion-reduce:transition-none">
              <Link href="/outfits/generate"><Sparkles className="mr-2 h-4 w-4" aria-hidden="true" />New outfit</Link>
            </Button>
            <Button asChild variant="outline" className="motion-reduce:transform-none motion-reduce:transition-none">
              <Link href="/outfits/create"><Plus className="mr-2 h-4 w-4" aria-hidden="true" />Build my own</Link>
            </Button>
          </div>
        </header>

        {/* A changing capsule must never block returning to an already saved look. */}
        {!loading && !error && (needsStyle || needsCapsule) && (
          <aside aria-label="Continue your setup" className="mb-6 flex flex-col gap-3 rounded-2xl border border-border/60 bg-card/80 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-sm font-medium text-card-foreground">{needsStyle ? 'Finish your style profile' : 'Complete your capsule for new outfits'}</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                {needsStyle ? 'Continue your questionnaire when you are ready. Your saved looks are available below.'
                  : 'New outfits need at least 10 usable pieces with shoes and either tops and bottoms or a one-piece. Your saved looks are still available.'}
              </p>
            </div>
            <Button asChild variant="outline" className="shrink-0 self-start motion-reduce:transform-none motion-reduce:transition-none">
              <Link href="/onboarding">{needsStyle ? 'Continue my style profile' : 'Continue my capsule'}<ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" /></Link>
            </Button>
          </aside>
        )}
        {error && (
          <aside role="alert" className="mb-6 rounded-2xl border border-border/60 bg-card/80 p-4">
            <p className="text-sm text-muted-foreground">Your setup progress could not be loaded. You can still open your saved looks below.</p>
            <Button variant="outline" size="sm" onClick={() => { void refresh(); }} disabled={loading} className="mt-2">Retry setup progress</Button>
          </aside>
        )}
        <OutfitGrid showFilters showSearch maxOutfits={1000} initialFavoritesOnly={initialFavoritesOnly} />
      </main>
      <ClientOnlyNav />
    </div>
  );
}
