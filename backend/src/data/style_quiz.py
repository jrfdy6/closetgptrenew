from typing import List, Dict, Any
from ..custom_types.style_discovery import QuizQuestion, StyleAesthetic, ColorSeason, BodyType
import logging

STYLE_QUIZ_QUESTIONS: List[QuizQuestion] = [
    # Aesthetic Questions
    QuizQuestion(
        id="movie_vibe",
        question="Which movie's aesthetic speaks to you the most?",
        type="image_choice",
        options=[
            {
                "image": "classic_hollywood.jpg",
                "text": "Classic Hollywood Glamour",
                "scores": {
                    "classic": 0.8,
                    "sophisticated": 0.6,
                    "romantic": 0.4
                }
            },
            {
                "image": "indie_romance.jpg",
                "text": "Indie Romance",
                "scores": {
                    "romantic": 0.8,
                    "bohemian": 0.6,
                    "vintage": 0.4
                }
            },
            {
                "image": "minimalist_scandi.jpg",
                "text": "Minimalist Scandinavian",
                "scores": {
                    "minimalist": 0.9,
                    "sophisticated": 0.5,
                    "comfortable": 0.3
                }
            },
            {
                "image": "street_style.jpg",
                "text": "Urban Street Style",
                "scores": {
                    "streetwear": 0.8,
                    "edgy": 0.6,
                    "athletic": 0.4
                }
            }
        ],
        category="aesthetic"
    ),
    
    # Color Questions
    QuizQuestion(
        id="color_preference",
        question="Which color palette feels most 'you'?",
        type="image_choice",
        options=[
            {
                "image": "warm_spring.jpg",
                "text": "Warm & Fresh",
                "scores": {
                    "warm_spring": 0.9,
                    "warm_autumn": 0.7
                }
            },
            {
                "image": "cool_summer.jpg",
                "text": "Soft & Cool",
                "scores": {
                    "cool_summer": 0.9,
                    "cool_spring": 0.7
                }
            },
            {
                "image": "deep_winter.jpg",
                "text": "Rich & Deep",
                "scores": {
                    "cool_winter": 0.9,
                    "warm_winter": 0.7
                }
            },
            {
                "image": "earthy_autumn.jpg",
                "text": "Earthy & Warm",
                "scores": {
                    "warm_autumn": 0.9,
                    "cool_autumn": 0.7
                }
            }
        ],
        category="color"
    ),
    
    # Fit Questions
    QuizQuestion(
        id="silhouette_preference",
        question="Which silhouette do you feel most confident in?",
        type="image_choice",
        options=[
            {
                "image": "fitted.jpg",
                "text": "Fitted & Structured",
                "scores": {
                    "hourglass": 0.8,
                    "rectangle": 0.6
                }
            },
            {
                "image": "flowy.jpg",
                "text": "Flowy & Relaxed",
                "scores": {
                    "pear": 0.8,
                    "apple": 0.6
                }
            },
            {
                "image": "balanced.jpg",
                "text": "Balanced & Proportional",
                "scores": {
                    "rectangle": 0.8,
                    "hourglass": 0.6
                }
            },
            {
                "image": "dramatic.jpg",
                "text": "Dramatic & Statement",
                "scores": {
                    "inverted_triangle": 0.8,
                    "triangle": 0.6
                }
            }
        ],
        category="fit"
    ),
    
    # Lifestyle Questions
    QuizQuestion(
        id="daily_activities",
        question="What best describes your daily activities?",
        type="multiple_choice",
        options=[
            {
                "text": "Office work and meetings",
                "scores": {
                    "professional": 0.8,
                    "classic": 0.6,
                    "sophisticated": 0.4
                }
            },
            {
                "text": "Creative work and casual meetings",
                "scores": {
                    "bohemian": 0.7,
                    "minimalist": 0.5,
                    "comfortable": 0.3
                }
            },
            {
                "text": "Active lifestyle and sports",
                "scores": {
                    "athletic": 0.8,
                    "streetwear": 0.6,
                    "comfortable": 0.4
                }
            },
            {
                "text": "Mix of everything",
                "scores": {
                    "versatile": 0.8,
                    "comfortable": 0.6,
                    "sophisticated": 0.4
                }
            }
        ],
        category="lifestyle"
    ),
    
    # Style Preference Questions
    QuizQuestion(
        id="style_elements",
        question="Which style elements do you gravitate towards?",
        type="multiple_choice",
        options=[
            {
                "text": "Clean lines and minimal details",
                "scores": {
                    "minimalist": 0.9,
                    "sophisticated": 0.6
                }
            },
            {
                "text": "Rich textures and patterns",
                "scores": {
                    "bohemian": 0.8,
                    "romantic": 0.6
                }
            },
            {
                "text": "Classic and timeless pieces",
                "scores": {
                    "classic": 0.9,
                    "preppy": 0.6
                }
            },
            {
                "text": "Bold and statement pieces",
                "scores": {
                    "edgy": 0.8,
                    "streetwear": 0.6
                }
            }
        ],
        category="style"
    )
]

def calculate_quiz_results(answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate quiz results based on user answers."""
    aesthetic_scores = {}
    color_scores = {}
    body_type_scores = {}
    style_scores = {}
    
    for answer in answers:
        try:
            question = next(q for q in STYLE_QUIZ_QUESTIONS if q.id == answer["question_id"])
            # Case-insensitive text matching
            selected_option = next(
                o for o in question.options 
                if o["text"].lower() == answer["selected_option"].lower()
            )
            
            # Update scores based on question category
            if question.category == "aesthetic":
                for style, score in selected_option["scores"].items():
                    aesthetic_scores[style] = aesthetic_scores.get(style, 0) + score * question.weight
            
            elif question.category == "color":
                for season, score in selected_option["scores"].items():
                    color_scores[season] = color_scores.get(season, 0) + score * question.weight
            
            elif question.category == "fit":
                for body_type, score in selected_option["scores"].items():
                    body_type_scores[body_type] = body_type_scores.get(body_type, 0) + score * question.weight
            
            elif question.category == "style":
                for style, score in selected_option["scores"].items():
                    style_scores[style] = style_scores.get(style, 0) + score * question.weight
        except (StopIteration, KeyError) as e:
            logging.error(f"Error processing answer: {answer}, Error: {str(e)}")
            continue
    
    # Normalize scores
    def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
        total = sum(scores.values())
        return {k: v/total for k, v in scores.items()} if total > 0 else scores
    
    # Determine color season
    color_season = max(color_scores.items(), key=lambda x: x[1])[0] if color_scores else None
    
    # Determine body type
    body_type = max(body_type_scores.items(), key=lambda x: x[1])[0] if body_type_scores else None
    
    return {
        "aesthetic_scores": normalize_scores(aesthetic_scores),
        "color_season": color_season,
        "body_type": body_type,
        "style_preferences": normalize_scores(style_scores)
    } 