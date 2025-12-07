'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Chip } from '@/components/ui/chip';
import { 
  Sparkles, 
  Palette, 
  Calendar, 
  MapPin, 
  Clock, 
  Zap,
  Shirt,
  RefreshCw,
  ArrowRight,
  Wand2,
  Target,
  Smile,
  Cloud,
  AlertCircle,
  Sun,
  Shuffle
} from 'lucide-react';
import { useAutoWeather } from '@/hooks/useWeather';
import { formatWeatherForDisplay } from '@/lib/weather';
import { motion } from 'framer-motion';

interface OutfitGenerationFormProps {
  formData: {
    occasion: string;
    style: string;
    mood: string;
    weather: string;
    description: string;
  };
  onFormChange: (field: string, value: string) => void;
  onGenerate: () => void;
  onShuffleAndGenerate?: (shuffledData: { occasion: string; style: string; mood: string }) => void;
  generating: boolean;
  wardrobeLoading: boolean;
  occasions: string[];
  styles: string[];
  moods: string[];
  weatherOptions: string[];
  baseItem?: any;
  onRemoveBaseItem?: () => void;
  freshWeatherData?: any; // Fresh weather data for UI display
  userGender?: string; // For gender-aware style shuffling
}

export default function OutfitGenerationForm({
  formData,
  onFormChange,
  onGenerate,
  onShuffleAndGenerate,
  generating,
  wardrobeLoading,
  occasions,
  styles,
  moods,
  weatherOptions,
  baseItem,
  onRemoveBaseItem,
  freshWeatherData,
  userGender
}: OutfitGenerationFormProps) {
  const [activeStep, setActiveStep] = useState(0);
  const { weather, loading: weatherLoading, fetchWeatherByLocation, error: weatherError } = useAutoWeather();
  
  // Use fresh weather data if available, otherwise fall back to hook weather
  const displayWeather = freshWeatherData || weather;
  
  const steps = [
    { id: 'occasion', label: 'Occasion', icon: Calendar },
    { id: 'style', label: 'Style', icon: Palette },
    { id: 'mood', label: 'Mood', icon: Smile },
    { id: 'weather', label: 'Weather', icon: Cloud }
  ];

  const isFormValid = formData.occasion && formData.style && formData.mood;
  
  // Shuffle function - auto-fills form with random gender-appropriate values
  const handleShuffle = () => {
    console.log('🎲 Shuffle button clicked!');
    
    // Filter styles based on gender
    const getGenderAppropriateStyles = (): string[] => {
      const gender = (userGender || 'male').toLowerCase();
      
      // Gender-specific filtering
      const obviouslyFeminineStyles = ['Coastal Grandmother', 'French Girl', 'Pinup', 'Clean Girl'];
      const obviouslyMasculineStyles = ['Techwear'];
      
      if (gender === 'male') {
        // Males: All styles except 4 feminine ones = 32 styles
        return styles.filter(style => !obviouslyFeminineStyles.includes(style));
      } else if (gender === 'female') {
        // Females: All styles except 1 masculine one = 35 styles
        return styles.filter(style => !obviouslyMasculineStyles.includes(style));
      } else {
        // Non-binary / Prefer not to say: ALL 36 styles
        return styles;
      }
    };
    
    const availableStyles = getGenderAppropriateStyles();
    const allMoods = ['Romantic', 'Playful', 'Serene', 'Dynamic', 'Bold', 'Subtle'];
    
    // Randomly select style and mood
    const randomStyle = availableStyles[Math.floor(Math.random() * availableStyles.length)];
    const randomMood = allMoods[Math.floor(Math.random() * allMoods.length)];
    
    console.log(`🎲 Shuffled to: ${randomStyle} / ${randomMood}`);
    
    const shuffledData = {
      occasion: 'Casual',
      style: randomStyle,
      mood: randomMood
    };
    
    // ✅ FIX: If parent provides shuffle handler, use it (bypasses state delay)
    if (onShuffleAndGenerate) {
      console.log('🎲 Using direct shuffle handler with values:', shuffledData);
      onShuffleAndGenerate(shuffledData);
      return;
    }
    
    // Fallback: Update form fields and trigger generation
    onFormChange('occasion', 'Casual');
    onFormChange('style', randomStyle);
    onFormChange('mood', randomMood);
    
    console.log('🎲 Form updated, triggering generation...');
    
    requestAnimationFrame(() => {
      setTimeout(() => {
        console.log('🎲 Calling onGenerate() - form should be fully updated');
        onGenerate();
      }, 500);
    });
  };

  const handleStepClick = (stepIndex: number) => {
    if (stepIndex <= activeStep) {
      setActiveStep(stepIndex);
    }
  };

  const getStepStatus = (stepIndex: number) => {
    if (stepIndex < activeStep) return 'completed';
    if (stepIndex === activeStep) return 'current';
    return 'upcoming';
  };

  return (
    <div className="space-y-6">
      {/* Base Item Indicator */}
      {baseItem && (
        <Card className="border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 dark:border-amber-800 dark:from-amber-900/20 dark:to-orange-900/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 bg-white dark:bg-gray-800 rounded-xl overflow-hidden flex-shrink-0 shadow-sm">
                <img
                  src={baseItem.imageUrl || baseItem.image_url || '/placeholder.jpg'}
                  alt={baseItem.name || 'Base item'}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = '/placeholder.jpg';
                  }}
                />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Target className="h-4 w-4 text-amber-600" />
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    Building outfit around: {baseItem.name || 'Unknown item'}
                  </h3>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  This item will be the foundation of your new outfit
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={onRemoveBaseItem}
                className="text-gray-500 hover:text-gray-700"
              >
                Remove
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Progress Steps - Mobile Optimized */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
            <Wand2 className="h-5 w-5 text-amber-600 flex-shrink-0" />
            <span className="truncate">Outfit Generation Steps</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {/* Mobile: Vertical Stack */}
          <div className="flex sm:hidden flex-col gap-2">
            {steps.map((step, index) => {
              const status = getStepStatus(index);
              const Icon = step.icon;
              const isCompleted = status === 'completed';
              const isCurrent = status === 'current';
              
              return (
                <button
                  key={step.id}
                  onClick={() => handleStepClick(index)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isCurrent 
                      ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' 
                      : isCompleted
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                      : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'
                  }`}
                >
                  <Icon className={`h-5 w-5 flex-shrink-0 ${isCompleted ? 'text-amber-600' : ''}`} />
                  <span className="text-sm font-medium flex-1 text-left">{step.label}</span>
                  {isCompleted && <div className="w-2 h-2 bg-amber-500 rounded-full flex-shrink-0" />}
                </button>
              );
            })}
          </div>
          
          {/* Desktop: Horizontal Flow */}
          <div className="hidden sm:flex items-center justify-between overflow-x-auto">
            {steps.map((step, index) => {
              const status = getStepStatus(index);
              const Icon = step.icon;
              const isCompleted = status === 'completed';
              const isCurrent = status === 'current';
              
              return (
                <div key={step.id} className="flex items-center">
                  <button
                    onClick={() => handleStepClick(index)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all whitespace-nowrap ${
                      isCurrent 
                        ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300' 
                        : isCompleted
                        ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300'
                        : 'text-gray-400 hover:text-gray-600'
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isCompleted ? 'text-amber-600' : ''}`} />
                    <span className="text-sm font-medium">{step.label}</span>
                    {isCompleted && <div className="w-2 h-2 bg-amber-500 rounded-full" />}
                  </button>
                  {index < steps.length - 1 && (
                    <ArrowRight className="h-4 w-4 text-gray-300 mx-2 flex-shrink-0" />
                  )}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Form Fields */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base sm:text-lg">
            <Sparkles className="h-5 w-5 text-amber-600 flex-shrink-0" />
            <span className="truncate">Outfit Preferences</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 sm:space-y-6">
          {/* Occasion Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Occasion *
            </label>
            <div className="flex flex-wrap gap-2">
              {occasions.map((occasion) => (
                <Chip
                  key={occasion}
                  variant="default"
                  size="default"
                  selected={formData.occasion === occasion}
                  onClick={() => onFormChange('occasion', occasion)}
                >
                  {occasion}
                </Chip>
              ))}
            </div>
          </div>

          {/* Style Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Style *
            </label>
            <div className="flex flex-wrap gap-2">
              {styles.map((style) => (
                <Chip
                  key={style}
                  variant="style"
                  size="style"
                  selected={formData.style === style}
                  onClick={() => onFormChange('style', style)}
                >
                  {style}
                </Chip>
              ))}
            </div>
          </div>

          {/* Mood Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Smile className="h-4 w-4" />
              Mood *
            </label>
            <div className="flex flex-wrap gap-2">
              {moods.map((mood) => (
                <Chip
                  key={mood}
                  variant="mood"
                  size="mood"
                  selected={formData.mood === mood}
                  onClick={() => onFormChange('mood', mood)}
                >
                  {mood}
                </Chip>
              ))}
            </div>
          </div>

          {/* Current Weather Display */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Cloud className="h-4 w-4" />
              Current Weather
            </label>
            
            {weatherLoading ? (
              <div className="h-12 bg-gray-50 dark:bg-gray-800 rounded-lg border flex items-center justify-center">
                <RefreshCw className="h-4 w-4 animate-spin text-gray-400 mr-2" />
                <span className="text-sm text-gray-500">Loading weather...</span>
              </div>
            ) : displayWeather ? (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3 sm:p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2">
                      <p className="text-2xl sm:text-lg font-semibold text-gray-900 dark:text-white">
                        {formatWeatherForDisplay(displayWeather).temperature}
                      </p>
                      <Sun className="h-5 w-5 sm:h-4 sm:w-4 text-amber-500" />
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                      {formatWeatherForDisplay(displayWeather).condition}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-0.5 truncate">
                      {displayWeather.location || 'Unknown Location'}
                    </p>
                  </div>
                  <div className="flex items-start justify-between sm:flex-col sm:text-right gap-2">
                    <div className="text-xs text-gray-600 dark:text-gray-400 space-y-0.5">
                      {formatWeatherForDisplay(displayWeather).details.slice(0, 2).map((detail, index) => (
                        <p key={index} className="whitespace-nowrap">{detail}</p>
                      ))}
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={fetchWeatherByLocation}
                      disabled={weatherLoading}
                      className="h-8 w-8 sm:h-6 sm:w-auto sm:px-2 sm:mt-1"
                    >
                      <RefreshCw className={`h-4 w-4 sm:h-3 sm:w-3 ${weatherLoading ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
                {displayWeather.fallback && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-2 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3 flex-shrink-0" />
                    <span>Using fallback weather data</span>
                  </p>
                )}
              </div>
            ) : (
              <div className="h-12 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg flex items-center justify-center">
                <AlertCircle className="h-4 w-4 text-red-500 mr-2" />
                <span className="text-sm text-red-600 dark:text-red-400">Weather unavailable</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={fetchWeatherByLocation}
                  className="ml-2 h-6 px-2"
                >
                  <RefreshCw className="h-3 w-3" />
                </Button>
              </div>
            )}
            
            {/* Manual Weather Override (Optional) */}
            <details className="group">
              <summary className="cursor-pointer text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
                Override weather manually (optional)
              </summary>
              <div className="mt-2">
                <Select value={formData.weather} onValueChange={(value) => onFormChange('weather', value)}>
                  <SelectTrigger className="h-10">
                    <SelectValue placeholder="Override current weather..." />
                  </SelectTrigger>
                  <SelectContent>
                    {weatherOptions.map((weather) => (
                      <SelectItem key={weather} value={weather}>
                        {weather}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </details>
          </div>

          {/* Selected Preferences Display */}
          {(formData.occasion || formData.style || formData.mood) && (
            <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Your Preferences:</h4>
              <div className="flex flex-wrap gap-2">
                {formData.occasion && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formData.occasion}
                  </Badge>
                )}
                {formData.style && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Palette className="h-3 w-3" />
                    {formData.style}
                  </Badge>
                )}
                {formData.mood && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <Smile className="h-3 w-3" />
                    {formData.mood}
                  </Badge>
                )}
                {formData.weather && (
                  <Badge variant="outline" className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    {formData.weather}
                  </Badge>
                )}
              </div>
            </div>
          )}

          {/* Generate Buttons Section */}
          <div className="space-y-3">
            {/* Primary Generate Button */}
            <Button 
              onClick={onGenerate} 
              disabled={generating || wardrobeLoading || !isFormValid}
              className="w-full h-12 sm:h-14 text-base sm:text-lg font-semibold bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 transition-all duration-200 shadow-lg hover:shadow-xl"
              size="lg"
            >
              {generating ? (
                <>
                  <RefreshCw className="h-4 w-4 sm:h-5 sm:w-5 mr-2 animate-spin" />
                  <span className="truncate">Creating Your Outfit...</span>
                </>
              ) : wardrobeLoading ? (
                <>
                  <RefreshCw className="h-4 w-4 sm:h-5 sm:w-5 mr-2 animate-spin" />
                  <span className="truncate">Loading Wardrobe...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0" />
                  <span>Generate My Outfit</span>
                </>
              )}
            </Button>

            {/* Shuffle Button - Auto-fills and generates */}
            <motion.div
              whileTap={{ scale: 0.98 }}
              whileHover={{ scale: 1.01 }}
            >
              <Button 
                onClick={handleShuffle} 
                disabled={generating || wardrobeLoading}
                variant="outline"
                className="w-full h-12 sm:h-14 text-base sm:text-lg font-semibold border-2 border-amber-500/50 hover:border-amber-500 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-all duration-200 relative overflow-hidden group"
                size="lg"
              >
                <motion.div
                  animate={generating ? { rotate: 360 } : {}}
                  transition={{
                    duration: 1,
                    repeat: generating ? Infinity : 0,
                    ease: "linear"
                  }}
                >
                  <Shuffle className="h-4 w-4 sm:h-5 sm:w-5 mr-2 flex-shrink-0" />
                </motion.div>
                <span>Surprise Me! (Shuffle)</span>
                <Sparkles className="h-4 w-4 ml-2 text-amber-500 group-hover:text-amber-600" />
                
                {/* Shimmer effect */}
                {!generating && (
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/20 to-transparent"
                    animate={{
                      x: ['-100%', '200%']
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: "linear",
                      repeatDelay: 1.5
                    }}
                  />
                )}
              </Button>
            </motion.div>

            {!isFormValid && (
              <p className="text-xs sm:text-sm text-amber-600 dark:text-amber-400 text-center px-2">
                {generating ? "Generating your outfit..." : "Fill in fields above or click 'Surprise Me!' to auto-generate"}
              </p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
