'use client';

import { useState, useEffect } from 'react';
import { useFirebase } from '@/lib/firebase-context';
import { useRouter } from 'next/navigation';
import Navigation from '@/components/Navigation';
import { ArrowRight, Sparkles } from 'lucide-react';

export const dynamic = 'force-dynamic';

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

interface UserProfile {
  id?: string;
  userId?: string;
  name: string;
  email: string;
  gender?: string;
  stylePreferences?: string[];
  preferences?: {
    style: string[];
    colors: string[];
    occasions: string[];
  };
  measurements?: {
    height?: number;
    weight?: number;
    bodyType?: string;
    skinTone?: string;
    heightFeetInches?: string;
    topSize?: string;
    bottomSize?: string;
    shoeSize?: string;
    dressSize?: string;
    jeanWaist?: string;
    braSize?: string;
    inseam?: string;
    waist?: string;
    chest?: string;
    shoulderWidth?: number;
    waistWidth?: number;
    hipWidth?: number;
    armLength?: number;
  };
  stylePersonality?: Record<string, number>;
  colorPalette?: {
    primary: string[];
    secondary: string[];
    accent: string[];
    neutral: string[];
    avoid: string[];
  };
  stylePersona?: {
    id: string;
    name: string;
    tagline: string;
    description: string;
    styleMission: string;
    traits: string[];
    examples: string[];
  };
  onboardingCompleted?: boolean;
}

