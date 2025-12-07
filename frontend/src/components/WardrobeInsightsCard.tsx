"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  TrendingUp, 
  TrendingDown,
  Calendar, 
  Palette, 
  Shirt, 
  AlertCircle,
  Sparkles,
  Clock,
  Target,
  BarChart3,
  ChevronRight
} from "lucide-react";

interface WardrobeInsightsProps {
  userId: string;
  wardrobeData?: {
    totalItems: number;
    wornThisWeek: number;
    outfitsCreated: number;
    topStyles: { name: string; count: number }[];
    topColors: { name: string; count: number }[];
    underutilizedItems: number;
  };
}

interface WeeklySummary {
  outfitsWorn: number;
  itemsWorn: number;
  outfitsCreated: number;
  mostWornItem: { name: string; count: number } | null;
  trend: 'up' | 'down' | 'stable';
  trendPercentage: number;
}

export default function WardrobeInsightsCard({ userId, wardrobeData }: WardrobeInsightsProps) {
  const [weeklySummary, setWeeklySummary] = useState<WeeklySummary | null>(null);
  const [utilizationRate, setUtilizationRate] = useState(0);

  useEffect(() => {
    if (wardrobeData) {
      // Calculate utilization rate
      const rate = wardrobeData.totalItems > 0 
        ? (wardrobeData.wornThisWeek / wardrobeData.totalItems) * 100 
        : 0;
      setUtilizationRate(Math.round(rate));

      // Mock weekly summary (in production, fetch from API)
      setWeeklySummary({
        outfitsWorn: wardrobeData.wornThisWeek,
        itemsWorn: Math.round(wardrobeData.wornThisWeek * 0.6),
        outfitsCreated: wardrobeData.outfitsCreated,
        mostWornItem: wardrobeData.topStyles[0] 
          ? { name: wardrobeData.topStyles[0].name, count: wardrobeData.topStyles[0].count }
          : null,
        trend: wardrobeData.wornThisWeek > 3 ? 'up' : wardrobeData.wornThisWeek < 2 ? 'down' : 'stable',
        trendPercentage: 15
      });
    }
  }, [wardrobeData]);

  if (!wardrobeData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Wardrobe Insights</CardTitle>
          <CardDescription>Loading your wardrobe insights...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getUtilizationColor = (rate: number) => {
    if (rate >= 70) return "text-green-600 dark:text-green-400";
    if (rate >= 40) return "text-yellow-600 dark:text-yellow-400";
    return "text-red-600 dark:text-red-400";
  };

  const getUtilizationMessage = (rate: number) => {
    if (rate >= 70) return "Excellent! You're maximizing your wardrobe.";
    if (rate >= 40) return "Good progress! Keep exploring your wardrobe.";
    return "Let's unlock more outfit potential!";
  };

  return (
    <Card className="border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60 bg-white/85 dark:bg-[#1A1A1A]/85">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2 text-[#1C1917] dark:text-[#F8F5F1]">
              <Sparkles className="h-5 w-5 text-[#C9956F] dark:text-[#D4A574]" />
              Wardrobe Insights
            </CardTitle>
            <CardDescription className="text-[#57534E] dark:text-[#C4BCB4]">Your style activity this week</CardDescription>
          </div>
          {weeklySummary && weeklySummary.trend === 'up' && (
            <Badge variant="secondary" className="bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300">
              <TrendingUp className="h-3 w-3 mr-1" />
              +{weeklySummary.trendPercentage}%
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Weekly Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-[#E8C8A0]/35 to-[#C9956F]/35 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60">
            <div className="flex items-center gap-2 mb-2">
              <Shirt className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              <p className="text-xs font-medium text-[#57534E] dark:text-[#C4BCB4]">Outfits Worn</p>
            </div>
            <p className="text-2xl font-bold text-[#1C1917] dark:text-[#F8F5F1]">
              {weeklySummary?.outfitsWorn || 0}
            </p>
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">this week</p>
          </div>

          <div className="bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60">
            <div className="flex items-center gap-2 mb-2">
              <Target className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              <p className="text-xs font-medium text-[#57534E] dark:text-[#C4BCB4]">Items Used</p>
            </div>
            <p className="text-2xl font-bold text-[#1C1917] dark:text-[#F8F5F1]">
              {weeklySummary?.itemsWorn || 0}
            </p>
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">unique items</p>
          </div>

          <div className="bg-gradient-to-br from-[#DDB896]/40 to-[#D4A574]/35 dark:from-[#E8C8A0]/25 dark:to-[#D4A574]/20 rounded-lg p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              <p className="text-xs font-medium text-[#57534E] dark:text-[#C4BCB4]">Created</p>
            </div>
            <p className="text-2xl font-bold text-[#1C1917] dark:text-[#F8F5F1]">
              {weeklySummary?.outfitsCreated || 0}
            </p>
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">new outfits</p>
          </div>

          <div className="bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-lg p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              <p className="text-xs font-medium text-[#57534E] dark:text-[#C4BCB4]">Utilization</p>
            </div>
            <p className={`text-2xl font-bold ${getUtilizationColor(utilizationRate)}`}>
              {utilizationRate}%
            </p>
            <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-1">of wardrobe</p>
          </div>
        </div>

        {/* Wardrobe Utilization Progress */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
              Wardrobe Utilization
            </h3>
            <span className={`text-sm font-medium ${getUtilizationColor(utilizationRate)}`}>
              {utilizationRate}%
            </span>
          </div>
          <Progress 
            value={utilizationRate} 
            className="h-2"
          />
          <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
            {getUtilizationMessage(utilizationRate)}
          </p>
        </div>

        {/* Most Worn Item */}
        {weeklySummary?.mostWornItem && (
          <div className="bg-[#F5F0E8]/30 dark:bg-[#262626]/30 rounded-lg p-4 border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/60">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4] mb-1">
                  Most Worn Style
                </p>
                <p className="text-lg font-semibold text-[#1C1917] dark:text-[#F8F5F1]">
                  {weeklySummary.mostWornItem.name}
                </p>
              </div>
              <Badge variant="secondary" className="text-lg px-3 py-1 bg-[#D4A574]/20 dark:bg-[#C9956F]/20 text-[#C9956F] dark:text-[#D4A574]">
                {weeklySummary.mostWornItem.count}×
              </Badge>
            </div>
          </div>
        )}

        {/* Style Insights */}
        {wardrobeData.topStyles && wardrobeData.topStyles.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-[#1C1917] dark:text-[#F8F5F1] flex items-center gap-2">
              <Palette className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              Your Go-To Styles
            </h3>
            <div className="space-y-2">
              {wardrobeData.topStyles.slice(0, 3).map((style, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div 
                      className={`h-2 w-2 rounded-full ${
                        index === 0 ? 'bg-[#C9956F] dark:bg-[#D4A574]' : 
                        index === 1 ? 'bg-[#D4A574] dark:bg-[#E8C8A0]' : 
                        'bg-[#E8C8A0] dark:bg-[#DDB896]'
                      }`}
                    />
                    <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                      {style.name}
                    </span>
                  </div>
                  <span className="text-sm font-medium text-[#1C1917] dark:text-[#F8F5F1]">
                    {style.count}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Color Analysis */}
        {wardrobeData.topColors && wardrobeData.topColors.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-[#1C1917] dark:text-[#F8F5F1] flex items-center gap-2">
              <Palette className="h-4 w-4 text-[#C9956F] dark:text-[#D4A574]" />
              Color Palette
            </h3>
            <div className="flex gap-2">
              {wardrobeData.topColors.slice(0, 5).map((color, index) => (
                <div 
                  key={index}
                  className="flex-1 text-center"
                >
                  <div 
                    className="h-12 rounded-lg mb-2 border-2 border-[#F5F0E8] dark:border-[#2E2E2E]"
                    style={{ backgroundColor: color.name.toLowerCase() }}
                    title={color.name}
                  />
                  <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] truncate">
                    {color.count}%
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actionable Insights */}
        {wardrobeData.underutilizedItems > 0 && (
          <div className="bg-[#DDB896]/20 dark:bg-[#D4A574]/10 border border-[#D4A574]/30 dark:border-[#C9956F]/30 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-[#C9956F] dark:text-[#D4A574] flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-medium text-[#1C1917] dark:text-[#F8F5F1] mb-1">
                  You have {wardrobeData.underutilizedItems} items not worn recently
                </p>
                <p className="text-xs text-[#57534E] dark:text-[#C4BCB4] mb-3">
                  Let's create some outfits with your forgotten gems!
                </p>
                <Button 
                  size="sm" 
                  variant="outline"
                  className="text-xs border-[#F5F0E8]/70 dark:border-[#2E2E2E]/80 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119]"
                >
                  View Forgotten Items
                  <ChevronRight className="h-3 w-3 ml-1" />
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

