'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
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
  AlertCircle
} from 'lucide-react';
import { useAutoWeather } from '@/hooks/useWeather';
import { formatWeatherForDisplay } from '@/lib/weather';

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
  generating: boolean;
  wardrobeLoading: boolean;
  occasions: string[];
  styles: string[];
  moods: string[];
  weatherOptions: string[];
  baseItem?: any;
  onRemoveBaseItem?: () => void;
  freshWeatherData?: any; // Fresh weather data for UI display
}

export default function OutfitGenerationForm({
  formData,
  onFormChange,
  onGenerate,
  generating,
  wardrobeLoading,
  occasions,
  styles,
  moods,
  weatherOptions,
  baseItem,
  onRemoveBaseItem,
  freshWeatherData
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

      {/* Progress Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Wand2 className="h-5 w-5 text-amber-600" />
            Outfit Generation Steps
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const status = getStepStatus(index);
              const Icon = step.icon;
              const isCompleted = status === 'completed';
              const isCurrent = status === 'current';
              
              return (
                <div key={step.id} className="flex items-center">
                  <button
                    onClick={() => handleStepClick(index)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg transition-all ${
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
                    <ArrowRight className="h-4 w-4 text-gray-300 mx-2" />
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
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-amber-600" />
            Outfit Preferences
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Occasion Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Occasion *
            </label>
            <Select value={formData.occasion} onValueChange={(value) => onFormChange('occasion', value)}>
              <SelectTrigger className="h-12">
                <SelectValue placeholder="Select an occasion..." />
              </SelectTrigger>
              <SelectContent>
                {occasions.map((occasion) => (
                  <SelectItem key={occasion} value={occasion}>
                    {occasion}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Style Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Style *
            </label>
            <Select value={formData.style} onValueChange={(value) => onFormChange('style', value)}>
              <SelectTrigger className="h-12">
                <SelectValue placeholder="Choose your style..." />
              </SelectTrigger>
              <SelectContent>
                {styles.map((style) => (
                  <SelectItem key={style} value={style}>
                    {style}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Mood Selection */}
          <div className="space-y-3">
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
              <Smile className="h-4 w-4" />
              Mood *
            </label>
            <Select value={formData.mood} onValueChange={(value) => onFormChange('mood', value)}>
              <SelectTrigger className="h-12">
                <SelectValue placeholder="How are you feeling?" />
              </SelectTrigger>
              <SelectContent>
                {moods.map((mood) => (
                  <SelectItem key={mood} value={mood}>
                    {mood}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
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
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white">
                      {formatWeatherForDisplay(displayWeather).temperature}
                    </p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatWeatherForDisplay(displayWeather).condition}
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-500">
                      {displayWeather.location}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-gray-600 dark:text-gray-400 space-y-1">
                      {formatWeatherForDisplay(displayWeather).details.slice(0, 2).map((detail, index) => (
                        <p key={index}>{detail}</p>
                      ))}
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={fetchWeatherByLocation}
                      disabled={weatherLoading}
                      className="mt-1 h-6 px-2"
                    >
                      <RefreshCw className={`h-3 w-3 ${weatherLoading ? 'animate-spin' : ''}`} />
                    </Button>
                  </div>
                </div>
                {displayWeather.fallback && (
                  <p className="text-xs text-amber-600 dark:text-amber-400 mt-2 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    Using fallback weather data
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

          {/* Generate Button */}
          <Button 
            onClick={onGenerate} 
            disabled={generating || wardrobeLoading || !isFormValid}
            className="w-full h-12 text-lg font-semibold bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            size="lg"
          >
            {generating ? (
              <>
                <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                Creating Your Outfit...
              </>
            ) : wardrobeLoading ? (
              <>
                <RefreshCw className="h-5 w-5 mr-2 animate-spin" />
                Loading Wardrobe...
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5 mr-2" />
                Generate My Outfit
              </>
            )}
          </Button>

          {!isFormValid && (
            <p className="text-sm text-amber-600 dark:text-amber-400 text-center">
              Please fill in all required fields to generate your outfit
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
