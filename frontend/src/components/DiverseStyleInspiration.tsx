"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Heart, 
  Star, 
  Sparkles, 
  Users, 
  Palette, 
  Shirt,
  Crown,
  Zap,
  TrendingUp
} from 'lucide-react';

interface DiverseStyleInspirationProps {
  className?: string;
}

const DIVERSE_STYLE_CATEGORIES = [
  {
    id: 'plus-size',
    title: 'Plus Size Style',
    description: 'Beautiful outfits for all body types',
    icon: <Heart className="w-5 h-5" />,
    color: 'bg-pink-50 border-pink-200',
    textColor: 'text-pink-700',
    outfits: [
      {
        id: 1,
        title: 'Confident Casual',
        description: 'High-waisted jeans with a flowy blouse',
        tags: ['casual', 'comfortable', 'flattering'],
        image: '/images/inspiration/plus-casual.jpg'
      },
      {
        id: 2,
        title: 'Elegant Evening',
        description: 'Wrap dress with statement accessories',
        tags: ['formal', 'elegant', 'sophisticated'],
        image: '/images/inspiration/plus-evening.jpg'
      },
      {
        id: 3,
        title: 'Athleisure Chic',
        description: 'Stylish activewear for any occasion',
        tags: ['athletic', 'comfortable', 'trendy'],
        image: '/images/inspiration/plus-athletic.jpg'
      }
    ]
  },
  {
    id: 'petite',
    title: 'Petite Style',
    description: 'Styling tips for smaller frames',
    icon: <Star className="w-5 h-5" />,
    color: 'bg-blue-50 border-blue-200',
    textColor: 'text-blue-700',
    outfits: [
      {
        id: 1,
        title: 'Lengthening Layers',
        description: 'Vertical lines and monochrome looks',
        tags: ['lengthening', 'monochrome', 'vertical'],
        image: '/images/inspiration/petite-layers.jpg'
      },
      {
        id: 2,
        title: 'Proportional Dressing',
        description: 'Balanced proportions for petite frames',
        tags: ['proportional', 'balanced', 'flattering'],
        image: '/images/inspiration/petite-proportional.jpg'
      },
      {
        id: 3,
        title: 'High-Waisted Magic',
        description: 'High-waisted pieces to elongate legs',
        tags: ['high-waisted', 'elongating', 'casual'],
        image: '/images/inspiration/petite-high-waist.jpg'
      }
    ]
  },
  {
    id: 'tall',
    title: 'Tall Style',
    description: 'Embracing height with confidence',
    icon: <Crown className="w-5 h-5" />,
    color: 'bg-purple-50 border-purple-200',
    textColor: 'text-purple-700',
    outfits: [
      {
        id: 1,
        title: 'Statement Silhouettes',
        description: 'Bold shapes that celebrate height',
        tags: ['statement', 'bold', 'dramatic'],
        image: '/images/inspiration/tall-silhouettes.jpg'
      },
      {
        id: 2,
        title: 'Layered Looks',
        description: 'Complex layering for tall frames',
        tags: ['layered', 'complex', 'textured'],
        image: '/images/inspiration/tall-layers.jpg'
      },
      {
        id: 3,
        title: 'Maxi Everything',
        description: 'Long pieces that work beautifully',
        tags: ['maxi', 'long', 'elegant'],
        image: '/images/inspiration/tall-maxi.jpg'
      }
    ]
  },
  {
    id: 'adaptive',
    title: 'Adaptive Fashion',
    description: 'Inclusive design for all abilities',
    icon: <Users className="w-5 h-5" />,
    color: 'bg-green-50 border-green-200',
    textColor: 'text-green-700',
    outfits: [
      {
        id: 1,
        title: 'Easy Access',
        description: 'Magnetic closures and adaptive features',
        tags: ['adaptive', 'accessible', 'functional'],
        image: '/images/inspiration/adaptive-access.jpg'
      },
      {
        id: 2,
        title: 'Sensory Friendly',
        description: 'Comfortable fabrics and seamless design',
        tags: ['sensory', 'comfortable', 'seamless'],
        image: '/images/inspiration/adaptive-sensory.jpg'
      },
      {
        id: 3,
        title: 'Mobility Focused',
        description: 'Designs that support movement',
        tags: ['mobility', 'supportive', 'flexible'],
        image: '/images/inspiration/adaptive-mobility.jpg'
      }
    ]
  }
];

