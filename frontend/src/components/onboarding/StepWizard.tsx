"use client";

import React, { useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ChevronLeft, ChevronRight, SkipForward } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface StepConfig {
  id: string;
  title: string;
  description: string;
  component: React.ComponentType<StepProps>;
  isOptional?: boolean;
  canSkip?: boolean;
}

export interface StepProps {
  onNext: () => void;
  onPrevious: () => void;
  onSkip?: () => void;
  isFirstStep: boolean;
  isLastStep: boolean;
  currentStep: number;
  totalSteps: number;
}

interface StepWizardProps {
  steps: StepConfig[];
  currentStepIndex: number;
  onStepChange: (stepIndex: number) => void;
  onComplete: () => void;
  className?: string;
  showProgress?: boolean;
  showNavigation?: boolean;
}

export function StepWizard({
  steps,
  currentStepIndex,
  onStepChange,
  onComplete,
  className,
  showProgress = true,
  showNavigation = true,
}: StepWizardProps) {
  // Safety check for invalid step index
  if (!steps || steps.length === 0) {
    return (
      <div className={cn("w-full max-w-4xl mx-auto", className)}>
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error: No steps configured</h1>
          <p className="text-muted-foreground">Please check the onboarding configuration.</p>
        </div>
      </div>
    );
  }

  // Ensure currentStepIndex is within bounds
  const safeStepIndex = Math.max(0, Math.min(currentStepIndex, steps.length - 1));
  const currentStep = steps[safeStepIndex];
  
  // Safety check for currentStep
  if (!currentStep) {
    return (
      <div className={cn("w-full max-w-4xl mx-auto", className)}>
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error: Current step is undefined</h1>
          <p className="text-muted-foreground">Step index: {safeStepIndex}</p>
        </div>
      </div>
    );
  }

  // Safety check for component
  if (!currentStep.component) {
    return (
      <div className={cn("w-full max-w-4xl mx-auto", className)}>
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600">Error: Step component is undefined</h1>
          <p className="text-muted-foreground">Step: {currentStep.id}</p>
        </div>
      </div>
    );
  }

  const isFirstStep = safeStepIndex === 0;
  const isLastStep = safeStepIndex === steps.length - 1;
  const progress = ((safeStepIndex + 1) / steps.length) * 100;

  const handleNext = useCallback(() => {
    if (isLastStep) {
      onComplete();
    } else {
      const nextStepIndex = safeStepIndex + 1;
      if (nextStepIndex < steps.length) {
        onStepChange(nextStepIndex);
      }
    }
  }, [isLastStep, safeStepIndex, steps.length, onComplete, onStepChange]);

  const handlePrevious = useCallback(() => {
    if (!isFirstStep) {
      const prevStepIndex = safeStepIndex - 1;
      if (prevStepIndex >= 0) {
        onStepChange(prevStepIndex);
      }
    }
  }, [isFirstStep, safeStepIndex, onStepChange]);

  const handleSkip = useCallback(() => {
    if (currentStep.canSkip) {
      const nextStepIndex = safeStepIndex + 1;
      if (nextStepIndex < steps.length) {
        onStepChange(nextStepIndex);
      }
    }
  }, [currentStep.canSkip, safeStepIndex, steps.length, onStepChange]);

  const StepComponent = currentStep.component;

  return (
    <div className={cn("w-full max-w-4xl mx-auto", className)}>
      {/* Progress Bar */}
      {showProgress && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">
              Step {safeStepIndex + 1} of {steps.length}
            </span>
            <span className="text-sm font-medium text-muted-foreground">
              {Math.round(progress)}% complete
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Step Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">{currentStep.title}</h1>
        <p className="text-muted-foreground">{currentStep.description}</p>
        {currentStep.isOptional && (
          <p className="text-sm text-muted-foreground mt-2">
            This step is optional
          </p>
        )}
      </div>

      {/* Step Content */}
      <Card className="p-6">
        <StepComponent
          onNext={handleNext}
          onPrevious={handlePrevious}
          onSkip={currentStep.canSkip ? handleSkip : undefined}
          isFirstStep={isFirstStep}
          isLastStep={isLastStep}
          currentStep={safeStepIndex + 1}
          totalSteps={steps.length}
        />
      </Card>

      {/* Navigation */}
      {showNavigation && (
        <div className="flex justify-between items-center mt-6">
          <Button
            variant="ghost"
            onClick={handlePrevious}
            disabled={isFirstStep}
            className="flex items-center"
          >
            <ChevronLeft className="w-4 h-4 mr-2" />
            Previous
          </Button>

          <div className="flex items-center space-x-2">
            {currentStep.canSkip && (
              <Button
                variant="outline"
                onClick={handleSkip}
                className="flex items-center"
              >
                <SkipForward className="w-4 h-4 mr-2" />
                Skip
              </Button>
            )}
            <Button
              onClick={handleNext}
              className="flex items-center"
            >
              {isLastStep ? 'Complete' : 'Next'}
              <ChevronRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
} 