"use client";

import { useState, useMemo } from 'react';
import { ChevronLeftIcon, ChevronRightIcon, PlusIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

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

interface CalendarProps {
  outfitHistory: OutfitHistoryEntry[];
  selectedDate: Date;
  onDateSelect: (date: Date) => void;
  onEntrySelect: (entry: OutfitHistoryEntry) => void;
  onMarkAsWorn: (outfitId: string, date: string) => void;
}

export function Calendar({
  outfitHistory,
  selectedDate,
  onDateSelect,
  onEntrySelect,
  onMarkAsWorn,
}: CalendarProps) {
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // Generate calendar days
  const calendarDays = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());
    
    const days = [];
    const currentDate = new Date(startDate);
    
    while (currentDate <= lastDay || days.length < 42) {
      days.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    return days;
  }, [currentMonth]);

  // Group outfit history by date
  const outfitHistoryByDate = useMemo(() => {
    const grouped: Record<string, OutfitHistoryEntry[]> = {};
    outfitHistory.forEach(entry => {
      const dateKey = new Date(entry.dateWorn).toISOString().split('T')[0];
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(entry);
    });
    return grouped;
  }, [outfitHistory]);

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentMonth(prev => {
      const newMonth = new Date(prev);
      if (direction === 'prev') {
        newMonth.setMonth(newMonth.getMonth() - 1);
      } else {
        newMonth.setMonth(newMonth.getMonth() + 1);
      }
      return newMonth;
    });
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  const isCurrentMonth = (date: Date) => {
    return date.getMonth() === currentMonth.getMonth();
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

  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
  };

  return (
    <div className="space-y-6">
      {/* Calendar Header */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigateMonth('prev')}
        >
          <ChevronLeftIcon className="h-4 w-4" />
        </Button>
        
        <h2 className="text-xl font-semibold">{formatDate(currentMonth)}</h2>
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigateMonth('next')}
        >
          <ChevronRightIcon className="h-4 w-4" />
        </Button>
      </div>

      {/* Calendar Grid */}
      <Card className="p-6">
        {/* Day Headers */}
        <div className="grid grid-cols-7 gap-1 mb-4">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
              {day}
            </div>
          ))}
        </div>

        {/* Calendar Days */}
        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map((date, index) => {
            const dateKey = date.toISOString().split('T')[0];
            const dayOutfits = outfitHistoryByDate[dateKey] || [];
            const isSelected = selectedDate.toDateString() === date.toDateString();

            return (
              <div
                key={index}
                className={cn(
                  "min-h-[120px] p-2 border rounded-lg cursor-pointer transition-colors",
                  isCurrentMonth(date) ? "bg-background" : "bg-muted/30",
                  isToday(date) && "ring-2 ring-primary",
                  isSelected && "ring-2 ring-primary ring-offset-2",
                  "hover:bg-muted/50"
                )}
                onClick={() => onDateSelect(date)}
              >
                {/* Date Number */}
                <div className={cn(
                  "text-sm font-medium mb-1",
                  isCurrentMonth(date) ? "text-foreground" : "text-muted-foreground",
                  isToday(date) && "text-primary font-bold"
                )}>
                  {date.getDate()}
                </div>

                {/* Outfit Thumbnails */}
                <div className="space-y-1">
                  {dayOutfits.slice(0, 2).map((outfit, outfitIndex) => (
                    <div
                      key={outfit.id}
                      className="flex items-center gap-1 p-1 bg-primary/10 rounded text-xs"
                      onClick={(e) => {
                        e.stopPropagation();
                        onEntrySelect(outfit);
                      }}
                    >
                      {outfit.outfitImage && (
                        <img
                          src={outfit.outfitImage}
                          alt={outfit.outfitName}
                          className="w-4 h-4 rounded object-cover"
                        />
                      )}
                      <span className="truncate flex-1">{outfit.outfitName}</span>
                      {outfit.weather && (
                        <span className="text-xs">
                          {getWeatherIcon(outfit.weather.condition)}
                        </span>
                      )}
                    </div>
                  ))}
                  
                  {dayOutfits.length > 2 && (
                    <div className="text-xs text-muted-foreground text-center">
                      +{dayOutfits.length - 2} more
                    </div>
                  )}
                </div>

                {/* Quick Add Button for Today */}
                {isToday(date) && dayOutfits.length === 0 && (
                  <Button
                    size="sm"
                    variant="ghost"
                    className="w-full h-6 mt-1 text-xs"
                    onClick={(e) => {
                      e.stopPropagation();
                      // TODO: Open outfit selector modal
                    }}
                  >
                    <PlusIcon className="h-3 w-3 mr-1" />
                    Add
                  </Button>
                )}
              </div>
            );
          })}
        </div>
      </Card>

      {/* Selected Date Info */}
      {selectedDate && (
        <Card className="p-4">
          <h3 className="font-semibold mb-2">
            {selectedDate.toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })}
          </h3>
          
          {outfitHistoryByDate[selectedDate.toISOString().split('T')[0]] ? (
            <div className="space-y-2">
              {outfitHistoryByDate[selectedDate.toISOString().split('T')[0]].map(outfit => (
                <div
                  key={outfit.id}
                  className="flex items-center gap-3 p-2 border rounded-lg cursor-pointer hover:bg-muted/50"
                  onClick={() => onEntrySelect(outfit)}
                >
                  {outfit.outfitImage && (
                    <img
                      src={outfit.outfitImage}
                      alt={outfit.outfitName}
                      className="w-12 h-12 rounded object-cover"
                    />
                  )}
                  <div className="flex-1">
                    <div className="font-medium">{outfit.outfitName}</div>
                    <div className="text-sm text-muted-foreground">
                      {outfit.occasion} • {outfit.mood}
                    </div>
                  </div>
                  <div className="text-right">
                    {outfit.weather && (
                      <div className="text-sm">
                        {getWeatherIcon(outfit.weather.condition)} {outfit.weather.temperature}°F
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-muted-foreground text-center py-4">
              No outfits recorded for this date
            </div>
          )}
        </Card>
      )}
    </div>
  );
} 