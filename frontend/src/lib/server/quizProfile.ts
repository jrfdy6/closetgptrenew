import { serverDebugLog } from '@/lib/server/debug';

export function mapQuizAnswersToProfile(
  userAnswers: Record<string, string>,
  colorAnalysis: any,
  stylePreferences: string[],
  colorPreferences: string[],
  userName: string = 'Quiz User',
  userEmail: string = 'quiz@example.com',
  userId: string = 'quiz-user',
  spendingRanges: Record<string, string> | null = null
) {
  // Calculate style personality scores based on preferences
  const stylePersonality = calculateStylePersonality(stylePreferences, userAnswers);

  // Determine the style persona based on quiz answers
  const determinedPersona = determineStylePersona(userAnswers, stylePreferences);

  const resolvedColorPreferences =
    colorPreferences.length > 0
      ? colorPreferences
      : Array.from(
          new Set(
            [
              ...(colorAnalysis?.palette?.primary || []),
              ...(colorAnalysis?.palette?.secondary || []),
              ...(colorAnalysis?.palette?.accents || []),
            ]
              .filter(Boolean)
              .slice(0, 8)
          )
        );

  const resolvedStylePreferences =
    stylePreferences.length > 0
      ? stylePreferences
      : Array.from(
          new Set(
            [
              // Don't include persona name in stylePreferences - it goes in stylePersona.name
              ...(Object.keys(stylePersonality || {}) || []),
            ]
              .map((value) => value.toString())
              .filter(Boolean)
          )
        );

  const resolvedBodyType =
    userAnswers.body_type_female ||
    userAnswers.body_type_male ||
    userAnswers.body_type_nonbinary ||
    '';
  const rawSkinTone = userAnswers.skin_tone || '';
  const resolvedSkinTone = /^skin_tone_(?:100|[1-9]?\d)$/.test(rawSkinTone)
    ? rawSkinTone
    : null;

  // Map basic profile fields
  const profileUpdate: any = {
    // Required fields for backend
    name: userName,
    email: userEmail,
    userId,
    user_id: userId,

    // Quiz-specific fields
    gender: userAnswers.gender,
    bodyType: resolvedBodyType,
    skinTone: resolvedSkinTone,
    measurements: {
      height: parseHeight(userAnswers.height),
      weight: parseWeight(userAnswers.weight),
      bodyType: resolvedBodyType,
      skinTone: resolvedSkinTone,
      topSize: userAnswers.top_size || '',
      bottomSize: userAnswers.bottom_size || '',
      shoeSize: userAnswers.shoe_size_male || userAnswers.shoe_size_female || userAnswers.shoe_size || '',
      braSize: userAnswers.cup_size || ''
    },
    // Also store the raw height value for display.
    heightFeetInches: parseHeight(userAnswers.height),
    // Store height and weight at top level for easy access
    height: parseHeight(userAnswers.height),
    weight: parseWeight(userAnswers.weight),
    stylePreferences: resolvedStylePreferences,
    preferences: {
      style: resolvedStylePreferences,
      colors: resolvedColorPreferences,
      occasions: [userAnswers.daily_activities || '']
    },
    stylePersonality: stylePersonality,
    colorPalette: {
      primary: resolvedColorPreferences.slice(0, 3),
      secondary: resolvedColorPreferences.slice(3, 6),
      accent: resolvedColorPreferences.slice(6, 9),
      neutral: ['black', 'white', 'gray', 'beige'],
      avoid: []
    },
    // Add persona data
    stylePersona: {
      id: determinedPersona.id,
      name: determinedPersona.name,
      tagline: determinedPersona.tagline,
      description: determinedPersona.description,
      styleMission: determinedPersona.styleMission,
      traits: determinedPersona.traits,
      examples: determinedPersona.examples
    },
    // Spending ranges saved during quiz submit.
    // Backend marks TVE recalculation as queued (non-blocking).
    ...(spendingRanges ? { spending_ranges: spendingRanges } : {}),
    updatedAt: Math.floor(Date.now() / 1000), // Unix timestamp like backend
    updated_at: Math.floor(Date.now() / 1000) // Also add with underscore for backend compatibility
  };

  // A shortened guest draft or omitted optional answer must never erase saved fields.
  const measurementQuestions: Record<string, string[]> = {
    height: ['height'], weight: ['weight'], bodyType: ['body_type_female', 'body_type_male', 'body_type_nonbinary'],
    skinTone: ['skin_tone'], topSize: ['top_size'], bottomSize: ['bottom_size'],
    shoeSize: ['shoe_size_male', 'shoe_size_female', 'shoe_size'], braSize: ['cup_size'],
  };
  for (const [field, ids] of Object.entries(measurementQuestions)) {
    if (!ids.some(id => Object.prototype.hasOwnProperty.call(userAnswers, id))) {
      delete profileUpdate.measurements[field];
      delete profileUpdate[field];
      if (field === 'height') delete profileUpdate.heightFeetInches;
    }
  }
  if (!Object.keys(profileUpdate.measurements).length) delete profileUpdate.measurements;
  if (!userAnswers.gender) delete profileUpdate.gender;
  if (!userAnswers.daily_activities) delete profileUpdate.preferences.occasions;
  if (!resolvedColorPreferences.length) {
    delete profileUpdate.preferences.colors;
    delete profileUpdate.colorPalette;
  }
  return profileUpdate;
}

