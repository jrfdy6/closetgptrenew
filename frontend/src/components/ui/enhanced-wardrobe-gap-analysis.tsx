'use client';

import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/AuthContext';
import { shoppingService, ShoppingRecommendationsResponse } from '@/lib/services/shoppingService';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  ShoppingBag, 
  ExternalLink, 
  DollarSign, 
  Star,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Heart,
  Filter,
  SortAsc,
  ChevronDown,
  ChevronRight,
  ShoppingCart,
  MapPin,
  Clock,
  Tag
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

interface WardrobeGap {
  category: string;
  priority: 'high' | 'medium' | 'low';
  description: string;
  suggestedItems: string[];
  currentCount: number;
  recommendedCount: number;
  gapSize: number;
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

interface EnhancedWardrobeGapAnalysisProps {
  gaps: WardrobeGap[];
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

export default function EnhancedWardrobeGapAnalysis({
  gaps,
  shoppingRecommendations: initialShoppingRecommendations,
  onRefresh,
  className = ""
}: EnhancedWardrobeGapAnalysisProps) {
  const { user } = useAuthContext();
  const [selectedBudget, setSelectedBudget] = useState<string>('medium');
  const [selectedPhase, setSelectedPhase] = useState<number>(1);
  const [expandedGaps, setExpandedGaps] = useState<Set<string>>(new Set());
  const [sortBy, setSortBy] = useState<'priority' | 'price' | 'versatility'>('priority');
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
  }, [selectedBudget, gaps, user]);

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
      case 'high':
        return 'text-[#FF4A3A] bg-[#FFF0EC] dark:bg-[#3D211F] border border-[#FF6F61]/40 shadow-sm';
      case 'medium':
        return 'text-[#B45309] bg-[#FFF7E6] dark:bg-[#262626] border border-[#FFB84C]/40 shadow-sm';
      case 'low':
        return 'text-[#0F766E] bg-[#ECFDF5] dark:bg-[#1F3D32] border border-[#6EE7B7]/40 shadow-sm';
      default:
        return 'text-[#57534E] bg-[#F5F0E8]/70 dark:bg-[#1A1A1A]/70 border border-[#F5F0E8]/50 dark:border-[#2E2E2E]/60 shadow-sm';
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

  const getVersatilityColor = (score: number) => {
    if (score >= 8) return 'text-[#0F766E]';
    if (score >= 6) return 'text-[#B45309]';
    return 'text-[#FF4A3A]';
  };

  const sortedRecommendations = shoppingRecommendations?.recommendations.sort((a, b) => {
    switch (sortBy) {
      case 'priority':
        const priorityOrder = { 'high': 3, 'medium': 2, 'low': 1 };
        return (priorityOrder[b.priority as keyof typeof priorityOrder] || 0) - 
               (priorityOrder[a.priority as keyof typeof priorityOrder] || 0);
      case 'price':
        return a.estimated_price - b.estimated_price;
      case 'versatility':
        return b.versatility_score - a.versatility_score;
      default:
        return 0;
    }
  }) || [];

