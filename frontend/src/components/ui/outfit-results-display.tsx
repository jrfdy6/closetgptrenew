'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Sparkles, 
  Zap,
  Shirt,
  Heart,
  Calendar,
  RefreshCw,
  Star,
  ThumbsUp,
  ThumbsDown,
  Info,
  Palette,
  Target,
  Clock,
  CheckCircle,
  ArrowRight,
  Eye,
  Share2
} from 'lucide-react';
import StyleEducationModule from './style-education-module';

interface GeneratedOutfit {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number;
  score_breakdown?: any;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    color: string;
    reason?: string;
  }>;
  reasoning: string;
  createdAt: string;
  metadata?: {
    generation_strategy?: string;
    [key: string]: any;
  };
}

interface OutfitRating {
  rating: number;
  isLiked: boolean;
  isDisliked: boolean;
  feedback?: string;
}

interface OutfitResultsDisplayProps {
  outfit: GeneratedOutfit;
  rating: OutfitRating;
  onRatingChange: (rating: number) => void;
  onLikeToggle: () => void;
  onDislikeToggle: () => void;
  onFeedbackChange: (feedback: string) => void;
  onWearOutfit: () => void;
  onRegenerate: () => void;
  onViewOutfits: () => void;
  ratingSubmitted: boolean;
  isWorn?: boolean;
}

