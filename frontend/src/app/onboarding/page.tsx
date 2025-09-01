"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Sparkles, Palette, Camera, TrendingUp, Heart, ArrowRight, CheckCircle } from "lucide-react";
import { useAuthContext } from "@/contexts/AuthContext";

interface QuizAnswer {
  question_id: string;
  selected_option: string;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  category: string;
  type?: "visual" | "color_swatches" | "text";
  images?: string[];
  colors?: string[];
}

// Mock quiz questions as fallback
const getMockQuizQuestions = (): QuizQuestion[] => [
  {
    id: "movie_vibe",
    question: "Which movie's aesthetic speaks to you the most?",
    options: [
      "Classic Hollywood Glamour",
      "Indie Romance", 
      "Minimalist Scandinavian",
      "Urban Street Style"
    ],
    category: "aesthetic",
    type: "visual",
    images: [
      "/quiz-images/classic-hollywood.jpg",
      "/quiz-images/indie-romance.jpg",
      "/quiz-images/minimalist-scandi.jpg",
      "/quiz-images/street-style.jpg"
    ]
  },
  {
    id: "color_preference",
    question: "Which color palette feels most 'you'?",
    options: [
      "Warm & Fresh",
      "Soft & Cool",
      "Rich & Deep", 
      "Earthy & Warm"
    ],
    category: "color",
    type: "visual",
    images: [
      "/quiz-images/warm-spring.jpg",
      "/quiz-images/cool-summer.jpg",
      "/quiz-images/deep-winter.jpg",
      "/quiz-images/earthy-autumn.jpg"
    ]
  },
  {
    id: "silhouette_preference",
    question: "Which silhouette do you feel most confident in?",
    options: [
      "Fitted & Structured",
      "Flowy & Relaxed",
      "Balanced & Proportional",
      "Dramatic & Statement"
    ],
    category: "fit",
    type: "visual",
    images: [
      "/quiz-images/fitted.jpg",
      "/quiz-images/flowy.jpg",
      "/quiz-images/balanced.jpg",
      "/quiz-images/dramatic.jpg"
    ]
  },
  {
    id: "daily_activities",
    question: "What best describes your daily activities?",
    options: [
      "Office work and meetings",
      "Creative work and casual meetings",
      "Active lifestyle and sports",
      "Mix of everything"
    ],
    category: "lifestyle"
  },
  {
    id: "style_elements",
    question: "Which style elements do you gravitate towards?",
    options: [
      "Clean lines and minimal details",
      "Rich textures and patterns",
      "Classic and timeless pieces",
      "Bold and statement pieces"
    ],
    category: "style"
  }
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState(1);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizResults, setQuizResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [questionsLoaded, setQuestionsLoaded] = useState(false);
  const { user, loading: authLoading } = useAuthContext();

  // Load quiz questions from backend
  useEffect(() => {
    const loadQuizQuestions = async () => {
      try {
        const response = await fetch('/api/style-quiz/questions');
        if (response.ok) {
          const data = await response.json();
          setQuizQuestions(data.questions || []);
        } else {
          // Fallback to mock questions if backend is unavailable
          setQuizQuestions(getMockQuizQuestions());
        }
      } catch (error) {
        console.error('Error loading quiz questions:', error);
        // Fallback to mock questions
        setQuizQuestions(getMockQuizQuestions());
      } finally {
        setQuestionsLoaded(true);
      }
    };

    if (!authLoading && user) {
      loadQuizQuestions();
    }
  }, [user, authLoading]);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      window.location.href = '/';
    }
  }, [user, authLoading]);

  const handleAnswer = (questionId: string, selectedOption: string) => {
    const newAnswers = answers.filter(a => a.question_id !== questionId);
    newAnswers.push({ question_id: questionId, selected_option: selectedOption });
    setAnswers(newAnswers);
  };

  const nextStep = () => {
    if (currentStep < quizQuestions.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    if (quizQuestions.length === 0) return false;
    const currentQuestion = quizQuestions[currentStep - 1];
    return answers.some(a => a.question_id === currentQuestion.id);
  };

  const submitQuiz = async () => {
    if (!user) {
      setError('Please sign in to complete the quiz');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      
      const response = await fetch('/api/style-quiz/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user.uid,
          answers: answers
        })
      });

      if (response.ok) {
        const result = await response.json();
        setQuizResults(result.data);
        setQuizCompleted(true);
      } else {
        console.error('Failed to submit quiz:', response.statusText);
        // Use mock data as fallback
        setQuizCompleted(true);
        setQuizResults({
          hybridStyleName: "Personal Style",
          quizResults: {
            aesthetic_scores: { "classic": 0.6, "sophisticated": 0.4 },
            color_season: "warm_spring",
            body_type: "rectangle",
            style_preferences: { "classic": 0.7, "minimalist": 0.3 }
          }
        });
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError('Failed to submit quiz. Please try again.');
      // Use mock data as fallback
      setQuizCompleted(true);
      setQuizResults({
        hybridStyleName: "Personal Style",
        quizResults: {
          aesthetic_scores: { "classic": 0.6, "sophisticated": 0.4 },
          color_season: "warm_spring",
          body_type: "rectangle",
          style_preferences: { "classic": 0.7, "minimalist": 0.3 }
        }
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderQuestion = () => {
    if (quizQuestions.length === 0) return null;
    const question = quizQuestions[currentStep - 1];
    const currentAnswer = answers.find(a => a.question_id === question.id);

    return (
      <div className="space-y-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            {question.question}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            {question.type === "visual" ? "Click on the image that best represents your style" :
             question.type === "color_swatches" ? "Select the color that best matches your skin tone" :
             "Choose the option that best describes you"}
          </p>
        </div>
        
        {question.type === "visual" && question.images ? (
          <div className="grid grid-cols-2 gap-4">
            {question.options.map((option, index) => (
              <div
                key={option}
                className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                  currentAnswer?.selected_option === option
                    ? "border-purple-600 ring-2 ring-purple-200 dark:ring-purple-800"
                    : "border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600"
                }`}
                onClick={() => handleAnswer(question.id, option)}
              >
                <div className="aspect-square relative">
                  <img
                    src={question.images[index]}
                    alt={option}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = "/images/placeholder.png";
                    }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all duration-200" />
                </div>
                <div className="p-3 bg-white dark:bg-gray-800">
                  <p className="text-sm font-medium text-center text-gray-900 dark:text-white">
                    {option}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : question.type === "color_swatches" && question.colors ? (
          <div className="grid grid-cols-3 gap-4">
            {question.options.map((option, index) => (
              <div
                key={option}
                className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                  currentAnswer?.selected_option === option
                    ? "border-purple-600 ring-2 ring-purple-200 dark:ring-purple-800"
                    : "border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600"
                }`}
                onClick={() => handleAnswer(question.id, option)}
              >
                <div className="aspect-square relative">
                  <div 
                    className="w-full h-full"
                    style={{ backgroundColor: question.colors[index] }}
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all duration-200" />
                </div>
                <div className="p-2 bg-white dark:bg-gray-800">
                  <p className="text-xs font-medium text-center text-gray-900 dark:text-white">
                    {option}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {question.options.map((option) => (
              <Button
                key={option}
                variant={currentAnswer?.selected_option === option ? "default" : "outline"}
                className="w-full h-20 text-lg justify-start text-left px-6"
                onClick={() => handleAnswer(question.id, option)}
              >
                {option}
              </Button>
            ))}
          </div>
        )}
      </div>
    );
  };

  // Show loading state while authenticating or loading questions
  if (authLoading || !questionsLoaded) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-0 shadow-xl text-center">
          <CardContent className="p-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">
              {authLoading ? 'Authenticating...' : 'Loading style quiz...'}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!user) {
    return null; // Will redirect via useEffect
  }

  // Show error if no questions loaded
  if (quizQuestions.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-0 shadow-xl text-center">
          <CardContent className="p-8">
            <p className="text-red-600 dark:text-red-400 mb-4">Failed to load quiz questions</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (quizCompleted && quizResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-0 shadow-xl text-center">
          <CardHeader>
            <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mb-4">
              <Sparkles className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white">
              Style Profile Complete!
            </CardTitle>
            <CardDescription className="text-gray-600 dark:text-gray-400">
              We've analyzed your preferences and created a personalized style profile
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-6 text-left">
              <h3 className="font-semibold mb-4 text-lg">Your Style Profile:</h3>
              
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  <span><strong>Hybrid Style:</strong> {quizResults.hybridStyleName}</span>
                </div>
                
                {quizResults.quizResults.color_season && (
                  <div className="flex items-center space-x-3">
                    <Palette className="h-5 w-5 text-purple-500" />
                    <span><strong>Color Season:</strong> {quizResults.quizResults.color_season.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                
                {quizResults.quizResults.body_type && (
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-5 w-5 text-blue-500" />
                    <span><strong>Body Type:</strong> {quizResults.quizResults.body_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  </div>
                )}
                
                {quizResults.quizResults.style_preferences && (
                  <div className="flex items-center space-x-3">
                    <Heart className="h-5 w-5 text-red-500" />
                    <span><strong>Top Styles:</strong> {Object.keys(quizResults.quizResults.style_preferences).slice(0, 3).map(style => 
                      style.replace(/\b\w/g, l => l.toUpperCase())
                    ).join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="space-y-3">
              <Link href="/dashboard">
                <Button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  Go to Dashboard
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              
              <Link href="/wardrobe">
                <Button variant="outline" className="w-full">
                  View My Wardrobe
                  <Camera className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl border-0 shadow-xl">
        <CardHeader className="text-center">
          <Link href="/" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Sparkles className="h-6 w-6 text-purple-600" />
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Style Discovery Quiz</h1>
          </div>
          <div className="flex items-center justify-center space-x-2">
            {quizQuestions.map((_, index) => (
              <div
                key={index}
                className={`w-3 h-3 rounded-full ${
                  index + 1 === currentStep
                    ? "bg-purple-600"
                    : index + 1 < currentStep
                    ? "bg-green-500"
                    : "bg-gray-300 dark:bg-gray-600"
                }`}
              />
            ))}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Question {currentStep} of {quizQuestions.length}
          </p>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200 text-sm">{error}</p>
            </div>
          )}
          
          {renderQuestion()}
          
          <div className="flex justify-between mt-8">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 1}
            >
              Previous
            </Button>
            
            {currentStep === quizQuestions.length ? (
              <Button
                onClick={submitQuiz}
                disabled={!canProceed() || isLoading}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {isLoading ? "Analyzing..." : "Complete Quiz"}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            ) : (
              <Button
                onClick={nextStep}
                disabled={!canProceed()}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                Next
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
