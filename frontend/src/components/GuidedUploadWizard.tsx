"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { ArrowRight, Check, Camera, Loader2, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { useFirebase } from '@/lib/firebase-context';
import { useOnboardingState } from '@/lib/hooks/useOnboardingState';
import { classifyGarment, evaluateCapsule, ownedBy } from '@/lib/onboarding/state';
import OnboardingProgress from '@/components/onboarding/OnboardingProgress';
import BatchImageUpload from './BatchImageUpload';

interface GuidedUploadWizardProps {
  userId: string;
  targetCount?: number;
  onComplete: (itemCount: number) => void | Promise<void>;
  stylePersona?: string;
  gender?: string;
}
type Garment = Record<string, any> & { id: string };
type Inventory = { uid: string; items: Garment[] | null; loading: boolean; error: string | null };
const categoryOptions = [
  ['unknown', 'Choose category'], ['top', 'Top'], ['bottom', 'Bottom'], ['one-piece', 'Dress or one-piece'],
  ['shoes', 'Shoes'], ['layer', 'Layer'], ['accessory', 'Accessory'],
];
const categoryType: Record<string, string> = { top: 'shirt', bottom: 'pants', 'one-piece': 'dress', shoes: 'shoes', layer: 'jacket', accessory: 'accessory' };

function processingMessage(item: Garment): string {
  if (item.processing_status === 'codex_pending') return 'Photo saved. Item details are being identified.';
  if (item.processing_status === 'failed') {
    if (item.processing_retry_action === 'replace_photo') return 'This photo could not be processed. Add a clearer replacement photo.';
    if (item.processing_retry_action === 'replace_item') return 'This item could not be processed. Add it again with a new photo.';
    return 'Cutout needs attention. Your original photo is still saved.';
  }
  if (item.processing_status === 'processing') return 'Original saved. Cutout is being prepared.';
  if (item.processing_status === 'pending') return 'Original saved. Cutout is queued.';
  return classifyGarment(item) === 'unknown' ? 'Photo saved. Choose a category so this item counts.' : 'Saved in your capsule';
}

function CapsuleItem({ item, onCategorySave, onRetry }: {
  item: Garment; onCategorySave: (id: string, type: string) => Promise<void>; onRetry: (item: Garment) => Promise<void>;
}) {
  const actualCategory = classifyGarment(item);
  const [category, setCategory] = useState(actualCategory);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { setCategory(actualCategory); }, [actualCategory]);
  const action = async (operation: () => Promise<void>) => {
    setPending(true); setError(null);
    try { await operation(); } catch (error) { setError(error instanceof Error ? error.message : 'This change was not confirmed. Please retry.'); }
    finally { setPending(false); }
  };
  const canRetry = item.processing_status === 'failed' && item.processing_retryable === true &&
    item.processing_retry_action === 'retry_item' && typeof item.processing_attempt_id === 'string' && item.processing_attempt_id.length > 0;
  return <li className="overflow-hidden rounded-2xl border border-border/70 bg-card">
    <div className="aspect-[4/3] bg-muted/40 p-3">
      <img src={item.originalImageUrl || item.imageUrl || item.image_url} alt={item.name || 'Saved clothing item'} className="h-full w-full object-contain" loading="lazy" />
    </div>
    <div className="space-y-3 p-4">
      <h3 className="break-words text-sm font-semibold">{item.name || 'Saved item'}</h3>
      <p className="min-h-10 text-xs leading-relaxed text-muted-foreground">{processingMessage(item)}</p>
      <div className="space-y-2">
        <label htmlFor={`category-${item.id}`} className="text-xs font-medium">Category</label>
        <select id={`category-${item.id}`} value={category} disabled={pending} onChange={event => setCategory(event.target.value as typeof category)} className="w-full rounded-lg border border-input bg-background p-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
          {categoryOptions.map(([value, label]) => <option key={value} value={value} disabled={value === 'unknown'}>{label}</option>)}
        </select>
        {category !== actualCategory && category !== 'unknown' && <Button size="sm" variant="outline" className="w-full" disabled={pending} onClick={() => void action(() => onCategorySave(item.id, categoryType[category]))}>{pending ? 'Saving category…' : 'Save category'}</Button>}
      </div>
      {canRetry && <Button size="sm" variant="outline" className="w-full" disabled={pending} onClick={() => void action(() => onRetry(item))}><RotateCcw aria-hidden="true" className="mr-2 h-3 w-3" />{pending ? 'Requesting retry…' : 'Retry cutout'}</Button>}
      {error && <p role="alert" className="text-xs text-destructive">{error}</p>}
    </div>
  </li>;
}

