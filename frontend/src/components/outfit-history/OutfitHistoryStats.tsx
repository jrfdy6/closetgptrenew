"use client";

import { useMemo } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  CalendarIcon, 
  TrendingUpIcon, 
  StarIcon, 
  CloudIcon,
  HeartIcon,
  ClockIcon,
  BarChart3Icon,
  TargetIcon
} from 'lucide-react';

interface OutfitHistoryEntry {
  id: string;
  outfitId: string;
  outfitName: string;
  outfitImage: string;
  dateWorn: string;
  weather: {
    temperature: number;
    condition: string;
    humidity: number;
  };
  occasion: string;
  mood: string;
  notes: string;
  tags: string[];
  createdAt: string;
  updatedAt: string;
}

interface OutfitHistoryStatsProps {
  outfitHistory: OutfitHistoryEntry[];
}

export function OutfitHistoryStats({ outfitHistory }: OutfitHistoryStatsProps) {
  const stats = useMemo(() => {
    if (!outfitHistory.length) {
      return {
        totalEntries: 0,
        uniqueOutfits: 0,
        mostWornOutfit: null,
        averageWearFrequency: 0,
        topOccasions: [],
        topMoods: [],
        weatherPatterns: [],
        recentActivity: 0,
        streakDays: 0,
        favoriteWeather: null,
      };
    }

    // Count unique outfits and their wear frequency
    const outfitCounts: Record<string, number> = {};
    const occasionCounts: Record<string, number> = {};
    const moodCounts: Record<string, number> = {};
    const weatherCounts: Record<string, number> = {};
    const temperatureRanges: number[] = [];

    outfitHistory.forEach(entry => {
      // Count outfit wear frequency
      outfitCounts[entry.outfitId] = (outfitCounts[entry.outfitId] || 0) + 1;
      
      // Count occasions
      occasionCounts[entry.occasion] = (occasionCounts[entry.occasion] || 0) + 1;
      
      // Count moods
      moodCounts[entry.mood] = (moodCounts[entry.mood] || 0) + 1;
      
      // Count weather patterns
      if (entry.weather) {
        weatherCounts[entry.weather.condition] = (weatherCounts[entry.weather.condition] || 0) + 1;
        temperatureRanges.push(entry.weather.temperature);
      }
    });

    // Find most worn outfit
    const mostWornOutfitId = Object.keys(outfitCounts).reduce((a, b) => 
      outfitCounts[a] > outfitCounts[b] ? a : b
    );
    const mostWornOutfit = outfitHistory.find(entry => entry.outfitId === mostWornOutfitId);

    // Calculate top occasions and moods
    const topOccasions = Object.entries(occasionCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([occasion, count]) => ({ occasion, count }));

    const topMoods = Object.entries(moodCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([mood, count]) => ({ mood, count }));

    // Calculate weather patterns
    const weatherPatterns = Object.entries(weatherCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([condition, count]) => ({ condition, count }));

    // Calculate average temperature
    const avgTemperature = temperatureRanges.length > 0 
      ? temperatureRanges.reduce((a, b) => a + b, 0) / temperatureRanges.length 
      : 0;

    // Calculate recent activity (last 7 days)
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
    const recentActivity = outfitHistory.filter(entry => 
      new Date(entry.dateWorn) >= sevenDaysAgo
    ).length;

    // Calculate streak (consecutive days with outfit entries)
    const sortedDates = outfitHistory
      .map(entry => new Date(entry.dateWorn))
      .sort((a, b) => b.getTime() - a.getTime());

    let streakDays = 0;
    let currentDate = new Date();
    currentDate.setHours(0, 0, 0, 0);

    for (let i = 0; i < 30; i++) {
      const hasEntry = sortedDates.some(date => {
        const entryDate = new Date(date);
        entryDate.setHours(0, 0, 0, 0);
        return entryDate.getTime() === currentDate.getTime();
      });

      if (hasEntry) {
        streakDays++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }

    return {
      totalEntries: outfitHistory.length,
      uniqueOutfits: Object.keys(outfitCounts).length,
      mostWornOutfit,
      averageWearFrequency: outfitHistory.length / Object.keys(outfitCounts).length,
      topOccasions,
      topMoods,
      weatherPatterns,
      recentActivity,
      streakDays,
      favoriteWeather: weatherPatterns[0] || null,
      averageTemperature: Math.round(avgTemperature),
    };
  }, [outfitHistory]);

  if (!outfitHistory.length) {
    return (
      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <CalendarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-semibold mb-2">No Outfit History Yet</h3>
          <p>Start tracking your outfits to see analytics and insights</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Total Entries */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Total Entries</p>
            <p className="text-2xl font-bold">{stats.totalEntries}</p>
          </div>
          <CalendarIcon className="h-8 w-8 text-primary" />
        </div>
      </Card>

      {/* Unique Outfits */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Unique Outfits</p>
            <p className="text-2xl font-bold">{stats.uniqueOutfits}</p>
          </div>
          <StarIcon className="h-8 w-8 text-primary" />
        </div>
      </Card>

      {/* Recent Activity */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Last 7 Days</p>
            <p className="text-2xl font-bold">{stats.recentActivity}</p>
          </div>
          <TrendingUpIcon className="h-8 w-8 text-primary" />
        </div>
      </Card>

      {/* Streak */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground">Current Streak</p>
            <p className="text-2xl font-bold">{stats.streakDays} days</p>
          </div>
          <TargetIcon className="h-8 w-8 text-primary" />
        </div>
      </Card>

      {/* Most Worn Outfit */}
      {stats.mostWornOutfit && (
        <Card className="p-4 md:col-span-2">
          <div className="flex items-center gap-4">
            {stats.mostWornOutfit.outfitImage && (
              <img
                src={stats.mostWornOutfit.outfitImage}
                alt={stats.mostWornOutfit.outfitName}
                className="w-16 h-16 rounded-lg object-cover"
              />
            )}
            <div className="flex-1">
              <p className="text-sm text-muted-foreground">Most Worn Outfit</p>
              <p className="font-semibold">{stats.mostWornOutfit.outfitName}</p>
              <div className="flex items-center gap-4 mt-1">
                <Badge variant="secondary">
                  {outfitHistory.filter(e => e.outfitId === stats.mostWornOutfit?.outfitId).length} times
                </Badge>
                <Badge variant="outline">{stats.mostWornOutfit.occasion}</Badge>
              </div>
            </div>
            <HeartIcon className="h-8 w-8 text-primary" />
          </div>
        </Card>
      )}

      {/* Top Occasions */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3Icon className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Top Occasions</h3>
        </div>
        <div className="space-y-2">
          {stats.topOccasions.map(({ occasion, count }) => (
            <div key={occasion} className="flex items-center justify-between">
              <span className="text-sm">{occasion}</span>
              <Badge variant="secondary">{count}</Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Top Moods */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <HeartIcon className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Top Moods</h3>
        </div>
        <div className="space-y-2">
          {stats.topMoods.map(({ mood, count }) => (
            <div key={mood} className="flex items-center justify-between">
              <span className="text-sm">{mood}</span>
              <Badge variant="outline">{count}</Badge>
            </div>
          ))}
        </div>
      </Card>

      {/* Weather Patterns */}
      <Card className="p-4">
        <div className="flex items-center gap-2 mb-3">
          <CloudIcon className="h-5 w-5 text-primary" />
          <h3 className="font-semibold">Weather Patterns</h3>
        </div>
        <div className="space-y-2">
          {stats.weatherPatterns.map(({ condition, count }) => (
            <div key={condition} className="flex items-center justify-between">
              <span className="text-sm">{condition}</span>
              <Badge variant="secondary">{count}</Badge>
            </div>
          ))}
                     {stats.averageTemperature && stats.averageTemperature > 0 && (
             <div className="pt-2 border-t">
               <span className="text-sm text-muted-foreground">
                 Avg: {stats.averageTemperature}°F
               </span>
             </div>
           )}
        </div>
      </Card>
    </div>
  );
} 