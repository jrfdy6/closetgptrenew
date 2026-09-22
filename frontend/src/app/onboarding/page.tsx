"use client";

// Force dynamic rendering to prevent static generation
export const dynamic = 'force-dynamic';

import React, { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Sparkles, Palette, Camera, TrendingUp, Heart, ArrowRight, CheckCircle } from "lucide-react";
import { useAuthContext } from "@/contexts/AuthContext";
import BodyPositiveMessage from "@/components/BodyPositiveMessage";
import GuidedUploadWizard from "@/components/GuidedUploadWizard";
import { SkinToneSlider } from "@/components/onboarding/SkinToneSlider";
import { useOnboardingDraft } from "@/lib/hooks/useOnboardingDraft";
import { fullQuizQuestions, QUIZ_QUESTIONS } from "@/lib/onboarding/questions";
import { ensureDefaultSkinToneAnswer, upsertQuizAnswer } from "@/lib/quizAnswerContract";

const ONBOARDING_DEBUG = process.env.NODE_ENV === 'development';

function debugOnboarding(...args: unknown[]) {
  if (ONBOARDING_DEBUG) {
    globalThis.console.log(...args);
  }
}

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
    examples: ["Michael B. Jordan", "Ryan Gosling", "Zendaya", "Emma Stone", "Idris Elba"],
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
    examples: ["Donald Glover", "Chris Paul", "Zendaya", "Mahershala Ali", "Lakeith Stanfield"],
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
    examples: ["Pharrell Williams", "Tyler, The Creator", "Zendaya", "Jaden Smith", "Timothée Chalamet"],
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
    examples: ["George Clooney", "David Beckham", "Meghan Markle", "Regé-Jean Page", "Dev Patel"],
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

