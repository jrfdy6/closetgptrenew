"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Sparkles, Palette, Camera, TrendingUp, Heart, ArrowRight, CheckCircle } from "lucide-react";
import { useAuthContext } from "@/contexts/AuthContext";
import BodyPositiveMessage from "@/components/BodyPositiveMessage";

interface QuizAnswer {
  question_id: string;
  selected_option: string;
}

interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  category: string;
  type?: "visual" | "text" | "rgb_slider" | "visual_yesno";
  images?: string[];
  gender?: string;
  style_name?: string;
  colors?: string[];
}

// Simple, clean quiz questions
const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: "gender",
    question: "What is your gender?",
    options: ["Female", "Male", "Non-binary", "Prefer not to say"],
    category: "personal"
  },
  {
    id: "body_type_female",
    question: "Which body shape best describes you? (All bodies are beautiful!)",
    options: ["Round/Apple", "Athletic", "Hourglass", "Pear", "Rectangle", "Inverted Triangle", "Plus Size", "Petite", "Tall"],
    category: "measurements",
    type: "visual",
    images: [
      "/images/body-types/apple.png",
      "/images/body-types/athletic.png",
      "/images/body-types/hourglass.png",
      "/images/body-types/pear.png",
      "/images/body-types/rectangular.png",
      "/images/body-types/inverted.png",
      "/images/body-types/curvy.png",
      "/images/body-types/athletic.png",
      "/images/body-types/athletic.png"
    ],
    gender: "female"
  },
  {
    id: "body_type_male",
    question: "Which body shape best describes you? (All bodies are beautiful!)",
    options: ["Round/Apple", "Athletic", "Rectangle", "Inverted Triangle", "Pear", "Oval", "Plus Size", "Slim", "Muscular"],
    category: "measurements",
    type: "visual",
    images: [
      "/images/body-types/apple.png",
      "/images/body-types/athletic.png",
      "/images/body-types/rectangular.png",
      "/images/body-types/inverted.png",
      "/images/body-types/pear.png",
      "/images/body-types/curvy.png",
      "/images/body-types/curvy.png",
      "/images/body-types/athletic.png",
      "/images/body-types/athletic.png"
    ],
    gender: "male"
  },
  {
    id: "skin_tone",
    question: "Select your skin tone using the slider below",
    options: ["skin_tone_slider"],
    category: "measurements",
    type: "rgb_slider"
  },
  {
    id: "height",
    question: "What is your height?",
    options: ["Under 5'0\"", "5'0\" - 5'3\"", "5'4\" - 5'7\"", "5'8\" - 5'11\"", "6'0\" - 6'3\"", "Over 6'3\""],
    category: "measurements"
  },
  {
    id: "weight",
    question: "What is your weight range? (Optional - helps with fit recommendations)",
    options: ["Under 100 lbs", "100-120 lbs", "121-140 lbs", "141-160 lbs", "161-180 lbs", "181-200 lbs", "201-250 lbs", "251-300 lbs", "Over 300 lbs", "Prefer not to specify"],
    category: "measurements"
  },
  {
    id: "top_size",
    question: "What is your top size?",
    options: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "4XL", "5XL", "6XL", "Plus Size", "Custom/Other"],
    category: "sizes"
  },
  {
    id: "bottom_size",
    question: "What is your bottom size?",
    options: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "4XL", "5XL", "6XL", "Plus Size", "Custom/Other"],
    category: "sizes"
  },
  {
    id: "cup_size",
    question: "What is your cup size? (Optional)",
    options: ["AA", "A", "B", "C", "D", "DD", "DDD", "E", "F", "FF", "G", "GG", "H", "HH", "I", "J", "K", "L", "M", "N", "O", "P", "Prefer not to say"],
    category: "sizes"
  },
  {
    id: "shoe_size",
    question: "What is your shoe size?",
    options: ["4 or smaller", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16 or larger", "Wide width", "Narrow width", "Custom/Other"],
    category: "sizes"
  },
  // Female style questions - using different numbered images for color variety
  {
    id: "style_item_f_1",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-ST4.png"],
    style_name: "Street Style",
    colors: ["black", "red", "white", "gray"],
    gender: "female"
  },
  {
    id: "style_item_f_2",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-CB5.png"],
    style_name: "Cottagecore",
    colors: ["pink", "cream", "brown", "green"],
    gender: "female"
  },
  {
    id: "style_item_f_3",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-MIN6.png"],
    style_name: "Minimalist",
    colors: ["white", "beige", "gray", "navy"],
    gender: "female"
  },
  {
    id: "style_item_f_4",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-OM7.png"],
    style_name: "Old Money",
    colors: ["burgundy", "camel", "cream", "navy"],
    gender: "female"
  },
  {
    id: "style_item_f_5",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-ST8.png"],
    style_name: "Urban Street",
    colors: ["black", "blue", "white", "gray"],
    gender: "female"
  },
  {
    id: "style_item_f_6",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-CB9.png"],
    style_name: "Natural Boho",
    colors: ["brown", "terracotta", "cream", "green"],
    gender: "female"
  },
  {
    id: "style_item_f_7",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-MIN10.png"],
    style_name: "Clean Minimal",
    colors: ["white", "gray", "black", "beige"],
    gender: "female"
  },
  {
    id: "style_item_f_8",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/F-OM3.png"],
    style_name: "Classic Elegant",
    colors: ["navy", "burgundy", "camel", "cream"],
    gender: "female"
  },
  // Male style questions - using different numbered images for color variety
  {
    id: "style_item_m_1",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-ST3.png"],
    style_name: "Street Style",
    colors: ["black", "red", "gray", "white"],
    gender: "male"
  },
  {
    id: "style_item_m_2",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-CB4.png"],
    style_name: "Cottagecore",
    colors: ["brown", "green", "cream", "olive"],
    gender: "male"
  },
  {
    id: "style_item_m_3",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-MIN5.png"],
    style_name: "Minimalist",
    colors: ["white", "beige", "gray", "navy"],
    gender: "male"
  },
  {
    id: "style_item_m_4",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-OM6.png"],
    style_name: "Old Money",
    colors: ["burgundy", "camel", "cream", "navy"],
    gender: "male"
  },
  {
    id: "style_item_m_5",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-ST7.png"],
    style_name: "Urban Street",
    colors: ["black", "blue", "white", "gray"],
    gender: "male"
  },
  {
    id: "style_item_m_6",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-CB8.png"],
    style_name: "Natural Boho",
    colors: ["brown", "terracotta", "cream", "green"],
    gender: "male"
  },
  {
    id: "style_item_m_7",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-MIN9.png"],
    style_name: "Clean Minimal",
    colors: ["white", "gray", "black", "beige"],
    gender: "male"
  },
  {
    id: "style_item_m_8",
    question: "Do you like this style?",
    options: ["Yes", "No"],
    category: "aesthetic",
    type: "visual_yesno",
    images: ["/images/outfit-quiz/M-OM10.png"],
    style_name: "Classic Elegant",
    colors: ["navy", "burgundy", "camel", "cream"],
    gender: "male"
  },
  {
    id: "daily_activities",
    question: "What best describes your daily activities?",
    options: ["Office work and meetings", "Creative work and casual meetings", "Active lifestyle and sports", "Mix of everything"],
    category: "lifestyle"
  },
  {
    id: "style_elements",
    question: "Which style elements do you gravitate towards?",
    options: ["Clean lines and minimal details", "Rich textures and patterns", "Classic and timeless pieces", "Bold and statement pieces"],
    category: "style"
  }
];

