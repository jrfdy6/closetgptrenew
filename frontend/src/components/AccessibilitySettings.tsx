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
    <Card className="bg-card/85 dark:bg-card/85 border border-border/60 dark:border-border/70 rounded-3xl shadow-lg backdrop-blur-xl">
      <CardHeader>
        <CardTitle className="text-xl font-display text-card-foreground">
          Accessibility & feedback
        </CardTitle>
        <CardDescription className="text-sm text-muted-foreground">
          Customize your experience for comfort and usability.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Visual Accessibility */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            <Eye className="w-4 h-4 inline mr-2 text-primary" />
            Visual comfort
          </h3>
          
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="high-contrast" className="text-sm font-medium text-card-foreground cursor-pointer">
                High contrast mode
              </Label>
              <p className="text-xs text-muted-foreground">
                Increases text contrast to WCAG AAA standards.
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
              <Label htmlFor="large-text" className="text-sm font-medium text-card-foreground cursor-pointer">
                Larger text
              </Label>
              <p className="text-xs text-muted-foreground">
                Increases base font size to 18px.
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
            <div className="p-3 bg-secondary/90 dark:bg-card border border-border/60 dark:border-border/70 rounded-2xl">
              <p className="text-sm text-accent dark:text-accent">
                ✓ Reduced motion detected from your system settings.
              </p>
            </div>
          )}
        </div>

        {/* Audio & Haptic Feedback */}
        <div className="space-y-4">
          <h3 className="text-sm font-semibold tracking-wide uppercase text-muted-foreground">
            <Volume2 className="w-4 h-4 inline mr-2 text-primary" />
            Sounds & feedback
          </h3>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label htmlFor="sounds" className="text-sm font-medium text-card-foreground cursor-pointer">
                Sound effects
              </Label>
              <p className="text-xs text-muted-foreground">
                Plays soft sounds for saves and achievements (silent by default).
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
              <Label htmlFor="haptics" className="text-sm font-medium text-card-foreground cursor-pointer">
                <Vibrate className="w-4 h-4 inline mr-1" />
                Haptic feedback
              </Label>
              <p className="text-xs text-muted-foreground">
                Subtle vibration feedback for key actions.
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
        <div className="p-4 bg-secondary/80 dark:bg-card/85 border border-border/60 dark:border-border/70 rounded-2xl">
          <p className="text-sm text-muted-foreground">
            <span className="font-semibold text-card-foreground">Note:</span> Visual feedback is always present. Sound and haptic feedback are optional enhancements for a multisensory experience.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

