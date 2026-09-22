'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { OnboardingDraft, OnboardingState } from '@/lib/onboarding/types';

type DraftUser = { uid: string; getIdToken: () => Promise<string> };
type Status = 'loading' | 'saving' | 'saved' | 'error' | 'conflict';
type Backup = { schemaVersion: 1; revision: number; draft: OnboardingDraft; dirty: boolean };
const emptyDraft = (): OnboardingDraft => ({ answers: [], currentQuestionId: 'gender' });
const equal = (a: OnboardingDraft, b: OnboardingDraft) => JSON.stringify(a) === JSON.stringify(b);

function readBackup(key: string): Backup | null {
  try {
    const parsed = JSON.parse(sessionStorage.getItem(key) || 'null');
    if (parsed?.schemaVersion !== 1 || !Array.isArray(parsed.draft?.answers)) return null;
    if (!parsed.draft.answers.every((answer: { question_id?: unknown; selected_option?: unknown }) =>
      typeof answer.question_id === 'string' && typeof answer.selected_option === 'string')) return null;
    return parsed;
  } catch { return null; }
}

/** Account-scoped drafts, optimistic revision checks and a local safety copy.
 * Guest mode is deliberately checked before the available authenticated user.
 */
export function useOnboardingDraft({ user, enabled, guest, allowProfileEdit = false }: {
  user: DraftUser | null;
  enabled: boolean;
  guest: boolean;
  allowProfileEdit?: boolean;
}) {
  const [draft, setDraft] = useState<OnboardingDraft>(emptyDraft);
  const [state, setState] = useState<OnboardingState | null>(null);
  const [ready, setReady] = useState(false);
  const [status, setStatus] = useState<Status>('loading');
  const [error, setError] = useState<string | null>(null);
  const [conflict, setConflict] = useState<OnboardingState | null>(null);
  const current = useRef(draft);
  const server = useRef<OnboardingState | null>(null);
  const dirty = useRef(false);
  const blocked = useRef(false);
  const session = useRef(0);
  const pending = useRef<Promise<boolean> | null>(null);
  const latest = useRef({ user, enabled, guest, allowProfileEdit });
  latest.current = { user, enabled, guest, allowProfileEdit };
  const key = guest ? 'easyoutfit:onboarding:guest:v1' : `easyoutfit:onboarding:${user?.uid}:v1`;
  const keyRef = useRef(key);
  keyRef.current = key;
  // Refs are reset in an effect; keep the rendered scope separate so neither
  // displayed answers nor actions can use those refs during an identity change.
  const scope = `${enabled ? 'enabled' : 'disabled'}:${guest ? 'guest' : 'account'}:${user?.uid ?? 'signed-out'}`;
  const latestScope = useRef(scope);
  latestScope.current = scope;
  const activeScope = useRef<string | null>(null);
  const [visibleScope, setVisibleScope] = useState<string | null>(null);
  const sameScope = useCallback(() => activeScope.current === scope && latestScope.current === scope, [scope]);
  const visible = enabled && visibleScope === scope && sameScope();

  const backup = useCallback(() => {
    if (!sameScope() || !latest.current.enabled) return false;
    try {
      sessionStorage.setItem(keyRef.current, JSON.stringify({
        schemaVersion: 1, revision: server.current?.revision ?? 0,
        draft: current.current, dirty: dirty.current,
      }));
      return true;
    } catch { return false; }
  }, [sameScope]);

  const refresh = useCallback(async (restore = false): Promise<OnboardingState | null> => {
    const context = latest.current;
    if (!sameScope() || !context.enabled || context.guest || !context.user) return null;
    const generation = session.current;
    try {
      const token = await context.user.getIdToken();
      if (!sameScope() || generation !== session.current) return null;
      const response = await fetch('/api/onboarding', { method: restore ? 'GET' : 'POST', headers: { Authorization: `Bearer ${token}` }, cache: 'no-store' });
      const payload = await response.json();
      if (!response.ok || payload.success !== true || !payload.state) throw new Error('Unable to load your saved progress. Please retry.');
      if (!sameScope() || generation !== session.current) return null;
      const next = payload.state as OnboardingState;
      server.current = next;
      setState(next);
      if (restore) {
        const saved = readBackup(keyRef.current);
        const useLocal = saved?.dirty && (!next.profileComplete || context.allowProfileEdit);
        current.current = useLocal ? saved.draft : next.draft;
        dirty.current = !!useLocal;
        setDraft(current.current);
        if (useLocal && saved.revision !== next.revision) {
          blocked.current = true;
          setConflict(next);
          setStatus('conflict');
          setError('A newer draft was saved elsewhere. Your local answers are still here. Load the newer draft before continuing.');
        } else {
          blocked.current = false;
          setConflict(null);
          setStatus(useLocal ? 'saving' : 'saved');
          setError(null);
        }
        setReady(true);
      }
      return next;
    } catch (cause) {
      if (sameScope() && generation === session.current) {
        setStatus('error');
        setError(cause instanceof Error ? cause.message : 'Unable to load your saved progress. Please retry.');
      }
      return null;
    }
  }, [sameScope]);

  useEffect(() => {
    activeScope.current = scope;
    setVisibleScope(scope);
    session.current += 1;
    pending.current = null;
    dirty.current = false;
    blocked.current = false;
    server.current = null;
    setReady(false);
    setState(null);
    setConflict(null);
    setError(null);
    setStatus('loading');
    current.current = emptyDraft();
    setDraft(current.current);
    if (!enabled) return;
    if (guest) {
      current.current = readBackup(key)?.draft ?? emptyDraft();
      setDraft(current.current);
      setStatus('saved');
      setReady(true);
    } else if (user) {
      void refresh(true);
    }
    return () => { activeScope.current = null; session.current += 1; };
  }, [enabled, guest, user?.uid, key, scope, refresh]);

  const updateDraft = useCallback((change: OnboardingDraft | ((previous: OnboardingDraft) => OnboardingDraft)) => {
    const context = latest.current;
    if (!sameScope() || !context.enabled || (!context.guest && (!server.current || (server.current.profileComplete && !context.allowProfileEdit)))) return;
    const next = typeof change === 'function' ? change(current.current) : change;
    if (equal(next, current.current)) return;
    current.current = next;
    dirty.current = !context.guest;
    setDraft(next);
    const backedUp = backup();
    if (context.guest) {
      setStatus(backedUp ? 'saved' : 'error');
      setError(backedUp ? null : 'Your browser could not save these answers. Keep this tab open and retry.');
    } else if (!blocked.current) {
      setStatus('saving');
      setError(null);
    }
  }, [backup, sameScope]);

  const flush = useCallback(async (): Promise<boolean> => {
    const context = latest.current;
    if (!sameScope() || !context.enabled) return false;
    if (context.guest) {
      const saved = backup();
      setStatus(saved ? 'saved' : 'error');
      setError(saved ? null : 'Your browser could not save these answers. Keep this tab open and retry.');
      return saved;
    }
    if (!context.enabled || !context.user || !server.current || blocked.current) return false;
    if (pending.current) return pending.current;
    const generation = session.current;
    const operation = (async () => {
      try {
        while (dirty.current && sameScope() && generation === session.current) {
          const sending = current.current;
          const expectedRevision = server.current!.revision;
          setStatus('saving');
          const token = await context.user!.getIdToken();
          if (!sameScope() || generation !== session.current) return false;
          const response = await fetch('/api/onboarding', {
            method: 'PATCH', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
            body: JSON.stringify({ expectedRevision, draft: sending }),
          });
          const payload = await response.json();
          if (!sameScope() || generation !== session.current) return false;
          if (response.status === 409 && payload.state) {
            blocked.current = true;
            setConflict({ ...server.current!, ...payload.state });
            setStatus('conflict');
            setError('A newer draft was saved elsewhere. Your local answers are still here. Load the newer draft before continuing.');
            return false;
          }
          if (!response.ok || payload.success !== true || !payload.state) throw new Error('Your latest answers have not saved. Please retry.');
          server.current = { ...server.current!, ...payload.state };
          setState(server.current);
          dirty.current = !equal(current.current, sending);
          backup();
        }
        if (!sameScope() || generation !== session.current) return false;
        setStatus('saved');
        setError(null);
        return true;
      } catch (cause) {
        if (sameScope() && generation === session.current) {
          setStatus('error');
          setError(cause instanceof Error ? cause.message : 'Your latest answers have not saved. Please retry.');
          backup();
        }
        return false;
      }
    })();
    pending.current = operation;
    try { return await operation; } finally { if (pending.current === operation) pending.current = null; }
  }, [backup, sameScope]);

  useEffect(() => {
    if (!visible || !ready || status !== 'saving' || guest) return;
    const timer = setTimeout(() => { void flush(); }, 150);
    return () => clearTimeout(timer);
  }, [draft, ready, status, guest, flush, visible]);

  useEffect(() => {
    const warnUnsaved = (event: BeforeUnloadEvent) => {
      if (activeScope.current !== latestScope.current || !dirty.current) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnUnsaved);
    return () => window.removeEventListener('beforeunload', warnUnsaved);
  }, []);

  const reloadLatest = useCallback(() => {
    if (!sameScope() || !latest.current.enabled || !conflict) return;
    server.current = conflict;
    current.current = conflict.draft;
    dirty.current = false;
    blocked.current = false;
    setState(conflict);
    setDraft(conflict.draft);
    setConflict(null);
    setError(null);
    setStatus('saved');
    backup();
  }, [conflict, backup, sameScope]);

  const retry = useCallback(async () => {
    if (!sameScope() || !latest.current.enabled) return false;
    if (!ready) return !!(await refresh(true));
    return flush();
  }, [ready, refresh, flush, sameScope]);

  return {
    draft: visible ? draft : emptyDraft(),
    state: visible ? state : null,
    ready: visible && ready,
    status: visible ? status : 'loading' as Status,
    error: visible ? error : null,
    conflict: visible ? conflict : null,
    updateDraft, flush, refresh, retry, reloadLatest,
  };
}
