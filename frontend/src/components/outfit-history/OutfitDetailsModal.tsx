"use client";

import { useState } from 'react';
import { XIcon, EditIcon, TrashIcon, SaveIcon, CalendarIcon, MapPinIcon, CloudIcon, HeartIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';

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

interface OutfitDetailsModalProps {
  entry: OutfitHistoryEntry;
  onClose: () => void;
  onUpdate: (entryId: string, updates: Partial<OutfitHistoryEntry>) => void;
  onDelete: (entryId: string) => void;
}

const OCCASIONS = [
  'Casual',
  'Work',
  'Formal',
  'Date Night',
  'Workout',
  'Travel',
  'Special Event',
  'Weekend',
  'Meeting',
  'Party',
];

const MOODS = [
  'Confident',
  'Comfortable',
  'Stylish',
  'Professional',
  'Relaxed',
  'Energetic',
  'Sophisticated',
  'Playful',
  'Serious',
  'Creative',
];

const WEATHER_CONDITIONS = [
  'Clear',
  'Clouds',
  'Rain',
  'Snow',
  'Thunderstorm',
  'Drizzle',
  'Mist',
  'Fog',
  'Haze',
];

export function OutfitDetailsModal({
  entry,
  onClose,
  onUpdate,
  onDelete,
}: OutfitDetailsModalProps) {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [editedEntry, setEditedEntry] = useState<OutfitHistoryEntry>(entry);
  const [newTag, setNewTag] = useState('');

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

  const handleSave = async () => {
    try {
      await onUpdate(entry.id, editedEntry);
      setIsEditing(false);
      toast({
        title: "Success",
        description: "Outfit history updated successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update outfit history",
        variant: "destructive",
      });
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this outfit history entry?')) {
      try {
        await onDelete(entry.id);
        onClose();
        toast({
          title: "Success",
          description: "Outfit history entry deleted",
        });
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to delete outfit history entry",
          variant: "destructive",
        });
      }
    }
  };

  const addTag = () => {
    if (newTag.trim() && !editedEntry.tags.includes(newTag.trim())) {
      setEditedEntry(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()],
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setEditedEntry(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove),
    }));
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-background rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-semibold">Outfit Details</h2>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <Button size="sm" onClick={handleSave}>
                  <SaveIcon className="h-4 w-4 mr-2" />
                  Save
                </Button>
                <Button size="sm" variant="outline" onClick={() => setIsEditing(false)}>
                  Cancel
                </Button>
              </>
            ) : (
              <>
                <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
                  <EditIcon className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button size="sm" variant="outline" onClick={handleDelete}>
                  <TrashIcon className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </>
            )}
            <Button size="sm" variant="ghost" onClick={onClose}>
              <XIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Outfit Image and Basic Info */}
          <div className="flex gap-6">
            <div className="flex-shrink-0">
              {entry.outfitImage && (
                <img
                  src={entry.outfitImage}
                  alt={entry.outfitName}
                  className="w-32 h-32 rounded-lg object-cover"
                />
              )}
            </div>
            <div className="flex-1 space-y-4">
              {isEditing ? (
                <div>
                  <Label htmlFor="outfitName">Outfit Name</Label>
                  <Input
                    id="outfitName"
                    value={editedEntry.outfitName}
                    onChange={(e) => setEditedEntry(prev => ({ ...prev, outfitName: e.target.value }))}
                  />
                </div>
              ) : (
                <h3 className="text-lg font-semibold">{entry.outfitName}</h3>
              )}

              {/* Date */}
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CalendarIcon className="h-4 w-4" />
                {formatDate(entry.dateWorn)}
              </div>

              {/* Weather */}
              {entry.weather && (
                <div className="flex items-center gap-2 text-sm">
                  <CloudIcon className="h-4 w-4" />
                  <span>{getWeatherIcon(entry.weather.condition)}</span>
                  <span>{entry.weather.temperature}°F</span>
                  <span>•</span>
                  <span>{entry.weather.humidity}% humidity</span>
                </div>
              )}
            </div>
          </div>

          {/* Occasion and Mood */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label>Occasion</Label>
              {isEditing ? (
                <Select
                  value={editedEntry.occasion}
                  onValueChange={(value) => setEditedEntry(prev => ({ ...prev, occasion: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {OCCASIONS.map(occasion => (
                      <SelectItem key={occasion} value={occasion}>
                        {occasion}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Badge variant="secondary">{entry.occasion}</Badge>
              )}
            </div>

            <div>
              <Label>Mood</Label>
              {isEditing ? (
                <Select
                  value={editedEntry.mood}
                  onValueChange={(value) => setEditedEntry(prev => ({ ...prev, mood: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {MOODS.map(mood => (
                      <SelectItem key={mood} value={mood}>
                        {mood}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <Badge variant="outline">{entry.mood}</Badge>
              )}
            </div>
          </div>

          {/* Tags */}
          <div>
            <Label>Tags</Label>
            <div className="flex flex-wrap gap-2 mt-2">
              {editedEntry.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  {isEditing && (
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-1 hover:text-destructive"
                    >
                      ×
                    </button>
                  )}
                </Badge>
              ))}
            </div>
            {isEditing && (
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="Add a tag..."
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addTag()}
                />
                <Button size="sm" onClick={addTag}>
                  Add
                </Button>
              </div>
            )}
          </div>

          {/* Notes */}
          <div>
            <Label>Notes</Label>
            {isEditing ? (
              <Textarea
                value={editedEntry.notes}
                onChange={(e) => setEditedEntry(prev => ({ ...prev, notes: e.target.value }))}
                placeholder="Add notes about this outfit..."
                rows={3}
              />
            ) : (
              <p className="text-sm text-muted-foreground mt-1">
                {entry.notes || 'No notes added'}
              </p>
            )}
          </div>

          {/* Analytics Section */}
          <Card className="p-4 bg-muted/30">
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <HeartIcon className="h-4 w-4" />
              Analytics
            </h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Times Worn:</span>
                <span className="ml-2 font-medium">3</span>
              </div>
              <div>
                <span className="text-muted-foreground">Last Worn:</span>
                <span className="ml-2 font-medium">2 days ago</span>
              </div>
              <div>
                <span className="text-muted-foreground">Favorite Occasion:</span>
                <span className="ml-2 font-medium">Work</span>
              </div>
              <div>
                <span className="text-muted-foreground">Weather Preference:</span>
                <span className="ml-2 font-medium">Clear, 70-80°F</span>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
} 