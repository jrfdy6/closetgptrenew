"use client";

import React, { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogDescription, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Download, Grid3x3, ImageOff, Images, Loader2, Maximize2, Share2 } from 'lucide-react';

interface FlatLayUsageInfo {
  tier: string;
  limit: number | null;
  used: number;
  remaining: number | null;
}

interface FlatLayViewerProps {
  flatLayUrl?: string | null;
  outfitId?: string;
  onRefresh?: () => void;
  refreshPending?: boolean;
  outfitName?: string;
  outfitItems?: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  className?: string;
  showItemGrid?: boolean;
  onViewChange?: (view: 'flat-lay' | 'grid') => void;
  status?: string;
  error?: string | null;
  flatLayUsage?: FlatLayUsageInfo | null;
  flatLayLoading?: boolean;
  flatLayError?: string | null;
  onRequestFlatLay?: () => void;
  onSkipFlatLay?: () => void;
  flatLayActionLoading?: boolean;
  hasFlatLayCredits?: boolean;
  requestAllowed?: boolean;
  admissionPaused?: boolean;
  admissionReason?: string | null;
}

export default function FlatLayViewer({
  flatLayUrl,
  outfitId, onRefresh, refreshPending = false,
  outfitName,
  outfitItems = [],
  className = '',
  showItemGrid = true,
  onViewChange,
  status,
  error,
  flatLayUsage = null,
  flatLayLoading = false,
  flatLayError = null,
  onRequestFlatLay,
  onSkipFlatLay,
  flatLayActionLoading = false,
  hasFlatLayCredits = false,
  requestAllowed = true,
  admissionPaused = false,
  admissionReason = null,
}: FlatLayViewerProps) {
  const normalizedStatus = (status ?? '').toLowerCase();
  const isComplete = ['done', 'completed', 'ready'].includes(normalizedStatus) || (!normalizedStatus && Boolean(flatLayUrl));
  const imageRef = useRef<HTMLImageElement>(null);
  const identity = `${outfitId ?? ''}:${isComplete ? flatLayUrl ?? '' : ''}`;
  const identityRef = useRef(identity);
  identityRef.current = identity;
  const actionRef = useRef<AbortController | null>(null);
  const [imageVersion, setImageVersion] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isLoading, setIsLoading] = useState(Boolean(flatLayUrl));
  const [imageError, setImageError] = useState(false);
  const [currentView, setCurrentView] = useState<'flat-lay' | 'grid'>(flatLayUrl ? 'flat-lay' : 'grid');
  const [activeAction, setActiveAction] = useState<'download' | 'share' | null>(null);
  const [actionFeedback, setActionFeedback] = useState<{ message: string; error: boolean } | null>(null);
  const [failedItemImages, setFailedItemImages] = useState<Record<string, string>>({});

  useEffect(() => {
    setImageError(false);
    setIsLoading(Boolean(flatLayUrl));
    setCurrentView(flatLayUrl ? 'flat-lay' : 'grid');
    setIsFullscreen(false);
    setActionFeedback(null);
    setActiveAction(null);
    setImageVersion(0);
    return () => { actionRef.current?.abort(); actionRef.current = null; };
  }, [identity]);

  const isPending = ['pending', 'processing', 'queued'].includes(normalizedStatus);
  const isDelayed = normalizedStatus === 'delayed';
  const isFailed = ['failed', 'error'].includes(normalizedStatus);
  const awaitingConsent = ['awaiting_consent', 'manual_pending'].includes(normalizedStatus);
  const isStale = ['stale', 'outdated'].includes(normalizedStatus);
  const isUnknown = Boolean(normalizedStatus) && !isComplete && !isPending && !isDelayed && !isFailed && !isStale && !awaitingConsent && normalizedStatus !== 'skipped';
  const hasImage = Boolean(flatLayUrl) && isComplete && !imageError;
  const canShowPieces = showItemGrid && outfitItems.length > 0;
  const showingImage = hasImage && (currentView === 'flat-lay' || !canShowPieces);
  const balanceKnown = Boolean(flatLayUsage) && !flatLayLoading && !flatLayError;
  const creditsExhausted = balanceKnown && flatLayUsage?.remaining !== null && Number.isFinite(flatLayUsage?.remaining) && (flatLayUsage?.remaining ?? 0) <= 0;
  const requestDisabled = admissionPaused || flatLayActionLoading || !balanceKnown || !hasFlatLayCredits || creditsExhausted;
  const canRequest = (requestAllowed || admissionPaused) && !flatLayUrl && !isPending && !isDelayed && !isUnknown && !isComplete && Boolean(onRequestFlatLay);
  const imageSource = flatLayUrl && /(?:storage\.googleapis\.com|firebasestorage\.googleapis\.com)/.test(flatLayUrl)
    ? `/api/flatlay-proxy?url=${encodeURIComponent(flatLayUrl)}`
    : flatLayUrl;

  useEffect(() => {
    // A cached image may already be ready before React observes its load event.
    const image = imageRef.current;
    if (showingImage && image?.complete && image.naturalWidth > 0) setIsLoading(false);
  }, [imageSource, showingImage]);

  const previewCaption = canShowPieces
    ? 'Garment details may vary. See Pieces for original photos.'
    : 'Garment details may vary.';

  const balanceText = flatLayLoading
    ? 'Checking flat lay credits…'
    : flatLayError || !flatLayUsage
      ? 'Your credit balance is unavailable. Please try again later.'
      : flatLayUsage.remaining === null
        ? 'Unlimited flat lays on your plan.'
        : `${flatLayUsage.remaining} flat lay ${flatLayUsage.remaining === 1 ? 'credit' : 'credits'} remaining this week.`;

  let statusHeading = 'Add a styled flat lay';
  let statusDescription = 'Create an AI-styled flat lay of these pieces.';
  if (imageError) {
    statusHeading = 'Your flat lay could not be loaded';
    statusDescription = 'Your outfit pieces are still here. Retry loading this image. This does not create another flat lay or use a credit.';
  } else if (admissionPaused && !isPending && !isDelayed && !isComplete) {
    statusHeading = 'Flat lays are temporarily unavailable';
    statusDescription = admissionReason || 'Your outfit is saved. Please check again later; no credit has been used.';
  } else if (isStale || (awaitingConsent && Boolean(error))) {
    statusHeading = 'Your outfit has changed';
    statusDescription = error || 'The earlier flat lay no longer matches these pieces. Create a new one only when you are ready.';
  } else if (isUnknown || (isComplete && !flatLayUrl)) {
    statusHeading = 'Your flat lay status is unavailable';
    statusDescription = 'Refresh the saved status before making another request. Your outfit pieces are still here.';
  } else if (isDelayed) {
    statusHeading = 'Your flat lay is taking longer than expected';
    statusDescription = 'The request is still on record. Please check back later; there is no need to request another.';
  } else if (isPending) {
    statusHeading = 'Your flat lay is being prepared';
    statusDescription = 'Your request is saved. You can leave and return to this look while the image is prepared.';
  } else if (isFailed) {
    statusHeading = 'Your flat lay could not be created';
    statusDescription = error || (requestAllowed
      ? 'Your outfit pieces are still available. You can make another request when you are ready.'
      : 'Your outfit pieces are still here. Please contact support before making another request.');
  } else if (!requestAllowed) {
    statusHeading = 'This flat lay request needs review';
    statusDescription = admissionReason || error || 'Your outfit pieces are still here. Please contact support before making another request.';
  } else if (flatLayActionLoading) {
    statusHeading = 'Requesting your flat lay…';
  }

  const changeView = (view: 'flat-lay' | 'grid') => {
    setCurrentView(view);
    onViewChange?.(view);
  };

  const handleImageError = () => {
    setImageError(true);
    setIsLoading(false);
    setIsFullscreen(false);
    setCurrentView('grid');
  };

  const handleDownload = async () => {
    if (!flatLayUrl || actionRef.current) return;
    const actionIdentity = identity;
    setActiveAction('download');
    setActionFeedback(null);
    let objectUrl: string | undefined;
    let link: HTMLAnchorElement | undefined;
    const controller = new AbortController();
    actionRef.current = controller;
    const timeout = window.setTimeout(() => controller.abort(), 15000);
    try {
      const response = await fetch(imageSource || flatLayUrl, { signal: controller.signal });
      if (!response.ok || !response.headers.get('content-type')?.toLowerCase().startsWith('image/')) {
        throw new Error('Image download unavailable');
      }
      const blob = await response.blob();
      if (!blob.size || !blob.type.toLowerCase().startsWith('image/')) throw new Error('Invalid image response');
      if (controller.signal.aborted || identityRef.current !== actionIdentity) return;
      objectUrl = window.URL.createObjectURL(blob);
      link = document.createElement('a');
      link.href = objectUrl;
      const extension = blob.type === 'image/jpeg' ? 'jpg' : blob.type === 'image/webp' ? 'webp' : 'png';
      link.download = `${outfitName || 'outfit'}-flat-lay.${extension}`;
      document.body.appendChild(link);
      link.click();
      setActionFeedback({ message: 'Download started.', error: false });
    } catch {
      if (identityRef.current === actionIdentity && actionRef.current === controller) setActionFeedback({ message: 'The flat lay could not be downloaded. Please try Download again.', error: true });
    } finally {
      window.clearTimeout(timeout);
      link?.remove();
      if (objectUrl) window.URL.revokeObjectURL(objectUrl);
      if (actionRef.current === controller) { actionRef.current = null; setActiveAction(null); }
    }
  };

  const handleShare = async () => {
    if (!flatLayUrl || actionRef.current) return;
    const actionIdentity = identity;
    const controller = new AbortController();
    actionRef.current = controller;
    setActiveAction('share');
    setActionFeedback(null);
    try {
      if (navigator.share) {
        await navigator.share({ title: outfitName || 'My outfit', text: 'My outfit from EasyOutfit', url: flatLayUrl });
      } else {
        if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(flatLayUrl);
        if (!controller.signal.aborted && identityRef.current === actionIdentity) setActionFeedback({ message: 'Flat lay link copied.', error: false });
      }
    } catch (shareError) {
      if (!controller.signal.aborted && identityRef.current === actionIdentity && !(shareError instanceof Error && shareError.name === 'AbortError')) {
        setActionFeedback({ message: 'The flat lay could not be shared. Try Share again or download the image.', error: true });
      }
    } finally {
      if (actionRef.current === controller) { actionRef.current = null; setActiveAction(null); }
    }
  };

  const imageActions = (
    <div className="flex flex-wrap items-center gap-1">
      <Button variant="ghost" size="sm" onClick={handleDownload} disabled={Boolean(activeAction) || isLoading}>
        {activeAction === 'download' ? <Loader2 className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" aria-hidden="true" /> : <Download className="mr-2 h-4 w-4" aria-hidden="true" />}
        Download
      </Button>
      <Button variant="ghost" size="sm" onClick={handleShare} disabled={Boolean(activeAction) || isLoading}>
        {activeAction === 'share' ? <Loader2 className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" aria-hidden="true" /> : <Share2 className="mr-2 h-4 w-4" aria-hidden="true" />}
        Share
      </Button>
    </div>
  );
  const feedback = actionFeedback ? (
    <p role={actionFeedback.error ? 'alert' : 'status'} className={`text-sm ${actionFeedback.error ? 'text-destructive' : 'text-muted-foreground'}`}>
      {actionFeedback.message}
    </p>
  ) : null;

  return (
    <Dialog open={isFullscreen} onOpenChange={setIsFullscreen}>
      <section className={`overflow-hidden rounded-3xl border border-stone-200 bg-[#f7f5f0] dark:border-stone-700 dark:bg-stone-900 motion-reduce:[&_button]:transition-none motion-reduce:[&_button]:transform-none ${className}`} aria-label="Outfit presentation">
        <div className="flex flex-wrap items-center justify-between gap-3 px-5 py-4 sm:px-6">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-stone-500 dark:text-stone-400">{showingImage ? 'AI styled preview' : 'From your wardrobe'}</p>
            <h3 className="mt-1 text-base font-medium text-stone-900 dark:text-stone-100">{showingImage ? 'Your look' : 'The pieces'}</h3>
          </div>
          {hasImage && canShowPieces && (
            <div className="flex rounded-xl border border-stone-200 bg-white/70 p-1 dark:border-stone-700 dark:bg-stone-800" role="group" aria-label="Outfit view">
              <Button variant="ghost" size="sm" className={showingImage ? 'bg-stone-100 text-stone-900 dark:bg-stone-700 dark:text-white' : ''} aria-pressed={showingImage} onClick={() => changeView('flat-lay')}>
                <Images className="mr-2 h-4 w-4" aria-hidden="true" />Flat lay
              </Button>
              <Button variant="ghost" size="sm" className={!showingImage ? 'bg-stone-100 text-stone-900 dark:bg-stone-700 dark:text-white' : ''} aria-pressed={!showingImage} onClick={() => changeView('grid')}>
                <Grid3x3 className="mr-2 h-4 w-4" aria-hidden="true" />Pieces
              </Button>
            </div>
          )}
        </div>

        {showingImage ? (
          <>
            <div className="relative aspect-square w-full bg-[#f3f0e9] dark:bg-stone-950" aria-busy={isLoading}>
              {isLoading && <div className="absolute inset-0 flex items-center justify-center" role="status"><Loader2 className="h-6 w-6 animate-spin motion-reduce:animate-none text-stone-500" aria-hidden="true" /><span className="sr-only">Loading flat lay</span></div>}
              <img key={`${identity}:${imageVersion}`} ref={imageRef} src={imageSource || undefined} alt={`AI-styled preview of ${outfitName || 'your outfit'}`} className="h-full w-full object-contain" onLoad={() => setIsLoading(false)} onError={handleImageError} />
              <DialogTrigger asChild>
                <Button variant="secondary" size="icon" className="absolute bottom-4 right-4 border border-stone-200 bg-white/90 text-stone-800 shadow-sm hover:bg-white" disabled={isLoading} aria-label="View flat lay in full screen">
                  <Maximize2 className="h-4 w-4" aria-hidden="true" />
                </Button>
              </DialogTrigger>
            </div>
            <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2 sm:px-5">
              <p className="text-xs text-stone-500 dark:text-stone-400">{previewCaption}</p>
              {imageActions}
            </div>
          </>
        ) : canShowPieces ? (
          <ul aria-label="Outfit pieces" className={`grid gap-3 px-4 pb-5 sm:gap-4 sm:px-6 sm:pb-6 ${outfitItems.length === 1 ? 'grid-cols-1' : outfitItems.length === 2 ? 'grid-cols-2' : 'grid-cols-2 sm:grid-cols-3'}`}>
            {outfitItems.map((item) => (
              <li key={item.id} className="min-w-0 overflow-hidden rounded-2xl border border-stone-200/80 bg-white/80 dark:border-stone-700 dark:bg-stone-800">
                <div className="flex aspect-square items-center justify-center bg-white p-3 dark:bg-stone-800 sm:p-4">
                  {item.imageUrl && !item.imageUrl.includes('placeholder') && failedItemImages[item.id] !== item.imageUrl ? (
                    <img src={item.imageUrl} alt={item.name} className="h-full w-full object-contain" onError={() => setFailedItemImages((previous) => ({ ...previous, [item.id]: item.imageUrl! }))} />
                  ) : <div className="text-center text-stone-400"><ImageOff className="mx-auto h-6 w-6" aria-hidden="true" /><span className="mt-2 block text-xs">Photo unavailable</span></div>}
                </div>
                <div className="border-t border-stone-100 px-3 py-3 dark:border-stone-700">
                  <p className="break-words text-sm font-medium leading-snug text-stone-900 dark:text-stone-100">{item.name}</p>
                  <p className="mt-1 text-xs capitalize text-stone-500 dark:text-stone-400">{item.type}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : <p className="px-6 pb-6 text-sm text-stone-500 dark:text-stone-400">No outfit photos available.</p>}

        {!hasImage && (
          <div className="space-y-3 border-t border-stone-200 px-5 py-4 dark:border-stone-700 sm:px-6">
            <div role={isFailed || imageError ? 'alert' : 'status'} className="flex items-start gap-3">
              {isPending || flatLayActionLoading ? <Loader2 className="mt-0.5 h-4 w-4 shrink-0 animate-spin motion-reduce:animate-none text-stone-500" aria-hidden="true" /> : <Images className="mt-0.5 h-4 w-4 shrink-0 text-stone-500" aria-hidden="true" />}
              <div className="space-y-1">
                <p className="text-sm font-medium text-stone-800 dark:text-stone-100">
                  {statusHeading}
                </p>
                <p className="text-sm leading-relaxed text-stone-500 dark:text-stone-400">
                  {statusDescription}
                </p>
              </div>
            </div>
            {imageError && <Button variant="outline" size="sm" className="ml-7 min-h-11" onClick={() => { setImageError(false); setIsLoading(true); setImageVersion(value => value + 1); setCurrentView('flat-lay'); }}>Retry loading image</Button>}
            {!imageError && onRefresh && (isPending || isDelayed || isUnknown || Boolean(flatLayError) || (canRequest && !balanceKnown) || (isComplete && !flatLayUrl) || (!requestAllowed && !hasImage)) && <Button variant="outline" size="sm" className="ml-7 min-h-11" onClick={onRefresh} disabled={refreshPending}>{refreshPending ? 'Refreshing…' : 'Refresh status'}</Button>}
            {canRequest && (
              <div className="space-y-2 pl-7">
                <div className="flex flex-wrap items-center gap-2">
                  <Button variant="outline" size="sm" className="border-stone-300 bg-transparent text-stone-800 shadow-none dark:border-stone-600 dark:text-stone-100" onClick={onRequestFlatLay} disabled={requestDisabled}>
                    {flatLayActionLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" aria-hidden="true" />}
                    {admissionPaused ? 'Temporarily unavailable' : flatLayActionLoading ? 'Requesting…' : isFailed ? 'Request a new flat lay' : 'Create flat lay'}
                  </Button>
                  {awaitingConsent && onSkipFlatLay && <Button variant="ghost" size="sm" onClick={onSkipFlatLay} disabled={flatLayActionLoading}>Maybe later</Button>}
                  {!admissionPaused && creditsExhausted && <Link href="/upgrade" className="rounded-md px-2 py-3 text-sm text-stone-600 underline underline-offset-4 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring dark:text-stone-300">View plans</Link>}
                </div>
                <p className="text-xs text-stone-500 dark:text-stone-400">Uses 1 flat lay credit. <span>{balanceText}</span></p>
                {flatLayError && <p role="alert" className="text-sm text-destructive">{flatLayError}</p>}
              </div>
            )}
          </div>
        )}
        {!isFullscreen && feedback && <div className="px-5 pb-4 sm:px-6">{feedback}</div>}
      </section>

      {hasImage && (
        <DialogContent className="w-[calc(100%_-_2rem)] max-w-5xl gap-3 overflow-hidden rounded-2xl border-stone-200 bg-[#f7f5f0] p-4 dark:border-stone-700 dark:bg-stone-900 motion-reduce:animate-none sm:p-6">
          <DialogTitle className="pr-8 text-stone-900 dark:text-stone-100">{outfitName || 'Your outfit'}</DialogTitle>
          <DialogDescription className="sr-only">AI-styled preview of your outfit. Download or share using the controls below.</DialogDescription>
          <img src={imageSource || undefined} alt={`AI-styled preview of ${outfitName || 'your outfit'}, enlarged`} className="max-h-[70dvh] w-full object-contain" onError={handleImageError} />
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-stone-500 dark:text-stone-400">{previewCaption}</p>
            {imageActions}
          </div>
          {feedback}
        </DialogContent>
      )}
    </Dialog>
  );
}
