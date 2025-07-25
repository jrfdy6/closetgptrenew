'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import { useFirebase } from '@/lib/firebase-context';
import ProtectedRoute from '@/components/ProtectedRoute';
import { auth } from '@/lib/firebase/config';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';

// TypeScript interfaces for the quiz
interface QuizOption {
  text: string;
  scores: Record<string, number>;
  image?: string;
}

interface QuizQuestion {
  id: string;
  question: string;
  type: string;
  options: QuizOption[];
  category: string;
}

// Backend style quiz questions (matching the backend structure)
const BACKEND_QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: "movie_vibe",
    question: "Which movie's aesthetic speaks to you the most?",
    type: "image_choice",
    options: [
      {
        image: "/quiz-images/classic-hollywood.jpg",
        text: "Classic Hollywood Glamour",
        scores: {
          "classic": 0.8,
          "sophisticated": 0.6,
          "romantic": 0.4
        }
      },
      {
        image: "/quiz-images/indie-romance.jpg",
        text: "Indie Romance",
        scores: {
          "romantic": 0.8,
          "bohemian": 0.6,
          "vintage": 0.4
        }
      },
      {
        image: "/quiz-images/minimalist-scandi.jpg",
        text: "Minimalist Scandinavian",
        scores: {
          "minimalist": 0.9,
          "sophisticated": 0.5,
          "comfortable": 0.3
        }
      },
      {
        image: "/quiz-images/street-style.jpg",
        text: "Urban Street Style",
        scores: {
          "streetwear": 0.8,
          "edgy": 0.6,
          "athletic": 0.4
        }
      }
    ],
    category: "aesthetic"
  },
  {
    id: "color_preference",
    question: "Which color palette feels most 'you'?",
    type: "image_choice",
    options: [
      {
        image: "/quiz-images/warm-spring.jpg",
        text: "Warm & Fresh",
        scores: {
          "warm_spring": 0.9,
          "warm_autumn": 0.7
        }
      },
      {
        image: "/quiz-images/cool-summer.jpg",
        text: "Soft & Cool",
        scores: {
          "cool_summer": 0.9,
          "cool_spring": 0.7
        }
      },
      {
        image: "/quiz-images/deep-winter.jpg",
        text: "Rich & Deep",
        scores: {
          "cool_winter": 0.9,
          "warm_winter": 0.7
        }
      },
      {
        image: "/quiz-images/earthy-autumn.jpg",
        text: "Earthy & Warm",
        scores: {
          "warm_autumn": 0.9,
          "cool_autumn": 0.7
        }
      }
    ],
    category: "color"
  },
  {
    id: "silhouette_preference",
    question: "Which silhouette do you feel most confident in?",
    type: "image_choice",
    options: [
      {
        image: "/quiz-images/fitted.jpg",
        text: "Fitted & Structured",
        scores: {
          "hourglass": 0.8,
          "rectangle": 0.6
        }
      },
      {
        image: "/quiz-images/flowy.jpg",
        text: "Flowy & Relaxed",
        scores: {
          "pear": 0.8,
          "apple": 0.6
        }
      },
      {
        image: "/quiz-images/balanced.jpg",
        text: "Balanced & Proportional",
        scores: {
          "rectangle": 0.8,
          "hourglass": 0.6
        }
      },
      {
        image: "/quiz-images/dramatic.jpg",
        text: "Dramatic & Statement",
        scores: {
          "inverted_triangle": 0.8,
          "triangle": 0.6
        }
      }
    ],
    category: "fit"
  },
  {
    id: "daily_activities",
    question: "What best describes your daily activities?",
    type: "multiple_choice",
    options: [
      {
        text: "Office work and meetings",
        scores: {
          "professional": 0.8,
          "classic": 0.6,
          "sophisticated": 0.4
        }
      },
      {
        text: "Creative work and casual meetings",
        scores: {
          "bohemian": 0.7,
          "minimalist": 0.5,
          "comfortable": 0.3
        }
      },
      {
        text: "Active lifestyle and sports",
        scores: {
          "athletic": 0.8,
          "streetwear": 0.6,
          "comfortable": 0.4
        }
      },
      {
        text: "Mix of everything",
        scores: {
          "versatile": 0.8,
          "comfortable": 0.6,
          "sophisticated": 0.4
        }
      }
    ],
    category: "lifestyle"
  },
  {
    id: "style_elements",
    question: "Which style elements do you gravitate towards?",
    type: "multiple_choice",
    options: [
      {
        text: "Clean lines and minimal details",
        scores: {
          "minimalist": 0.9,
          "sophisticated": 0.6
        }
      },
      {
        text: "Rich textures and patterns",
        scores: {
          "bohemian": 0.8,
          "romantic": 0.6
        }
      },
      {
        text: "Classic and timeless pieces",
        scores: {
          "classic": 0.9,
          "preppy": 0.6
        }
      },
      {
        text: "Bold and statement pieces",
        scores: {
          "edgy": 0.8,
          "streetwear": 0.6
        }
      }
    ],
    category: "style"
  }
];

