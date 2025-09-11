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
  className?: string;
}

export default function StyleEducationModule({ 
  outfitStyle, 
  outfitMood, 
  outfitOccasion,
  className = "" 
}: StyleEducationModuleProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);
  const [showAllTips, setShowAllTips] = useState(false);

  const styleGuides = [
    {
      id: 'color-harmony',
      title: 'Color Harmony',
      icon: Palette,
      description: 'How we create perfect color combinations',
      tips: [
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
      description: 'Creating flattering silhouettes',
      tips: [
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
      description: 'Mixing textures for depth and interest',
      tips: [
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
      description: 'Dressing for the right moment',
      tips: [
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

  const aiProcessSteps = [
    {
      step: 1,
      title: 'Style Analysis',
      description: 'We analyze your wardrobe pieces, considering color, cut, and style',
      icon: Eye
    },
    {
      step: 2,
      title: 'Context Matching',
      description: 'Your occasion, mood, and preferences guide the selection process',
      icon: Target
    },
    {
      step: 3,
      title: 'Harmony Creation',
      description: 'AI applies fashion principles to create cohesive, flattering combinations',
      icon: Sparkles
    },
    {
      step: 4,
      title: 'Confidence Scoring',
      description: 'Each outfit receives a confidence score based on style principles',
      icon: Star
    }
  ];

  const quickTips = [
    'Color harmony follows the 60-30-10 rule',
    'Proportion balance creates flattering silhouettes',
    'Texture mixing adds visual depth',
    'Accessories can make or break an outfit',
    'Confidence is the best accessory',
    'Fit matters more than following trends'
  ];

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
                Style Education
              </CardTitle>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Discover how our AI creates your perfect outfits
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* AI Process Overview */}
          <div>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-purple-600" />
              How We Select Your Outfit
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

          {/* Current Outfit Context - Only show if we have outfit data */}
          {(outfitStyle || outfitMood || outfitOccasion) && (
            <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                <Info className="h-4 w-4 text-blue-600" />
                This Outfit's Style Context
              </h4>
              <div className="flex flex-wrap gap-2">
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
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
