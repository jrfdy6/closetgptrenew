import { NextResponse } from 'next/server';

// Mock quiz questions that match the backend structure
const MOCK_QUIZ_QUESTIONS = [
  {
    id: "style_preference",
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
    category: "aesthetic"
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
