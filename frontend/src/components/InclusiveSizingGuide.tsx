"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Ruler, 
  Heart, 
  Star, 
  Info, 
  CheckCircle, 
  AlertCircle,
  Accessibility,
  Users,
  Sparkles
} from 'lucide-react';

interface InclusiveSizingGuideProps {
  className?: string;
}

const SIZING_SYSTEMS = {
  'US': {
    name: 'US Sizing',
    ranges: {
      'XXS': '00-0',
      'XS': '2-4',
      'S': '6-8',
      'M': '10-12',
      'L': '14-16',
      'XL': '18-20',
      'XXL': '22-24',
      'XXXL': '26-28',
      '4XL': '30-32',
      '5XL': '34-36',
      '6XL': '38-40'
    }
  },
  'UK': {
    name: 'UK Sizing',
    ranges: {
      'XXS': '4-6',
      'XS': '8-10',
      'S': '12-14',
      'M': '16-18',
      'L': '20-22',
      'XL': '24-26',
      'XXL': '28-30',
      'XXXL': '32-34',
      '4XL': '36-38',
      '5XL': '40-42',
      '6XL': '44-46'
    }
  },
  'EU': {
    name: 'EU Sizing',
    ranges: {
      'XXS': '32-34',
      'XS': '36-38',
      'S': '40-42',
      'M': '44-46',
      'L': '48-50',
      'XL': '52-54',
      'XXL': '56-58',
      'XXXL': '60-62',
      '4XL': '64-66',
      '5XL': '68-70',
      '6XL': '72-74'
    }
  }
};

const ADAPTIVE_FEATURES = [
  {
    category: 'Mobility',
    features: [
      'Magnetic closures',
      'Velcro fastenings',
      'Elastic waistbands',
      'Side zippers',
      'Adjustable straps'
    ],
    icon: <Accessibility className="w-5 h-5" />
  },
  {
    category: 'Sensory',
    features: [
      'Soft, tagless fabrics',
      'Seamless construction',
      'Breathable materials',
      'No scratchy labels',
      'Smooth textures'
    ],
    icon: <Heart className="w-5 h-5" />
  },
  {
    category: 'Comfort',
    features: [
      'Stretchy materials',
      'Loose fits',
      'Breathable fabrics',
      'Non-restrictive cuts',
      'Comfortable waistlines'
    ],
    icon: <Star className="w-5 h-5" />
  }
];

const BODY_POSITIVE_TIPS = [
  "Focus on how clothes make you feel, not the number on the tag",
  "Every body is different - find what works for you",
  "Size is just a number - confidence is everything",
  "Your worth isn't determined by your clothing size",
  "Style is about expressing yourself, not fitting a mold"
];

export default function InclusiveSizingGuide({ className = '' }: InclusiveSizingGuideProps) {
  const [selectedSystem, setSelectedSystem] = useState<keyof typeof SIZING_SYSTEMS>('US');
  const [showTips, setShowTips] = useState(false);

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Body Positive Message */}
      <Card className="bg-gradient-to-r from-pink-50 to-purple-50 border-pink-200">
        <CardContent className="p-4">
          <div className="flex items-center gap-2 text-pink-700">
            <Sparkles className="w-5 h-5" />
            <p className="font-medium">
              {BODY_POSITIVE_TIPS[Math.floor(Math.random() * BODY_POSITIVE_TIPS.length)]}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Sizing Systems */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Ruler className="w-5 h-5" />
            Inclusive Sizing Guide
          </CardTitle>
          <CardDescription>
            Find your perfect fit with our comprehensive sizing guide
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* System Selector */}
          <div className="flex gap-2 flex-wrap">
            {Object.keys(SIZING_SYSTEMS).map((system) => (
              <Button
                key={system}
                variant={selectedSystem === system ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedSystem(system as keyof typeof SIZING_SYSTEMS)}
              >
                {SIZING_SYSTEMS[system as keyof typeof SIZING_SYSTEMS].name}
              </Button>
            ))}
          </div>

          {/* Size Chart */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
            {Object.entries(SIZING_SYSTEMS[selectedSystem].ranges).map(([size, range]) => (
              <div
                key={size}
                className="p-3 border rounded-lg text-center hover:bg-gray-50 transition-colors"
              >
                <div className="font-semibold text-sm">{size}</div>
                <div className="text-xs text-gray-600">{range}</div>
              </div>
            ))}
          </div>

          <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
            <Info className="w-4 h-4 inline mr-1" />
            <strong>Note:</strong> Sizes may vary between brands. Always check the specific brand's size chart.
          </div>
        </CardContent>
      </Card>

      {/* Adaptive Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            Adaptive & Inclusive Features
          </CardTitle>
          <CardDescription>
            Features designed to make fashion accessible for everyone
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {ADAPTIVE_FEATURES.map((category) => (
              <div key={category.category} className="space-y-3">
                <div className="flex items-center gap-2 text-lg font-semibold">
                  {category.icon}
                  {category.category}
                </div>
                <ul className="space-y-2">
                  {category.features.map((feature) => (
                    <li key={feature} className="flex items-center gap-2 text-sm">
                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Body Positive Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Heart className="w-5 h-5" />
            Body Positive Tips
          </CardTitle>
          <CardDescription>
            Remember: You are beautiful exactly as you are!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {BODY_POSITIVE_TIPS.map((tip, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-pink-50 rounded-lg">
                <Star className="w-5 h-5 text-pink-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-pink-800">{tip}</p>
              </div>
            ))}
          </div>
          
          <Button
            variant="outline"
            className="w-full mt-4"
            onClick={() => setShowTips(!showTips)}
          >
            {showTips ? 'Hide' : 'Show'} More Tips
          </Button>
          
          {showTips && (
            <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg">
              <h4 className="font-semibold mb-2">Additional Resources:</h4>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>• Follow body-positive influencers and brands</li>
                <li>• Focus on comfort and confidence over trends</li>
                <li>• Remember that all bodies are good bodies</li>
                <li>• Style is about expressing your personality</li>
                <li>• Your worth isn't determined by your appearance</li>
              </ul>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
