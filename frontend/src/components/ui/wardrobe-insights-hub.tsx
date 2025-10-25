'use client';

import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { shoppingService, ShoppingRecommendationsResponse } from '@/lib/services/shoppingService';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StyleInspirationCard } from '@/components/ui/style-inspiration-card';
import { 
  ShoppingBag, 
  DollarSign, 
  Star,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Clock,
  Tag,
  ChevronDown,
  ChevronRight,
  ShoppingCart,
  MapPin,
  Sparkles,
  Sun,
  Snowflake,
  RefreshCw
} from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";

// Types
interface StyleExpansion {
  name: string;
  direction: string;
  count?: number;
}

interface WardrobeGap {
  id?: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
  suggestedItems: string[];
  currentCount: number;
  recommendedCount: number;
  gapSize: number;
  type?: string;
  severity?: string;
  title?: string;
  data?: {
    current_count?: number;
    required_count?: number;
    season?: string;
  };
}

interface ShoppingRecommendation {
  id: string;
  name: string;
  category: string;
  item_type: string;
  description: string;
  style_tags: string[];
  colors: string[];
  sizes: string[];
  materials: string[];
  estimated_price: number;
  priority: string;
  why_needed: string;
  styling_tips: string;
  care_instructions: string;
  versatility_score: number;
  seasonality: string[];
  formality_level: string;
}

interface StoreRecommendation {
  name: string;
  description: string;
  price_range: string;
}

interface ShoppingStrategy {
  total_items_needed: number;
  high_priority_items: number;
  estimated_total_cost: number;
  budget_range: string;
  shopping_phases: Array<{
    phase: number;
    name: string;
    description: string;
    items: ShoppingRecommendation[];
    estimated_cost: number;
  }>;
  tips: string[];
}

interface TopItem {
  id: string;
  name: string;
  type: string;
  imageUrl: string;
  wearCount: number;
  rating: number;
}

interface WardrobeInsightsHubProps {
  styleExpansions?: StyleExpansion[];
  gaps?: WardrobeGap[];
  shoppingRecommendations?: {
    success: boolean;
    recommendations: ShoppingRecommendation[];
    store_recommendations: StoreRecommendation[];
    shopping_strategy: ShoppingStrategy;
    total_estimated_cost: number;
    budget_range: string;
  };
  onRefresh?: () => void;
  className?: string;
}

