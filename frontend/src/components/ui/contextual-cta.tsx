import React from 'react';
import { Button } from './button';
import { Badge } from './badge';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { 
  Cloud, 
  CloudRain, 
  Sun, 
  Snowflake, 
  Umbrella, 
  Thermometer,
  Sparkles,
  Calendar,
  Heart,
  TrendingUp
} from 'lucide-react';

interface WeatherData {
  condition: string;
  temperature: number;
  humidity?: number;
}

interface ContextualCTAProps {
  weather?: WeatherData;
  occasion?: string;
  mood?: string;
  styleLevel?: number;
  onAction: (action: string) => void;
  className?: string;
}

const weatherPrompts = {
  'rain': {
    icon: Umbrella,
    title: 'View rainy day fits ☔',
    description: 'Stay dry and stylish',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700'
  },
  'snow': {
    icon: Snowflake,
    title: 'Bundle up with winter looks ❄️',
    description: 'Cozy and warm outfits',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-cyan-500 to-cyan-600 hover:from-cyan-600 hover:to-cyan-700'
  },
  'sunny': {
    icon: Sun,
    title: 'Bright and sunny outfits ☀️',
    description: 'Perfect for the weather',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700'
  },
  'cloudy': {
    icon: Cloud,
    title: 'Cloudy day essentials ☁️',
    description: 'Versatile layers for changing weather',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700'
  },
  'hot': {
    icon: Thermometer,
    title: 'Beat the heat outfits 🔥',
    description: 'Light and breathable',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700'
  },
  'cold': {
    icon: Thermometer,
    title: 'Stay warm and cozy 🧥',
    description: 'Layered looks for cold weather',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700'
  }
};

const occasionPrompts = {
  'work': {
    icon: Calendar,
    title: 'Professional work looks 💼',
    description: 'Office-appropriate outfits',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-slate-500 to-slate-600 hover:from-slate-600 hover:to-slate-700'
  },
  'casual': {
    icon: Heart,
    title: 'Casual comfort fits 😊',
    description: 'Relaxed and comfortable',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700'
  },
  'formal': {
    icon: Sparkles,
    title: 'Elegant formal wear ✨',
    description: 'Sophisticated and polished',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700'
  },
  'date': {
    icon: Heart,
    title: 'Date night magic 💕',
    description: 'Romantic and attractive',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700'
  }
};

const levelUpPrompts = {
  level5: {
    icon: TrendingUp,
    title: 'Level up your style! ⭐',
    description: 'You\'re close to the next level',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-yellow-500 to-yellow-600 hover:from-yellow-600 hover:to-yellow-700'
  },
  milestone: {
    icon: Sparkles,
    title: 'Style milestone reached! 🏆',
    description: 'Unlock new features',
    variant: 'default' as const,
    className: 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700'
  }
};

export function ContextualCTA({
  weather,
  occasion,
  mood,
  styleLevel = 0,
  onAction,
  className
}: ContextualCTAProps) {
  // Determine which prompt to show based on context
  const getPrompt = () => {
    // Check for level up opportunities first
    if (styleLevel >= 4 && styleLevel < 5) {
      return levelUpPrompts.level5;
    }
    
    if (styleLevel % 10 === 0 && styleLevel > 0) {
      return levelUpPrompts.milestone;
    }
    
    // Check weather conditions
    if (weather) {
      const condition = weather.condition.toLowerCase();
      const temp = weather.temperature;
      
      if (condition.includes('rain') || condition.includes('drizzle')) {
        return weatherPrompts.rain;
      }
      if (condition.includes('snow') || condition.includes('sleet')) {
        return weatherPrompts.snow;
      }
      if (condition.includes('sunny') || condition.includes('clear')) {
        return weatherPrompts.sunny;
      }
      if (condition.includes('cloudy') || condition.includes('overcast')) {
        return weatherPrompts.cloudy;
      }
      if (temp > 80) {
        return weatherPrompts.hot;
      }
      if (temp < 40) {
        return weatherPrompts.cold;
      }
    }
    
    // Check occasion
    if (occasion && occasionPrompts[occasion as keyof typeof occasionPrompts]) {
      return occasionPrompts[occasion as keyof typeof occasionPrompts];
    }
    
    // Default prompt
    return {
      icon: Sparkles,
      title: 'Discover new styles ✨',
      description: 'Explore your wardrobe possibilities',
      variant: 'default' as const,
      className: 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700'
    };
  };

  const prompt = getPrompt();
  const Icon = prompt.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={cn(
        'relative overflow-hidden rounded-xl border border-border',
        'bg-gradient-to-r from-muted/50 to-background',
        'p-4 hover:shadow-lg transition-all duration-300',
        className
      )}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-emerald-500/10 to-transparent rounded-full -translate-y-10 translate-x-10" />
      
      <div className="relative flex items-center gap-4">
        {/* Icon */}
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 flex items-center justify-center">
            <Icon className="w-6 h-6 text-emerald-600" />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground mb-1">
            {prompt.title}
          </h3>
          <p className="text-sm text-muted-foreground mb-3">
            {prompt.description}
          </p>
          
          {/* Context badges */}
          <div className="flex flex-wrap gap-2 mb-3">
            {weather && (
              <Badge variant="outline" className="text-xs">
                {weather.condition} {weather.temperature}°F
              </Badge>
            )}
            {occasion && (
              <Badge variant="secondary" className="text-xs">
                {occasion}
              </Badge>
            )}
            {mood && (
              <Badge variant="outline" className="text-xs">
                {mood}
              </Badge>
            )}
            {styleLevel > 0 && (
              <Badge variant="default" className="text-xs bg-gradient-to-r from-yellow-500 to-yellow-600">
                Level {styleLevel}
              </Badge>
            )}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex-shrink-0">
          <Button
            onClick={() => onAction(prompt.title.toLowerCase())}
            className={cn(
              'shadow-md hover:shadow-lg transition-all duration-200',
              'hover:scale-105 active:scale-95',
              prompt.className
            )}
            size="sm"
          >
            Explore
          </Button>
        </div>
      </div>
    </motion.div>
  );
}

// Quick contextual button for specific actions
export function QuickContextualButton({
  type,
  onClick,
  className
}: {
  type: 'weather' | 'occasion' | 'level';
  onClick: () => void;
  className?: string;
}) {
  const getQuickPrompt = () => {
    switch (type) {
      case 'weather':
        return {
          icon: Cloud,
          title: 'Weather-based outfits',
          className: 'bg-gradient-to-r from-blue-500 to-blue-600'
        };
      case 'occasion':
        return {
          icon: Calendar,
          title: 'Occasion-specific looks',
          className: 'bg-gradient-to-r from-purple-500 to-purple-600'
        };
      case 'level':
        return {
          icon: TrendingUp,
          title: 'Level up your style',
          className: 'bg-gradient-to-r from-yellow-500 to-yellow-600'
        };
    }
  };

  const prompt = getQuickPrompt();
  const Icon = prompt.icon;

  return (
    <Button
      onClick={onClick}
      className={cn(
        'rounded-full shadow-md hover:shadow-lg transition-all duration-200',
        'hover:scale-105 active:scale-95',
        prompt.className,
        className
      )}
      size="sm"
    >
      <Icon className="w-4 h-4 mr-2" />
      {prompt.title}
    </Button>
  );
} 