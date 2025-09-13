"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles, Palette, Camera, TrendingUp, Heart, ArrowRight, CheckCircle } from "lucide-react";
import { useAuthContext } from "@/contexts/AuthContext";
import BodyPositiveMessage from "@/components/BodyPositiveMessage";

interface QuizAnswer {
  question_id: string;
  selected_option: string;
}

interface StylePersona {
  id: string;
  name: string;
  tagline: string;
  description: string;
  styleMission: string;
  examples: string[];
  traits: string[];
  cta: string;
}

const STYLE_PERSONAS: Record<string, StylePersona> = {
  architect: {
    id: "architect",
    name: "The Architect",
    tagline: "Clean fits. Simple choices. Always looks good.",
    description: "You're that person who always looks put together without trying too hard. Your style is built on solid foundations - quality basics, perfect fits, and a neutral palette that works everywhere. You believe in investing in pieces that last and building a wardrobe that makes getting dressed effortless.",
    styleMission: "Your style journey is about adding layers to what you've already built. Start experimenting with textures, subtle patterns, and statement accessories while keeping your core aesthetic intact.",
    examples: ["Michael B. Jordan", "Ryan Gosling", "John Cho", "Oscar Isaac", "Idris Elba"],
    traits: [
      "Minimal but fresh",
      "Sticks to what works", 
      "Neutral colors on lock",
      "Details matter",
      "Effortless vibes"
    ],
    cta: "See My Plan Options →"
  },
  strategist: {
    id: "strategist", 
    name: "The Strategist",
    tagline: "Street style meets sophistication. Always ready for anything.",
    description: "You know how to mix classic and bold. Your style adapts to any situation - from boardroom to bar - because you understand the power of versatile pieces and smart layering. You're not afraid to take risks, but they're always calculated ones.",
    styleMission: "Keep building your flexible wardrobe. Every move is intentional. Focus on pieces that can transition between formal and casual, and don't be afraid to mix high and low.",
    examples: ["Donald Glover", "Chris Paul", "John Legend", "Mahershala Ali", "Lakeith Stanfield"],
    traits: [
      "Calculated risks",
      "Versatile pieces",
      "Confident mixing",
      "Adapts to any situation",
      "Quality over quantity"
    ],
    cta: "See My Plan Options →"
  },
  innovator: {
    id: "innovator",
    name: "The Innovator", 
    tagline: "Bold choices. Creative expression. Stand out from the crowd.",
    description: "You're not afraid to be the most stylish person in the room. Your style is a form of self-expression and creativity. You experiment with trends, mix unexpected pieces, and aren't afraid to take fashion risks that pay off.",
    styleMission: "Push boundaries while staying true to your vision. Focus on unique pieces that tell your story and don't be afraid to be the trendsetter in your circle.",
    examples: ["Pharrell Williams", "Tyler, The Creator", "A$AP Rocky", "Jaden Smith", "Timothée Chalamet"],
    traits: [
      "Trendsetter",
      "Creative expression",
      "Bold choices",
      "Unique pieces",
      "Confident individuality"
    ],
    cta: "See My Plan Options →"
  },
  classic: {
    id: "classic",
    name: "The Classic",
    tagline: "Timeless elegance. Sophisticated style. Never goes out of fashion.",
    description: "You appreciate the finer things and believe in investing in quality pieces that will last decades. Your style is refined, sophisticated, and built on traditional menswear principles. You look polished without being flashy.",
    styleMission: "Refine your existing foundation. Focus on perfect tailoring, quality fabrics, and subtle details that elevate your look without being obvious.",
    examples: ["George Clooney", "David Beckham", "Henry Golding", "Regé-Jean Page", "Dev Patel"],
    traits: [
      "Timeless pieces",
      "Quality investment",
      "Sophisticated details",
      "Refined taste",
      "Elegant simplicity"
    ],
    cta: "See My Plan Options →"
  },
  wanderer: {
    id: "wanderer",
    name: "The Wanderer",
    tagline: "Free spirit. Earthy vibes. Connected to nature.",
    description: "Your style reflects your connection to the natural world and your free-spirited approach to life. You gravitate toward earthy tones, flowing fabrics, and pieces that tell a story. Your wardrobe is an extension of your values - sustainable, authentic, and effortlessly beautiful.",
    styleMission: "Embrace your natural aesthetic while adding structure. Focus on quality natural fabrics and pieces that can transition from day to night, city to country.",
    examples: ["Zendaya", "Florence Pugh", "Emma Stone", "Lupita Nyong'o", "Tessa Thompson"],
    traits: [
      "Earth tones",
      "Natural fabrics",
      "Free-spirited",
      "Sustainable choices",
      "Effortless beauty"
    ],
    cta: "See My Plan Options →"
  },
  rebel: {
    id: "rebel",
    name: "The Rebel",
    tagline: "Street smart. Bold statements. Own the room.",
    description: "You're not here to blend in - you're here to stand out. Your style is bold, confident, and unapologetically you. You mix streetwear with high fashion, aren't afraid of bright colors, and use fashion as a form of self-expression and rebellion against the ordinary.",
    styleMission: "Keep pushing boundaries while building a cohesive wardrobe. Focus on statement pieces that reflect your personality and don't be afraid to mix unexpected elements.",
    examples: ["Rihanna", "Billie Eilish", "Lil Nas X", "Bad Bunny", "Doja Cat"],
    traits: [
      "Bold statements",
      "Street smart",
      "Confident mixing",
      "Trend forward",
      "Unapologetic style"
    ],
    cta: "See My Plan Options →"
  },
  connoisseur: {
    id: "connoisseur",
    name: "The Connoisseur",
    tagline: "Refined taste. Luxury details. Quiet confidence.",
    description: "You have an eye for quality and appreciate the finer things in life. Your style is sophisticated, understated, and built on investment pieces that speak to your refined taste. You understand that true luxury is in the details, not the labels.",
    styleMission: "Curate your collection with intention. Focus on exceptional pieces that will last decades and don't be afraid to invest in quality over quantity.",
    examples: ["Meghan Markle", "Blake Lively", "Ryan Reynolds", "Henry Cavill", "Cate Blanchett"],
    traits: [
      "Refined taste",
      "Quality over quantity",
      "Luxury details",
      "Quiet confidence",
      "Investment pieces"
    ],
    cta: "See My Plan Options →"
  },
  modernist: {
    id: "modernist",
    name: "The Modernist",
    tagline: "Clean lines. Contemporary edge. Future-focused.",
    description: "You're drawn to clean, contemporary design and appreciate the intersection of fashion and function. Your style is modern, streamlined, and forward-thinking. You value versatility and pieces that work across different contexts while maintaining a sleek, contemporary aesthetic.",
    styleMission: "Build a wardrobe that's both functional and fashionable. Focus on versatile pieces with clean lines and don't be afraid to experiment with modern silhouettes.",
    examples: ["Hailey Bieber", "Kendall Jenner", "Timothée Chalamet", "Harry Styles", "Anya Taylor-Joy"],
    traits: [
      "Clean lines",
      "Contemporary edge",
      "Functional fashion",
      "Versatile pieces",
      "Future-focused"
    ],
    cta: "See My Plan Options →"
  }
};

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

  const determineStylePersona = (): StylePersona => {
    const userAnswers = answers.reduce((acc, answer) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {} as Record<string, string>);

    // Score each persona based on quiz answers
    const personaScores: Record<string, number> = {
      architect: 0,
      strategist: 0,
      innovator: 0,
      classic: 0,
      wanderer: 0,
      rebel: 0,
      connoisseur: 0,
      modernist: 0
    };

    // Analyze visual style preferences from quiz answers
    const stylePreferences: Record<string, number> = {};
    answers.forEach(answer => {
      const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
      if (question && question.type === 'visual_yesno' && answer.selected_option === 'Yes') {
        const styleName = question.style_name;
        if (styleName) {
          stylePreferences[styleName] = (stylePreferences[styleName] || 0) + 1;
        }
      }
    });

    // Map style preferences to personas
    if (stylePreferences['Minimalist'] || stylePreferences['Clean Minimal']) {
      personaScores.architect += 3;
      personaScores.modernist += 2;
    }
    if (stylePreferences['Street Style'] || stylePreferences['Urban Street']) {
      personaScores.rebel += 3;
      personaScores.strategist += 2;
    }
    if (stylePreferences['Classic Elegant']) {
      personaScores.classic += 3;
      personaScores.connoisseur += 2;
    }
    if (stylePreferences['Old Money']) {
      personaScores.connoisseur += 3;
      personaScores.classic += 2;
    }
    if (stylePreferences['Cottagecore'] || stylePreferences['Natural Boho']) {
      personaScores.wanderer += 3;
    }

    // Daily activities scoring
    if (userAnswers.daily_activities === 'Office work and meetings') {
      personaScores.classic += 2;
      personaScores.architect += 1;
      personaScores.connoisseur += 1;
    }
    if (userAnswers.daily_activities === 'Creative work and casual meetings') {
      personaScores.strategist += 2;
      personaScores.innovator += 1;
      personaScores.modernist += 1;
    }
    if (userAnswers.daily_activities === 'Active lifestyle and sports') {
      personaScores.rebel += 2;
      personaScores.strategist += 1;
    }
    if (userAnswers.daily_activities === 'Mix of everything') {
      personaScores.strategist += 3;
      personaScores.modernist += 2;
    }

    // Style elements scoring
    if (userAnswers.style_elements === 'Clean lines and minimal details') {
      personaScores.architect += 3;
      personaScores.modernist += 2;
    }
    if (userAnswers.style_elements === 'Rich textures and patterns') {
      personaScores.connoisseur += 3;
      personaScores.wanderer += 2;
    }
    if (userAnswers.style_elements === 'Classic and timeless pieces') {
      personaScores.classic += 3;
      personaScores.architect += 1;
    }
    if (userAnswers.style_elements === 'Bold and statement pieces') {
      personaScores.rebel += 3;
      personaScores.innovator += 2;
    }

    // Body type scoring
    const bodyType = userAnswers.body_type_female || userAnswers.body_type_male;
    if (bodyType === 'Rectangle' || bodyType === 'Athletic') {
      personaScores.architect += 1;
      personaScores.strategist += 1;
      personaScores.modernist += 1;
    }
    if (bodyType === 'Hourglass' || bodyType === 'Pear') {
      personaScores.strategist += 1;
      personaScores.wanderer += 1;
    }
    if (bodyType === 'Plus Size') {
      personaScores.wanderer += 1;
      personaScores.connoisseur += 1;
    }

    // Find the highest scoring persona
    const sortedPersonas = Object.entries(personaScores)
      .sort(([,a], [,b]) => b - a);
    
    const topPersona = sortedPersonas[0][0];
    
    // Debug logging
    console.log('🎯 [Persona] Persona scores:', personaScores);
    console.log('🎯 [Persona] Sorted personas:', sortedPersonas);
    console.log('🎯 [Persona] Selected persona:', topPersona);

    return STYLE_PERSONAS[topPersona] || STYLE_PERSONAS.strategist;
  };

  const generateStyleTraits = () => {
    const userAnswers = answers.reduce((acc, answer) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {} as Record<string, string>);

    const traits: string[] = [];

    // Analyze for "Calculated" trait
    const calculatedIndicators = [
      userAnswers.style_preference === 'Classic',
      userAnswers.style_preference === 'Minimalist',
      userAnswers.body_type_female === 'Rectangle' || userAnswers.body_type_male === 'Rectangle',
      userAnswers.body_type_female === 'Athletic' || userAnswers.body_type_male === 'Athletic',
      userAnswers.color_preference === 'Neutral',
      userAnswers.occasion_preference === 'Professional'
    ];
    if (calculatedIndicators.filter(Boolean).length >= 2) {
      traits.push('Calculated');
    }

    // Analyze for "Versatile" trait
    const versatileIndicators = [
      userAnswers.style_preference === 'Contemporary',
      userAnswers.occasion_preference === 'Casual',
      userAnswers.occasion_preference === 'Both',
      userAnswers.color_preference === 'Both',
      userAnswers.body_type_female === 'Hourglass' || userAnswers.body_type_male === 'Hourglass',
      userAnswers.body_type_female === 'Pear' || userAnswers.body_type_male === 'Pear'
    ];
    if (versatileIndicators.filter(Boolean).length >= 2) {
      traits.push('Versatile');
    }

    // Analyze for "Confident" trait
    const confidentIndicators = [
      userAnswers.style_preference === 'Street Style',
      userAnswers.style_preference === 'Bold',
      userAnswers.color_preference === 'Bold',
      userAnswers.body_type_female === 'Athletic' || userAnswers.body_type_male === 'Athletic',
      userAnswers.occasion_preference === 'Formal',
      userAnswers.occasion_preference === 'Both'
    ];
    if (confidentIndicators.filter(Boolean).length >= 2) {
      traits.push('Confident');
    }

    // Fallback traits if none match
    if (traits.length === 0) {
      traits.push('Calculated', 'Versatile', 'Confident');
    }

    // Ensure we have at least 3 traits
    const fallbackTraits = ['Calculated', 'Versatile', 'Confident'];
    while (traits.length < 3) {
      const remainingTrait = fallbackTraits.find(trait => !traits.includes(trait));
      if (remainingTrait) {
        traits.push(remainingTrait);
      } else {
        break;
      }
    }

    return traits.slice(0, 3);
  };

  const generateStyleFingerprint = () => {
    const userAnswers = answers.reduce((acc, answer) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {} as Record<string, string>);

    // Creative Expression: Restrained vs Expressive
    let creativeScore = 50; // Start neutral
    if (userAnswers.style_preference === 'Street Style' || userAnswers.style_preference === 'Bold') {
      creativeScore += 30; // More expressive
    }
    if (userAnswers.style_preference === 'Classic' || userAnswers.style_preference === 'Minimalist') {
      creativeScore -= 20; // More restrained
    }
    if (userAnswers.color_preference === 'Bold') {
      creativeScore += 15;
    }
    if (userAnswers.color_preference === 'Neutral') {
      creativeScore -= 15;
    }
    creativeScore = Math.max(10, Math.min(90, creativeScore)); // Keep between 10-90

    // Trend Awareness: Timeless vs Trendsetting
    let trendScore = 50; // Start neutral
    if (userAnswers.style_preference === 'Contemporary' || userAnswers.style_preference === 'Street Style') {
      trendScore += 25; // More trendsetting
    }
    if (userAnswers.style_preference === 'Classic' || userAnswers.style_preference === 'Vintage') {
      trendScore -= 25; // More timeless
    }
    if (userAnswers.occasion_preference === 'Casual') {
      trendScore += 10;
    }
    if (userAnswers.occasion_preference === 'Professional') {
      trendScore -= 10;
    }
    trendScore = Math.max(10, Math.min(90, trendScore)); // Keep between 10-90

    // Wardrobe Flexibility: Focused vs Versatile
    let flexibilityScore = 50; // Start neutral
    if (userAnswers.occasion_preference === 'Both') {
      flexibilityScore += 30; // More versatile
    }
    if (userAnswers.color_preference === 'Both') {
      flexibilityScore += 20;
    }
    if (userAnswers.color_preference === 'Neutral') {
      flexibilityScore += 10; // Neutrals are versatile
    }
    if (userAnswers.style_preference === 'Contemporary') {
      flexibilityScore += 15;
    }
    if (userAnswers.style_preference === 'Classic') {
      flexibilityScore += 10; // Classics are versatile
    }
    if (userAnswers.occasion_preference === 'Professional') {
      flexibilityScore -= 15; // More focused
    }
    flexibilityScore = Math.max(10, Math.min(90, flexibilityScore)); // Keep between 10-90

    return {
      creativeExpression: {
        restrained: 100 - creativeScore,
        expressive: creativeScore
      },
      trendAwareness: {
        timeless: 100 - trendScore,
        trendsetting: trendScore
      },
      wardrobeFlexibility: {
        focused: 100 - flexibilityScore,
        versatile: flexibilityScore
      }
    };
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
          hybridStyleName: determineStylePersona().name, // Use persona name
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
        hybridStyleName: determineStylePersona().name, // Use persona name
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
      <div className="animate-fade-in">
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
                    <div className="font-semibold">{option}</div>
                  </div>
                </button>
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
                {question.type === "multiple_choice" && (
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
                )}
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-white mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Authenticating...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!user) {
    return null; // Will redirect via useEffect
  }

  if (quizCompleted && quizResults) {
    const persona = determineStylePersona();
    
    // Debug logging
    console.log('🎭 [Onboarding] Determined persona:', persona);
    console.log('🎭 [Onboarding] User answers:', answers);
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 flex items-center justify-center p-4">
        <div className="w-full max-w-4xl">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-serif text-gray-900 dark:text-white mb-8 leading-tight">
              {persona.tagline}
            </h1>
          </div>
          
          <div className="space-y-6">
            {/* Main Persona Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
              <div className="text-center mb-6">
                <div className="text-sm text-gray-500 dark:text-gray-400 mb-2">YOU ARE</div>
                <h2 className="text-3xl font-serif text-gray-900 dark:text-white mb-6">
                  {persona.name}
                </h2>
                <p className="text-lg text-gray-600 dark:text-gray-400 max-w-3xl mx-auto leading-relaxed mb-6">
                  {persona.description}
                </p>
                <div className="flex flex-wrap justify-center gap-2">
                  {persona.traits.map((trait, index) => (
                    <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium dark:bg-red-900 dark:text-red-200">
                      {trait}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Style Mission Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
              <h3 className="text-xl font-serif text-gray-900 dark:text-white mb-3">Your Style Mission</h3>
              <p className="text-gray-600 dark:text-gray-400">
                {persona.styleMission}
              </p>
            </div>

            {/* Cultural Anchors Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
              <h3 className="text-xl font-serif text-gray-900 dark:text-white mb-4">The {persona.name.split(' ')[1]}s You May Know</h3>
              <div className="flex flex-wrap gap-3">
                {persona.examples.map((example, index) => (
                  <div key={index} className="flex items-center space-x-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                    <span className="text-gray-600 dark:text-gray-400">♪</span>
                    <span className="text-gray-900 dark:text-white font-medium">{example}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Style Fingerprint Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
              <h3 className="text-xl font-serif text-gray-900 dark:text-white mb-6">Your Style Fingerprint</h3>
              <div className="space-y-6">
                {(() => {
                  const fingerprint = generateStyleFingerprint();
                  return (
                    <>
                      {/* Creative Expression */}
                      <div className="bg-gray-900 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-white font-medium mb-3">Creative Expression</div>
                        <div className="flex justify-between text-sm text-gray-300 mb-2">
                          <span>Restrained</span>
                          <span>Expressive</span>
                        </div>
                        <div className="flex justify-between text-sm text-white mb-2">
                          <span>{Math.round(fingerprint.creativeExpression.restrained)}%</span>
                          <span>{Math.round(fingerprint.creativeExpression.expressive)}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div className="bg-white h-2 rounded-full" style={{width: `${fingerprint.creativeExpression.expressive}%`}}></div>
                        </div>
                      </div>

                      {/* Trend Awareness */}
                      <div className="bg-gray-900 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-white font-medium mb-3">Trend Awareness</div>
                        <div className="flex justify-between text-sm text-gray-300 mb-2">
                          <span>Timeless</span>
                          <span>Trendsetting</span>
                        </div>
                        <div className="flex justify-between text-sm text-white mb-2">
                          <span>{Math.round(fingerprint.trendAwareness.timeless)}%</span>
                          <span>{Math.round(fingerprint.trendAwareness.trendsetting)}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div className="bg-white h-2 rounded-full" style={{width: `${fingerprint.trendAwareness.trendsetting}%`}}></div>
                        </div>
                      </div>

                      {/* Wardrobe Flexibility */}
                      <div className="bg-gray-900 dark:bg-gray-700 rounded-lg p-4">
                        <div className="text-white font-medium mb-3">Wardrobe Flexibility</div>
                        <div className="flex justify-between text-sm text-gray-300 mb-2">
                          <span>Focused</span>
                          <span>Versatile</span>
                        </div>
                        <div className="flex justify-between text-sm text-white mb-2">
                          <span>{Math.round(fingerprint.wardrobeFlexibility.focused)}%</span>
                          <span>{Math.round(fingerprint.wardrobeFlexibility.versatile)}%</span>
                        </div>
                        <div className="w-full bg-gray-600 rounded-full h-2">
                          <div className="bg-white h-2 rounded-full" style={{width: `${fingerprint.wardrobeFlexibility.versatile}%`}}></div>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* CTA Card */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg text-center">
              <Link href="/dashboard">
                <button className="px-8 py-4 bg-gray-900 text-white rounded-lg text-lg font-medium hover:bg-gray-800 transition-all duration-300 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100 shadow-lg">
                  {persona.cta}
                  <ArrowRight className="ml-3 h-5 w-5 inline-block" />
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl text-center">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 mb-8">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Link>
        </div>
        
        {error && (
          <div className="mb-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg max-w-2xl mx-auto">
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
      </div>
    </div>
  );
}