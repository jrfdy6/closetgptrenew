import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { CheckCircle, Edit } from 'lucide-react';

interface ReviewStepProps {
  onComplete: () => void;
  onEdit: (step: number) => void;
}

export function ReviewStep({ onComplete, onEdit }: ReviewStepProps) {
  const {
    name,
    gender,
    selfieUrl,
    height,
    weight,
    bodyType,
    skinTone,
    topSize,
    bottomSize,
    shoeSize,
    stylePreferences,
    occasions,
    formality,
    budget,
    preferredBrands
  } = useOnboardingStore();

  const heightInFeet = Math.floor((parseInt(height) || 0) / 12);
  const heightInInches = (parseInt(height) || 0) % 12;

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <div className="text-center space-y-4">
        <h2 className="text-2xl font-bold">Review Your Profile</h2>
        <p className="text-gray-600">
          Please review your information before we create your personalized style profile.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Basic Information */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Basic Information</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(1)}
              className="text-gray-500"
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Name:</span>
              <span className="font-medium">{name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Gender:</span>
              <span className="font-medium capitalize">{gender}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Body Type:</span>
              <span className="font-medium">{bodyType}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Skin Tone:</span>
              <span className="font-medium">
                {skinTone && skinTone.id 
                  ? `${skinTone.depth} ${skinTone.undertone}` 
                  : 'Not selected'}
              </span>
            </div>
            {selfieUrl && (
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-sm text-gray-600">Selfie uploaded</span>
              </div>
            )}
          </div>
        </Card>

        {/* Measurements */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Measurements</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(2)}
              className="text-gray-500"
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
          
          <div className="space-y-3">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Height:</span>
                <p className="font-medium">
                  {heightInFeet}'{heightInInches}" ({height} inches)
                </p>
              </div>
              <div>
                <span className="text-gray-500">Weight:</span>
                <p className="font-medium">{weight} lbs</p>
              </div>
            </div>
            
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div>
                <span className="text-gray-500">Top:</span>
                <p className="font-medium">{topSize || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-gray-500">Bottom:</span>
                <p className="font-medium">{bottomSize || 'Not specified'}</p>
              </div>
              <div>
                <span className="text-gray-500">Shoes:</span>
                <p className="font-medium">{shoeSize || 'Not specified'}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Style Preferences */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Style Preferences</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(3)}
              className="text-gray-500"
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
          
          <div className="space-y-3">
            <div>
              <span className="text-gray-500 text-sm">Selected Styles:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {Array.isArray(stylePreferences) && stylePreferences.length > 0 ? (
                  stylePreferences.map((style) => (
                    <Badge key={style} variant="secondary" className="text-xs">
                      {style}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-gray-400">No styles selected</span>
                )}
              </div>
            </div>
            
            <div>
              <span className="text-gray-500 text-sm">Occasions:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {Array.isArray(occasions) && occasions.length > 0 ? (
                  occasions.map((occasion) => (
                    <Badge key={occasion} variant="outline" className="text-xs">
                      {occasion}
                    </Badge>
                  ))
                ) : (
                  <span className="text-sm text-gray-400">No occasions selected</span>
                )}
              </div>
            </div>
            
            <div>
              <span className="text-gray-500 text-sm">Formality:</span>
              <p className="font-medium capitalize">{formality?.replace('_', ' ') || 'Not specified'}</p>
            </div>
          </div>
        </Card>

        {/* Budget & Brands */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Budget & Brands</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onEdit(4)}
              className="text-gray-500"
            >
              <Edit className="w-4 h-4 mr-1" />
              Edit
            </Button>
          </div>
          
          <div className="space-y-3">
            <div>
              <span className="text-gray-500 text-sm">Budget Range:</span>
              <p className="font-medium capitalize">{budget?.replace('-', ' ') || 'Not specified'}</p>
            </div>
            
            {Array.isArray(preferredBrands) && preferredBrands.length > 0 ? (
              <div>
                <span className="text-gray-500 text-sm">Preferred Brands:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {preferredBrands.slice(0, 5).map((brand) => (
                    <Badge key={brand} variant="outline" className="text-xs">
                      {brand}
                    </Badge>
                  ))}
                  {preferredBrands.length > 5 && (
                    <Badge variant="outline" className="text-xs">
                      +{preferredBrands.length - 5} more
                    </Badge>
                  )}
                </div>
              </div>
            ) : (
              <div>
                <span className="text-gray-500 text-sm">Preferred Brands:</span>
                <span className="text-sm text-gray-400">No brands selected</span>
              </div>
            )}
          </div>
        </Card>
      </div>

      <div className="text-center space-y-4">
        <p className="text-sm text-gray-600">
          Ready to create your personalized style profile? We'll use this information to provide you with tailored outfit recommendations.
        </p>
        <Button onClick={onComplete} size="lg" className="px-8">
          Create My Profile
        </Button>
      </div>
    </div>
  );
} 