import type { QuizAnswerRecord } from '@/lib/quizAnswerContract';

export interface OnboardingDraft {
  answers: QuizAnswerRecord[];
  currentQuestionId: string | null;
}

export interface CapsuleReadiness {
  savedCount: number;
  usableCount: number;
  minimum: 10;
  hasCoverage: boolean;
  missingCategories: string[];
  ready: boolean;
}

export interface OnboardingState {
  schemaVersion: 1;
  revision: number;
  draft: OnboardingDraft;
  profileComplete: boolean;
  capsule: CapsuleReadiness;
  stage: 'style' | 'capsule' | 'first-look' | 'complete';
  milestones: {
    styleCompletedAt: string | null;
    capsuleCompletedAt: string | null;
    firstOutfitId: string | null;
  };
}

export interface OnboardingPatch {
  expectedRevision: number;
  draft: OnboardingDraft;
}

/** Save acknowledgements intentionally omit wardrobe/history scans per answer. */
export type OnboardingDraftState = Pick<OnboardingState, 'schemaVersion' | 'revision' | 'draft' | 'milestones'>;
