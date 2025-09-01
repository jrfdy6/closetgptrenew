import { NextResponse } from 'next/server';

// Mock quiz questions that match the backend structure
const MOCK_QUIZ_QUESTIONS = [
  {
    id: "movie_vibe",
    question: "Which movie's aesthetic speaks to you the most?",
    type: "image_choice",
    options: [
      {
        image: "classic_hollywood.jpg",
        text: "Classic Hollywood Glamour",
        scores: {
          classic: 0.8,
          sophisticated: 0.6,
          romantic: 0.4
        }
      },
      {
        image: "indie_romance.jpg",
        text: "Indie Romance",
        scores: {
          romantic: 0.8,
          bohemian: 0.6,
          vintage: 0.4
        }
      },
      {
        image: "minimalist_scandi.jpg",
        text: "Minimalist Scandinavian",
        scores: {
          minimalist: 0.9,
          sophisticated: 0.5,
          comfortable: 0.3
        }
      },
      {
        image: "street_style.jpg",
        text: "Urban Street Style",
        scores: {
          streetwear: 0.8,
          edgy: 0.6,
          athletic: 0.4
        }
      }
    ],
    category: "aesthetic"
  },
  {
    id: "color_preference",
    question: "Which color palette feels most 'you'?",
    type: "image_choice",
    options: [
      {
        image: "warm_spring.jpg",
        text: "Warm & Fresh",
        scores: {
          warm_spring: 0.9,
          warm_autumn: 0.7
        }
      },
      {
        image: "cool_summer.jpg",
        text: "Soft & Cool",
        scores: {
          cool_summer: 0.9,
          cool_spring: 0.7
        }
      },
      {
        image: "deep_winter.jpg",
        text: "Rich & Deep",
        scores: {
          cool_winter: 0.9,
          warm_winter: 0.7
        }
      },
      {
        image: "earthy_autumn.jpg",
        text: "Earthy & Warm",
        scores: {
          warm_autumn: 0.9,
          cool_autumn: 0.7
        }
      }
    ],
    category: "color"
  },
  {
    id: "silhouette_preference",
    question: "Which silhouette do you feel most confident in?",
    type: "image_choice",
    options: [
      {
        image: "fitted.jpg",
        text: "Fitted & Structured",
        scores: {
          hourglass: 0.8,
          rectangle: 0.6
        }
      },
      {
        image: "flowy.jpg",
        text: "Flowy & Relaxed",
        scores: {
          pear: 0.8,
          apple: 0.6
        }
      },
      {
        image: "balanced.jpg",
        text: "Balanced & Proportional",
        scores: {
          rectangle: 0.8,
          hourglass: 0.6
        }
      },
      {
        image: "dramatic.jpg",
        text: "Dramatic & Statement",
        scores: {
          inverted_triangle: 0.8,
          triangle: 0.6
        }
      }
    ],
    category: "fit"
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
        ? question.options.map(option => `/quiz-images/${option.image}`)
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
