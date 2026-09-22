'use client';

import { useEffect, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { ArrowRight, CheckCircle2, Shirt } from 'lucide-react';
import { Button } from '@/components/ui/button';
import OnboardingProgress from '@/components/onboarding/OnboardingProgress';
import { WardrobeService } from '@/lib/services/wardrobeService';
import type { ClothingItem } from '@/lib/hooks/useWardrobe';
import type { QuizAnswerRecord } from '@/lib/quizAnswerContract';
import { evaluateCapsule, ownedBy } from '@/lib/onboarding/state';
import { selectedStyleNames } from '@/lib/onboarding/quizPresentation';
import { fullQuizQuestions } from '@/lib/onboarding/questions';

type RecapItem = ClothingItem & { originalImageUrl?: string; image_url?: string };
const originalPhoto = (item: RecapItem) => item.originalImageUrl || item.imageUrl || item.image_url;

interface OnboardingRecapProps {
  userId: string;
  answers: QuizAnswerRecord[];
  onManageCapsule: () => void;
  onRetake: () => void;
  hasFirstLook?: boolean;
}

/** Read-only recap. A failed or stale wardrobe read never becomes a ready/empty capsule. */
export default function OnboardingRecap({ userId, answers, onManageCapsule, onRetake, hasFirstLook = false }: OnboardingRecapProps) {
  const [attempt, setAttempt] = useState(0);
  const [result, setResult] = useState<{ userId: string; items?: ClothingItem[]; error?: string } | null>(null);
  useEffect(() => {
    let active = true;
    setResult(null);
    WardrobeService.getWardrobeItems().then(items => {
      if (active) setResult({ userId, items: items.filter(item => ownedBy(item, userId)) });
    }).catch(() => {
      if (active) setResult({ userId, error: 'We couldn’t load your saved capsule. Your photos have not been removed. Please try again.' });
    });
    return () => { active = false; };
  }, [userId, attempt]);
  const current = result?.userId === userId ? result : null;
  const capsule = current?.items ? evaluateCapsule(current.items) : null;
  const activeQuestionIds = new Set(fullQuizQuestions(answers.find(answer => answer.question_id === 'gender')?.selected_option || null).map(question => question.id));
  const styles = selectedStyleNames(answers.filter(answer => activeQuestionIds.has(answer.question_id)));
  const everyday = answers.find(answer => answer.question_id === 'daily_activities')?.selected_option;
  const details = answers.find(answer => answer.question_id === 'style_elements')?.selected_option;
  const previews = (current?.items || []).filter(item => originalPhoto(item)).slice(0, 6);

  return (
    <main className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 px-4 py-6 text-stone-900 dark:from-stone-950 dark:via-stone-900 dark:to-amber-950 dark:text-stone-100 sm:py-10">
      <div className="mx-auto max-w-3xl space-y-8">
        <OnboardingProgress stage="first-look" />
        <header className="space-y-3 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-800 dark:text-amber-300">Made from what you own</p>
          <h1 className="font-serif text-3xl sm:text-4xl">Your style. Your clothes. Your first look.</h1>
          <p className="mx-auto max-w-xl text-base text-stone-600 dark:text-stone-300">Choose an occasion and mood next. We’ll use your saved wardrobe to put a look together.</p>
        </header>
        <section aria-labelledby="capsule-recap-title" className="rounded-3xl border border-amber-200/70 bg-white/90 p-5 shadow-sm dark:border-stone-700 dark:bg-stone-900 sm:p-8">
          <div className="mb-5 flex items-start justify-between gap-3">
            <div><h2 id="capsule-recap-title" className="font-serif text-2xl">Your capsule</h2>
              {capsule && <p className="mt-1 text-sm text-stone-600 dark:text-stone-300">{capsule.usableCount} unique usable {capsule.usableCount === 1 ? 'piece' : 'pieces'} saved</p>}
            </div>
            {capsule?.ready && <span className="flex items-center gap-1.5 rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-medium text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200"><CheckCircle2 aria-hidden="true" className="h-4 w-4" />Ready</span>}
          </div>
          <div className="mb-6 space-y-3 border-b border-stone-200 pb-6 dark:border-stone-700">
            {capsule?.ready ? <Button asChild className="h-auto min-h-12 w-full whitespace-normal rounded-2xl bg-amber-700 px-6 py-3 text-base text-white hover:bg-amber-800 sm:w-auto"><Link href="/outfits/generate?onboarding=1">Create my first outfit<ArrowRight aria-hidden="true" className="ml-2 h-4 w-4 shrink-0" /></Link></Button> : <Button disabled className="min-h-12 rounded-2xl px-6">{current?.error ? 'Load your capsule to continue' : capsule ? 'Finish your capsule to continue' : 'Checking your capsule…'}</Button>}
            <p className="text-sm text-stone-600 dark:text-stone-300">You’ll review the outfit settings before creating anything.</p>
          </div>
          {!current && <p role="status" className="py-6 text-stone-600 dark:text-stone-300">Loading your saved pieces…</p>}
          {current?.error && <div className="space-y-3"><p role="alert">{current.error}</p><Button variant="outline" onClick={() => setAttempt(value => value + 1)}>Retry loading capsule</Button></div>}
          {capsule && <>
            <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
              {previews.map(item => <div key={item.id} className="relative aspect-[3/4] overflow-hidden rounded-xl bg-stone-100 dark:bg-stone-800"><Image src={originalPhoto(item)!} alt={item.name || item.type || 'Saved garment'} fill sizes="(max-width: 640px) 28vw, 100px" unoptimized className="object-contain p-1" /></div>)}
            </div>
            <p className="mt-4 text-sm text-stone-600 dark:text-stone-300">Original photos from your wardrobe. You can keep adding pieces as you go.</p>
            {!capsule.ready && <p role="status" className="mt-3 text-sm text-amber-900 dark:text-amber-200">{capsule.usableCount < 10 ? `Add ${10 - capsule.usableCount} more unique usable ${10 - capsule.usableCount === 1 ? 'piece' : 'pieces'} to reach ten. ` : ''}{!capsule.hasCoverage ? `Include ${capsule.missingCategories.join(' and ')} so we can build a complete outfit.` : ''}</p>}
            <button type="button" onClick={onManageCapsule} className="mt-4 inline-flex min-h-11 items-center gap-2 text-sm font-semibold underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-amber-700"><Shirt aria-hidden="true" className="h-4 w-4" />Review or add pieces</button>
          </>}
          <div className="mt-6 border-t border-stone-200 pt-6 dark:border-stone-700">
            <h2 className="font-serif text-xl">Your style notes</h2>
            {styles.length > 0 && <div className="mt-3 flex flex-wrap gap-2">{styles.map(style => <span key={style} className="rounded-full bg-amber-50 px-3 py-1.5 text-sm text-amber-950 dark:bg-amber-950 dark:text-amber-100">{style}</span>)}</div>}
            {everyday && <p className="mt-3 text-sm"><span className="text-stone-500 dark:text-stone-400">Your days: </span>{everyday}</p>}
            {details && <p className="mt-2 text-sm"><span className="text-stone-500 dark:text-stone-400">Drawn to: </span>{details}</p>}
            {!styles.length && !everyday && !details && <p className="mt-3 text-sm text-stone-600 dark:text-stone-300">Your saved style profile is ready to use.</p>}
            <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-sm"><Link href="/style-persona" className="inline-flex min-h-11 items-center underline underline-offset-4">View my style profile</Link><button type="button" onClick={onRetake} className="min-h-11 underline underline-offset-4">Retake my style quiz</button></div>
          </div>
        </section>
        {hasFirstLook && <div className="pb-4 text-center"><Link href="/outfits" className="inline-flex min-h-11 items-center text-sm underline underline-offset-4">Back to My Looks</Link></div>}
      </div>
    </main>
  );
}