  if (!gaps || gaps.length === 0) {
    return (
      <Card className={cn("bg-white/85 dark:bg-[#0D0D0D]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl shadow-lg backdrop-blur-xl", className)}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-amber-600" />
            Wardrobe Gap Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-10">
            <CheckCircle className="w-16 h-16 text-[#FFB84C] mx-auto mb-4" />
            <p className="text-[#57534E] dark:text-[#C4BCB4] mb-4 font-semibold">No wardrobe gaps found!</p>
            <p className="text-sm text-[#827869] dark:text-[#8A827A]">
              Your wardrobe is well-balanced. Great job!
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Gap Analysis Card */}
      <Card className="bg-white/85 dark:bg-[#0D0D0D]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl shadow-lg backdrop-blur-xl">
        <CardHeader className="border-b border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
              <ShoppingBag className="h-5 w-5 text-[#FFB84C]" />
              Wardrobe Gap Analysis
            </CardTitle>
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
              >
                <TrendingUp className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {gaps.map((gap, index) => {
              const gapId = `gap-${index}`;
              const isExpanded = expandedGaps.has(gapId);
              
              return (
                <div key={index} className="border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-2xl p-4 bg-white/80 dark:bg-[#1A1510]/80 shadow-sm">
                  <Collapsible open={isExpanded} onOpenChange={() => toggleGapExpansion(gapId)}>
                    <CollapsibleTrigger asChild>
                      <div className="flex items-center justify-between cursor-pointer">
                        <div className="flex items-center gap-3">
                          <div className={cn("p-2 rounded-xl flex items-center justify-center transition-colors", getPriorityColor(gap.priority))}>
                            {getPriorityIcon(gap.priority)}
                          </div>
                          <div>
                            <h4 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
                              {gap.category}
                            </h4>
                            <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
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
                        <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                          {gap.description}
                        </p>
                        
                        <div className="flex flex-wrap gap-2">
                          {gap.suggestedItems.map((item, itemIndex) => (
                            <Badge key={itemIndex} variant="outline" className="border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4]">
                              {item}
                            </Badge>
                          ))}
                        </div>
                        
                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm text-[#57534E] dark:text-[#C4BCB4]">
                            <span>Progress</span>
                            <span>{gap.recommendedCount && gap.recommendedCount > 0 
                              ? `${Math.round((gap.currentCount / gap.recommendedCount) * 100)}%` 
                              : '0%'}</span>
                          </div>
                          <div className="w-full bg-[#E7DDCF] dark:bg-[#262626] rounded-full h-2">
                            <div 
                              className="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${gap.recommendedCount && gap.recommendedCount > 0 
                                ? Math.min((gap.currentCount / gap.recommendedCount) * 100, 100) 
                                : 0}%` }}
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
        </CardContent>
      </Card>

      {/* Shopping Recommendations */}
      {(shoppingRecommendations?.success || loadingRecommendations) && (
        <Card className="bg-white/85 dark:bg-[#0D0D0D]/85 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-3xl shadow-lg backdrop-blur-xl">
          <CardHeader className="border-b border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
                <ShoppingCart className="h-5 w-5 text-[#FFB84C]" />
                Shopping Recommendations
                {loadingRecommendations && (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-[#6EE7B7]"></div>
                )}
              </CardTitle>
              <div className="flex items-center gap-2">
                <Select value={selectedBudget} onValueChange={setSelectedBudget}>
                  <SelectTrigger className="w-32 border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 bg-white/80 dark:bg-[#1A1510]/80">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low budget</SelectItem>
                    <SelectItem value="medium">Medium budget</SelectItem>
                    <SelectItem value="high">High budget</SelectItem>
                    <SelectItem value="luxury">Luxury</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            {shoppingRecommendations?.success && (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-[#57534E]" />
                  <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                    Total: {formatPrice(shoppingRecommendations.total_estimated_cost)}
                  </span>
                </div>
                <Badge variant="outline" className="border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4]">
                  {shoppingRecommendations.budget_range} budget
                </Badge>
              </div>
            )}
          </CardHeader>
          <CardContent>
            {loadingRecommendations ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#6EE7B7] mx-auto mb-4"></div>
                <p className="text-[#57534E] dark:text-[#C4BCB4]">Loading shopping recommendations…</p>
              </div>
            ) : shoppingRecommendations?.success ? (
              <div className="space-y-6">
                {/* Shopping Strategy */}
                {shoppingRecommendations.shopping_strategy && (
                <div className="bg-[#ECF2FF]/80 dark:bg-[#1E2840]/70 border border-[#93C5FD]/40 p-4 rounded-2xl">
                  <h4 className="font-semibold text-[#1D4ED8] dark:text-[#BFDBFE] mb-3">
                    Shopping Strategy
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#1D4ED8] dark:text-[#BFDBFE]">
                        {shoppingRecommendations.shopping_strategy.total_items_needed}
                      </div>
                      <div className="text-sm text-[#B45309] dark:text-[#Fbbf24]">Items needed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#1D4ED8] dark:text-[#BFDBFE]">
                        {shoppingRecommendations.shopping_strategy.high_priority_items}
                      </div>
                      <div className="text-sm text-[#B45309] dark:text-[#Fbbf24]">High priority</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[#1D4ED8] dark:text-[#BFDBFE]">
                        {formatPrice(shoppingRecommendations.shopping_strategy.estimated_total_cost)}
                      </div>
                      <div className="text-sm text-[#B45309] dark:text-[#Fbbf24]">Total cost</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Shopping Phases */}
              {shoppingRecommendations.shopping_strategy?.shopping_phases && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">Shopping phases</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {shoppingRecommendations.shopping_strategy.shopping_phases.map((phase) => (
                      <div key={phase.phase} className="border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-2xl p-4 bg-white/80 dark:bg-[#1A1510]/80 shadow-sm">
                        <div className="flex items-center justify-between mb-2">
                          <h5 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">Phase {phase.phase}: {phase.name}</h5>
                          <Badge variant="outline" className="border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4]">
                            {formatPrice(phase.estimated_cost)}
                          </Badge>
                        </div>
                        <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">
                          {phase.description}
                        </p>
                        <div className="text-xs text-[#827869] dark:text-[#8A827A]">
                          {phase.items.length} items
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Store Recommendations */}
              {shoppingRecommendations.store_recommendations && (
                <div className="space-y-4">
                  <h4 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">Recommended stores</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {shoppingRecommendations.store_recommendations.map((store, index) => (
                      <div key={index} className="border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 rounded-2xl p-4 bg-white/80 dark:bg-[#1A1510]/75 hover:shadow-xl transition-shadow">
                        <div className="flex items-center gap-2 mb-2 text-[#57534E] dark:text-[#C4BCB4]">
                          <MapPin className="h-4 w-4 text-[#FF9400]" />
                          <h5 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1]">{store.name}</h5>
                        </div>
                        <p className="text-sm text-[#57534E] dark:text-[#C4BCB4] mb-2">
                          {store.description}
                        </p>
                        <Badge variant="outline" className="text-xs border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 text-[#57534E] dark:text-[#C4BCB4]">
                          {store.price_range}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Shopping Tips */}
              {shoppingRecommendations.shopping_strategy?.tips && (
                <div className="bg-[#F5F0E8]/70 dark:bg-[#1A1A1A]/80 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 p-4 rounded-2xl shadow-sm">
                  <h4 className="font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-3">Shopping tips</h4>
                  <ul className="space-y-2">
                    {shoppingRecommendations.shopping_strategy.tips.map((tip, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-[#57534E] dark:text-[#C4BCB4]">
                        <CheckCircle className="h-4 w-4 text-[#34D399] mt-0.5 flex-shrink-0" />
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              </div>
            ) : (
              <div className="text-center py-8">
                <AlertCircle className="w-16 h-16 text-amber-500 mx-auto mb-4" />
                <p className="text-[#57534E] dark:text-[#C4BCB4] mb-2 font-semibold">No shopping recommendations available</p>
                <p className="text-sm text-[#827869] dark:text-[#8A827A]">
                  Try refreshing or check back later.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
