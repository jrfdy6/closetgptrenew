import { useState } from "react";
import { useOnboardingStore } from "@/lib/store/onboardingStore";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { MultiSelect } from "@/components/ui/multi-select";
import { useToast } from "@/components/ui/use-toast";
import type { Occasion, FormalityLevel } from "@/lib/store/onboardingStore";

const OCCASIONS = [
  { value: "casual", label: "Casual" },
  { value: "business", label: "Business" },
  { value: "formal", label: "Formal" },
  { value: "sporty", label: "Sporty" },
  { value: "evening", label: "Evening" },
  { value: "beach", label: "Beach" },
  { value: "outdoor", label: "Outdoor" },
  { value: "party", label: "Party" },
  { value: "travel", label: "Travel" },
  { value: "home", label: "Home" },
];

const FORMALITY_LEVELS = [
  { value: "very_casual", label: "Very Casual" },
  { value: "casual", label: "Casual" },
  { value: "smart_casual", label: "Smart Casual" },
  { value: "business_casual", label: "Business Casual" },
  { value: "business", label: "Business" },
  { value: "formal", label: "Formal" },
  { value: "very_formal", label: "Very Formal" },
];

export function StylePreferencesStep({ onComplete }: { onComplete: () => void }) {
  const { toast } = useToast();
  const { 
    occasions, 
    formality, 
    setStylePreferences 
  } = useOnboardingStore();

  const handleComplete = () => {
    if (!occasions?.length) {
      toast({
        title: "Please select at least one occasion",
        description: "This helps us understand your lifestyle.",
        variant: "destructive",
      });
      return;
    }
    if (!formality) {
      toast({
        title: "Please select your preferred formality level",
        description: "This helps us suggest appropriate outfits.",
        variant: "destructive",
      });
      return;
    }
    onComplete();
  };

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        <div>
          <Label>Occasions</Label>
          <MultiSelect
            options={OCCASIONS}
            value={occasions || []}
            onChange={(value: Occasion[]) => setStylePreferences({ occasions: value })}
            placeholder="Select occasions"
          />
        </div>

        <div>
          <Label>Formality Level</Label>
          <Select
            value={formality}
            onValueChange={(value: FormalityLevel) => setStylePreferences({ formality: value })}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select formality level" />
            </SelectTrigger>
            <SelectContent>
              {FORMALITY_LEVELS.map((level) => (
                <SelectItem key={level.value} value={level.value}>
                  {level.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <Button onClick={handleComplete} className="w-full">
        Complete
      </Button>
    </div>
  );
} 