import { useOnboardingStore, Gender } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { Check, Shirt, Users } from 'lucide-react';
import type { StepProps } from '../StepWizard';

export function StepSizePicker({ onNext, onPrevious }: StepProps) {
  const { toast } = useToast();
  const { gender, topSize, bottomSize, dressSize, jeanWaist, braSize, shoeSize, setMeasurements } = useOnboardingStore();

  // Gender-specific size options
  const getSizeOptions = (gender: Gender) => {
    if (gender === 'male') {
      return {
        top: ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'],
        bottom: ['28', '29', '30', '31', '32', '33', '34', '36', '38', '40', '42', '44'],
        shoe: ['7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '11.5', '12', '13'],
        dress: [] as string[],
        jeanWaist: [] as string[],
        bra: [] as string[],
      };
    } else if (gender === 'female') {
      return {
        top: ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18'],
        bottom: ['00', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24'],
        dress: ['00', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24'],
        jeanWaist: ['23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40'],
        bra: ['30A', '30B', '30C', '30D', '32A', '32B', '32C', '32D', '34A', '34B', '34C', '34D', '36A', '36B', '36C', '36D', '38A', '38B', '38C', '38D', '40A', '40B', '40C', '40D'],
        shoe: ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11'],
      };
    } else {
      // Non-binary: show both men's and women's sizes
      return {
        top: ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18'],
        bottom: ['00', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24', '28', '29', '30', '31', '32', '33', '34', '36', '38', '40', '42', '44'],
        dress: ['00', '0', '2', '4', '6', '8', '10', '12', '14', '16', '18', '20', '22', '24'],
        jeanWaist: ['23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40'],
        bra: ['30A', '30B', '30C', '30D', '32A', '32B', '32C', '32D', '34A', '34B', '34C', '34D', '36A', '36B', '36C', '36D', '38A', '38B', '38C', '38D', '40A', '40B', '40C', '40D'],
        shoe: ['5', '5.5', '6', '6.5', '7', '7.5', '8', '8.5', '9', '9.5', '10', '10.5', '11', '12', '13'],
      };
    }
  };

  const sizeOptions = getSizeOptions(gender);

  const handleNext = () => {
    // For women, require at least one size to be selected
    if (gender === 'female' && !topSize && !bottomSize && !dressSize && !jeanWaist && !braSize && !shoeSize) {
      toast({
        title: "Please select at least one size",
        description: "This helps us provide better size recommendations.",
        variant: "destructive",
      });
      return;
    }
    // For men and non-binary, require at least one size
    if ((gender === 'male' || gender === 'non-binary') && !topSize && !bottomSize && !shoeSize) {
      toast({
        title: "Please select at least one size",
        description: "This helps us provide better size recommendations.",
        variant: "destructive",
      });
      return;
    }
    onNext();
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          What are your typical sizes?
        </h2>
        <p className="text-lg text-gray-600">
          Select your typical sizes for tops, bottoms, and shoes.
        </p>
      </div>

      <Card className="p-6">
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="topSize">Top Size</Label>
            <Select value={topSize} onValueChange={(value) => setMeasurements({ topSize: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select top size" />
              </SelectTrigger>
              <SelectContent>
                {sizeOptions.top.map((size) => (
                  <SelectItem key={size} value={size}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="bottomSize">Bottom Size</Label>
            <Select value={bottomSize} onValueChange={(value) => setMeasurements({ bottomSize: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select bottom size" />
              </SelectTrigger>
              <SelectContent>
                {sizeOptions.bottom.map((size) => (
                  <SelectItem key={size} value={size}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="shoeSize">Shoe Size</Label>
            <Select value={shoeSize} onValueChange={(value) => setMeasurements({ shoeSize: value })}>
              <SelectTrigger>
                <SelectValue placeholder="Select shoe size" />
              </SelectTrigger>
              <SelectContent>
                {sizeOptions.shoe.map((size) => (
                  <SelectItem key={size} value={size}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Women's specific sizes */}
          {(gender === 'female' || gender === 'non-binary') && (
            <>
              <div className="space-y-2">
                <Label htmlFor="dressSize">Dress Size</Label>
                <Select value={dressSize} onValueChange={(value) => setMeasurements({ dressSize: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select dress size" />
                  </SelectTrigger>
                  <SelectContent>
                    {sizeOptions.dress.map((size) => (
                      <SelectItem key={size} value={size}>
                        {size}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="jeanWaist">Jean Waist</Label>
                <Select value={jeanWaist} onValueChange={(value) => setMeasurements({ jeanWaist: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select jean waist" />
                  </SelectTrigger>
                  <SelectContent>
                    {sizeOptions.jeanWaist.map((size) => (
                      <SelectItem key={size} value={size}>
                        {size}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="braSize">Bra Size</Label>
                <Select value={braSize} onValueChange={(value) => setMeasurements({ braSize: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select bra size" />
                  </SelectTrigger>
                  <SelectContent>
                    {sizeOptions.bra.map((size) => (
                      <SelectItem key={size} value={size}>
                        {size}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext}>
          Next
        </Button>
      </div>
    </div>
  );
} 