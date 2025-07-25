import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { quizQuestions } from '@/lib/quiz-questions';
import { StyleProfile } from '@/types/style-quiz';

interface StyleQuizStepProps {
  onComplete: () => void;
}

export function StyleQuizStep({ onComplete }: StyleQuizStepProps) {
  const { toast } = useToast();
  const { setStylePreferences } = useOnboardingStore();
  const [currentQuestionId, setCurrentQuestionId] = useState(quizQuestions[0].id);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [styleProfile, setStyleProfile] = useState<StyleProfile>({
    preferredColors: [],
    preferredPatterns: [],
    preferredStyles: [],
    formality: 'casual',
    seasonality: ['spring', 'summer', 'fall', 'winter'],
    confidence: 0
  });

  const currentQuestion = quizQuestions.find(q => q.id === currentQuestionId);
  const progress = (Object.keys(answers).length / quizQuestions.length) * 100;

  const handleAnswer = (optionId: string) => {
    if (!currentQuestion) return;

    const selectedOption = currentQuestion.options.find(opt => opt.id === optionId);
    if (!selectedOption) return;

    const newAnswers = { 
      ...answers, 
      [currentQuestion.id]: selectedOption.label 
    };
    const nextQuestionId = currentQuestion.nextQuestionId;
    const isLastQuestion = !nextQuestionId;

    // Update style profile based on the selected option
    const newStyleProfile = updateStyleProfile(styleProfile, selectedOption.styleAttributes);

    setAnswers(newAnswers);
    setStyleProfile(newStyleProfile);

    if (isLastQuestion) {
      // Save the style profile to the onboarding store
      setStylePreferences({
        stylePreferences: newStyleProfile.preferredStyles,
        preferredColors: newStyleProfile.preferredColors,
        formality: newStyleProfile.formality,
        seasonality: newStyleProfile.seasonality
      });
      onComplete();
    } else {
      setCurrentQuestionId(nextQuestionId);
    }
  };

  const updateStyleProfile = (currentProfile: StyleProfile, newAttributes: any): StyleProfile => {
    return {
      preferredColors: [...new Set([...currentProfile.preferredColors, ...newAttributes.colors])],
      preferredPatterns: [...new Set([...currentProfile.preferredPatterns, ...newAttributes.patterns])],
      preferredStyles: [...new Set([...currentProfile.preferredStyles, ...newAttributes.styles])],
      formality: newAttributes.formality,
      seasonality: newAttributes.seasonality,
      confidence: Math.min(1, currentProfile.confidence + 0.33)
    };
  };

  if (!currentQuestion) return null;

  return (
    <div className="space-y-8 max-w-2xl mx-auto">
      <Progress value={progress} className="mb-8" />
      
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-6">{currentQuestion.question}</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {currentQuestion.options.map((option) => (
            <Button
              key={option.id}
              variant="outline"
              className="h-auto p-4 flex flex-col items-center gap-2"
              onClick={() => handleAnswer(option.id)}
            >
              {option.imageUrl && (
                <img
                  src={option.imageUrl}
                  alt={option.label}
                  className="w-full h-48 object-cover rounded-md mb-2"
                />
              )}
              <span className="font-medium">{option.label}</span>
            </Button>
          ))}
        </div>
      </Card>
    </div>
  );
} 