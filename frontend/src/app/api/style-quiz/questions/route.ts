import { NextResponse } from 'next/server';

// Mock quiz questions that match the backend structure
const MOCK_QUIZ_QUESTIONS = [
  {
    id: "style_preference",
    question: "Which style resonates with you most?",
    type: "image_choice",
    options: [
      {
        image: "street.jpeg",
        text: "Street Style",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      },
      {
        image: "cottagecore_floral_dress.jpg",
        text: "Cottagecore",
        scores: {
          romantic: 0.8,
          bohemian: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "coastal.jpeg",
        text: "Coastal Chic",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      },
      {
        image: "darkacad.jpeg",
        text: "Dark Academia",
        scores: {
          classic: 0.8,
          sophisticated: 0.6,
          romantic: 0.4
        }
      }
    ],
    category: "aesthetic"
  },
  {
    id: "outfit_style",
    question: "Which outfit style appeals to you most?",
    type: "image_choice",
    options: [
      {
        image: "streetwear_oversized_hoodie.jpg",
        text: "Streetwear",
        scores: {
          streetwear: 0.9,
          edgy: 0.7,
          athletic: 0.5
        }
      },
      {
        image: "boho_flowy_dress.jpg",
        text: "Bohemian",
        scores: {
          bohemian: 0.9,
          romantic: 0.7,
          vintage: 0.5
        }
      },
      {
        image: "coastal_chic_linen_set.jpg",
        text: "Coastal Chic",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.7,
          comfortable: 0.5
        }
      },
      {
        image: "old_money_tweed_suit.jpg",
        text: "Old Money",
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
        image: "minimal_clean_blazer.jpg",
        text: "Minimalist",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.7,
          comfortable: 0.5
        }
      },
      {
        image: "grunge_flannel_combat.jpg",
        text: "Grunge",
        scores: {
          edgy: 0.9,
          streetwear: 0.7,
          vintage: 0.5
        }
      },
      {
        image: "y2k_crop_top_set.jpg",
        text: "Y2K",
        scores: {
          edgy: 0.9,
          streetwear: 0.7,
          athletic: 0.5
        }
      },
      {
        image: "romantic_lace_blouse.jpg",
        text: "Romantic",
        scores: {
          romantic: 0.9,
          bohemian: 0.7,
          vintage: 0.5
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
        ? question.options.map(option => {
            // Use the correct directory based on image type
            if (option.image.includes('_')) {
              return `/images/outfit-quiz/${option.image}`;
            } else {
              return `/images/styles/${option.image}`;
            }
          })
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
