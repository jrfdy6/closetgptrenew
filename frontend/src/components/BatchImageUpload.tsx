"use client";

import { useCallback, useEffect, useRef, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Check, ImagePlus, Loader2, RotateCcw, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useFirebase } from '@/lib/firebase-context';
import { persistBatchWardrobeItem } from '@/lib/persistBatchWardrobeItem';
import { getPublicBackendUrl } from '@/lib/publicBackendUrl';
import { prepareCapsulePhoto, photoHash } from '@/lib/onboarding/capsulePhoto';
import { normalizeItemMetadata } from '../../lib/normalization';

interface BatchImageUploadProps {
  /** Fires once after the selected batch is resolved; callers may close the dialog. */
  onUploadComplete?: (items: any[]) => void | Promise<void>;
  /** Incremental acknowledgment for callers that keep the uploader mounted. */
  onItemSaved?: (item: SavedItem) => void | Promise<void>;
  onError?: (message: string) => void;
  onPendingChange?: (hasUnsavedItems: boolean) => void;
  userId: string;
  quickMode?: boolean;
  /** Kept for callers outside onboarding. A single photo may always be saved. */
  requireStaging?: boolean;
  requiredCount?: number;
}
type UploadStatus = 'pending' | 'uploading' | 'analyzing' | 'saving' | 'success' | 'error' | 'duplicate';
type SavedItem = Record<string, any> & { id: string };
type UploadItem = {
  id: string; file: File; preview: string; status: UploadStatus; error?: string;
  imageUrl?: string; hash?: string; preparedFile?: File; savedInput?: SavedItem;
};
const statusLabel: Record<UploadStatus, string> = {
  pending: 'Ready to upload', uploading: 'Uploading photo', analyzing: 'Identifying your item',
  saving: 'Saving to your wardrobe', success: 'Saved to your wardrobe', error: 'Not saved yet', duplicate: 'Already added',
};

