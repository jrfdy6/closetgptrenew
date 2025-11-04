"use client";

import { useAccessibility } from "@/lib/hooks/useAccessibility";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Eye, Volume2, Vibrate } from "lucide-react";
import { useState, useEffect } from "react";

export default function AccessibilitySettings() {
  const { reducedMotion, highContrast, largeText, toggleHighContrast, toggleLargeText } = useAccessibility();
  const [soundsEnabled, setSoundsEnabled] = useState(false);
  const [hapticsEnabled, setHapticsEnabled] = useState(true);

  useEffect(() => {
    // Load preferences from localStorage
    const sounds = localStorage.getItem("soundsEnabled") === "true";
    const haptics = localStorage.getItem("hapticsEnabled") !== "false"; // Default true
    
    setSoundsEnabled(sounds);
    setHapticsEnabled(haptics);
  }, []);

  const handleSoundsToggle = (enabled: boolean) => {
    localStorage.setItem("soundsEnabled", String(enabled));
    setSoundsEnabled(enabled);
  };

  const handleHapticsToggle = (enabled: boolean) => {
    localStorage.setItem("hapticsEnabled", String(enabled));
    setHapticsEnabled(enabled);
  };

  return (
    <Card className="card-surface">
      <CardHeader>
        <CardTitle className="heading-md">Accessibility & Feedback</CardTitle>
        <CardDescription className="text-body-sm">
          Customize your experience for comfort and usability
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Visual Accessibility */}
        <div className="space-y-4">
          <h3 className="text-button text-gray-900 dark:text-[#F8F5F1]">
            <Eye className="w-4 h-4 inline mr-2" />
            Visual
          </h3>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="high-contrast" className="text-label cursor-pointer">
                High Contrast Mode
              </Label>
              <p className="text-caption text-gray-600 dark:text-[#8A827A]">
                Increases text contrast to WCAG AAA standards
              </p>
            </div>
            <Switch
              id="high-contrast"
              checked={highContrast}
              onCheckedChange={toggleHighContrast}
              aria-label="Toggle high contrast mode"
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="large-text" className="text-label cursor-pointer">
                Larger Text
              </Label>
              <p className="text-caption text-gray-600 dark:text-[#8A827A]">
                Increases base font size to 18px
              </p>
            </div>
            <Switch
              id="large-text"
              checked={largeText}
              onCheckedChange={toggleLargeText}
              aria-label="Toggle large text mode"
            />
          </div>

          {reducedMotion && (
            <div className="p-3 bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800 rounded-lg">
              <p className="text-body-sm text-blue-800 dark:text-blue-200">
                ✓ Reduced motion is enabled (system setting)
              </p>
            </div>
          )}
        </div>

        {/* Audio & Haptic Feedback */}
        <div className="space-y-4">
          <h3 className="text-button text-gray-900 dark:text-[#F8F5F1]">
            <Volume2 className="w-4 h-4 inline mr-2" />
            Sounds & Feedback
          </h3>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="sounds" className="text-label cursor-pointer">
                Sound Effects
              </Label>
              <p className="text-caption text-gray-600 dark:text-[#8A827A]">
                Plays soft sounds for saves & achievements (silent by default)
              </p>
            </div>
            <Switch
              id="sounds"
              checked={soundsEnabled}
              onCheckedChange={handleSoundsToggle}
              aria-label="Toggle sound effects"
            />
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="haptics" className="text-label cursor-pointer">
                <Vibrate className="w-4 h-4 inline mr-1" />
                Haptic Feedback
              </Label>
              <p className="text-caption text-gray-600 dark:text-[#8A827A]">
                Vibration feedback for key actions
              </p>
            </div>
            <Switch
              id="haptics"
              checked={hapticsEnabled}
              onCheckedChange={handleHapticsToggle}
              aria-label="Toggle haptic feedback"
            />
          </div>
        </div>

        {/* Info Note */}
        <div className="p-4 bg-gray-50 dark:bg-[#3D2F24] rounded-lg">
          <p className="text-body-sm text-gray-700 dark:text-[#C4BCB4]">
            <strong>Note:</strong> Visual feedback is always present. Sound and haptic feedback are optional enhancements for a multisensory experience.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

