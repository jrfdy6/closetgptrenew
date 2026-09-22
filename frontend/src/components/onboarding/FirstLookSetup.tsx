'use client';

import type { ComponentProps } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import OutfitGenerationBottomSheet from '@/components/outfits/OutfitGenerationBottomSheet';
import { useOnboardingState } from '@/lib/hooks/useOnboardingState';

type Props = Omit<ComponentProps<typeof OutfitGenerationBottomSheet>, 'inline' | 'open' | 'onClose'>;

/** Entry from capsule completion must still verify the currently saved progress. */
export default function FirstLookSetup(props: Props) {
  const { state, loading, error, refresh } = useOnboardingState();
  if (loading && !state) return <p role="status" className="py-8 text-center text-muted-foreground">Loading your saved capsule…</p>;
  if (error) return <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-6 text-red-900 dark:border-red-900 dark:bg-red-950 dark:text-red-100">
    <p>{error}</p><Button variant="outline" onClick={() => void refresh()} className="mt-3">Retry saved progress</Button>
  </div>;
  if (!state?.profileComplete || !state.capsule.ready) return <div className="rounded-3xl border border-stone-200 bg-white p-6 dark:border-stone-700 dark:bg-stone-900">
    <h2 className="font-serif text-2xl">{state?.profileComplete ? 'Your capsule needs a few essentials' : 'Let’s finish your style profile'}</h2>
    <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{state?.profileComplete
      ? 'Keep the pieces you’ve saved and add what’s missing before creating your first look.'
      : 'Your saved answers are waiting. Finish the full questionnaire, then build your capsule.'}</p>
    <Button asChild className="mt-5"><Link href="/onboarding">{state?.profileComplete ? 'Continue my capsule' : 'Continue my style profile'}</Link></Button>
  </div>;
  return <OutfitGenerationBottomSheet {...props} disabled={props.disabled || loading} inline open onClose={() => undefined} />;
}
