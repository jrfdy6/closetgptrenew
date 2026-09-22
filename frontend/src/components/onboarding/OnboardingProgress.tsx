import { Check } from 'lucide-react';

export type OnboardingStage = 'style' | 'capsule' | 'first-look';

const stages: { id: OnboardingStage; label: string }[] = [
  { id: 'style', label: 'Your style' },
  { id: 'capsule', label: 'Your capsule' },
  { id: 'first-look', label: 'Your first look' },
];

/** The shared journey marker describes stages; each stage owns its real progress. */
export default function OnboardingProgress({ stage }: { stage: OnboardingStage }) {
  const current = stages.findIndex(item => item.id === stage);
  return (
    <nav aria-label="Your wardrobe setup" className="mx-auto w-full max-w-3xl py-5 sm:py-7">
      <ol className="grid grid-cols-3 gap-2 sm:gap-6">
        {stages.map((item, index) => (
          <li key={item.id} aria-current={index === current ? 'step' : undefined}
            className={`flex min-w-0 flex-col items-center gap-2 text-center sm:flex-row sm:gap-3 sm:text-left ${index <= current ? 'text-stone-900 dark:text-stone-100' : 'text-stone-500 dark:text-stone-400'}`}>
            <span aria-hidden="true" className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${index === current ? 'bg-stone-900 text-white dark:bg-amber-200 dark:text-stone-950' : index < current ? 'bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200' : 'border border-stone-300 dark:border-stone-600'}`}>
              {index < current ? <Check className="h-4 w-4" /> : index + 1}
            </span>
            <span className="text-xs font-medium sm:text-sm">
              <span className="sr-only">Step {index + 1}: </span>{item.label}
              {index < current && <span className="sr-only">, complete</span>}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  );
}
