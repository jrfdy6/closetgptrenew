'use client';

import { useEffect, useState } from 'react';
import { CheckCircle, Sparkles, TrendingUp } from 'lucide-react';

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

export default function LearningConfirmation({
  learning,
  onClose,
  autoCloseDelay = 5000
}: LearningConfirmationProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    // Auto-close after delay
    const timer = setTimeout(() => {
      setIsVisible(false);
      if (onClose) {
        setTimeout(onClose, 300); // Wait for fade animation
      }
    }, autoCloseDelay);

    return () => clearTimeout(timer);
  }, [autoCloseDelay, onClose]);

  if (!isVisible) return null;

  const getConfidenceBadge = () => {
    switch (learning.confidence_level) {
      case 'high':
        return {
          label: 'Highly Personalized',
          color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200'
        };
      case 'medium':
        return {
          label: 'Getting Smarter',
          color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200'
        };
      default:
        return {
          label: 'Learning Your Style',
          color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200'
        };
    }
  };

  const badge = getConfidenceBadge();

  return (
    <div className={`
      fixed top-4 right-4 z-50 max-w-md
      transform transition-all duration-300 ease-out
      ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
    `}>
      <div className="bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-900/40 dark:to-emerald-900/40 
                      border-2 border-green-200 dark:border-green-700 
                      rounded-xl shadow-2xl p-5 backdrop-blur-sm">
        {/* Header */}
        <div className="flex items-start gap-3 mb-3">
          <div className="flex-shrink-0 w-10 h-10 rounded-full bg-green-500 dark:bg-green-600 
                          flex items-center justify-center animate-bounce-subtle">
            <CheckCircle className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-green-900 dark:text-green-100 text-lg">
                We're Learning!
              </h4>
              <span className={`text-xs px-2 py-1 rounded-full ${badge.color} font-medium`}>
                {badge.label}
              </span>
            </div>
          </div>
        </div>

        {/* Learning Messages */}
        <div className="space-y-2 mb-4">
          {learning.messages.map((message, index) => (
            <div key={index} className="flex items-start gap-2">
              <Sparkles className="w-4 h-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-800 dark:text-green-200 font-medium">
                {message}
              </p>
            </div>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs text-green-700 dark:text-green-300">
            <span className="flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              Your AI Progress
            </span>
            <span className="font-semibold">
              {learning.personalization_level}% trained
            </span>
          </div>
          
          <div className="h-2 bg-green-200 dark:bg-green-800 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-emerald-500 dark:from-green-600 dark:to-emerald-600 
                         transition-all duration-1000 ease-out rounded-full"
              style={{ width: `${learning.personalization_level}%` }}
            />
          </div>
          
          <p className="text-xs text-green-700 dark:text-green-300 text-center">
            We've learned from <span className="font-semibold">{learning.total_feedback_count}</span> of your ratings
          </p>
        </div>

        {/* Next Milestone */}
        {learning.personalization_level < 100 && (
          <div className="mt-3 p-2 bg-white/60 dark:bg-black/20 rounded-lg">
            <p className="text-xs text-green-800 dark:text-green-200">
              💡 {learning.total_feedback_count < 10 
                ? `${10 - learning.total_feedback_count} more ratings to reach "Good Match" level`
                : learning.total_feedback_count < 25
                ? `${25 - learning.total_feedback_count} more ratings for "Highly Personalized"`
                : 'Almost perfect! Keep rating for even better suggestions'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

