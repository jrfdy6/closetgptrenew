'use client';

import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { shoppingService, ShoppingRecommendationsResponse } from '@/lib/services/shoppingService';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
        <Tabs defaultValue="style-expansion" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="style-expansion" className="flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Style Expansion
            </TabsTrigger>
            <TabsTrigger value="gap-analysis" className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Gap Analysis
            </TabsTrigger>
            <TabsTrigger value="shopping" className="flex items-center gap-2">
              <ShoppingCart className="h-4 w-4" />
              Shopping
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Style Expansion */}
          <TabsContent value="style-expansion" className="space-y-6">
            {/* Style Expansion Areas */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Style Areas to Explore</h3>
                <p className="text-sm text-stone-600 dark:text-stone-400">
                  Your clothing items will allow you to explore the following areas as well
                </p>
              </div>
              
              {styleExpansions && styleExpansions.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {styleExpansions.map((expansion, index) => (
                    <div 
                      key={index} 
                      className="flex items-center justify-between p-4 border border-stone-200 dark:border-stone-700 rounded-lg bg-gradient-to-br from-white to-stone-50 dark:from-stone-900 dark:to-stone-800 hover:shadow-md transition-shadow"
                    >
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                          <Star className="h-5 w-5 text-purple-600" />
                        </div>
                        <span className="font-medium text-gray-900 dark:text-white capitalize">
                          {expansion.name}
                        </span>
                      </div>
                      <Badge 
                        variant={expansion.direction === 'Established' ? 'default' : 'outline'}
                        className={expansion.direction === 'Established' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' : ''}
                      >
                        {expansion.direction}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12 border border-dashed border-stone-300 dark:border-stone-700 rounded-lg">
                  <Sparkles className="w-16 h-16 text-stone-300 dark:text-stone-600 mx-auto mb-4" />
                  <p className="text-stone-500 dark:text-stone-400 mb-2">No style expansions available yet</p>
                  <p className="text-sm text-stone-600 dark:text-stone-500">
                    Add more diverse items to your wardrobe to unlock new style directions
                  </p>
                </div>
              )}
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

          {/* Tab 3: Shopping Recommendations */}
          <TabsContent value="shopping" className="space-y-6">
            {/* Budget Selection */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Shopping Recommendations</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Personalized suggestions based on your wardrobe gaps
                </p>
              </div>
              <Select value={selectedBudget} onValueChange={setSelectedBudget}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low Budget</SelectItem>
                  <SelectItem value="medium">Medium Budget</SelectItem>
                  <SelectItem value="high">High Budget</SelectItem>
                  <SelectItem value="luxury">Luxury</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {loadingRecommendations ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
                <p className="text-gray-500 dark:text-gray-400">Loading shopping recommendations...</p>
              </div>
            ) : (
              <>
                {/* Shopping Strategy Summary */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 p-6 rounded-lg border border-purple-200 dark:border-purple-800">
                  <h4 className="font-medium text-purple-900 dark:text-purple-100 mb-4 flex items-center gap-2">
                    <ShoppingBag className="h-5 w-5" />
                    Shopping Strategy
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-800 dark:text-purple-200">
                        {shoppingRecommendations?.shopping_strategy?.total_items_needed || gaps.length || 0}
                      </div>
                      <div className="text-sm text-purple-600 dark:text-purple-400">Items Needed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-800 dark:text-purple-200">
                        {shoppingRecommendations?.shopping_strategy?.high_priority_items || 
                         gaps.filter(g => g.priority === 'high').length || 0}
                      </div>
                      <div className="text-sm text-purple-600 dark:text-purple-400">High Priority</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-800 dark:text-purple-200">
                        {formatPrice(shoppingRecommendations?.total_estimated_cost || 0)}
                      </div>
                      <div className="text-sm text-purple-600 dark:text-purple-400">Total Cost</div>
                    </div>
                  </div>
                  <div className="mt-4 text-center">
                    <Badge variant="outline" className="bg-white/50 dark:bg-stone-900/50">
                      {selectedBudget} budget
                    </Badge>
                  </div>
                </div>

                {/* Shopping Phases */}
                {shoppingRecommendations?.shopping_strategy?.shopping_phases && 
                 shoppingRecommendations.shopping_strategy.shopping_phases.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-900 dark:text-white">Shopping Phases</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {shoppingRecommendations.shopping_strategy.shopping_phases.map((phase) => (
                        <div key={phase.phase} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex items-center justify-between mb-2">
                            <h5 className="font-medium">Phase {phase.phase}: {phase.name}</h5>
                            <Badge variant="outline">{formatPrice(phase.estimated_cost)}</Badge>
                          </div>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                            {phase.description}
                          </p>
                          <div className="text-xs text-gray-500">
                            {phase.items.length} items
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Store Recommendations */}
                <div className="space-y-4">
                  <h4 className="font-medium text-gray-900 dark:text-white flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-gray-500" />
                    Recommended Stores
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {stores.map((store, index) => (
                      <div 
                        key={index} 
                        className="border border-stone-200 dark:border-stone-700 rounded-lg p-4 hover:shadow-lg transition-all hover:border-purple-300 dark:hover:border-purple-700"
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <div className="p-1.5 bg-purple-100 dark:bg-purple-900/30 rounded">
                            <ShoppingBag className="h-4 w-4 text-purple-600" />
                          </div>
                          <h5 className="font-medium text-gray-900 dark:text-white">{store.name}</h5>
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                          {store.description}
                        </p>
                        <Badge variant="outline" className="text-xs">
                          {store.price_range}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Shopping Tips */}
                <div className="bg-gray-50 dark:bg-stone-800 p-6 rounded-lg border border-stone-200 dark:border-stone-700">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                    <Star className="h-5 w-5 text-yellow-500" />
                    Shopping Tips
                  </h4>
                  <ul className="space-y-3">
                    {tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-3 text-sm text-gray-600 dark:text-gray-400">
                        <CheckCircle className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{tip}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

