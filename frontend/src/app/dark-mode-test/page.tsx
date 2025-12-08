"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Moon, Sun, Check, Palette } from 'lucide-react';
import Navigation from '@/components/Navigation';

// Dark mode variations configuration
const variations = [
  {
    id: 'navy',
    name: 'Deep Navy Midnight',
    description: 'Sophisticated midnight blue with amber gold accents',
    colors: {
      background: '#0F1419',
      card: '#1A2330',
      border: '#2F3A47',
      hover: '#2A3441',
    },
    css: {
      '--background': '220 30% 8%',
      '--foreground': '30 10% 97%',
      '--card': '220 25% 12%',
      '--card-foreground': '30 10% 97%',
      '--popover': '220 25% 12%',
      '--popover-foreground': '30 10% 97%',
      '--primary': '38 92% 63%',
      '--primary-foreground': '220 30% 8%',
      '--secondary': '220 20% 18%',
      '--secondary-foreground': '30 10% 97%',
      '--muted': '220 20% 18%',
      '--muted-foreground': '30 8% 75%',
      '--accent': '33 100% 56%',
      '--accent-foreground': '220 30% 8%',
      '--destructive': '0 72% 51%',
      '--destructive-foreground': '0 0% 98%',
      '--border': '220 20% 20%',
      '--input': '220 20% 18%',
      '--ring': '38 92% 63%',
      '--surface': '220 25% 12%',
      '--surface-variant': '220 20% 18%',
    },
    bodyGradient: 'linear-gradient(135deg, #0F1419 0%, #1A2330 50%, #0F1419 100%)',
  },
  {
    id: 'black',
    name: 'Pure Black Luxury',
    description: 'Rich true black with amber gold accents - high contrast, modern',
    colors: {
      background: '#0D0D0D',
      card: '#1A1A1A',
      border: '#2E2E2E',
      hover: '#262626',
    },
    css: {
      '--background': '0 0% 5%',
      '--foreground': '30 10% 97%',
      '--card': '0 0% 10%',
      '--card-foreground': '30 10% 97%',
      '--popover': '0 0% 10%',
      '--popover-foreground': '30 10% 97%',
      '--primary': '38 92% 63%',
      '--primary-foreground': '0 0% 5%',
      '--secondary': '0 0% 15%',
      '--secondary-foreground': '30 10% 97%',
      '--muted': '0 0% 15%',
      '--muted-foreground': '30 8% 75%',
      '--accent': '33 100% 56%',
      '--accent-foreground': '0 0% 5%',
      '--destructive': '0 72% 51%',
      '--destructive-foreground': '0 0% 98%',
      '--border': '0 0% 18%',
      '--input': '0 0% 15%',
      '--ring': '38 92% 63%',
      '--surface': '0 0% 10%',
      '--surface-variant': '0 0% 15%',
    },
    bodyGradient: 'linear-gradient(135deg, #0D0D0D 0%, #1A1A1A 50%, #0D0D0D 100%)',
  },
  {
    id: 'plum',
    name: 'Deep Plum Elegance',
    description: 'Rich deep purple/plum with amber gold accents - elegant and warm',
    colors: {
      background: '#1A141D',
      card: '#251F2B',
      border: '#3A3244',
      hover: '#342D3D',
    },
    css: {
      '--background': '280 25% 8%',
      '--foreground': '30 10% 97%',
      '--card': '280 20% 12%',
      '--card-foreground': '30 10% 97%',
      '--popover': '280 20% 12%',
      '--popover-foreground': '30 10% 97%',
      '--primary': '38 92% 63%',
      '--primary-foreground': '280 25% 8%',
      '--secondary': '280 15% 18%',
      '--secondary-foreground': '30 10% 97%',
      '--muted': '280 15% 18%',
      '--muted-foreground': '30 8% 75%',
      '--accent': '33 100% 56%',
      '--accent-foreground': '280 25% 8%',
      '--destructive': '0 72% 51%',
      '--destructive-foreground': '0 0% 98%',
      '--border': '280 15% 20%',
      '--input': '280 15% 18%',
      '--ring': '38 92% 63%',
      '--surface': '280 20% 12%',
      '--surface-variant': '280 15% 18%',
    },
    bodyGradient: 'linear-gradient(135deg, #1A141D 0%, #251F2B 50%, #1A141D 100%)',
  },
  {
    id: 'slate',
    name: 'Charcoal Slate Modern',
    description: 'Clean charcoal slate with amber gold accents - modern and professional',
    colors: {
      background: '#121618',
      card: '#1C2225',
      border: '#31383D',
      hover: '#2B3236',
    },
    css: {
      '--background': '210 15% 8%',
      '--foreground': '30 10% 97%',
      '--card': '210 12% 12%',
      '--card-foreground': '30 10% 97%',
      '--popover': '210 12% 12%',
      '--popover-foreground': '30 10% 97%',
      '--primary': '38 92% 63%',
      '--primary-foreground': '210 15% 8%',
      '--secondary': '210 10% 18%',
      '--secondary-foreground': '30 10% 97%',
      '--muted': '210 10% 18%',
      '--muted-foreground': '30 8% 75%',
      '--accent': '33 100% 56%',
      '--accent-foreground': '210 15% 8%',
      '--destructive': '0 72% 51%',
      '--destructive-foreground': '0 0% 98%',
      '--border': '210 10% 20%',
      '--input': '210 10% 18%',
      '--ring': '38 92% 63%',
      '--surface': '210 12% 12%',
      '--surface-variant': '210 10% 18%',
    },
    bodyGradient: 'linear-gradient(135deg, #121618 0%, #1C2225 50%, #121618 100%)',
  },
];

