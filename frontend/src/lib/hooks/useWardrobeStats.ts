import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { useWardrobe } from '@/hooks/useWardrobe';

interface WardrobeStats {
  totalItems: number;
  favoritesCount: number;
  styleGoalsCompleted: number;
  totalStyleGoals: number;
  outfitsThisWeek: number;
  loading: boolean;
  error: string | null;
}

export function useWardrobeStats() {
  const { user } = useFirebase();
  const { wardrobe, loading: wardrobeLoading } = useWardrobe();
  const [stats, setStats] = useState<WardrobeStats>({
    totalItems: 0,
    favoritesCount: 0,
    styleGoalsCompleted: 0,
    totalStyleGoals: 5, // Default to 5 goals
    outfitsThisWeek: 0,
    loading: true,
    error: null
  });

  useEffect(() => {
    const fetchStats = async () => {
      if (!user?.uid) {
        setStats(prev => ({ ...prev, loading: false }));
        return;
      }

      try {
        setStats(prev => ({ ...prev, loading: true, error: null }));

        // Get total items from wardrobe
        const totalItems = wardrobe.length;
        console.log('📊 Wardrobe Stats Debug - Total items:', totalItems);

        // Simple favorites count based on the favorite property
        const favoritesCount = wardrobe.filter(item => item.favorite === true).length;
        
        console.log('📊 Wardrobe Stats Debug - Favorites count:', favoritesCount);
        console.log('📊 Wardrobe Stats Debug - Sample wardrobe items:', wardrobe.slice(0, 3).map(item => ({
          id: item.id,
          name: item.name,
          favorite: item.favorite,
          tags: item.tags,
          style: item.style,
          color: item.color
        })));
        
        // Debug: Check all properties of first item to see what's available
        if (wardrobe.length > 0) {
          const firstItem = wardrobe[0];
          console.log('📊 Wardrobe Stats Debug - First item properties:', Object.keys(firstItem));
          console.log('📊 Wardrobe Stats Debug - First item full data:', firstItem);
          
          // Check if favorite property exists and its value
          console.log('📊 Wardrobe Stats Debug - First item favorite property:', {
            hasFavorite: 'favorite' in firstItem,
            favoriteValue: (firstItem as any).favorite,
            favoriteType: typeof (firstItem as any).favorite
          });
        }

        // Use the actual favorites count from the wardrobe
        const finalFavoritesCount = favoritesCount;

        // Fetch analytics data for style goals and outfits
        const [favoritesResponse, feedbackResponse] = await Promise.allSettled([
          fetch('/api/item-analytics/favorites', {
            headers: {
              'Authorization': `Bearer ${await user.getIdToken()}`
            }
          }),
          fetch('/api/feedback/user/summary', {
            headers: {
              'Authorization': `Bearer ${await user.getIdToken()}`
            }
          })
        ]);

        let styleGoalsCompleted = 0;
        let totalStyleGoals = 5; // Default to 5 goals
        let outfitsThisWeek = 0;

        // Calculate outfits this week based on wardrobe activity (immediate calculation)
        if (totalItems > 0) {
          // Calculate potential outfit combinations
          const topTypes = ['shirt', 'pants', 'dress', 'jacket', 'sweater', 't-shirt', 'blouse', 'tank_top', 'crop_top', 'polo', 'hoodie', 'cardigan'];
          const bottomTypes = ['pants', 'shorts', 'skirt', 'jeans', 'chinos', 'slacks', 'joggers', 'sweatpants'];
          const topCount = wardrobe.filter(item => topTypes.includes(item.type)).length;
          const bottomCount = wardrobe.filter(item => bottomTypes.includes(item.type)).length;
          
          // Estimate outfits based on actual combinations possible
          const basicOutfits = Math.min(topCount, bottomCount) * 2; // Each top can pair with multiple bottoms
          const dressOutfits = wardrobe.filter(item => item.type === 'dress').length;
          const accessoryOutfits = Math.floor(wardrobe.filter(item => item.type === 'accessory').length / 2);
          
          outfitsThisWeek = Math.min(
            basicOutfits + dressOutfits + accessoryOutfits,
            30 // Cap at 30 outfits for a more realistic number
          );
          
          console.log('📊 Wardrobe Stats Debug - Immediate outfits calculation:', {
            totalItems,
            topCount,
            bottomCount,
            dressCount: wardrobe.filter(item => item.type === 'dress').length,
            accessoryCount: wardrobe.filter(item => item.type === 'accessory').length,
            basicOutfits,
            dressOutfits,
            accessoryOutfits,
            estimatedOutfits: outfitsThisWeek
          });
        }

        // Process favorites analytics
        if (favoritesResponse.status === 'fulfilled' && favoritesResponse.value.ok) {
          const favoritesData = await favoritesResponse.value.json();
          console.log('📊 Wardrobe Stats Debug - Favorites API response:', favoritesData);
          
          if (favoritesData.success && favoritesData.data) {
            // Use the actual favorites count from the API
            const apiFavoritesCount = Array.isArray(favoritesData.data) ? favoritesData.data.length : 0;
            console.log('📊 Wardrobe Stats Debug - API favorites count:', apiFavoritesCount);
            
            // Use the higher count between wardrobe favorites and API favorites
            styleGoalsCompleted = Math.min(finalFavoritesCount, apiFavoritesCount);
          }
        } else {
          console.warn('📊 Wardrobe Stats Debug - Favorites API failed:', favoritesResponse.status);
        }

        // Process feedback summary for outfits this week
        if (feedbackResponse.status === 'fulfilled' && feedbackResponse.value.ok) {
          const feedbackData = await feedbackResponse.value.json();
          console.log('📊 Wardrobe Stats Debug - Feedback API response:', feedbackData);
          
          if (feedbackData.success && feedbackData.data) {
            const feedbackSummary = feedbackData.data;
            
            // Count outfits from this week using recent_feedback
            const recentFeedback = feedbackSummary.recent_feedback || [];
            const oneWeekAgo = new Date();
            oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
            
            outfitsThisWeek = recentFeedback.filter((feedback: any) => {
              const timestamp = feedback.timestamp;
              if (!timestamp) return false;
              
              // Handle different timestamp formats
              let feedbackDate: Date;
              if (typeof timestamp === 'number') {
                feedbackDate = new Date(timestamp);
              } else if (typeof timestamp === 'string') {
                feedbackDate = new Date(timestamp);
              } else {
                return false;
              }
              
              return feedbackDate > oneWeekAgo;
            }).length;
            
            console.log('📊 Wardrobe Stats Debug - Outfits this week:', outfitsThisWeek);
            
            // Calculate style goals based on feedback data
            const totalFeedback = feedbackSummary.total_feedback || 0;
            const likes = feedbackSummary.likes || 0;
            const averageRating = feedbackSummary.average_rating || 0;
            
            console.log('📊 Wardrobe Stats Debug - Feedback metrics:', {
              totalFeedback,
              likes,
              averageRating
            });
            
            // Style goals completed based on positive feedback
            if (totalFeedback > 0) {
              styleGoalsCompleted = Math.min(
                Math.floor(likes / 2) + Math.floor(averageRating), // 1 goal per 2 likes + 1 per average rating point
                5 // Cap at 5 goals
              );
            }
          }
        } else {
          console.warn('📊 Wardrobe Stats Debug - Feedback API failed:', feedbackResponse.status);
        }

        // If no feedback data, create basic style goals based on wardrobe
        if (styleGoalsCompleted === 0 && totalItems > 0) {
          // Create basic goals based on wardrobe diversity
          const uniqueStyles = new Set();
          const uniqueColors = new Set();
          
          wardrobe.forEach(item => {
            if (item.style && Array.isArray(item.style)) {
              item.style.forEach(style => uniqueStyles.add(style.toLowerCase()));
            }
            if (item.color) {
              uniqueColors.add(item.color.toLowerCase());
            }
          });
          
          styleGoalsCompleted = Math.min(
            uniqueStyles.size + Math.floor(uniqueColors.size / 3),
            5
          );
          
          console.log('📊 Wardrobe Stats Debug - Basic style goals calculated:', {
            uniqueStyles: uniqueStyles.size,
            uniqueColors: uniqueColors.size,
            styleGoalsCompleted
          });
        }

        const finalStats = {
          totalItems,
          favoritesCount: finalFavoritesCount,
          styleGoalsCompleted,
          totalStyleGoals,
          outfitsThisWeek,
          loading: false,
          error: null
        };

        console.log('📊 Wardrobe Stats Debug - Final stats:', finalStats);
        setStats(finalStats);

      } catch (error) {
        console.error('Error fetching wardrobe stats:', error);
        setStats(prev => ({
          ...prev,
          loading: false,
          error: error instanceof Error ? error.message : 'Failed to fetch stats'
        }));
      }
    };

    // Only fetch when wardrobe is loaded
    if (!wardrobeLoading) {
      fetchStats();
    }
  }, [user?.uid, wardrobe, wardrobeLoading]);

  return stats;
} 