'use client';

import { useEffect, useState } from 'react';
import { CheckCircle } from 'lucide-react';

interface LearningConfirmationProps {
  learning: {
    messages: string[];
    total_feedback_count: number;
    personalization_level: number;
    confidence_level: string;
    preferred_colors?: string[];
    preferred_styles?: string[];
  };
  onClose?: () => void;
  autoCloseDelay?: number;
}

export default function LearningConfirmation({ onClose, autoCloseDelay = 5000 }: LearningConfirmationProps) {
  const [isVisible, setIsVisible] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, autoCloseDelay);
    return () => clearTimeout(timer);
  }, [autoCloseDelay, onClose]);

  if (!isVisible) return null;
  return (
    <div role="status" className="fixed top-4 right-4 z-50 mx-4 max-w-md rounded-xl border border-green-200 bg-green-50 p-5 shadow-xl dark:border-green-700 dark:bg-green-950">
      <div className="flex items-start gap-3">
        <CheckCircle aria-hidden="true" className="h-6 w-6 shrink-0 text-green-700 dark:text-green-300" />
        <div>
          <h4 className="font-semibold text-green-900 dark:text-green-100">Feedback saved</h4>
          <p className="mt-1 text-sm text-green-800 dark:text-green-200">Your feedback helps shape future outfit suggestions.</p>
        </div>
      </div>
    </div>
  );
}
