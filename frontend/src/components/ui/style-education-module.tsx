'use client';

import { useState } from 'react';
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
  Info
} from 'lucide-react';

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
  className?: string;
}

export default function StyleEducationModule({ 
  outfitStyle, 
  outfitMood, 
  outfitOccasion,
  outfitItems = [],
  outfitReasoning,
  styleStrategy,
  className = "" 
}: StyleEducationModuleProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

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

  // Generate outfit-specific insights
  const getOutfitInsights = () => {
    const colors = outfitItems.map(item => item.color).filter(Boolean);
    const types = outfitItems.map(item => item.type).filter(Boolean);
    const hasLayers = types.some(type => ['jacket', 'blazer', 'cardigan', 'sweater'].includes(type.toLowerCase()));
    const hasFitted = types.some(type => ['shirt', 'blouse', 'dress'].includes(type.toLowerCase()));
    const hasLoose = types.some(type => ['pants', 'shorts', 'skirt'].includes(type.toLowerCase()));
    
    const insights = [];
    
    // Color insight
    if (colors.length > 1) {
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
    
    // Layering insight
    if (hasLayers) {
      insights.push({
        id: 'layering',
        icon: Sparkles,
        title: 'Layering Depth',
        insight: 'Multiple layers add dimension and adaptability',
        tips: [
          'Layers create visual interest and texture',
          'Remove outer pieces to adjust for temperature',
          'Each layer should be visible for maximum effect'
        ]
      });
    }
    
    // Occasion insight (always show if available)
    if (outfitOccasion) {
      insights.push({
        id: 'occasion',
        icon: CheckCircle,
        title: `${outfitOccasion} Ready`,
        insight: `This outfit hits the right tone for ${outfitOccasion.toLowerCase()}`,
        tips: [
          outfitStyle ? `${outfitStyle} style matches the event's vibe` : 'The formality level is spot-on',
          'Comfortable enough to wear confidently',
          'Easy to accessorize up or down as needed'
        ]
      });
    }
    
    return insights;
  };

  const outfitInsights = getOutfitInsights();

  const toggleSection = (sectionId: string) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
  };

  return (
    <div className={`space-y-4 ${className}`}>
      <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <BookOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">
                Learn from This Outfit
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Understand what makes this combination work
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* Outfit Context - Compact badges only */}
          {(outfitStyle || outfitMood || outfitOccasion) && (
            <div className="flex flex-wrap gap-2">
              {outfitStyle && (
                <Badge variant="secondary" className="bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300">
                  {outfitStyle}
                </Badge>
              )}
              {outfitMood && (
                <Badge variant="secondary" className="bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300">
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
                <Info className="h-4 w-4 text-purple-600" />
                Selected Pieces
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {outfitItems.map((item, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
                    <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                        {item.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
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
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                  >
                    <button
                      onClick={() => toggleSection(insight.id)}
                      className="w-full p-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <insight.icon className="h-4 w-4 text-purple-600 flex-shrink-0" />
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
                      <div className="px-3 pb-3 border-t border-gray-200 dark:border-gray-700">
                        <ul className="pt-3 space-y-1.5">
                          {insight.tips.map((tip, index) => (
                            <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                              <CheckCircle className="h-3.5 w-3.5 text-green-500 mt-0.5 flex-shrink-0" />
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
