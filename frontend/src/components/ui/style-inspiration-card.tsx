"use client"

import React, { useState } from 'react';
import { Button } from './button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './card';
import { Badge } from './badge';
import { Skeleton } from './skeleton';
import { Sparkles, RefreshCw, X, Heart, Info } from 'lucide-react';
import { useAuthContext } from '@/contexts/AuthContext';

export interface StyleInspiration {
  id: string;
  title: string;
  brand: string;
  price: string;
  price_cents: number;
  currency: string;
  image_url: string;
  categories: string[];
  tags: string[];
  style_vector: Record<string, number>;
  classification: 'reinforce' | 'bridge' | 'expand';
  similarity_score: number;
  weather_score: number;
  final_score: number;
  rationale: string;
  seasonality: string[];
  materials: string[];
}

interface StyleInspirationCardProps {
  onRefresh?: () => void;
  className?: string;
}

export function StyleInspirationCard({ onRefresh, className = '' }: StyleInspirationCardProps) {
  const { user } = useAuthContext();
  const [inspiration, setInspiration] = useState<StyleInspiration | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [excludedIds, setExcludedIds] = useState<string[]>([]);
  const [showDetails, setShowDetails] = useState(false);

  const classificationColors = {
    reinforce: 'bg-blue-100 text-blue-800',
    bridge: 'bg-purple-100 text-purple-800',
    expand: 'bg-green-100 text-green-800',
  };

  const classificationLabels = {
    reinforce: 'Reinforce Your Style',
    bridge: 'Bridge Styles',
    expand: 'Expand Your Range',
  };

  const fetchInspiration = async () => {
    setLoading(true);
    setError(null);

    try {
      // Check if user is logged in
      if (!user) {
        setError('Please log in to get style inspiration');
        setLoading(false);
        return;
      }

      // Get Firebase auth token
      const token = await user.getIdToken();

      const response = await fetch('/api/style-inspiration/get-inspiration', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          excluded_ids: excludedIds,
          weather: null, // Can be enhanced to fetch current weather
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch inspiration: ${response.statusText}`);
      }

      const data = await response.json();

      if (data.success && data.inspiration) {
        setInspiration(data.inspiration);
        setExcludedIds([...excludedIds, data.inspiration.id]);
      } else {
        setError(data.message || 'No inspiration available');
      }
    } catch (err) {
      console.error('Error fetching inspiration:', err);
      setError(err instanceof Error ? err.message : 'Failed to load inspiration');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchInspiration();
    onRefresh?.();
  };

  const handleDismiss = () => {
    setInspiration(null);
  };

  const handleReset = () => {
    setExcludedIds([]);
    setInspiration(null);
  };

  // Auto-fetch on mount (only when user is available)
  React.useEffect(() => {
    if (user && !inspiration && !loading) {
      fetchInspiration();
    }
  }, [user]);

  if (loading) {
    return (
      <Card className={`w-full max-w-md ${className}`}>
        <CardHeader>
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2 mt-2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-64 w-full rounded-lg" />
          <div className="mt-4 space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={`w-full max-w-md ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Style Inspiration
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-red-600 mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!inspiration) {
    return (
      <Card className={`w-full max-w-md ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Style Inspiration
          </CardTitle>
          <CardDescription>
            Discover pieces that complement your style
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={fetchInspiration} className="w-full">
            <Sparkles className="w-4 h-4 mr-2" />
            Get Inspiration
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Get top 3 style scores for display
  const topStyles = Object.entries(inspiration.style_vector)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);

  return (
    <Card className={`w-full max-w-md ${className} relative`}>
      {/* Header */}
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="flex items-center gap-2 text-lg">
              <Sparkles className="w-5 h-5 text-yellow-500" />
              Style Inspiration
            </CardTitle>
            <Badge
              className={`mt-2 ${classificationColors[inspiration.classification]}`}
              variant="secondary"
            >
              {classificationLabels[inspiration.classification]}
            </Badge>
          </div>
          <Button
            onClick={handleDismiss}
            variant="ghost"
            size="icon"
            className="h-8 w-8"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </CardHeader>

      {/* Image */}
      <CardContent className="space-y-4">
        <div className="relative rounded-lg overflow-hidden bg-gray-100">
          <img
            src={inspiration.image_url}
            alt={inspiration.title}
            className="w-full h-64 object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src =
                'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400';
            }}
          />
        </div>

        {/* Item Info */}
        <div>
          <h3 className="font-semibold text-lg">{inspiration.title}</h3>
          <p className="text-sm text-gray-600">{inspiration.brand}</p>
          <p className="text-lg font-bold text-gray-900 mt-1">
            {inspiration.price}
          </p>
        </div>

        {/* Rationale */}
        <div className="bg-gray-50 p-3 rounded-lg">
          <p className="text-sm text-gray-700 leading-relaxed">
            {inspiration.rationale}
          </p>
        </div>

        {/* Style Scores */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs font-medium text-gray-600">
            <span>Style Match</span>
            <Button
              onClick={() => setShowDetails(!showDetails)}
              variant="ghost"
              size="sm"
              className="h-6 px-2"
            >
              <Info className="w-3 h-3 mr-1" />
              {showDetails ? 'Hide' : 'Details'}
            </Button>
          </div>

          {showDetails && (
            <div className="space-y-1">
              {topStyles.map(([style, score]) => (
                <div key={style} className="flex items-center gap-2">
                  <span className="text-xs text-gray-600 w-24">{style}</span>
                  <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                      style={{ width: `${score * 100}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-gray-700">
                    {Math.round(score * 100)}%
                  </span>
                </div>
              ))}
            </div>
          )}

          {/* Tags */}
          <div className="flex flex-wrap gap-1 mt-2">
            {inspiration.tags.slice(0, 4).map((tag) => (
              <Badge key={tag} variant="outline" className="text-xs">
                {tag}
              </Badge>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <Button
            onClick={handleRefresh}
            className="flex-1"
            variant="default"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Show Another
          </Button>
          <Button
            onClick={() => alert('Save to wishlist (coming soon!)')}
            variant="outline"
            size="icon"
          >
            <Heart className="w-4 h-4" />
          </Button>
        </div>

        {/* Reset button (shown after viewing multiple items) */}
        {excludedIds.length > 3 && (
          <Button
            onClick={handleReset}
            variant="ghost"
            size="sm"
            className="w-full text-xs"
          >
            Reset & Start Over
          </Button>
        )}

        {/* Debug info (can be removed in production) */}
        {process.env.NODE_ENV === 'development' && (
          <div className="text-xs text-gray-400 pt-2 border-t">
            <p>Similarity: {Math.round(inspiration.similarity_score * 100)}%</p>
            <p>Weather: {Math.round(inspiration.weather_score * 100)}%</p>
            <p>Final Score: {Math.round(inspiration.final_score * 100)}%</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