export default function WardrobeInsightsHub({
  styleExpansions = [],
  gaps = [],
  shoppingRecommendations: initialShoppingRecommendations,
  onRefresh,
  className = ""
}: WardrobeInsightsHubProps) {
  const { user } = useAuthContext();
  const [selectedBudget, setSelectedBudget] = useState<string>('medium');
  const [expandedGaps, setExpandedGaps] = useState<Set<string>>(new Set());
  const [shoppingRecommendations, setShoppingRecommendations] = useState<ShoppingRecommendationsResponse | null>(initialShoppingRecommendations || null);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Fetch shopping recommendations when gaps are available
  useEffect(() => {
    const fetchShoppingRecommendations = async () => {
      if (gaps && gaps.length > 0 && user && !shoppingRecommendations) {
        setLoadingRecommendations(true);
        try {
          const recommendations = await shoppingService.getShoppingRecommendations(user, selectedBudget);
          setShoppingRecommendations(recommendations);
        } catch (error) {
          console.error('Failed to fetch shopping recommendations:', error);
        } finally {
          setLoadingRecommendations(false);
        }
      }
    };

    fetchShoppingRecommendations();
  }, [gaps, user, selectedBudget, shoppingRecommendations]);

  // Refetch recommendations when budget changes
  useEffect(() => {
    if (gaps && gaps.length > 0 && user) {
      setLoadingRecommendations(true);
      shoppingService.getShoppingRecommendations(user, selectedBudget)
        .then(setShoppingRecommendations)
        .catch(console.error)
        .finally(() => setLoadingRecommendations(false));
    }
  }, [selectedBudget]);

  const toggleGapExpansion = (gapId: string) => {
    const newExpanded = new Set(expandedGaps);
    if (newExpanded.has(gapId)) {
      newExpanded.delete(gapId);
    } else {
      newExpanded.add(gapId);
    }
    setExpandedGaps(newExpanded);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'medium': return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
      case 'low': return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      default: return 'text-gray-600 bg-gray-100 dark:bg-gray-900/20';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high': return <AlertCircle className="h-4 w-4" />;
      case 'medium': return <Clock className="h-4 w-4" />;
      case 'low': return <CheckCircle className="h-4 w-4" />;
      default: return <Tag className="h-4 w-4" />;
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  // Separate seasonal gaps from regular gaps
  const seasonalGaps = gaps.filter(gap => 
    gap.type === 'seasonal' || 
    gap.category?.toLowerCase().includes('summer') || 
    gap.category?.toLowerCase().includes('winter') ||
    gap.category?.toLowerCase().includes('essentials')
  );
  
  const regularGaps = gaps.filter(gap => 
    gap.type !== 'seasonal' && 
    !gap.category?.toLowerCase().includes('summer') && 
    !gap.category?.toLowerCase().includes('winter') &&
    !gap.category?.toLowerCase().includes('essentials')
  );

  // Default store recommendations if none provided
  const defaultStores: StoreRecommendation[] = [
    {
      name: 'Zara',
      description: 'Trendy pieces with good quality',
      price_range: '$20-100'
    },
    {
      name: 'Mango',
      description: 'European style and quality',
      price_range: '$30-120'
    },
    {
      name: 'J.Crew',
      description: 'Classic American style',
      price_range: '$40-150'
    },
    {
      name: 'Madewell',
      description: 'Denim and casual chic',
      price_range: '$30-120'
    }
  ];

  const defaultTips = [
    'Start with high-priority items that will have the most impact',
    'Look for versatile pieces that can be styled multiple ways',
    'Consider buying one quality item over multiple cheap alternatives',
    'Check for sales and seasonal discounts',
    'Try items on in-store when possible for the best fit',
    'Keep receipts for easy returns if needed'
  ];

  const stores = shoppingRecommendations?.store_recommendations || defaultStores;
  const tips = shoppingRecommendations?.shopping_strategy?.tips || defaultTips;

  return (
    <Card className={`border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm ${className}`}>
      <CardHeader className="pb-6">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100 flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-purple-600" />
              Wardrobe Insights Hub
            </CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">
              Explore your style, identify gaps, and get personalized shopping recommendations
            </CardDescription>
          </div>
          {onRefresh && (
            <Button variant="outline" size="sm" onClick={onRefresh}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="style-inspiration" className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="style-inspiration" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Style Inspiration
            </TabsTrigger>
            <TabsTrigger value="gap-analysis" className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Gap Analysis
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Style Inspiration */}
          <TabsContent value="style-inspiration" className="space-y-6">
            {/* Style Inspiration Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Discover New Pieces</h3>
                  <p className="text-sm text-stone-600 dark:text-stone-400">
                    Get personalized recommendations based on your style profile and current weather
                  </p>
                </div>
              </div>
              
              <div className="flex justify-center">
                <StyleInspirationCard 
                  className="w-full max-w-2xl"
                />
              </div>
            </div>
          </TabsContent>

          {/* Tab 2: Wardrobe Gap Analysis */}
          <TabsContent value="gap-analysis" className="space-y-6">
            {/* Seasonal Essentials Section */}
            {seasonalGaps.length > 0 && (
              <div className="space-y-4">
                <div className="flex items-center gap-2 mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Seasonal Essentials</h3>
                  <Button variant="ghost" size="sm" onClick={onRefresh}>
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {seasonalGaps.map((gap, index) => {
                    const gapId = gap.id || `seasonal-${index}`;
                    const isExpanded = expandedGaps.has(gapId);
                    const isSummer = gap.category?.toLowerCase().includes('summer');
                    const currentCount = gap.data?.current_count ?? gap.currentCount ?? 0;
                    const requiredCount = gap.data?.required_count ?? gap.recommendedCount ?? 0;
                    const priorityLevel = gap.data?.current_count ?? gap.priority ?? 3;
                    
                    return (
                      <div 
                        key={gapId} 
                        className={`border rounded-lg p-4 ${
                          isSummer 
                            ? 'bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-900/20 dark:to-orange-900/20 border-yellow-200 dark:border-yellow-800' 
                            : 'bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border-blue-200 dark:border-blue-800'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${
                              isSummer 
                                ? 'bg-yellow-100 dark:bg-yellow-900/40' 
                                : 'bg-blue-100 dark:bg-blue-900/40'
                            }`}>
                              {isSummer ? (
                                <Sun className="h-5 w-5 text-yellow-600" />
                              ) : (
                                <Snowflake className="h-5 w-5 text-blue-600" />
                              )}
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {gap.category || gap.title}
                              </h4>
                              <p className="text-sm text-gray-600 dark:text-gray-400">
                                {currentCount}/{requiredCount} items
                              </p>
                            </div>
                          </div>
                          <Badge variant="outline" className="bg-white/50 dark:bg-stone-900/50">
                            {priorityLevel} priority
                          </Badge>
                        </div>
                        
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {gap.description}
                        </p>
                        
                        {gap.suggestedItems && gap.suggestedItems.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {gap.suggestedItems.map((item, itemIndex) => (
                              <Badge key={itemIndex} variant="secondary" className="text-xs">
                                {item}
                              </Badge>
                            ))}
                          </div>
                        )}
                        
                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600 dark:text-gray-400">Progress</span>
                            <span className="font-medium">{Math.round((currentCount / requiredCount) * 100)}%</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full transition-all duration-300 ${
                                isSummer 
                                  ? 'bg-gradient-to-r from-yellow-500 to-orange-500' 
                                  : 'bg-gradient-to-r from-blue-500 to-indigo-500'
                              }`}
                              style={{ width: `${Math.min((currentCount / requiredCount) * 100, 100)}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Regular Gaps Section */}
            {regularGaps.length > 0 && (
              <div className="space-y-4">
                {seasonalGaps.length > 0 && (
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">Additional Gaps</h3>
                )}
                
                {regularGaps.map((gap, index) => {
                  const gapId = gap.id || `gap-${index}`;
                  const isExpanded = expandedGaps.has(gapId);
                  
                  return (
                    <div key={gapId} className="border rounded-lg p-4">
                      <Collapsible open={isExpanded} onOpenChange={() => toggleGapExpansion(gapId)}>
                        <CollapsibleTrigger asChild>
                          <div className="flex items-center justify-between cursor-pointer">
                            <div className="flex items-center gap-3">
                              <div className={`p-2 rounded-lg ${getPriorityColor(gap.priority)}`}>
                                {getPriorityIcon(gap.priority)}
                              </div>
                              <div>
                                <h4 className="font-medium text-gray-900 dark:text-white">
                                  {gap.category}
                                </h4>
                                <p className="text-sm text-gray-600 dark:text-gray-400">
                                  {gap.currentCount}/{gap.recommendedCount} items
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant={gap.priority === 'high' ? 'destructive' : gap.priority === 'medium' ? 'secondary' : 'outline'}>
                                {gap.priority} priority
                              </Badge>
                              {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                            </div>
                          </div>
                        </CollapsibleTrigger>
                        
                        <CollapsibleContent className="mt-4">
                          <div className="space-y-3">
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {gap.description}
                            </p>
                            
                            {gap.suggestedItems && gap.suggestedItems.length > 0 && (
                              <div className="flex flex-wrap gap-2">
                                {gap.suggestedItems.map((item, itemIndex) => (
                                  <Badge key={itemIndex} variant="outline">
                                    {item}
                                  </Badge>
                                ))}
                              </div>
                            )}
                            
                            {/* Progress Bar */}
                            <div className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span>Progress</span>
                                <span>{Math.round((gap.currentCount / gap.recommendedCount) * 100)}%</span>
                              </div>
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                <div 
                                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                                  style={{ width: `${Math.min((gap.currentCount / gap.recommendedCount) * 100, 100)}%` }}
                                />
                              </div>
                            </div>
                          </div>
                        </CollapsibleContent>
                      </Collapsible>
                    </div>
                  );
                })}
              </div>
            )}

            {gaps.length === 0 && (
              <div className="text-center py-12 border border-dashed border-stone-300 dark:border-stone-700 rounded-lg">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <p className="text-stone-500 dark:text-stone-400 mb-2">No wardrobe gaps found!</p>
                <p className="text-sm text-stone-600 dark:text-stone-500">
                  Your wardrobe is well-balanced. Great job!
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

