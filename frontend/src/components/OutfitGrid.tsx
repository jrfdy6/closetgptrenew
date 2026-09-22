"use client";

import React, { useState, useMemo, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { useAuthContext } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Heart, ArrowUpRight, ImageOff, Edit, Trash2, RefreshCw, ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

// Import the established pattern components
import useOutfits from '@/lib/hooks/useOutfits_proper';
import { Outfit, OutfitFilters } from '@/lib/services/outfitService';
import OutfitEditModal from './OutfitEditModal';
import { OutfitUpdate } from '@/lib/services/outfitService';

// ===== COMPONENT INTERFACES =====
interface OutfitGridProps {
  showFilters?: boolean;
  showSearch?: boolean;
  maxOutfits?: number;
  className?: string;
  initialFavoritesOnly?: boolean;
}

interface OutfitCardProps {
  outfit: Outfit;
  onFavorite: (id: string, isFavorite: boolean) => void;
  mutationError?: string;
  pending?: boolean;
  onEdit: (id: string) => void;
  onDelete: (id: string) => void;
}

// Original garment photos are intentional browse previews. The detail route checks
// the current private request/source identity before presenting a generated flatlay.
function PiecePhoto({ item }: { item: Outfit['items'][number] }) {
  const original = (item as typeof item & { originalImageUrl?: string }).originalImageUrl || item.imageUrl;
  const [failedSource, setFailedSource] = useState<string | undefined>();
  return (
    <div className="flex min-h-0 items-center justify-center overflow-hidden rounded-xl bg-background/70">
      {original && failedSource !== original ? (
        <img src={original} alt={item.name || 'Wardrobe piece'} loading="lazy"
          className="h-full w-full object-contain p-2"
          onError={() => setFailedSource(original)} />
      ) : (
        <span className="px-3 text-center text-xs text-muted-foreground">
          <ImageOff className="mx-auto mb-1 h-4 w-4" aria-hidden="true" />
          {item.name || 'Wardrobe piece'}<br />Photo unavailable
        </span>
      )}
    </div>
  );
}

function savedDate(value: unknown): Date | null {
  let parsed: Date | null = null;
  if (value instanceof Date) parsed = value;
  else if (typeof value === 'number') parsed = new Date(value < 1e12 ? value * 1000 : value);
  else if (typeof value === 'string' && value.trim()) parsed = new Date(value);
  else if (value && typeof value === 'object' && 'seconds' in value && typeof value.seconds === 'number') {
    parsed = new Date(value.seconds * 1000);
  }
  return parsed && Number.isFinite(parsed.getTime()) ? parsed : null;
}

function OutfitCard({ outfit, onFavorite, onEdit, onDelete, mutationError, pending }: OutfitCardProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const pieces = Array.isArray(outfit.items) ? outfit.items : [];
  const name = outfit.name || 'Untitled outfit';
  const created = savedDate(outfit.createdAt);
  const lastWorn = savedDate(outfit.lastWorn);
  const wearCount = outfit.wearCount || 0;

  return (
    <Card className="flex h-full flex-col overflow-hidden rounded-2xl border-border/60 bg-card/90 shadow-sm">
      <CardHeader className="flex-row items-center justify-between space-y-0 px-4 py-2">
        <p className="text-xs font-medium uppercase tracking-widest text-muted-foreground">Saved outfit</p>
        <Button variant="ghost" size="icon" onClick={() => onFavorite(outfit.id, !outfit.isFavorite)}
          disabled={pending}
          aria-label={`${outfit.isFavorite ? 'Remove' : 'Add'} ${name} ${outfit.isFavorite ? 'from' : 'to'} favorites`}
          aria-pressed={Boolean(outfit.isFavorite)}
          className="shrink-0 motion-reduce:transform-none motion-reduce:transition-none">
          <Heart className={cn('h-5 w-5', outfit.isFavorite && 'fill-primary text-primary')} aria-hidden="true" />
        </Button>
      </CardHeader>
      <CardContent className="flex flex-1 flex-col px-4 pb-4 pt-0">
        <Link href={`/outfits/${encodeURIComponent(outfit.id)}`} aria-label={`Open ${name}`}
          className="group block rounded-xl focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-4">
          <div className="aspect-[4/3] overflow-hidden rounded-xl border border-border/50 bg-secondary/40 p-2">
            {pieces.length ? (
              <div className={cn('grid h-full gap-2', pieces.length === 1 ? 'grid-cols-1' : 'grid-cols-2', pieces.length > 2 && 'grid-rows-2')}>
                {pieces.slice(0, 4).map((item, index) => <PiecePhoto key={`${item.id}-${index}`} item={item} />)}
              </div>
            ) : (
              <div className="flex h-full flex-col items-center justify-center gap-2 px-4 text-center text-sm text-muted-foreground">
                <ImageOff className="h-6 w-6" aria-hidden="true" />
                <span>No pieces saved with this outfit.</span>
              </div>
            )}
          </div>
          <CardTitle className="mt-4 line-clamp-2 text-lg font-display font-semibold text-card-foreground group-hover:text-primary">
            {name}
          </CardTitle>
          <p className="mt-1 text-xs text-muted-foreground">
            {pieces.length ? `${pieces.length} ${pieces.length === 1 ? 'piece' : 'pieces'} · Your pieces` : 'Earlier saved entry'}
          </p>
          <span className="mt-3 inline-flex min-h-11 items-center gap-1 text-sm font-medium text-primary">
            Open outfit <ArrowUpRight className="h-4 w-4" aria-hidden="true" />
          </span>
        </Link>
        <div className="mb-4 mt-1 flex flex-wrap gap-2">
          {outfit.occasion && <Badge variant="secondary" className="text-xs">{outfit.occasion}</Badge>}
          {outfit.style && <Badge variant="outline" className="text-xs">{outfit.style}</Badge>}
          {outfit.mood && <Badge variant="outline" className="text-xs">{outfit.mood}</Badge>}
        </div>
        <div className="mt-auto border-t border-border/50 pt-3">
          <div className="flex flex-wrap items-center justify-between gap-1 text-xs text-muted-foreground">
            <span>{wearCount ? `Worn ${wearCount} ${wearCount === 1 ? 'time' : 'times'}` : 'Not worn yet'}</span>
            {lastWorn ? <span>Last worn {lastWorn.toLocaleDateString()}</span> : created ? <span>Saved {created.toLocaleDateString()}</span> : null}
          </div>
          <div className="mt-2 flex items-center justify-end gap-1">
            <Button variant="ghost" size="sm" onClick={() => onEdit(outfit.id)} disabled={pending}
              aria-label={`Edit ${name}`} className="motion-reduce:transform-none motion-reduce:transition-none">
              <Edit className="mr-2 h-4 w-4" aria-hidden="true" /> Edit
            </Button>
            <Button variant="ghost" size="icon" onClick={() => setDeleteDialogOpen(true)} disabled={pending}
              aria-label={`Delete ${name}`} className="text-muted-foreground hover:text-destructive motion-reduce:transform-none motion-reduce:transition-none">
              <Trash2 className="h-4 w-4" aria-hidden="true" />
            </Button>
          </div>
        </div>
        {mutationError && <p role="alert" className="mt-3 text-sm text-destructive">{mutationError} Please try the action again.</p>}
      </CardContent>
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent className="rounded-2xl border-border/60 bg-card">
          <AlertDialogHeader>
            <AlertDialogTitle>Delete outfit</AlertDialogTitle>
            <AlertDialogDescription>This will remove &quot;{name}&quot; permanently.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => { onDelete(outfit.id); setDeleteDialogOpen(false); }} className="bg-destructive hover:bg-destructive/90">
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}

// ===== FILTERS COMPONENT =====
interface OutfitFiltersProps {
  filters: OutfitFilters;
  onFiltersChange: (filters: OutfitFilters) => void;
  onSearch: (query: string) => void;
  onClear: () => void;
  sortBy: 'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least';
  onSortChange: (sortBy: 'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least') => void;
  showSearch: boolean;
  showFilters: boolean;
}

function OutfitFiltersComponent({ filters, onFiltersChange, onSearch, onClear, sortBy, onSortChange, showSearch, showFilters }: OutfitFiltersProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const activeFilters = Boolean(filters.occasion || filters.style || sortBy !== 'date-newest');
  return (
    <div className="rounded-2xl border border-border/60 bg-card/80 p-4">
      {showSearch && <form onSubmit={event => { event.preventDefault(); onSearch(searchQuery); }}>
        <label htmlFor="outfit-search" className="mb-2 block text-sm font-medium text-card-foreground">Search outfits</label>
        <div className="flex gap-2">
          <Input id="outfit-search" className="h-11 min-w-0" placeholder="Name, occasion, or style" value={searchQuery} onChange={event => setSearchQuery(event.target.value)} />
          <Button type="submit" size="sm" className="motion-reduce:transform-none motion-reduce:transition-none">Search</Button>
        </div>
      </form>}
      {showFilters && <details className={showSearch ? 'mt-2' : ''}>
        <summary className="flex min-h-11 cursor-pointer items-center gap-2 rounded-lg text-sm font-medium text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
          <ChevronDown className="h-4 w-4" aria-hidden="true" />Filters and sort{activeFilters ? ' · Active' : ''}
        </summary>
        <div className="mt-2 grid gap-3 sm:grid-cols-3">
          <div>
            <label htmlFor="outfit-occasion" className="mb-2 block text-sm text-muted-foreground">Occasion</label>
            <Select value={filters.occasion || 'all'} onValueChange={value => onFiltersChange({ ...filters, occasion: value === 'all' ? undefined : value })}>
              <SelectTrigger id="outfit-occasion" className="h-11"><SelectValue placeholder="All occasions" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All occasions</SelectItem><SelectItem value="casual">Casual</SelectItem>
                <SelectItem value="business">Business</SelectItem><SelectItem value="formal">Formal</SelectItem>
                <SelectItem value="athletic">Athletic</SelectItem><SelectItem value="evening">Evening</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label htmlFor="outfit-style" className="mb-2 block text-sm text-muted-foreground">Style</label>
            <Select value={filters.style || 'all'} onValueChange={value => onFiltersChange({ ...filters, style: value === 'all' ? undefined : value })}>
              <SelectTrigger id="outfit-style" className="h-11"><SelectValue placeholder="All styles" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All styles</SelectItem><SelectItem value="classic">Classic</SelectItem>
                <SelectItem value="modern">Modern</SelectItem><SelectItem value="vintage">Vintage</SelectItem>
                <SelectItem value="bohemian">Bohemian</SelectItem><SelectItem value="minimalist">Minimalist</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label htmlFor="outfit-sort" className="mb-2 block text-sm text-muted-foreground">Sort by</label>
            <Select value={sortBy} onValueChange={onSortChange}>
              <SelectTrigger id="outfit-sort" className="h-11"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="date-newest">Newest first</SelectItem><SelectItem value="date-oldest">Oldest first</SelectItem>
                <SelectItem value="wear-most">Most worn</SelectItem><SelectItem value="wear-least">Least worn</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <Button variant="ghost" size="sm" className="mt-3 motion-reduce:transform-none motion-reduce:transition-none"
          onClick={() => { setSearchQuery(''); onSortChange('date-newest'); onClear(); }}>Clear filters</Button>
      </details>}
    </div>
  );
}

// ===== MAIN OUTFIT GRID COMPONENT =====
export default function OutfitGrid(props: OutfitGridProps) {
  const { user, loading } = useAuthContext();
  // Close old account dialogs and clear local filters synchronously on account
  // changes, in addition to the hook's request/acknowledgment fences.
  return <OutfitGridContent key={loading ? 'auth-loading' : user?.uid ?? 'signed-out'} {...props} />;
}

function OutfitGridContent({
  showFilters = true,
  showSearch = true,
  maxOutfits = 1000,
  className,
  initialFavoritesOnly = false,
}: OutfitGridProps) {
  // ===== HOOK USAGE =====
  // This follows the established wardrobe service architecture pattern:
  // - useOutfits_proper provides data and actions
  // - outfitService_proper handles API calls
  // - Proper TypeScript interfaces for data contracts
  const {
    outfits,
    loading,
    loadingMore,
    hasMore,
    error,
    mutationErrors,
    pendingMutations,
    fetchOutfits,
    loadMoreOutfits,
    toggleFavorite,
    updateOutfit,
    deleteOutfit,
    refresh
  } = useOutfits();

  // ===== LOCAL STATE =====
  const [filters, setFilters] = useState<OutfitFilters>({});
  const [activeSearchQuery, setActiveSearchQuery] = useState('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(initialFavoritesOnly);
  const isSearching = activeSearchQuery.length > 0;
  const [sortBy, setSortBy] = useState<'date-newest' | 'date-oldest' | 'wear-most' | 'wear-least'>('date-newest');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Edit modal state
  const [editModalOpen, setEditModalOpen] = useState(false);
  const [editingOutfit, setEditingOutfit] = useState<Outfit | null>(null);

  // Intersection observer for infinite scroll
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const refreshQueryHandledRef = useRef(false);

  // Deduplicate overlapping refreshes without a timeout or stale state closure.
  const refreshInFlight = useRef(false);
  const debouncedRefresh = useCallback(async () => {
    if (refreshInFlight.current) return;
    refreshInFlight.current = true;
    setIsRefreshing(true);
    try { await refresh(); }
    finally { refreshInFlight.current = false; setIsRefreshing(false); }
  }, [refresh]);

  // ===== COMPUTED VALUES =====
  const totalFavorites = useMemo(
    () => outfits.filter(outfit => outfit.isFavorite).length,
    [outfits]
  );

  const filteredOutfits = useMemo(() => {
    let baseOutfits = outfits;

    if (isSearching) {
      baseOutfits = outfits.filter(outfit => {
        const searchText = `${outfit.name} ${outfit.occasion} ${outfit.style} ${outfit.mood || ''}`.toLowerCase();
        return searchText.includes(activeSearchQuery);
      });
    }

    if (showFavoritesOnly) {
      baseOutfits = baseOutfits.filter(outfit => outfit.isFavorite);
    }

    // Apply sorting based on selected option
    const sorted = [...baseOutfits].sort((a, b) => {
      switch (sortBy) {
        case 'date-newest':
          const dateA = (savedDate(a.createdAt) || new Date(0));
          const dateB = (savedDate(b.createdAt) || new Date(0));
          return dateB.getTime() - dateA.getTime(); // Newest first

        case 'date-oldest':
          const dateAOld = (savedDate(a.createdAt) || new Date(0));
          const dateBOld = (savedDate(b.createdAt) || new Date(0));
          return dateAOld.getTime() - dateBOld.getTime(); // Oldest first

        case 'wear-most':
          const wearCountA = a.wearCount || 0;
          const wearCountB = b.wearCount || 0;
          return wearCountB - wearCountA; // Most worn first

        case 'wear-least':
          const wearCountALeast = a.wearCount || 0;
          const wearCountBLeast = b.wearCount || 0;
          return wearCountALeast - wearCountBLeast; // Least worn first

        default:
          return 0;
      }
    });

    return sorted;
  }, [outfits, activeSearchQuery, isSearching, sortBy, showFavoritesOnly]);

  // ===== EFFECTS =====
  // Removed problematic useEffect that was causing infinite refresh loop
  // The useOutfits hook already handles initial data fetching

  /**
   * Listen for outfit marked as worn events to refresh outfit data
   */
  useEffect(() => {
    const handleOutfitMarkedAsWorn = (event: CustomEvent) => {
      console.log('🔄 [OutfitGrid] Outfit marked as worn, refreshing outfit data...', event.detail);
      debouncedRefresh();
    };

    window.addEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);

    return () => {
      window.removeEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    };
  }, [debouncedRefresh]);

  /**
   * Handle refresh query parameter once to avoid repeated reload loops.
   * Ensures the outfits grid only reacts a single time even if the callback identities change.
   */
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const refreshParam = urlParams.get('refresh');

    if (!refreshParam) {
      return;
    }

    if (!refreshQueryHandledRef.current) {
      refreshQueryHandledRef.current = true;
      console.log('🔄 [OutfitGrid] Refresh parameter detected, triggering debounced refresh');
      debouncedRefresh();
    } else {
      console.log('🔄 [OutfitGrid] Refresh parameter already handled, skipping duplicate refresh');
    }

    urlParams.delete('refresh');
    const remainingQuery = urlParams.toString();
    const cleanUrl = remainingQuery
      ? `${window.location.pathname}?${remainingQuery}`
      : window.location.pathname;
    window.history.replaceState(window.history.state, '', cleanUrl);
  }, [debouncedRefresh]);

  /**
   * Intersection observer for automatic infinite scroll
   */
  useEffect(() => {
    // Don't set up observer if there's no more to load or we're already loading
    if (!hasMore || loadingMore || isRefreshing || error) {
      return;
    }

    let timeoutId: NodeJS.Timeout | null = null;

    const observer = new IntersectionObserver(
      (entries) => {
        const first = entries[0];
        // Only trigger if:
        // 1. Element is intersecting
        // 2. We have more to load
        // 3. We're not currently loading
        // 4. We're not refreshing
        if (first.isIntersecting && hasMore && !loadingMore && !isRefreshing) {
          // Debounce: Clear any pending timeout and set a new one
          if (timeoutId) {
            clearTimeout(timeoutId);
          }
          timeoutId = setTimeout(() => {
            console.log('🔄 [OutfitGrid] Load more trigger reached, loading more outfits');
            loadMoreOutfits();
          }, 300); // 300ms debounce
        } else if (!first.isIntersecting && timeoutId) {
          // Cancel pending load if element is no longer visible
          clearTimeout(timeoutId);
          timeoutId = null;
        }
      },
      { threshold: 0.1, rootMargin: '50px' } // Reduced rootMargin to prevent premature triggering
    );

    const currentRef = loadMoreRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      observer.disconnect();
    };
  }, [hasMore, loadingMore, loadMoreOutfits, isRefreshing, error]);

  // ===== EVENT HANDLERS =====
  const handleFiltersChange = (newFilters: OutfitFilters) => {
    setFilters(newFilters);
    setActiveSearchQuery('');
    fetchOutfits(newFilters);
  };

  const handleSearch = async (query: string) => {
    const normalizedQuery = query.trim().toLowerCase();
    setActiveSearchQuery(normalizedQuery);
    if (normalizedQuery) {
      // Derive matches from current state as the larger fetch resolves.
      // An empty result remains empty instead of falling back to all outfits.
      await fetchOutfits({ ...filters, limit: maxOutfits });
    }
  };

  const handleClear = () => {
    setActiveSearchQuery('');
    setFilters({ limit: maxOutfits });
    fetchOutfits({ limit: maxOutfits });
  };

  const handleFavorite = async (id: string, isFavorite: boolean) => {
    await toggleFavorite(id, isFavorite);
  };

  const handleEdit = (id: string) => {
    const outfit = outfits.find(o => o.id === id);
    if (outfit) {
      setEditingOutfit(outfit);
      setEditModalOpen(true);
    }
  };

  const handleSaveEdit = async (updates: OutfitUpdate) => {
    if (!editingOutfit) throw new Error('No outfit selected');
    const result = await updateOutfit(editingOutfit.id, updates);
    if (!result) throw new Error('Unable to save your outfit. Please try again.');
    setEditModalOpen(false);
    setEditingOutfit(null);
  };

  const handleCloseEdit = () => {
    setEditModalOpen(false);
    setEditingOutfit(null);
  };

  const handleDelete = async (id: string) => {
    // The card has already shown the confirmation dialog.
    await deleteOutfit(id);
  };

  // ===== RENDER STATES =====
  if (loading && outfits.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin motion-reduce:animate-none text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Loading your outfits...</p>
        </div>
      </div>
    );
  }

  if (error && outfits.length === 0) {
    return (
      <div role="alert" className="rounded-2xl border border-destructive/30 bg-card p-6 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <div className="flex gap-2 justify-center">
          <Button onClick={debouncedRefresh} disabled={isRefreshing} size="sm">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  // ===== MAIN RENDER =====
  return (
    <div className={cn("space-y-6", className)}>
      {error && (
        <div role="alert" className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">{error}</p>
          <Button onClick={refresh} variant="outline" size="sm">Try Again</Button>
        </div>
      )}
      {/* Header with Stats */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-display font-semibold text-card-foreground">
            {isSearching ? 'Search results' : showFavoritesOnly ? 'Favorite looks' : 'Saved outfits'}
          </h2>
          <p className="text-sm text-muted-foreground">
            {(() => {
              const displayCount = filteredOutfits.length;
              const searchLabel = displayCount === 1 ? 'outfit' : 'outfits';

              if (isSearching) {
                return `Found ${displayCount} ${showFavoritesOnly ? 'favorite ' : ''}${searchLabel} matching your search in loaded outfits`;
              }

              if (showFavoritesOnly) {
                return `Showing ${displayCount} of ${totalFavorites} favorite ${totalFavorites === 1 ? 'outfit' : 'outfits'}`;
              }

              return `Showing ${displayCount} of ${outfits.length} loaded ${outfits.length === 1 ? 'outfit' : 'outfits'}`;
            })()}
          </p>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={() => setShowFavoritesOnly(prev => !prev)}
            aria-pressed={showFavoritesOnly}
            variant={showFavoritesOnly ? 'default' : 'outline'}
            size="sm"
            className={cn(
              "flex items-center gap-2 border motion-reduce:transform-none motion-reduce:transition-none",
              showFavoritesOnly
                ? "bg-red-100 text-red-600 border-red-200 hover:bg-red-200"
                        : "text-muted-foreground border-border/60 hover:bg-secondary"
            )}
          >
            <Heart className={cn("h-4 w-4", showFavoritesOnly ? "fill-current" : "")} />
            {showFavoritesOnly ? 'Favorites Only' : 'Favorites'}
          </Button>
          <Button
            onClick={debouncedRefresh}
            variant="outline"
            size="sm"
            className="motion-reduce:transform-none motion-reduce:transition-none"
            disabled={loading || isRefreshing}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin motion-reduce:animate-none")} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters and Search */}
      {(showFilters || showSearch) && (
        <OutfitFiltersComponent
          showSearch={showSearch}
          showFilters={showFilters}
          filters={filters}
          onFiltersChange={handleFiltersChange}
          onSearch={handleSearch}
          onClear={handleClear}
          sortBy={sortBy}
          onSortChange={setSortBy}
        />
      )}

      {/* Search Results Indicator */}
      {isSearching && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800 text-sm">
            🔍 Showing {filteredOutfits.length} matches in loaded outfits.
            <button
              onClick={handleClear}
              className="text-blue-600 hover:text-blue-800 underline ml-2"
            >
              Clear search
            </button>
          </p>
        </div>
      )}

      {/* Outfits Grid */}
      {filteredOutfits.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-muted-foreground mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-card-foreground mb-2">
            {isSearching
              ? showFavoritesOnly ? 'No favorite outfits found' : 'No outfits found'
              : showFavoritesOnly ? 'No favorite outfits yet' : 'No outfits yet'}
          </h3>
          <p className="text-muted-foreground mb-4">
            {isSearching
              ? 'Try adjusting your search terms or filters'
              : showFavoritesOnly
                ? 'Tap the heart icon on outfits you love to collect them here.'
                : 'Your created outfits will be saved here. Open one anytime to view its pieces or record a wear.'}
          </p>
          {!isSearching && showFavoritesOnly && (
            <Button onClick={() => setShowFavoritesOnly(false)} variant="outline">
              View all outfits
            </Button>
          )}
          {!isSearching && !showFavoritesOnly && (
            <Button asChild><Link href="/outfits/generate">Create an outfit</Link></Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredOutfits.map((outfit) => (
            <OutfitCard
              key={outfit.id}
              outfit={outfit}
              onFavorite={handleFavorite}
              onEdit={handleEdit}
              onDelete={handleDelete}
              mutationError={mutationErrors[outfit.id]}
              pending={pendingMutations.includes(outfit.id)}
            />
          ))}
        </div>
      )}

      {/* Load More Section */}
      {hasMore && (
        <div ref={loadMoreRef} className="text-center py-8">
          {loadingMore ? (
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="h-6 w-6 animate-spin motion-reduce:animate-none text-muted-foreground" />
              <p className="text-muted-foreground text-sm">Loading more outfits...</p>
            </div>
          ) : (
            <Button
              onClick={loadMoreOutfits}
              variant="outline"
              className="flex items-center gap-2"
              disabled={loadingMore}
            >
              <ChevronDown className="h-4 w-4" />
              Load More Looks
            </Button>
          )}
        </div>
      )}

      {/* End of Results */}
      {!hasMore && outfits.length > 0 && (
        <div className="text-center py-6">
          <p className="text-muted-foreground text-sm">
            {outfits.length} outfits loaded.
          </p>
        </div>
      )}

      {/* Edit Modal */}
      {editingOutfit && (
        <OutfitEditModal
          outfit={editingOutfit}
          isOpen={editModalOpen}
          onClose={handleCloseEdit}
          onSave={handleSaveEdit}
        />
      )}
    </div>
  );
}
