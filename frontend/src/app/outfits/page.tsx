'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Plus, Palette, Star } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';

interface Outfit {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  createdAt: string;
}

export default function OutfitsPage() {
  const { user, loading: authLoading } = useFirebase();
  const [outfits, setOutfits] = useState<Outfit[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user && !authLoading) {
      fetchOutfits();
    }
  }, [user, authLoading]);

  const fetchOutfits = async () => {
    try {
      if (!user) {
        setError('Please sign in to view outfits');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      
      const response = await fetch('/api/outfits', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view outfits.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data = await response.json();
      setOutfits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch outfits');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">
              {authLoading ? 'Authenticating...' : 'Loading your outfits...'}
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <Palette className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
          <p className="text-muted-foreground mb-4">Please sign in to view your outfits</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center">
          <Palette className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">Unable to Load Outfits</h2>
          <p className="text-muted-foreground mb-4">{error}</p>
          <Button onClick={fetchOutfits}>Try Again</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">My Outfits</h1>
          <p className="text-muted-foreground">Your AI-generated style combinations</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Generate New Outfit
        </Button>
      </div>

      {outfits.length === 0 ? (
        <div className="text-center py-12">
          <Palette className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
          <h2 className="text-xl font-semibold mb-2">No Outfits Yet</h2>
          <p className="text-muted-foreground mb-4">
            Start by generating your first AI-powered outfit combination
          </p>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Generate Outfit
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {outfits.map((outfit) => (
            <Card key={outfit.id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <CardTitle className="text-lg">{outfit.name}</CardTitle>
                  <div className="flex items-center space-x-1">
                    <Star className="h-4 w-4 text-yellow-500 fill-current" />
                    <span className="text-sm text-muted-foreground">
                      {Math.round(outfit.confidence_score * 100)}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                  <span className="capitalize">{outfit.style}</span>
                  <span>•</span>
                  <span className="capitalize">{outfit.mood}</span>
                  <span>•</span>
                  <span className="capitalize">{outfit.occasion}</span>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <p className="text-sm text-muted-foreground">
                    {outfit.items.length} items
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {outfit.items.slice(0, 3).map((item) => (
                      <span
                        key={item.id}
                        className="inline-block px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded"
                      >
                        {item.type}
                      </span>
                    ))}
                    {outfit.items.length > 3 && (
                      <span className="inline-block px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded">
                        +{outfit.items.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