export default function GuidedUploadWizard({ userId, onComplete }: GuidedUploadWizardProps) {
  const { user } = useFirebase();
  const { state, loading: progressLoading, error: progressError, refresh } = useOnboardingState();
  const [inventory, setInventory] = useState<Inventory>({ uid: userId, items: null, loading: true, error: null });
  const [actionNotice, setActionNotice] = useState<string | null>(null);
  const [continuing, setContinuing] = useState(false);
  const [hasUnsavedItems, setHasUnsavedItems] = useState(false);
  const current = useRef({ userId, user });
  const requestSequence = useRef(0);
  current.current = { userId, user };

  const loadInventory = useCallback(async () => {
    const { user: activeUser, userId: uid } = current.current;
    const sequence = ++requestSequence.current;
    if (!activeUser || activeUser.uid !== uid) return;
    setInventory(previous => ({ uid, items: previous.uid === uid ? previous.items : null, loading: true, error: null }));
    try {
      const response = await fetch('/api/wardrobe', { headers: { Authorization: `Bearer ${await activeUser.getIdToken()}` }, cache: 'no-store' });
      const result = await response.json();
      if (!response.ok || result.success !== true || !Array.isArray(result.items)) throw new Error('Your saved capsule could not be loaded. Please retry.');
      if (sequence !== requestSequence.current || current.current.userId !== uid || current.current.user?.uid !== uid) return;
      const unique = new Map<string, Garment>();
      result.items.forEach((item: Garment) => { if (typeof item.id === 'string' && ownedBy(item, uid) && !item.deleted && !item.isDeleted && !item.deletedAt) unique.set(item.id, item); });
      setInventory({ uid, items: Array.from(unique.values()), loading: false, error: null });
    } catch {
      if (sequence === requestSequence.current && current.current.userId === uid) {
        setInventory(previous => ({ uid, items: previous.uid === uid ? previous.items : null, loading: false, error: 'Your saved capsule could not be loaded. Please retry.' }));
      }
    }
  }, []);
  const reload = useCallback(async () => { await Promise.all([loadInventory(), refresh()]); }, [loadInventory, refresh]);
  useEffect(() => {
    void loadInventory();
    return () => { requestSequence.current += 1; };
  }, [userId, user?.uid, loadInventory]);
  useEffect(() => {
    const restore = () => { if (document.visibilityState === 'visible') void reload(); };
    window.addEventListener('focus', restore);
    return () => window.removeEventListener('focus', restore);
  }, [reload]);

  // Hide the previous account synchronously, before the hydration effect runs.
  const currentInventory = inventory.uid === userId && user?.uid === userId ? inventory : null;
  const items = currentInventory?.items;
  const capsule = items ? evaluateCapsule(items) : null;
  const awaitingProcessing = items?.some(item => ['pending', 'processing', 'codex_pending'].includes(item.processing_status));
  useEffect(() => {
    if (!awaitingProcessing) return;
    const timer = window.setInterval(() => { if (document.visibilityState === 'visible') void reload(); }, 30_000);
    return () => window.clearInterval(timer);
  }, [awaitingProcessing, reload]);

  const handleItemSaved = async (saved: Garment) => {
    if (current.current.user?.uid !== userId || current.current.userId !== userId) return;
    setInventory(previous => {
      const known = new Map((previous.uid === userId ? previous.items || [] : []).map(item => [item.id, item]));
      if (ownedBy(saved, userId)) known.set(saved.id, saved);
      return { uid: userId, items: Array.from(known.values()), loading: true, error: null };
    });
    await reload();
  };
  const saveCategory = async (id: string, type: string) => {
    const activeUser = current.current.user;
    if (!activeUser || activeUser.uid !== userId) throw new Error('Please sign in again before editing this item.');
    const response = await fetch(`/api/wardrobe/${encodeURIComponent(id)}`, {
      method: 'PUT', headers: { Authorization: `Bearer ${await activeUser.getIdToken()}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ type }),
    });
    const result = await response.json();
    if (!response.ok || result.success !== true) throw new Error('The category was not confirmed saved. Please retry.');
    await reload();
  };
  const retryProcessing = async (item: Garment) => {
    const activeUser = current.current.user;
    if (!activeUser || activeUser.uid !== userId) throw new Error('Please sign in again before retrying this item.');
    const response = await fetch(`/api/wardrobe/${encodeURIComponent(item.id)}/retry-processing`, {
      method: 'POST', headers: { Authorization: `Bearer ${await activeUser.getIdToken()}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ expected_attempt_id: item.processing_attempt_id }),
    });
    const result = await response.json();
    if (!response.ok || result.success !== true) throw new Error(response.status === 409 ? 'This item has changed. Refresh your capsule to see its current status.' : 'The cutout retry was not confirmed. Please retry.');
    await reload();
  };
  const ready = Boolean(state?.capsule.ready && capsule?.ready && !progressError && !currentInventory?.error);
  const continueToFirstLook = async () => {
    setContinuing(true); setActionNotice(null);
    try {
      const confirmed = await refresh();
      if (current.current.userId !== userId || current.current.user?.uid !== userId) return;
      if (!confirmed?.capsule.ready) throw new Error('Your capsule is not ready yet. Check the saved count and missing categories.');
      await onComplete(confirmed.capsule.usableCount);
    } catch (error) {
      if (current.current.userId === userId && current.current.user?.uid === userId) {
        setActionNotice(error instanceof Error ? error.message : 'Your progress could not be confirmed. Please retry.');
      }
    } finally {
      if (current.current.userId === userId && current.current.user?.uid === userId) setContinuing(false);
    }
  };

  return <div className="min-h-screen bg-background px-4 pb-12 sm:px-6">
    <div className="mx-auto max-w-5xl">
      <OnboardingProgress stage="capsule" />
      <header className="mb-7 max-w-2xl space-y-3 pt-3">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-amber-800 dark:text-amber-300">A wardrobe that works together</p>
        <h1 className="font-serif text-3xl font-semibold tracking-tight sm:text-4xl">Start with pieces you love wearing.</h1>
        <p className="text-base leading-relaxed text-muted-foreground">Save 10 different items to build your capsule. Include tops, bottoms and shoes—or a dress or one-piece with shoes. Add them a few at a time; saved items will be here when you return.</p>
      </header>
      <div className="mb-7 rounded-2xl border border-amber-200/70 bg-amber-50/70 p-5 dark:border-amber-800/50 dark:bg-amber-950/20 sm:p-6">
        {capsule ? <>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p role="status" className="text-lg font-semibold">{capsule.usableCount} of 10 capsule items saved</p>
            {capsule.ready && <span className="flex items-center gap-1 text-sm font-medium"><Check aria-hidden="true" className="h-4 w-4" />Your essentials are covered</span>}
          </div>
          <Progress aria-label="Capsule items saved" value={Math.min(100, capsule.usableCount * 10)} className="mt-3 h-2" />
          <p className="mt-3 text-sm text-muted-foreground">{capsule.usableCount < 10 ? `${10 - capsule.usableCount} more unique items to reach your capsule.` : 'You have enough items.'} {capsule.missingCategories.length > 0 ? `Still needed: ${capsule.missingCategories.join(', ')}.` : 'You have the pieces for a complete outfit.'}</p>
          {capsule.savedCount > capsule.usableCount && <p className="mt-2 text-xs text-muted-foreground">{capsule.savedCount} records saved. Repeated photos and items awaiting a category do not add to the capsule count.</p>}
        </> : <p role="status" className="text-sm">{currentInventory?.error ? 'Saved count unavailable' : 'Loading your saved capsule…'}</p>}
        {(currentInventory?.error || progressError) && <div role="alert" className="mt-3 space-y-2 text-sm"><p>{currentInventory?.error || progressError}</p><Button variant="outline" size="sm" onClick={() => void reload()}>Retry loading capsule</Button></div>}
        {currentInventory?.loading && capsule && <p className="mt-2 text-xs text-muted-foreground">Checking saved progress…</p>}
        <div className="mt-5 flex flex-col gap-3 border-t border-amber-200/70 pt-5 dark:border-amber-800/50 sm:flex-row sm:items-center sm:justify-between">
          <p className="max-w-lg text-sm text-muted-foreground">{hasUnsavedItems ? 'Save or remove your selected photos before continuing.' : ready ? 'Your capsule is ready. Next, review your style and choose your first look.' : 'Keep adding your favorites. You can leave after items are marked saved and return to finish.'}</p>
          <Button size="lg" className="shrink-0" disabled={!ready || hasUnsavedItems || continuing || progressLoading || currentInventory?.loading} onClick={() => void continueToFirstLook()}>{continuing ? <Loader2 aria-hidden="true" className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" /> : null}Continue to my first look<ArrowRight aria-hidden="true" className="ml-2 h-4 w-4" /></Button>
        </div>
        {actionNotice && <p role="alert" className="mt-3 text-sm text-destructive">{actionNotice}</p>}
      </div>
      <div className="rounded-2xl border border-border/60 bg-card/70 p-4 sm:p-6">
        <BatchImageUpload key={userId} userId={userId} onItemSaved={handleItemSaved} onPendingChange={setHasUnsavedItems} />
        <details className="mt-5 border-t pt-4 text-sm">
          <summary className="cursor-pointer font-medium"><Camera aria-hidden="true" className="mr-2 inline h-4 w-4" />A few photo tips</summary>
          <p className="mt-3 max-w-2xl leading-relaxed text-muted-foreground">One item per photo, fully visible. A hanger or a flat surface both work. Use even light and a simple background. Your original stays saved while we prepare its cutout.</p>
        </details>
      </div>
      {items && items.length > 0 && <section aria-labelledby="saved-capsule-heading" className="mt-9">
        <div className="mb-4 flex items-center justify-between gap-3"><h2 id="saved-capsule-heading" className="text-xl font-semibold">Already in your capsule</h2><Button variant="ghost" size="sm" disabled={currentInventory?.loading} onClick={() => void reload()}><RotateCcw aria-hidden="true" className="mr-2 h-4 w-4" />Refresh</Button></div>
        <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">{items.map(item => <CapsuleItem key={item.id} item={item} onCategorySave={saveCategory} onRetry={retryProcessing} />)}</ul>
      </section>}
    </div>
  </div>;
}
