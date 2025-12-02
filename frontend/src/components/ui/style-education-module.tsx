'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Sparkles, 
  Palette, 
  Target, 
  ChevronDown, 
  ChevronUp,
  CheckCircle,
  Info,
  Calendar,
  Cloud,
  Heart,
  Zap
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import UpgradePrompt from '@/components/UpgradePrompt';

interface OutfitAnalysis {
  textureAnalysis?: {
    insight: string;
    smoothItems?: string[];
    texturedItems?: string[];
    uniformTexture?: string;
  } | null;
  patternBalance?: {
    insight: string;
    statement?: string;
    neutral?: string[];
    patterns?: string[];
  } | null;
  colorStrategy?: {
    insight: string;
    popColor?: string;
    popItem?: string;
    neutrals?: string[];
    boldColors?: string[];
    strategy?: string;
  } | null;
  styleSynergy?: {
    insight: string;
    primaryStyle?: string;
    secondaryStyle?: string;
    mixedStyles?: string[];
  } | null;
}

interface ExplanationData {
  category: string;
  icon: string;
  title: string;
  text: string;
  confidence: number;
  tips: string[];
}

interface ConfidenceBreakdown {
  overall: number;
  factors: {
    style_match?: number;
    color_combo?: number;
    occasion_fit?: number;
    weather?: number;
    personalization?: number;
  };
  summary: string;
}

interface StructuredExplanation {
  explanations?: ExplanationData[];
  confidence_breakdown?: ConfidenceBreakdown;
}

interface StyleEducationModuleProps {
  outfitStyle?: string;
  outfitMood?: string;
  outfitOccasion?: string;
  outfitItems?: Array<{
    name: string;
    type: string;
    color: string;
    reason?: string;
  }>;
  outfitReasoning?: string;
  styleStrategy?: string; // e.g. "cohesive_composition", "body_type_optimized", etc.
  outfitAnalysis?: OutfitAnalysis; // Detailed texture, pattern, color, style analysis
  structuredExplanation?: StructuredExplanation; // NEW: Structured explanation from backend
  weather?: {
    temperature?: number;
    condition?: string;
  };
  personalizationInsights?: {
    summary: string;
    confidence: string;
    insights: string[];
    personalization_level: number;
  };
  className?: string;
}