// Determine style persona based on quiz answers (copied from onboarding)
function determineStylePersona(userAnswers: Record<string, string>, stylePreferences: string[]): any {
  const STYLE_PERSONAS: Record<string, any> = {
    architect: {
      id: "architect",
      name: "The Architect",
      tagline: "Clean lines. Bold vision. Timeless design.",
      description: "You approach fashion like an architect approaches buildings - with precision, intention, and a focus on form following function. Your style is structured, sophisticated, and built to last. You appreciate quality construction and aren't afraid to make a statement with clean, geometric lines.",
      styleMission: "Build your wardrobe like you'd design a building - with a strong foundation, thoughtful details, and pieces that stand the test of time.",
      examples: ["Zaha Hadid", "Tadao Ando", "Frank Gehry", "Norman Foster", "Rem Koolhaas"],
      traits: ["Clean lines", "Bold vision", "Timeless design", "Quality construction", "Geometric precision"],
      cta: "See My Plan Options →"
    },
    strategist: {
      id: "strategist",
      name: "The Strategist",
      tagline: "Smart choices. Versatile pieces. Effortless style.",
      description: "You approach fashion strategically, building a wardrobe that works hard for you. Your style is practical, versatile, and always appropriate. You value pieces that can be mixed and matched across different occasions and seasons.",
      styleMission: "Build a strategic wardrobe with pieces that work together seamlessly. Focus on versatility and quality over quantity.",
      examples: ["Amal Clooney", "Victoria Beckham", "Ryan Gosling", "Emma Stone", "Chris Evans"],
      traits: ["Smart choices", "Versatile pieces", "Effortless style", "Strategic thinking", "Quality over quantity"],
      cta: "See My Plan Options →"
    },
    innovator: {
      id: "innovator",
      name: "The Innovator",
      tagline: "Forward-thinking. Experimental. Trend-setting.",
      description: "You're always ahead of the curve, experimenting with new styles and pushing boundaries. Your fashion choices reflect your innovative spirit and willingness to take risks. You're not afraid to try new things and often set trends rather than follow them.",
      styleMission: "Stay ahead of trends and don't be afraid to experiment. Focus on pieces that reflect your innovative spirit and forward-thinking approach.",
      examples: ["Lady Gaga", "Pharrell Williams", "Rihanna", "Billy Porter", "Zendaya"],
      traits: ["Forward-thinking", "Experimental", "Trend-setting", "Risk-taking", "Innovative spirit"],
      cta: "See My Plan Options →"
    },
    classic: {
      id: "classic",
      name: "The Classic",
      tagline: "Timeless elegance. Sophisticated style. Never goes out of fashion.",
      description: "You appreciate the finer things and believe in investing in pieces that will last a lifetime. Your style is elegant, sophisticated, and built on timeless principles. You look polished without being flashy, and your wardrobe reflects your appreciation for quality and tradition.",
      styleMission: "Refine your existing foundation. Focus on perfect tailoring, quality fabrics, and timeless silhouettes. Invest in pieces that will last decades.",
      examples: ["Audrey Hepburn", "Grace Kelly", "Cary Grant", "Sophia Loren", "Paul Newman"],
      traits: ["Timeless elegance", "Sophisticated style", "Quality investment", "Polished appearance", "Traditional values"],
      cta: "See My Plan Options →"
    },
    wanderer: {
      id: "wanderer",
      name: "The Wanderer",
      tagline: "Free-spirited. Bohemian soul. Adventure-ready.",
      description: "You're drawn to pieces that tell a story and reflect your adventurous spirit. Your style is eclectic, free-spirited, and often inspired by your travels and experiences. You value comfort and self-expression over trends.",
      styleMission: "Embrace your free spirit and don't be afraid to mix styles and cultures. Focus on pieces that reflect your adventures and personal journey.",
      examples: ["Stevie Nicks", "Johnny Depp", "Kate Moss", "Lenny Kravitz", "Sienna Miller"],
      traits: ["Free-spirited", "Bohemian soul", "Adventure-ready", "Eclectic style", "Story-telling pieces"],
      cta: "See My Plan Options →"
    },
    rebel: {
      id: "rebel",
      name: "The Rebel",
      tagline: "Bold statements. Unconventional choices. Authentic expression.",
      description: "You don't follow trends - you create them. Your style is bold, unconventional, and authentically you. You're not afraid to mix unexpected pieces, experiment with color, or wear something that makes people look twice. Your fashion choices are a form of self-expression and rebellion against the ordinary.",
      styleMission: "Break the rules, set your own trends, and wear what makes you feel most like yourself. Don't be afraid to stand out.",
      examples: ["David Bowie", "Grace Jones", "Prince", "Frida Kahlo", "Alexander McQueen"],
      traits: ["Bold statements", "Unconventional choices", "Authentic expression", "Rule breaking", "Trend setting"],
      cta: "See My Plan Options →"
    },
    connoisseur: {
      id: "connoisseur",
      name: "The Connoisseur",
      tagline: "Refined taste. Luxury details. Quiet confidence.",
      description: "You have an eye for quality and appreciate the finer things in life. Your style is sophisticated, understated, and built on investment pieces that speak to your refined taste. You understand that true luxury is in the details, not the labels.",
      styleMission: "Curate your collection with intention. Focus on exceptional pieces that will last decades and don't be afraid to invest in quality over quantity.",
      examples: ["Meghan Markle", "Blake Lively", "Ryan Reynolds", "Henry Cavill", "Cate Blanchett"],
      traits: ["Refined taste", "Quality over quantity", "Luxury details", "Quiet confidence", "Investment pieces"],
      cta: "See My Plan Options →"
    },
    modernist: {
      id: "modernist",
      name: "The Modernist",
      tagline: "Clean lines. Contemporary edge. Future-focused.",
      description: "You're drawn to clean, contemporary design and appreciate the intersection of fashion and function. Your style is modern, streamlined, and forward-thinking. You value versatility and pieces that work across different contexts while maintaining a sleek, contemporary aesthetic.",
      styleMission: "Build a wardrobe that's both functional and fashionable. Focus on versatile pieces with clean lines and don't be afraid to experiment with modern silhouettes.",
      examples: ["Hailey Bieber", "Kendall Jenner", "Timothée Chalamet", "Harry Styles", "Anya Taylor-Joy"],
      traits: ["Clean lines", "Contemporary edge", "Functional fashion", "Versatile pieces", "Future-focused"],
      cta: "See My Plan Options →"
    }
  };

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

  // Map style preferences to personas
  if (stylePreferences.includes('Minimalist') || stylePreferences.includes('Clean Minimal')) {
    personaScores.architect += 3;
    personaScores.modernist += 2;
  }
  if (stylePreferences.includes('Street Style') || stylePreferences.includes('Urban Street')) {
    personaScores.rebel += 3;
    personaScores.strategist += 1;
  }
  if (stylePreferences.includes('Classic Elegant')) {
    personaScores.classic += 3;
    personaScores.connoisseur += 2;
  }
  if (stylePreferences.includes('Old Money')) {
    personaScores.classic += 2;
    personaScores.connoisseur += 3;
  }
  if (stylePreferences.includes('Cottagecore') || stylePreferences.includes('Natural Boho')) {
    personaScores.wanderer += 3;
    personaScores.rebel += 1;
  }

  // Daily activities scoring
  if (userAnswers.daily_activities === 'Office work and meetings') {
    personaScores.connoisseur += 2;
    personaScores.architect += 1;
    personaScores.classic += 1;
  }
  if (userAnswers.daily_activities === 'Creative work and casual meetings') {
    personaScores.modernist += 2;
    personaScores.rebel += 1;
    personaScores.innovator += 1;
  }
  if (userAnswers.daily_activities === 'Active lifestyle and sports') {
    personaScores.rebel += 2;
    personaScores.strategist += 1;
  }
  if (userAnswers.daily_activities === 'Mix of everything') {
    personaScores.modernist += 3;
    personaScores.strategist += 2;
  }

  // Style elements scoring
  if (userAnswers.style_elements === 'Clean lines and minimal details') {
    personaScores.architect += 3;
    personaScores.modernist += 2;
  }
  if (userAnswers.style_elements === 'Rich textures and patterns') {
    personaScores.connoisseur += 3;
    personaScores.classic += 1;
  }
  if (userAnswers.style_elements === 'Classic and timeless pieces') {
    personaScores.classic += 3;
    personaScores.connoisseur += 2;
    personaScores.architect += 1;
  }
  if (userAnswers.style_elements === 'Bold and statement pieces') {
    personaScores.rebel += 3;
    personaScores.innovator += 1;
  }

  // Find the highest scoring persona
  const sortedPersonas = Object.entries(personaScores)
    .sort(([,a], [,b]) => b - a);

  const topPersona = sortedPersonas[0][0];

  serverDebugLog('🎯 [Quiz Submit] Persona scores:', personaScores);
  serverDebugLog('🎯 [Quiz Submit] Selected persona:', topPersona);

  return STYLE_PERSONAS[topPersona] || STYLE_PERSONAS.rebel;
}

