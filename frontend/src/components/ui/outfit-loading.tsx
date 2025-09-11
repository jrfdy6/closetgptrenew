'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Sparkles, Shirt, Palette, Zap, RefreshCw } from 'lucide-react';

interface OutfitLoadingProps {
  message?: string;
  showProgress?: boolean;
}

export default function OutfitLoading({ 
  message = "Generating your perfect outfit...", 
  showProgress = true 
}: OutfitLoadingProps) {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    { icon: Shirt, text: "Analyzing your wardrobe", color: "text-blue-600" },
    { icon: Palette, text: "Matching colors & styles", color: "text-purple-600" },
    { icon: Zap, text: "Applying AI magic", color: "text-yellow-600" },
    { icon: Sparkles, text: "Finalizing your look", color: "text-pink-600" }
  ];

  useEffect(() => {
    if (!showProgress) return;

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => (prev + 1) % steps.length);
    }, 1000);

    return () => {
      clearInterval(interval);
      clearInterval(stepInterval);
    };
  }, [showProgress, steps.length]);

  return (
    <div className="flex items-center justify-center min-h-[400px]">
      <Card className="w-full max-w-md">
        <CardContent className="p-8 text-center">
          {/* Animated Icon */}
          <div className="relative mb-6">
            <div className="w-20 h-20 mx-auto bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/20 dark:to-pink-900/20 rounded-full flex items-center justify-center">
              <RefreshCw className="h-8 w-8 text-purple-600 animate-spin" />
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
              <Sparkles className="h-3 w-3 text-white animate-pulse" />
            </div>
          </div>

          {/* Message */}
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
            {message}
          </h3>

          {/* Progress Bar */}
          {showProgress && (
            <div className="space-y-4">
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all duration-300 ease-out"
                  style={{ width: `${Math.min(progress, 100)}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {Math.round(Math.min(progress, 100))}% complete
              </p>
            </div>
          )}

          {/* Current Step */}
          {showProgress && (
            <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="flex items-center justify-center gap-3">
                {steps.map((step, index) => {
                  const Icon = step.icon;
                  const isActive = index === currentStep;
                  const isCompleted = index < currentStep;
                  
                  return (
                    <div key={index} className="flex flex-col items-center gap-2">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center transition-all duration-300 ${
                        isActive 
                          ? 'bg-purple-100 dark:bg-purple-900/30 scale-110' 
                          : isCompleted
                          ? 'bg-green-100 dark:bg-green-900/30'
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}>
                        <Icon className={`h-4 w-4 ${
                          isActive 
                            ? step.color 
                            : isCompleted
                            ? 'text-green-600'
                            : 'text-gray-400'
                        }`} />
                      </div>
                      <span className={`text-xs text-center ${
                        isActive 
                          ? 'text-purple-600 dark:text-purple-400 font-medium' 
                          : isCompleted
                          ? 'text-green-600 dark:text-green-400'
                          : 'text-gray-500 dark:text-gray-400'
                      }`}>
                        {step.text}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Fun Facts */}
          <div className="mt-6 text-xs text-gray-500 dark:text-gray-400">
            <p>💡 Did you know? Our AI considers over 50 style factors!</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

// Specialized loading components for different scenarios
export function WardrobeLoading() {
  return (
    <OutfitLoading 
      message="Loading your wardrobe..." 
      showProgress={false}
    />
  );
}

export function OutfitGenerating() {
  return (
    <OutfitLoading 
      message="Creating your perfect outfit..." 
      showProgress={true}
    />
  );
}

export function OutfitSaving() {
  return (
    <OutfitLoading 
      message="Saving your outfit..." 
      showProgress={false}
    />
  );
}
