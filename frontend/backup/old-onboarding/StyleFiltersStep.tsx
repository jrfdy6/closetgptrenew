import { useState, useEffect } from 'react';
import { useOnboardingStore, StylePreference } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Check } from 'lucide-react';

interface StyleFiltersStepProps {
  onComplete: () => void;
}

const STYLE_OPTIONS = [
  {
    id: 'Dark Academia' as StylePreference,
    name: 'Dark Academia',
    description: 'Intellectual, sophisticated style with dark colors and vintage elements',
    imageUrl: '/quiz-images/dark-academia.jpg',
    tags: ['intellectual', 'sophisticated', 'vintage']
  },
  {
    id: 'Old Money' as StylePreference,
    name: 'Old Money',
    description: 'Timeless, luxurious style with quality fabrics and classic silhouettes',
    imageUrl: '/quiz-images/old-money.jpg',
    tags: ['luxurious', 'timeless', 'classic']
  },
  {
    id: 'Streetwear' as StylePreference,
    name: 'Streetwear',
    description: 'Urban, trendy style with bold graphics and contemporary pieces',
    imageUrl: '/quiz-images/streetwear.jpg',
    tags: ['urban', 'trendy', 'bold']
  },
  {
    id: 'Y2K' as StylePreference,
    name: 'Y2K',
    description: 'Retro-futuristic style inspired by the early 2000s',
    imageUrl: '/quiz-images/y2k.jpg',
    tags: ['retro', 'futuristic', 'nostalgic']
  },
  {
    id: 'Minimalist' as StylePreference,
    name: 'Minimalist',
    description: 'Clean lines, neutral colors, and essential pieces',
    imageUrl: '/quiz-images/minimalist.jpg',
    tags: ['clean', 'simple', 'essential']
  },
  {
    id: 'Boho' as StylePreference,
    name: 'Boho',
    description: 'Free-spirited style with eclectic patterns and natural elements',
    imageUrl: '/quiz-images/boho.jpg',
    tags: ['free-spirited', 'eclectic', 'natural']
  },
  {
    id: 'Preppy' as StylePreference,
    name: 'Preppy',
    description: 'Classic, polished look with structured pieces and traditional patterns',
    imageUrl: '/quiz-images/preppy.jpg',
    tags: ['classic', 'polished', 'traditional']
  },
  {
    id: 'Grunge' as StylePreference,
    name: 'Grunge',
    description: 'Edgy, rebellious style with distressed elements and dark tones',
    imageUrl: '/quiz-images/grunge.jpg',
    tags: ['edgy', 'rebellious', 'distressed']
  },
  {
    id: 'Classic' as StylePreference,
    name: 'Classic',
    description: 'Timeless, elegant style that never goes out of fashion',
    imageUrl: '/quiz-images/classic.jpg',
    tags: ['timeless', 'elegant', 'sophisticated']
  },
  {
    id: 'Techwear' as StylePreference,
    name: 'Techwear',
    description: 'Futuristic, functional style with technical fabrics and modern design',
    imageUrl: '/quiz-images/techwear.jpg',
    tags: ['futuristic', 'functional', 'modern']
  },
  {
    id: 'Androgynous' as StylePreference,
    name: 'Androgynous',
    description: 'Gender-neutral style that blurs traditional fashion boundaries',
    imageUrl: '/quiz-images/androgynous.jpg',
    tags: ['gender-neutral', 'boundary-breaking', 'modern']
  },
  {
    id: 'Coastal Chic' as StylePreference,
    name: 'Coastal Chic',
    description: 'Relaxed, beach-inspired style with natural fabrics and ocean tones',
    imageUrl: '/quiz-images/coastal-chic.jpg',
    tags: ['relaxed', 'natural', 'beach']
  },
  {
    id: 'Business Casual' as StylePreference,
    name: 'Business Casual',
    description: 'Professional yet relaxed style for modern workplaces',
    imageUrl: '/quiz-images/business-casual.jpg',
    tags: ['professional', 'modern', 'versatile']
  },
  {
    id: 'Avant-Garde' as StylePreference,
    name: 'Avant-Garde',
    description: 'Experimental, artistic style that pushes fashion boundaries',
    imageUrl: '/quiz-images/avant-garde.jpg',
    tags: ['experimental', 'artistic', 'innovative']
  },
  {
    id: 'Cottagecore' as StylePreference,
    name: 'Cottagecore',
    description: 'Romantic, pastoral style inspired by rural life and nature',
    imageUrl: '/quiz-images/cottagecore.jpg',
    tags: ['romantic', 'pastoral', 'nature']
  },
  {
    id: 'Edgy' as StylePreference,
    name: 'Edgy',
    description: 'Bold, rebellious style with dark elements and statement pieces',
    imageUrl: '/quiz-images/edgy.jpg',
    tags: ['bold', 'rebellious', 'statement']
  },
  {
    id: 'Athleisure' as StylePreference,
    name: 'Athleisure',
    description: 'Comfortable, sporty pieces that work for everyday wear',
    imageUrl: '/quiz-images/athleisure.jpg',
    tags: ['comfortable', 'sporty', 'casual']
  },
  {
    id: 'Casual Cool' as StylePreference,
    name: 'Casual Cool',
    description: 'Effortlessly stylish casual wear with a laid-back attitude',
    imageUrl: '/quiz-images/casual-cool.jpg',
    tags: ['effortless', 'stylish', 'laid-back']
  },
  {
    id: 'Romantic' as StylePreference,
    name: 'Romantic',
    description: 'Soft, feminine style with flowing fabrics and delicate details',
    imageUrl: '/quiz-images/romantic.jpg',
    tags: ['feminine', 'soft', 'delicate']
  },
  {
    id: 'Artsy' as StylePreference,
    name: 'Artsy',
    description: 'Creative, expressive style with unique pieces and artistic flair',
    imageUrl: '/quiz-images/artsy.jpg',
    tags: ['creative', 'expressive', 'unique']
  }
];

