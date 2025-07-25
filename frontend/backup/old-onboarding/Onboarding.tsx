import { useState } from "react";
import { useRouter } from "next/navigation";
import { useUserProfile } from "@/hooks/useUserProfile";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/components/ui/use-toast";

const BODY_TYPES = [
  "Athletic",
  "Curvy",
  "Rectangular",
  "Hourglass",
  "Pear",
  "Apple",
  "Inverted Triangle",
];

const SKIN_TONES = [
  "Warm",
  "Cool",
  "Neutral",
  "Olive",
  "Deep",
  "Medium",
  "Fair",
];

const STYLE_PREFERENCES = [
  "Minimal Luxe",
  "Gorpcore",
  "Boho",
  "Streetwear",
  "Old Money",
  "Clean Girl",
  "Korean Core",
  "Y2K",
  "Coastal Grandmother",
  "Dark Academia",
];

const OCCASIONS = [
  "Casual",
  "Work",
  "Party",
  "Formal",
  "Date Night",
  "Brunch",
  "Travel",
  "Gym",
  "Beach",
  "Outdoor",
];

export default function Onboarding() {
  const router = useRouter();
  const { toast } = useToast();
  const { updateProfile } = useUserProfile();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  // Form states
  const [name, setName] = useState("");
  const [bodyType, setBodyType] = useState("");
  const [skinTone, setSkinTone] = useState("");
  const [height, setHeight] = useState("");
  const [weight, setWeight] = useState("");
  const [selectedStyles, setSelectedStyles] = useState<string[]>([]);
  const [selectedOccasions, setSelectedOccasions] = useState<string[]>([]);
  const [selectedColors, setSelectedColors] = useState<string[]>([]);

  const handleStyleToggle = (style: string) => {
    setSelectedStyles(prev =>
      prev.includes(style)
        ? prev.filter(s => s !== style)
        : [...prev, style]
    );
  };

  const handleOccasionToggle = (occasion: string) => {
    setSelectedOccasions(prev =>
      prev.includes(occasion)
        ? prev.filter(o => o !== occasion)
        : [...prev, occasion]
    );
  };

  const handleColorToggle = (color: string) => {
    setSelectedColors(prev =>
      prev.includes(color)
        ? prev.filter(c => c !== color)
        : [...prev, color]
    );
  };

  const handleSubmit = async () => {
    if (!name || !bodyType || !skinTone || !height || !weight || selectedStyles.length === 0) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    setLoading(true);
    try {
      await updateProfile({
        name,
        preferences: {
          style: selectedStyles,
          colors: selectedColors,
          occasions: selectedOccasions,
        },
        measurements: {
          height: Number(height),
          weight: Number(weight),
          bodyType,
          skinTone,
        },
      });

      toast({
        title: "Profile Created",
        description: "Your style profile has been set up successfully!",
      });

      router.push("/dashboard");
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create profile. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="max-w-2xl mx-auto">
        <CardHeader>
          <CardTitle>Welcome to ClosetGPT!</CardTitle>
          <p className="text-muted-foreground">
            Let's set up your style profile to get personalized outfit recommendations.
          </p>
        </CardHeader>
        <CardContent>
          {step === 1 && (
            <div className="space-y-4">
              <div>
                <Label htmlFor="name">What's your name?</Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Enter your name"
                />
              </div>
              <div>
                <Label htmlFor="bodyType">What's your body type?</Label>
                <Select value={bodyType} onValueChange={setBodyType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your body type" />
                  </SelectTrigger>
                  <SelectContent>
                    {BODY_TYPES.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="skinTone">What's your skin tone?</Label>
                <Select value={skinTone} onValueChange={setSkinTone}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select your skin tone" />
                  </SelectTrigger>
                  <SelectContent>
                    {SKIN_TONES.map((tone) => (
                      <SelectItem key={tone} value={tone}>
                        {tone}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="height">Height (cm)</Label>
                  <Input
                    id="height"
                    type="number"
                    value={height}
                    onChange={(e) => setHeight(e.target.value)}
                    placeholder="Enter your height"
                  />
                </div>
                <div>
                  <Label htmlFor="weight">Weight (kg)</Label>
                  <Input
                    id="weight"
                    type="number"
                    value={weight}
                    onChange={(e) => setWeight(e.target.value)}
                    placeholder="Enter your weight"
                  />
                </div>
              </div>
              <Button
                className="w-full"
                onClick={() => setStep(2)}
                disabled={!name || !bodyType || !skinTone || !height || !weight}
              >
                Next
              </Button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div>
                <Label>Select your style preferences</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {STYLE_PREFERENCES.map((style) => (
                    <div key={style} className="flex items-center space-x-2">
                      <Checkbox
                        id={style}
                        checked={selectedStyles.includes(style)}
                        onCheckedChange={() => handleStyleToggle(style)}
                      />
                      <Label htmlFor={style}>{style}</Label>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <Label>Select your preferred occasions</Label>
                <div className="grid grid-cols-2 gap-2 mt-2">
                  {OCCASIONS.map((occasion) => (
                    <div key={occasion} className="flex items-center space-x-2">
                      <Checkbox
                        id={occasion}
                        checked={selectedOccasions.includes(occasion)}
                        onCheckedChange={() => handleOccasionToggle(occasion)}
                      />
                      <Label htmlFor={occasion}>{occasion}</Label>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setStep(1)}>
                  Back
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={loading || selectedStyles.length === 0}
                >
                  {loading ? "Creating Profile..." : "Complete Setup"}
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 