export default function StyleEducationModule({ 
  outfitStyle, 
  outfitMood, 
  outfitOccasion,
  outfitItems = [],
  outfitReasoning,
  styleStrategy,
  outfitAnalysis,
  structuredExplanation,
  weather,
  personalizationInsights,
  className = "" 
}: StyleEducationModuleProps) {
  const { user } = useFirebase();
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [subscription, setSubscription] = useState<any>(null);
  const [hasAccess, setHasAccess] = useState(true); // Default to true - basic explanations are free
  const [loading, setLoading] = useState(false); // Don't block on subscription check for basic explanations

  useEffect(() => {
    const checkSubscription = async () => {
      if (!user) {
        setHasAccess(true); // Basic explanations are free
        setLoading(false);
        return;
      }
      
      try {
        const { subscriptionService } = await import('@/lib/services/subscriptionService');
        const sub = await subscriptionService.getCurrentSubscription(user);
        setSubscription(sub);
        // Basic explanations (5 categories) are free for all users
        // Only advanced analysis (texture, pattern details) requires premium
        setHasAccess(true);
      } catch (err) {
        console.error('Error checking subscription:', err);
        // Default to access - basic explanations are free
        setHasAccess(true);
      } finally {
        setLoading(false);
      }
    };

    checkSubscription();
  }, [user]);

  // Convert technical strategy name to user-friendly description
  const getStrategyDescription = (strategy?: string) => {
    if (!strategy) return null;
    
    const strategies: Record<string, { title: string; description: string }> = {
      'cohesive_composition': {
        title: 'Cohesive Composition',
        description: 'Pieces selected for visual harmony and complementary aesthetics'
      },
      'body_type_optimized': {
        title: 'Body-Type Optimized',
        description: 'Outfit tailored to flatter your unique body proportions'
      },
      'style_profile_matched': {
        title: 'Style Profile Match',
        description: 'Items chosen based on your personal style preferences and history'
      },
      'weather_adapted': {
        title: 'Weather-Adapted',
        description: 'Temperature and conditions-appropriate outfit selection'
      },
      'fallback_simple': {
        title: 'Simple Selection',
        description: 'Straightforward outfit combination using available pieces'
      },
      'hybrid': {
        title: 'Hybrid Approach',
        description: 'Multi-factor intelligent selection combining style, fit, and context'
      },
      'robust_6d_with_diversity': {
        title: 'Advanced Algorithm',
        description: 'Sophisticated multi-dimensional analysis for optimal outfit creation'
      }
    };

    // Clean up the strategy string (remove underscores, handle variations)
    const cleanStrategy = strategy.toLowerCase().replace(/-/g, '_');
    return strategies[cleanStrategy] || {
      title: strategy.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      description: 'Intelligent outfit generation based on your wardrobe and preferences'
    };
  };

  const strategyInfo = getStrategyDescription(styleStrategy);

  // Get icon component from string name
  const getIconComponent = (iconName: string) => {
    const iconMap: Record<string, any> = {
      'palette': Palette,
      'droplet': Palette, // Color uses palette icon
      'calendar': Calendar,
      'cloud': Cloud,
      'heart': Heart,
      'target': Target,
      'sparkles': Sparkles,
      'checkcircle': CheckCircle,
      'info': Info
    };
    return iconMap[iconName.toLowerCase()] || Info;
  };

  // Generate outfit-specific insights (basic + backend analysis + structured explanations)
  const getOutfitInsights = () => {
    // If we have structured explanations from backend, use those first
    if (structuredExplanation?.explanations && structuredExplanation.explanations.length > 0) {
      return structuredExplanation.explanations.map(explanation => ({
        id: explanation.category,
        icon: getIconComponent(explanation.icon),
        title: explanation.title,
        insight: explanation.text,
        confidence: explanation.confidence,
        tips: explanation.tips || []
      }));
    }
    
    // Fallback to existing logic for backward compatibility
    const colors = outfitItems.map(item => item.color).filter(Boolean);
    const types = outfitItems.map(item => item.type).filter(Boolean);
    const hasLayers = types.some(type => ['jacket', 'blazer', 'cardigan', 'sweater'].includes(type.toLowerCase()));
    const hasFitted = types.some(type => ['shirt', 'blouse', 'dress'].includes(type.toLowerCase()));
    const hasLoose = types.some(type => ['pants', 'shorts', 'skirt'].includes(type.toLowerCase()));
    
    const insights = [];
    
    // Backend-generated Color Strategy (priority)
    if (outfitAnalysis?.colorStrategy) {
      insights.push({
        id: 'color-strategy',
        icon: Palette,
        title: 'Color Strategy',
        insight: outfitAnalysis.colorStrategy.insight,
        tips: [
          outfitAnalysis.colorStrategy.popColor 
            ? `${outfitAnalysis.colorStrategy.popColor} acts as your statement color`
            : null,
          outfitAnalysis.colorStrategy.neutrals && outfitAnalysis.colorStrategy.neutrals.length > 0
            ? `${outfitAnalysis.colorStrategy.neutrals.join(' and ')} provide a neutral canvas`
            : null,
          outfitAnalysis.colorStrategy.strategy === 'monochromatic'
            ? 'Vary textures to add interest to the single-color palette'
            : 'Color placement draws the eye to your best features'
        ].filter(Boolean)
      });
    } else if (colors.length > 1) {
      // Fallback color insight
      insights.push({
        id: 'color',
        icon: Palette,
        title: 'Color Harmony',
        insight: `The ${colors.join(' + ')} palette creates ${colors.length > 2 ? 'dynamic contrast' : 'balanced harmony'}`,
        tips: [
          `${colors[0]} serves as your base color`,
          colors[1] ? `${colors[1]} adds ${colors.length > 2 ? 'accent and depth' : 'complementary contrast'}` : null,
          colors.length > 2 ? 'Multiple colors add visual interest—keep accessories simple' : 'Two-tone combinations are timeless and versatile'
        ].filter(Boolean)
      });
    }
    
    // Backend-generated Texture Analysis
    if (outfitAnalysis?.textureAnalysis) {
      insights.push({
        id: 'texture',
        icon: Sparkles,
        title: 'Texture Mix',
        insight: outfitAnalysis.textureAnalysis.insight,
        tips: [
          outfitAnalysis.textureAnalysis.smoothItems
            ? `Smooth pieces (${outfitAnalysis.textureAnalysis.smoothItems.join(', ')}) feel polished`
            : null,
          outfitAnalysis.textureAnalysis.texturedItems
            ? `Textured pieces (${outfitAnalysis.textureAnalysis.texturedItems.join(', ')}) add tactile interest`
            : null,
          'Mixing textures creates depth without additional colors'
        ].filter(Boolean)
      });
    }
    
    // Backend-generated Pattern Balance
    if (outfitAnalysis?.patternBalance) {
      insights.push({
        id: 'pattern',
        icon: Target,
        title: 'Pattern Balance',
        insight: outfitAnalysis.patternBalance.insight,
        tips: [
          outfitAnalysis.patternBalance.statement
            ? `${outfitAnalysis.patternBalance.statement} is your focal point`
            : null,
          outfitAnalysis.patternBalance.neutral && outfitAnalysis.patternBalance.neutral.length > 0
            ? `Plain ${outfitAnalysis.patternBalance.neutral[0]} prevents visual overwhelm`
            : null,
          'Let one piece be the star—others should support, not compete'
        ].filter(Boolean)
      });
    }
    
    // Proportion insight
    if (hasFitted && hasLoose) {
      insights.push({
        id: 'proportion',
        icon: Target,
        title: 'Silhouette Balance',
        insight: 'Fitted + loose pieces create a flattering, proportioned silhouette',
        tips: [
          'This contrast defines your natural waistline',
          'Balanced proportions elongate your figure',
          'Try belting to further emphasize the shape'
        ]
      });
    }
    
    // Backend-generated Style Synergy
    if (outfitAnalysis?.styleSynergy) {
      insights.push({
        id: 'style-synergy',
        icon: CheckCircle,
        title: 'Style Harmony',
        insight: outfitAnalysis.styleSynergy.insight,
        tips: [
          outfitAnalysis.styleSynergy.primaryStyle
            ? `${outfitAnalysis.styleSynergy.primaryStyle} is your foundation`
            : null,
          outfitAnalysis.styleSynergy.secondaryStyle
            ? `${outfitAnalysis.styleSynergy.secondaryStyle} elements add personality`
            : null,
          'Mixing styles shows confidence and personal flair'
        ].filter(Boolean)
      });
    } else if (outfitOccasion) {
      // Fallback occasion insight
      insights.push({
        id: 'occasion',
        icon: Calendar,
        title: `${outfitOccasion} Ready`,
        insight: `This outfit hits the right tone for ${outfitOccasion.toLowerCase()}`,
        tips: [
          outfitStyle ? `${outfitStyle} style matches the event's vibe` : 'The formality level is spot-on',
          'Comfortable enough to wear confidently',
          'Easy to accessorize up or down as needed'
        ]
      });
    }
    
    // Add Weather Appropriateness if weather data is available
    if (weather && (weather.temperature !== undefined || weather.condition)) {
      const temp = weather.temperature || 70;
      let weatherText = '';
      if (temp >= 80) {
        weatherText = `Lightweight, breathable fabrics perfect for ${temp}°F weather.`;
      } else if (temp >= 65) {
        weatherText = `Lightweight layers ideal for ${temp}°F weather - comfortable and versatile.`;
      } else if (temp >= 50) {
        weatherText = `Layered pieces perfect for ${temp}°F weather - warm but not heavy.`;
      } else if (temp >= 32) {
        weatherText = `Warm layers appropriate for ${temp}°F weather - cozy and protective.`;
      } else {
        weatherText = `Heavy layers and insulation for ${temp}°F weather - maximum warmth.`;
      }
      
      if (weather.condition) {
        const condition = weather.condition.toLowerCase();
        if (condition.includes('rain') || condition.includes('storm')) {
          weatherText += ' Water-resistant pieces help you stay dry.';
        } else if (condition.includes('snow')) {
          weatherText += ' Insulated layers keep you warm in snowy conditions.';
        }
      }
      
      insights.push({
        id: 'weather',
        icon: Cloud,
        title: 'Weather Appropriateness',
        insight: weatherText,
        tips: [
          `Temperature-appropriate for ${temp}°F conditions`,
          'Layering allows you to adjust throughout the day',
          'Materials chosen for weather comfort'
        ]
      });
    }
    
    // Add Personalization with Spotify-style specific insights
    if (personalizationInsights && personalizationInsights.insights && personalizationInsights.insights.length > 0) {
      // Enhanced Spotify-style personalization with specific learned data
      const confidenceBadge = personalizationInsights.confidence === 'high' 
        ? '🎯 Highly Confident' 
        : personalizationInsights.confidence === 'medium'
        ? '✨ Good Match'
        : '🌱 Learning Your Style';
      
      // Build comprehensive tips combining learned insights + current outfit
      const enhancedTips = [
        `${confidenceBadge} - ${personalizationInsights.summary}`,
        ...personalizationInsights.insights,
        personalizationInsights.personalization_level > 0 
          ? `Your AI is ${personalizationInsights.personalization_level}% trained (${
              personalizationInsights.confidence === 'high' ? 'Expert level!' :
              personalizationInsights.confidence === 'medium' ? 'Getting smarter!' :
              'Building your profile'
            })`
          : 'Rate more outfits to improve personalization'
      ];
      
      insights.push({
        id: 'personalization',
        icon: Heart,
        title: 'Personalized for You',
        insight: 'This outfit matches your learned preferences and style evolution.',
        tips: enhancedTips
      });
    } else {
      // Fallback for users with no feedback history yet
      insights.push({
        id: 'personalization',
        icon: Heart,
        title: 'Personalized for You',
        insight: 'This outfit is tailored to your style preferences.',
        tips: [
          'Based on your personal style profile',
          'Combines items you love wearing',
          '💡 Rate outfits to unlock Spotify-style personalization!',
          'Each rating helps us learn: colors, styles, patterns you prefer'
        ]
      });
    }
    
    return insights;
  };

  const outfitInsights = getOutfitInsights();

  const toggleSection = (sectionId: string) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
  };

  // Show upgrade prompt if user doesn't have access
  if (!loading && !hasAccess) {
    return (
      <div className={className}>
        <UpgradePrompt 
          feature="learn_from_outfit"
          currentTier={subscription?.role || 'tier1'}
        />
      </div>
    );
  }

  // Show loading state while checking subscription
  if (loading) {
    return (
      <div className={className}>
        <Card className="border-2 border-amber-200 dark:border-amber-800">
          <CardContent className="p-6 text-center">
            <p className="text-muted-foreground">Loading...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      <Card className="border-2 border-amber-200 dark:border-amber-800 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-amber-500 to-orange-500 rounded-lg">
              <BookOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">
                Why This Outfit?
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Understand what makes this combination work
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* Confidence Breakdown - NEW */}
          {structuredExplanation?.confidence_breakdown && (
            <div className="p-4 bg-gradient-to-r from-amber-100 to-orange-100 dark:from-amber-900/30 dark:to-orange-900/30 rounded-lg border border-amber-200 dark:border-amber-800">
              <div className="flex items-center gap-2 mb-3">
                <Zap className="h-5 w-5 text-amber-600 dark:text-amber-400" />
                <h4 className="text-sm font-semibold text-amber-900 dark:text-amber-100">
                  Confidence Score
                </h4>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-amber-800 dark:text-amber-200">
                    Overall Confidence
                  </span>
                  <span className="text-lg font-bold text-amber-900 dark:text-amber-100">
                    {Math.round(structuredExplanation.confidence_breakdown.overall * 100)}%
                  </span>
                </div>
                {structuredExplanation.confidence_breakdown.factors && Object.keys(structuredExplanation.confidence_breakdown.factors).length > 0 && (
                  <div className="space-y-1.5 pt-2 border-t border-amber-200 dark:border-amber-700">
                    {Object.entries(structuredExplanation.confidence_breakdown.factors).map(([factor, score]) => {
                      const factorNames: Record<string, string> = {
                        'style_match': 'Style Match',
                        'color_combo': 'Color Combo',
                        'occasion_fit': 'Occasion Fit',
                        'weather': 'Weather',
                        'personalization': 'Personalization'
                      };
                      return (
                        <div key={factor} className="flex items-center justify-between text-xs">
                          <span className="text-amber-700 dark:text-amber-300">
                            {factorNames[factor] || factor.replace('_', ' ')}
                          </span>
                          <div className="flex items-center gap-2">
                            <div className="w-20 h-2 bg-amber-200 dark:bg-amber-800 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-gradient-to-r from-amber-500 to-orange-500"
                                style={{ width: `${(score as number) * 100}%` }}
                              />
                            </div>
                            <span className="text-amber-800 dark:text-amber-200 font-medium w-8 text-right">
                              {Math.round((score as number) * 100)}%
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                {structuredExplanation.confidence_breakdown.summary && (
                  <p className="text-xs text-amber-700 dark:text-amber-300 mt-2 pt-2 border-t border-amber-200 dark:border-amber-700">
                    {structuredExplanation.confidence_breakdown.summary}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Outfit Context - Compact badges only */}
          {(outfitStyle || outfitMood || outfitOccasion) && (
            <div className="flex flex-wrap gap-2">
                  {outfitStyle && (
                    <Badge variant="secondary" className="bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300">
                  {outfitStyle}
                    </Badge>
                  )}
                  {outfitMood && (
                    <Badge variant="secondary" className="bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300">
                  {outfitMood}
                    </Badge>
                  )}
                  {outfitOccasion && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                  {outfitOccasion}
                    </Badge>
                  )}
            </div>
          )}

          {/* Style Strategy - Generation Method */}
          {strategyInfo && (
            <div className="p-3 bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border border-indigo-200 dark:border-indigo-800">
              <div className="flex items-start gap-2">
                <Sparkles className="h-4 w-4 text-indigo-600 dark:text-indigo-400 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-semibold text-indigo-900 dark:text-indigo-100 mb-1">
                    {strategyInfo.title}
                  </h4>
                  <p className="text-xs text-indigo-700 dark:text-indigo-300">
                    {strategyInfo.description}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Selected Items - More prominent */}
              {outfitItems.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <Info className="h-4 w-4 text-amber-600" />
                Selected Pieces
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {outfitItems.map((item, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 bg-white/85 dark:bg-[#1A1510]/85 rounded-2xl border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 shadow-sm">
                    <div className="w-1.5 h-1.5 bg-[#FFB84C] rounded-full mt-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-[#1C1917] dark:text-[#F8F5F1] truncate">
                        {item.name}
                      </p>
                      <p className="text-xs text-[#57534E] dark:text-[#C4BCB4]">
                        {item.type} • {item.color}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
                </div>
              )}

          {/* AI Reasoning - If provided */}
              {outfitReasoning && (
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {outfitReasoning}
                  </p>
            </div>
          )}

          {/* Style Insights - Contextual and actionable */}
          {outfitInsights.length > 0 && (
          <div>
              <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                Why This Works
            </h3>
              <div className="space-y-2">
                {outfitInsights.map((insight) => (
                  <div 
                    key={insight.id}
                  className="bg-white/85 dark:bg-[#1A1510]/85 rounded-2xl border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 overflow-hidden shadow-md"
                >
                  <button
                      onClick={() => toggleSection(insight.id)}
                      className="w-full p-3 text-left hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] transition-colors"
                  >
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <insight.icon className="h-4 w-4 text-amber-600 flex-shrink-0" />
                          <div className="min-w-0 flex-1">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white">
                              {insight.title}
                          </h4>
                            <p className="text-xs text-gray-600 dark:text-gray-400 truncate">
                              {insight.insight}
                          </p>
                        </div>
                      </div>
                        {expandedSection === insight.id ? (
                          <ChevronUp className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      ) : (
                          <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                  
                    {expandedSection === insight.id && (
                      <div className="px-3 pb-3 border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
                        <ul className="pt-3 space-y-1.5">
                          {insight.tips.map((tip, index) => (
                              <li key={index} className="text-sm text-[#57534E] dark:text-[#C4BCB4] flex items-start gap-2">
                              <CheckCircle className="h-3.5 w-3.5 text-amber-500 mt-0.5 flex-shrink-0" />
                                {tip}
                              </li>
                            ))}
                          </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
          )}

        </CardContent>
      </Card>
    </div>
  );
}