export function StyleFiltersStep({ onComplete }: StyleFiltersStepProps) {
  const { toast } = useToast();
  const { stylePreferences, setStylePreferences } = useOnboardingStore();
  const [selectedStyles, setSelectedStyles] = useState<StylePreference[]>(
    Array.isArray(stylePreferences) ? stylePreferences : []
  );

  const handleStyleToggle = (style: StylePreference) => {
    const currentStyles = Array.isArray(selectedStyles) ? selectedStyles : [];
    
    if (currentStyles.includes(style)) {
      setSelectedStyles(currentStyles.filter(s => s !== style));
    } else if (currentStyles.length < 3) {
      setSelectedStyles([...currentStyles, style]);
    } else {
      toast({
        title: "Maximum styles reached",
        description: "Please deselect one style before choosing another",
        variant: "destructive",
      });
    }
  };

  const handleComplete = () => {
    const currentStyles = Array.isArray(selectedStyles) ? selectedStyles : [];
    
    if (currentStyles.length === 0) {
      toast({
        title: "No styles selected",
        description: "Please select at least one style preference",
        variant: "destructive",
      });
      return;
    }

    setStylePreferences({ stylePreferences: currentStyles });
    onComplete();
  };

  useEffect(() => {
    if (Array.isArray(stylePreferences)) {
      setSelectedStyles(stylePreferences);
    }
  }, [stylePreferences]);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold">Style Filters</h2>
        <p className="text-gray-600">
          Choose your top 3 style preferences. We'll use these to curate personalized recommendations.
        </p>
        <div className="text-sm text-gray-500">
          {Array.isArray(selectedStyles) ? selectedStyles.length : 0}/3 styles selected
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {STYLE_OPTIONS.map((style) => {
          const currentStyles = Array.isArray(selectedStyles) ? selectedStyles : [];
          const isSelected = currentStyles.includes(style.id);
          const isDisabled = !isSelected && currentStyles.length >= 3;

          return (
            <Card
              key={style.id}
              className={`relative cursor-pointer transition-all duration-200 ${
                isSelected
                  ? 'ring-2 ring-primary border-primary'
                  : isDisabled
                  ? 'opacity-50 cursor-not-allowed'
                  : 'hover:border-primary/50 hover:shadow-md'
              }`}
              onClick={() => !isDisabled && handleStyleToggle(style.id)}
            >
              <div className="aspect-[4/3] relative overflow-hidden rounded-t-lg">
                <div className="w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                  <span className="text-gray-500 text-sm">Style Image</span>
                </div>
                {isSelected && (
                  <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}
              </div>
              
              <div className="p-4">
                <h3 className="font-semibold text-lg mb-2">{style.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{style.description}</p>
                
                <div className="flex flex-wrap gap-1 mb-3">
                  {style.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="flex justify-center">
        <Button 
          onClick={handleComplete}
          disabled={!Array.isArray(selectedStyles) || selectedStyles.length === 0}
          className="px-8"
        >
          Continue
        </Button>
      </div>
    </div>
  );
} 