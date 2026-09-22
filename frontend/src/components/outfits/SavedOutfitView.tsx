'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { User } from 'firebase/auth';
import OutfitResultsDisplay from '@/components/ui/outfit-results-display';
import { Button } from '@/components/ui/button';
import { extractFlatLayState } from '@/lib/flatLayState';
import { requestFlatLay } from '@/lib/services/flatLayService';
import { subscriptionService } from '@/lib/services/subscriptionService';
import { mapRoleToPlan } from '@/types/subscription';
import { FLATLAY_WEEKLY_LIMITS } from '@/utils/flatLayConfig';
import { hasOutfitCoverage } from '@/lib/onboarding/state';
import { readSavedOutfit, savedOutfitRequest, SavedOutfitError, type SavedOutfit, localDay, savedDate, wearOperationKey, clearWearOperation } from '@/lib/savedOutfit';

type Rating = { rating: number; isLiked: boolean; isDisliked: boolean; feedback: string };
const emptyRating: Rating = { rating: 0, isLiked: false, isDisliked: false, feedback: '' };
const pendingPreview = (outfit: SavedOutfit) => ['pending', 'processing', 'queued'].includes(extractFlatLayState(outfit).status);
const message = (error: unknown, fallback: string) => error instanceof Error ? error.message : fallback;