function OnboardingContent() {
  const router = useRouter();
  const [flowMode, setFlowMode] = useState<string | null>(null);
  const [modeResolved, setModeResolved] = useState(false);
  const isGuestFlow = flowMode === 'guest' || flowMode === 'preauth';

  const [isLoading, setIsLoading] = useState(false);
  const [retake, setRetake] = useState(false);
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [uploadPhase, setUploadPhase] = useState(false);
  const [uploadComplete, setUploadComplete] = useState(false);
  
  // Debug: Track when quizCompleted changes
  useEffect(() => {
    debugOnboarding('🎯 [Quiz State] quizCompleted changed to:', quizCompleted);
    if (quizCompleted) {
      debugOnboarding('🎯 [Quiz State] Quiz completed! Stack trace:', new Error().stack);
    }
  }, [quizCompleted]);
  const [quizResults, setQuizResults] = useState<any>(null);
  
  // Debug: Track when quizResults changes
  useEffect(() => {
    debugOnboarding('🎯 [Quiz State] quizResults changed to:', !!quizResults);
    if (quizResults) {
      debugOnboarding('🎯 [Quiz State] Quiz results set! Stack trace:', new Error().stack);
    }
  }, [quizResults]);
  const [error, setError] = useState<string | null>(null);

  const autoAdvanceTimer = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelAutoAdvance = React.useCallback(() => {
    if (autoAdvanceTimer.current !== null) {
      clearTimeout(autoAdvanceTimer.current);
      autoAdvanceTimer.current = null;
    }
  }, []);
  useEffect(() => cancelAutoAdvance, [cancelAutoAdvance]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const submissionSaved = React.useRef(false);

  const { user, loading: authLoading } = useAuthContext();
  const flowIdentity = React.useRef<string | null>(null);
  flowIdentity.current = isGuestFlow ? 'guest' : user?.uid || null;
  const onboarding = useOnboardingDraft({ user, enabled: modeResolved && !authLoading, guest: isGuestFlow, allowProfileEdit: retake });
  useEffect(() => {
    cancelAutoAdvance();
    submissionSaved.current = false;
    setIsSubmitting(false);
    setIsLoading(false);
    setQuizCompleted(false);
    setQuizResults(null);
    setUploadPhase(false);
    setUploadComplete(false);
    setError(null);
  }, [user?.uid, isGuestFlow, cancelAutoAdvance]);
  const answers = onboarding.draft.answers;
  const userGender = answers.find(answer => answer.question_id === 'gender')?.selected_option || null;
  const setAnswers = React.useCallback((update: (previous: QuizAnswer[]) => QuizAnswer[]) => onboarding.updateDraft(previous => ({
    ...previous, answers: update(previous.answers),
  })), [onboarding.updateDraft]);



  // Use searchParams only on client side to avoid SSR issues
  const [mounted, setMounted] = useState(false);
  
  useEffect(() => {
    setMounted(true);
  }, []);
  
  // Redirect if not authenticated
  useEffect(() => {
    if (!mounted) return;
    
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const mode = params.get('mode') || params.get('flow');
      setFlowMode(mode);
      setRetake(params.get('retake') === '1');
      setModeResolved(true);
    }
  }, [mounted]);

  useEffect(() => {
    if (typeof window !== 'undefined' && !authLoading && !user && modeResolved && !isGuestFlow) {
      router.push('/');
    }
  }, [user, authLoading, isGuestFlow, modeResolved, router]);


  const getFilteredQuestions = (genderOverride?: string) => fullQuizQuestions(genderOverride || userGender, isGuestFlow);
  const questions = React.useMemo(() => fullQuizQuestions(userGender, isGuestFlow), [userGender, isGuestFlow]);
  const currentQuestionIndex = Math.max(0, questions.findIndex(question => question.id === onboarding.draft.currentQuestionId));
  const setCurrentQuestionIndex = (update: (previous: number) => number) => {
    onboarding.updateDraft(previous => {
      const activeQuestions = fullQuizQuestions(previous.answers.find(answer => answer.question_id === 'gender')?.selected_option || null, isGuestFlow);
      const index = Math.max(0, activeQuestions.findIndex(question => question.id === previous.currentQuestionId));
      return { ...previous, currentQuestionId: activeQuestions[update(index)]?.id || activeQuestions[0]?.id || null };
    });
  };

  // The slider's visible midpoint is a real answer. Commit it when the question
  // first becomes active so Next is enabled even when 50 is already correct.
  React.useEffect(() => {
    const activeQuestion = questions[currentQuestionIndex];
    if (!onboarding.ready || activeQuestion?.type !== 'rgb_slider') return;

    setAnswers(previousAnswers =>
      ensureDefaultSkinToneAnswer(previousAnswers, activeQuestion.id)
    );
  }, [currentQuestionIndex, questions, onboarding.ready, setAnswers]);

  // Debug: Log when userGender changes
  React.useEffect(() => {
    debugOnboarding('👤 [Gender Change] userGender changed to:', userGender);
  }, [userGender]);

  const nextStep = () => {
    cancelAutoAdvance();
    if (currentQuestionIndex < questions.length - 1) {
      // The timer and a click may originate from the same rendered question.
      // Only that question may advance; a stale callback cannot skip the next.
      setCurrentQuestionIndex(prev => prev === currentQuestionIndex ? prev + 1 : prev);
    }
  };

  const prevStep = () => {
    cancelAutoAdvance();
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev === currentQuestionIndex ? prev - 1 : prev);
    }
  };

  const canProceed = () => {
    if (questions.length === 0) return false;
    const currentQuestion = questions[currentQuestionIndex];
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

  const deriveQuizPreferences = () => {
    const stylePreferences: string[] = [];
    const colorPreferences: string[] = [];

    answers.forEach(answer => {
      const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
      if (question && question.type === 'visual_yesno' && answer.selected_option === 'Yes') {
        const styleName = question.style_name;
        if (styleName && !stylePreferences.includes(styleName)) {
          stylePreferences.push(styleName);
        }
        if (question.colors) {
          question.colors.forEach(color => {
            if (!colorPreferences.includes(color)) {
              colorPreferences.push(color);
            }
          });
        }
      }
    });

    return { stylePreferences, colorPreferences };
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
          debugOnboarding('🎨 [Style] Found style preference:', styleName, 'for question:', answer.question_id);
        }
      }
    });
    
    debugOnboarding('🎨 [Style] All style preferences:', stylePreferences);

    // Map style preferences to personas
    if (stylePreferences['Minimalist'] || stylePreferences['Clean Minimal']) {
      personaScores.architect += 3;
      personaScores.modernist += 2;
      debugOnboarding('🎨 [Persona] Added points for Minimalist style');
    }
    if (stylePreferences['Street Style'] || stylePreferences['Urban Street']) {
      personaScores.rebel += 3;
      personaScores.strategist += 2;
      debugOnboarding('🎨 [Persona] Added points for Street Style');
    }
    if (stylePreferences['Classic Elegant']) {
      personaScores.classic += 3;
      personaScores.connoisseur += 2;
      debugOnboarding('🎨 [Persona] Added points for Classic Elegant');
    }
    if (stylePreferences['Old Money']) {
      personaScores.connoisseur += 3;
      personaScores.classic += 2;
      debugOnboarding('🎨 [Persona] Added points for Old Money');
    }
    if (stylePreferences['Cottagecore'] || stylePreferences['Natural Boho']) {
      personaScores.wanderer += 3;
      debugOnboarding('🎨 [Persona] Added points for Cottagecore/Boho');
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
    const bodyType = userAnswers.body_type_female || userAnswers.body_type_male || userAnswers.body_type_nonbinary;
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
    debugOnboarding('🎯 [Persona] User answers:', userAnswers);
    debugOnboarding('🎯 [Persona] Style preferences:', stylePreferences);
    debugOnboarding('🎯 [Persona] Persona scores:', personaScores);
    debugOnboarding('🎯 [Persona] Sorted personas:', sortedPersonas);
    debugOnboarding('🎯 [Persona] Selected persona:', topPersona);
    
    // Count total "Yes" answers for style questions
    const styleYesAnswers = answers.filter(answer => {
      const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
      return question && question.type === 'visual_yesno' && answer.selected_option === 'Yes';
    }).length;
    debugOnboarding('🎯 [Persona] Total style "Yes" answers:', styleYesAnswers);

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

  // Hero images mapping for each persona
  const getHeroImageForPersona = (personaId: string): string => {
    debugOnboarding('🖼️ [Hero Image] Persona ID:', personaId, 'User Gender:', userGender);
    
    // Determine which gender variant to use
    let genderVariant = 'unisex'; // default fallback
    if (userGender === 'Male') {
      genderVariant = 'men';
    } else if (userGender === 'Female') {
      genderVariant = 'women';
    }
    
    const heroImages: Record<string, Record<string, string>> = {
      architect: {
        men: "/images/style-heroes/architect-men-hero..png",
        women: "/images/style-heroes/architect-women-hero.png",
        unisex: "/images/style-heroes/architect-unisex-hero.png"
      },
      strategist: {
        men: "/images/style-heroes/strategist-men-hero.png",
        women: "/images/style-heroes/strategist-women-hero.png",
        unisex: "/images/style-heroes/strategist-unisex-hero.png"
      },
      innovator: {
        men: "/images/style-heroes/innovator-men-hero.png",
        women: "/images/style-heroes/innovator-women-hero.png",
        unisex: "/images/style-heroes/innovator-unisex-hero.png"
      },
      classic: {
        men: "/images/style-heroes/classic-men-hero.png",
        women: "/images/style-heroes/classic-women-hero.png",
        unisex: "/images/style-heroes/classic-unisex-hero.png"
      },
      wanderer: {
        men: "/images/style-heroes/wanderer-men-hero.png",
        women: "/images/style-heroes/wanderer-women-hero.png",
        unisex: "/images/style-heroes/wanderer-unisex-hero.png"
      },
      rebel: {
        men: "/images/style-heroes/rebel-men-hero.png",
        women: "/images/style-heroes/rebel-women-hero.png",
        unisex: "/images/style-heroes/rebel-unisex-hero.png"
      },
      connoisseur: {
        men: "/images/style-heroes/connoisseur-men-hero.png",
        women: "/images/style-heroes/connoisseur-women-hero.png",
        unisex: "/images/style-heroes/connoisseur-unisex-hero.png"
      },
      modernist: {
        men: "/images/style-heroes/modernist-men-hero.png",
        women: "/images/style-heroes/modernist-women-hero.png",
        unisex: "/images/style-heroes/modernist-unisex-hero.png"
      }
    };
    
    const imageUrl = heroImages[personaId]?.[genderVariant] || "/images/placeholder.jpg";
    debugOnboarding('🖼️ [Hero Image] Selected image:', imageUrl, 'for gender variant:', genderVariant);
    return imageUrl;
  };

  const getGenderSpecificCelebrities = (personaId: string, userGender?: string): string[] => {
    // Define gender-specific celebrity examples for each persona
    const celebrityExamples: Record<string, Record<string, string[]>> = {
      architect: {
        men: ["Michael B. Jordan", "Ryan Gosling", "John Cho", "Oscar Isaac", "Idris Elba"],
        women: ["Zendaya", "Emma Stone", "Lupita Nyong'o", "Tessa Thompson", "Florence Pugh"],
        unisex: ["Michael B. Jordan", "Zendaya", "Ryan Gosling", "Emma Stone", "Idris Elba"]
      },
      strategist: {
        men: ["Donald Glover", "Chris Paul", "John Legend", "Mahershala Ali", "Lakeith Stanfield"],
        women: ["Zendaya", "Viola Davis", "Kerry Washington", "Danai Gurira", "Issa Rae"],
        unisex: ["Donald Glover", "Zendaya", "Chris Paul", "Viola Davis", "Mahershala Ali"]
      },
      innovator: {
        men: ["Pharrell Williams", "Tyler, The Creator", "A$AP Rocky", "Jaden Smith", "Timothée Chalamet"],
        women: ["Zendaya", "Rihanna", "Billie Eilish", "Doja Cat", "Lizzo"],
        unisex: ["Pharrell Williams", "Zendaya", "Tyler, The Creator", "Rihanna", "Jaden Smith"]
      },
      classic: {
        men: ["George Clooney", "David Beckham", "Henry Golding", "Regé-Jean Page", "Dev Patel"],
        women: ["Meghan Markle", "Blake Lively", "Cate Blanchett", "Lupita Nyong'o", "Emma Stone"],
        unisex: ["George Clooney", "Meghan Markle", "David Beckham", "Blake Lively", "Regé-Jean Page"]
      },
      wanderer: {
        men: ["Jason Momoa", "Chris Hemsworth", "Timothée Chalamet", "Harry Styles", "Dev Patel"],
        women: ["Zendaya", "Florence Pugh", "Emma Stone", "Lupita Nyong'o", "Tessa Thompson"],
        unisex: ["Jason Momoa", "Zendaya", "Chris Hemsworth", "Florence Pugh", "Timothée Chalamet"]
      },
      rebel: {
        men: ["Lil Nas X", "Bad Bunny", "Tyler, The Creator", "A$AP Rocky", "Harry Styles"],
        women: ["Rihanna", "Billie Eilish", "Doja Cat", "Lizzo", "Megan Thee Stallion"],
        unisex: ["Lil Nas X", "Rihanna", "Bad Bunny", "Billie Eilish", "Tyler, The Creator"]
      },
      connoisseur: {
        men: ["Ryan Reynolds", "Henry Cavill", "Michael B. Jordan", "Idris Elba", "John Legend"],
        women: ["Meghan Markle", "Blake Lively", "Cate Blanchett", "Lupita Nyong'o", "Viola Davis"],
        unisex: ["Ryan Reynolds", "Meghan Markle", "Henry Cavill", "Blake Lively", "Michael B. Jordan"]
      },
      modernist: {
        men: ["Timothée Chalamet", "Harry Styles", "Donald Glover", "Pharrell Williams", "Ryan Gosling"],
        women: ["Hailey Bieber", "Kendall Jenner", "Anya Taylor-Joy", "Zendaya", "Florence Pugh"],
        unisex: ["Timothée Chalamet", "Hailey Bieber", "Harry Styles", "Kendall Jenner", "Donald Glover"]
      }
    };

    // Determine which gender variant to use
    let genderVariant = 'unisex'; // default fallback
    if (userGender === 'Male') {
      genderVariant = 'men';
    } else if (userGender === 'Female') {
      genderVariant = 'women';
    }

    return celebrityExamples[personaId]?.[genderVariant] || celebrityExamples[personaId]?.unisex || [];
  };

  // Style examples mapping for each persona
  const getStyleExamplesForPersona = (personaId: string): Array<{url: string, caption: string}> => {
    debugOnboarding('🎨 [Style Examples] Persona ID:', personaId);
    const styleExamples: Record<string, Array<{url: string, caption: string}>> = {
      strategist: [
        { url: "/images/style-examples/strategist/business-meeting.jpg", caption: "Strategic Planning Session" },
        { url: "/images/style-examples/strategist/office-collaboration.jpg", caption: "Team Collaboration" },
        { url: "/images/style-examples/strategist/presentation.jpg", caption: "Client Presentation" }
      ],
      innovator: [
        { url: "/images/style-examples/innovator/art-studio.jpg", caption: "Creative Workshop" },
        { url: "/images/style-examples/innovator/design-session.jpg", caption: "Design Innovation" },
        { url: "/images/style-examples/innovator/experimental-art.jpg", caption: "Artistic Expression" }
      ],
      classic: [
        { url: "/images/style-examples/classic/luxury-meeting.jpg", caption: "Refined Business" },
        { url: "/images/style-examples/classic/cultural-discussion.jpg", caption: "Cultural Engagement" },
        { url: "/images/style-examples/classic/sophisticated-gathering.jpg", caption: "Elegant Social" }
      ],
      wanderer: [
        { url: "/images/style-examples/wanderer/nature-art.jpg", caption: "Natural Creativity" },
        { url: "/images/style-examples/wanderer/community-project.jpg", caption: "Community Art" },
        { url: "/images/style-examples/wanderer/bohemian-lifestyle.jpg", caption: "Free-Spirited Living" }
      ],
      rebel: [
        { url: "/images/style-examples/rebel/street-art.png", caption: "Urban Expression" },
        { url: "/images/style-examples/rebel/alternative-fashion.png", caption: "Bold Statements" },
        { url: "/images/style-examples/rebel/underground-scene.png", caption: "Creative Rebellion" }
      ],
      connoisseur: [
        { url: "/images/style-examples/connoisseur/wine-education.jpg", caption: "Wine Expertise" },
        { url: "/images/style-examples/connoisseur/culinary-arts.jpg", caption: "Culinary Mastery" },
        { url: "/images/style-examples/connoisseur/luxury-experience.jpg", caption: "Refined Tastes" }
      ],
      modernist: [
        { url: "/images/style-examples/modernist/clean-design.png", caption: "Minimalist Aesthetic" },
        { url: "/images/style-examples/modernist/tech-innovation.png", caption: "Tech Innovation" },
        { url: "/images/style-examples/modernist/contemporary-space.png", caption: "Modern Living" }
      ],
      architect: [
        { url: "/images/style-examples/architect/blueprint-review.jpg", caption: "Design Planning" },
        { url: "/images/style-examples/architect/3d-modeling.jpg", caption: "3D Visualization" },
        { url: "/images/style-examples/architect/construction-site.jpg", caption: "Project Management" }
      ]
    };
    
    debugOnboarding('🎨 [Style Examples] Available personas:', Object.keys(styleExamples));
    debugOnboarding('🎨 [Style Examples] Selected examples:', styleExamples[personaId]);
    
    return styleExamples[personaId] || [
      { url: "/images/style-examples/default/example-1.jpg", caption: "Style Example" },
      { url: "/images/style-examples/default/example-2.jpg", caption: "Style Example" },
      { url: "/images/style-examples/default/example-3.jpg", caption: "Style Example" }
    ];
  };

  const generateStyleFingerprint = () => {
    const userAnswers = answers.reduce((acc, answer) => {
      acc[answer.question_id] = answer.selected_option;
      return acc;
    }, {} as Record<string, string>);

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

    // Creative Expression: Restrained vs Expressive
    let creativeScore = 50; // Start neutral
    if (stylePreferences['Street Style'] || stylePreferences['Urban Street']) {
      creativeScore += 30; // More expressive
    }
    if (stylePreferences['Minimalist'] || stylePreferences['Clean Minimal']) {
      creativeScore -= 20; // More restrained
    }
    if (stylePreferences['Old Money'] || stylePreferences['Classic Elegant']) {
      creativeScore -= 15; // More restrained
    }
    if (stylePreferences['Cottagecore'] || stylePreferences['Natural Boho']) {
      creativeScore += 10; // Slightly more expressive
    }
    creativeScore = Math.max(10, Math.min(90, creativeScore)); // Keep between 10-90

    // Trend Awareness: Timeless vs Trendsetting
    let trendScore = 50; // Start neutral
    if (stylePreferences['Street Style'] || stylePreferences['Urban Street']) {
      trendScore += 25; // More trendsetting
    }
    if (stylePreferences['Classic Elegant'] || stylePreferences['Old Money']) {
      trendScore -= 25; // More timeless
    }
    if (stylePreferences['Minimalist'] || stylePreferences['Clean Minimal']) {
      trendScore -= 10; // More timeless
    }
    if (userAnswers.daily_activities === 'Creative work and casual meetings') {
      trendScore += 10;
    }
    if (userAnswers.daily_activities === 'Office work and meetings') {
      trendScore -= 10;
    }
    trendScore = Math.max(10, Math.min(90, trendScore)); // Keep between 10-90

    // Wardrobe Flexibility: Focused vs Versatile
    let flexibilityScore = 50; // Start neutral
    if (userAnswers.daily_activities === 'Mix of everything') {
      flexibilityScore += 30; // More versatile
    }
    if (stylePreferences['Minimalist'] || stylePreferences['Clean Minimal']) {
      flexibilityScore += 15; // Minimalist pieces are versatile
    }
    if (stylePreferences['Classic Elegant']) {
      flexibilityScore += 10; // Classics are versatile
    }
    if (stylePreferences['Street Style'] || stylePreferences['Urban Street']) {
      flexibilityScore += 5; // Street style can be versatile
    }
    if (userAnswers.daily_activities === 'Office work and meetings') {
      flexibilityScore -= 15; // More focused
    }
    if (userAnswers.style_elements === 'Clean lines and minimal details') {
      flexibilityScore += 10; // Clean lines are versatile
    }
    if (userAnswers.style_elements === 'Bold and statement pieces') {
      flexibilityScore -= 10; // Statement pieces are more focused
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
    const submittingIdentity = flowIdentity.current;
    const startTime = Date.now();
    debugOnboarding('🚀 [submitQuiz] Function called at:', new Date().toISOString());
    debugOnboarding('🚀 [submitQuiz] User:', !!user);
    debugOnboarding('🚀 [submitQuiz] Answers:', answers.length);
    
    debugOnboarding('⏱️ [submitQuiz] Starting color analysis...');
    const colorAnalysis = analyzeColors();
    debugOnboarding('⏱️ [submitQuiz] Color analysis took:', Date.now() - startTime, 'ms');
    
    debugOnboarding('⏱️ [submitQuiz] Starting preference derivation...');
    const { stylePreferences, colorPreferences } = deriveQuizPreferences();
    debugOnboarding('⏱️ [submitQuiz] Preference derivation took:', Date.now() - startTime, 'ms');
    
    // Guest mode remains local even when the browser already has an account session.
    if (isGuestFlow) {
      try {
        sessionStorage.setItem('pendingQuizSubmission', JSON.stringify({
          answers, colorAnalysis, stylePreferences, colorPreferences,
          persona: determineStylePersona(), createdAt: Date.now(),
        }));
        router.replace('/finish-profile?from=quiz');
      } catch {
        setError('Your browser could not save your answers. Keep this tab open and try again.');
      }
      return;
    }
    if (!user) {
      setError('Please sign in to complete the quiz');
      return;
    }
    if (!submissionSaved.current && !await onboarding.flush()) {
      if (submittingIdentity === flowIdentity.current) setError('Your latest answers have not saved yet. Retry saving before completing the quiz.');
      return;
    }

    if (submittingIdentity !== flowIdentity.current) return;
    debugOnboarding('🚀 [submitQuiz] Starting submission...');
    setIsLoading(true);
    setError(null);

    try {
      let data: Record<string, unknown> = {};
      if (!submissionSaved.current) {
        debugOnboarding('⏱️ [submitQuiz] Getting ID token...');
        const tokenStart = Date.now();
        const token = await user.getIdToken();
        if (submittingIdentity !== flowIdentity.current) return;
        debugOnboarding('⏱️ [submitQuiz] Got ID token in:', Date.now() - tokenStart, 'ms');
      
        // Extract spending ranges from answers (8 categories)
        const spending_ranges = {
          tops: answers.find(a => a.question_id === "category_spend_tops")?.selected_option || "unknown",
          pants: answers.find(a => a.question_id === "category_spend_pants")?.selected_option || "unknown",
          shoes: answers.find(a => a.question_id === "category_spend_shoes")?.selected_option || "unknown",
          jackets: answers.find(a => a.question_id === "category_spend_jackets")?.selected_option || "unknown",
          dresses: answers.find(a => a.question_id === "category_spend_dresses")?.selected_option || "unknown",
          accessories: answers.find(a => a.question_id === "category_spend_accessories")?.selected_option || "unknown",
          undergarments: answers.find(a => a.question_id === "category_spend_undergarments")?.selected_option || "unknown",
          swimwear: answers.find(a => a.question_id === "category_spend_swimwear")?.selected_option || "unknown"
        };

        // Spending ranges are sent via /api/style-quiz/submit (server-side), to avoid adding
        // extra concurrent backend calls during onboarding.
      
        const submissionData = {
            userId: user.uid,
            token: token,
            answers: answers,
            colorAnalysis: colorAnalysis,
            stylePreferences: stylePreferences,
            colorPreferences: colorPreferences,
            spending_ranges: spending_ranges,
            ...(retake ? { retake: true } : {})
        };

        debugOnboarding('🔍 [Quiz Frontend] Submitting quiz data:', {
          userId: user.uid,
          answersCount: answers.length,
          stylePreferences: stylePreferences,
          colorPreferences: colorPreferences,
          hasColorAnalysis: !!colorAnalysis
        });

        debugOnboarding('🌐 [Quiz Frontend] Making API call to /api/style-quiz/submit at:', Date.now() - startTime, 'ms');
        const apiStart = Date.now();
        const response = await fetch('/api/style-quiz/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(submissionData)
        });
      
        debugOnboarding('🌐 [Quiz Frontend] API response received in:', Date.now() - apiStart, 'ms');
        debugOnboarding('🌐 [Quiz Frontend] API response status:', response.status);
        debugOnboarding('⏱️ [submitQuiz] Total time so far:', Date.now() - startTime, 'ms');

        data = await response.json();
        if (submittingIdentity !== flowIdentity.current) return;
        if (!response.ok || data.success !== true) throw new Error(typeof data.error === 'string' ? data.error : 'Failed to save your style profile. Please try again.');
        submissionSaved.current = true;
      }
      // Read the shared resolver after persistence; cached profile item counts are not authoritative.
      const savedState = await onboarding.refresh();
      if (submittingIdentity !== flowIdentity.current) return;
      if (!savedState?.profileComplete) throw new Error('Your style profile saved, but we could not load your next step. Retry to continue.');
      setQuizCompleted(true);
      setQuizResults({ ...data, colorAnalysis });
      if (savedState.capsule.ready || savedState.stage === 'complete') {
        router.push('/style-persona?from=quiz');
      } else {
        setUploadPhase(true);
      }
    } catch (cause) {
      if (submittingIdentity === flowIdentity.current) setError(cause instanceof Error ? cause.message : 'Failed to save your style profile. Please try again.');
      // Keep the actual answers on screen. A failed request is never quiz completion.
    } finally {
      if (submittingIdentity === flowIdentity.current) setIsLoading(false);
    }
  };

  const saveAnswerWithoutAdvance = (questionId: string, answer: string) => {
    setAnswers(previousAnswers => upsertQuizAnswer(previousAnswers, questionId, answer));
  };

  const renderQuestion = () => {
    if (questions.length === 0) {
      console.error('No questions available for quiz');
      return (
        <div className="text-center p-8">
          <p className="text-red-600 dark:text-red-400">No questions available. Please refresh the page.</p>
        </div>
      );
    }
    
    const question = questions[currentQuestionIndex];
    if (!question) {
      console.error('No question found for current question index:', currentQuestionIndex);
      return (
        <div className="text-center p-8">
          <p className="text-red-600 dark:text-red-400">Question not found. Please refresh the page.</p>
        </div>
      );
    }
    
    const currentAnswer = answers.find(a => a.question_id === question.id);
    const skinToneValue = Number.parseInt(
      currentAnswer?.selected_option?.replace('skin_tone_', '') || '50',
      10
    );

    return (
      <div className="animate-in fade-in-0 slide-in-from-right-4 duration-500">
        {/* Hide question text for visual_yesno questions */}
        {question.type !== "visual_yesno" && (
          <div className="text-center mb-12">
            <h2 className="heading-lg text-card-foreground mb-8">
              {question.question}
            </h2>
            {question.type === "visual" && (
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
                Select the option that best represents your style
              </p>
            )}
            {question.type === "rgb_slider" && (
              <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
                Drag the slider to select your skin tone
              </p>
            )}
          </div>
        )}
        
        {question.type === "visual" && question.images ? (
          <div className="space-y-2 sm:space-y-4">
            {(question.id === "body_type_female" || question.id === "body_type_male" || question.id === "body_type_nonbinary") && (
              <BodyPositiveMessage variant="profile" className="mb-2 sm:mb-4" />
            )}
            <div className={`max-w-2xl mx-auto ${
              question.options.length >= 6 
                ? 'grid grid-cols-2 gap-2 sm:gap-3' 
                : 'space-y-2 sm:space-y-3'
            }`}>
              {question.options.map((option) => (
                <button
                  key={option}
                  className={`w-full py-2.5 sm:py-3 px-3 sm:px-4 rounded-xl text-sm sm:text-base font-medium transition-all duration-300 ${
                    currentAnswer?.selected_option === option
                      ? "bg-gray-900 text-white dark:bg-white dark:text-gray-900 shadow-lg"
                      : "bg-white text-gray-900 border border-gray-300 hover:border-gray-400 dark:bg-gray-800 dark:text-white dark:border-gray-600 dark:hover:border-gray-500"
                  }`}
                  onClick={() => {
                    handleAnswer(question.id, option);
                  }}
                >
                  <div className="text-center">
                    <div className="font-semibold truncate">{option}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : question.type === "visual_yesno" && question.images ? (
          <div className="max-w-lg mx-auto">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border-2 border-gray-200 dark:border-gray-700">
              <div className="relative mb-3 flex items-center justify-center" style={{ height: 'clamp(200px, 35vh, 400px)' }}>
                <img
                  src={question.images[0]}
                  alt={question.style_name}
                  className="max-w-full max-h-full object-contain rounded-lg"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.src = "/placeholder.png";
                  }}
                />
              </div>
              <div className="text-center mb-3">
                <h3 className="text-base sm:text-lg font-semibold text-card-foreground mb-1">
                  {question.style_name}
                </h3>
                <p className="text-xs text-gray-600 dark:text-gray-400">
                  {question.colors?.join(", ").replace(/\b\w/g, l => l.toUpperCase())}
                </p>
              </div>
              <div className="flex gap-3 justify-center">
                <Button
                  variant={currentAnswer?.selected_option === "Yes" ? "default" : "outline"}
                  className="flex-1 h-11 text-base font-medium"
                  onClick={() => {
                    handleAnswer(question.id, "Yes");
                  }}
                >
                  👍 Yes
                </Button>
                <Button
                  variant={currentAnswer?.selected_option === "No" ? "default" : "outline"}
                  className="flex-1 h-11 text-base font-medium"
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
          <SkinToneSlider
            value={skinToneValue}
            onValueChange={(value) =>
              saveAnswerWithoutAdvance(question.id, `skin_tone_${value}`)
            }
          />
        ) : (
        <div className={`max-w-2xl mx-auto ${
          question.options.length >= 6 
            ? 'grid grid-cols-2 gap-2 sm:gap-3' 
            : 'space-y-2 sm:space-y-3'
        }`}>
          {question.options.map((option) => (
            <button
              key={option}
              className={`w-full py-2.5 sm:py-3 px-3 sm:px-4 rounded-xl text-sm sm:text-base font-medium transition-all duration-300 ${
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
        )}
      </div>
    );
  };

  // Show loading state while authenticating
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-body text-muted-foreground">Authenticating...</p>
        </div>
      </div>
    );
  }

  // Redirect if not authenticated
  if (!modeResolved) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-body text-muted-foreground">Loading your experience...</p>
        </div>
      </div>
    );
  }

  if (!user && !isGuestFlow) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center space-y-4">
          <p className="text-lg text-muted-foreground">Redirecting you back home...</p>
        </div>
      </div>
    );
  }


  if (!onboarding.ready) {
    return <div className="min-h-screen flex items-center justify-center p-4"><div className="text-center space-y-4">
      <p role={onboarding.error ? 'alert' : 'status'}>{onboarding.error || 'Loading your saved progress...'}</p>
      {onboarding.error && <Button onClick={() => void onboarding.retry()}>Retry loading progress</Button>}
    </div></div>;
  }

  if (onboarding.state?.profileComplete && !retake && !uploadPhase) {
    return <div className="min-h-screen flex items-center justify-center p-4"><div className="max-w-md space-y-4">
      <h1 className="text-2xl font-serif">Your style profile is saved</h1>
      <p>{onboarding.state.capsule.usableCount} of 10 capsule pieces saved.</p>
      <Button onClick={() => {
        if (onboarding.state?.stage === 'complete') router.push('/outfits');
        else if (onboarding.state?.capsule.ready) router.push('/style-persona');
        else setUploadPhase(true);
      }}>Continue your journey</Button>
      <Button variant="outline" onClick={() => { setRetake(true); router.replace('/onboarding?retake=1'); }}>Retake my style quiz</Button>
    </div></div>;
  }

  // Show upload phase after quiz completion
  if (uploadPhase && !uploadComplete) {
    return (
      <GuidedUploadWizard
        userId={user?.uid || ''}
        targetCount={10}
        stylePersona={quizResults?.stylePersona || 'default'}
        gender={userGender || 'Male'}
        onComplete={(itemCount) => {
          debugOnboarding(`✅ Upload complete with ${itemCount} items`);
          void onboarding.refresh();
          setUploadComplete(true);
          // Redirect to persona page after upload
          setTimeout(() => {
            router.replace('/style-persona?from=quiz');
          }, 2000);
        }}
      />
    );
  }

  // Show loading state while redirecting after upload completion
  if (uploadComplete) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-white mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Redirecting to your style persona...</p>
        </div>
      </div>
    );
  }

  // This should never be reached since we redirect immediately after quiz completion
  if (false) {
    // Retained only as a reference for the retired inline-results design. Keep
    // its data bindings explicit so the dead branch cannot pollute type checks.
    const persona = quizResults?.persona as any;
    const styleFingerprint = quizResults?.styleFingerprint as any;
    const currentGender = userGender;
    return (
      <div className="min-h-screen bg-gradient-to-br from-stone-50 via-amber-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
        <div className="max-w-6xl mx-auto px-4 py-12">
          {/* Hero Section */}
          <div className="bg-white dark:bg-gray-800 rounded-3xl overflow-hidden shadow-xl mb-8">
            {/* Hero Image */}
            <div className="relative aspect-[4/3] overflow-hidden">
              <img 
                src={getHeroImageForPersona(persona.id)}
                alt={`${persona.name} style example`}
                className="w-full h-full object-contain"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-black/40 via-transparent to-black/60"></div>
              
              {/* Hero Content - Left Side */}
              <div className="absolute inset-0 flex items-center">
                <div className="max-w-2xl p-8 text-white">
                  <div className="text-sm font-medium text-gray-300 mb-3 tracking-wider">YOU ARE</div>
                  <h1 className="heading-xl mb-6 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
                  {persona.name}
                </h1>
                  <p className="text-2xl text-gray-100 mb-8 leading-relaxed font-light">
                    {persona.tagline}
                  </p>
                  
                  {/* Style Traits - Inline with hero */}
                  <div className="flex flex-wrap gap-3">
                  {persona.traits.map((trait, index) => (
                      <span 
                        key={index}
                        className="px-4 py-2 bg-white/20 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/30"
                      >
                      {trait}
                    </span>
                  ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Content Section */}
            <div className="p-8">
              {/* Description */}
              <div className="text-center max-w-4xl mx-auto">
                <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-8">
                  {persona.description}
                </p>
                
                {/* Style Mission */}
                <div className="bg-gray-50 dark:bg-gray-700 rounded-2xl p-8">
                  <h3 className="text-2xl font-serif font-semibold text-gray-900 dark:text-white mb-4">Your Style Mission</h3>
                  <p className="text-lg text-gray-600 dark:text-gray-400 italic leading-relaxed">
                {persona.styleMission}
              </p>
            </div>
                  </div>
              </div>
            </div>


            {/* Style Fingerprint Section */}
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl mb-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-4">Your Style Fingerprint</h2>
                <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                  A detailed breakdown of your unique style characteristics
                </p>
              </div>
              
              <div className="space-y-8">
                      {/* Creative Expression */}
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Creative Expression</h3>
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <span>Restrained</span>
                          <span>Expressive</span>
                        </div>
                  <div className="relative">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-1000"
                        style={{ width: `${styleFingerprint.creativeExpression.expressive}%` }}
                      ></div>
                        </div>
                    <div className="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mt-2">
                      <span>{styleFingerprint.creativeExpression.restrained}%</span>
                      <span>{styleFingerprint.creativeExpression.expressive}%</span>
                    </div>
                        </div>
                      </div>

                      {/* Trend Awareness */}
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Trend Awareness</h3>
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <span>Timeless</span>
                          <span>Trendsetting</span>
                        </div>
                  <div className="relative">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-green-500 to-pink-500 h-3 rounded-full transition-all duration-1000"
                        style={{ width: `${styleFingerprint.trendAwareness.trendsetting}%` }}
                      ></div>
                        </div>
                    <div className="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mt-2">
                      <span>{styleFingerprint.trendAwareness.timeless}%</span>
                      <span>{styleFingerprint.trendAwareness.trendsetting}%</span>
                    </div>
                        </div>
                      </div>

                      {/* Wardrobe Flexibility */}
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white">Wardrobe Flexibility</h3>
                  <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                          <span>Focused</span>
                          <span>Versatile</span>
                        </div>
                  <div className="relative">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                      <div 
                        className="bg-gradient-to-r from-orange-500 to-teal-500 h-3 rounded-full transition-all duration-1000"
                        style={{ width: `${styleFingerprint.wardrobeFlexibility.versatile}%` }}
                      ></div>
                        </div>
                    <div className="flex justify-between text-sm font-medium text-gray-700 dark:text-gray-300 mt-2">
                      <span>{styleFingerprint.wardrobeFlexibility.focused}%</span>
                      <span>{styleFingerprint.wardrobeFlexibility.versatile}%</span>
                        </div>
                      </div>
                </div>
              </div>
            </div>

            {/* Style Mission Section */}
            <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl p-8 text-white shadow-xl mb-8">
              <div className="text-center">
                <h2 className="text-3xl font-serif font-bold mb-4">Your Style Mission</h2>
                <p className="text-xl text-purple-100 max-w-4xl mx-auto leading-relaxed">
                  {persona.styleMission}
                </p>
              </div>
            </div>

            {/* The Rebels You May Know Section */}
            <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl mb-8">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-4">
                  The {persona.name.split(' ')[1]}s You May Know
                </h2>
                <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
                  Celebrities and icons who embody the {persona.name.toLowerCase()} style
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {getGenderSpecificCelebrities(persona.id, currentGender)?.map((celebrity, index) => (
                  <div key={index} className="text-center p-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-2xl hover:shadow-lg transition-shadow">
                    <div className="text-4xl mb-3">♪</div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {celebrity}
                    </h3>
                  </div>
                )) || (
                  // Fallback for personas without celebrities defined
                  <div className="text-center p-6 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800 rounded-2xl">
                    <div className="text-4xl mb-3">♪</div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      Style Icons
                    </h3>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      Discover your style inspirations
                    </p>
                  </div>
                )}
              </div>
            </div>

          {/* Call-to-Action Section */}
            <div className="bg-gradient-to-r from-red-600 to-red-700 rounded-3xl p-12 text-center text-white shadow-xl">
              <h2 className="text-4xl font-serif font-bold mb-4">We've Got You Covered</h2>
              <p className="text-xl text-red-100 mb-8 max-w-2xl mx-auto leading-relaxed">
                Your {persona.name.toLowerCase()} style is ready to shine. Let's build the perfect wardrobe that matches your bold personality.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
                <button 
                  onClick={() => router.push('/outfits')}
                  className="bg-white text-red-600 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transition-colors shadow-lg"
                >
                  See My Style Plan →
                </button>
                <div className="flex items-center space-x-2 text-red-100">
                  <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                    <span className="text-sm font-bold">4</span>
            </div>
                  <span className="text-sm">Steps to perfect style</span>
          </div>
              </div>
              
              {/* Navigation Links */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button 
                  onClick={() => router.push('/')}
                  className="bg-white/20 text-white px-6 py-3 rounded-full font-medium hover:bg-white/30 transition-colors border border-white/30"
                >
                  🏠 Dashboard
                </button>
                <button 
                  onClick={() => router.push('/profile')}
                  className="bg-white/20 text-white px-6 py-3 rounded-full font-medium hover:bg-white/30 transition-colors border border-white/30"
                >
                  👤 My Profile
                </button>
                <button 
                  onClick={() => router.push('/style-persona')}
                  className="bg-white/20 text-white px-6 py-3 rounded-full font-medium hover:bg-white/30 transition-colors border border-white/30"
                >
                  ✨ Style Persona
                </button>
              </div>
            </div>

        </div>
      </div>
    );
  }

  // Quiz functions
  const handleAnswer = (questionId: string, answer: string) => {
    debugOnboarding('📝 [Answer] Saving answer:', { questionId, answer });
    
    // Set user gender when gender question is answered
    if (questionId === 'gender') {
      debugOnboarding('👤 [Gender] About to set user gender from:', userGender, 'to:', answer);
      debugOnboarding('👤 [Gender] Set user gender:', answer);
      
      // Debug: Show what questions will be available after gender selection
      const newFiltered = getFilteredQuestions(answer);
      debugOnboarding('🔄 [Gender] After gender selection, available questions:', {
        totalQuestions: newFiltered.length,
        visualYesNoQuestions: newFiltered.filter(q => q.type === 'visual_yesno').map(q => q.id),
        femaleStyleQuestions: newFiltered.filter(q => q.id.startsWith('style_item_f_')).map(q => q.id),
        maleStyleQuestions: newFiltered.filter(q => q.id.startsWith('style_item_m_')).map(q => q.id)
      });
      
    }
    
    setAnswers(prev => {
      const existing = prev.find(a => a.question_id === questionId);
      if (existing) {
        return prev.map(a => a.question_id === questionId ? { ...a, selected_option: answer } : a);
      } else {
        return [...prev, { question_id: questionId, selected_option: answer }];
      }
    });
    
    // Debug: Log current state after answering
    debugOnboarding('🔍 [Quiz State] After answering:', {
      currentQuestionIndex,
      totalQuestions: questions.length,
      isLastQuestion: currentQuestionIndex === questions.length - 1,
      answersCount: answers.length + 1
    });

    // Only the latest choice owns an auto-advance. Manual navigation and
    // unmounting cancel this timer, preserving the visual feedback delay.
    cancelAutoAdvance();
    if (currentQuestionIndex < questions.length - 1) {
      autoAdvanceTimer.current = setTimeout(nextStep, 300);
    }
  };

  const handleNext = () => {
    debugOnboarding('🔄 [Navigation] Next clicked:', {
      currentQuestionIndex,
      totalQuestions: questions.length,
      canGoNext: currentQuestionIndex < questions.length - 1,
      isLastQuestion: currentQuestionIndex === questions.length - 1
    });
    
    cancelAutoAdvance();
    if (currentQuestionIndex < questions.length - 1) {
      nextStep();
    } else {
      // If this is the last question, submit the quiz
      debugOnboarding('🎯 [Quiz] Last question reached, submitting quiz...');
      debugOnboarding('🎯 [Quiz] submitQuiz function available:', typeof submitQuiz);
      debugOnboarding('🎯 [Quiz] User available:', !!user);
      debugOnboarding('🎯 [Quiz] Answers count:', answers.length);
      submitQuiz();
    }
  };

  const handlePrevious = prevStep;

  const handleSubmit = async () => {
    cancelAutoAdvance();
    debugOnboarding('🚀 [handleSubmit] Called - redirecting to submitQuiz');
    setIsSubmitting(true);
    try {
      await submitQuiz();
    } catch (error) {
      console.error('Error submitting quiz:', error);
      setError('Failed to submit quiz. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Get current question
  const question = questions[currentQuestionIndex];
  
  // Debug: Log current question details
  debugOnboarding('🎯 [Current Question]', {
    currentQuestionIndex,
    totalQuestions: questions.length,
    questionId: question?.id,
    questionType: question?.type,
    isVisualYesNo: question?.type === 'visual_yesno',
    styleName: question?.style_name
  });
  
  // Debug: Show visual breakdown of all questions
  debugOnboarding('📋 [Quiz Overview]', {
    allQuestions: questions.map((q, index) => ({
      index,
      id: q.id,
      type: q.type,
      isVisualYesNo: q.type === 'visual_yesno',
      gender: q.gender
    })),
    visualYesNoCount: questions.filter(q => q.type === 'visual_yesno').length,
    currentlyAt: `${currentQuestionIndex + 1}/${questions.length}`
  });

  const hasAnsweredCurrent = !!answers.find(a => a.question_id === question?.id);
  const isLastQuestion = currentQuestionIndex === questions.length - 1;
  const questionContent = renderQuestion();

  // Show quiz questions
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex flex-col p-4">
      <div className="w-full max-w-4xl mx-auto flex-1 flex flex-col">
        <div className="text-center mb-6 flex-shrink-0">
          <h1 className="text-3xl md:text-4xl font-serif text-gray-900 dark:text-white mb-4 leading-tight">
            Let's Discover Your Style
          </h1>
        </div>

        <div className="glass-float p-4 flex-1 flex flex-col min-h-0 glass-shadow overflow-hidden">
          <div className="flex-1 overflow-y-auto pr-1 space-y-6">
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                {question?.id === 'gender'
                  ? 'Getting started'
                  : `Question ${currentQuestionIndex + 1} of ${questions.length}`}
              </span>
              <div className="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-amber-500 to-orange-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: question?.id === 'gender' ? '0%' : `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-500 dark:text-gray-400 whitespace-nowrap">
                {question?.id === 'gender'
                  ? 'Start'
                  : `${Math.round(((currentQuestionIndex + 1) / questions.length) * 100)}%`}
              </span>
            </div>

            <div aria-live="polite" className="text-sm text-muted-foreground">
              <p role="status">{onboarding.status === 'saving' ? 'Saving your progress...' : onboarding.status === 'saved' ? (isGuestFlow ? 'Saved in this browser' : 'Progress saved') : 'Progress needs attention'}</p>
              {onboarding.error && <p role="alert">{onboarding.error}</p>}
              {onboarding.status === 'error' && <Button variant="outline" onClick={() => void onboarding.retry()}>Retry saving</Button>}
              {onboarding.conflict && <Button variant="outline" onClick={() => { cancelAutoAdvance(); onboarding.reloadLatest(); }}>Load newer draft</Button>}
            </div>
            {error && <p role="alert" className="text-red-700 dark:text-red-300">{error}</p>}
            {questionContent}
          </div>

          <div className="sticky bottom-0 -mx-4 mt-4 pt-4 bg-gradient-to-t from-amber-50 to-transparent dark:from-amber-950 dark:to-transparent backdrop-blur-sm">
            <div className="px-4 pb-3 sm:pb-0 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
              <button
                onClick={handlePrevious}
                disabled={currentQuestionIndex === 0}
                className="flex w-full sm:w-auto items-center justify-center px-4 py-3 rounded-2xl text-button font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-secondary dark:bg-muted text-card-foreground hover:bg-secondary/80"
              >
                <ArrowLeft className="h-4 w-4 mr-2 inline-block" />
                Previous
              </button>

              {isLastQuestion ? (
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting || isLoading || !!onboarding.conflict}
                  className="flex w-full sm:w-auto items-center justify-center px-6 py-3 rounded-2xl font-semibold text-button gradient-primary text-white shadow-lg shadow-[#FFB84C]/20 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
                >
                  {isSubmitting ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Discover My Style
                      <ArrowRight className="h-4 w-4 ml-2 inline-block" />
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={handleNext}
                  disabled={!hasAnsweredCurrent}
                  className="flex w-full sm:w-auto items-center justify-center px-6 py-3 rounded-2xl font-semibold text-button gradient-primary text-white shadow-lg shadow-[#FFB84C]/20 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90"
                >
                  Next
                  <ArrowRight className="h-4 w-4 ml-2 inline-block" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Onboarding() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex items-center justify-center">
        <div className="animate-pulse text-center">
          <Sparkles className="h-12 w-12 mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading onboarding...</p>
        </div>
      </div>
    }>
      <OnboardingContent />
    </Suspense>
  );
}
