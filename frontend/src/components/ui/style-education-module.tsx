'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  BookOpen, 
  Sparkles, 
  Palette, 
  Target, 
  Zap, 
  ChevronDown, 
  ChevronUp,
  Lightbulb,
  TrendingUp,
  Eye,
  Heart,
  Star,
  ArrowRight,
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
  className?: string;
}

export default function StyleEducationModule({ 
  outfitStyle, 
  outfitMood, 
  outfitOccasion,
  outfitItems = [],
  outfitReasoning,
  className = "" 
}: StyleEducationModuleProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [showAllTips, setShowAllTips] = useState(false);

  // Generate outfit-specific style guides
  const getOutfitSpecificGuides = () => {
    const colors = outfitItems.map(item => item.color).filter(Boolean);
    const types = outfitItems.map(item => item.type).filter(Boolean);
    const hasLayers = types.some(type => ['jacket', 'blazer', 'cardigan', 'sweater'].includes(type.toLowerCase()));
    const hasFitted = types.some(type => ['shirt', 'blouse', 'dress'].includes(type.toLowerCase()));
    const hasLoose = types.some(type => ['pants', 'shorts', 'skirt'].includes(type.toLowerCase()));
    
    return [
      {
        id: 'color-harmony',
        title: 'Color Harmony',
        icon: Palette,
        description: colors.length > 0 ? `How your ${colors.join(', ')} combination works` : 'How we create perfect color combinations',
        tips: colors.length > 0 ? [
          `Your ${colors[0]} creates the foundation`,
          colors[1] ? `${colors[1]} provides contrast and interest` : 'Neutral colors anchor the look',
          'The color balance creates visual harmony',
          'Each color serves a specific purpose in your outfit'
        ] : [
          'Complementary colors create visual excitement',
          'Analogous colors provide harmony and flow',
          'Neutral colors anchor bold statement pieces',
          'Color temperature affects mood and perception'
        ],
        principles: [
          '60-30-10 rule: 60% dominant, 30% secondary, 10% accent',
          'Warm colors advance, cool colors recede',
          'Monochromatic schemes create sophisticated looks',
          'Color blocking can define your silhouette'
        ]
      },
      {
        id: 'proportion-balance',
        title: 'Proportion & Balance',
        icon: Target,
        description: hasFitted && hasLoose ? 'How your fitted and loose pieces create balance' : 'Creating flattering silhouettes',
        tips: hasFitted && hasLoose ? [
          'Your fitted top balances the looser bottom',
          'This creates an hourglass silhouette',
          'The contrast defines your waistline',
          'Proportional balance makes you look taller'
        ] : [
          'Balance loose with fitted pieces',
          'High-waisted bottoms elongate legs',
          'V-necks create the illusion of length',
          'Belt placement defines your waistline'
        ],
        principles: [
          'Rule of thirds for visual balance',
          'Vertical lines create height',
          'Horizontal lines add width',
          'Asymmetrical balance creates interest'
        ]
      },
      {
        id: 'fabric-texture',
        title: 'Fabric & Texture',
        icon: Sparkles,
        description: hasLayers ? 'How your layered pieces create texture and depth' : 'Mixing textures for depth and interest',
        tips: hasLayers ? [
          'Your layering creates visual depth',
          'Different textures add dimension',
          'The combination feels both structured and comfortable',
          'Texture mixing makes the outfit more interesting'
        ] : [
          'Smooth fabrics feel more formal',
          'Textured fabrics add casual comfort',
          'Layering different textures creates dimension',
          'Fabric weight affects drape and movement'
        ],
        principles: [
          'Contrast textures for visual interest',
          'Heavy fabrics add structure',
          'Light fabrics create flow',
          'Texture can balance proportions'
        ]
      },
      {
        id: 'occasion-appropriateness',
        title: 'Occasion Matching',
        icon: CheckCircle,
        description: outfitOccasion ? `Why this works for ${outfitOccasion.toLowerCase()}` : 'Dressing for the right moment',
        tips: outfitOccasion ? [
          `This outfit is perfect for ${outfitOccasion.toLowerCase()}`,
          'The style matches the occasion\'s requirements',
          'It strikes the right balance of comfort and style',
          'The pieces work together for this specific event'
        ] : [
          'Formal events require structured pieces',
          'Casual settings allow for more creativity',
          'Work attire balances professionalism and style',
          'Date night outfits should feel confident'
        ],
        principles: [
          'Dress codes provide guidelines, not limits',
          'Comfort enhances confidence',
          'Accessories can transform any outfit',
          'Weather-appropriate choices show consideration'
        ]
      }
    ];
  };

  const styleGuides = getOutfitSpecificGuides();

  // Generate outfit-specific process steps
  const getOutfitSpecificSteps = () => {
    const colors = outfitItems.map(item => item.color).filter(Boolean);
    const hasMultipleColors = colors.length > 1;
    
    return [
      {
        step: 1,
        title: 'Style Analysis',
        description: hasMultipleColors 
          ? `We analyzed your ${colors.join(' and ')} color combination for harmony`
          : 'We evaluated each piece for color harmony, fit, and style compatibility',
        icon: Eye
      },
      {
        step: 2,
        title: 'Context Matching',
        description: outfitOccasion 
          ? `We matched this outfit to your ${outfitOccasion.toLowerCase()} occasion`
          : 'We ensured each piece works for your specific occasion and mood',
        icon: Target
      },
      {
        step: 3,
        title: 'Harmony Creation',
        description: outfitItems.length > 0
          ? `We created cohesion between your ${outfitItems.length} pieces for a flattering look`
          : 'We applied fashion principles to create a cohesive, flattering combination',
        icon: Sparkles
      },
      {
        step: 4,
        title: 'Confidence Scoring',
        description: outfitStyle
          ? `We ensured this ${outfitStyle.toLowerCase()} look feels right and looks great`
          : 'We verified this combination makes you feel confident and look amazing',
        icon: Star
      }
    ];
  };

  const aiProcessSteps = getOutfitSpecificSteps();

  // Generate outfit-specific quick tips
  const getOutfitSpecificTips = () => {
    const colors = outfitItems.map(item => item.color).filter(Boolean);
    const types = outfitItems.map(item => item.type).filter(Boolean);
    const hasLayers = types.some(type => ['jacket', 'blazer', 'cardigan', 'sweater'].includes(type.toLowerCase()));
    
    const baseTips = [
      'Color harmony follows the 60-30-10 rule',
      'Proportion balance creates flattering silhouettes',
      'Texture mixing adds visual depth',
      'Accessories can make or break an outfit',
      'Confidence is the best accessory',
      'Fit matters more than following trends'
    ];

    const outfitSpecificTips = [];
    
    if (colors.length > 0) {
      outfitSpecificTips.push(`Your ${colors[0]} creates a strong foundation`);
    }
    
    if (hasLayers) {
      outfitSpecificTips.push('Layering adds dimension and sophistication');
    }
    
    if (outfitStyle) {
      outfitSpecificTips.push(`${outfitStyle} style emphasizes timeless elegance`);
    }
    
    if (outfitOccasion) {
      outfitSpecificTips.push(`Perfect for ${outfitOccasion.toLowerCase()} occasions`);
    }

    return [...outfitSpecificTips, ...baseTips].slice(0, 6);
  };

  const quickTips = getOutfitSpecificTips();

  const toggleSection = (sectionId: string) => {
    setExpandedSection(expandedSection === sectionId ? null : sectionId);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Education Card */}
      <Card className="border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
              <BookOpen className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white">
                Learn from This Outfit
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Understand why this outfit works and how to apply these principles yourself
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Outfit-Specific Analysis */}
          {(outfitStyle || outfitMood || outfitOccasion || outfitItems.length > 0) && (
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Info className="h-5 w-5 text-blue-600" />
                Why This Outfit Was Selected
              </h3>
              
              {/* Style Context */}
              <div className="mb-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Style Context</h4>
                <div className="flex flex-wrap gap-2 mb-3">
                  {outfitStyle && (
                    <Badge variant="secondary" className="bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300">
                      {outfitStyle} Style
                    </Badge>
                  )}
                  {outfitMood && (
                    <Badge variant="secondary" className="bg-pink-100 text-pink-700 dark:bg-pink-900 dark:text-pink-300">
                      {outfitMood} Mood
                    </Badge>
                  )}
                  {outfitOccasion && (
                    <Badge variant="secondary" className="bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300">
                      {outfitOccasion} Occasion
                    </Badge>
                  )}
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  This combination was chosen to match your {outfitStyle?.toLowerCase()} style for a {outfitOccasion?.toLowerCase()} occasion, 
                  creating a {outfitMood?.toLowerCase()} mood that's both appropriate and stylish.
                </p>
              </div>

              {/* Item Analysis */}
              {outfitItems.length > 0 && (
                <div className="mb-4">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Item Selection Logic</h4>
                  <div className="space-y-2">
                    {outfitItems.map((item, index) => (
                      <div key={index} className="flex items-start gap-3 p-2 bg-white dark:bg-gray-800 rounded-lg">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            {item.name}
                          </p>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {item.type} in {item.color}
                          </p>
                          {item.reason && (
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                              {item.reason}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Reasoning */}
              {outfitReasoning && (
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">AI's Style Reasoning</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
                    {outfitReasoning}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* AI Process Overview */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-purple-600" />
              The Science Behind Great Style
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {aiProcessSteps.map((step, index) => (
                <div 
                  key={step.step}
                  className="relative p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:shadow-lg hover:scale-105 transition-all duration-300 group"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-sm font-bold group-hover:scale-110 transition-transform duration-300">
                      {step.step}
                    </div>
                    <step.icon className="h-4 w-4 text-purple-600 group-hover:text-purple-700 transition-colors duration-300" />
                  </div>
                  <h4 className="font-medium text-gray-900 dark:text-white text-sm mb-1">
                    {step.title}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
                    {step.description}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Style Guides */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Lightbulb className="h-5 w-5 text-purple-600" />
              Fashion System Guides
            </h3>
            <div className="space-y-3">
              {styleGuides.map((guide) => (
                <div 
                  key={guide.id}
                  className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
                >
                  <button
                    onClick={() => toggleSection(guide.id)}
                    className="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-300 hover:shadow-sm"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <guide.icon className="h-5 w-5 text-purple-600" />
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">
                            {guide.title}
                          </h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {guide.description}
                          </p>
                        </div>
                      </div>
                      {expandedSection === guide.id ? (
                        <ChevronUp className="h-4 w-4 text-gray-400" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      )}
                    </div>
                  </button>
                  
                  {expandedSection === guide.id && (
                    <div className="px-4 pb-4 border-t border-gray-200 dark:border-gray-700">
                      <div className="pt-4 space-y-4">
                        <div>
                          <h5 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <TrendingUp className="h-4 w-4 text-green-600" />
                            Key Tips
                          </h5>
                          <ul className="space-y-1">
                            {guide.tips.map((tip, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                                <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                                {tip}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                            <Star className="h-4 w-4 text-yellow-600" />
                            Core Principles
                          </h5>
                          <ul className="space-y-1">
                            {guide.principles.map((principle, index) => (
                              <li key={index} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
                                <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                                {principle}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Quick Tips */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Heart className="h-5 w-5 text-purple-600" />
              Quick Style Tips
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {quickTips.slice(0, showAllTips ? quickTips.length : 4).map((tip, index) => (
                <div 
                  key={index}
                  className="flex items-center gap-3 p-3 bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg border border-purple-200 dark:border-purple-800 hover:shadow-md hover:scale-105 transition-all duration-300"
                >
                  <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex-shrink-0" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">{tip}</span>
                </div>
              ))}
            </div>
            {quickTips.length > 4 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAllTips(!showAllTips)}
                className="mt-3 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
              >
                {showAllTips ? 'Show Less' : `Show ${quickTips.length - 4} More Tips`}
                <ArrowRight className={`h-4 w-4 ml-1 transition-transform ${showAllTips ? 'rotate-90' : ''}`} />
              </Button>
            )}
          </div>

        </CardContent>
      </Card>
    </div>
  );
}
