'use client';

import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Calendar, Check, ChevronDown, RefreshCw, Shirt, Star, ThumbsDown, ThumbsUp } from 'lucide-react';
import FlatLayViewer from '../FlatLayViewer';
import { extractFlatLayState, validStylingScore, type FlatLaySource } from '@/lib/flatLayState';

export interface GeneratedOutfit extends FlatLaySource {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score?: number | null;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    thumbnailUrl?: string;
    backgroundRemovedUrl?: string;
    color: string;
    reason?: string;
  }>;
  reasoning?: string;
  createdAt?: string;
  outfitAnalysis?: Record<string, unknown>;
}

interface OutfitResultsDisplayProps {
  outfit: GeneratedOutfit;
  rating: { rating: number; isLiked: boolean; isDisliked: boolean; feedback?: string };
  onRatingChange: (rating: number) => void;
  onLikeToggle: () => void;
  onDislikeToggle: () => void;
  onFeedbackChange: (feedback: string) => void;
  onWearOutfit: () => void;
  onRegenerate: () => void;
  onViewOutfits: () => void;
  ratingSubmitted: boolean;
  isWorn?: boolean;
  flatLayUsage?: { tier: string; limit: number | null; used: number; remaining: number | null } | null;
  flatLayLoading?: boolean;
  flatLayError?: string | null;
  onRequestFlatLay?: () => void;
  onSkipFlatLay?: () => void;
  flatLayActionLoading?: boolean;
  hasFlatLayCredits?: boolean;
}

function text(value: unknown): string | null {
  return typeof value === 'string' && value.trim() ? value : null;
}

