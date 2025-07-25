'use client';

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useWardrobe } from '@/hooks/useWardrobe';
import { useUserProfile } from '@/hooks/useUserProfile';
import { WardrobeItem, Season } from '@/types/wardrobe';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Star, 
  Calendar, 
  Palette, 
  Target, 
  TrendingUp, 
  CheckCircle, 
  AlertCircle,
  ShoppingCart,
  Plus,
  Sparkles,
  Zap,
  Lightbulb,
  ThumbsUp,
  ThumbsDown,
  Heart
} from 'lucide-react';
import { authenticatedFetch } from '@/lib/utils/auth';
import { useAuth } from '@/hooks/useAuth';

interface StyleGoal {
  name: string;
  target: number;
  current: number;
  description: string;
  category: 'collection' | 'balance' | 'variety' | 'expansion' | 'feedback';
  insights?: string;
  recommendations?: string;
  isExpansion?: boolean;
  feedbackData?: {
    averageRating: number;
    totalFeedback: number;
    likes: number;
    dislikes: number;
    topRatedStyles: string[];
    improvementAreas: string[];
  };
}

interface GoalCategories {
  collection: StyleGoal[];
  balance: StyleGoal[];
  variety: StyleGoal[];
  expansion: StyleGoal[];
  feedback: StyleGoal[];
}

