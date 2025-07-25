'use client';

import { useState } from 'react';
import { useOnboardingStore, ClothingType } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Check, Shirt, Users, Heart, Layers, Footprints, ShoppingBag, Dumbbell, Briefcase } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepClothingTypes({ onNext, onSkip }: StepProps) {
  const { toast } = useToast();
  const { clothingTypes, setStylePreferences } = useOnboardingStore();
  const [selectedTypes, setSelectedTypes] = useState<ClothingType[]>(
    clothingTypes || []
  );

  const clothingTypeOptions = [
    {
      id: 'tops' as ClothingType,
      title: 'Tops',
      description: 'Shirts, blouses, sweaters, t-shirts',
      icon: Shirt,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      examples: 'T-shirts, blouses, sweaters, button-downs'
    },
    {
      id: 'bottoms' as ClothingType,
      title: 'Bottoms',
      description: 'Pants, jeans, skirts, shorts',
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      examples: 'Jeans, trousers, skirts, shorts'
    },
    {
      id: 'dresses' as ClothingType,
      title: 'Dresses',
      description: 'One-piece outfits for any occasion',
      icon: Heart,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100',
      examples: 'Casual dresses, formal gowns, maxi dresses'
    },
    {
      id: 'outerwear' as ClothingType,
      title: 'Outerwear',
      description: 'Jackets, coats, blazers',
      icon: Layers,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      examples: 'Jackets, coats, blazers, cardigans'
    },
    {
      id: 'shoes' as ClothingType,
      title: 'Shoes',
      description: 'Footwear for every occasion',
      icon: Footprints,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      examples: 'Sneakers, heels, boots, sandals'
    },
    {
      id: 'accessories' as ClothingType,
      title: 'Accessories',
      description: 'Bags, jewelry, scarves, belts',
      icon: ShoppingBag,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      examples: 'Handbags, jewelry, scarves, belts'
    },
    {
      id: 'activewear' as ClothingType,
      title: 'Activewear',
      description: 'Workout and athletic clothing',
      icon: Dumbbell,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      examples: 'Leggings, sports bras, workout tops'
    },
    {
      id: 'formal' as ClothingType,
      title: 'Formal Wear',
      description: 'Business and special occasion attire',
      icon: Briefcase,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
      examples: 'Suits, formal dresses, business attire'
    }
  ];

  const handleTypeToggle = (type: ClothingType) => {
    setSelectedTypes(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  const handleNext = () => {
    if (selectedTypes.length === 0) {
      toast({
        title: "Please select at least one clothing type",
        description: "This helps us understand what you're looking for.",
        variant: "destructive",
      });
      return;
    }

    setStylePreferences({ clothingTypes: selectedTypes });
    onNext();
  };

  const handleSkip = () => {
    onSkip?.();
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold">What are you looking for?</h2>
        <p className="text-muted-foreground text-lg">
          Select the types of clothing you're most interested in.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {clothingTypeOptions.map((type) => {
          const IconComponent = type.icon;
          return (
            <Card
              key={type.id}
              className={`p-4 cursor-pointer transition-all hover:shadow-md ${
                selectedTypes.includes(type.id)
                  ? 'ring-2 ring-primary bg-primary/5'
                  : ''
              }`}
              onClick={() => handleTypeToggle(type.id)}
            >
              <div className="space-y-3">
                <div className="flex flex-col items-center space-y-2">
                  <div className={`w-12 h-12 ${type.bgColor} rounded-full flex items-center justify-center`}>
                    <IconComponent className={`w-6 h-6 ${type.color}`} />
                  </div>
                  <div className="text-center">
                    <h3 className="font-semibold">{type.title}</h3>
                    <p className="text-xs text-muted-foreground">{type.description}</p>
                  </div>
                </div>
                {selectedTypes.includes(type.id) && (
                  <div className="flex justify-center">
                    <Check className="w-5 h-5 text-primary" />
                  </div>
                )}
                <p className="text-xs text-muted-foreground text-center">
                  {type.examples}
                </p>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={handleSkip}
          className="flex items-center"
        >
          Skip for now
        </Button>
        <Button
          onClick={handleNext}
          className="flex items-center"
          disabled={selectedTypes.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
} 