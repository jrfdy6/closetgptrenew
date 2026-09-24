"use client";

import { motion, AnimatePresence, useReducedMotion } from 'framer-motion';
import { Sparkles, Award, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface XPNotificationProps {
  xp: number;
  reason: string;
  show?: boolean;
  onDismiss?: () => void;
  levelUp?: boolean;
  newLevel?: number;
  inline?: boolean;
}

export default function XPNotification({ xp, reason, show = true, onDismiss, levelUp = false, newLevel, inline = false }: XPNotificationProps) {
  const [visible, setVisible] = useState(show);
  const reduceMotion = useReducedMotion();
  const dismiss = useRef(onDismiss);
  dismiss.current = onDismiss;
  useEffect(() => {
    setVisible(show);
    if (!show) return;
    const timer = setTimeout(() => { setVisible(false); dismiss.current?.(); }, 3500);
    return () => clearTimeout(timer);
  }, [show]);

  const validLevelUp = levelUp && Number.isInteger(newLevel) && (newLevel ?? 0) > 0;
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={reduceMotion ? false : { opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: reduceMotion ? 0 : 20 }}
          transition={{ duration: reduceMotion ? 0 : 0.25, ease: 'easeOut' }}
          className={`${inline ? 'relative w-full' : 'fixed top-4 right-4 z-50 w-[calc(100%-2rem)] max-w-[320px]'} pointer-events-auto rounded-xl p-3 shadow-lg bg-card border-2 border-primary/30 text-card-foreground`}
        >
          <div className="flex items-center gap-3">
            {validLevelUp ? <Award aria-hidden="true" className="h-5 w-5 shrink-0 text-[#80502F] dark:text-[#E8C8A0]" /> : <Sparkles aria-hidden="true" className="h-5 w-5 shrink-0 text-[#80502F] dark:text-[#E8C8A0]" />}
            <div role="status" aria-live="polite" aria-atomic="true" className="min-w-0 flex-1">
              <div className="text-sm font-semibold">{validLevelUp ? `Level ${newLevel} reached!` : `+${xp} XP`}</div>
              <div className="mt-0.5 text-xs text-muted-foreground break-words">{validLevelUp ? `+${xp} XP · ${reason}` : reason}</div>
            </div>
            {onDismiss && (
              <button type="button" aria-label="Dismiss XP notification" onClick={() => { setVisible(false); dismiss.current?.(); }} className="flex min-h-11 min-w-11 items-center justify-center rounded-md hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring">
                <X aria-hidden="true" className="h-4 w-4" />
              </button>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

interface XPNotificationStackProps {
  notifications: Array<{ id: string; xp: number; reason: string; levelUp?: boolean; newLevel?: number }>;
  onDismiss: (id: string) => void;
}

export function XPNotificationStack({ notifications, onDismiss }: XPNotificationStackProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex w-[calc(100%-2rem)] max-w-[320px] max-h-[calc(100dvh-2rem)] flex-col gap-2 overflow-y-auto pointer-events-none">
      {notifications.map(notification => (
        <XPNotification key={notification.id} inline xp={notification.xp} reason={notification.reason} levelUp={notification.levelUp} newLevel={notification.newLevel} onDismiss={() => onDismiss(notification.id)} />
      ))}
    </div>
  );
}
