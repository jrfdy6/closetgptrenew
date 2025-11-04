/**
 * PersonalizationStatusCard Component
 * ===================================
 * 
 * Displays the user's personalization status based on existing Firebase data.
 * Shows preferences, interaction counts, and readiness for personalization.
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Brain, 
  Heart, 
  TrendingUp, 
  Palette, 
  Shirt, 
  Calendar,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import { useExistingDataPersonalization } from '@/lib/hooks/useExistingDataPersonalization';

interface PersonalizationStatusCardProps {
  className?: string;
  showRefreshButton?: boolean;
  compact?: boolean;
}

export default function PersonalizationStatusCard({ 
  className = '', 
  showRefreshButton = true,
  compact = false 
}: PersonalizationStatusCardProps) {
  const {
    personalizationStatus,
    userPreferences,
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
    refreshPersonalizationData,
    dataSource,
    usesExistingData
  } = useExistingDataPersonalization();

  const handleRefresh = async () => {
    await refreshPersonalizationData();
  };

  if (isLoading && !personalizationStatus) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">Loading personalization data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            Personalization Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 mb-4">{error}</p>
          {showRefreshButton && (
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  if (!personalizationStatus) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-center justify-center">
            <Info className="h-6 w-6 text-muted-foreground" />
            <span className="ml-2 text-muted-foreground">No personalization data available</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-blue-500" />
            Personalization Status
            {isReadyForPersonalization ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertCircle className="h-4 w-4 text-yellow-500" />
            )}
          </CardTitle>
          {showRefreshButton && (
            <Button 
              onClick={handleRefresh} 
              variant="ghost" 
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Status Overview */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
              {totalInteractions}
            </div>
            <div className="text-sm text-amber-600 dark:text-amber-400">Total Interactions</div>
          </div>
          
          <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">
              {favoriteItemsCount + mostWornItemsCount}
            </div>
            <div className="text-sm text-amber-600 dark:text-amber-400">Engaged Items</div>
          </div>
        </div>

        {/* Readiness Status */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <span className="font-medium">Personalization Ready</span>
          <Badge variant={isReadyForPersonalization ? "default" : "secondary"}>
            {isReadyForPersonalization ? "Yes" : "Not Yet"}
          </Badge>
        </div>

        {/* Data Source */}
        <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <span className="font-medium">Data Source</span>
          <Badge variant="outline">
            {usesExistingData ? "Existing Firebase Data" : "Unknown"}
          </Badge>
        </div>

        {!compact && (
          <>
            {/* Top Preferences */}
            {topColors.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Palette className="h-4 w-4 text-purple-500" />
                  <span className="font-medium">Top Colors</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {topColors.map((color, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {color}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {topStyles.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Shirt className="h-4 w-4 text-blue-500" />
                  <span className="font-medium">Top Styles</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {topStyles.map((style, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {style}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {topOccasions.length > 0 && (
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="h-4 w-4 text-green-500" />
                  <span className="font-medium">Top Occasions</span>
                </div>
                <div className="flex flex-wrap gap-1">
                  {topOccasions.map((occasion, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {occasion}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {/* Detailed Stats */}
            <div className="grid grid-cols-2 gap-4 pt-4 border-t">
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <Heart className="h-4 w-4 text-red-500" />
                  <span className="text-sm font-medium">Favorites</span>
                </div>
                <div className="text-lg font-bold">{favoriteItemsCount}</div>
              </div>
              
              <div className="text-center">
                <div className="flex items-center justify-center gap-1 mb-1">
                  <TrendingUp className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium">Most Worn</span>
                </div>
                <div className="text-lg font-bold">{mostWornItemsCount}</div>
              </div>
            </div>
          </>
        )}

        {/* System Info */}
        <div className="text-xs text-muted-foreground pt-2 border-t">
          <div>Data Source: {dataSource}</div>
          <div>Uses Existing Data: {usesExistingData ? "Yes" : "No"}</div>
          <div>Min Interactions Required: {personalizationStatus.min_interactions_required}</div>
        </div>
      </CardContent>
    </Card>
  );
}
