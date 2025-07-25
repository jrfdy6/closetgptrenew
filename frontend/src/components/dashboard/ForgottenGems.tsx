'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Sparkles, 
  Clock, 
  Heart, 
  Trash2, 
  RefreshCw, 
  AlertTriangle,
  Calendar,
  TrendingUp,
  Palette,
  Zap
} from 'lucide-react';
import Image from 'next/image';
import { getFirebaseIdToken } from '@/lib/utils/auth';

interface ForgottenItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  color: string;
  style: string[];
  lastWorn?: number; // timestamp
  daysSinceWorn: number;
  usageCount: number;
  favoriteScore: number;
  suggestedOutfits: string[];
  declutterReason?: string;
  rediscoveryPotential: number; // 0-100 score
}

interface ForgottenGemsData {
  forgottenItems: ForgottenItem[];
  totalUnwornItems: number;
  potentialSavings: number;
  rediscoveryOpportunities: number;
  analysis_timestamp: string;
}

const ForgottenGems: React.FC = () => {
  const [forgottenData, setForgottenData] = useState<ForgottenGemsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Function to shuffle array and get top 3 items
  const getTop3RotatedItems = (items: ForgottenItem[]): ForgottenItem[] => {
    if (items.length <= 3) return items;
    
    // Create a copy of the array and shuffle it
    const shuffled = [...items].sort(() => Math.random() - 0.5);
    
    // Return top 3 items (highest rediscovery potential first)
    return shuffled
      .sort((a, b) => b.rediscoveryPotential - a.rediscoveryPotential)
      .slice(0, 3);
  };

  const fetchForgottenGems = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get authentication token
      const token = await getFirebaseIdToken();
      if (!token) {
        setError('Authentication required');
        setLoading(false);
        return;
      }
      
      // Call the real API endpoint
      const response = await fetch('/api/wardrobe/forgotten-gems', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch forgotten gems');
      }
      
      const result = await response.json();
      
      if (result.success) {
        // Rotate and limit to top 3 items
        const rotatedData = {
          ...result.data,
          forgottenItems: getTop3RotatedItems(result.data.forgottenItems)
        };
        setForgottenData(rotatedData);
      } else {
        throw new Error(result.message || 'Failed to fetch forgotten gems');
      }
      
    } catch (err) {
      console.error('Error fetching forgotten gems:', err);
      setError('Error loading forgotten items');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchForgottenGems();
  }, [fetchForgottenGems]);

  const handleStyleItem = (item: ForgottenItem) => {
    // Navigate to outfit generator with this item pre-selected
    window.location.href = `/outfits/generate?item=${encodeURIComponent(item.id)}`;
  };

  const handleDeclutterItem = async (item: ForgottenItem) => {
    try {
      // Get authentication token
      const token = await getFirebaseIdToken();
      if (!token) {
        alert('Authentication required');
        return;
      }
      
      // Call the API to mark item for decluttering
      const response = await fetch('/api/wardrobe/forgotten-gems', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: item.id,
          action: 'declutter'
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to mark item for decluttering');
      }
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Marking "${item.name}" for decluttering. This item will be moved to your declutter list.`);
        // Refresh the data
        fetchForgottenGems();
      } else {
        throw new Error(result.message || 'Failed to mark item for decluttering');
      }
      
    } catch (err) {
      console.error('Error decluttering item:', err);
      alert('Error marking item for decluttering. Please try again.');
    }
  };

  const handleRediscoverItem = async (item: ForgottenItem) => {
    try {
      // Get authentication token
      const token = await getFirebaseIdToken();
      if (!token) {
        alert('Authentication required');
        return;
      }
      
      // Call the API to mark item as rediscovered
      const response = await fetch('/api/wardrobe/forgotten-gems', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: item.id,
          action: 'rediscover'
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to rediscover item');
      }
      
      const result = await response.json();
      
      if (result.success) {
        alert(`"${item.name}" has been marked as rediscovered! We'll suggest it in future outfit generations.`);
        // Refresh the data
        fetchForgottenGems();
      } else {
        throw new Error(result.message || 'Failed to rediscover item');
      }
      
    } catch (err) {
      console.error('Error rediscovering item:', err);
      alert('Error rediscovering item. Please try again.');
    }
  };

  const getRediscoveryColor = (potential: number) => {
    if (potential >= 80) return 'text-green-600 bg-green-100';
    if (potential >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getRediscoveryIcon = (potential: number) => {
    if (potential >= 80) return <Sparkles className="w-4 h-4" />;
    if (potential >= 60) return <RefreshCw className="w-4 h-4" />;
    return <AlertTriangle className="w-4 h-4" />;
  };

  const formatTimeAgo = (days: number) => {
    if (days >= 365) return `${Math.floor(days / 365)} year${Math.floor(days / 365) > 1 ? 's' : ''} ago`;
    if (days >= 30) return `${Math.floor(days / 30)} month${Math.floor(days / 30) > 1 ? 's' : ''} ago`;
    if (days >= 7) return `${Math.floor(days / 7)} week${Math.floor(days / 7) > 1 ? 's' : ''} ago`;
    return `${days} day${days > 1 ? 's' : ''} ago`;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Forgotten Gems
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 rounded w-1/4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Forgotten Gems
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
          <Button onClick={fetchForgottenGems} variant="outline" size="sm" className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!forgottenData || forgottenData.forgottenItems.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Forgotten Gems
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Sparkles className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground mb-2">No forgotten items found!</p>
            <p className="text-sm text-muted-foreground">
              Great job keeping your wardrobe active. Keep using items regularly to maintain a healthy closet.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full overflow-hidden border border-border bg-card shadow-xl">
      <CardHeader className="bg-gradient-to-r from-amber-600 to-orange-600 text-white pb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold">Forgotten Gems</CardTitle>
              <p className="text-amber-100 text-sm">Rediscover items you haven't worn in a while</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{forgottenData.totalUnwornItems}</div>
              <div className="text-xs text-amber-100">Unworn Items</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{forgottenData.rediscoveryOpportunities}</div>
              <div className="text-xs text-amber-100">Rediscovery Opportunities</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">${forgottenData.potentialSavings}</div>
              <div className="text-xs text-amber-100">Potential Savings</div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6">
        <Alert className="mb-6 border-amber-200 bg-amber-50 dark:bg-amber-950/30 dark:border-amber-800">
          <Sparkles className="h-4 w-4 text-amber-600" />
          <AlertDescription className="text-amber-800 dark:text-amber-200">
            Showing top 3 items with highest rediscovery potential. Refresh to see different items!
          </AlertDescription>
        </Alert>

        {/* Forgotten Items List - Now limited to top 3 */}
        <div className="space-y-4">
          {forgottenData.forgottenItems.map((item) => (
            <Card key={item.id} className="overflow-hidden border border-border">
              <CardContent className="p-6">
                <div className="flex gap-4">
                  {/* Image Section */}
                  <div className="relative w-24 h-24 flex-shrink-0">
                    <Image
                      src={item.imageUrl || '/placeholder.svg'}
                      alt={item.name}
                      fill
                      className="object-cover rounded-lg border border-border"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.src = '/placeholder.svg';
                        target.onerror = null;
                      }}
                    />
                  </div>
                  
                  {/* Content Section */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <h4 className="font-semibold text-foreground">{item.name}</h4>
                        <p className="text-sm text-muted-foreground capitalize">{item.type}</p>
                      </div>
                      <Badge className={getRediscoveryColor(item.rediscoveryPotential)}>
                        {getRediscoveryIcon(item.rediscoveryPotential)}
                        <span className="ml-1">{item.rediscoveryPotential}% potential</span>
                      </Badge>
                    </div>
                    
                    {/* Usage Stats */}
                    <div className="flex items-center gap-4 text-sm text-muted-foreground mb-3">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        <span>Last worn {formatTimeAgo(item.daysSinceWorn)}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        <span>{item.usageCount} times used</span>
                      </div>
                    </div>
                    

                    
                    {/* Declutter Reason */}
                    {item.declutterReason && (
                      <div className="mb-3 p-2 bg-red-50 rounded text-sm text-red-700">
                        <AlertTriangle className="w-3 h-3 inline mr-1" />
                        {item.declutterReason}
                      </div>
                    )}
                    
                    {/* Action Buttons */}
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        onClick={() => handleStyleItem(item)}
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        <Sparkles className="w-3 h-3 mr-1" />
                        Style It
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleRediscoverItem(item)}
                      >
                        <RefreshCw className="w-3 h-3 mr-1" />
                        Rediscover
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleDeclutterItem(item)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-3 h-3 mr-1" />
                        Declutter
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

      </CardContent>
    </Card>
  );
};

export default ForgottenGems;