export default function OutfitResultsDisplay({
  outfit,
  rating,
  onRatingChange,
  onLikeToggle,
  onDislikeToggle,
  onFeedbackChange,
  onWearOutfit,
  onRegenerate,
  onViewOutfits,
  ratingSubmitted,
  isWorn = false
}: OutfitResultsDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [showReasoning, setShowReasoning] = useState(false);

  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
    return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
  };

  const getConfidenceText = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Fair Match';
  };

  return (
    <div className="space-y-6">
      {/* Main Outfit Card */}
      <Card className="overflow-hidden border-2 border-purple-200 dark:border-purple-800 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {outfit.name}
              </CardTitle>
              <div className="flex flex-wrap gap-2 mb-3">
                <Badge variant="secondary" className="flex items-center gap-1">
                  <Palette className="h-3 w-3" />
                  {outfit.style}
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1">
                  <Target className="h-3 w-3" />
                  {outfit.mood}
                </Badge>
                <Badge variant="outline" className="flex items-center gap-1">
                  <Calendar className="h-3 w-3" />
                  {outfit.occasion}
                </Badge>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge 
                variant="secondary" 
                className={`flex items-center gap-1 ${getConfidenceColor(outfit.confidence_score)}`}
              >
                <Zap className="h-3 w-3" />
                {Math.round(outfit.confidence_score * 100)}% Match
              </Badge>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="text-gray-500 hover:text-gray-700"
              >
                <Eye className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Outfit Items Grid */}
          <div>
            <h4 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shirt className="h-5 w-5 text-purple-600" />
              Outfit Pieces ({outfit.items.length})
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {outfit.items.map((item, index) => (
                <div 
                  key={index} 
                  className="group relative bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-16 h-16 bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden flex-shrink-0">
                      {item.imageUrl ? (
                        <img 
                          src={item.imageUrl} 
                          alt={item.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const target = e.target as HTMLImageElement;
                            target.src = '/placeholder.jpg';
                          }}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Shirt className="h-8 w-8 text-gray-400" />
                        </div>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h5 className="font-medium text-gray-900 dark:text-white truncate">
                        {item.name}
                      </h5>
                      <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                        {item.type} • {item.color}
                      </p>
                      {item.reason && (
                        <p className="text-xs text-gray-500 dark:text-gray-500 mt-1 line-clamp-2">
                          {item.reason}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Weather-Informed Advisory Text - Always Visible */}
          {outfit.reasoning && (
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Info className="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">Outfit Advisory</h4>
                  <p className="text-sm text-blue-800 dark:text-blue-200 leading-relaxed">
                    {outfit.reasoning}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Score Breakdown */}
          {showDetails && outfit.score_breakdown && (
            <div className="space-y-4">
              <h4 className="font-semibold text-gray-900 dark:text-white">Outfit Analysis</h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Overall Score</span>
                  </div>
                  <div className="text-2xl font-bold text-blue-800 dark:text-blue-200">
                    {outfit.score_breakdown.total_score}
                  </div>
                  <div className="text-xs text-amber-600 dark:text-amber-400">
                    Grade: {outfit.score_breakdown.grade}
                  </div>
                </div>
                <div className="bg-gradient-to-r from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-700 dark:text-green-300">Confidence</span>
                  </div>
                  <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                    {Math.round(outfit.confidence_score * 100)}%
                  </div>
                  <div className="text-xs text-amber-600 dark:text-amber-400">
                    {getConfidenceText(outfit.confidence_score)}
                  </div>
                </div>
              </div>
              
              {/* Component Scores */}
              <div className="space-y-2">
                {Object.entries(outfit.score_breakdown).map(([key, value]) => {
                  if (key === 'total_score' || key === 'grade' || key === 'score_interpretation') return null;
                  return (
                    <div key={key} className="flex justify-between items-center text-sm py-2 px-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <span className="capitalize text-gray-700 dark:text-gray-300">
                        {key.replace(/_/g, ' ')}
                      </span>
                      <span className="font-medium text-gray-900 dark:text-white">
                        {value}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Rating Section */}
          <div className="border-t pt-6">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">Rate This Outfit</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
              Click the stars to rate this outfit. Your feedback helps improve future suggestions!
            </p>
            
            {/* Star Rating */}
            <div className="flex items-center gap-3 mb-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">Rating:</span>
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => onRatingChange(star)}
                    className={`text-2xl transition-all duration-200 hover:scale-110 cursor-pointer select-none ${
                      star <= rating.rating
                        ? 'text-yellow-400 fill-current'
                        : 'text-gray-300 dark:text-gray-600 hover:text-yellow-300'
                    }`}
                    style={{ userSelect: 'none' }}
                    disabled={ratingSubmitted}
                  >
                    ★
                  </button>
                ))}
              </div>
              {rating.rating > 0 && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {rating.rating} star{rating.rating !== 1 ? 's' : ''}
                </span>
              )}
              {ratingSubmitted && (
                <span className="text-xs text-amber-600 dark:text-amber-400 ml-2">
                  ✓ Submitted
                </span>
              )}
            </div>

            {/* Like/Dislike Buttons */}
            <div className="flex gap-3 mb-4">
              <Button
                variant={rating.isLiked ? "default" : "outline"}
                size="sm"
                onClick={onLikeToggle}
                disabled={ratingSubmitted}
                className={`flex items-center gap-2 ${
                  rating.isLiked 
                    ? 'bg-green-600 hover:bg-green-700 text-white' 
                    : 'hover:bg-green-50 hover:text-green-600'
                } ${ratingSubmitted ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <ThumbsUp className="h-4 w-4" />
                {rating.isLiked ? 'Liked' : 'Like'}
              </Button>
              <Button
                variant={rating.isDisliked ? "destructive" : "outline"}
                size="sm"
                onClick={onDislikeToggle}
                disabled={ratingSubmitted}
                className={`flex items-center gap-2 ${ratingSubmitted ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <ThumbsDown className="h-4 w-4" />
                {rating.isDisliked ? 'Disliked' : 'Dislike'}
              </Button>
            </div>

            {/* Feedback */}
            <div className="mb-4">
              <Textarea
                placeholder="Share your thoughts about this outfit..."
                value={rating.feedback}
                onChange={(e) => onFeedbackChange(e.target.value)}
                rows={3}
                className="text-sm"
                disabled={ratingSubmitted}
              />
            </div>

            {/* Status Messages */}
            {rating.rating > 0 && !ratingSubmitted && (
              <div className="text-xs text-amber-600 dark:text-amber-400 text-center mb-4">
                ✓ Rating will be automatically submitted
              </div>
            )}

            {ratingSubmitted && (
              <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg mb-4">
                <p className="text-sm text-amber-600 dark:text-amber-400 text-center">
                  ✓ Rating submitted! This helps improve future suggestions.
                </p>
              </div>
            )}

            {isWorn && (
              <div className="p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg mb-4">
                <p className="text-sm text-amber-600 dark:text-amber-400 text-center">
                  ✓ Outfit marked as worn! Redirecting to outfits page...
                </p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            {isWorn ? (
              <Button 
                onClick={onViewOutfits} 
                className="flex-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
              >
                <Shirt className="h-4 w-4 mr-2" />
                View My Outfits
              </Button>
            ) : ratingSubmitted ? (
              <>
                <Button onClick={onWearOutfit} className="flex-1 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-green-700 hover:to-emerald-700">
                  <Calendar className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
                <Button 
                  variant="outline" 
                  onClick={onViewOutfits}
                  className="flex-1"
                >
                  <Shirt className="h-4 w-4 mr-2" />
                  View All Outfits
                </Button>
              </>
            ) : (
              <>
                <Button onClick={onWearOutfit} className="flex-1 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-green-700 hover:to-emerald-700">
                  <Calendar className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
                <Button variant="outline" onClick={onRegenerate} className="flex-1">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Style Education Module */}
      <StyleEducationModule 
        outfitStyle={outfit.style}
        outfitMood={outfit.mood}
        outfitOccasion={outfit.occasion}
        outfitItems={outfit.items}
        outfitReasoning={outfit.reasoning}
        styleStrategy={outfit.metadata?.generation_strategy}
        className="mt-8"
      />
    </div>
  );
}
