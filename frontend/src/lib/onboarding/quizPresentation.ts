import { QUIZ_QUESTIONS, type QuizQuestion } from './questions';
import type { QuizAnswerRecord } from '@/lib/quizAnswerContract';

/** Presentation metadata only: the question/option catalog and stored values stay unchanged. */
export function quizSection(question: QuizQuestion) {
  if (question.id.startsWith('category_spend_')) return {
    id: 'spending', title: 'Your wardrobe habits',
    description: 'Share what you usually invest in each category to round out your style profile.',
  };
  if (question.type === 'visual_yesno') return {
    id: 'inspiration', title: 'What catches your eye',
    description: 'React to each look. There is no right answer, and you can like more than one style.',
  };
  if (question.id === 'daily_activities' || question.id === 'style_elements') return {
    id: 'everyday', title: 'Style for your everyday',
    description: 'Connect the looks you like with the way you actually spend your days.',
  };
  return {
    id: 'fit', title: 'A little about you',
    description: 'Build a profile around your fit and preferences. Optional details can stay private.',
  };
}

export function quizQuestionHint(question: QuizQuestion): string | null {
  if (question.id === 'height') return 'Height is shown in feet and inches.';
  if (question.id === 'weight') return 'Optional · Ranges are in pounds (lbs). Choose “Prefer not to specify” to leave this private.';
  if (question.id === 'cup_size') return 'Optional · Choose “Prefer not to say” to leave this private.';
  if (question.id.startsWith('shoe_size')) return question.id === 'shoe_size_female'
    ? 'US women’s shoe sizes. Choose “Prefer not to say” if you are unsure.'
    : question.id === 'shoe_size_male'
      ? 'US men’s shoe sizes. Choose “Prefer not to say” if you are unsure.'
      : 'Use your usual US numeric shoe size, or choose “Prefer not to say” if you are unsure.';
  if (question.id.startsWith('category_spend_')) return 'Amounts are in dollars per year, for this category. Your best estimate is fine.';
  if (question.type === 'rgb_slider') return 'Adjust the slider, or keep the current selection. Use the arrow keys for small changes.';
  if (question.type === 'visual') return 'Choose the description that feels closest to you.';
  return null;
}

export function selectedStyleNames(answers: readonly QuizAnswerRecord[]): string[] {
  return Array.from(new Set(answers.flatMap(answer => {
    const question = QUIZ_QUESTIONS.find(item => item.id === answer.question_id);
    return answer.selected_option === 'Yes' && question?.type === 'visual_yesno' && question.style_name
      ? [question.style_name] : [];
  })));
}