export default function Onboarding() {
  const [currentStep, setCurrentStep] = useState(1);
  const [answers, setAnswers] = useState<QuizAnswer[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userGender, setUserGender] = useState<string | null>(null);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [quizResults, setQuizResults] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const { user, loading: authLoading } = useAuthContext();


  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      window.location.href = '/';
    }
  }, [user, authLoading]);

  // Filter questions based on gender
  const getFilteredQuestions = (): QuizQuestion[] => {
    // Always show all questions initially, then filter based on gender selection
    return QUIZ_QUESTIONS.filter(question => {
      // Show cup size only for females
      if (question.id === 'cup_size' && userGender && userGender !== 'female') {
        return false;
      }
      
      // Show gender-specific body type questions
      if (question.id === 'body_type_female' && userGender && userGender !== 'female') {
        return false;
      }
      if (question.id === 'body_type_male' && userGender && userGender !== 'male') {
        return false;
      }
      
      // Show gender-specific style questions
      if (question.id.startsWith('style_item_f_') && userGender && userGender !== 'female') {
        return false;
      }
      if (question.id.startsWith('style_item_m_') && userGender && userGender !== 'male') {
        return false;
      }
      
      return true;
    });
  };

  const filteredQuestions = getFilteredQuestions();


  const handleAnswer = (questionId: string, selectedOption: string) => {
    const newAnswers = answers.filter(a => a.question_id !== questionId);
    newAnswers.push({ question_id: questionId, selected_option: selectedOption });
    setAnswers(newAnswers);

    // Track gender selection
    if (questionId === 'gender') {
      setUserGender(selectedOption.toLowerCase());
    }
  };

  const nextStep = () => {
    if (currentStep < filteredQuestions.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = () => {
    if (filteredQuestions.length === 0) return false;
    const currentQuestion = filteredQuestions[currentStep - 1];
    return answers.some(a => a.question_id === currentQuestion.id);
  };

  // Analyze colors from user's style preferences
  const analyzeColors = () => {
    const colorCounts: { [key: string]: number } = {};
    const likedStyles: string[] = [];

    // Count colors from styles the user liked
    answers.forEach(answer => {
      if (answer.selected_option === "Yes" && (answer.question_id.startsWith("style_item_f_") || answer.question_id.startsWith("style_item_m_"))) {
        const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
        if (question && question.colors) {
          likedStyles.push(question.style_name || "");
          question.colors.forEach(color => {
            colorCounts[color] = (colorCounts[color] || 0) + 1;
          });
        }
      }
    });

    // Get top 3 colors
    const topColors = Object.entries(colorCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3)
      .map(([color]) => color);

    return {
      topColors,
      likedStyles,
      colorCounts
    };
  };

  const generateStyleName = () => {
    const userAnswers = answers.reduce((acc, answer) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {} as Record<string, string>);

    // Analyze style preferences from answers
    const styleScores: Record<string, number> = {};
    
    // Count style preferences from visual questions
    answers.forEach(answer => {
      const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
      if (question && question.type === 'visual_yesno' && answer.selected_option === 'Yes') {
        // Extract style from question id or style_name
        const styleName = question.style_name || question.id.replace('style_item_', '').replace(/_[fm]_\d+/, '');
        if (styleName) {
          styleScores[styleName] = (styleScores[styleName] || 0) + 1;
        }
      }
    });

    // Get top 2 styles
    const topStyles = Object.entries(styleScores)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([style]) => style);

    if (topStyles.length >= 2) {
      return `${topStyles[0]} ${topStyles[1]}`;
    } else if (topStyles.length === 1) {
      return topStyles[0];
    } else {
      // Fallback based on other answers
      const gender = userAnswers.gender;
      const bodyType = userAnswers.body_type_female || userAnswers.body_type_male;
      
      if (bodyType === 'Athletic') return 'Athletic Chic';
      if (bodyType === 'Hourglass') return 'Classic Elegant';
      if (bodyType === 'Pear') return 'Sophisticated Style';
      if (bodyType === 'Rectangle') return 'Modern Minimalist';
      if (bodyType === 'Round/Apple') return 'Comfortable Classic';
      
      return 'Personal Style';
    }
  };

  const submitQuiz = async () => {
    if (!user) {
      setError('Please sign in to complete the quiz');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const colorAnalysis = analyzeColors();
      const token = await user.getIdToken();
      const response = await fetch('/api/style-quiz/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          userId: user.uid,
          answers: answers,
          colorAnalysis: colorAnalysis
        })
      });

      if (response.ok) {
        const data = await response.json();
        setQuizCompleted(true);
        setQuizResults({
          ...data,
          hybridStyleName: generateStyleName(), // Override with generated style name
          colorAnalysis: colorAnalysis,
          userAnswers: answers.reduce((acc, answer) => {
            acc[answer.question_id] = answer.selected_option;
            return acc;
          }, {} as Record<string, string>)
        });
      } else {
        throw new Error('Failed to submit quiz');
      }
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError('Failed to submit quiz. Please try again.');
      // Use actual user answers as fallback instead of mock data
      const colorAnalysis = analyzeColors();
      const userAnswers = answers.reduce((acc, answer) => {
        acc[answer.question_id] = answer.selected_option;
        return acc;
      }, {} as Record<string, string>);
      
      setQuizCompleted(true);
      setQuizResults({
        hybridStyleName: generateStyleName(),
        quizResults: {
          aesthetic_scores: { "classic": 0.6, "sophisticated": 0.4 },
          color_season: userAnswers.skin_tone || "warm_spring",
          body_type: userAnswers.body_type_female || userAnswers.body_type_male || "rectangle",
          style_preferences: { "classic": 0.7, "minimalist": 0.3 }
        },
        colorAnalysis: colorAnalysis,
        userAnswers: userAnswers
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderQuestion = () => {
    if (filteredQuestions.length === 0) {
      console.error('No questions available for quiz');
      return (
        <div className="text-center p-8">
          <p className="text-red-600 dark:text-red-400">No questions available. Please refresh the page.</p>
        </div>
      );
    }
    
    const question = filteredQuestions[currentStep - 1];
    if (!question) {
      console.error('No question found for current step:', currentStep);
      return (
        <div className="text-center p-8">
          <p className="text-red-600 dark:text-red-400">Question not found. Please refresh the page.</p>
        </div>
      );
    }
    
    const currentAnswer = answers.find(a => a.question_id === question.id);

    return (
      <div className="space-y-12 animate-fade-in">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-serif text-gray-900 dark:text-white mb-8 leading-tight">
            {question.question}
          </h2>
          {question.type === "visual" && (
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Click on the image that best represents your style
            </p>
          )}
          {question.type === "multiple_choice" && (
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Choose the option that best describes you
            </p>
          )}
          {question.type === "rgb_slider" && (
            <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
              Drag the slider to select your skin tone
            </p>
          )}
        </div>
        
        {question.type === "visual" && question.images ? (
          <div className="space-y-4">
            {(question.id === "body_type_female" || question.id === "body_type_male") && (
              <BodyPositiveMessage variant="profile" className="mb-4" />
            )}
            <div className="grid grid-cols-2 gap-4 min-h-[400px]">
              {question.options.map((option, index) => (
              <div
                key={option}
                className={`relative cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 h-[200px] ${
                  currentAnswer?.selected_option === option
                    ? "border-purple-600 ring-2 ring-purple-200 dark:ring-purple-800"
                    : "border-gray-200 dark:border-gray-700 hover:border-purple-300 dark:hover:border-purple-600"
                }`}
                onClick={() => {
                  handleAnswer(question.id, option);
                }}
              >
                <div className="aspect-square relative h-[140px] bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 flex items-center justify-center rounded-t-lg">
                  <div className="flex flex-col items-center justify-center space-y-2">
                    <div className="w-16 h-16 rounded-full bg-purple-200 dark:bg-purple-800 flex items-center justify-center">
                      <span className="text-2xl">
                        {option === 'Round/Apple' ? '🍎' :
                         option === 'Athletic' ? '💪' :
                         option === 'Hourglass' ? '⏳' :
                         option === 'Pear' ? '🍐' :
                         option === 'Rectangle' ? '📐' :
                         option === 'Inverted Triangle' ? '🔺' :
                         option === 'Oval' ? '🥚' :
                         option === 'Plus Size' ? '❤️' :
                         option === 'Slim' ? '🌿' :
                         option === 'Muscular' ? '🏋️' :
                         option === 'Petite' ? '🌸' :
                         option === 'Tall' ? '🌲' : '👤'}
                      </span>
                    </div>
                    <span className="text-xs font-medium text-purple-700 dark:text-purple-300 text-center px-2">
                      {option}
                    </span>
                  </div>
                  <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all duration-200 rounded-t-lg" />
                </div>
                <div className="p-3 bg-white dark:bg-gray-800 h-[60px] flex items-center justify-center">
                  <p className="text-center font-medium text-gray-900 dark:text-white text-sm">
                    {option}
                  </p>
                </div>
              </div>
            ))}
            </div>
          </div>
        ) : question.type === "visual_yesno" && question.images ? (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border-2 border-gray-200 dark:border-gray-700">
              <div className="aspect-[4/5] relative mb-4">
                <img
                  src={question.images[0]}
                  alt={question.style_name}
                  className="w-full h-full object-cover rounded-lg"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = "/placeholder.png";
                  }}
                />
              </div>
              <div className="text-center mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                  {question.style_name}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {question.colors?.join(", ").replace(/\b\w/g, l => l.toUpperCase())}
                </p>
              </div>
              <div className="flex gap-4 justify-center">
                <Button
                  variant={currentAnswer?.selected_option === "Yes" ? "default" : "outline"}
                  className="flex-1 h-12 text-lg"
                  onClick={() => {
                    handleAnswer(question.id, "Yes");
                  }}
                >
                  👍 Yes
                </Button>
                <Button
                  variant={currentAnswer?.selected_option === "No" ? "default" : "outline"}
                  className="flex-1 h-12 text-lg"
                  onClick={() => {
                    handleAnswer(question.id, "No");
                  }}
                >
                  👎 No
                </Button>
              </div>
            </div>
          </div>
        ) : question.type === "rgb_slider" ? (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg border-2 border-gray-200 dark:border-gray-700">
              <div className="space-y-4">
                <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                  <span>Lightest</span>
                  <span>Darkest</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  defaultValue="50"
                  className="w-full h-8 rounded-lg appearance-none cursor-pointer"
                  style={{
                    background: 'linear-gradient(to right, #FEF3C7, #FDE68A, #FCD34D, #F59E0B, #D97706, #B45309, #92400E, #78350F, #451A03, #1F2937)'
                  }}
                  onChange={(e) => {
                    const value = parseInt(e.target.value);
                    const skinTone = `skin_tone_${value}`;
                    handleAnswer(question.id, skinTone);
                  }}
                />
                <div className="text-center">
                  <div 
                    className="w-16 h-16 rounded-full border-4 border-gray-300 dark:border-gray-600 mx-auto mb-2"
                    style={{ 
                      backgroundColor: currentAnswer?.selected_option ? 
                        `hsl(${Math.max(0, 30 - (parseInt(currentAnswer.selected_option.split('_')[2]) || 50) * 0.3)}, ${Math.max(20, 60 - (parseInt(currentAnswer.selected_option.split('_')[2]) || 50) * 0.4)}%, ${Math.max(20, 80 - (parseInt(currentAnswer.selected_option.split('_')[2]) || 50) * 0.6)}%)` :
                        'hsl(30, 40%, 60%)'
                    }}
                  />
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {currentAnswer?.selected_option ? 
                      `Skin tone: ${currentAnswer.selected_option.split('_')[2] || 50}%` : 
                      'Select your skin tone'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
        <div className="space-y-3 max-w-2xl mx-auto">
          {question.options.map((option) => (
            <button
              key={option}
              className={`w-full py-5 px-6 rounded-full text-lg font-medium transition-all duration-300 ${
                currentAnswer?.selected_option === option
                  ? "bg-gray-900 text-white dark:bg-white dark:text-gray-900 shadow-lg"
                  : "bg-white text-gray-900 border border-gray-300 hover:border-gray-400 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:border-gray-500"
              }`}
              onClick={() => {
                handleAnswer(question.id, option);
              }}
            >
              <div className="text-center">
                <div className="font-semibold mb-1">{option}</div>
                <div className="text-sm opacity-75">
                  {option === 'Contemporary' ? 'minimalist, timeless pieces' :
                   option === 'Classic' ? 'elegant, sophisticated style' :
                   option === 'Street Style' ? 'urban, edgy fashion' :
                   option === 'Bohemian' ? 'free-spirited, artistic vibe' :
                   option === 'Preppy' ? 'clean, collegiate aesthetic' :
                   option === 'Romantic' ? 'feminine, delicate details' :
                   option === 'Athletic' ? 'sporty, functional wear' :
                   option === 'Vintage' ? 'retro, nostalgic charm' :
                   'sophisticated, refined look'}
                </div>
              </div>
            </button>
          ))}
        </div>
        )}
      </div>
    );
  };

  // Show loading state while authenticating
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl border-0 shadow-xl text-center">
          <CardContent className="p-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Authenticating...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!user) {
    return null; // Will redirect via useEffect
  }

  if (quizCompleted && quizResults) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl text-center">
          <div className="mb-16">
            <h1 className="text-4xl md:text-5xl font-serif text-gray-900 dark:text-white mb-8 leading-tight">
              Great choice — {quizResults.hybridStyleName?.toLowerCase()}, timeless confidence
            </h1>
            <div className="text-center mb-8">
              <div className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-4">
                {quizResults.hybridStyleName?.toUpperCase() || "PERSONAL STYLE"}
              </div>
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed">
                We've styled over 1 million outfits, and here's what we've learned: The #1 reason people stick around? The fit. When it fits right, it feels right. And when you feel right, you show up different.
              </p>
            </div>
          </div>
          <div className="space-y-8 max-w-3xl mx-auto">
            {/* Style traits */}
            <div className="text-center">
              <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">Your style traits</p>
              <div className="flex flex-wrap justify-center gap-2">
                <span className="px-4 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium dark:bg-red-900 dark:text-red-200">
                  Calculated
                </span>
                <span className="px-4 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium dark:bg-red-900 dark:text-red-200">
                  Versatile
                </span>
                <span className="px-4 py-2 bg-red-100 text-red-800 rounded-full text-sm font-medium dark:bg-red-900 dark:text-red-200">
                  Confident
                </span>
              </div>
            </div>

            {/* Style description */}
            <div className="text-center space-y-4">
              <h2 className="text-2xl font-serif text-gray-900 dark:text-white">
                You play the long game with your look.
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                The {quizResults.hybridStyleName || "Personal Style"} style adapts to any situation. You're prepared, and your style reflects that confidence. When it fits right, it feels right.
              </p>
              <a href="#" className="text-sm text-gray-500 dark:text-gray-400 underline hover:text-gray-700 dark:hover:text-gray-300">
                see more
              </a>
            </div>
            
            <div className="text-center">
              <Link href="/dashboard">
                <button className="px-12 py-4 bg-gray-900 text-white rounded-lg text-lg font-medium hover:bg-gray-800 transition-all duration-300 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100 shadow-lg">
                  See My Plan Options
                  <ArrowRight className="ml-3 h-5 w-5 inline-block" />
                </button>
              </Link>
              <div className="mt-4 flex items-center justify-center space-x-2">
                <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-600 dark:text-gray-400">4</span>
                </div>
                <span className="text-sm text-gray-500 dark:text-gray-400">classic, bold, or both—so you're always ready</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-16">
          <Link href="/" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 mb-8">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
          <h1 className="text-4xl md:text-5xl font-serif text-gray-900 dark:text-white mb-8 leading-tight">
            Your style is a signal
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed mb-12">
            It doesn't just reflect who you are — it trains people how to treat you. We help you send the right signal, without the stress of figuring it out alone.
          </p>
          <div className="flex items-center justify-center space-x-2">
            {filteredQuestions.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${
                  index + 1 === currentStep
                    ? "bg-gray-900 dark:bg-white"
                    : index + 1 < currentStep
                    ? "bg-gray-600 dark:bg-gray-400"
                    : "bg-gray-300 dark:bg-gray-600"
                }`}
              />
            ))}
          </div>
        </div>
        <CardContent>
          {error && (
            <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-600 dark:text-red-400">{error}</p>
            </div>
          )}
          
          {renderQuestion()}
          
          <div className="flex justify-center mt-12">
            {currentStep === filteredQuestions.length ? (
              <button
                onClick={submitQuiz}
                disabled={!canProceed() || isLoading}
                className="px-12 py-4 bg-gray-900 text-white rounded-full text-lg font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3 inline-block"></div>
                    Analyzing...
                  </>
                ) : (
                  <>
                    Complete Quiz
                    <ArrowRight className="h-5 w-5 ml-3 inline-block" />
                  </>
                )}
              </button>
            ) : (
              <button
                onClick={nextStep}
                disabled={!canProceed()}
                className="px-12 py-4 bg-gray-900 text-white rounded-full text-lg font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
              >
                Next
                <ArrowRight className="h-5 w-5 ml-3 inline-block" />
              </button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}