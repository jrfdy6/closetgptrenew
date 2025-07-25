import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, User, Ruler, Palette, ShoppingBag, Target } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepReview({ onNext, onPrevious }: StepProps) {
  const {
    name,
    email,
    gender,
    height,
    weight,
    bodyType,
    topSize,
    bottomSize,
    shoeSize,
    stylePreferences,
    shoppingPriorities,
    clothingTypes,
    colorPalette,
    quizResponses
  } = useOnboardingStore();

  const handleComplete = () => {
    onNext();
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-blue-500 rounded-full flex items-center justify-center">
            <Check className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="text-3xl font-bold">Review Your Profile</h2>
        <p className="text-muted-foreground text-lg">
          Let's review all the information we've collected about your style preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Information */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <User className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Basic Information</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Name:</span>
              <span className="font-medium">{name || 'Not provided'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Email:</span>
              <span className="font-medium">{email || 'Not provided'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Gender:</span>
              <span className="font-medium capitalize">{gender?.replace('-', ' ') || 'Not specified'}</span>
            </div>
          </div>
        </Card>

        {/* Measurements */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Ruler className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Measurements</h3>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Height:</span>
              <span className="font-medium">{height || 'Not provided'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Weight:</span>
              <span className="font-medium">{weight || 'Not provided'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Body Type:</span>
              <span className="font-medium">{bodyType || 'Not specified'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Sizes:</span>
              <span className="font-medium">
                {topSize && bottomSize ? `${topSize} / ${bottomSize}` : 'Not provided'}
              </span>
            </div>
          </div>
        </Card>

        {/* Style Preferences */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <Target className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Style Preferences</h3>
          </div>
          <div className="space-y-3">
            {stylePreferences && stylePreferences.length > 0 && (
              <div>
                <span className="text-sm text-muted-foreground">Preferred Styles:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {stylePreferences.map((style) => (
                    <Badge key={style} variant="secondary">
                      {style}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {shoppingPriorities && shoppingPriorities.length > 0 && (
              <div>
                <span className="text-sm text-muted-foreground">Shopping Priorities:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {shoppingPriorities.map((priority) => (
                    <Badge key={priority} variant="outline">
                      {priority}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Clothing Types */}
        <Card className="p-6">
          <div className="flex items-center space-x-3 mb-4">
            <ShoppingBag className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Clothing Types</h3>
          </div>
          <div className="space-y-2">
            {clothingTypes && clothingTypes.length > 0 ? (
              <div className="flex flex-wrap gap-1">
                {clothingTypes.map((type) => (
                  <Badge key={type} variant="secondary">
                    {type}
                  </Badge>
                ))}
              </div>
            ) : (
              <span className="text-muted-foreground">No clothing types selected</span>
            )}
          </div>
        </Card>

        {/* Color Palette */}
        <Card className="p-6 md:col-span-2">
          <div className="flex items-center space-x-3 mb-4">
            <Palette className="w-5 h-5 text-primary" />
            <h3 className="text-lg font-semibold">Color Palette</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {colorPalette && (
              <>
                <div>
                  <h4 className="font-medium text-sm mb-2">Primary Colors</h4>
                  <div className="flex flex-wrap gap-1">
                    {colorPalette.primary.map((color) => (
                      <Badge key={color} variant="outline" className="text-xs">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Secondary Colors</h4>
                  <div className="flex flex-wrap gap-1">
                    {colorPalette.secondary.map((color) => (
                      <Badge key={color} variant="outline" className="text-xs">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Accent Colors</h4>
                  <div className="flex flex-wrap gap-1">
                    {colorPalette.accent.map((color) => (
                      <Badge key={color} variant="outline" className="text-xs">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Neutral Colors</h4>
                  <div className="flex flex-wrap gap-1">
                    {colorPalette.neutral.map((color) => (
                      <Badge key={color} variant="outline" className="text-xs">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="font-medium text-sm mb-2">Colors to Avoid</h4>
                  <div className="flex flex-wrap gap-1">
                    {colorPalette.avoid.map((color) => (
                      <Badge key={color} variant="destructive" className="text-xs">
                        {color}
                      </Badge>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </Card>
      </div>

      <div className="flex justify-between items-center">
        <Button
          variant="outline"
          onClick={onPrevious}
          className="flex items-center"
        >
          Previous
        </Button>
        <Button
          onClick={handleComplete}
          className="flex items-center"
        >
          Complete Profile
        </Button>
      </div>
    </div>
  );
} 