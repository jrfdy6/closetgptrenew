/**
 * Personalization Integration Example
 * ===================================
 * 
 * This is a simple example showing how to integrate the existing data
 * personalization system into your current outfit generation page.
 * 
 * Copy this code and modify it to fit your existing page structure.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  Sparkles, 
  RefreshCw, 
  Heart, 
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { useExistingDataPersonalization } from '@/lib/hooks/useExistingDataPersonalization';
import { PersonalizedOutfit } from '@/lib/services/existingDataPersonalizationService';

interface PersonalizationIntegrationExampleProps {
  className?: string;
  onOutfitGenerated?: (outfit: PersonalizedOutfit) => void;
  onError?: (error: string) => void;
}

export default function PersonalizationIntegrationExample({
  className = '',
  onOutfitGenerated,
  onError
}: PersonalizationIntegrationExampleProps) {
  const {
    personalizationStatus,
    isLoading,
    error,
    isReadyForPersonalization,
    hasExistingData,
    totalInteractions,
    topColors,
    topStyles,
    topOccasions,
    favoriteItemsCount,
    mostWornItemsCount,
    generatePersonalizedOutfit,
    refreshPersonalizationData
  } = useExistingDataPersonalization();

  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<PersonalizedOutfit | null>(null);

  const handleGeneratePersonalizedOutfit = async () => {
    try {
      setGenerating(true);
      
      const outfit = await generatePersonalizedOutfit({
        occasion: 'Business',
        style: 'Classic',
        mood: 'Confident',
        weather: {
          temperature: 72,
          condition: 'Clear',
          humidity: 50,
          wind_speed: 5,
          location: 'Current Location'
        }
      });

      if (outfit) {
        setGeneratedOutfit(outfit);
        onOutfitGenerated?.(outfit);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate outfit';
      onError?.(errorMessage);
    } finally {
      setGenerating(false);
    }
  };

  const handleRefreshData = async () => {
    await refreshPersonalizationData();
  };

  return (
    <div className={className}>
      {/* Personalization Status Card */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Personalization Status
            {isReadyForPersonalization ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            )}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Status Overview */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
              <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                {totalInteractions}
              </div>
              <div className="text-sm text-blue-600 dark:text-blue-400">Interactions</div>
            </div>
            
            <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <div className="text-xl font-bold text-green-600 dark:text-green-400">
                {favoriteItemsCount + mostWornItemsCount}
              </div>
              <div className="text-sm text-green-600 dark:text-green-400">Engaged Items</div>
            </div>
          </div>

          {/* Readiness Status */}
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <span className="font-medium">Personalization Ready</span>
            <Badge variant={isReadyForPersonalization ? "default" : "secondary"}>
              {isReadyForPersonalization ? "Yes" : "Not Yet"}
            </Badge>
          </div>

          {/* Data Status */}
          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <span className="font-medium">Has Existing Data</span>
            <Badge variant={hasExistingData ? "default" : "secondary"}>
              {hasExistingData ? "Yes" : "No"}
            </Badge>
          </div>

          {/* Top Preferences */}
          {topColors.length > 0 && (
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">Your Top Colors</div>
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
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-2">Your Top Styles</div>
              <div className="flex flex-wrap gap-1">
                {topStyles.slice(0, 5).map((style, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {style}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2">
            <Button 
              onClick={handleRefreshData}
              variant="outline" 
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh Data
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Enhanced Generation Button */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-500" />
            Generate Personalized Outfit
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg mb-4">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-red-600">Error: {error}</span>
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
            onClick={handleGeneratePersonalizedOutfit}
            disabled={generating || isLoading}
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
                <div className="text-sm font-medium text-muted-foreground mb-2">
                  Items ({generatedOutfit.items.length})
                </div>
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
                <Button variant="outline" size="sm">
                  <Heart className="h-4 w-4 mr-2" />
                  Save Outfit
                </Button>
                <Button variant="outline" size="sm">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Integration Info */}
      <Card className="mt-6 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
        <CardContent className="p-4">
          <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
            🎯 Personalization Integration
          </h3>
          <div className="text-sm text-blue-700 dark:text-blue-300">
            <p className="mb-2">This component demonstrates how to integrate the existing data personalization system:</p>
            <ul className="space-y-1 text-xs">
              <li>• Uses your existing Firebase data (favorites, wears, style profiles)</li>
              <li>• No data duplication - leverages existing collections</li>
              <li>• Shows personalization status and user preferences</li>
              <li>• Generates personalized outfits based on real behavior</li>
              <li>• Includes error handling and loading states</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