export default function StyleGoalsProgress() {
  const { wardrobe } = useWardrobe();
  const { profile } = useUserProfile();
  const { user, loading } = useAuth();
  const [loadingState, setLoadingState] = useState(false);
  const [feedbackData, setFeedbackData] = useState<any>(null);
  const goalsCache = useRef<{ wardrobeHash: string; goals: StyleGoal[] }>({ wardrobeHash: '', goals: [] });

  // Fetch feedback data
  useEffect(() => {
    const fetchFeedbackData = async () => {
      // Don't make API calls if user is not authenticated or still loading
      if (loading || !user) {
        return;
      }

      try {
        const response = await authenticatedFetch('/api/feedback/user/summary');
        if (response.ok) {
          const data = await response.json();
          setFeedbackData(data);
        } else if (response.status === 401) {
          console.warn('User not authenticated for feedback data');
          // Don't set error, just continue without feedback data
        }
      } catch (error) {
        console.warn('Failed to fetch feedback data:', error);
        // Don't set error, just continue without feedback data
      }
    };

    fetchFeedbackData();
  }, [user, loading]);

  // Memoized calculation functions
  const getStyleTarget = useCallback((totalItems: number, styleCount: number) => {
    const baseTarget = Math.max(5, Math.floor(totalItems * 0.15));
    return Math.min(baseTarget, 15); // Cap at 15 items per style
  }, []);

  // Calculate seasonal balance in a user-friendly way
  const calculateSeasonalBalance = useCallback((itemsPerSeason: number[]) => {
    if (itemsPerSeason.length === 0) return { isBalanced: true, underrepresented: [], overrepresented: [], score: 0 };
    
    const seasons = ['Spring', 'Summer', 'Fall', 'Winter'];
    const totalItems = itemsPerSeason.reduce((sum, count) => sum + count, 0);
    const expectedPerSeason = totalItems / 4; // Ideal equal distribution
    
    const underrepresented: string[] = [];
    const overrepresented: string[] = [];
    
    itemsPerSeason.forEach((count, index) => {
      const season = seasons[index];
      const percentage = totalItems > 0 ? (count / totalItems) * 100 : 0;
      
      if (count < expectedPerSeason * 0.7) { // Less than 70% of expected
        underrepresented.push(`${season} (${count} items, ${percentage.toFixed(0)}%)`);
      } else if (count > expectedPerSeason * 1.3) { // More than 130% of expected
        overrepresented.push(`${season} (${count} items, ${percentage.toFixed(0)}%)`);
      }
    });
    
    const isBalanced = underrepresented.length === 0 && overrepresented.length === 0;
    const score = isBalanced ? 100 : Math.max(0, 100 - (underrepresented.length + overrepresented.length) * 25);
    
    return { isBalanced, underrepresented, overrepresented, score };
  }, []);

  const getSeasonalInsights = useCallback((underrepresented: string[], overrepresented: string[]) => {
    if (underrepresented.length === 0 && overrepresented.length === 0) {
      return "Perfect seasonal balance! Your wardrobe is well-distributed across all seasons.";
    }
    
    let insight = "";
    if (underrepresented.length > 0) {
      insight += `Consider adding items for: ${underrepresented.join(', ')}. `;
    }
    if (overrepresented.length > 0) {
      insight += `You have strong collections for: ${overrepresented.join(', ')}.`;
    }
    return insight;
  }, []);

  const getSeasonalRecommendations = useCallback((underrepresented: string[]) => {
    if (underrepresented.length === 0) return undefined;
    
    const seasonItems: Record<string, string[]> = {
      'Spring': ['light jackets', 'pastel colors', 'floral prints', 'cardigans'],
      'Summer': ['breathable fabrics', 'shorts', 'sandals', 'light dresses'],
      'Fall': ['sweaters', 'jeans', 'boots', 'warm layers'],
      'Winter': ['coats', 'scarves', 'warm accessories', 'thermal items']
    };
    
    const recommendations = underrepresented.map(season => {
      const seasonName = season.split(' ')[0];
      const items = seasonItems[seasonName] || ['seasonal items'];
      return `${seasonName}: ${items.slice(0, 2).join(', ')}`;
    });
    
    return `Focus on: ${recommendations.join('; ')}`;
  }, []);

  const getGoalIcon = useCallback((goalName: string) => {
    switch (goalName) {
      case 'Seasonal Balance': return <Calendar className="w-4 h-4" />;
      case 'Color Variety': return <Palette className="w-4 h-4" />;
      case 'Style Expansion': return <Sparkles className="w-4 h-4" />;
      case 'Feedback Quality': return <Star className="w-4 h-4" />;
      case 'Style Satisfaction': return <Heart className="w-4 h-4" />;
      default: return <Star className="w-4 h-4" />;
    }
  }, []);

  const getProgressColor = useCallback((progress: number) => {
    if (progress >= 100) return 'bg-green-500';
    if (progress >= 70) return 'bg-yellow-500';
    if (progress >= 40) return 'bg-blue-500';
    return 'bg-red-500';
  }, []);

  const getInsights = useCallback((goal: StyleGoal) => {
    if (goal.isExpansion) {
      return "You've mastered this style! Ready to explore new directions?";
    } else if (goal.current < goal.target * 0.3) {
      return "Consider adding more items in this category";
    } else if (goal.current >= goal.target) {
      return "Great job! Consider exploring new styles";
    }
    return "You're making good progress!";
  }, []);

  const getRecommendations = useCallback((goal: StyleGoal) => {
    if (goal.isExpansion) {
      return `Explore ${goal.name.toLowerCase()} to expand your style repertoire`;
    } else if (goal.current < goal.target) {
      const needed = goal.target - goal.current;
      return `Add ${needed} more ${goal.name.toLowerCase().replace(' collection', '')} items to reach your goal`;
    }
    return undefined;
  }, []);

  // Analyze wardrobe style with feedback integration
  const analyzeWardrobeStyle = useCallback(() => {
    if (!wardrobe || wardrobe.length === 0) {
      return { dominantStyles: [], styleCounts: {} };
    }

    const styleCounts: Record<string, number> = {};
    const styleRatings: Record<string, number[]> = {};

    wardrobe.forEach(item => {
      if (item.style && Array.isArray(item.style)) {
        item.style.forEach(style => {
          const styleKey = style.toLowerCase();
          styleCounts[styleKey] = (styleCounts[styleKey] || 0) + 1;
          
          // If we have feedback data, track ratings by style
          if (feedbackData && item.id) {
            const itemFeedback = feedbackData.itemFeedback?.[item.id];
            if (itemFeedback && itemFeedback.rating) {
              if (!styleRatings[styleKey]) {
                styleRatings[styleKey] = [];
              }
              styleRatings[styleKey].push(itemFeedback.rating);
            }
          }
        });
      }
    });

    // Sort by count and get top styles
    const sortedStyles = Object.entries(styleCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 5)
      .map(([style]) => style);

    return { 
      dominantStyles: sortedStyles, 
      styleCounts,
      styleRatings 
    };
  }, [wardrobe, feedbackData]);

  // Generate feedback-based goals
  const generateFeedbackGoals = useCallback(() => {
    const feedbackGoals: StyleGoal[] = [];
    
    if (!feedbackData) return feedbackGoals;

    // Goal 1: Overall Feedback Quality
    const avgRating = feedbackData.averageRating || 0;
    const totalFeedback = feedbackData.totalFeedback || 0;
    
    if (totalFeedback > 0) {
      feedbackGoals.push({
        name: 'Feedback Quality',
        target: 5,
        current: avgRating,
        description: 'Maintain high ratings for your outfit recommendations',
        category: 'feedback',
        insights: avgRating >= 4 ? 
          `Excellent! Your average rating is ${avgRating.toFixed(1)}/5` :
          `Your average rating is ${avgRating.toFixed(1)}/5. Consider what makes your favorite outfits special.`,
        recommendations: avgRating < 4 ? 
          'Focus on styles and combinations that consistently receive high ratings' : undefined,
        feedbackData: {
          averageRating: avgRating,
          totalFeedback,
          likes: feedbackData.likes || 0,
          dislikes: feedbackData.dislikes || 0,
          topRatedStyles: feedbackData.topRatedStyles || [],
          improvementAreas: feedbackData.improvementAreas || []
        }
      });
    }

    // Goal 2: Style Satisfaction
    const { styleRatings } = analyzeWardrobeStyle();
    const styleSatisfaction = Object.entries(styleRatings)
      .filter(([, ratings]) => ratings.length >= 2)
      .map(([style, ratings]) => ({
        style,
        avgRating: ratings.reduce((sum, r) => sum + r, 0) / ratings.length
      }))
      .sort((a, b) => b.avgRating - a.avgRating);

    if (styleSatisfaction.length > 0) {
      const topStyle = styleSatisfaction[0];
      const satisfactionScore = Math.min(100, topStyle.avgRating * 20); // Convert 1-5 to 0-100
      
      feedbackGoals.push({
        name: 'Style Satisfaction',
        target: 100,
        current: satisfactionScore,
        description: `Your highest-rated style: ${topStyle.style}`,
        category: 'feedback',
        insights: `Your ${topStyle.style} items average ${topStyle.avgRating.toFixed(1)}/5 stars`,
        recommendations: satisfactionScore < 80 ? 
          'Explore more items in your highest-rated styles' : undefined,
        feedbackData: {
          averageRating: topStyle.avgRating,
          totalFeedback: styleRatings[topStyle.style].length,
          likes: feedbackData.likes || 0,
          dislikes: feedbackData.dislikes || 0,
          topRatedStyles: [topStyle.style],
          improvementAreas: styleSatisfaction
            .filter(s => s.avgRating < 3)
            .map(s => s.style)
        }
      });
    }

    return feedbackGoals;
  }, [feedbackData, analyzeWardrobeStyle]);

  // Generate expansion suggestions based on current style
  const generateExpansionGoals = useCallback((dominantStyles: string[], styleCounts: Record<string, number>) => {
    const expansionGoals: StyleGoal[] = [];
    
    // Style expansion mappings
    const styleExpansions: Record<string, string[]> = {
      'casual': ['smart casual', 'business casual', 'streetwear', 'athleisure'],
      'business': ['business casual', 'smart casual', 'preppy', 'sophisticated'],
      'formal': ['semi-formal', 'business', 'elegant', 'sophisticated'],
      'classic': ['preppy', 'sophisticated', 'elegant', 'business'],
      'streetwear': ['urban', 'casual', 'athleisure', 'contemporary'],
      'minimalist': ['androgynous', 'contemporary', 'sophisticated', 'clean'],
      'bohemian': ['coastal chic', 'natural', 'romantic', 'artistic'],
      'preppy': ['business', 'sophisticated', 'elegant', 'classic']
    };
    
    dominantStyles.forEach(style => {
      const currentCount = styleCounts[style] || 0;
      const target = getStyleTarget(wardrobe?.length || 0, 1);
      
      // If they have a strong collection in this style, suggest expansion
      if (currentCount >= target * 0.8) {
        const expansionOptions = styleExpansions[style] || [];
        const suggestedExpansion = expansionOptions[0]; // Take the first suggestion
        
        if (suggestedExpansion) {
          // Calculate current count for the suggested expansion style
          const expansionCurrentCount = wardrobe?.filter(item => {
            if (!item.style || !Array.isArray(item.style)) return false;
            return item.style.some(s => 
              s.toLowerCase().includes(suggestedExpansion.toLowerCase()) ||
              suggestedExpansion.toLowerCase().includes(s.toLowerCase())
            );
          }).length || 0;
          
          expansionGoals.push({
            name: `${suggestedExpansion} Expansion`,
            target: 3, // Start with a small goal
            current: expansionCurrentCount,
            description: `Explore ${suggestedExpansion} style to complement your strong ${style} collection`,
            category: 'expansion',
            insights: `You have ${currentCount} ${style} items - ready to explore ${suggestedExpansion}?`,
            recommendations: expansionCurrentCount < 3 ? `Try adding ${3 - expansionCurrentCount} ${suggestedExpansion} pieces to expand your style` : undefined,
            isExpansion: true
          });
        }
      }
    });
    
    return expansionGoals;
  }, [wardrobe, getStyleTarget]);

  const safeCalculateGoals = useCallback(() => {
    if (!wardrobe || wardrobe.length === 0) {
      return [];
    }

    const wardrobeHash = JSON.stringify(wardrobe.map(item => item.id).sort());
    if (goalsCache.current.wardrobeHash === wardrobeHash) {
      return goalsCache.current.goals;
    }

    const newGoals: StyleGoal[] = [];
    const totalItems = wardrobe.length;
    const userStylePreferences = profile?.stylePreferences || [];

    console.log('🎯 Style Goals Debug:', {
      totalItems,
      userStylePreferences,
      feedbackData: !!feedbackData
    });

    // Analyze current wardrobe style
    const { dominantStyles, styleCounts } = analyzeWardrobeStyle();
    
    console.log('🔍 Style Goals Debug:', {
      userStylePreferences,
      dominantStyles,
      styleCounts,
      totalItems
    });

    // Goal 1: Style collection goals based on user preferences
    if (userStylePreferences.length > 0) {
      userStylePreferences.forEach(style => {
        const itemsInStyle = wardrobe.filter(item => {
          if (!item.style || !Array.isArray(item.style)) return false;
          
          // Enhanced style matching
          const exactMatch = item.style.some(s => s.toLowerCase() === style.toLowerCase());
          const partialMatch = item.style.some(s => 
            s.toLowerCase().includes(style.toLowerCase()) || 
            style.toLowerCase().includes(s.toLowerCase())
          );
          
          return exactMatch || partialMatch;
        }).length;
        
        const target = getStyleTarget(totalItems, userStylePreferences.length);
        
        const goal = {
          name: `${style} Collection`,
          target,
          current: itemsInStyle,
          description: `Build a collection of ${style} pieces`,
          category: 'collection' as const,
          insights: getInsights({ name: style, target, current: itemsInStyle, description: '', category: 'collection' }),
          recommendations: getRecommendations({ name: style, target, current: itemsInStyle, description: '', category: 'collection' })
        };
        
        console.log(`📋 Created collection goal:`, goal);
        newGoals.push(goal);
      });
    } else {
      // If no style preferences set, create goals based on dominant styles in wardrobe
      if (dominantStyles.length > 0) {
        dominantStyles.slice(0, 3).forEach(style => {
          const currentCount = styleCounts[style] || 0;
          const target = getStyleTarget(totalItems, 3);
          
          const goal = {
            name: `${style.charAt(0).toUpperCase() + style.slice(1)} Collection`,
            target,
            current: currentCount,
            description: `Develop your ${style} style collection`,
            category: 'collection' as const,
            insights: `You naturally gravitate toward ${style} styles`,
            recommendations: currentCount < target ? `Add ${target - currentCount} more ${style} pieces` : undefined
          };
          
          console.log(`📋 Created dominant style goal:`, goal);
          newGoals.push(goal);
        });
      } else {
        // Fallback: create generic style goals if no dominant styles found
        console.log('⚠️ No dominant styles found, creating fallback goals');
        const fallbackStyles = ['Casual', 'Business', 'Formal'];
        fallbackStyles.forEach(style => {
          const target = getStyleTarget(totalItems, 3);
          const goal = {
            name: `${style} Collection`,
            target,
            current: 0, // Start at 0 since we don't have style data
            description: `Build a collection of ${style} pieces`,
            category: 'collection' as const,
            insights: `Start building your ${style} style collection`,
            recommendations: `Add ${target} ${style} pieces to get started`
          };
          
          console.log(`📋 Created fallback style goal:`, goal);
          newGoals.push(goal);
        });
      }
    }

    // Goal 2: Seasonal balance
    const seasons: Season[] = ['spring', 'summer', 'fall', 'winter'];
    const itemsPerSeason = seasons.map(season =>
      wardrobe.filter(item => item.season?.includes(season as Season)).length
    );
    
    console.log('🌤️ Seasonal analysis:', {
      seasons,
      itemsPerSeason,
      totalItems,
      sampleSeasonData: wardrobe.slice(0, 3).map(item => ({
        id: item.id,
        name: item.name,
        season: item.season,
        seasonType: typeof item.season,
        isArray: Array.isArray(item.season)
      }))
    });
    
    const { isBalanced, underrepresented, overrepresented, score } = calculateSeasonalBalance(itemsPerSeason);
    const balanceTarget = 100; // Target for balanced seasonal distribution (score is 0-100)
    
    const seasonalGoal = {
      name: 'Seasonal Balance',
      target: balanceTarget,
      current: score,
      description: 'Maintain balanced wardrobe across all seasons',
      category: 'balance' as const,
      insights: getSeasonalInsights(underrepresented, overrepresented),
      recommendations: getSeasonalRecommendations(underrepresented)
    };
    
    console.log(`📋 Created seasonal balance goal:`, {
      ...seasonalGoal,
      itemsPerSeason,
      isBalanced,
      underrepresented,
      overrepresented
    });
    newGoals.push(seasonalGoal);

    // Goal 3: Color variety
    const colorCounts: Record<string, number> = {};
    wardrobe.forEach(item => {
      if (item.color) {
        const color = item.color.toLowerCase();
        colorCounts[color] = (colorCounts[color] || 0) + 1;
      }
    });
    
    console.log('🎨 Color analysis:', {
      colorCounts,
      uniqueColors: Object.keys(colorCounts).length,
      sampleColorData: wardrobe.slice(0, 3).map(item => ({
        id: item.id,
        name: item.name,
        color: item.color,
        colorType: typeof item.color
      }))
    });
    
    const uniqueColors = Object.keys(colorCounts).length;
    const colorVarietyTarget = Math.min(8, Math.max(5, Math.floor(totalItems * 0.3)));
    
    const colorGoal = {
      name: 'Color Variety',
      target: colorVarietyTarget,
      current: uniqueColors,
      description: 'Build a diverse color palette',
      category: 'variety' as const,
      insights: uniqueColors >= colorVarietyTarget ? 'Excellent color variety!' : 'Consider exploring new colors',
      recommendations: uniqueColors < colorVarietyTarget ? `Add ${colorVarietyTarget - uniqueColors} new colors to your palette` : undefined
    };
    
    console.log(`📋 Created color variety goal:`, {
      ...colorGoal,
      colorCounts,
      totalItems
    });
    newGoals.push(colorGoal);

    // Goal 4: Style expansion (when maxing out current styles)
    const expansionGoals = generateExpansionGoals(dominantStyles, styleCounts);
    console.log(`📋 Created ${expansionGoals.length} expansion goals:`, expansionGoals);
    newGoals.push(...expansionGoals);

    // Goal 5: Feedback-based goals
    const feedbackGoals = generateFeedbackGoals();
    console.log(`📋 Created ${feedbackGoals.length} feedback goals:`, feedbackGoals);
    newGoals.push(...feedbackGoals);

    console.log(`🎯 Final goals summary:`, {
      totalGoals: newGoals.length,
      byCategory: {
        collection: newGoals.filter(g => g.category === 'collection').length,
        balance: newGoals.filter(g => g.category === 'balance').length,
        variety: newGoals.filter(g => g.category === 'variety').length,
        expansion: newGoals.filter(g => g.category === 'expansion').length,
        feedback: newGoals.filter(g => g.category === 'feedback').length
      },
      goals: newGoals.map(g => ({
        name: g.name,
        current: g.current,
        target: g.target,
        category: g.category
      }))
    });

    // Cache the results
    goalsCache.current = { wardrobeHash, goals: newGoals };
    return newGoals;
  }, [wardrobe, profile, feedbackData, analyzeWardrobeStyle, generateExpansionGoals, generateFeedbackGoals, getStyleTarget, calculateSeasonalBalance, getSeasonalInsights, getSeasonalRecommendations, getInsights, getRecommendations]);

  const goals = useMemo(() => safeCalculateGoals(), [safeCalculateGoals]);

  const goalCategories = useMemo(() => {
    const categories: GoalCategories = {
      collection: [],
      balance: [],
      variety: [],
      expansion: [],
      feedback: []
    };
    
    goals.forEach(goal => {
      if (categories[goal.category]) {
        categories[goal.category].push(goal);
      }
    });
    
    return categories;
  }, [goals]);

  // Calculate overall progress
  const overallProgress = useMemo(() => {
    if (goals.length === 0) return 0;
    
    console.log('🎯 Overall Progress Debug:', {
      totalGoals: goals.length,
      goals: goals.map(g => ({
        name: g.name,
        current: g.current,
        target: g.target,
        category: g.category,
        progress: g.category === 'balance' ? 
          g.current : // For balance goals, current is already a percentage
          Math.min(100, (g.current / g.target) * 100)
      }))
    });
    
    const totalProgress = goals.reduce((sum, goal) => {
      if (goal.category === 'balance') {
        // For balance goals, current is already a percentage (0-100)
        const progress = goal.current;
        console.log(`Balance goal "${goal.name}": ${goal.current}/${goal.target} = ${progress}%`);
        return sum + progress;
      } else {
        const progress = Math.min(100, (goal.current / goal.target) * 100);
        console.log(`Regular goal "${goal.name}": ${goal.current}/${goal.target} = ${progress}%`);
        return sum + progress;
      }
    }, 0);
    
    const average = Math.round(totalProgress / goals.length);
    console.log(`📊 Overall Progress: ${totalProgress} / ${goals.length} = ${average}%`);
    return average;
  }, [goals]);

  // Early return for loading state
  if (loading) {
    return (
      <Card className="border border-border bg-card">
        <CardHeader className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6" />
            <div>
              <CardTitle className="text-xl font-bold">Style Goals</CardTitle>
              <p className="text-purple-100 text-sm">Analyzing your style...</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Early return for no wardrobe data
  if (!wardrobe?.length) {
    return (
      <Card className="border border-border bg-card">
        <CardHeader className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6" />
            <div>
              <CardTitle className="text-xl font-bold">Style Goals</CardTitle>
              <p className="text-purple-100 text-sm">Start building your wardrobe to see personalized goals</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6 text-center space-y-4">
          <div className="text-muted-foreground">
            <Sparkles className="w-12 h-12 mx-auto mb-3 text-purple-200" />
            <p className="text-lg font-medium">No wardrobe items yet</p>
            <p className="text-sm">Add some clothing items to get personalized style goals and recommendations</p>
          </div>
          <Button onClick={() => window.location.href = '/wardrobe/add'} className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Add Your First Item
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border border-border bg-card">
      <CardHeader className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Target className="w-6 h-6" />
            <div>
              <CardTitle className="text-xl font-bold">Style Goals</CardTitle>
              <p className="text-purple-100 text-sm">
                {profile?.stylePreferences?.length ? 'Personalized goals based on your style preferences' : 'Goals based on your current wardrobe'}
                {feedbackData && ' • Enhanced with feedback insights'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{overallProgress}%</div>
            <div className="text-purple-100 text-sm">Overall Progress</div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6 space-y-6">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="font-medium text-foreground">Overall Progress</span>
            <span className="text-foreground">{overallProgress}%</span>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </div>

        {/* Feedback Goals */}
        {goalCategories.feedback.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Star className="w-4 h-4 text-yellow-500" />
              Feedback Insights
            </h3>
            <div className="space-y-4">
              {goalCategories.feedback.map((goal) => {
                const progress = goal.category === 'feedback' ? 
                  (goal.current / goal.target) * 100 : 
                  Math.min(100, (goal.current / goal.target) * 100);
                const isComplete = goal.current >= goal.target;

                return (
                  <div key={goal.name} className="space-y-3 p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        {getGoalIcon(goal.name)}
                        <h4 className="font-semibold text-foreground">{goal.name}</h4>
                        {isComplete && <CheckCircle className="w-4 h-4 text-green-500" />}
                      </div>
                      <Badge variant={isComplete ? "default" : "secondary"}>
                        {goal.category === 'feedback' ? 
                          `${goal.current.toFixed(1)}/${goal.target}` : 
                          `${goal.current}/${goal.target}`}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium text-foreground">{Math.round(progress)}%</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getProgressColor(progress)}`}
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">{goal.description}</p>
                    
                    {goal.insights && (
                      <div className="flex items-start gap-2 p-2 bg-card rounded border border-border">
                        <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5" />
                        <p className="text-sm text-foreground">{goal.insights}</p>
                      </div>
                    )}

                    {/* Feedback Data Display */}
                    {goal.feedbackData && (
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex items-center gap-1">
                          <ThumbsUp className="w-3 h-3 text-green-500" />
                          <span>{goal.feedbackData.likes} likes</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <ThumbsDown className="w-3 h-3 text-red-500" />
                          <span>{goal.feedbackData.dislikes} dislikes</span>
                        </div>
                        {goal.feedbackData.topRatedStyles.length > 0 && (
                          <div className="col-span-2 text-xs text-muted-foreground">
                            Top rated: {goal.feedbackData.topRatedStyles.join(', ')}
                          </div>
                        )}
                      </div>
                    )}
                    
                    {goal.recommendations && (
                      <div className="flex items-center justify-between p-2 bg-yellow-500/10 rounded border border-yellow-500/20">
                        <div className="flex items-center gap-2">
                          <Lightbulb className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                          <p className="text-sm text-yellow-700 dark:text-yellow-300">{goal.recommendations}</p>
                        </div>
                        <Button size="sm" variant="outline" className="text-xs border-yellow-500/30 text-yellow-700 dark:text-yellow-300">
                          <Plus className="w-3 h-3 mr-1" />
                          Improve
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Style Collection Goals */}
        {goalCategories.collection.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Star className="w-4 h-4 text-purple-500" />
              Style Collections
            </h3>
            <div className="space-y-4">
              {goalCategories.collection.map((goal) => {
                const progress = Math.min(100, (goal.current / goal.target) * 100);
                const isComplete = goal.current >= goal.target;

                return (
                  <div key={goal.name} className="space-y-3 p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        {getGoalIcon(goal.name)}
                        <h4 className="font-semibold text-foreground">{goal.name}</h4>
                        {isComplete && <CheckCircle className="w-4 h-4 text-green-500" />}
                      </div>
                      <Badge variant={isComplete ? "default" : "secondary"}>
                        {goal.current}/{goal.target}
                      </Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Progress</span>
                        <span className="font-medium text-foreground">{Math.round(progress)}%</span>
                      </div>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${getProgressColor(progress)}`}
                          style={{ width: `${progress}%` }}
                          role="progressbar"
                          aria-label={`${goal.name} progress: ${goal.current} of ${goal.target}`}
                          aria-valuenow={goal.current}
                          aria-valuemin={0}
                          aria-valuemax={goal.target}
                        />
                      </div>
                    </div>
                    
                    <p className="text-sm text-muted-foreground">{goal.description}</p>
                    
                    {goal.insights && (
                      <div className="flex items-start gap-2 p-2 bg-card rounded border border-border">
                        <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5" />
                        <p className="text-sm text-foreground">{goal.insights}</p>
                      </div>
                    )}
                    
                    {goal.recommendations && (
                      <div className="flex items-center justify-between p-2 bg-blue-500/10 rounded border border-blue-500/20">
                        <div className="flex items-center gap-2">
                          <ShoppingCart className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                          <p className="text-sm text-blue-700 dark:text-blue-300">{goal.recommendations}</p>
                        </div>
                        <Button size="sm" variant="outline" className="text-xs">
                          <Plus className="w-3 h-3 mr-1" />
                          Add Items
                        </Button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Style Expansion Goals */}
        {goalCategories.expansion.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-yellow-500" />
              Style Expansion
            </h3>
            <p className="text-sm text-muted-foreground">
              Your clothing items will allow you to explore the following areas as well
            </p>
            <div className="space-y-4">
              {goalCategories.expansion.map((goal) => (
                <div key={goal.name} className="space-y-3 p-4 bg-yellow-500/10 rounded-lg border border-yellow-500/20">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />
                      <h4 className="font-semibold text-foreground">{goal.name}</h4>
                      <Badge variant="outline" className="text-yellow-700 dark:text-yellow-300 border-yellow-500/30">
                        New Direction
                      </Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Balance & Variety Goals */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {goalCategories.balance.map((goal) => {
            const progress = goal.current; // Score is already 0-100
            const isComplete = progress >= 80; // Consider balanced if 80% or higher

            return (
              <div key={goal.name} className="space-y-3 p-4 bg-green-500/10 rounded-lg border border-green-500/20">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    {getGoalIcon(goal.name)}
                    <h4 className="font-semibold text-foreground">{goal.name}</h4>
                    {isComplete && <CheckCircle className="w-4 h-4 text-green-500" />}
                  </div>
                  <Badge variant={isComplete ? "default" : "secondary"}>
                    {Math.round(progress)}%
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Balance Score</span>
                    <span className="font-medium text-foreground">{isComplete ? 'Balanced' : 'Needs Work'}</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${isComplete ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground">{goal.description}</p>
                
                {goal.insights && (
                  <div className="flex items-start gap-2 p-2 bg-card rounded border border-border">
                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5" />
                    <p className="text-sm text-foreground">{goal.insights}</p>
                  </div>
                )}

                {goal.recommendations && (
                  <div className="flex items-center justify-between p-2 bg-green-500/10 rounded border border-green-500/20">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-green-600 dark:text-green-400" />
                      <p className="text-sm text-green-700 dark:text-green-300">{goal.recommendations}</p>
                    </div>
                    <Button size="sm" variant="outline" className="text-xs border-green-500/30 text-green-700 dark:text-green-300">
                      <Plus className="w-3 h-3 mr-1" />
                      Add Items
                    </Button>
                  </div>
                )}
              </div>
            );
          })}

          {goalCategories.variety.map((goal) => {
            const progress = Math.min(100, (goal.current / goal.target) * 100);
            const isComplete = goal.current >= goal.target;

            return (
              <div key={goal.name} className="space-y-3 p-4 bg-orange-500/10 rounded-lg border border-orange-500/20">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    {getGoalIcon(goal.name)}
                    <h4 className="font-semibold text-foreground">{goal.name}</h4>
                    {isComplete && <CheckCircle className="w-4 h-4 text-green-500" />}
                  </div>
                  <Badge variant={isComplete ? "default" : "secondary"}>
                    {goal.current}/{goal.target}
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium text-foreground">{Math.round(progress)}%</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${getProgressColor(progress)}`}
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                </div>
                
                <p className="text-sm text-muted-foreground">{goal.description}</p>
                
                {goal.insights && (
                  <div className="flex items-start gap-2 p-2 bg-card rounded border border-border">
                    <TrendingUp className="w-4 h-4 text-blue-500 mt-0.5" />
                    <p className="text-sm text-foreground">{goal.insights}</p>
                  </div>
                )}
                
                {goal.recommendations && (
                  <div className="flex items-center justify-between p-2 bg-orange-500/10 rounded border border-orange-500/20">
                    <div className="flex items-center gap-2">
                      <Palette className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                      <p className="text-sm text-orange-700 dark:text-orange-300">{goal.recommendations}</p>
                    </div>
                    <Button size="sm" variant="outline" className="text-xs">
                      <Plus className="w-3 h-3 mr-1" />
                      Explore Colors
                    </Button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
} 