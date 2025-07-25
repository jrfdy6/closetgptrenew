import { QuizQuestion } from '@/types/style-quiz';

export const quizQuestions: QuizQuestion[] = [
  {
    id: 'movie_vibe',
    type: 'outfit',
    question: 'Which movie\'s aesthetic speaks to you the most?',
    options: [
      {
        id: 'o1',
        label: 'Classic Hollywood Glamour',
        imageUrl: '/quiz-images/classic-hollywood.jpg',
        styleAttributes: {
          colors: ['navy', 'white', 'gray'],
          patterns: ['solid'],
          styles: ['classic', 'sophisticated'],
          formality: 'formal',
          seasonality: ['spring', 'fall']
        }
      },
      {
        id: 'o2',
        label: 'Indie Romance',
        imageUrl: '/quiz-images/indie-romance.jpg',
        styleAttributes: {
          colors: ['earth', 'rust', 'cream'],
          patterns: ['floral', 'ethnic'],
          styles: ['romantic', 'bohemian'],
          formality: 'casual',
          seasonality: ['spring', 'summer']
        }
      },
      {
        id: 'o3',
        label: 'Minimalist Scandinavian',
        imageUrl: '/quiz-images/minimalist-scandi.jpg',
        styleAttributes: {
          colors: ['black', 'white', 'gray', 'beige'],
          patterns: ['solid', 'minimal'],
          styles: ['minimalist', 'sophisticated'],
          formality: 'casual',
          seasonality: ['spring', 'summer', 'fall', 'winter']
        }
      },
      {
        id: 'o4',
        label: 'Urban Street Style',
        imageUrl: '/quiz-images/street-style.jpg',
        styleAttributes: {
          colors: ['black', 'white', 'red'],
          patterns: ['graphic', 'minimal'],
          styles: ['streetwear', 'edgy'],
          formality: 'casual',
          seasonality: ['spring', 'summer', 'fall']
        }
      }
    ],
    nextQuestionId: 'color_preference'
  },
  {
    id: 'color_preference',
    type: 'color',
    question: 'Which color palette feels most \'you\'?',
    options: [
      {
        id: 'c1',
        label: 'Warm & Fresh',
        imageUrl: '/quiz-images/warm-spring.jpg',
        styleAttributes: {
          colors: ['coral', 'peach', 'mint', 'sage'],
          patterns: ['solid', 'floral'],
          styles: ['fresh', 'natural'],
          formality: 'casual',
          seasonality: ['spring', 'summer']
        }
      },
      {
        id: 'c2',
        label: 'Soft & Cool',
        imageUrl: '/quiz-images/cool-summer.jpg',
        styleAttributes: {
          colors: ['lavender', 'mint', 'powder-blue', 'rose'],
          patterns: ['solid', 'subtle'],
          styles: ['soft', 'romantic'],
          formality: 'casual',
          seasonality: ['spring', 'summer']
        }
      },
      {
        id: 'c3',
        label: 'Rich & Deep',
        imageUrl: '/quiz-images/deep-winter.jpg',
        styleAttributes: {
          colors: ['navy', 'burgundy', 'emerald', 'plum'],
          patterns: ['solid', 'rich'],
          styles: ['sophisticated', 'elegant'],
          formality: 'formal',
          seasonality: ['fall', 'winter']
        }
      },
      {
        id: 'c4',
        label: 'Earthy & Warm',
        imageUrl: '/quiz-images/earthy-autumn.jpg',
        styleAttributes: {
          colors: ['olive', 'rust', 'terracotta', 'mustard'],
          patterns: ['solid', 'natural'],
          styles: ['earthy', 'natural'],
          formality: 'casual',
          seasonality: ['fall', 'winter']
        }
      }
    ],
    nextQuestionId: 'silhouette_preference'
  },
  {
    id: 'silhouette_preference',
    type: 'style',
    question: 'Which silhouette do you feel most confident in?',
    options: [
      {
        id: 'f1',
        label: 'Fitted & Structured',
        imageUrl: '/quiz-images/fitted.jpg',
        styleAttributes: {
          colors: ['navy', 'black', 'gray'],
          patterns: ['solid', 'subtle'],
          styles: ['structured', 'elegant'],
          formality: 'formal',
          seasonality: ['spring', 'summer', 'fall', 'winter']
        }
      },
      {
        id: 'f2',
        label: 'Flowy & Relaxed',
        imageUrl: '/quiz-images/flowy.jpg',
        styleAttributes: {
          colors: ['earth', 'cream', 'sage'],
          patterns: ['flowy', 'soft'],
          styles: ['relaxed', 'comfortable'],
          formality: 'casual',
          seasonality: ['spring', 'summer']
        }
      },
      {
        id: 'f3',
        label: 'Balanced & Proportional',
        imageUrl: '/quiz-images/balanced.jpg',
        styleAttributes: {
          colors: ['navy', 'khaki', 'white'],
          patterns: ['solid', 'balanced'],
          styles: ['balanced', 'proportional'],
          formality: 'casual',
          seasonality: ['spring', 'summer', 'fall', 'winter']
        }
      },
      {
        id: 'f4',
        label: 'Dramatic & Statement',
        imageUrl: '/quiz-images/dramatic.jpg',
        styleAttributes: {
          colors: ['black', 'red', 'gold'],
          patterns: ['bold', 'dramatic'],
          styles: ['dramatic', 'statement'],
          formality: 'formal',
          seasonality: ['fall', 'winter']
        }
      }
    ]
  }
]; 