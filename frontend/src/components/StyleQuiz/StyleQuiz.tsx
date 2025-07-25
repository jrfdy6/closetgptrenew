import React, { useState, useEffect } from 'react';
import { QuizQuestion, QuizState, StyleProfile } from '@/types/style-quiz';
import { quizQuestions } from '@/lib/quiz-questions';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';

interface StyleQuizProps {
  onComplete: (styleProfile: StyleProfile) => void;
}

export const StyleQuiz: React.FC<StyleQuizProps> = ({ onComplete }) => {
  const [quizState, setQuizState] = useState<QuizState>({
    currentQuestionId: quizQuestions[0].id,
    answers: {},
    completed: false,
    styleProfile: {
      preferredColors: [],
      preferredPatterns: [],
      preferredStyles: [],
      formality: 'casual',
      seasonality: ['spring', 'summer', 'fall', 'winter'],
      confidence: 0
    }
  });

  const currentQuestion = quizQuestions.find(q => q.id === quizState.currentQuestionId);
  const progress = (Object.keys(quizState.answers).length / quizQuestions.length) * 100;

  const handleAnswer = (optionId: string) => {
    if (!currentQuestion) return;

    const selectedOption = currentQuestion.options.find(opt => opt.id === optionId);
    if (!selectedOption) return;

    const newAnswers = { 
      ...quizState.answers, 
      [currentQuestion.id]: selectedOption.label 
    };
    const nextQuestionId = currentQuestion.nextQuestionId;
    const isLastQuestion = !nextQuestionId;

    // Update style profile based on the selected option
    const newStyleProfile = updateStyleProfile(quizState.styleProfile, selectedOption.styleAttributes);

    setQuizState(prev => ({
      ...prev,
      answers: newAnswers,
      currentQuestionId: nextQuestionId || prev.currentQuestionId,
      completed: isLastQuestion,
      styleProfile: newStyleProfile
    }));

    if (isLastQuestion) {
      onComplete(newStyleProfile);
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
    <div className="max-w-2xl mx-auto p-6">
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
}; 