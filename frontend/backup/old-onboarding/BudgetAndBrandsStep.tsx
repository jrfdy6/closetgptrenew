import { useState, useEffect } from 'react';
import { useOnboardingStore, BudgetRange } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/components/ui/use-toast';
import { SkipForward, Plus, X } from 'lucide-react';

interface BudgetAndBrandsStepProps {
  onComplete: () => void;
}

const BUDGET_OPTIONS = [
  {
    value: 'budget' as BudgetRange,
    label: 'Budget-Friendly',
    description: '$20-50 per item',
    icon: '💰'
  },
  {
    value: 'mid-range' as BudgetRange,
    label: 'Mid-Range',
    description: '$50-150 per item',
    icon: '💳'
  },
  {
    value: 'premium' as BudgetRange,
    label: 'Premium',
    description: '$150-500 per item',
    icon: '✨'
  },
  {
    value: 'luxury' as BudgetRange,
    label: 'Luxury',
    description: '$500+ per item',
    icon: '👑'
  }
];

const POPULAR_BRANDS = [
  'Nike', 'Adidas', 'Zara', 'H&M', 'Uniqlo', 'Gap', 'Old Navy',
  'Target', 'Walmart', 'Amazon', 'ASOS', 'Forever 21', 'Urban Outfitters',
  'Anthropologie', 'Free People', 'Lululemon', 'Athleta', 'Patagonia',
  'North Face', 'Columbia', 'Levi\'s', 'Wrangler', 'Dockers',
  'Calvin Klein', 'Tommy Hilfiger', 'Ralph Lauren', 'Polo', 'Nautica'
];

export function BudgetAndBrandsStep({ onComplete }: BudgetAndBrandsStepProps) {
  const { toast } = useToast();
  const { budget, preferredBrands, setStylePreferences } = useOnboardingStore();
  const [newBrand, setNewBrand] = useState('');
  const [selectedBrands, setSelectedBrands] = useState<string[]>(
    Array.isArray(preferredBrands) ? preferredBrands : []
  );

  const handleBudgetSelect = (value: BudgetRange) => {
    setStylePreferences({ budget: value });
  };

  const handleAddBrand = () => {
    const currentBrands = Array.isArray(selectedBrands) ? selectedBrands : [];
    if (newBrand.trim() && !currentBrands.includes(newBrand.trim())) {
      setSelectedBrands([...currentBrands, newBrand.trim()]);
      setNewBrand('');
    }
  };

  const handleRemoveBrand = (brand: string) => {
    const currentBrands = Array.isArray(selectedBrands) ? selectedBrands : [];
    setSelectedBrands(currentBrands.filter(b => b !== brand));
  };

  const handleAddPopularBrand = (brand: string) => {
    const currentBrands = Array.isArray(selectedBrands) ? selectedBrands : [];
    if (!currentBrands.includes(brand)) {
      setSelectedBrands([...currentBrands, brand]);
    }
  };

  const handleComplete = () => {
    const currentBrands = Array.isArray(selectedBrands) ? selectedBrands : [];
    setStylePreferences({ preferredBrands: currentBrands });
    onComplete();
  };

  useEffect(() => {
    if (Array.isArray(preferredBrands)) {
      setSelectedBrands(preferredBrands);
    }
  }, [preferredBrands]);

  const handleSkip = () => {
    toast({
      title: "Skipped budget & brands",
      description: "You can always add these later in your profile settings",
    });
    onComplete();
  };

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Budget & Brands</h2>
        <p className="text-gray-600 mb-6">
          Help us recommend items within your budget and from your favorite brands.
        </p>

        <div className="space-y-6">
          {/* Budget Range */}
          <div>
            <Label className="text-base font-medium">Budget Range</Label>
            <p className="text-sm text-gray-500 mb-4">
              What's your typical budget for clothing items?
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {BUDGET_OPTIONS.map((option) => (
                <Card
                  key={option.value}
                  className={`p-4 cursor-pointer transition-all ${
                    budget === option.value
                      ? 'border-primary ring-2 ring-primary'
                      : 'hover:border-primary/50'
                  }`}
                  onClick={() => handleBudgetSelect(option.value)}
                >
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{option.icon}</span>
                    <div>
                      <h3 className="font-medium">{option.label}</h3>
                      <p className="text-sm text-gray-600">{option.description}</p>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Preferred Brands */}
          <div>
            <Label className="text-base font-medium">Preferred Brands</Label>
            <p className="text-sm text-gray-500 mb-4">
              Add brands you love or frequently shop from
            </p>

            {/* Add Brand Input */}
            <div className="flex gap-2 mb-4">
              <Input
                value={newBrand}
                onChange={(e) => setNewBrand(e.target.value)}
                placeholder="Add a brand name"
                onKeyPress={(e) => e.key === 'Enter' && handleAddBrand()}
              />
              <Button 
                onClick={handleAddBrand}
                disabled={!newBrand.trim()}
                size="sm"
              >
                <Plus className="w-4 h-4" />
              </Button>
            </div>

            {/* Selected Brands */}
            {Array.isArray(selectedBrands) && selectedBrands.length > 0 && (
              <div className="mb-4">
                <Label className="text-sm font-medium">Your Brands</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {selectedBrands.map((brand) => (
                    <div
                      key={brand}
                      className="flex items-center gap-1 px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                    >
                      {brand}
                      <button
                        onClick={() => handleRemoveBrand(brand)}
                        className="ml-1 hover:bg-primary/20 rounded-full p-0.5"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Popular Brands */}
            <div>
              <Label className="text-sm font-medium">Popular Brands</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {POPULAR_BRANDS.map((brand) => {
                  const currentBrands = Array.isArray(selectedBrands) ? selectedBrands : [];
                  const isSelected = currentBrands.includes(brand);
                  
                  return (
                    <button
                      key={brand}
                      onClick={() => handleAddPopularBrand(brand)}
                      disabled={isSelected}
                      className={`px-3 py-1 rounded-full text-sm transition-all ${
                        isSelected
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-gray-100 text-gray-700 hover:bg-primary/10 hover:text-primary'
                      }`}
                    >
                      {brand}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-between">
          <Button 
            variant="ghost" 
            onClick={handleSkip}
            className="text-gray-500"
          >
            <SkipForward className="w-4 h-4 mr-2" />
            Skip for now
          </Button>
          <Button onClick={handleComplete}>
            Continue
          </Button>
        </div>
      </Card>
    </div>
  );
} 