"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, ThumbsUp, ThumbsDown, AlertTriangle, Calendar, Eye, CheckCircle, Sparkles, ArrowRight, RefreshCw } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import { PageLoadingSkeleton } from '@/components/ui/loading-states';
import { SwipeableCard, InteractiveButton, HoverCard, hapticFeedback } from '@/components/ui/micro-interactions';

interface Outfit {
  id: string;
  name: string;
  description?: string;
  occasion?: string;
  season?: string;
  style?: string | string[];
  style_tags?: string[];
  createdAt: number;
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

export default function OutfitsPage() {
  const { user, loading: authLoading } = useFirebase();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingWorn, setMarkingWorn] = useState<string | null>(null);

  const fetchOutfits = useCallback(async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Get the user's ID token for authentication
      const idToken = await user.getIdToken();
      
      // Fetch outfits from the API
      const response = await fetch('/api/outfits', {
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 504) {
          throw new Error('Backend is currently unavailable. Please try again in a few minutes.');
        }
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const outfitsData = await response.json();
      
      // DEBUG: Log the raw data
      console.log('🔍 DEBUG: Raw outfits data received:', outfitsData);
      console.log('🔍 DEBUG: Data type:', typeof outfitsData);
      console.log('🔍 DEBUG: Is array?', Array.isArray(outfitsData));
      
      // Handle the backend response format
      const outfitsArray = outfitsData.outfits || outfitsData;
      
      // DEBUG: Log the processed array
      console.log('🔍 DEBUG: Processed outfits array:', outfitsArray);
      console.log('🔍 DEBUG: Array length:', outfitsArray.length);
      
      // Ensure we have an array to map over
      if (!Array.isArray(outfitsArray)) {
        console.error('Expected outfits array but got:', outfitsArray);
        setOutfits([]);
        setLoading(false);
        return;
      }
      
      // Transform the API response to match our interface
      const transformedOutfits: Outfit[] = outfitsArray.map((outfit: any) => ({
        id: outfit.id,
        name: outfit.name || 'Untitled Outfit',
        description: outfit.reasoning || '',
        occasion: outfit.occasion || 'Casual',
        style: outfit.style || '',
        createdAt: typeof outfit.createdAt === 'string' ? new Date(outfit.createdAt).getTime() / 1000 : outfit.createdAt / 1000,
        items: outfit.items || [],
        feedback_summary: outfit.feedback_summary,
        userFeedback: outfit.userFeedback
      }));
      
      // DEBUG: Log the final transformed outfits
      console.log('🔍 DEBUG: Final transformed outfits:', transformedOutfits);
      console.log('🔍 DEBUG: Final count:', transformedOutfits.length);
      
      setOutfits(transformedOutfits);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching outfits:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to load outfits';
      
      // Provide more user-friendly error messages
      let userFriendlyError = errorMessage;
      if (errorMessage.includes('504') || errorMessage.includes('timeout')) {
        userFriendlyError = 'Backend is currently unavailable. Please try again in a few minutes.';
      } else if (errorMessage.includes('403') || errorMessage.includes('Not authenticated')) {
        userFriendlyError = 'Authentication issue. Please refresh the page and try again.';
      } else if (errorMessage.includes('500')) {
        userFriendlyError = 'Server error. Please try again in a moment.';
      }
      
      setError(userFriendlyError);
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    if (authLoading) {
      return;
    }

    if (!user) {
      return;
    }

    fetchOutfits();
  }, [user, authLoading, fetchOutfits]);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleMarkAsWorn = async (outfitId: string) => {
    try {
      setMarkingWorn(outfitId);
      
      // Get the user's ID token for authentication
      const idToken = await user!.getIdToken();
      
      // Call the real API to mark outfit as worn
      const response = await fetch(`/api/outfit-history/mark-worn`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${idToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ outfit_id: outfitId }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      alert('Outfit marked as worn successfully!');
    } catch (error) {
      console.error('Error marking outfit as worn:', error);
      alert('Failed to mark outfit as worn. Please try again.');
    } finally {
      setMarkingWorn(null);
    }
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

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">My Outfits</h1>
          <p className="text-muted-foreground">
            {outfits.length} outfit{outfits.length !== 1 ? 's' : ''} in your collection
            {/* DEBUG: Show the actual count */}
            <span className="text-xs text-red-500 ml-2">(DEBUG: {outfits.length})</span>
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

      {outfits.length === 0 ? (
        <Card>
          <CardContent className="p-8">
            <div className="text-center">
              <Sparkles className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Outfits Yet</h3>
              <p className="text-muted-foreground mb-6">
                Start building your outfit collection by creating or generating your first outfit.
              </p>
              <div className="flex gap-3 justify-center">
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
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {outfits.map((outfit) => (
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
                  <div className="grid grid-cols-2 gap-2">
                    {outfit.items.slice(0, 4).map((item) => (
                      <div
                        key={item.id}
                        className="aspect-square bg-muted rounded-lg border border-border overflow-hidden relative"
                      >
                        {item.imageUrl ? (
                          <img
                            src={item.imageUrl}
                            alt={item.name}
                            className="w-full h-full object-cover"
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
                    {outfit.items.length > 4 && (
                      <div className="aspect-square bg-muted rounded-lg border border-border flex items-center justify-center">
                        <div className="text-center">
                          <p className="text-sm font-medium text-muted-foreground">
                            +{outfit.items.length - 4} more
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
                    
                                         <InteractiveButton
                       variant="outline"
                       size="sm"
                       className="px-2"
                       onClick={() => {
                         // TODO: Navigate to outfit details
                         console.log('View outfit details:', outfit.id);
                       }}
                     >
                       <Eye className="w-3 h-3" />
                     </InteractiveButton>
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
    </div>
  );
} 