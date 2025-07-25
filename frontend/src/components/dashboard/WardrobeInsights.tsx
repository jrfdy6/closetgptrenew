import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Image from 'next/image';
import { Heart, Star, TrendingUp, Eye, Edit, MousePointer } from 'lucide-react';
import { getFirebaseIdToken } from '@/lib/utils/auth';

interface FavoriteItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  color: string;
  style: string[];
  favorite_score: number;
  usage_count: number;
  feedback_score: number;
  interaction_score: number;
  style_match_score: number;
  base_item_score: number;
}

interface CategoryTopItem {
  category: string;
  item: FavoriteItem;
}

export default function WardrobeInsights() {
  const [favorites, setFavorites] = useState<FavoriteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFavorites = async () => {
      try {
        setLoading(true);
        console.log('🔍 WardrobeInsights: Starting to fetch favorites');
        
        const token = await getFirebaseIdToken();
        console.log('🔍 WardrobeInsights: Token retrieved:', !!token);
        
        // If no token, show empty state instead of making API call
        if (!token) {
          console.log('⚠️ WardrobeInsights: No token available, showing empty state');
          setFavorites([]);
          setLoading(false);
          return;
        }
        
        const headers = new Headers();
        headers.set('Authorization', `Bearer ${token}`);
        console.log('🔍 WardrobeInsights: Authorization header set');
        
        // Fetch all favorites
        console.log('🔍 WardrobeInsights: Making API call for all favorites...');
        const allFavoritesResponse = await fetch('/api/item-analytics/favorites?limit=20', { headers });
        
        console.log('🔍 WardrobeInsights: All favorites response status:', allFavoritesResponse.status);

        if (allFavoritesResponse.ok) {
          const allData = await allFavoritesResponse.json();
          console.log('🔍 WardrobeInsights: All favorites data:', allData);
          
          if (allData.favorites && allData.favorites.length > 0) {
            console.log('🔍 WardrobeInsights: Setting favorites:', allData.favorites);
            setFavorites(allData.favorites);
          } else {
            console.log('🔍 WardrobeInsights: No favorites found');
            setFavorites([]);
          }
        } else if (allFavoritesResponse.status === 401) {
          console.log('⚠️ WardrobeInsights: Unauthorized, user may not be logged in');
          setFavorites([]);
          setError('Please log in to view your favorites');
        } else {
          console.log('⚠️ WardrobeInsights: API response not ok:', allFavoritesResponse.status);
          setFavorites([]);
        }
      } catch (err) {
        console.error('❌ WardrobeInsights: Error fetching favorites:', err);
        setError('Failed to load favorite items');
      } finally {
        setLoading(false);
      }
    };

    fetchFavorites();
  }, []);

  // Get top item from each category
  const getTopItemsByCategory = (): CategoryTopItem[] => {
    const categories = ['top', 'bottom', 'shoe', 'accessory'];
    const topItems: CategoryTopItem[] = [];

    console.log('🔍 WardrobeInsights: Processing favorites:', favorites.map(f => ({ name: f.name, type: f.type, score: f.favorite_score })));

    categories.forEach(category => {
      // Map category to actual item types in the database
      let itemTypes: string[] = [];
      switch (category.toLowerCase()) {
        case 'top':
          itemTypes = ['shirt', 'sweater', 'jacket', 'blouse', 't-shirt', 'top'];
          break;
        case 'bottom':
          itemTypes = ['pants', 'shorts', 'jeans', 'skirt', 'trousers', 'bottom'];
          break;
        case 'shoe':
          itemTypes = ['shoes', 'sneakers', 'boots', 'sandals', 'heels', 'shoe'];
          break;
        case 'accessory':
          itemTypes = ['accessory', 'bag', 'hat', 'scarf', 'jewelry', 'belt', 'watch'];
          break;
        default:
          itemTypes = [category];
      }

      // Filter items by any of the mapped types (case insensitive)
      const categoryItems = favorites.filter(item => 
        itemTypes.some(type => item.type.toLowerCase() === type.toLowerCase())
      );

      console.log(`🔍 WardrobeInsights: Category "${category}" (types: ${itemTypes.join(', ')}) found ${categoryItems.length} items:`, 
        categoryItems.map(item => ({ name: item.name, type: item.type, score: item.favorite_score })));

      if (categoryItems.length > 0) {
        // Sort by favorite score and get the top one
        const topItem = categoryItems.sort((a, b) => b.favorite_score - a.favorite_score)[0];
        topItems.push({
          category,
          item: topItem
        });
        console.log(`✅ WardrobeInsights: Top ${category}: ${topItem.name} (${topItem.type}) with score ${topItem.favorite_score}`);
      } else {
        console.log(`⚠️ WardrobeInsights: No items found for category "${category}"`);
      }
    });

    console.log('🔍 WardrobeInsights: Final top items by category:', topItems.map(t => ({ category: t.category, name: t.item.name, type: t.item.type })));
    return topItems;
  };

  const getCategoryIcon = (category: string) => {
    switch (category.toLowerCase()) {
      case 'top':
        return '👕';
      case 'bottom':
        return '👖';
      case 'shoe':
        return '👟';
      case 'accessory':
        return '💍';
      default:
        return '👕';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'top':
        return 'text-blue-600';
      case 'bottom':
        return 'text-green-600';
      case 'shoe':
        return 'text-purple-600';
      case 'accessory':
        return 'text-orange-600';
      default:
        return 'text-gray-600';
    }
  };

  const renderTopItemCard = (categoryTopItem: CategoryTopItem, index: number) => {
    const { category, item } = categoryTopItem;
    
    return (
      <Card key={item.id} className="overflow-hidden border border-border bg-card hover:bg-accent/50 transition-colors">
        <CardHeader className="pb-3 bg-gradient-to-r from-muted/50 to-background">
          <CardTitle className="flex items-center gap-2 text-lg text-foreground">
            <span className="text-2xl">{getCategoryIcon(category)}</span>
            <span className={getCategoryColor(category)}>
              Top {category.charAt(0).toUpperCase() + category.slice(1)}
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4">
          <div className="flex gap-4">
            {/* Image Section */}
            <div className="relative w-32 h-32 flex-shrink-0">
              <Image
                src={item.imageUrl || '/placeholder.svg'}
                alt={item.name || 'Top wardrobe item'}
                fill
                className="object-cover rounded-lg border border-border shadow-sm"
                priority={index === 0} // Add priority for the first image (LCP)
                onError={(e) => {
                  // Fallback to placeholder if image fails to load
                  const target = e.target as HTMLImageElement;
                  target.src = '/placeholder.svg';
                  target.onerror = null; // Prevent infinite loop
                }}
                unoptimized={true}
              />
            </div>
            
            {/* Content Section */}
            <div className="flex-1 min-w-0">
              <div className="font-semibold text-foreground text-base line-clamp-2 mb-2">
                {item.name}
              </div>
              <div className="text-sm text-muted-foreground capitalize mb-3">{item.type}</div>
              
              {/* Favorite Score */}
              <div className="flex items-center gap-2 mb-3">
                <Star className="w-4 h-4 text-yellow-500 fill-current" />
                <span className="text-sm font-medium text-foreground">
                  {Math.round(item.favorite_score * 100)}% Favorite
                </span>
              </div>

              {/* Usage Stats */}
              <div className="grid grid-cols-2 gap-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  <span>{Math.round(item.usage_count)} uses</span>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-yellow-500" />
                  <span>{Math.round(item.feedback_score * 5)}/5 rating</span>
                </div>
                {item.style_match_score > 0 && (
                  <div className="flex items-center gap-1 col-span-2">
                    <Heart className="w-3 h-3 text-red-500" />
                    <span>{Math.round(item.style_match_score * 100)}% style match</span>
                  </div>
                )}
                {item.base_item_score > 0 && (
                  <div className="flex items-center gap-1 col-span-2">
                    <MousePointer className="w-3 h-3" />
                    <span>Base item favorite</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <section className="bg-card rounded-lg border border-border p-6">
        <h2 className="text-xl font-bold mb-4 text-foreground">📊 Wardrobe Insights</h2>
        <div className="text-muted-foreground">Loading your top items...</div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="bg-card rounded-lg border border-border p-6">
        <h2 className="text-xl font-bold mb-4 text-foreground">📊 Wardrobe Insights</h2>
        <div className="text-destructive">{error}</div>
      </section>
    );
  }

  const topItemsByCategory = getTopItemsByCategory();

  return (
    <section className="bg-card rounded-lg border border-border p-6">
      <h2 className="text-xl font-bold mb-4 text-foreground">📊 Wardrobe Insights</h2>
      
      {topItemsByCategory.length === 0 ? (
        <div className="text-center py-8">
          <Heart className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
          <p className="text-muted-foreground mb-2">No top items yet</p>
          <p className="text-sm text-muted-foreground">
            Your top items will appear here based on:
          </p>
          <div className="mt-3 space-y-1 text-xs text-muted-foreground">
            <div>• How often items appear in outfits</div>
            <div>• Your feedback ratings</div>
            <div>• How often you view/edit items</div>
            <div>• Style preference matches</div>
            <div>• Base item usage</div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              💡 <strong>Tip:</strong> Add items to your wardrobe and use them in outfits to start seeing your top items!
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {topItemsByCategory.map((categoryTopItem, index) => 
            renderTopItemCard(categoryTopItem, index)
          )}
        </div>
      )}
    </section>
  );
} 