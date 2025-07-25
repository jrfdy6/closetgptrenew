'use client';

import { useState } from 'react';
import { useOnboardingStore, ShoppingPriority } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/use-toast';
import { Check, Target, Clock, DollarSign, Star, Zap, Leaf } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepShoppingPriorities({ onNext, onSkip }: StepProps) {
  const { toast } = useToast();
  const { shoppingPriorities, setStylePreferences } = useOnboardingStore();
  const [selectedPriorities, setSelectedPriorities] = useState<ShoppingPriority[]>(
    shoppingPriorities || []
  );

  const priorityOptions = [
    {
      id: 'quality' as ShoppingPriority,
      title: 'Quality',
      description: 'I prioritize well-made, durable pieces',
      icon: Star,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
      examples: 'Premium fabrics, excellent craftsmanship, long-lasting items'
    },
    {
      id: 'price' as ShoppingPriority,
      title: 'Price',
      description: 'I look for the best value for money',
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      examples: 'Sales, discounts, affordable options, good deals'
    },
    {
      id: 'trends' as ShoppingPriority,
      title: 'Trends',
      description: 'I want to stay current with fashion',
      icon: Zap,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      examples: 'Latest styles, seasonal pieces, fashion-forward items'
    },
    {
      id: 'comfort' as ShoppingPriority,
      title: 'Comfort',
      description: 'I prioritize feeling good in my clothes',
      icon: Target,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      examples: 'Soft fabrics, relaxed fits, easy-to-wear pieces'
    },
    {
      id: 'versatility' as ShoppingPriority,
      title: 'Versatility',
      description: 'I want pieces that work for multiple occasions',
      icon: Clock,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
      examples: 'Mix-and-match items, transitional pieces, multi-purpose clothing'
    },
    {
      id: 'sustainability' as ShoppingPriority,
      title: 'Sustainability',
      description: 'I care about ethical and eco-friendly fashion',
      icon: Leaf,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100',
      examples: 'Eco-friendly materials, ethical brands, second-hand options'
    }
  ];

  const handlePriorityToggle = (priority: ShoppingPriority) => {
    setSelectedPriorities(prev =>
      prev.includes(priority)
        ? prev.filter(p => p !== priority)
        : [...prev, priority]
    );
  };

  const handleNext = () => {
    if (selectedPriorities.length === 0) {
      toast({
        title: "Please select at least one priority",
        description: "This helps us understand what matters most to you when shopping.",
        variant: "destructive",
      });
      return;
    }

    setStylePreferences({ shoppingPriorities: selectedPriorities });
    onNext();
  };

  const handleSkip = () => {
    onSkip?.();
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold">What's important to you?</h2>
        <p className="text-muted-foreground text-lg">
          Select the factors that matter most when you're shopping for clothes.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {priorityOptions.map((priority) => {
          const IconComponent = priority.icon;
          return (
            <Card
              key={priority.id}
              className={`p-6 cursor-pointer transition-all hover:shadow-md ${
                selectedPriorities.includes(priority.id)
                  ? 'ring-2 ring-primary bg-primary/5'
                  : ''
              }`}
              onClick={() => handlePriorityToggle(priority.id)}
            >
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 ${priority.bgColor} rounded-full flex items-center justify-center`}>
                    <IconComponent className={`w-5 h-5 ${priority.color}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{priority.title}</h3>
                    <p className="text-sm text-muted-foreground">{priority.description}</p>
                  </div>
                  {selectedPriorities.includes(priority.id) && (
                    <Check className="w-5 h-5 text-primary" />
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  Examples: {priority.examples}
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
          disabled={selectedPriorities.length === 0}
        >
          Continue
        </Button>
      </div>
    </div>
  );
} 