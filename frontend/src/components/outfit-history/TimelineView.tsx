"use client";

import { useState, useMemo } from 'react';
import { SearchIcon, FilterIcon, CalendarIcon, CloudIcon, HeartIcon } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
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

interface TimelineViewProps {
  outfitHistory: OutfitHistoryEntry[];
  onEntrySelect: (entry: OutfitHistoryEntry) => void;
  onUpdateEntry: (entryId: string, updates: Partial<OutfitHistoryEntry>) => void;
  onDeleteEntry: (entryId: string) => void;
}

export function TimelineView({
  outfitHistory,
  onEntrySelect,
  onUpdateEntry,
  onDeleteEntry,
}: TimelineViewProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [occasionFilter, setOccasionFilter] = useState<string>('all');
  const [moodFilter, setMoodFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'occasion' | 'mood'>('date');

  // Get unique occasions and moods for filters
  const occasions = useMemo(() => {
    const unique = [...new Set(outfitHistory.map(entry => entry.occasion))];
    return unique.sort();
  }, [outfitHistory]);

  const moods = useMemo(() => {
    const unique = [...new Set(outfitHistory.map(entry => entry.mood))];
    return unique.sort();
  }, [outfitHistory]);

  // Filter and sort outfit history
  const filteredHistory = useMemo(() => {
    let filtered = outfitHistory.filter(entry => {
      const matchesSearch = entry.outfitName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           entry.notes.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           entry.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
      
      const matchesOccasion = occasionFilter === 'all' || entry.occasion === occasionFilter;
      const matchesMood = moodFilter === 'all' || entry.mood === moodFilter;
      
      return matchesSearch && matchesOccasion && matchesMood;
    });

    // Sort the filtered results
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.dateWorn).getTime() - new Date(a.dateWorn).getTime();
        case 'occasion':
          return a.occasion.localeCompare(b.occasion);
        case 'mood':
          return a.mood.localeCompare(b.mood);
        default:
          return 0;
      }
    });

    return filtered;
  }, [outfitHistory, searchTerm, occasionFilter, moodFilter, sortBy]);

  // Group by date for timeline display
  const groupedHistory = useMemo(() => {
    const grouped: Record<string, OutfitHistoryEntry[]> = {};
    
    filteredHistory.forEach(entry => {
      const dateKey = new Date(entry.dateWorn).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      });
      
      if (!grouped[dateKey]) {
        grouped[dateKey] = [];
      }
      grouped[dateKey].push(entry);
    });

    return grouped;
  }, [filteredHistory]);

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

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const clearFilters = () => {
    setSearchTerm('');
    setOccasionFilter('all');
    setMoodFilter('all');
    setSortBy('date');
  };

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <Card className="p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search outfits, notes, or tags..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Filters */}
          <div className="flex gap-2">
            <Select value={occasionFilter} onValueChange={setOccasionFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Occasion" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Occasions</SelectItem>
                {occasions.map(occasion => (
                  <SelectItem key={occasion} value={occasion}>
                    {occasion}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={moodFilter} onValueChange={setMoodFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Mood" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Moods</SelectItem>
                {moods.map(mood => (
                  <SelectItem key={mood} value={mood}>
                    {mood}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="date">Sort by Date</SelectItem>
                <SelectItem value="occasion">Sort by Occasion</SelectItem>
                <SelectItem value="mood">Sort by Mood</SelectItem>
              </SelectContent>
            </Select>

            <Button variant="outline" size="sm" onClick={clearFilters}>
              Clear
            </Button>
          </div>
        </div>

        {/* Active Filters Display */}
        {(searchTerm || occasionFilter !== 'all' || moodFilter !== 'all') && (
          <div className="flex items-center gap-2 mt-3 pt-3 border-t">
            <FilterIcon className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Active filters:</span>
            {searchTerm && (
              <Badge variant="secondary" className="text-xs">
                Search: "{searchTerm}"
              </Badge>
            )}
            {occasionFilter !== 'all' && (
              <Badge variant="secondary" className="text-xs">
                Occasion: {occasionFilter}
              </Badge>
            )}
            {moodFilter !== 'all' && (
              <Badge variant="outline" className="text-xs">
                Mood: {moodFilter}
              </Badge>
            )}
          </div>
        )}
      </Card>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Showing {filteredHistory.length} of {outfitHistory.length} entries
        </p>
      </div>

      {/* Timeline */}
      <div className="space-y-6">
        {Object.keys(groupedHistory).length === 0 ? (
          <Card className="p-8">
            <div className="text-center text-muted-foreground">
              <CalendarIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <h3 className="text-lg font-semibold mb-2">No entries found</h3>
              <p>Try adjusting your search or filters</p>
            </div>
          </Card>
        ) : (
          Object.entries(groupedHistory).map(([date, entries]) => (
            <div key={date} className="space-y-4">
              {/* Date Header */}
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-primary rounded-full"></div>
                <h3 className="font-semibold text-lg">{date}</h3>
                <Badge variant="secondary">{entries.length} outfit{entries.length !== 1 ? 's' : ''}</Badge>
              </div>

              {/* Entries for this date */}
              <div className="ml-6 space-y-3">
                {entries.map((entry, index) => (
                  <Card
                    key={entry.id}
                    className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => onEntrySelect(entry)}
                  >
                    <div className="flex gap-4">
                      {/* Outfit Image */}
                      <div className="flex-shrink-0">
                        {entry.outfitImage && (
                          <img
                            src={entry.outfitImage}
                            alt={entry.outfitName}
                            className="w-16 h-16 rounded-lg object-cover"
                          />
                        )}
                      </div>

                      {/* Entry Details */}
                      <div className="flex-1 space-y-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold">{entry.outfitName}</h4>
                            <p className="text-sm text-muted-foreground">
                              {formatTime(entry.dateWorn)}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            {entry.weather && (
                              <div className="flex items-center gap-1 text-sm">
                                <span>{getWeatherIcon(entry.weather.condition)}</span>
                                <span>{entry.weather.temperature}°F</span>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">{entry.occasion}</Badge>
                          <Badge variant="outline">{entry.mood}</Badge>
                        </div>

                        {entry.notes && (
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {entry.notes}
                          </p>
                        )}

                        {entry.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                                                         {entry.tags.slice(0, 3).map(tag => (
                               <Badge key={tag} variant="outline" className="text-xs">
                                 {tag}
                               </Badge>
                             ))}
                             {entry.tags.length > 3 && (
                               <Badge variant="outline" className="text-xs">
                                 +{entry.tags.length - 3} more
                               </Badge>
                             )}
                          </div>
                        )}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
} 