const BODY_POSITIVE_QUOTES = [
  "Style is about expressing who you are, not who you think you should be",
  "Every body is a good body - dress it with confidence",
  "Fashion is for everyone, regardless of size, shape, or ability",
  "Your unique style is your superpower",
  "Beauty comes in all shapes, sizes, and abilities"
];

export default function DiverseStyleInspiration({ className = '' }: DiverseStyleInspirationProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [favoriteOutfits, setFavoriteOutfits] = useState<Set<number>>(new Set());

  const toggleFavorite = (outfitId: number) => {
    const newFavorites = new Set(favoriteOutfits);
    if (newFavorites.has(outfitId)) {
      newFavorites.delete(outfitId);
    } else {
      newFavorites.add(outfitId);
    }
    setFavoriteOutfits(newFavorites);
  };

  const getRandomQuote = () => {
    return BODY_POSITIVE_QUOTES[Math.floor(Math.random() * BODY_POSITIVE_QUOTES.length)];
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Body Positive Message */}
      <Card className="bg-gradient-to-r from-pink-50 to-purple-50 border-pink-200">
        <CardContent className="p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Diverse Style Inspiration
            </h2>
            <p className="text-gray-600 mb-4">
              {getRandomQuote()}
            </p>
            <div className="flex items-center justify-center gap-2 text-pink-600">
              <Sparkles className="w-5 h-5" />
              <span className="font-medium">Celebrating all bodies, all styles, all abilities</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Style Categories */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
        {DIVERSE_STYLE_CATEGORIES.map((category) => (
          <Card 
            key={category.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${category.color} ${
              selectedCategory === category.id ? 'ring-2 ring-offset-2 ring-blue-500' : ''
            }`}
            onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
          >
            <CardHeader className="pb-3">
              <CardTitle className={`flex items-center gap-2 text-lg ${category.textColor}`}>
                {category.icon}
                {category.title}
              </CardTitle>
              <CardDescription className={category.textColor}>
                {category.description}
              </CardDescription>
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* Selected Category Outfits */}
      {selectedCategory && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shirt className="w-5 h-5" />
              {DIVERSE_STYLE_CATEGORIES.find(c => c.id === selectedCategory)?.title} Outfits
            </CardTitle>
            <CardDescription>
              Inspiration for {DIVERSE_STYLE_CATEGORIES.find(c => c.id === selectedCategory)?.description.toLowerCase()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {DIVERSE_STYLE_CATEGORIES
                .find(c => c.id === selectedCategory)
                ?.outfits.map((outfit) => (
                <div key={outfit.id} className="group relative">
                  <Card className="overflow-hidden hover:shadow-lg transition-all">
                    <div className="aspect-[4/5] relative bg-gray-100">
                      <img
                        src={outfit.image}
                        alt={outfit.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          const target = e.target as HTMLImageElement;
                          target.src = '/placeholder.png';
                        }}
                      />
                      <Button
                        size="sm"
                        variant="ghost"
                        className="absolute top-2 right-2 bg-white/80 hover:bg-white"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavorite(outfit.id);
                        }}
                      >
                        <Heart 
                          className={`w-4 h-4 ${
                            favoriteOutfits.has(outfit.id) ? 'text-red-500 fill-red-500' : 'text-gray-500'
                          }`} 
                        />
                      </Button>
                    </div>
                    <CardContent className="p-4">
                      <h3 className="font-semibold text-lg mb-2">{outfit.title}</h3>
                      <p className="text-sm text-gray-600 mb-3">{outfit.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {outfit.tags.map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Body Positive Tips */}
      <Card className="bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-yellow-800">
            <Zap className="w-5 h-5" />
            Style Confidence Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <h4 className="font-semibold text-yellow-800">For Every Body:</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• Focus on fit, not size</li>
                <li>• Choose colors that make you feel confident</li>
                <li>• Accessorize to express your personality</li>
                <li>• Comfort is always in style</li>
              </ul>
            </div>
            <div className="space-y-3">
              <h4 className="font-semibold text-yellow-800">Style Mindset:</h4>
              <ul className="text-sm text-yellow-700 space-y-1">
                <li>• Your body is perfect for you</li>
                <li>• Style is about self-expression</li>
                <li>• Confidence is your best accessory</li>
                <li>• Every body deserves beautiful clothes</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

