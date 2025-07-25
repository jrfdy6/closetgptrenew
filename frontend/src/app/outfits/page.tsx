'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Star, ThumbsUp, ThumbsDown, AlertTriangle, Calendar, Eye, CheckCircle, Sparkles, ArrowRight } from 'lucide-react';
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

  useEffect(() => {
    console.log('🔍 Outfits page useEffect - authLoading:', authLoading, 'user:', user);
    
    // Don't make API calls if user is not authenticated or still loading
    if (authLoading) {
      console.log('🔍 Still loading auth...');
      return;
    }

    if (!user) {
      console.log('🔍 No user, setting loading to false');
      setLoading(false);
      return;
    }

    const fetchOutfits = async () => {
      try {
        setLoading(true);
        console.log('🔍 Fetching outfits for user:', user.uid);
        
        // Get the user's ID token for authentication
        const idToken = await user.getIdToken();
        
        // Fetch real outfits from the API
        const response = await fetch('/api/outfits', {
          headers: {
            'Authorization': `Bearer ${idToken}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const outfitsData = await response.json();
        console.log('🔍 Fetched outfits:', outfitsData);
        
        // Transform the API response to match our interface
        const transformedOutfits: Outfit[] = outfitsData.map((outfit: any) => ({
          id: outfit.id,
          name: outfit.name || 'Untitled Outfit',
          description: outfit.reasoning || '',
          occasion: outfit.occasion || 'Casual',
          style: outfit.style || '',
          createdAt: new Date(outfit.createdAt).getTime() / 1000,
          items: outfit.items || [],
          feedback_summary: outfit.feedback_summary,
          userFeedback: outfit.userFeedback
        }));
        
        setOutfits(transformedOutfits);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching outfits:', err);
        setError('Failed to load outfits');
        setLoading(false);
      }
    };

    fetchOutfits();
  }, [user, authLoading]);

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
      console.log('🔍 Marking outfit as worn:', outfitId);
      
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

  console.log('🔍 Rendering outfits page - authLoading:', authLoading, 'loading:', loading, 'user:', user);

  // Show loading state while authentication is being determined
  if (authLoading) {
    console.log('🔍 Showing auth loading state');
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Loading Authentication...</h1>
          <p className="text-muted-foreground">Checking authentication status...</p>
          <p className="text-sm text-muted-foreground mt-2">authLoading: {authLoading.toString()}</p>
          <p className="text-sm text-muted-foreground mt-2">User: {user ? 'Logged in' : 'Not logged in'}</p>
          <div className="mt-4">
            <Link href="/signin">
              <Button>Go to Login</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Show login prompt if user is not authenticated
  if (!user) {
    console.log('🔍 No user found, showing login prompt');
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Please Log In</h1>
          <p className="text-muted-foreground mb-4">You need to be logged in to view your outfits.</p>
          <p className="text-sm text-muted-foreground mb-4">User: {user ? 'Logged in' : 'Not logged in'}</p>
                        <Link href="/signin">
            <Button>Log In</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="container-readable space-section py-8">
        <PageLoadingSkeleton 
          showHero={true}
          showStats={false}
          showContent={true}
        />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Error</h1>
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container-readable space-section py-8">
      {/* Hero Header */}
      <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h1 className="text-2xl sm:text-hero text-foreground">Your Outfits</h1>
            </div>
            <p className="text-secondary text-base sm:text-lg">
              {outfits.length} outfit{outfits.length !== 1 ? 's' : ''} • 
              {outfits.filter(o => o.feedback_summary?.total_feedback).length} with feedback
            </p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
            <Button variant="outline" asChild className="shadow-md hover:shadow-lg w-full sm:w-auto">
              <Link href="/outfits/create">
                Create Custom Outfit
              </Link>
            </Button>
            <Button asChild className="shadow-md hover:shadow-lg w-full sm:w-auto">
              <Link href="/outfits/generate">
                Generate New Outfit
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="grid-outfits">
        {outfits.map((outfit, index) => (
          <SwipeableCard
            key={outfit.id}
            onSwipeLeft={() => {
              hapticFeedback.success();
              console.log('Swiped left on outfit:', outfit.name);
              // TODO: Implement dislike or archive
            }}
            onSwipeRight={() => {
              hapticFeedback.success();
              console.log('Swiped right on outfit:', outfit.name);
              // TODO: Implement like or favorite
            }}
            threshold={50}
          >
            <HoverCard intensity={5}>
              <Card className={`card-hover animate-fade-in stagger-${Math.min(index + 1, 6)}`}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-subheader">{outfit.name}</CardTitle>
                  {outfit.description && (
                    <CardDescription className="mt-2 text-secondary">{outfit.description}</CardDescription>
                  )}
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center gap-2 text-secondary">
                  <Calendar className="w-4 h-4" />
                  {formatDate(outfit.createdAt)}
                </div>
                
                <div className="space-y-3">
                  {outfit.occasion && (
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs bg-emerald-50 text-emerald-700 border-emerald-200">
                        {outfit.occasion}
                      </Badge>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-2 text-secondary">
                    <Eye className="w-4 h-4" />
                    {outfit.items.length} item{outfit.items.length !== 1 ? 's' : ''}
                  </div>
                </div>
                
                <div className="pt-3 space-y-3">
                  <div className="flex gap-2">
                    <InteractiveButton
                      variant="outline"
                      size="sm"
                      className="flex-1 shadow-sm hover:shadow-md"
                      onClick={() => handleMarkAsWorn(outfit.id)}
                      disabled={markingWorn === outfit.id}
                      hapticType="success"
                    >
                      {markingWorn === outfit.id ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                          Marking...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Mark as Worn
                        </>
                      )}
                    </InteractiveButton>
                    <InteractiveButton
                      variant="outline"
                      size="sm"
                      className="shadow-sm hover:shadow-md"
                      hapticType="light"
                      onClick={() => {
                        // Navigate to outfit details
                        window.location.href = `/outfits/${outfit.id}`;
                      }}
                    >
                      <Eye className="w-4 h-4" />
                    </InteractiveButton>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
            </HoverCard>
          </SwipeableCard>
        ))}
      </div>
      
      {outfits.length === 0 && (
        <Card className="card-enhanced p-12 text-center">
          <div className="w-20 h-20 bg-gradient-to-br from-emerald-500/20 to-yellow-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Sparkles className="w-10 h-10 text-emerald-600" />
          </div>
          <h3 className="text-subheader mb-3">No Outfits Yet</h3>
          <p className="text-secondary mb-6 max-w-md mx-auto">
            Start generating outfits to see them here with feedback and ratings.
          </p>
          <Button asChild className="shadow-md hover:shadow-lg">
            <Link href="/outfits/generate">
              Generate Your First Outfit
              <ArrowRight className="w-4 h-4 ml-2" />
            </Link>
          </Button>
        </Card>
      )}
    </div>
  );
} 