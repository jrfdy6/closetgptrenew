import { NextResponse } from 'next/server';

// Mock quiz questions that match the backend structure
const MOCK_QUIZ_QUESTIONS = [
  {
    id: "gender",
    question: "What is your gender?",
    type: "multiple_choice",
    options: [
      {
        text: "Female",
        scores: {
          gender: "female"
        }
      },
      {
        text: "Male",
        scores: {
          gender: "male"
        }
      },
      {
        text: "Non-binary",
        scores: {
          gender: "non-binary"
        }
      },
      {
        text: "Prefer not to say",
        scores: {
          gender: "prefer-not-to-say"
        }
      }
    ],
    category: "personal"
  },
  {
    id: "body_type_female",
    question: "Which body type best describes you?",
    type: "image_choice",
    options: [
      {
        image: "apple.png",
        text: "Apple",
        scores: {
          body_type: "apple"
        }
      },
      {
        image: "athletic.png",
        text: "Athletic",
        scores: {
          body_type: "athletic"
        }
      },
      {
        image: "hourglass.png",
        text: "Hourglass",
        scores: {
          body_type: "hourglass"
        }
      },
      {
        image: "pear.png",
        text: "Pear",
        scores: {
          body_type: "pear"
        }
      },
      {
        image: "rectangular.png",
        text: "Rectangle",
        scores: {
          body_type: "rectangle"
        }
      },
      {
        image: "inverted.png",
        text: "Inverted Triangle",
        scores: {
          body_type: "inverted_triangle"
        }
      }
    ],
    category: "measurements",
    depends_on: { gender: "female" }
  },
  {
    id: "body_type_male",
    question: "Which body type best describes you?",
    type: "image_choice",
    options: [
      {
        image: "athletic.png",
        text: "Athletic",
        scores: {
          body_type: "athletic"
        }
      },
      {
        image: "rectangular.png",
        text: "Rectangle",
        scores: {
          body_type: "rectangle"
        }
      },
      {
        image: "inverted.png",
        text: "Inverted Triangle",
        scores: {
          body_type: "inverted_triangle"
        }
      },
      {
        image: "apple.png",
        text: "Apple",
        scores: {
          body_type: "apple"
        }
      }
    ],
    category: "measurements",
    depends_on: { gender: "male" }
  },
  {
    id: "body_type_nonbinary",
    question: "Which body type best describes you?",
    type: "image_choice",
    options: [
      {
        image: "apple.png",
        text: "Apple",
        scores: {
          body_type: "apple"
        }
      },
      {
        image: "athletic.png",
        text: "Athletic",
        scores: {
          body_type: "athletic"
        }
      },
      {
        image: "hourglass.png",
        text: "Hourglass",
        scores: {
          body_type: "hourglass"
        }
      },
      {
        image: "pear.png",
        text: "Pear",
        scores: {
          body_type: "pear"
        }
      },
      {
        image: "rectangular.png",
        text: "Rectangle",
        scores: {
          body_type: "rectangle"
        }
      },
      {
        image: "inverted.png",
        text: "Inverted Triangle",
        scores: {
          body_type: "inverted_triangle"
        }
      }
    ],
    category: "measurements",
    depends_on: { gender: "non-binary" }
  },
  {
    id: "skin_tone",
    question: "Which skin tone best matches yours?",
    type: "skin_tone_scale",
    options: [
      {
        text: "Very Light",
        color: "#F5E6D3",
        scores: {
          skin_tone: "very_light"
        }
      },
      {
        text: "Light",
        color: "#E6C7A8",
        scores: {
          skin_tone: "light"
        }
      },
      {
        text: "Light-Medium",
        color: "#D4A574",
        scores: {
          skin_tone: "light_medium"
        }
      },
      {
        text: "Medium",
        color: "#C68642",
        scores: {
          skin_tone: "medium"
        }
      },
      {
        text: "Medium-Dark",
        color: "#A0522D",
        scores: {
          skin_tone: "medium_dark"
        }
      },
      {
        text: "Dark",
        color: "#8B4513",
        scores: {
          skin_tone: "dark"
        }
      },
      {
        text: "Very Dark",
        color: "#654321",
        scores: {
          skin_tone: "very_dark"
        }
      }
    ],
    category: "measurements"
  },
  {
    id: "height",
    question: "What is your height?",
    type: "multiple_choice",
    options: [
      {
        text: "Under 5'0\"",
        scores: {
          height: "under_5ft"
        }
      },
      {
        text: "5'0\" - 5'3\"",
        scores: {
          height: "5ft_0_5ft_3"
        }
      },
      {
        text: "5'4\" - 5'7\"",
        scores: {
          height: "5ft_4_5ft_7"
        }
      },
      {
        text: "5'8\" - 5'11\"",
        scores: {
          height: "5ft_8_5ft_11"
        }
      },
      {
        text: "6'0\" - 6'3\"",
        scores: {
          height: "6ft_0_6ft_3"
        }
      },
      {
        text: "Over 6'3\"",
        scores: {
          height: "over_6ft_3"
        }
      }
    ],
    category: "measurements"
  },
  {
    id: "weight",
    question: "What is your weight range?",
    type: "multiple_choice",
    options: [
      {
        text: "Under 100 lbs",
        scores: {
          weight: "under_100"
        }
      },
      {
        text: "100-120 lbs",
        scores: {
          weight: "100_120"
        }
      },
      {
        text: "121-140 lbs",
        scores: {
          weight: "121_140"
        }
      },
      {
        text: "141-160 lbs",
        scores: {
          weight: "141_160"
        }
      },
      {
        text: "161-180 lbs",
        scores: {
          weight: "161_180"
        }
      },
      {
        text: "181-200 lbs",
        scores: {
          weight: "181_200"
        }
      },
      {
        text: "Over 200 lbs",
        scores: {
          weight: "over_200"
        }
      }
    ],
    category: "measurements"
  },
  {
    id: "top_size",
    question: "What is your top size?",
    type: "multiple_choice",
    options: [
      {
        text: "XS",
        scores: {
          top_size: "xs"
        }
      },
      {
        text: "S",
        scores: {
          top_size: "s"
        }
      },
      {
        text: "M",
        scores: {
          top_size: "m"
        }
      },
      {
        text: "L",
        scores: {
          top_size: "l"
        }
      },
      {
        text: "XL",
        scores: {
          top_size: "xl"
        }
      },
      {
        text: "XXL",
        scores: {
          top_size: "xxl"
        }
      },
      {
        text: "XXXL",
        scores: {
          top_size: "xxxl"
        }
      }
    ],
    category: "sizes"
  },
  {
    id: "bottom_size",
    question: "What is your bottom size?",
    type: "multiple_choice",
    options: [
      {
        text: "XS",
        scores: {
          bottom_size: "xs"
        }
      },
      {
        text: "S",
        scores: {
          bottom_size: "s"
        }
      },
      {
        text: "M",
        scores: {
          bottom_size: "m"
        }
      },
      {
        text: "L",
        scores: {
          bottom_size: "l"
        }
      },
      {
        text: "XL",
        scores: {
          bottom_size: "xl"
        }
      },
      {
        text: "XXL",
        scores: {
          bottom_size: "xxl"
        }
      },
      {
        text: "XXXL",
        scores: {
          bottom_size: "xxxl"
        }
      }
    ],
    category: "sizes"
  },
  {
    id: "cup_size",
    question: "What is your cup size?",
    type: "multiple_choice",
    options: [
      {
        text: "A",
        scores: {
          cup_size: "a"
        }
      },
      {
        text: "B",
        scores: {
          cup_size: "b"
        }
      },
      {
        text: "C",
        scores: {
          cup_size: "c"
        }
      },
      {
        text: "D",
        scores: {
          cup_size: "d"
        }
      },
      {
        text: "DD",
        scores: {
          cup_size: "dd"
        }
      },
      {
        text: "DDD",
        scores: {
          cup_size: "ddd"
        }
      },
      {
        text: "Prefer not to say",
        scores: {
          cup_size: "prefer_not_to_say"
        }
      }
    ],
    category: "sizes",
    depends_on: { gender: ["female", "non-binary"] }
  },
  {
    id: "shoe_size",
    question: "What is your shoe size?",
    type: "multiple_choice",
    options: [
      {
        text: "5 or smaller",
        scores: {
          shoe_size: "5_or_smaller"
        }
      },
      {
        text: "6",
        scores: {
          shoe_size: "6"
        }
      },
      {
        text: "7",
        scores: {
          shoe_size: "7"
        }
      },
      {
        text: "8",
        scores: {
          shoe_size: "8"
        }
      },
      {
        text: "9",
        scores: {
          shoe_size: "9"
        }
      },
      {
        text: "10",
        scores: {
          shoe_size: "10"
        }
      },
      {
        text: "11",
        scores: {
          shoe_size: "11"
        }
      },
      {
        text: "12 or larger",
        scores: {
          shoe_size: "12_or_larger"
        }
      }
    ],
    category: "sizes"
  },
  {
    id: "style_preference_female",
    question: "Which style resonates with you most?",
    type: "image_choice",
    options: [
      {
        image: "F-ST1.png",
        text: "Street Style",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      },
      {
        image: "F-CB1.png",
        text: "Cottagecore",
        scores: {
          romantic: 0.8,
          bohemian: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "F-MIN1.png",
        text: "Minimalist",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      },
      {
        image: "F-OM1.png",
        text: "Old Money",
        scores: {
          classic: 0.8,
          sophisticated: 0.6,
          romantic: 0.4
        }
      }
    ],
    category: "aesthetic",
    depends_on: { gender: "female" }
  },
  {
    id: "style_preference_male",
    question: "Which style resonates with you most?",
    type: "image_choice",
    options: [
      {
        image: "M-ST1.png",
        text: "Street Style",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      },
      {
        image: "M-CB1.png",
        text: "Natural Boho",
        scores: {
          bohemian: 0.8,
          romantic: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "M-MIN1.png",
        text: "Minimalist",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      },
      {
        image: "M-OM1.png",
        text: "Old Money",
        scores: {
          classic: 0.8,
          sophisticated: 0.6,
          romantic: 0.4
        }
      }
    ],
    category: "aesthetic",
    depends_on: { gender: "male" }
  },
  {
    id: "style_preference_nonbinary",
    question: "Which style resonates with you most?",
    type: "image_choice",
    options: [
      {
        image: "F-ST1.png",
        text: "Street Style (F)",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      },
      {
        image: "M-ST1.png",
        text: "Street Style (M)",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      },
      {
        image: "F-CB1.png",
        text: "Cottagecore (F)",
        scores: {
          romantic: 0.8,
          bohemian: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "M-CB1.png",
        text: "Natural Boho (M)",
        scores: {
          bohemian: 0.8,
          romantic: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "F-MIN1.png",
        text: "Minimalist (F)",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      },
      {
        image: "M-MIN1.png",
        text: "Minimalist (M)",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      }
    ],
    category: "aesthetic",
    depends_on: { gender: "non-binary" }
  },
  {
    id: "outfit_style",
    question: "Which outfit style appeals to you most?",
    type: "image_choice",
    options: [
      {
        image: "M-ST1.png",
        text: "Grunge Street",
        scores: {
          streetwear: 0.9,
          edgy: 0.7,
          athletic: 0.5
        }
      },
      {
        image: "M-CB1.png",
        text: "Natural Boho",
        scores: {
          bohemian: 0.9,
          romantic: 0.7,
          vintage: 0.5
        }
      },
      {
        image: "M-MIN1.png",
        text: "Clean Minimal",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.7,
          comfortable: 0.5
        }
      },
      {
        image: "M-OM1.png",
        text: "Classic Elegant",
        scores: {
          classic: 0.9,
          sophisticated: 0.7,
          preppy: 0.5
        }
      }
    ],
    category: "style"
  },
  {
    id: "fashion_style",
    question: "Which fashion style speaks to you?",
    type: "image_choice",
    options: [
      {
        image: "F-MIN2.png",
        text: "Modern Minimal",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.7,
          comfortable: 0.5
        }
      },
      {
        image: "F-ST2.png",
        text: "Urban Street",
        scores: {
          edgy: 0.9,
          streetwear: 0.7,
          vintage: 0.5
        }
      },
      {
        image: "F-CB2.png",
        text: "Boho Layered",
        scores: {
          bohemian: 0.9,
          romantic: 0.7,
          vintage: 0.5
        }
      },
      {
        image: "F-OM2.png",
        text: "Classic Preppy",
        scores: {
          classic: 0.9,
          sophisticated: 0.7,
          preppy: 0.5
        }
      }
    ],
    category: "aesthetic"
  },
  {
    id: "daily_activities",
    question: "What best describes your daily activities?",
    type: "multiple_choice",
    options: [
      {
        text: "Office work and meetings",
        scores: {
          professional: 0.8,
          classic: 0.6,
          sophisticated: 0.4
        }
      },
      {
        text: "Creative work and casual meetings",
        scores: {
          bohemian: 0.7,
          minimalist: 0.5,
          comfortable: 0.3
        }
      },
      {
        text: "Active lifestyle and sports",
        scores: {
          athletic: 0.8,
          streetwear: 0.6,
          comfortable: 0.4
        }
      },
      {
        text: "Mix of everything",
        scores: {
          versatile: 0.8,
          comfortable: 0.6,
          sophisticated: 0.4
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
          minimalist: 0.9,
          sophisticated: 0.6
        }
      },
      {
        text: "Rich textures and patterns",
        scores: {
          bohemian: 0.8,
          romantic: 0.6
        }
      },
      {
        text: "Classic and timeless pieces",
        scores: {
          classic: 0.9,
          preppy: 0.6
        }
      },
      {
        text: "Bold and statement pieces",
        scores: {
          edgy: 0.8,
          streetwear: 0.6
        }
      }
    ],
    category: "style"
  },
  {
    id: "color_preferences",
    question: "Which colors do you prefer to wear? (Select all that apply)",
    type: "color_choice",
    options: [
      {
        text: "Black",
        color: "#000000",
        scores: {
          color_preference: "black"
        }
      },
      {
        text: "White",
        color: "#FFFFFF",
        scores: {
          color_preference: "white"
        }
      },
      {
        text: "Navy",
        color: "#000080",
        scores: {
          color_preference: "navy"
        }
      },
      {
        text: "Gray",
        color: "#808080",
        scores: {
          color_preference: "gray"
        }
      },
      {
        text: "Charcoal",
        color: "#36454F",
        scores: {
          color_preference: "charcoal"
        }
      },
      {
        text: "Brown",
        color: "#8B4513",
        scores: {
          color_preference: "brown"
        }
      },
      {
        text: "Beige",
        color: "#F5F5DC",
        scores: {
          color_preference: "beige"
        }
      },
      {
        text: "Cream",
        color: "#FFFDD0",
        scores: {
          color_preference: "cream"
        }
      },
      {
        text: "Red",
        color: "#FF0000",
        scores: {
          color_preference: "red"
        }
      },
      {
        text: "Blue",
        color: "#0000FF",
        scores: {
          color_preference: "blue"
        }
      },
      {
        text: "Olive",
        color: "#808000",
        scores: {
          color_preference: "olive"
        }
      },
      {
        text: "Terracotta",
        color: "#E2725B",
        scores: {
          color_preference: "terracotta"
        }
      },
      {
        text: "Pink",
        color: "#FFC0CB",
        scores: {
          color_preference: "pink"
        }
      },
      {
        text: "Lavender",
        color: "#E6E6FA",
        scores: {
          color_preference: "lavender"
        }
      },
      {
        text: "Mint",
        color: "#98FB98",
        scores: {
          color_preference: "mint"
        }
      },
      {
        text: "Peach",
        color: "#FFCBA4",
        scores: {
          color_preference: "peach"
        }
      },
      {
        text: "Sky Blue",
        color: "#87CEEB",
        scores: {
          color_preference: "sky_blue"
        }
      },
      {
        text: "Burgundy",
        color: "#800020",
        scores: {
          color_preference: "burgundy"
        }
      },
      {
        text: "Emerald",
        color: "#50C878",
        scores: {
          color_preference: "emerald"
        }
      },
      {
        text: "Camel",
        color: "#C19A6B",
        scores: {
          color_preference: "camel"
        }
      }
    ],
    category: "color_preferences"
  },
  {
    id: "style_preferences",
    question: "Which style categories interest you most? (Select all that apply)",
    type: "multiple_choice",
    options: [
      {
        text: "Streetwear",
        scores: {
          style_preference: "streetwear"
        }
      },
      {
        text: "Cottagecore",
        scores: {
          style_preference: "cottagecore"
        }
      },
      {
        text: "Minimalist",
        scores: {
          style_preference: "minimalist"
        }
      },
      {
        text: "Old Money",
        scores: {
          style_preference: "old_money"
        }
      },
      {
        text: "Bohemian",
        scores: {
          style_preference: "bohemian"
        }
      },
      {
        text: "Dark Academia",
        scores: {
          style_preference: "dark_academia"
        }
      },
      {
        text: "Grunge",
        scores: {
          style_preference: "grunge"
        }
      },
      {
        text: "Y2K",
        scores: {
          style_preference: "y2k"
        }
      },
      {
        text: "Romantic",
        scores: {
          style_preference: "romantic"
        }
      },
      {
        text: "Preppy",
        scores: {
          style_preference: "preppy"
        }
      },
      {
        text: "Athletic/Sporty",
        scores: {
          style_preference: "athletic"
        }
      },
      {
        text: "Vintage",
        scores: {
          style_preference: "vintage"
        }
      }
    ],
    category: "style_preferences"
  }
];

export async function GET() {
  try {
    console.log('🔍 DEBUG: Style quiz questions API called - MOCK VERSION');
    
    // Transform backend format to frontend format
    const frontendQuestions = MOCK_QUIZ_QUESTIONS.map(question => ({
      id: question.id,
      question: question.question,
      category: question.category,
      type: question.type === "image_choice" ? "visual" : "text",
      options: question.options.map(option => option.text),
      images: question.type === "image_choice" 
        ? question.options.map(option => `/images/outfit-quiz/${option.image}`)
        : undefined
    }));

    return NextResponse.json({
      success: true,
      questions: frontendQuestions,
      message: 'Quiz questions loaded successfully (mock version)'
    });
  } catch (error) {
    console.error('Error loading quiz questions:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to load quiz questions',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
