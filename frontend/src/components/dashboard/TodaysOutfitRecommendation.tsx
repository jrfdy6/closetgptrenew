'use client';

import { useState, useEffect, useRef } from 'react';
import { OutfitGeneratedOutfit, ClothingItem, UserProfile } from '../shared/types/index';
import { WeatherData } from '@/types/weather';
import { useWeather } from '@/hooks/useWeather';
import { useOutfitGenerator } from '@/hooks/useOutfitGenerator';
import { useWardrobe } from '@/hooks/useWardrobe';
import { useUserProfile } from '@/hooks/useUserProfile';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import Image from 'next/image';
import { 
  Sparkles, 
  RefreshCw, 
  Heart, 
  Share2, 
  Calendar as CalendarIcon,
  Sun,
  Cloud,
  Umbrella,
  Thermometer,
  Image as ImageIcon,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  Briefcase,
  Coffee,
  Plane,
  Home,
  Users,
  GraduationCap
} from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { OutfitWarnings } from '@/components/ui/OutfitWarnings';
import { WearOutfitButton } from '@/components/ui/floating-action-button';
import { toastMessages } from '@/components/ui/enhanced-toast';
import { ContextualCTA } from '@/components/ui/contextual-cta';
import { InteractiveButton, HoverCard, MagneticButton, hapticFeedback } from '@/components/ui/micro-interactions';

// Occasion options with icons and descriptions
const OCCASION_OPTIONS = [
  { value: 'casual', label: 'Casual', icon: Home, description: 'Everyday comfort' },
  { value: 'work', label: 'Work', icon: Briefcase, description: 'Professional attire' },
  { value: 'date', label: 'Date Night', icon: Coffee, description: 'Romantic evening' },
  { value: 'travel', label: 'Travel', icon: Plane, description: 'On the go' },
  { value: 'social', label: 'Social', icon: Users, description: 'Meeting friends' },
  { value: 'formal', label: 'Formal', icon: GraduationCap, description: 'Special events' }
];

// Local storage keys
const OUTFIT_STORAGE_KEY = 'todays_outfit_data';
const OUTFIT_TIMESTAMP_KEY = 'todays_outfit_timestamp';
const OCCASION_PREFERENCE_KEY = 'user_occasion_preference';

// Check if outfit should be regenerated (24 hours)
const shouldRegenerateOutfit = (lastGenerated: number): boolean => {
  const now = Date.now();
  const twentyFourHours = 24 * 60 * 60 * 1000; // 24 hours in milliseconds
  return now - lastGenerated > twentyFourHours;
};

// Get today's date string for comparison
const getTodayString = (): string => {
  return new Date().toDateString();
};