export default function SavedOutfitView({ id, user, authLoading = false }: { id: string; user: User | null; authLoading?: boolean }) {
  const router = useRouter();
  const key = (user?.uid || '') + ':' + id;
  const activeKey = useRef(key);
  activeKey.current = key;
  const mounted = useRef(true);
  const mutationRevision = useRef(0);
  useEffect(() => { mounted.current = true; return () => { mounted.current = false; }; }, []);
  const current = (requestKey: string) => mounted.current && activeKey.current === requestKey;
  const [saved, setSaved] = useState<{ key: string; outfit: SavedOutfit } | null>(null);
  const [loadError, setLoadError] = useState<{ key: string; message: string; status?: number } | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [version, setVersion] = useState(0);
  const [usageVersion, setUsageVersion] = useState(0);
  const [usage, setUsage] = useState<{ tier: string; limit: number; used: number; remaining: number } | null>(null);
  const [usageLoading, setUsageLoading] = useState(false);
  const [balanceError, setBalanceError] = useState<string | null>(null);
  const [flatError, setFlatError] = useState<string | null>(null);
  const [flatPending, setFlatPending] = useState(false);
  const [wearPending, setWearPending] = useState(false);
  const [wearError, setWearError] = useState<string | null>(null);
  const [wearNotice, setWearNotice] = useState<string | null>(null);
  const [favoritePending, setFavoritePending] = useState(false);
  const [favoriteError, setFavoriteError] = useState<string | null>(null);
  const [rating, setRating] = useState<Rating>(emptyRating);
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [feedbackPending, setFeedbackPending] = useState(false);
  const [feedbackError, setFeedbackError] = useState<string | null>(null);
  const actions = useRef(new Set<string>());
  const favoriteDesired = useRef<boolean | null>(null);
  const creditIdentity = useRef<{ key: string; value: string } | null>(null);
  const hydratedRating = useRef<string | null>(null);
  const outfit = saved?.key === key ? saved.outfit : null;
  const error = loadError?.key === key ? loadError : null;

  useEffect(() => {
    actions.current.clear(); favoriteDesired.current = null; hydratedRating.current = null;
    setUsage(null); setBalanceError(null); setFlatError(null); setWearError(null); setWearNotice(null); setFavoriteError(null);
    setFlatPending(false); setWearPending(false); setFavoritePending(false); setFeedbackPending(false);
    setRating(emptyRating); setRatingSubmitted(false); setFeedbackError(null);
  }, [key]);

  useEffect(() => {
    if (!user) return;
    let disposed = false;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | undefined;
    let wasPending = false;
    const refresh = async () => {
      setRefreshing(true);
      try {
        const token = await user.getIdToken();
        if (disposed || !current(key)) return;
        const revision = mutationRevision.current;
        const result = await readSavedOutfit(id, user.uid, token, controller.signal);
        if (disposed || !current(key) || revision !== mutationRevision.current) return;
        const settlement = result.flat_lay_request_id + ':' + result.flat_lay_credit_status;
        if (creditIdentity.current?.key === key && creditIdentity.current.value !== settlement) setUsageVersion(value => value + 1);
        creditIdentity.current = { key, value: settlement };
        setSaved({ key, outfit: result }); setLoadError(null);
        if (hydratedRating.current !== key) {
          setRating({ rating: result.rating || 0, isLiked: result.isLiked === true, isDisliked: result.isDisliked === true, feedback: result.feedback || '' });
          setRatingSubmitted(Boolean(result.rating || result.isLiked || result.isDisliked || result.feedback));
          hydratedRating.current = key;
        }
        wasPending = pendingPreview(result);
      } catch (err) {
        if (disposed || !current(key)) return;
        if (err instanceof SavedOutfitError && [401, 403, 404].includes(err.status)) setSaved(null);
        setLoadError({ key, message: message(err, 'Your saved outfit could not be loaded.'), status: err instanceof SavedOutfitError ? err.status : undefined });
      } finally {
        if (!disposed && current(key)) {
          setRefreshing(false);
          if (wasPending) timer = setTimeout(refresh, 5000);
        }
      }
    };
    refresh();
    return () => { disposed = true; controller.abort(); if (timer) clearTimeout(timer); };
  }, [id, user?.uid, version]);

  useEffect(() => {
    if (!user) return;
    let active = true;
    setUsageLoading(true);
    subscriptionService.getCurrentSubscription(user).then(subscription => {
      if (!active || !current(key)) return;
      const tier = mapRoleToPlan(subscription.role);
      const limit = FLATLAY_WEEKLY_LIMITS[tier] ?? 1;
      const remaining = subscription.flatlays_remaining ?? 0;
      setUsage({ tier, limit, used: Math.max(0, limit - remaining), remaining });
      setBalanceError(null);
    }).catch(() => { if (active && current(key)) setBalanceError('Unable to load your flatlay balance. Refresh to try again.'); })
      .finally(() => { if (active && current(key)) setUsageLoading(false); });
    return () => { active = false; };
  }, [user?.uid, id, usageVersion]);

  const refresh = () => { setVersion(value => value + 1); setUsageVersion(value => value + 1); };
  const begin = (name: string) => { if (actions.current.has(name)) return false; actions.current.add(name); return true; };
  const requestPreview = async () => {
    if (!user || !outfit || !begin('flatlay')) return;
    setFlatPending(true); setFlatError(null);
    try {
      const token = await user.getIdToken();
      if (!current(key)) return;
      await requestFlatLay(id, token);
      if (current(key)) refresh();
    } catch (err) {
      if (current(key)) { setFlatError(message(err, 'We could not confirm the preview request. Refresh its status before trying again.')); setVersion(value => value + 1); }
    } finally { if (current(key)) { actions.current.delete('flatlay'); setFlatPending(false); } }
  };
  const wear = async () => {
    if (!user || !outfit || !begin('wear')) return;
    setWearPending(true); setWearError(null); setWearNotice(null);
    try {
      const operationKey = wearOperationKey(user.uid, id);
      const token = await user.getIdToken();
      if (!current(key)) return;
      const result = await savedOutfitRequest(encodeURIComponent(id) + '/worn', token, { method: 'POST', body: JSON.stringify({ idempotency_key: operationKey, timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' }) });
      if (result?.success !== true || result.outfit_id !== id || !Number.isInteger(result.wear_count) || !result.event_id) throw new Error('We could not confirm the wear record. Retry to check the same action.');
      if (!current(key)) return;
      mutationRevision.current += 1;
      clearWearOperation(user.uid, id);
      setSaved(previous => previous?.key === key ? { key, outfit: { ...previous.outfit, wearCount: result.wear_count, lastWorn: result.last_worn, lastWearDate: result.last_wear_date, lastWearTimezone: result.last_wear_timezone } } : previous);
      setWearNotice('Wear recorded for ' + result.wear_date + '.');
      setVersion(value => value + 1);
      window.dispatchEvent(new CustomEvent('outfitWorn', { detail: { outfitId: id, wearCount: result.wear_count } }));
    } catch (err) { if (current(key)) setWearError(message(err, 'We could not confirm the wear record. Retry to check the same action.')); }
    finally { if (current(key)) { actions.current.delete('wear'); setWearPending(false); } }
  };
  const favorite = async () => {
    if (!user || !outfit || !begin('favorite')) return;
    const desired = favoriteDesired.current ?? !outfit.isFavorite;
    favoriteDesired.current = desired;
    setFavoritePending(true); setFavoriteError(null);
    try {
      const token = await user.getIdToken();
      if (!current(key)) return;
      const result = await savedOutfitRequest(encodeURIComponent(id) + '/favorite', token, { method: 'PUT', body: JSON.stringify({ isFavorite: desired }) });
      if (result?.isFavorite !== desired) throw new Error('We could not confirm the favorite update. Please retry.');
      if (!current(key)) return;
      mutationRevision.current += 1;
      setSaved(previous => previous?.key === key ? { key, outfit: { ...previous.outfit, isFavorite: desired } } : previous);
      favoriteDesired.current = null;
      setVersion(value => value + 1);
    } catch (err) { if (current(key)) setFavoriteError(message(err, 'Favorite could not be saved. Please retry.')); }
    finally { if (current(key)) { actions.current.delete('favorite'); setFavoritePending(false); } }
  };
  const saveFeedback = async () => {
    if (!user || !outfit || !begin('feedback')) return;
    setFeedbackPending(true); setFeedbackError(null);
    try {
      const token = await user.getIdToken();
      if (!current(key)) return;
      await savedOutfitRequest('rate', token, { method: 'POST', body: JSON.stringify({ outfitId: id, ...(rating.rating ? { rating: rating.rating } : {}), isLiked: rating.isLiked, isDisliked: rating.isDisliked, feedback: rating.feedback }) });
      if (current(key)) setRatingSubmitted(true);
    } catch (err) { if (current(key)) setFeedbackError(message(err, 'Feedback could not be saved. Please retry.')); }
    finally { if (current(key)) { actions.current.delete('feedback'); setFeedbackPending(false); } }
  };

  if (authLoading) return <p role="status" className="p-8 text-center">Loading your saved look…</p>;
  if (!user) return <div className="rounded-3xl border bg-card p-8 text-center"><h1 className="font-display text-3xl">Your look is saved</h1><p className="my-4">Sign in to view your private wardrobe and saved outfits.</p><Link href={'/signin?redirect=' + encodeURIComponent('/outfits/' + id)}>Sign in</Link></div>;
  if (!outfit) return <div role={error ? 'alert' : 'status'} className="rounded-3xl border bg-card p-8 text-center"><p>{error?.message || 'Opening your saved look…'}</p>{error && <Button variant="outline" onClick={refresh} className="mt-4">Try again</Button>}</div>;
  const canWear = outfit.items_available !== false && hasOutfitCoverage(outfit.items);
  const wornToday = outfit.lastWorn != null && localDay(outfit.lastWorn) === localDay();
  return <div className="space-y-4">
    <div className="flex flex-wrap items-center justify-between gap-3 text-sm text-muted-foreground"><Link href="/outfits" className="underline underline-offset-4">Back to My Looks</Link><span>Saved to My Looks</span></div>
    {!canWear && <p role="status" className="rounded-xl border p-4">Some pieces are unavailable or this earlier look is incomplete. You can still view it and create another outfit from your current wardrobe.</p>}
    {flatError && <div role="alert" className="rounded-xl border p-4 text-sm"><p>{flatError}</p><Button variant="outline" onClick={() => { setFlatError(null); refresh(); }} disabled={refreshing} className="mt-2 min-h-11">Refresh status</Button></div>}
    {wearNotice && <p role="status" className="text-sm text-muted-foreground">{wearNotice}</p>}
    <OutfitResultsDisplay outfit={outfit} liveUpdates={false} onRefresh={refresh} refreshPending={refreshing} updatesError={error?.message}
      rating={rating} ratingSubmitted={ratingSubmitted} onRatingChange={value => setRating(previous => ({ ...previous, rating: value }))}
      onLikeToggle={() => setRating(previous => ({ ...previous, isLiked: !previous.isLiked, isDisliked: false }))}
      onDislikeToggle={() => setRating(previous => ({ ...previous, isDisliked: !previous.isDisliked, isLiked: false }))}
      onFeedbackChange={value => setRating(previous => ({ ...previous, feedback: value }))}
      onSaveFeedback={saveFeedback} feedbackPending={feedbackPending} feedbackError={feedbackError}
      onWearOutfit={wear} canWear={canWear} wearPending={wearPending} wearError={wearError}
      wearCount={outfit.wearCount ?? 0} lastWornAt={savedDate(outfit.lastWorn)?.toISOString() ?? null} isWorn={wornToday}
      isFavorite={outfit.isFavorite} onFavoriteToggle={favorite} favoritePending={favoritePending} favoriteError={favoriteError}
      onRegenerate={() => router.push('/outfits/generate')} onViewOutfits={() => router.push('/outfits')}
      flatLayUsage={usage} flatLayLoading={usageLoading} flatLayError={balanceError} onRequestFlatLay={canWear ? requestPreview : undefined}
      flatLayActionLoading={flatPending} hasFlatLayCredits={Boolean(usage && usage.remaining > 0)} />
  </div>;
}
