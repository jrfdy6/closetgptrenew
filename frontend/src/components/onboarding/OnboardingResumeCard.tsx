import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { OnboardingState } from '@/lib/onboarding/types';

export default function OnboardingResumeCard({ state }: { state: OnboardingState }) {
  if (state.stage === 'complete') return null;
  const style = state.stage === 'style';
  const firstLook = !style && state.capsule.ready;
  return <section aria-label="Continue your setup" className="mb-6 flex flex-col gap-5 rounded-3xl border border-amber-200/80 bg-amber-50/80 p-5 sm:flex-row sm:items-center sm:justify-between sm:p-7 dark:border-amber-800 dark:bg-amber-950/30">
    <div>
      <p className="text-xs font-semibold uppercase tracking-widest text-amber-800 dark:text-amber-200">Your wardrobe, taking shape</p>
      <h2 className="mt-2 font-serif text-2xl text-stone-900 dark:text-stone-100">{style ? 'Pick up where you left off' : firstLook ? 'Your capsule is ready for its first look' : `${state.capsule.usableCount} of 10 pieces saved`}</h2>
      <p className="mt-2 max-w-xl text-sm leading-relaxed text-stone-600 dark:text-stone-300">{style
        ? 'Continue your saved style questionnaire, then add the clothes you reach for.'
        : firstLook ? 'Choose the occasion, style and mood before we create your outfit.'
          : state.capsule.missingCategories.length ? `Add ${state.capsule.missingCategories.join(', ')} to give your outfits the essentials. Your saved pieces are waiting.` : 'Add a few more favorites whenever you’re ready. Your saved pieces are waiting.'}</p>
    </div>
    <Button asChild className="h-12 shrink-0 rounded-xl"><Link href={firstLook ? '/outfits/generate?onboarding=1' : '/onboarding'}>
      {style ? 'Continue my style profile' : firstLook ? 'Create my first outfit' : 'Continue my capsule'}<ArrowRight className="ml-2 h-4 w-4" aria-hidden="true" />
    </Link></Button>
  </section>;
}