const STYLE_PERSONAS: Record<string, StylePersona> = {
  architect: {
    id: "architect",
    name: "The Architect",
    tagline: "Clean lines. Bold vision. Timeless design.",
    description: "You approach fashion like an architect approaches buildings - with precision, intention, and a focus on form following function. Your style is structured, sophisticated, and built to last. You appreciate quality construction and aren't afraid to make a statement with clean, geometric lines.",
    styleMission: "Build your wardrobe like you'd design a building - with a strong foundation, thoughtful details, and pieces that stand the test of time.",
    examples: ["Zaha Hadid", "Tadao Ando", "Frank Gehry", "Norman Foster", "Rem Koolhaas"],
    traits: [
      "Clean lines",
      "Bold vision",
      "Timeless design",
      "Quality construction",
      "Geometric precision"
    ],
    cta: "See My Plan Options →"
  },
  rebel: {
    id: "rebel",
    name: "The Rebel",
    tagline: "Bold statements. Unconventional choices. Authentic expression.",
    description: "You don't follow trends - you create them. Your style is bold, unconventional, and authentically you. You're not afraid to mix unexpected pieces, experiment with color, or wear something that makes people look twice. Your fashion choices are a form of self-expression and rebellion against the ordinary.",
    styleMission: "Break the rules, set your own trends, and wear what makes you feel most like yourself. Don't be afraid to stand out.",
    examples: ["David Bowie", "Grace Jones", "Prince", "Frida Kahlo", "Alexander McQueen"],
    traits: [
      "Bold statements",
      "Unconventional choices",
      "Authentic expression",
      "Rule breaking",
      "Trend setting"
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

const getHeroImageForPersona = (personaId: string, userGender?: string): string => {
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
  
  return heroImages[personaId]?.[genderVariant] || "/images/placeholder.jpg";
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
  const normalizedGender = userGender?.toLowerCase();
  if (normalizedGender === 'male') {
    genderVariant = 'men';
  } else if (normalizedGender === 'female') {
    genderVariant = 'women';
  }

  console.log('🎭 [Gender Celebrities] User gender:', userGender, 'Normalized:', normalizedGender, 'Selected variant:', genderVariant, 'Persona:', personaId);
  
  const result = celebrityExamples[personaId]?.[genderVariant] || celebrityExamples[personaId]?.unisex || [];
  console.log('🎭 [Gender Celebrities] Result:', result);
  
  return result;
};

const getStyleExamplesForPersona = (personaId: string) => {
  const examples: Record<string, Array<{url: string, caption: string}>> = {
    architect: [
      { url: '/images/outfit-quiz/architect-1.jpg', caption: 'Urban Expression' },
      { url: '/images/outfit-quiz/architect-2.jpg', caption: 'Bold Statements' },
      { url: '/images/outfit-quiz/architect-3.jpg', caption: 'Timeless Design' }
    ],
    rebel: [
      { url: '/images/outfit-quiz/F-ST4.png', caption: 'Urban Expression' },
      { url: '/images/outfit-quiz/F-ST5.png', caption: 'Bold Statements' },
      { url: '/images/outfit-quiz/F-ST6.png', caption: 'Creative Edge' }
    ],
    connoisseur: [
      { url: '/images/outfit-quiz/connoisseur-1.jpg', caption: 'Refined Elegance' },
      { url: '/images/outfit-quiz/connoisseur-2.jpg', caption: 'Luxury Details' },
      { url: '/images/outfit-quiz/connoisseur-3.jpg', caption: 'Quiet Confidence' }
    ],
    modernist: [
      { url: '/images/outfit-quiz/modernist-1.jpg', caption: 'Clean Lines' },
      { url: '/images/outfit-quiz/modernist-2.jpg', caption: 'Contemporary Edge' },
      { url: '/images/outfit-quiz/modernist-3.jpg', caption: 'Future Focused' }
    ]
  };
  return examples[personaId] || examples.rebel;
};

export default function StylePersonaPage() {
  const { user, loading: authLoading } = useFirebase();
  const router = useRouter();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cameFromQuiz, setCameFromQuiz] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    setCameFromQuiz(params.get('from') === 'quiz');
  }, []);

  useEffect(() => {
    if (user && !authLoading) {
      fetchProfile();
    } else if (!user && !authLoading) {
      router.push('/');
    }
  }, [user, authLoading, router]);

  // Force refresh when page loads (e.g., coming from quiz)
  useEffect(() => {
    if (user && !authLoading) {
      // Add a small delay to ensure backend has processed the quiz
      const timer = setTimeout(() => {
        console.log('🔄 [Persona Page] Force refreshing profile data...');
        fetchProfile();
      }, 1000); // Increased delay to 1 second
      return () => clearTimeout(timer);
    }
  }, []); // Run once on mount

  // Refresh profile data when page becomes visible (e.g., returning from quiz)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && user && !authLoading) {
        fetchProfile();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [user, authLoading]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const token = await user?.getIdToken();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'https://closetgptrenew-production.up.railway.app'}/api/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const profileData = await response.json();
        console.log('🎭 [Persona Page] Fetched profile data:', profileData);
        setProfile(profileData);
      } else {
        throw new Error('Failed to fetch profile');
      }
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError('Failed to load your style persona');
    } finally {
      setLoading(false);
    }
  };

  const determineStylePersona = (): StylePersona => {
    console.log('🎭 [Style Persona] Determining persona for profile:', profile);
    
    // First, try to use the stored persona from the profile
    const storedPersona =
      (profile?.stylePersona as StylePersona | undefined) ||
      (profile as any)?.style_persona;

    if (storedPersona && storedPersona.id && STYLE_PERSONAS[storedPersona.id]) {
      console.log('🎭 [Style Persona] Using stored persona:', storedPersona);
      
      // Override the stored persona's examples with gender-specific ones
      const basePersona = {
        ...STYLE_PERSONAS[storedPersona.id],
        ...storedPersona,
      } as StylePersona;
      const genderSpecificExamples = getGenderSpecificCelebrities(basePersona.id, profile?.gender);
      
      return {
        ...basePersona,
        examples: genderSpecificExamples
      };
    }

    // Fallback: determine persona based on style preferences
    const combinedPreferences = [
      ...(profile?.stylePreferences || []),
      ...((profile?.preferences?.style || []) as string[]),
      ...((profile as any)?.style_preferences || []),
    ]
      .filter(Boolean)
      .map((pref) => pref.toString().toLowerCase());
    
    const personaScores: Record<string, number> = {
      architect: 0,
      strategist: 0,
      innovator: 0,
      classic: 0,
      wanderer: 0,
      rebel: 0,
      connoisseur: 0,
      modernist: 0,
    };

    const bump = (persona: keyof typeof personaScores, amount = 1) => {
      personaScores[persona] += amount;
    };

    combinedPreferences.forEach((pref) => {
      if (pref.includes('minimal') || pref.includes('architect') || pref.includes('structured')) {
        bump('architect', 3);
        bump('modernist', 2);
      }
      if (pref.includes('street') || pref.includes('urban') || pref.includes('rebel') || pref.includes('bold')) {
        bump('rebel', 3);
        bump('strategist', 1);
      }
      if (pref.includes('classic') || pref.includes('old money') || pref.includes('heritage')) {
        bump('classic', 3);
        bump('connoisseur', 2);
      }
      if (pref.includes('luxury') || pref.includes('connoisseur') || pref.includes('refined')) {
        bump('connoisseur', 3);
        bump('classic', 1);
      }
      if (pref.includes('boho') || pref.includes('cottage') || pref.includes('wanderer')) {
        bump('wanderer', 3);
        bump('rebel', 1);
      }
      if (pref.includes('innovator') || pref.includes('creative') || pref.includes('trend')) {
        bump('innovator', 2);
        bump('modernist', 1);
        bump('rebel', 1);
      }
      if (pref.includes('modern') || pref.includes('contemporary')) {
        bump('modernist', 3);
        bump('architect', 1);
      }
    });

    const stylePersonality =
      profile?.stylePersonality ||
      (profile as any)?.style_personality ||
      null;

    if (stylePersonality) {
      if ((stylePersonality.minimal ?? 0) >= 0.6) {
        bump('architect', 3);
        bump('modernist', 2);
      }
      if ((stylePersonality.classic ?? 0) >= 0.6) {
        bump('classic', 3);
        bump('connoisseur', 2);
      }
      if ((stylePersonality.bold ?? 0) >= 0.6) {
        bump('rebel', 3);
        bump('innovator', 1);
      }
      if ((stylePersonality.creative ?? 0) >= 0.6) {
        bump('innovator', 2);
        bump('wanderer', 1);
      }
      if ((stylePersonality.modern ?? 0) >= 0.6) {
        bump('modernist', 2);
        bump('strategist', 1);
      }
    }

    const ranked = Object.entries(personaScores)
      .sort(([, a], [, b]) => b - a);

    const [topPersona, topScore] = ranked[0] || ['modernist', 0];

    if (topScore > 0 && topPersona && STYLE_PERSONAS[topPersona as keyof typeof STYLE_PERSONAS]) {
      const selectedPersona = STYLE_PERSONAS[topPersona as keyof typeof STYLE_PERSONAS];
      // Add gender-specific celebrity examples
      const genderSpecificExamples = getGenderSpecificCelebrities(selectedPersona.id, profile?.gender);
      return {
        ...selectedPersona,
        examples: genderSpecificExamples
      };
    }

    // Default fallback to modernist with gender-specific examples
    const fallbackPersona = STYLE_PERSONAS.modernist;
    const genderSpecificExamples = getGenderSpecificCelebrities(fallbackPersona.id, profile?.gender);
    return {
      ...fallbackPersona,
      examples: genderSpecificExamples
    };
  };

  const generateStyleFingerprint = () => {
    const stylePersonality =
      profile?.stylePersonality ||
      (profile as any)?.style_personality ||
      null;

    if (!stylePersonality) {
      return {
        creativeExpression: { restrained: 30, expressive: 70 },
        trendAwareness: { timeless: 40, trendsetting: 60 },
        wardrobeFlexibility: { focused: 50, versatile: 50 }
      };
    }

    return {
      creativeExpression: {
        restrained: Math.round((1 - (stylePersonality.creative || 0.5)) * 100),
        expressive: Math.round((stylePersonality.creative || 0.5) * 100)
      },
      trendAwareness: {
        timeless: Math.round((1 - (stylePersonality.trendy || 0.6)) * 100),
        trendsetting: Math.round((stylePersonality.trendy || 0.6) * 100)
      },
      wardrobeFlexibility: {
        focused: Math.round((1 - (stylePersonality.versatile || 0.5)) * 100),
        versatile: Math.round((stylePersonality.versatile || 0.5) * 100)
      }
    };
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 dark:border-white mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your style persona...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950 flex items-center justify-center p-4">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Style Persona Not Found</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error || "We couldn't find your style persona. Please complete the style quiz first."}
          </p>
          <button
            onClick={() => router.push('/onboarding')}
            className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-3 rounded-full font-medium transition-colors"
          >
            Take Style Quiz
          </button>
        </div>
      </div>
    );
  }

  const persona = determineStylePersona();
  const styleFingerprint = generateStyleFingerprint();

  // Safety check: If no persona determined, default to modernist
  if (!persona || !persona.id) {
    console.error('⚠️ No persona determined, using modernist as fallback');
    const fallbackPersona = STYLE_PERSONAS['modernist'];
    
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
        <Navigation />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <div className="bg-white dark:bg-gray-800 rounded-3xl p-8 mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Welcome to {fallbackPersona.name}!
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              We've set your default persona. Retake the quiz to get a personalized style persona.
            </p>
            <button
              onClick={() => router.push('/onboarding')}
              className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-white px-6 py-3 rounded-full font-semibold"
            >
              Retake Style Quiz
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />
      
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Hero Section with Glass Effect */}
        <div className="glass-float rounded-3xl overflow-hidden mb-8 glass-shadow-strong">
          {/* Hero Image Only - Text Moved Below */}
          <div className="relative h-[500px] overflow-hidden rounded-t-3xl">
            <img 
              src={getHeroImageForPersona(persona.id, profile?.gender)}
              alt={`${persona.name} style example`}
              className="w-full h-full object-cover object-top"
              onError={(e) => {
                console.error('❌ [Persona Page] Hero image failed to load:', e.currentTarget.src);
                e.currentTarget.src = '/images/placeholder.jpg';
              }}
            />
          </div>

          {/* Content Section - BELOW Image */}
          <div className="p-8 bg-[#2C2119] dark:bg-[#2C2119]">
            {/* Persona Title and Tagline */}
            <div className="text-center max-w-4xl mx-auto mb-8">
              <div className="text-sm font-medium text-gray-400 mb-3 tracking-wider">YOU ARE</div>
              <h1 className="text-5xl md:text-6xl font-serif font-bold mb-4 leading-tight text-white">
                {persona.name}
              </h1>
              <p className="text-xl text-gray-300 mb-6 leading-relaxed font-light">
                {persona.tagline}
              </p>
              
              {/* Style Traits */}
              <div className="flex flex-wrap gap-3 justify-center mb-8">
                {persona.traits.map((trait, index) => (
                  <span 
                    key={index}
                    className="px-4 py-2 bg-white/10 backdrop-blur-sm text-white rounded-full text-sm font-medium border border-white/20"
                  >
                    {trait}
                  </span>
                ))}
              </div>
            </div>

            {/* Description */}
            <div className="text-center max-w-4xl mx-auto mb-8">
              <p className="text-lg text-gray-300 leading-relaxed">
                {persona.description}
              </p>
            </div>
            
            {/* Style Mission */}
            <div className="max-w-3xl mx-auto">
              <div className="bg-[#1A1510] rounded-2xl p-8 border border-[#3D2F24]">
                <h3 className="text-2xl font-serif font-semibold text-white mb-4">Your Style Mission</h3>
                <p className="text-lg text-gray-400 italic leading-relaxed">
                  {persona.styleMission}
                </p>
              </div>
            </div>
          </div>
        </div>


        {/* Premium Upsell Section */}
        <div className="glass-float rounded-3xl p-10 mb-10 glass-shadow border border-[#F5F0E8]/80 dark:border-[#3D2F24]/80 bg-gradient-to-r from-[#FFB84C]/20 via-[#FFF4E0]/40 to-[#FF9400]/20 dark:from-[#4A2E1A]/70 dark:via-[#2C2119]/80 dark:to-[#3D2F24]/70">
          <div className="flex flex-col lg:flex-row gap-8 lg:items-center">
            <div className="flex-1 space-y-4">
              <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-[#B45309] dark:text-[#FBBF24]">
                <Sparkles className="h-4 w-4" />
                Premium Style Blueprint
              </span>
              <h2 className="text-3xl font-serif font-bold text-[#1C1917] dark:text-[#F8F5F1]">
                Level up your {persona.name} look with pro styling
              </h2>
              <p className="text-lg text-[#57534E] dark:text-[#C4BCB4] leading-relaxed">
                Unlock a bespoke wardrobe roadmap, tailored capsule collections, and weekly fit drops designed specifically for your {persona.name.toLowerCase()} vibe.
              </p>
              <ul className="grid sm:grid-cols-2 gap-3 pt-2 text-sm text-[#57534E] dark:text-[#C4BCB4]">
                <li className="glass-inner rounded-xl px-4 py-3 flex items-start gap-3">
                  <span className="text-[#FF9400]">◆</span>
                  <span>Curated outfit playbooks refreshed every season</span>
                </li>
                <li className="glass-inner rounded-xl px-4 py-3 flex items-start gap-3">
                  <span className="text-[#FF9400]">◆</span>
                  <span>Shopping lists with brand & price filters matched to you</span>
                </li>
                <li className="glass-inner rounded-xl px-4 py-3 flex items-start gap-3">
                  <span className="text-[#FF9400]">◆</span>
                  <span>Style coach check-ins to keep your streak alive</span>
                </li>
                <li className="glass-inner rounded-xl px-4 py-3 flex items-start gap-3">
                  <span className="text-[#FF9400]">◆</span>
                  <span>Advanced color + fit guidance for every event</span>
                </li>
              </ul>
              <div className="flex flex-col sm:flex-row sm:items-center gap-4 pt-4">
                <button
                  onClick={() => router.push('/upgrade?plan=style-blueprint')}
                  className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-8 py-3 rounded-2xl font-semibold shadow-lg shadow-amber-500/25 transition-transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  Upgrade for {persona.name} perks
                  <ArrowRight className="h-4 w-4" />
                </button>
                {cameFromQuiz && (
                  <span className="text-sm font-medium text-[#B45309] dark:text-[#FBBF24]">
                    You’re moments away from your premium wardrobe kit.
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Style Fingerprint Section with Glass Effect */}
        <div className="glass-float rounded-3xl p-8 mb-8 glass-shadow">
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

        {/* The [Persona]s You May Know Section */}
        <div className="glass-float rounded-3xl p-8 mb-8 glass-shadow">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-serif font-bold text-gray-900 dark:text-white mb-4">
              The {persona.name.split(' ')[1]}s You May Know
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              Celebrities and icons who embody the {persona.name.toLowerCase()} style
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {getGenderSpecificCelebrities(persona.id, profile?.gender)?.map((celebrity, index) => {
              console.log('🎭 [Celebrities] Profile gender:', profile?.gender, 'Persona:', persona.id, 'Celebrity:', celebrity);
              return (
              <div key={index} className="text-center p-6 glass-inner rounded-2xl glass-transition hover:shadow-lg hover:bg-white/30 dark:hover:bg-gray-900/30 hover:scale-105">
                <div className="text-4xl mb-3">♪</div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  {celebrity}
                </h3>
              </div>
              );
            }) || (
              // Fallback for personas without celebrities defined
              <div className="text-center p-6 glass-inner rounded-2xl">
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
        <div className="glass-float rounded-3xl p-12 text-center glass-shadow-strong bg-gradient-to-r from-amber-500/20 to-orange-500/20 dark:from-amber-900/40 dark:to-orange-900/40 backdrop-blur-2xl border-2 border-amber-300/30 dark:border-amber-700/30">
          <h2 className="text-4xl font-serif font-bold mb-4 text-gray-900 dark:text-white">We've Got You Covered</h2>
          <p className="text-xl text-gray-700 dark:text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed">
            Your {persona.name.toLowerCase()} style is ready to shine. Let's build the perfect wardrobe that matches your bold personality.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <button 
              onClick={() => router.push('/upgrade?plan=style-blueprint')}
              className="glass-button-primary px-8 py-4 rounded-full font-semibold text-lg glass-transition hover:scale-105"
            >
              Unlock my premium plan →
            </button>
            <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
              <div className="w-8 h-8 glass-inner rounded-full flex items-center justify-center">
                <span className="text-sm font-bold">4</span>
              </div>
              <span className="text-sm">Personalized recommendations</span>
            </div>
          </div>
          
          {/* Navigation Links */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button 
              onClick={() => router.push('/')}
              className="glass-button-secondary text-stone-900 dark:text-stone-100 px-6 py-3 rounded-full font-medium glass-transition"
            >
              🏠 Dashboard
            </button>
            <button 
              onClick={() => router.push('/profile')}
              className="glass-button-secondary text-stone-900 dark:text-stone-100 px-6 py-3 rounded-full font-medium glass-transition"
            >
              👤 My Profile
            </button>
            <button 
              onClick={() => router.push('/onboarding')}
              className="glass-button-secondary text-stone-900 dark:text-stone-100 px-6 py-3 rounded-full font-medium glass-transition"
            >
              🔄 Retake Quiz
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
