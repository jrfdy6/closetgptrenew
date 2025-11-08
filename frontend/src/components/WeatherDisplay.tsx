"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { getWeatherIcon, formatWeatherForDisplay, getClothingRecommendations } from "@/lib/weather";
import { useAutoWeather } from "@/hooks/useWeather";
import type { WeatherData } from "@/types/weather";
import { MapPin, RefreshCw, AlertCircle } from "lucide-react";

export function WeatherDisplay() {
  const { weather, loading, error, fetchWeatherByLocation, isStale } = useAutoWeather();
  const [showRecommendations, setShowRecommendations] = useState(false);

  const handleRefresh = async () => {
    await fetchWeatherByLocation();
  };

  const hasWeather = Boolean(weather);

  if (loading && !hasWeather) {
    return (
      <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl font-serif text-stone-900 dark:text-stone-100 flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Current Weather
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-stone-400" />
            <span className="ml-2 text-stone-600 dark:text-stone-400">Loading weather data...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error && !hasWeather) {
    return (
      <Card className="border border-red-200 dark:border-red-800 bg-red-50/50 dark:bg-red-900/20 backdrop-blur-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-xl font-serif text-stone-900 dark:text-stone-100 flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-red-500" />
            Weather Unavailable
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (!hasWeather) {
    return null;
  }

  const formattedWeather = formatWeatherForDisplay(weather);
  const recommendations = getClothingRecommendations(weather);
  const usingFallback = Boolean(weather.fallback);
  const isGreyedOut = isStale;

  return (
    <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm hover:shadow-xl transition-all duration-300">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-serif text-stone-900 dark:text-stone-100 flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Current Weather
          </CardTitle>
          <div className="flex items-center gap-2">
            {usingFallback && (
              <span className="text-xs text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/30 px-2 py-1 rounded-full">
                Fallback Data
              </span>
            )}
            {isStale && (
              <span className="text-xs text-orange-600 dark:text-orange-400 bg-orange-100 dark:bg-orange-900/30 px-2 py-1 rounded-full">
                Outdated
              </span>
            )}
            {loading && (
              <span className="text-xs text-stone-500 dark:text-stone-400 flex items-center gap-1">
                <RefreshCw className="h-3 w-3 animate-spin" />
                Updating
              </span>
            )}
            <Button onClick={handleRefresh} variant="ghost" size="sm" disabled={loading}>
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`space-y-4 transition-all ${isGreyedOut ? 'opacity-60 grayscale' : ''}`}>
          {/* Main Weather Info */}
          <div className="flex items-center justify-between">
            <div>
              <p className="text-3xl font-bold text-stone-900 dark:text-stone-100">
                {formattedWeather.temperature}
              </p>
              <p className="text-lg text-stone-700 dark:text-stone-300">
                {formattedWeather.condition}
              </p>
              <p className="text-sm text-stone-500 dark:text-stone-500">
                {weather.location}
              </p>
            </div>
            <div className="text-right">
              <div className="text-sm text-stone-600 dark:text-stone-400 space-y-1">
                {formattedWeather.details.map((detail, index) => (
                  <p key={index}>{detail}</p>
                ))}
              </div>
            </div>
          </div>

          {/* Weather Recommendations */}
          {recommendations.length > 0 && (
            <div className="border-t border-stone-200 dark:border-stone-700 pt-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowRecommendations(!showRecommendations)}
                className="w-full justify-between text-stone-600 dark:text-stone-400 hover:text-stone-900 dark:hover:text-stone-100"
              >
                <span>Weather Recommendations</span>
                <span className={`transform transition-transform ${showRecommendations ? 'rotate-180' : ''}`}>
                  ▼
                </span>
              </Button>
              
              {showRecommendations && (
                <div className="mt-3 space-y-2">
                  <div className="grid grid-cols-2 gap-2">
                    {recommendations.slice(0, 6).map((rec, index) => (
                      <span
                        key={index}
                        className="text-xs bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 px-2 py-1 rounded-full text-center"
                      >
                        {rec}
                      </span>
                    ))}
                  </div>
                  {error && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-2">
                      Note: Using fallback weather data
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}