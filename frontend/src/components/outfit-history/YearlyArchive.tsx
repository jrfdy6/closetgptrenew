"use client";

import { useState, useMemo } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, CalendarIcon, BarChart3Icon, TrendingUpIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

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

interface YearlyArchiveProps {
  outfitHistory: OutfitHistoryEntry[];
  onEntrySelect: (entry: OutfitHistoryEntry) => void;
  onUpdateEntry: (entryId: string, updates: Partial<OutfitHistoryEntry>) => void;
  onDeleteEntry: (entryId: string) => void;
}

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export function YearlyArchive({
  outfitHistory,
  onEntrySelect,
  onUpdateEntry,
  onDeleteEntry,
}: YearlyArchiveProps) {
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Get available years from outfit history
  const availableYears = useMemo(() => {
    const years = new Set(outfitHistory.map(entry => new Date(entry.dateWorn).getFullYear()));
    return Array.from(years).sort((a, b) => b - a);
  }, [outfitHistory]);

  // Group outfit history by year and month
  const yearlyData = useMemo(() => {
    const grouped: Record<number, Record<number, OutfitHistoryEntry[]>> = {};
    
    outfitHistory.forEach(entry => {
      const date = new Date(entry.dateWorn);
      const year = date.getFullYear();
      const month = date.getMonth();
      
      if (!grouped[year]) {
        grouped[year] = {};
      }
      if (!grouped[year][month]) {
        grouped[year][month] = [];
      }
      grouped[year][month].push(entry);
    });

    return grouped;
  }, [outfitHistory]);

  // Get year statistics
  const yearStats = useMemo(() => {
    const yearEntries = yearlyData[selectedYear] || {};
    const allYearEntries = Object.values(yearEntries).flat();
    
    if (allYearEntries.length === 0) {
      return {
        totalEntries: 0,
        uniqueOutfits: 0,
        topOccasions: [],
        topMoods: [],
        averageTemperature: 0,
        mostActiveMonth: null,
        totalDays: 0,
      };
    }

    // Count unique outfits
    const uniqueOutfits = new Set(allYearEntries.map(entry => entry.outfitId)).size;

    // Count occasions and moods
    const occasionCounts: Record<string, number> = {};
    const moodCounts: Record<string, number> = {};
    const temperatures: number[] = [];

    allYearEntries.forEach(entry => {
      occasionCounts[entry.occasion] = (occasionCounts[entry.occasion] || 0) + 1;
      moodCounts[entry.mood] = (moodCounts[entry.mood] || 0) + 1;
      if (entry.weather) {
        temperatures.push(entry.weather.temperature);
      }
    });

    // Find most active month
    const monthCounts = Object.entries(yearEntries).map(([month, entries]) => ({
      month: parseInt(month),
      count: entries.length,
    }));
    const mostActiveMonth = monthCounts.reduce((a, b) => a.count > b.count ? a : b);

    // Count unique days
    const uniqueDays = new Set(allYearEntries.map(entry => 
      new Date(entry.dateWorn).toDateString()
    )).size;

    return {
      totalEntries: allYearEntries.length,
      uniqueOutfits,
      topOccasions: Object.entries(occasionCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3)
        .map(([occasion, count]) => ({ occasion, count })),
      topMoods: Object.entries(moodCounts)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 3)
        .map(([mood, count]) => ({ mood, count })),
      averageTemperature: temperatures.length > 0 
        ? Math.round(temperatures.reduce((a, b) => a + b, 0) / temperatures.length)
        : 0,
      mostActiveMonth: mostActiveMonth ? MONTHS[mostActiveMonth.month] : null,
      totalDays: uniqueDays,
    };
  }, [yearlyData, selectedYear]);

  const navigateYear = (direction: 'prev' | 'next') => {
    const currentIndex = availableYears.indexOf(selectedYear);
    if (direction === 'prev' && currentIndex < availableYears.length - 1) {
      setSelectedYear(availableYears[currentIndex + 1]);
    } else if (direction === 'next' && currentIndex > 0) {
      setSelectedYear(availableYears[currentIndex - 1]);
    }
  };

  const getWeatherIcon = (condition: string) => {
    const weatherIcons: Record<string, string> = {
      'Clear': '☀️',
      'Clouds': '☁️',
      'Rain': '🌧️',
      'Snow': '❄️',
      'Thunderstorm': '⛈️',
      'Drizzle': '🌦️',
      'Mist': '🌫️',
      'Fog': '🌫️',
      'Haze': '🌫️',
    };
    return weatherIcons[condition] || '🌤️';
  };

  return (
    <div className="space-y-6">
      {/* Year Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateYear('prev')}
            disabled={availableYears.indexOf(selectedYear) >= availableYears.length - 1}
          >
            <ChevronLeftIcon className="h-4 w-4" />
          </Button>
          
          <Select value={selectedYear.toString()} onValueChange={(value) => setSelectedYear(parseInt(value))}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {availableYears.map(year => (
                <SelectItem key={year} value={year.toString()}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigateYear('next')}
            disabled={availableYears.indexOf(selectedYear) <= 0}
          >
            <ChevronRightIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Year Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Entries</p>
              <p className="text-2xl font-bold">{yearStats.totalEntries}</p>
            </div>
            <CalendarIcon className="h-8 w-8 text-primary" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Unique Outfits</p>
              <p className="text-2xl font-bold">{yearStats.uniqueOutfits}</p>
            </div>
            <BarChart3Icon className="h-8 w-8 text-primary" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Days Worn</p>
              <p className="text-2xl font-bold">{yearStats.totalDays}</p>
            </div>
            <TrendingUpIcon className="h-8 w-8 text-primary" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Avg Temperature</p>
              <p className="text-2xl font-bold">{yearStats.averageTemperature}°F</p>
            </div>
            <div className="text-2xl">🌡️</div>
          </div>
        </Card>
      </div>

      {/* Year Insights */}
      {yearStats.totalEntries > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4">
            <h3 className="font-semibold mb-3">Top Occasions</h3>
            <div className="space-y-2">
              {yearStats.topOccasions.map(({ occasion, count }) => (
                <div key={occasion} className="flex items-center justify-between">
                  <span className="text-sm">{occasion}</span>
                  <Badge variant="secondary">{count}</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-3">Top Moods</h3>
            <div className="space-y-2">
              {yearStats.topMoods.map(({ mood, count }) => (
                <div key={mood} className="flex items-center justify-between">
                  <span className="text-sm">{mood}</span>
                  <Badge variant="outline">{count}</Badge>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="font-semibold mb-3">Insights</h3>
            <div className="space-y-2 text-sm">
              {yearStats.mostActiveMonth && (
                <div>
                  <span className="text-muted-foreground">Most Active Month:</span>
                  <span className="ml-2 font-medium">{yearStats.mostActiveMonth}</span>
                </div>
              )}
              <div>
                <span className="text-muted-foreground">Average Entries/Month:</span>
                <span className="ml-2 font-medium">
                  {Math.round(yearStats.totalEntries / 12)}
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Wear Rate:</span>
                <span className="ml-2 font-medium">
                  {Math.round((yearStats.totalDays / 365) * 100)}%
                </span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Monthly Breakdown */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold">Monthly Breakdown</h2>
        
        {yearStats.totalEntries === 0 ? (
          <Card className="p-8">
            <div className="text-center text-muted-foreground">
              <CalendarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No entries for {selectedYear}</h3>
              <p>Select a different year or start tracking your outfits</p>
            </div>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {MONTHS.map((month, monthIndex) => {
              const monthEntries = yearlyData[selectedYear]?.[monthIndex] || [];
              const isCurrentMonth = new Date().getFullYear() === selectedYear && 
                                   new Date().getMonth() === monthIndex;

              return (
                <Card
                  key={month}
                  className={`p-4 ${isCurrentMonth ? 'ring-2 ring-primary' : ''}`}
                >
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">{month}</h3>
                    <Badge variant="secondary">{monthEntries.length}</Badge>
                  </div>

                  {monthEntries.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No entries</p>
                  ) : (
                    <div className="space-y-2">
                      {monthEntries.slice(0, 3).map(entry => (
                        <div
                          key={entry.id}
                          className="flex items-center gap-2 p-2 bg-muted/30 rounded cursor-pointer hover:bg-muted/50"
                          onClick={() => onEntrySelect(entry)}
                        >
                          {entry.outfitImage && (
                            <img
                              src={entry.outfitImage}
                              alt={entry.outfitName}
                              className="w-8 h-8 rounded object-cover"
                            />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium truncate">{entry.outfitName}</p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(entry.dateWorn).getDate()}
                            </p>
                          </div>
                          {entry.weather && (
                            <span className="text-xs">
                              {getWeatherIcon(entry.weather.condition)}
                            </span>
                          )}
                        </div>
                      ))}
                      
                      {monthEntries.length > 3 && (
                        <p className="text-xs text-muted-foreground text-center">
                          +{monthEntries.length - 3} more entries
                        </p>
                      )}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
} 