// Calculate style personality scores based on quiz answers
function calculateStylePersonality(stylePreferences: string[], userAnswers: Record<string, string>) {
  const scores = {
    classic: 0.5,
    modern: 0.5,
    creative: 0.5,
    minimal: 0.5,
    bold: 0.5
  };

  // Adjust scores based on style preferences
  stylePreferences.forEach(style => {
    switch (style) {
      case 'Classic Elegant':
      case 'Old Money':
        scores.classic += 0.3;
        scores.minimal += 0.1;
        break;
      case 'Street Style':
      case 'Urban Street':
        scores.bold += 0.3;
        scores.creative += 0.2;
        break;
      case 'Minimalist':
      case 'Clean Minimal':
        scores.minimal += 0.3;
        scores.classic += 0.1;
        break;
      case 'Cottagecore':
      case 'Natural Boho':
        scores.creative += 0.2;
        scores.modern += 0.1;
        break;
    }
  });

  // Adjust based on daily activities
  if (userAnswers.daily_activities === 'Office work and meetings') {
    scores.classic += 0.2;
    scores.minimal += 0.1;
  } else if (userAnswers.daily_activities === 'Creative work and casual meetings') {
    scores.creative += 0.2;
    scores.modern += 0.1;
  }

  // Adjust based on style elements
  if (userAnswers.style_elements === 'Clean lines and minimal details') {
    scores.minimal += 0.2;
    scores.classic += 0.1;
  } else if (userAnswers.style_elements === 'Bold and statement pieces') {
    scores.bold += 0.2;
    scores.creative += 0.1;
  }

  // Normalize scores to 0-1 range
  Object.keys(scores).forEach(key => {
    scores[key] = Math.max(0, Math.min(1, scores[key]));
  });

  return scores;
}

// Helper functions to parse measurements
function parseHeight(heightStr: string): string {
  if (!heightStr) return '';
  // Return the height range as-is since we're now using ranges
  return heightStr;
}

function parseWeight(weightStr: string): string {
  if (!weightStr) return '';
  // Return the weight range as-is since we're now using ranges
  return weightStr;
}
