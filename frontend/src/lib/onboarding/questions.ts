export interface QuizQuestion {
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
export const QUIZ_QUESTIONS: QuizQuestion[] = [
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
    id: "body_type_nonbinary",
    question: "Which body shape best describes you? (All bodies are beautiful!)",
    options: ["Round/Apple", "Athletic", "Rectangle", "Inverted Triangle", "Pear", "Hourglass", "Oval", "Plus Size", "Petite", "Tall", "Slim", "Muscular"],
    category: "measurements",
    type: "visual",
    images: [
      "/images/body-types/apple.png",
      "/images/body-types/athletic.png",
      "/images/body-types/rectangular.png",
      "/images/body-types/inverted.png",
      "/images/body-types/pear.png",
      "/images/body-types/hourglass.png",
      "/images/body-types/curvy.png",
      "/images/body-types/curvy.png",
      "/images/body-types/athletic.png",
      "/images/body-types/athletic.png",
      "/images/body-types/athletic.png",
      "/images/body-types/athletic.png"
    ],
    gender: "nonbinary"
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
    options: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL+", "Prefer not to say"],
    category: "sizes"
  },
  {
    id: "bottom_size",
    question: "What is your bottom size?",
    options: ["XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL+", "Prefer not to say"],
    category: "sizes"
  },
  {
    id: "cup_size",
    question: "What is your cup size? (Optional)",
    options: ["AA", "A", "B", "C", "D", "DD", "DDD+", "Prefer not to say"],
    category: "sizes"
  },
  {
    id: "shoe_size_female",
    question: "What is your shoe size?",
    options: ["4 or smaller", "5", "6", "7", "8", "9", "10", "11", "12+", "Prefer not to say"],
    category: "sizes",
    gender: "female"
  },
  {
    id: "shoe_size_male",
    question: "What is your shoe size?",
    options: ["4 or smaller", "5", "6", "7", "8", "9", "10", "11", "12", "13+", "Prefer not to say"],
    category: "sizes",
    gender: "male"
  },
  {
    id: "shoe_size",
    question: "What is your shoe size?",
    options: ["4 or smaller", "5", "6", "7", "8", "9", "10", "11", "12", "13+", "Prefer not to say"],
    category: "sizes"
    // No gender filter - shows for Non-binary and Prefer not to say
  },
  // Spending questions - after all size questions
  {
    id: "category_spend_tops",
    question: "How much do you typically spend on tops per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_pants",
    question: "How much do you typically spend on pants per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_shoes",
    question: "How much do you typically spend on shoes per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_jackets",
    question: "How much do you typically spend on jackets per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_dresses",
    question: "How much do you typically spend on dresses per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements",
    gender: "female" // Show for Female + Non-binary + Prefer not to say (see filter logic)
  },
  {
    id: "category_spend_accessories",
    question: "How much do you typically spend on accessories per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_undergarments",
    question: "How much do you typically spend on undergarments per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
  },
  {
    id: "category_spend_swimwear",
    question: "How much do you typically spend on swimwear per year?",
    options: ["$0-$100", "$100-$250", "$250-$500", "$500-$1,000", "$1,000+"],
    category: "measurements"
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

// Keep the pre-auth preview focused on the inputs needed to demonstrate
// personalization. Signed-in users can complete the deeper sizing and spend
// profile without turning the first product experience into a long intake form.
const GUEST_DEEP_PROFILE_QUESTION_IDS = new Set([
  'height',
  'weight',
  'top_size',
  'bottom_size',
  'cup_size',
  'shoe_size_female',
  'shoe_size_male',
  'shoe_size',
]);

export function fullQuizQuestions(currentGender: string | null, guest = false): QuizQuestion[] {
    const filtered = QUIZ_QUESTIONS.filter(question => {
      if (
        guest &&
        (GUEST_DEEP_PROFILE_QUESTION_IDS.has(question.id) || question.id.startsWith('category_spend_'))
      ) {
        return false;
      }

      // GENERIC GENDER FILTER: Check question.gender attribute first
      // Special handling for style questions - non-binary users should see BOTH male and female style questions
      const isStyleQuestion = question.id.startsWith('style_item_f_') || question.id.startsWith('style_item_m_');
      const isNonBinaryUser = currentGender === 'Non-binary' || currentGender === 'Prefer not to say';
      const isDressesSpendQuestion = question.id === 'category_spend_dresses';

      // For female-specific questions: show to Female users, and also to Non-binary users if it's a style question
      if (question.gender === 'female' && currentGender && currentGender !== 'Female') {
        // Exception: dresses spend question should also show for Non-binary / Prefer not to say (but not Male)
        if (!((isStyleQuestion && isNonBinaryUser) || (isDressesSpendQuestion && isNonBinaryUser))) {
          return false;
        }
      }
      // For male-specific questions: show to Male users, and also to Non-binary users if it's a style question
      if (question.gender === 'male' && currentGender && currentGender !== 'Male') {
        if (!(isStyleQuestion && isNonBinaryUser)) {
          return false;
        }
      }
      // For nonbinary-specific questions: only show to Non-binary and Prefer not to say users
      if (question.gender === 'nonbinary' && currentGender &&
          currentGender !== 'Non-binary' &&
          currentGender !== 'Prefer not to say') {
        return false;
      }

      // Show cup size for females, non-binary, and prefer not to say users
      if (question.id === 'cup_size' && currentGender &&
          currentGender !== 'Female' &&
          currentGender !== 'Non-binary' &&
          currentGender !== 'Prefer not to say') {
        return false;
      }

      // Show gender-specific body type questions
      if (question.id === 'body_type_female' && currentGender && currentGender !== 'Female') {
        return false;
      }
      if (question.id === 'body_type_male' && currentGender && currentGender !== 'Male') {
        return false;
      }
      if (question.id === 'body_type_nonbinary' && currentGender && (currentGender === 'Female' || currentGender === 'Male')) {
        return false;
      }

      // Show gender-specific shoe size questions
      if (question.id === 'shoe_size_female' && currentGender && currentGender !== 'Female') {
        return false;
      }
      if (question.id === 'shoe_size_male' && currentGender && currentGender !== 'Male') {
        return false;
      }
      // Generic shoe_size (for non-binary / prefer not to say)
      if (question.id === 'shoe_size' && currentGender && (currentGender === 'Male' || currentGender === 'Female')) {
        return false;
      }

      // Style questions are already handled by the generic gender filter above
      // which allows non-binary users to see both male and female style questions

      return true;
    });

    return filtered;
}