export default function StyleQuizPage() {
  const router = useRouter();
  const { user } = useFirebase();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const currentQuestion = BACKEND_QUIZ_QUESTIONS[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / BACKEND_QUIZ_QUESTIONS.length) * 100;
  const isLastQuestion = currentQuestionIndex === BACKEND_QUIZ_QUESTIONS.length - 1;

  // Debug: Log the current question and total questions
  console.log('Style Quiz Debug:', {
    currentQuestionIndex,
    totalQuestions: BACKEND_QUIZ_QUESTIONS.length,
    currentQuestion: currentQuestion?.question,
    currentQuestionOptions: currentQuestion?.options?.map(opt => opt.text)
  });

  const handleAnswer = (selectedOption: QuizOption) => {
    const newAnswers = {
      ...answers,
      [currentQuestion.id]: selectedOption.text
    };
    
    setAnswers(newAnswers);

    if (isLastQuestion) {
      handleQuizComplete(newAnswers);
    } else {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handleQuizComplete = async (finalAnswers: Record<string, string>) => {
    if (!user || !auth) {
      toast.error('Please sign in to save your style profile');
      router.push('/signin');
      return;
    }

    try {
      setIsSubmitting(true);
      
      // Get the current user's ID token
      const idToken = await auth.currentUser?.getIdToken();
      if (!idToken) {
        throw new Error('Failed to get authentication token');
      }
      
      // Format the quiz submission data for backend processing
      const quizSubmission = {
        user_id: user.uid,
        answers: Object.entries(finalAnswers).map(([questionId, selectedOption]) => ({
          question_id: questionId,
          selected_option: selectedOption
        }))
      };
      
      // Send to backend for comprehensive style analysis
      const response = await fetch('/api/style-quiz/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${idToken}`
        },
        body: JSON.stringify(quizSubmission),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.details || 'Failed to analyze style profile');
      }

      toast.success('Your style profile has been analyzed and saved!');
      router.push('/dashboard');
    } catch (error) {
      console.error('Error saving style profile:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to save style profile');
    } finally {
      setIsSubmitting(false);
    }
  };

  const generateHybridStyleName = (aestheticScores: Record<string, number>) => {
    const sortedAesthetics = Object.entries(aestheticScores)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 2);
    
    if (sortedAesthetics.length >= 2) {
      const [primary, secondary] = sortedAesthetics;
      return `${primary[0].charAt(0).toUpperCase() + primary[0].slice(1)} ${secondary[0].charAt(0).toUpperCase() + secondary[0].slice(1)}`;
    } else if (sortedAesthetics.length === 1) {
      return sortedAesthetics[0][0].charAt(0).toUpperCase() + sortedAesthetics[0][0].slice(1);
    }
    return 'Personal Style';
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        <div className="container mx-auto py-8">
          <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold text-center mb-4">
              Discover Your Style
            </h1>
            <p className="text-center text-muted-foreground mb-8 max-w-2xl mx-auto">
              Answer these questions to help us understand your style preferences
              and create your personalized hybrid style profile.
            </p>

            <Progress value={progress} className="mb-8" />

            <Card className="p-8">
              <h2 className="text-2xl font-bold mb-6 text-center">
                {currentQuestion.question}
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {currentQuestion.options.map((option, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    className="h-auto p-6 flex flex-col items-center gap-4 hover:bg-secondary"
                    onClick={() => handleAnswer(option)}
                    disabled={isSubmitting}
                  >
                    {'image' in option && option.image && (
                      <img
                        src={option.image}
                        alt={option.text}
                        className="w-full h-48 object-cover rounded-md"
                      />
                    )}
                    <span className="font-medium text-center">{option.text}</span>
                  </Button>
                ))}
              </div>

              {isSubmitting && (
                <div className="mt-6 text-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto mb-2"></div>
                  <p className="text-muted-foreground">Analyzing your style profile...</p>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
} 