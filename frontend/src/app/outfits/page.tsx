"use client";

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Star, 
  ThumbsUp, 
  ThumbsDown, 
  AlertTriangle, 
  Calendar, 
  Eye, 
  CheckCircle, 
  Sparkles, 
  ArrowRight, 
  RefreshCw,
  Search,
  Filter,
  SortAsc,
  SortDesc,
  Grid3X3,
  List
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import { PageLoadingSkeleton } from '@/components/ui/loading-states';
import { SwipeableCard, InteractiveButton, HoverCard, hapticFeedback } from '@/components/ui/micro-interactions';
import { useInView } from 'react-intersection-observer';

interface Outfit {
  id: string;
  name: string;
  description?: string;
  occasion?: string;
  season?: string;
  style?: string | string[];
  style_tags?: string[];
  createdAt: number | string;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  feedback_summary?: {
    total_feedback: number;
    likes: number;
    dislikes: number;
    issues: number;
    average_rating: number;
  };
  userFeedback?: {
    liked: boolean;
    rating: number;
    comment?: string;
    timestamp: number;
  };
}

type SortOption = 'newest' | 'oldest' | 'name' | 'rating';
type ViewMode = 'grid' | 'list';

const ITEMS_PER_PAGE = 12;

export default function OutfitsPage() {
  const { user, loading: authLoading } = useFirebase();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingWorn, setMarkingWorn] = useState<string | null>(null);
  
  // Filtering and sorting state
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedOccasion, setSelectedOccasion] = useState<string>('all');
  const [selectedStyle, setSelectedStyle] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('newest');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');
  
  // Lazy loading state
  const [visibleItems, setVisibleItems] = useState(ITEMS_PER_PAGE);
  const [hasMore, setHasMore] = useState(true);

  // Intersection observer for lazy loading
  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0.1,
    triggerOnce: false,
  });

  const fetchOutfits = useCallback(async () => {
    if (!user) {
      console.log('🔍 DEBUG: No user available, skipping fetch');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const idToken = await user.getIdToken();
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 65000); // 65 second timeout
      
      const response = await fetch('/api/outfits', {
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      });
      
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch outfits: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('🔍 DEBUG: Fetched outfits:', data.length);
      
      // Helper function to convert timestamp to number for sorting
      const getTimestampForSorting = (timestamp: number | string): number => {
        if (typeof timestamp === 'string') {
          return new Date(timestamp).getTime();
        } else {
          // Check if it's already in milliseconds (13 digits) or seconds (10 digits)
          if (timestamp > 1000000000000) {
            return timestamp;
          } else {
            return timestamp * 1000;
          }
        }
      };
      
      // Sort by newest first by default
      const sortedOutfits = data.sort((a: Outfit, b: Outfit) => getTimestampForSorting(b.createdAt) - getTimestampForSorting(a.createdAt));
      setOutfits(sortedOutfits);
      setHasMore(sortedOutfits.length > ITEMS_PER_PAGE);
    } catch (err) {
      console.error('Error fetching outfits:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch outfits');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (!user || authLoading) {
      return;
    }
    fetchOutfits();
  }, [user, authLoading, fetchOutfits]);

  // Lazy loading effect
  useEffect(() => {
    if (inView && hasMore) {
      setVisibleItems(prev => {
        const newCount = prev + ITEMS_PER_PAGE;
        setHasMore(newCount < filteredAndSortedOutfits.length);
        return newCount;
      });
    }
  }, [inView, hasMore]);

  // Filter and sort outfits
  const filteredAndSortedOutfits = useMemo(() => {
    let filtered = outfits.filter(outfit => {
      const matchesSearch = searchQuery === '' || 
        outfit.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        outfit.description?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        outfit.items.some(item => item.name.toLowerCase().includes(searchQuery.toLowerCase()));
      
      const matchesOccasion = selectedOccasion === 'all' || outfit.occasion === selectedOccasion;
      const matchesStyle = selectedStyle === 'all' || 
        (Array.isArray(outfit.style) ? outfit.style.includes(selectedStyle) : outfit.style === selectedStyle);
      
      return matchesSearch && matchesOccasion && matchesStyle;
    });

    // Helper function to convert timestamp to number for sorting
    const getTimestampForSorting = (timestamp: number | string): number => {
      if (typeof timestamp === 'string') {
        return new Date(timestamp).getTime();
      } else {
        // Check if it's already in milliseconds (13 digits) or seconds (10 digits)
        if (timestamp > 1000000000000) {
          return timestamp;
        } else {
          return timestamp * 1000;
        }
      }
    };

    // Sort outfits
    switch (sortBy) {
      case 'newest':
        filtered.sort((a, b) => getTimestampForSorting(b.createdAt) - getTimestampForSorting(a.createdAt));
        break;
      case 'oldest':
        filtered.sort((a, b) => getTimestampForSorting(a.createdAt) - getTimestampForSorting(b.createdAt));
        break;
      case 'name':
        filtered.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'rating':
        filtered.sort((a, b) => {
          const ratingA = a.feedback_summary?.average_rating || 0;
          const ratingB = b.feedback_summary?.average_rating || 0;
          return ratingB - ratingA;
        });
        break;
    }

    return filtered;
  }, [outfits, searchQuery, selectedOccasion, selectedStyle, sortBy]);

  // Get unique occasions and styles for filters
  const occasions = useMemo(() => {
    const uniqueOccasions = [...new Set(outfits.map(outfit => outfit.occasion).filter(Boolean) as string[])];
    return uniqueOccasions.sort();
  }, [outfits]);

  const styles = useMemo(() => {
    const allStyles = outfits.flatMap(outfit => {
      if (Array.isArray(outfit.style)) {
        return outfit.style;
      }
      return outfit.style ? [outfit.style] : [];
    });
    const uniqueStyles = [...new Set(allStyles)];
    return uniqueStyles.sort();
  }, [outfits]);

  const formatDate = (timestamp: number | string) => {
    let date: Date;
    
    if (typeof timestamp === 'string') {
      // Handle ISO string format
      date = new Date(timestamp);
    } else {
      // Handle Unix timestamp (seconds since epoch)
      // Check if it's already in milliseconds (13 digits) or seconds (10 digits)
      if (timestamp > 1000000000000) {
        // Already in milliseconds
        date = new Date(timestamp);
      } else {
        // In seconds, convert to milliseconds
        date = new Date(timestamp * 1000);
      }
    }
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid Date';
    }
    
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleMarkAsWorn = async (outfitId: string) => {
    try {
      setMarkingWorn(outfitId);
      
      const idToken = await user!.getIdToken();
      
      const response = await fetch(`/api/outfit-history/mark-worn`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          outfitId: outfitId,
          dateWorn: new Date().toISOString().split('T')[0] // Today's date in YYYY-MM-DD format
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      // Update the outfit in the local state
      setOutfits(prev => prev.map(outfit => 
        outfit.id === outfitId 
          ? { ...outfit, lastWorn: Date.now() }
          : outfit
      ));
      
      hapticFeedback.success();
    } catch (error) {
      console.error('Error marking outfit as worn:', error);
      alert('Failed to mark outfit as worn. Please try again.');
    } finally {
      setMarkingWorn(null);
    }
  };

  const resetFilters = () => {
    setSearchQuery('');
    setSelectedOccasion('all');
    setSelectedStyle('all');
    setSortBy('newest');
    setVisibleItems(ITEMS_PER_PAGE);
  };

  // Show loading state while authentication is being determined
  if (authLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading Authentication...</h1>
          <p className="text-muted-foreground">Checking authentication status...</p>
        </div>
      </div>
    );
  }

  // Show sign-in prompt if user is not authenticated
  if (!user) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Sign In Required</h1>
          <p className="text-muted-foreground mb-6">Please sign in to view your outfits.</p>
          <Link href="/signin">
            <Button>Sign In</Button>
          </Link>
        </div>
      </div>
    );
  }

  // Show loading state while fetching outfits
  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">My Outfits</h1>
            <p className="text-muted-foreground">Your curated outfit collection</p>
          </div>
          <div className="flex gap-2">
            <Link href="/outfits/create">
              <Button>
                <Sparkles className="w-4 h-4 mr-2" />
                Create Outfit
              </Button>
            </Link>
            <Link href="/outfits/generate">
              <Button variant="outline">
                <ArrowRight className="w-4 h-4 mr-2" />
                Generate Outfit
              </Button>
            </Link>
          </div>
        </div>
        <PageLoadingSkeleton />
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">My Outfits</h1>
            <p className="text-muted-foreground">Your curated outfit collection</p>
          </div>
          <div className="flex gap-2">
            <Link href="/outfits/create">
              <Button>
                <Sparkles className="w-4 h-4 mr-2" />
                Create Outfit
              </Button>
            </Link>
            <Link href="/outfits/generate">
              <Button variant="outline">
                <ArrowRight className="w-4 h-4 mr-2" />
                Generate Outfit
              </Button>
            </Link>
          </div>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Error Loading Outfits</h3>
              <p className="text-muted-foreground mb-4">{error}</p>
              <Button onClick={fetchOutfits}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const displayedOutfits = filteredAndSortedOutfits.slice(0, visibleItems);

  return (
    <div className="container mx-auto py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">My Outfits</h1>
          <p className="text-muted-foreground">
            {filteredAndSortedOutfits.length} of {outfits.length} outfit{outfits.length !== 1 ? 's' : ''} in your collection
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/outfits/create">
            <Button>
              <Sparkles className="w-4 h-4 mr-2" />
              Create Outfit
            </Button>
          </Link>
          <Link href="/outfits/generate">
            <Button variant="outline">
              <ArrowRight className="w-4 h-4 mr-2" />
              Generate Outfit
            </Button>
          </Link>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input
                placeholder="Search outfits..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>

            {/* Occasion Filter */}
            <Select value={selectedOccasion} onValueChange={setSelectedOccasion}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by occasion" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Occasions</SelectItem>
                {occasions.map((occasion) => (
                  <SelectItem key={occasion} value={occasion}>
                    {occasion}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Style Filter */}
            <Select value={selectedStyle} onValueChange={setSelectedStyle}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by style" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Styles</SelectItem>
                {styles.map((style) => (
                  <SelectItem key={style} value={style}>
                    {style}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Sort */}
            <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortOption)}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="newest">Newest First</SelectItem>
                <SelectItem value="oldest">Oldest First</SelectItem>
                <SelectItem value="name">Name A-Z</SelectItem>
                <SelectItem value="rating">Highest Rated</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* View Mode and Reset */}
          <div className="flex items-center justify-between mt-4 pt-4 border-t">
            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === 'grid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('grid')}
              >
                <Grid3X3 className="w-4 h-4 mr-2" />
                Grid
              </Button>
              <Button
                variant={viewMode === 'list' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewMode('list')}
              >
                <List className="w-4 h-4 mr-2" />
                List
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={resetFilters}>
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Outfits Grid/List */}
      {displayedOutfits.length === 0 ? (
        <Card>
          <CardContent className="p-8">
            <div className="text-center">
              <Sparkles className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                {filteredAndSortedOutfits.length === 0 && outfits.length > 0 
                  ? 'No Outfits Match Your Filters' 
                  : 'No Outfits Yet'
                }
              </h3>
              <p className="text-muted-foreground mb-6">
                {filteredAndSortedOutfits.length === 0 && outfits.length > 0
                  ? 'Try adjusting your search or filters to see more outfits.'
                  : 'Start building your outfit collection by creating or generating your first outfit.'
                }
              </p>
              <div className="flex gap-3 justify-center">
                {filteredAndSortedOutfits.length === 0 && outfits.length > 0 ? (
                  <Button onClick={resetFilters}>
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Clear Filters
                  </Button>
                ) : (
                  <>
                    <Link href="/outfits/create">
                      <Button>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Create Outfit
                      </Button>
                    </Link>
                    <Link href="/outfits/generate">
                      <Button variant="outline">
                        <ArrowRight className="w-4 h-4 mr-2" />
                        Generate Outfit
                      </Button>
                    </Link>
                  </>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className={viewMode === 'grid' 
          ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" 
          : "space-y-4"
        }>
          {displayedOutfits.map((outfit) => (
            <SwipeableCard key={outfit.id} className="group">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold group-hover:text-primary transition-colors">
                      {outfit.name}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      Created {formatDate(outfit.createdAt)}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-1">
                    {outfit.userFeedback?.liked && (
                      <ThumbsUp className="w-4 h-4 text-green-500" />
                    )}
                    {outfit.feedback_summary && outfit.feedback_summary.average_rating > 0 && (
                      <div className="flex items-center gap-1">
                        <Star className="w-4 h-4 text-yellow-500 fill-current" />
                        <span className="text-sm font-medium">
                          {outfit.feedback_summary.average_rating.toFixed(1)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="pt-0">
                <div className="space-y-4">
                  {/* Occasion and Style Badges */}
                  <div className="flex flex-wrap gap-2">
                    {outfit.occasion && (
                      <Badge variant="secondary" className="text-xs">
                        {outfit.occasion}
                      </Badge>
                    )}
                    {outfit.style && (
                      <Badge variant="outline" className="text-xs">
                        {Array.isArray(outfit.style) ? outfit.style[0] : outfit.style}
                      </Badge>
                    )}
                  </div>

                  {/* Items Grid */}
                  <div className={viewMode === 'grid' 
                    ? "grid grid-cols-2 gap-2" 
                    : "grid grid-cols-4 gap-2"
                  }>
                    {outfit.items.slice(0, viewMode === 'grid' ? 4 : 8).map((item) => (
                      <div
                        key={item.id}
                        className="aspect-square bg-muted rounded-lg border border-border overflow-hidden relative"
                      >
                        {item.imageUrl ? (
                          <img
                            src={item.imageUrl}
                            alt={item.name}
                            className="w-full h-full object-cover"
                            loading="lazy"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <div className="text-center p-2">
                              <div className="w-6 h-6 bg-muted-foreground/20 rounded mx-auto mb-1" />
                              <p className="text-xs text-muted-foreground font-medium truncate">
                                {item.name}
                              </p>
                            </div>
                          </div>
                        )}
                        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-1">
                          <p className="text-white text-xs truncate">{item.name}</p>
                        </div>
                      </div>
                    ))}
                    {outfit.items.length > (viewMode === 'grid' ? 4 : 8) && (
                      <div className="aspect-square bg-muted rounded-lg border border-border flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-sm font-medium text-muted-foreground">
                            +{outfit.items.length - (viewMode === 'grid' ? 4 : 8)} more
                          </p>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 pt-2">
                    <InteractiveButton
                      onClick={() => handleMarkAsWorn(outfit.id)}
                      disabled={markingWorn === outfit.id}
                      className="flex-1"
                      variant="outline"
                      size="sm"
                    >
                      {markingWorn === outfit.id ? (
                        <>
                          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                          Marking...
                        </>
                      ) : (
                        <>
                          <Calendar className="w-3 h-3 mr-1" />
                          Mark as Worn
                        </>
                      )}
                    </InteractiveButton>
                    
                    <Link href={`/outfits/${outfit.id}`}>
                      <InteractiveButton
                        variant="outline"
                        size="sm"
                        className="px-2"
                      >
                        <Eye className="w-3 h-3" />
                      </InteractiveButton>
                    </Link>
                  </div>

                  {/* Feedback Summary */}
                  {outfit.feedback_summary && outfit.feedback_summary.total_feedback > 0 && (
                    <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t">
                      <div className="flex items-center gap-2">
                        <ThumbsUp className="w-3 h-3" />
                        <span>{outfit.feedback_summary.likes}</span>
                        <ThumbsDown className="w-3 h-3" />
                        <span>{outfit.feedback_summary.dislikes}</span>
                      </div>
                      <span>{outfit.feedback_summary.total_feedback} reviews</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </SwipeableCard>
          ))}
        </div>
      )}

      {/* Load More Trigger */}
      {hasMore && (
        <div ref={loadMoreRef} className="flex justify-center mt-8">
          <div className="text-center">
            <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading more outfits...</p>
          </div>
        </div>
      )}

      {/* End of Results */}
      {!hasMore && displayedOutfits.length > 0 && (
        <div className="text-center mt-8">
          <p className="text-sm text-muted-foreground">
            You've reached the end of your outfits
          </p>
        </div>
      )}
    </div>
  );
} 