/** One stable item ID and one acknowledged save per photo, including retries. */
export default function BatchImageUpload({ onUploadComplete, onItemSaved, onError, onPendingChange, userId }: BatchImageUploadProps) {
  const { user } = useFirebase();
  const [items, setItems] = useState<UploadItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [preparingCount, setPreparingCount] = useState(0);
  const [queueOwner, setQueueOwner] = useState(userId);
  const mounted = useRef(true);
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const itemsRef = useRef(items);
  const activeOwner = useRef(userId);
  const currentUser = useRef(user);
  const running = useRef(false);
  const preparingSelections = useRef(new Set<symbol>());
  const pendingCallback = useRef(onPendingChange);
  const unreportedSaves = useRef(new Map<string, SavedItem>());
  const visibleItems = queueOwner === userId && user?.uid === userId ? items : [];
  itemsRef.current = visibleItems;
  currentUser.current = user;
  activeOwner.current = userId;
  pendingCallback.current = onPendingChange;

  useEffect(() => {
    mounted.current = true;
    const selections = preparingSelections.current;
    return () => {
      mounted.current = false;
      selections.clear();
      pendingCallback.current?.(false);
    };
  }, []);

  useEffect(() => {
    const selections = preparingSelections.current;
    setItems([]);
    itemsRef.current = [];
    unreportedSaves.current.clear();
    setQueueOwner(userId);
    setBusy(false);
    running.current = false;
    selections.clear();
    setPreparingCount(0);
    setSelectionError(null);
    return () => {
      selections.clear();
      itemsRef.current.forEach(item => URL.revokeObjectURL(item.preview));
    };
  }, [userId, user?.uid]);

  const update = (id: string, values: Partial<UploadItem>) => {
    const next = itemsRef.current.map(item => item.id === id ? { ...item, ...values } : item);
    itemsRef.current = next;
    setItems(next);
  };
  const isCurrent = useCallback((uid: string) => mounted.current && activeOwner.current === uid && currentUser.current?.uid === uid, []);

  const finishResolvedBatch = useCallback(async (owner: string) => {
    // Existing dashboard/wardrobe callers close their dialog here. An earlier
    // successful sibling must never hide a later pending or failed selection.
    if (!isCurrent(owner) || running.current || preparingSelections.current.size || !unreportedSaves.current.size ||
      itemsRef.current.some(item => item.status !== 'success' && item.status !== 'duplicate')) return;
    const saved = Array.from(unreportedSaves.current.values());
    unreportedSaves.current.clear();
    try { await onUploadComplete?.(saved); }
    catch {
      if (isCurrent(owner)) setSelectionError('Your items are saved, but the wardrobe view could not be refreshed. Please refresh it.');
    }
  }, [isCurrent, onUploadComplete]);
  const removeItem = (item: UploadItem) => {
    URL.revokeObjectURL(item.preview);
    const next = itemsRef.current.filter(entry => entry.id !== item.id);
    itemsRef.current = next;
    setItems(next);
    void finishResolvedBatch(userId);
  };

  const onDrop = useCallback(async (files: File[]) => {
    if (!user || user.uid !== userId || running.current || !files.length) return;
    const owner = userId;
    const selection = Symbol('photo-selection');
    preparingSelections.current.add(selection);
    setPreparingCount(preparingSelections.current.size);
    const selectionIsCurrent = () => isCurrent(owner) && preparingSelections.current.has(selection);
    const selected: UploadItem[] = [];
    let staged = false;
    setSelectionError(null);
    try {
      const token = await user.getIdToken();
      if (!selectionIsCurrent()) return;
      const response = await fetch('/api/wardrobe', { headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
      const payload = await response.json();
      if (!selectionIsCurrent()) return;
      if (!response.ok || payload.success !== true || !Array.isArray(payload.items)) {
        throw new Error('We could not check your saved photos. Please try selecting them again.');
      }
      const knownHashes = new Set<string>([
        ...payload.items.flatMap((item: SavedItem) => [item.contentHash, item.imageHash].filter(Boolean)),
        ...itemsRef.current.map(item => item.hash).filter((value): value is string => Boolean(value)),
      ]);
      for (const file of files) {
        const hash = await photoHash(file);
        if (!selectionIsCurrent()) return;
        const duplicate = knownHashes.has(hash);
        knownHashes.add(hash);
        let preparedFile: File | undefined;
        let error: string | undefined;
        try { preparedFile = await prepareCapsulePhoto(file); } catch (failure) { error = failure instanceof Error ? failure.message : 'This photo could not be read.'; }
        if (!selectionIsCurrent()) return;
        selected.push({ id: `item-${crypto.randomUUID()}`, file, hash, preparedFile, error, preview: URL.createObjectURL(preparedFile || file), status: duplicate ? 'duplicate' : error ? 'error' : 'pending' });
      }
      // A concurrent selection may have staged the same hash during preparation.
      const stagedHashes = new Set(itemsRef.current.map(item => item.hash).filter(Boolean));
      selected.forEach(item => {
        if (item.hash && stagedHashes.has(item.hash)) item.status = 'duplicate';
      });
      const next = [...itemsRef.current, ...selected];
      itemsRef.current = next;
      setItems(next);
      staged = true;
    } catch (error) {
      if (selectionIsCurrent()) setSelectionError(error instanceof Error ? error.message : 'These photos could not be selected. Please try again.');
    } finally {
      if (!staged) selected.forEach(item => URL.revokeObjectURL(item.preview));
      const wasCurrent = selectionIsCurrent();
      preparingSelections.current.delete(selection);
      if (wasCurrent) {
        setPreparingCount(preparingSelections.current.size);
        if (staged) await finishResolvedBatch(owner);
      }
    }
  }, [user, userId, isCurrent, finishResolvedBatch]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, disabled: busy,
    accept: { 'image/jpeg': ['.jpg', '.jpeg'], 'image/png': ['.png'], 'image/webp': ['.webp'], 'image/heic': ['.heic'], 'image/heif': ['.heif'] },
    maxSize: 10 * 1024 * 1024, multiple: true,
    onDropRejected: () => setSelectionError('Choose a JPEG, PNG, WebP or HEIC photo up to 10 MB. Other selected photos are kept.'),
  });

  const startUpload = async (onlyId?: string) => {
    if (!user || user.uid !== userId || running.current) return;
    const owner = userId;
    const guardedUser = { getIdToken: async () => {
      const token = await user.getIdToken();
      if (!isCurrent(owner)) throw new Error('Your account changed before this item was saved.');
      return token;
    } };
    const pending = itemsRef.current.filter(item => (item.status === 'pending' || item.status === 'error') && (!onlyId || item.id === onlyId));
    if (!pending.length) return;
    running.current = true;
    setBusy(true);
    try {
      for (const item of pending) {
        if (!isCurrent(owner)) break;
        try {
          if (!item.imageUrl) {
            update(item.id, { status: 'uploading', error: undefined });
            item.preparedFile = item.preparedFile || await prepareCapsulePhoto(item.file);
            if (!isCurrent(owner)) break;
            const form = new FormData();
            form.append('file', item.preparedFile); form.append('category', 'clothing'); form.append('name', item.file.name);
            const response = await fetch(`${getPublicBackendUrl()}/api/image/upload`, {
              method: 'POST', headers: { Authorization: `Bearer ${await guardedUser.getIdToken()}` }, body: form,
            });
            const result = await response.json();
            if (!isCurrent(owner)) break;
            if (!response.ok || result.fallback === true || result.success !== true || typeof result.image_url !== 'string' || !result.image_url) throw new Error('Photo upload failed. Retry this photo.');
            item.imageUrl = result.image_url;
            update(item.id, { imageUrl: item.imageUrl, preparedFile: item.preparedFile });
          }
          if (!isCurrent(owner)) break;
          if (!item.savedInput) {
            update(item.id, { status: 'analyzing', error: undefined });
            const response = await fetch(`${getPublicBackendUrl()}/analyze-image`, {
              method: 'POST', headers: { Authorization: `Bearer ${await guardedUser.getIdToken()}`, 'Content-Type': 'application/json' },
              body: JSON.stringify({ image: { url: item.imageUrl }, client_item_id: item.id, file_name: item.file.name }),
            });
            const result = await response.json();
            if (!isCurrent(owner)) break;
            if (!response.ok || (!result.analysis && result.analysis_status !== 'pending')) throw new Error('Your photo uploaded, but its details could not be identified. Retry analysis.');
            const analysis = result.analysis || {};
            item.savedInput = normalizeItemMetadata({
              id: item.id, userId: owner, imageUrl: item.imageUrl,
              name: analysis.name || analysis.clothing_type || item.file.name.replace(/\.[^.]+$/, ''),
              type: analysis.type || analysis.clothing_type || 'unknown', color: analysis.color || analysis.primary_color || 'unknown',
              analysis, contentHash: item.hash, imageHash: item.hash, fileSize: item.file.size,
              createdAt: new Date().toISOString(),
              processing_status: result.analysis_status === 'pending' ? 'codex_pending' : 'pending',
              metadata: result.analysis_status === 'pending' ? {
                codex_job_id: result.codex_job_id,
                codex_analysis: { provider: result.analysis_provider || 'codex', status: 'pending', job_id: result.codex_job_id },
              } : {},
              brand: analysis.brand || '', style: analysis.style || [], material: analysis.material || '',
              season: analysis.season || [], occasion: analysis.occasion || [], subType: analysis.subType || '',
              gender: analysis.gender || 'unisex', mood: analysis.mood || [],
              backgroundRemoved: false, favorite: false, wearCount: 0, lastWorn: null,
            });
            update(item.id, { savedInput: item.savedInput });
          }
          if (!isCurrent(owner)) break;
          update(item.id, { status: 'saving', error: undefined });
          const saved = await persistBatchWardrobeItem(item.savedInput!, guardedUser);
          if (!isCurrent(owner)) break;
          update(item.id, { status: 'success', error: undefined });
          unreportedSaves.current.set(saved.id, saved);
          // Onboarding refreshes each persisted item without closing the uploader.
          try { await onItemSaved?.(saved); } catch { /* Parent owns reconciliation feedback. */ }
        } catch (error) {
          if (!isCurrent(owner)) break;
          const message = error instanceof Error ? error.message : 'This item was not confirmed saved. Please retry.';
          update(item.id, { status: 'error', error: message });
          onError?.(message);
        }
      }
    } finally {
      running.current = false;
      if (isCurrent(owner)) setBusy(false);
    }
    await finishResolvedBatch(owner);
  };

  const pendingCount = visibleItems.filter(item => item.status === 'pending' || item.status === 'error').length;
  const preparing = queueOwner === userId && user?.uid === userId && preparingCount > 0;
  const hasUnsaved = pendingCount > 0 || busy || preparing;
  useEffect(() => { onPendingChange?.(hasUnsaved); }, [hasUnsaved, onPendingChange]);
  useEffect(() => {
    if (!hasUnsaved) return;
    const confirmLeave = (event: BeforeUnloadEvent) => { event.preventDefault(); event.returnValue = ''; };
    window.addEventListener('beforeunload', confirmLeave);
    return () => window.removeEventListener('beforeunload', confirmLeave);
  }, [hasUnsaved]);

  return <section aria-labelledby="capsule-upload-heading" className="space-y-5">
    <div {...getRootProps()} className={`cursor-pointer rounded-2xl border-2 border-dashed p-6 text-center transition-colors focus-within:ring-2 focus-within:ring-primary ${isDragActive ? 'border-primary bg-primary/10' : 'border-border bg-background/60'}`}>
      <input {...getInputProps({ 'aria-label': 'Choose clothing photos' })} />
      <ImagePlus aria-hidden="true" className="mx-auto mb-3 h-7 w-7 text-primary" />
      <h2 id="capsule-upload-heading" className="font-semibold text-lg">Add a few favorites</h2>
      <p className="mt-1 text-sm text-muted-foreground">Choose photos or drop them here. Save one item or several at a time.</p>
      <p className="mt-3 text-xs text-muted-foreground">JPEG, PNG, WebP or HEIC · up to 10 MB each</p>
    </div>
    {preparing && <p role="status" className="text-sm text-muted-foreground">Preparing your photos…</p>}
    {selectionError && <p role="alert" className="text-sm text-destructive">{selectionError}</p>}
    {visibleItems.length > 0 && <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">{busy ? 'Keep this page open while your items save.' : pendingCount ? 'Leaving before confirmation discards unsaved selections. Save your items before you go.' : 'Your saved items are in the capsule below.'}</p>
        <Button onClick={() => void startUpload()} disabled={busy || !pendingCount}>
          {busy ? <><Loader2 aria-hidden="true" className="mr-2 h-4 w-4 animate-spin motion-reduce:animate-none" />Saving items…</> : `Save ${pendingCount} ${pendingCount === 1 ? 'item' : 'items'}`}
        </Button>
      </div>
      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
        {visibleItems.map(item => <li key={item.id} className="overflow-hidden rounded-xl border bg-card">
          <div className="relative aspect-square bg-muted/40">
            <img src={item.preview} alt={item.file.name} className="h-full w-full object-contain p-2" />
            {!busy && <button type="button" aria-label={`Remove ${item.file.name} from this selection`} className="absolute right-2 top-2 rounded-full bg-background p-2 shadow-sm focus-visible:ring-2 focus-visible:ring-primary" onClick={() => removeItem(item)}><X aria-hidden="true" className="h-4 w-4" /></button>}
          </div>
          <div className="space-y-2 p-3">
            <p className="truncate text-sm font-medium" title={item.file.name}>{item.file.name}</p>
            <p role="status" className="flex items-center gap-1 text-xs text-muted-foreground">{item.status === 'success' && <Check aria-hidden="true" className="h-3 w-3" />}{statusLabel[item.status]}</p>
            {item.error && <p role="alert" className="text-xs text-destructive">{item.error}</p>}
            {item.status === 'error' && <Button variant="outline" size="sm" disabled={busy} onClick={() => void startUpload(item.id)}><RotateCcw aria-hidden="true" className="mr-1 h-3 w-3" />{item.savedInput ? 'Retry save' : item.imageUrl ? 'Retry analysis' : 'Retry upload'}</Button>}
          </div>
        </li>)}
      </ul>
    </>}
  </section>;
}