export default function TodaysOutfitRecommendation() {
  const [outfit, setOutfit] = useState<OutfitGeneratedOutfit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [liked, setLiked] = useState(false);
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({});
  const [lastGeneratedDate, setLastGeneratedDate] = useState<string>('');
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [selectedOccasion, setSelectedOccasion] = useState('casual');
  const [isWearingOutfit, setIsWearingOutfit] = useState(false);
  
  const { weather, loading: weatherLoading } = useWeather();
  const { wardrobe, loading: wardrobeLoading } = useWardrobe();
  const { profile } = useUserProfile();
  const { generateOutfit, loading: generatingOutfit } = useOutfitGenerator();

  // Load occasion preference from localStorage
  useEffect(() => {
    const savedOccasion = localStorage.getItem(OCCASION_PREFERENCE_KEY);
    if (savedOccasion) {
      setSelectedOccasion(savedOccasion);
    }
  }, []);

  // Save occasion preference to localStorage
  const handleOccasionChange = (occasion: string) => {
    setSelectedOccasion(occasion);
    localStorage.setItem(OCCASION_PREFERENCE_KEY, occasion);
  };

  const handleImageError = (itemId: string) => {
    setImageErrors(prev => ({ ...prev, [itemId]: true }));
  };

  const handleImageLoad = (itemId: string) => {
    setImageErrors(prev => ({ ...prev, [itemId]: false }));
  };

  const handleWearOutfit = async () => {
    if (!outfit) return;
    
    setIsWearingOutfit(true);
    try {
      // TODO: Implement outfit logging functionality
      // This would typically save to Firebase or your backend
      console.log('Wearing outfit:', outfit.name);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success feedback
      // You can integrate with your toast system here
      console.log('Toast message:', toastMessages.outfitWorn);
      // For now, using alert but you can replace with your toast system
      alert('🎉 Outfit logged! You\'re looking great!');
      
    } catch (error) {
      console.error('Error logging outfit:', error);
      alert('Failed to log outfit. Please try again.');
    } finally {
      setIsWearingOutfit(false);
    }
  };

  // Load saved outfit from localStorage
  const loadSavedOutfit = (): OutfitGeneratedOutfit | null => {
    try {
      const savedOutfit = localStorage.getItem(OUTFIT_STORAGE_KEY);
      const savedTimestamp = localStorage.getItem(OUTFIT_TIMESTAMP_KEY);
      
      if (savedOutfit && savedTimestamp) {
        const outfitData = JSON.parse(savedOutfit);
        const timestamp = parseInt(savedTimestamp);
        const today = getTodayString();
        
        // Check if outfit was generated today and within 24 hours
        if (outfitData.generatedDate === today && !shouldRegenerateOutfit(timestamp)) {
          console.log('📅 Loading saved outfit from today');
          setLastGeneratedDate(today);
          return outfitData.outfit;
        } else {
          console.log('📅 Saved outfit is outdated, will generate new one');
          // Clear outdated data
          localStorage.removeItem(OUTFIT_STORAGE_KEY);
          localStorage.removeItem(OUTFIT_TIMESTAMP_KEY);
        }
      }
    } catch (error) {
      console.error('Error loading saved outfit:', error);
      // Clear corrupted data
      localStorage.removeItem(OUTFIT_STORAGE_KEY);
      localStorage.removeItem(OUTFIT_TIMESTAMP_KEY);
    }
    return null;
  };

  // Save outfit to localStorage
  const saveOutfit = (outfitData: OutfitGeneratedOutfit) => {
    try {
      const today = getTodayString();
      const dataToSave = {
        outfit: outfitData,
        generatedDate: today
      };
      localStorage.setItem(OUTFIT_STORAGE_KEY, JSON.stringify(dataToSave));
      localStorage.setItem(OUTFIT_TIMESTAMP_KEY, Date.now().toString());
      setLastGeneratedDate(today);
      console.log('📅 Saved outfit to localStorage');
    } catch (error) {
      console.error('Error saving outfit:', error);
    }
  };

  // Clear saved outfit data
  const clearSavedOutfit = () => {
    try {
      localStorage.removeItem(OUTFIT_STORAGE_KEY);
      localStorage.removeItem(OUTFIT_TIMESTAMP_KEY);
      setLastGeneratedDate('');
      console.log('📅 Cleared saved outfit from localStorage');
    } catch (error) {
      console.error('Error clearing saved outfit:', error);
    }
  };

  // Generate outfit explainability text
  const generateOutfitExplanation = () => {
    if (!outfit || !weather || !profile) return '';

    const occasionInfo = OCCASION_OPTIONS.find(opt => opt.value === selectedOccasion);
    const weatherDesc = weather.condition ? `${weather.temperature}°F ${weather.condition}` : `${weather.temperature}°F`;
    const stylePrefs = profile.preferences?.style || [];
    const styleText = stylePrefs.length > 0 ? stylePrefs.slice(0, 2).join(' + ') : 'your style preferences';

    return `Selected for today's ${weatherDesc} weather, ${occasionInfo?.label.toLowerCase()} occasion, and your ${styleText}. The outfit balances comfort with style while considering the current weather conditions and your personal fashion preferences.`;
  };

  useEffect(() => {
    const generateTodaysOutfit = async () => {
      try {
        setLoading(true);
        setError(null);

        if (!weather || !wardrobe || !profile) {
          return;
        }

        // Try to load saved outfit first
        const savedOutfit = loadSavedOutfit();
        if (savedOutfit) {
          setOutfit(savedOutfit);
          setLoading(false);
          return;
        }

        // Generate new outfit if no saved outfit or it's outdated
        console.log('🎨 Generating new outfit for today');
        const generatedOutfit = await generateOutfit({
          wardrobe: wardrobe as ClothingItem[],
          weather,
          occasion: selectedOccasion,
          userProfile: profile as UserProfile
        });

        setOutfit(generatedOutfit);
        saveOutfit(generatedOutfit);
      } catch (err) {
        setError('Failed to generate outfit recommendation');
        console.error('Error generating outfit:', err);
      } finally {
        setLoading(false);
      }
    };

    if (!weatherLoading && !wardrobeLoading && !generatingOutfit) {
      generateTodaysOutfit();
    }
  }, [weather, wardrobe, profile, weatherLoading, wardrobeLoading, generatingOutfit, selectedOccasion]);

  const handleGenerateOutfit = async () => {
    if (!weather || !wardrobe || !profile) {
      return;
    }

    setIsGenerating(true);
    try {
      // Clear any existing saved outfit data
      clearSavedOutfit();
      
      const newOutfit = await generateOutfit({
        wardrobe: wardrobe as ClothingItem[],
        weather,
        occasion: selectedOccasion,
        userProfile: profile as UserProfile
      });

      setOutfit(newOutfit);
      saveOutfit(newOutfit);
      setLiked(false); // Reset like status for new outfit
    } catch (err) {
      setError('Failed to generate new outfit');
      console.error('Error generating new outfit:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  if (loading || generatingOutfit) {
    return (
      <Card className="w-full overflow-hidden border border-border bg-card shadow-xl">
        <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white pb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <CardTitle className="text-xl font-bold">Today's Outfit</CardTitle>
                <p className="text-indigo-100 text-sm">Perfect for your day ahead</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(selectedDate, 'EEEE, MMM d')}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full overflow-hidden border border-border bg-card shadow-xl">
        <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white pb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <CardTitle className="text-xl font-bold">Today's Outfit</CardTitle>
                <p className="text-indigo-100 text-sm">Perfect for your day ahead</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(selectedDate, 'EEEE, MMM d')}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <Button onClick={handleGenerateOutfit} className="mt-4">
              Try Again
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!outfit) {
    return (
      <Card className="w-full overflow-hidden border border-border bg-card shadow-xl">
        <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white pb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Sparkles className="w-6 h-6" />
              </div>
              <div>
                <CardTitle className="text-xl font-bold">Today's Outfit</CardTitle>
                <p className="text-indigo-100 text-sm">Perfect for your day ahead</p>
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(selectedDate, 'EEEE, MMM d')}</span>
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-6">
          <div className="text-center py-8">
            <p className="text-muted-foreground">No outfit generated yet</p>
            <Button onClick={handleGenerateOutfit} className="mt-4">
              Generate Outfit
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full overflow-hidden border border-border bg-card shadow-xl">
      <CardHeader className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white pb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold">Today's Outfit</CardTitle>
              <p className="text-indigo-100 text-sm">Perfect for your day ahead</p>
              {lastGeneratedDate && (
                <p className="text-indigo-200 text-xs mt-1">
                  Generated: {new Date(lastGeneratedDate).toLocaleDateString('en-US', { 
                    weekday: 'short', 
                    month: 'short', 
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Occasion Selector */}
            <Select value={selectedOccasion} onValueChange={handleOccasionChange}>
              <SelectTrigger className="w-40 bg-white/20 border-white/30 text-white hover:bg-white/30">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {OCCASION_OPTIONS.map((occasion) => {
                  const IconComponent = occasion.icon;
                  return (
                    <SelectItem key={occasion.value} value={occasion.value}>
                      <div className="flex items-center gap-2">
                        <IconComponent className="w-4 h-4" />
                        <span>{occasion.label}</span>
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>

            {/* Calendar Popover */}
            <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
              <PopoverTrigger asChild>
                <Button variant="outline" size="sm" className="bg-white/20 border-white/30 text-white hover:bg-white/30">
                  <CalendarIcon className="w-4 h-4 mr-2" />
                  {format(selectedDate, 'MMM d, yyyy')}
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-auto p-0" align="end">
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={(date) => {
                    if (date) {
                      setSelectedDate(date);
                      setCalendarOpen(false);
                    }
                  }}
                  initialFocus
                />
              </PopoverContent>
            </Popover>
            
            <div className="flex items-center gap-2 text-sm">
              <CalendarIcon className="w-4 h-4" />
              <span>{format(selectedDate, 'EEEE, MMM d')}</span>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-6">
        {/* Weather Section */}
        <div className="mb-6 p-4 bg-muted/50 rounded-xl border border-border">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cloud className="w-6 h-6 text-blue-500" />
              <div>
                <p className="font-semibold text-foreground">{weather?.condition}</p>
                <p className="text-sm text-muted-foreground">Perfect weather for this outfit</p>
                {weather?.fallback && (
                  <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                    ⚠️ Using estimated weather data
                  </p>
                )}
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-foreground">{weather?.temperature}°F</p>
              <p className="text-xs text-muted-foreground">Feels great!</p>
            </div>
          </div>
        </div>

        {/* Outfit Display */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
              {outfit?.name || 'Your Outfit'}
            </h3>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="text-xs">
                {outfit?.occasion || 'Casual'}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {outfit?.style || 'Stylish'}
              </Badge>
            </div>
          </div>

          {/* NEW: Display warnings and validation details */}
          {outfit && (
            <OutfitWarnings
              warnings={outfit.warnings}
              validationErrors={outfit.validationErrors}
              validationDetails={outfit.validation_details}
              wasSuccessful={outfit.wasSuccessful}
              className="mb-4"
            />
          )}
          
          <div className={cn(
            "grid gap-4 auto-rows-fr",
            (outfit?.items as any[])?.length <= 4 
              ? "grid-cols-2" // 2x2 grid for 4 or fewer items
              : "grid-cols-3" // 3x2 grid for more than 4 items
          )}>
            {(outfit?.items as any[])?.map((item: any, index: number) => {
              // If item is a string (ID), look up the full item in wardrobe
              let clothingItem: ClothingItem | null = null;
              if (typeof item === 'string') {
                clothingItem = (wardrobe as ClothingItem[]).find(w => w.id === item) || null;
                if (!clothingItem) {
                  // If not found, show placeholder with ID
                  return (
                    <div 
                      key={index}
                      className="relative aspect-square bg-muted rounded-lg border border-border overflow-hidden"
                    >
                      <div className="w-full h-full flex items-center justify-center">
                        <div className="text-center p-4">
                          <ImageIcon className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                          <p className="text-xs text-muted-foreground font-medium">{item}</p>
                        </div>
                      </div>
                    </div>
                  );
                }
              } else {
                clothingItem = item as ClothingItem;
              }
              if (!clothingItem) return null;
              const hasImageError = imageErrors[clothingItem.id] || !clothingItem.imageUrl || clothingItem.imageUrl === "";
              return (
                <div
                  key={clothingItem.id}
                  className="relative aspect-square bg-muted rounded-lg border border-border overflow-hidden group"
                  style={{ minHeight: '150px', height: '150px' }}
                >
                  {hasImageError ? (
                    <div className="w-full h-full flex items-center justify-center">
                      <ImageIcon className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-xs text-muted-foreground font-medium">{clothingItem.name || clothingItem.id}</p>
                    </div>
                  ) : (
                    <Image
                      src={clothingItem.imageUrl}
                      alt={clothingItem.name || 'Wardrobe item'}
                      fill
                      className="object-cover"
                      onError={() => handleImageError(clothingItem.id)}
                      onLoad={() => handleImageLoad(clothingItem.id)}
                      unoptimized={true}
                    />
                  )}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                    <p className="text-white text-xs font-medium truncate">{clothingItem.name}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <Badge variant="secondary" className="text-xs bg-white/20 text-white border-0">
                        {clothingItem.type}
                      </Badge>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Contextual CTA */}
        <div className="mb-6">
          <ContextualCTA
            weather={weather || undefined}
            occasion={selectedOccasion}
            styleLevel={3} // TODO: Get from user profile
            onAction={(action) => {
              console.log('Contextual action:', action);
              // TODO: Implement contextual actions
            }}
          />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Wear Outfit Button - Prominent */}
          {outfit && (
            <Button
              onClick={handleWearOutfit}
              disabled={isWearingOutfit}
              className="flex-1 bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-700 hover:to-emerald-800 text-white shadow-lg hover:shadow-xl transition-all duration-200 text-lg font-semibold py-6"
            >
              {isWearingOutfit ? (
                <>
                  <RefreshCw className="w-5 h-5 mr-3 animate-spin" />
                  Wearing Outfit...
                </>
              ) : (
                <>
                  <span className="text-xl mr-3">👕</span>
                  Wear This Outfit
                </>
              )}
            </Button>
          )}
          
          <div className="flex gap-2">
            <InteractiveButton
              variant="outline"
              size="sm"
              onClick={() => {
                hapticFeedback.success();
                setLiked(!liked);
              }}
              hapticType="success"
              className={`transition-all duration-200 ${
                liked 
                  ? 'bg-red-500/10 border-red-500/20 text-red-500 hover:bg-red-500/20' 
                  : 'hover:bg-accent'
              }`}
            >
              <Heart className={`w-4 h-4 ${liked ? 'fill-current' : ''}`} />
            </InteractiveButton>
            <InteractiveButton
              variant="outline"
              size="sm"
              hapticType="light"
              className="hover:bg-accent"
            >
              <Share2 className="w-4 h-4" />
            </InteractiveButton>
          </div>
        </div>


      </CardContent>
    </Card>
  );
} 