export default function OutfitResultsDisplay({
  outfit, rating, onRatingChange, onLikeToggle, onDislikeToggle, onFeedbackChange,
  onWearOutfit, onRegenerate, onViewOutfits, ratingSubmitted, isWorn = false,
  flatLayUsage = null, flatLayLoading = false, flatLayError = null,
  onRequestFlatLay, onSkipFlatLay, flatLayActionLoading = false, hasFlatLayCredits = false,
}: OutfitResultsDisplayProps) {
  const initial = extractFlatLayState(outfit);
  const [flatLay, setFlatLay] = useState(initial);
  const [updatesUnavailable, setUpdatesUnavailable] = useState(false);
  const [listenerVersion, setListenerVersion] = useState(0);
  const [waitingLonger, setWaitingLonger] = useState(false);

  useEffect(() => {
    setFlatLay({ url: initial.url, status: initial.status, error: initial.error, requestAllowed: initial.requestAllowed });
  }, [outfit.id, initial.url, initial.status, initial.error, initial.requestAllowed]);

  useEffect(() => {
    setUpdatesUnavailable(false);
    if (!outfit.id) return;
    let disposed = false;
    let unsubscribe: (() => void) | undefined;
    (async () => {
      try {
        const [{ db }, { doc, onSnapshot }] = await Promise.all([
          import('@/lib/firebase/config'), import('firebase/firestore'),
        ]);
        if (disposed) return;
        unsubscribe = onSnapshot(doc(db, 'outfits', outfit.id), snapshot => {
          if (disposed) return;
          if (!snapshot.exists()) {
            setUpdatesUnavailable(true);
            return;
          }
          setFlatLay(extractFlatLayState(snapshot.data()));
          setUpdatesUnavailable(false);
        }, () => { if (!disposed) setUpdatesUnavailable(true); });
      } catch {
        if (!disposed) setUpdatesUnavailable(true);
      }
    })();
    return () => { disposed = true; unsubscribe?.(); };
  }, [outfit.id, listenerVersion]);

  useEffect(() => {
    setWaitingLonger(false);
    if (!['pending', 'processing', 'queued'].includes(flatLay.status)) return;
    // A session-only waiting message, not a claim that the server job timed out.
    const timer = setTimeout(() => setWaitingLonger(true), 90000);
    return () => clearTimeout(timer);
  }, [outfit.id, flatLay.status]);

  const score = validStylingScore(outfit.confidence_score);
  const reasoning = text(outfit.reasoning);
  const insights = Object.entries(outfit.outfitAnalysis ?? {}).flatMap(([key, value]) => {
    const insight = value && typeof value === 'object' ? text((value as Record<string, unknown>).insight) : null;
    return insight ? [{ key, insight }] : [];
  });
  const itemReasons = outfit.items.filter(item => text(item.reason));
  const hasNotes = Boolean(reasoning || insights.length || itemReasons.length || score !== null);
  const weather = outfit.weather ?? outfit.metadata?.weather;
  const temperature = weather && typeof weather === 'object' ? (weather as Record<string, unknown>).temperature : null;
  const weatherEstimated = weather && typeof weather === 'object' && Boolean((weather as Record<string, unknown>).fallback);

  return (
    <section aria-label="Your outfit" className="overflow-hidden rounded-[2rem] border border-border/60 bg-card shadow-sm">
      <header className="px-5 pb-6 pt-7 sm:px-8 sm:pt-8">
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-[0.2em] text-muted-foreground">Selected from your wardrobe</p>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <h2 className="break-words font-display text-3xl font-medium tracking-tight text-foreground sm:text-4xl">{outfit.name}</h2>
            <div className="mt-4 flex flex-wrap items-center gap-2">
              {[outfit.occasion, outfit.style, outfit.mood].filter(Boolean).map((label, index) => (
                <Badge key={`${index}-${label}`} variant="outline" className="border-border/60 px-3 py-1 font-normal">{label}</Badge>
              ))}
              {typeof temperature === 'number' && Number.isFinite(temperature) && (
                <span className="text-xs text-muted-foreground">{weatherEstimated ? 'Estimated context: ' : 'Weather context: '}{temperature}°F</span>
              )}
            </div>
          </div>
          {isWorn && <span role="status" className="flex items-center gap-2 text-sm text-muted-foreground"><Check className="h-4 w-4" />Marked as worn</span>}
        </div>
      </header>

      <div className="grid gap-8 px-5 pb-7 sm:px-8 sm:pb-8 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] lg:gap-10">
        <div className="min-w-0">
          <FlatLayViewer
            flatLayUrl={flatLay.url} outfitName={outfit.name} outfitItems={outfit.items}
            status={waitingLonger ? 'delayed' : flatLay.status} error={flatLay.error}
            requestAllowed={flatLay.requestAllowed}
            flatLayUsage={flatLayUsage} flatLayLoading={flatLayLoading} flatLayError={flatLayError}
            onRequestFlatLay={onRequestFlatLay} onSkipFlatLay={onSkipFlatLay}
            flatLayActionLoading={flatLayActionLoading} hasFlatLayCredits={hasFlatLayCredits}
          />
          {updatesUnavailable && (
            <div role="status" className="mt-3 rounded-xl border border-border p-3 text-sm text-muted-foreground">
              Live preview updates are unavailable. Your outfit pieces are still here.
              <button className="ml-2 underline underline-offset-4" onClick={() => setListenerVersion(value => value + 1)}>Reconnect</button>
            </div>
          )}
        </div>

        <div className="flex min-w-0 flex-col gap-7">
          <div className={`order-2 lg:order-1 ${flatLay.url ? '' : 'hidden lg:block'}`}>
            <div className="mb-4 flex items-baseline justify-between gap-3">
              <h3 className="text-lg font-medium">The pieces</h3>
              <span className="text-xs text-muted-foreground">{outfit.items.length} from your closet</span>
            </div>
            <ul className="divide-y divide-border/60">
              {outfit.items.map((item, index) => (
                <li key={`${item.id}-${index}`} className="flex items-start gap-4 py-3.5 first:pt-0">
                  <span className="pt-1 text-xs tabular-nums text-muted-foreground">{String(index + 1).padStart(2, '0')}</span>
                  <div className="min-w-0">
                    <p className="break-words text-sm font-medium leading-relaxed">{item.name}</p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{[item.color, item.type].filter(Boolean).join(' · ')}</p>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="order-1 space-y-2 lg:order-2">
            <Button onClick={isWorn ? onViewOutfits : onWearOutfit} className="h-12 w-full rounded-xl">
              {isWorn ? <Shirt className="mr-2 h-4 w-4" /> : <Calendar className="mr-2 h-4 w-4" />}
              {isWorn ? 'View My Looks' : 'Wear this outfit'}
            </Button>
            <div className="grid grid-cols-2 gap-2">
              <Button variant="outline" onClick={onRegenerate} className="h-11 rounded-xl"><RefreshCw className="mr-2 h-4 w-4" />Try another</Button>
              <Button variant="ghost" onClick={onViewOutfits} className="h-11 rounded-xl">My Looks</Button>
            </div>
          </div>

          {hasNotes && (
            <details className="group order-3 border-t border-border/60 pt-4">
              <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium">
                Styling notes<ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
              </summary>
              <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted-foreground">
                {reasoning && <p>{reasoning}</p>}
                {insights.map(({ key, insight }) => <p key={key}>{insight}</p>)}
                {itemReasons.map(item => <p key={item.id}><span className="font-medium text-foreground">{item.name}: </span>{item.reason}</p>)}
                {score !== null && <p className="text-xs">Styling score: {Math.round(score * 100)}/100 · Internal ranking score</p>}
              </div>
            </details>
          )}

          <details className="group order-4 border-t border-border/60 pt-4">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-3 text-sm font-medium">
              {ratingSubmitted ? 'Feedback saved' : 'How does this feel?'}
              <ChevronDown className="h-4 w-4 transition-transform group-open:rotate-180" />
            </summary>
            <div className="mt-4 space-y-4">
              <p className="text-sm text-muted-foreground">Optional feedback for future suggestions.</p>
              <div role="group" aria-label="Rate this outfit" className="flex gap-1">
                {[1, 2, 3, 4, 5].map(star => <button key={star} aria-label={`Rate ${star} ${star === 1 ? 'star' : 'stars'}`} aria-pressed={star === rating.rating} disabled={ratingSubmitted} onClick={() => onRatingChange(star)} className="rounded-lg p-2 text-primary focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:opacity-60"><Star className={`h-6 w-6 ${star <= rating.rating ? 'fill-current' : ''}`} /></button>)}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" aria-pressed={rating.isLiked} onClick={onLikeToggle} disabled={ratingSubmitted}><ThumbsUp className="mr-2 h-4 w-4" />{rating.isLiked ? 'Liked' : 'Like'}</Button>
                <Button variant="outline" size="sm" aria-pressed={rating.isDisliked} onClick={onDislikeToggle} disabled={ratingSubmitted}><ThumbsDown className="mr-2 h-4 w-4" />{rating.isDisliked ? 'Disliked' : 'Not for me'}</Button>
              </div>
              <label className="block text-sm" htmlFor="outfit-feedback">Anything you would change?</label>
              <Textarea id="outfit-feedback" value={rating.feedback ?? ''} onChange={event => onFeedbackChange(event.target.value)} rows={3} disabled={ratingSubmitted} placeholder="Color, fit, occasion…" />
              {ratingSubmitted && <p role="status" className="text-sm text-muted-foreground">Thanks — your feedback is saved.</p>}
            </div>
          </details>
        </div>
      </div>
    </section>
  );
}