export default function DarkModeTestPage() {
  const [selectedVariation, setSelectedVariation] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [originalStyles, setOriginalStyles] = useState<{ [key: string]: string }>({});

  // Check if dark mode is active
  useEffect(() => {
    const checkDarkMode = () => {
      const html = document.documentElement;
      setIsDarkMode(html.classList.contains('dark'));
    };

    checkDarkMode();

    // Watch for dark mode changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['class'],
    });

    return () => observer.disconnect();
  }, []);

  // Apply variation styles
  const applyVariation = (variation: typeof variations[0]) => {
    const root = document.documentElement;
    const body = document.body;

    // Store original styles if first time
    if (Object.keys(originalStyles).length === 0) {
      const styles: { [key: string]: string } = {};
      Object.keys(variation.css).forEach(key => {
        const value = getComputedStyle(root).getPropertyValue(key);
        if (value) styles[key] = value;
      });
      setOriginalStyles(styles);
    }

    // Apply new styles
    Object.entries(variation.css).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });

    // Update body gradient
    if (body) {
      body.style.background = variation.bodyGradient;
    }

    setSelectedVariation(variation.id);
    
    // Save to localStorage for persistence
    localStorage.setItem('darkModeVariation', variation.id);
  };

  // Reset to original
  const resetVariation = () => {
    const root = document.documentElement;
    const body = document.body;

    // Restore original styles
    Object.entries(originalStyles).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });

    // Restore original body background
    if (body) {
      body.style.background = '';
    }

    setSelectedVariation(null);
    localStorage.removeItem('darkModeVariation');
  };

  // Load saved variation on mount
  useEffect(() => {
    const saved = localStorage.getItem('darkModeVariation');
    if (saved && isDarkMode) {
      const variation = variations.find(v => v.id === saved);
      if (variation) {
        applyVariation(variation);
      }
    }
  }, [isDarkMode]);

  // Toggle dark mode
  const toggleDarkMode = () => {
    const html = document.documentElement;
    if (html.classList.contains('dark')) {
      html.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      html.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDarkMode(!isDarkMode);
  };

  return (
    <div className="min-h-screen transition-colors duration-300">
      <Navigation />
      
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-display font-bold text-foreground mb-2">
                Dark Mode Color Variations
              </h1>
              <p className="text-muted-foreground text-base sm:text-lg">
                Test different dark mode color palettes. Make sure dark mode is enabled to see the variations.
              </p>
            </div>
            <Button
              onClick={toggleDarkMode}
              variant="outline"
              size="lg"
              className="flex items-center gap-2 border-border/70 dark:border-border/80 text-muted-foreground hover:bg-secondary"
            >
              {isDarkMode ? (
                <>
                  <Sun className="h-5 w-5" />
                  Light Mode
                </>
              ) : (
                <>
                  <Moon className="h-5 w-5" />
                  Dark Mode
                </>
              )}
            </Button>
          </div>

          {!isDarkMode && (
            <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl">
              <p className="text-amber-800 dark:text-amber-200 text-sm">
                💡 Enable dark mode above to see the color variations in action.
              </p>
            </div>
          )}
        </div>

        {/* Variation Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 mb-8">
          {variations.map((variation) => (
            <Card
              key={variation.id}
              className={`card-surface backdrop-blur-xl rounded-2xl border transition-all duration-300 cursor-pointer hover:scale-[1.02] hover:shadow-xl ${
                selectedVariation === variation.id
                  ? 'border-primary shadow-lg shadow-amber-500/20'
                  : 'border-border/60 dark:border-border/70'
              }`}
              onClick={() => isDarkMode && applyVariation(variation)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-lg sm:text-xl text-card-foreground">
                        {variation.name}
                      </CardTitle>
                      {selectedVariation === variation.id && (
                        <Check className="h-5 w-5 text-primary" />
                      )}
                    </div>
                    <CardDescription className="text-sm text-muted-foreground">
                      {variation.description}
                    </CardDescription>
                  </div>
                  <Palette className="h-6 w-6 text-accent dark:text-primary flex-shrink-0" />
                </div>
              </CardHeader>
              <CardContent>
                {/* Color Swatches */}
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-20">Background:</span>
                    <div className="flex items-center gap-2 flex-1">
                      <div
                        className="w-12 h-8 rounded-lg border border-border/60 dark:border-border/70"
                        style={{ backgroundColor: variation.colors.background }}
                      />
                      <span className="text-xs font-mono text-muted-foreground">
                        {variation.colors.background}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-20">Card:</span>
                    <div className="flex items-center gap-2 flex-1">
                      <div
                        className="w-12 h-8 rounded-lg border border-border/60 dark:border-border/70"
                        style={{ backgroundColor: variation.colors.card }}
                      />
                      <span className="text-xs font-mono text-muted-foreground">
                        {variation.colors.card}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground w-20">Border:</span>
                    <div className="flex items-center gap-2 flex-1">
                      <div
                        className="w-12 h-8 rounded-lg border border-border/60 dark:border-border/70"
                        style={{ backgroundColor: variation.colors.border }}
                      />
                      <span className="text-xs font-mono text-muted-foreground">
                        {variation.colors.border}
                      </span>
                    </div>
                  </div>
                </div>

                <Button
                  className={`w-full mt-4 ${
                    selectedVariation === variation.id
                      ? 'bg-gradient-to-r from-primary to-accent text-primary-foreground hover:from-primary hover:to-accent/90'
                      : 'bg-secondary dark:bg-muted text-muted-foreground hover:bg-secondary'
                  }`}
                  disabled={!isDarkMode}
                  onClick={(e) => {
                    e.stopPropagation();
                    applyVariation(variation);
                  }}
                >
                  {selectedVariation === variation.id ? 'Selected' : 'Apply This Variation'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Reset Button */}
        {selectedVariation && (
          <div className="flex justify-center">
            <Button
              onClick={resetVariation}
              variant="outline"
              className="border-border/70 dark:border-border/80 text-muted-foreground hover:bg-secondary"
            >
              Reset to Default Dark Mode
            </Button>
          </div>
        )}

        {/* Preview Section */}
        {isDarkMode && (
          <div className="mt-12">
            <h2 className="text-2xl font-display font-semibold text-foreground mb-6">
              Preview Components
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
              {/* Preview Card 1 */}
              <Card className="card-surface backdrop-blur-xl rounded-2xl border border-border/60 dark:border-border/70">
                <CardHeader>
                  <CardTitle className="text-card-foreground">Sample Card</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    This is how cards look with your selected variation
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Notice how the background, borders, and text colors work together.
                  </p>
                  <Button className="bg-gradient-to-r from-primary to-accent text-primary-foreground hover:from-primary hover:to-accent/90">
                    Amber Button
                  </Button>
                </CardContent>
              </Card>

              {/* Preview Card 2 */}
              <Card className="card-surface backdrop-blur-xl rounded-2xl border border-border/60 dark:border-border/70">
                <CardHeader>
                  <CardTitle className="text-card-foreground">Text Hierarchy</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-card-foreground font-semibold mb-2">
                    Primary Text Color
                  </p>
                  <p className="text-sm text-muted-foreground mb-4">
                    Secondary/muted text maintains excellent readability.
                  </p>
                  <div className="space-y-2">
                    <div className="h-2 bg-primary rounded-full w-3/4" />
                    <div className="h-2 bg-accent rounded-full w-1/2" />
                  </div>
                </CardContent>
              </Card>

              {/* Preview Card 3 */}
              <Card className="card-surface backdrop-blur-xl rounded-2xl border border-border/60 dark:border-border/70">
                <CardHeader>
                  <CardTitle className="text-card-foreground">Gradients & Accents</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="h-12 bg-gradient-to-r from-primary to-accent rounded-lg flex items-center justify-center">
                      <span className="text-primary-foreground font-semibold">Amber Gradient</span>
                    </div>
                    <div className="flex gap-2">
                      <div className="h-8 w-8 rounded bg-primary" />
                      <div className="h-8 w-8 rounded bg-accent" />
                      <div className="h-8 w-8 rounded bg-accent/80" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-12 p-6 bg-secondary dark:bg-muted rounded-2xl border border-border/60 dark:border-border/70">
          <h3 className="text-lg font-semibold text-card-foreground mb-3">
            How to Use
          </h3>
          <ol className="space-y-2 text-sm text-muted-foreground list-decimal list-inside">
            <li>Enable dark mode using the button in the top right</li>
            <li>Click on any variation card to apply it</li>
            <li>The variation will persist even if you navigate away</li>
            <li>Use "Reset to Default" to return to the original dark mode</li>
            <li>Check the preview components below to see how it looks</li>
            <li>When you find one you like, update your globals.css with the values from DARK_MODE_PALETTE_VARIATIONS.md</li>
          </ol>
        </div>
      </div>
    </div>
  );
}

