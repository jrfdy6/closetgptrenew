"use client";

import React, { useState } from 'react';
import { StepWizard, StepConfig, StepProps } from '@/components/onboarding/StepWizard';

// Simple test step components with proper StepProps interface
const TestStep1 = ({ onNext }: StepProps) => {
  const handleNext = () => {
    console.log('TestStep1: Next button clicked');
    onNext();
  };

  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">Test Step 1</h2>
      <p className="mb-4">This is a test step to verify StepWizard works.</p>
      <button 
        onClick={handleNext} 
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Next
      </button>
    </div>
  );
};

const TestStep2 = ({ onNext, onPrevious }: StepProps) => {
  const handleNext = () => {
    console.log('TestStep2: Next button clicked');
    onNext();
  };

  const handlePrevious = () => {
    console.log('TestStep2: Previous button clicked');
    onPrevious();
  };

  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">Test Step 2</h2>
      <p className="mb-4">This is another test step.</p>
      <div className="space-x-4">
        <button 
          onClick={handlePrevious} 
          className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
        >
          Previous
        </button>
        <button 
          onClick={handleNext} 
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Next
        </button>
      </div>
    </div>
  );
};

const TestStep3 = ({ onPrevious }: StepProps) => {
  const handlePrevious = () => {
    console.log('TestStep3: Previous button clicked');
    onPrevious();
  };

  return (
    <div className="text-center">
      <h2 className="text-2xl font-bold mb-4">Test Step 3</h2>
      <p className="mb-4">This is the final test step.</p>
      <button 
        onClick={handlePrevious} 
        className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
      >
        Previous
      </button>
    </div>
  );
};

export default function TestStepWizard() {
  const [currentStep, setCurrentStep] = useState(0);

  const steps: StepConfig[] = [
    {
      id: "step1",
      title: "Step 1",
      description: "First test step",
      component: TestStep1,
    },
    {
      id: "step2", 
      title: "Step 2",
      description: "Second test step",
      component: TestStep2,
    },
    {
      id: "step3",
      title: "Step 3", 
      description: "Final test step",
      component: TestStep3,
    },
  ];

  const handleStepChange = (stepIndex: number) => {
    console.log('TestStepWizard: Step changed to:', stepIndex);
    setCurrentStep(stepIndex);
  };

  const handleComplete = () => {
    console.log('TestStepWizard: Wizard completed!');
    alert('Test completed successfully!');
  };

  console.log('TestStepWizard: Rendering with currentStep:', currentStep);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">StepWizard Test</h1>
        <p className="text-center text-gray-600 mb-8">
          Current step: {currentStep + 1} of {steps.length}
        </p>
        <StepWizard
          steps={steps}
          currentStepIndex={currentStep}
          onStepChange={handleStepChange}
          onComplete={handleComplete}
          showProgress={true}
          showNavigation={true}
        />
      </div>
    </div>
  );
} 