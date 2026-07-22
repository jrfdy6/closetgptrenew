export interface QuizAnswerRecord {
  question_id: string;
  selected_option: string;
}

export function upsertQuizAnswer(
  answers: QuizAnswerRecord[],
  questionId: string,
  selectedOption: string
): QuizAnswerRecord[] {
  const hasExistingAnswer = answers.some(answer => answer.question_id === questionId);
  if (!hasExistingAnswer) {
    return [...answers, { question_id: questionId, selected_option: selectedOption }];
  }

  return answers.map(answer =>
    answer.question_id === questionId
      ? { ...answer, selected_option: selectedOption }
      : answer
  );
}

export function ensureDefaultSkinToneAnswer(
  answers: QuizAnswerRecord[],
  questionId: string
): QuizAnswerRecord[] {
  if (answers.some(answer => answer.question_id === questionId)) {
    return answers;
  }
  return upsertQuizAnswer(answers, questionId, 'skin_tone_50');
}
