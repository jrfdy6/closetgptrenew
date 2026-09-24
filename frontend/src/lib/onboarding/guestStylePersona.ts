import type { QuizAnswerRecord } from '@/lib/quizAnswerContract';
import { QUIZ_QUESTIONS } from './questions';

// Retain the existing local guest persona payload; account profiles are saved by the server.
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

export function guestStylePersona(answers: readonly QuizAnswerRecord[]): StylePersona {
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
    
    // Count total "Yes" answers for style questions
    const styleYesAnswers = answers.filter(answer => {
      const question = QUIZ_QUESTIONS.find(q => q.id === answer.question_id);
      return question && question.type === 'visual_yesno' && answer.selected_option === 'Yes';
    }).length;

    return STYLE_PERSONAS[topPersona] || STYLE_PERSONAS.strategist;
  }
