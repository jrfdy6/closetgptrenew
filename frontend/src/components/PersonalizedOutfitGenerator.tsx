/**
 * PersonalizedOutfitGenerator Component
 * =====================================
 * 
 * Enhanced outfit generator that uses existing Firebase data for personalization.
 * Falls back to regular generation if personalization is not available.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  Brain, 
  RefreshCw, 
  Heart, 
  TrendingUp,
  Palette,
  Shirt,
  Calendar,
  AlertCircle,
  CheckCircle,
  Info
} from 'lucide-react';
import { useExistingDataPersonalization } from '@/lib/hooks/useExistingDataPersonalization';
import { PersonalizedOutfit, OutfitGenerationRequest } from '@/lib/services/existingDataPersonalizationService';

interface PersonalizedOutfitGeneratorProps {
  className?: string;
  onOutfitGenerated?: (outfit: PersonalizedOutfit) => void;
  onError?: (error: string) => void;
  initialRequest?: Partial<OutfitGenerationRequest>;
}

export default function PersonalizedOutfitGenerator({
  className = '',
  onOutfitGenerated,
  onError,
  initialRequest = {}
}: PersonalizedOutfitGeneratorProps) {
  const {
    personalizationStatus,
    isLoading: personalizationLoading,
    error: personalizationError,
    isReadyForPersonalization,
    hasExistingData,
    totalInteractions,
    topColors,
    topStyles,
    topOccasions,
    generatePersonalizedOutfit,
    refreshPersonalizationData
  } = useExistingDataPersonalization();

  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<PersonalizedOutfit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateOutfit = async () => {
    if (!personalizationStatus) {
      const errorMsg = 'Personalization data not available';
      setError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      setGenerating(true);
      setError(null);

      // Create request with defaults
      const request: OutfitGenerationRequest = {
        occasion: initialRequest.occasion || 'Casual',
        style: initialRequest.style || 'Classic',
        mood: initialRequest.mood || 'Confident',
        weather: initialRequest.weather || {
          temperature: 72,
          condition: 'Clear',
          humidity: 50,
          wind_speed: 5,
          location: 'Current Location'
        },
        wardrobe: initialRequest.wardrobe || [],
        user_profile: initialRequest.user_profile || {},
        baseItemId: initialRequest.baseItemId
      };

      console.log('🎯 [PersonalizedOutfitGenerator] Generating outfit with request:', request);

      const outfit = await generatePersonalizedOutfit(request);
      
      if (outfit) {
        setGeneratedOutfit(outfit);
        onOutfitGenerated?.(outfit);
        console.log('✅ [PersonalizedOutfitGenerator] Outfit generated successfully:', outfit);
      } else {
        throw new Error('Failed to generate outfit');
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to generate personalized outfit';
      setError(errorMsg);
      onError?.(errorMsg);
      console.error('❌ [PersonalizedOutfitGenerator] Error generating outfit:', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerate = () => {
    setGeneratedOutfit(null);
    setError(null);
    handleGenerateOutfit();
  };

  const handleRefreshPersonalization = async () => {
    await refreshPersonalizationData();
  };

  return (
    <div className={className}>
      {/* Personalization Status */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Personalization Engine
            {isReadyForPersonalization ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                {totalInteractions}
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-400">Interactions</div>
            </div>
            
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-xl font-bold text-green-600 dark:text-green-400">
                {personalizationStatus?.favorite_items_count || 0}
              </div>
              <div className="text-sm text-green-600 dark:text-green-400">Favorites</div>
            </div>
            
            <div className="text-center p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <div className="text-xl font-bold text-purple-600 dark:text-purple-400">
                {personalizationStatus?.most_worn_items_count || 0}
              </div>
              <div className="text-sm text-purple-600 dark:text-purple-400">Most Worn</div>
            </div>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg mb-4">
            <span className="font-medium">Personalization Status</span>
            <Badge variant={isReadyForPersonalization ? "default" : "secondary"}>
              {isReadyForPersonalization ? "Ready" : "Learning"}
            </Badge>
          </div>

          {/* Top Preferences */}
          {topColors.length > 0 && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Palette className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">Your Top Colors</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {topColors.slice(0, 5).map((color, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {color}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {topStyles.length > 0 && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Shirt className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">Your Top Styles</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {topStyles.slice(0, 5).map((style, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {style}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {topOccasions.length > 0 && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">Your Top Occasions</span>
              </div>
              <div className="flex flex-wrap gap-1">
                {topOccasions.slice(0, 5).map((occasion, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {occasion}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <Button 
              onClick={handleRefreshPersonalization}
              variant="outline" 
              size="sm"
              disabled={personalizationLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${personalizationLoading ? 'animate-spin' : ''}`} />
              Refresh Data
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Generation Controls */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            Generate Personalized Outfit
          </CardTitle>
        </CardHeader>
        <CardContent>
          {personalizationError ? (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg mb-4">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-600">Personalization Error: {personalizationError}</span>
            </div>
          ) : !hasExistingData ? (
            <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg mb-4">
              <Info className="h-4 w-4 text-yellow-500" />
              <span className="text-yellow-600">No existing data found. Personalization will be limited.</span>
            </div>
          ) : !isReadyForPersonalization ? (
            <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg mb-4">
              <Info className="h-4 w-4 text-blue-500" />
              <span className="text-blue-600">
                Learning from your data... ({totalInteractions} interactions)
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg mb-4">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span className="text-green-600">Ready for personalized recommendations!</span>
            </div>
          )}

          <Button 
            onClick={handleGenerateOutfit}
            disabled={generating || personalizationLoading}
            className="w-full"
          >
            {generating ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Generating Personalized Outfit...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4 mr-2" />
                Generate Personalized Outfit
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Outfit Display */}
      {generatedOutfit && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="h-5 w-5 text-red-500" />
              Generated Outfit
              {generatedOutfit.personalization_applied && (
                <Badge variant="default" className="ml-2">
                  Personalized
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Outfit Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Style</div>
                  <div className="font-semibold">{generatedOutfit.style}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-muted-foreground">Occasion</div>
                  <div className="font-semibold">{generatedOutfit.occasion}</div>
                </div>
              </div>

              {/* Personalization Info */}
              {generatedOutfit.personalization_applied && (
                <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-2">
                    Personalization Applied
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Score:</span>
                      <span className="ml-2 font-medium">
                        {generatedOutfit.personalization_score?.toFixed(2) || 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Interactions:</span>
                      <span className="ml-2 font-medium">{generatedOutfit.user_interactions}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Items */}
              <div>
                <div className="text-sm font-medium text-muted-foreground mb-2">Items ({generatedOutfit.items.length})</div>
                <div className="space-y-2">
                  {generatedOutfit.items.map((item, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                      <div>
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-muted-foreground">{item.type} • {item.color}</div>
                      </div>
                      <Badge variant="outline">{item.color}</Badge>
                    </div>
                  ))}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t">
                <Button onClick={handleRegenerate} variant="outline" size="sm">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Regenerate
                </Button>
                <Button variant="outline" size="sm">
                  <Heart className="h-4 w-4 mr-2" />
                  Save Outfit
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error Display */}
      {error && (
        <Card className="mt-6">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
