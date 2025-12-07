"use client";

import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, TrendingUp, Award } from 'lucide-react';
import { useEffect, useState } from 'react';

interface XPNotificationProps {
  xp: number;
  reason: string;
  show?: boolean;
  onDismiss?: () => void;
  levelUp?: boolean;
  newLevel?: number;
}

export default function XPNotification({
  xp,
  reason,
  show = true,
  onDismiss,
  levelUp = false,
  newLevel
}: XPNotificationProps) {
  const [visible, setVisible] = useState(show);

  useEffect(() => {
    setVisible(show);
    
    if (show) {
      // Auto-dismiss after 3 seconds
      const timer = setTimeout(() => {
        setVisible(false);
        if (onDismiss) {
          setTimeout(onDismiss, 300); // Wait for animation to complete
        }
      }, 3000);

      return () => clearTimeout(timer);
    }
  }, [show, onDismiss]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: 20 }}
          transition={{
            duration: 0.25,
            ease: "easeOut"
          }}
          className={`fixed top-4 right-4 z-50 pointer-events-auto min-w-[240px] max-w-[320px]
            rounded-xl p-3 shadow-lg ${
              levelUp
                ? 'gradient-copper-gold border-none'
                : 'bg-white dark:bg-[#1A1A1A] border border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70'
            }`}
        >
          <div className="flex items-center gap-3">
            {levelUp ? (
              <Award className="w-5 h-5 text-white" />
            ) : (
              <Sparkles className="w-5 h-5 text-[var(--copper-dark)]" />
            )}
            
            <div className="flex-1">
              {levelUp ? (
                <>
                  <div className="text-sm font-medium text-white">
                    Level Up!
                  </div>
                  <div className="text-xs text-white/90 mt-0.5">
                    You're now Level {newLevel}!
                  </div>
                </>
              ) : (
                <>
                  <div className="text-sm font-medium gradient-copper-gold bg-clip-text text-transparent">
                    +{xp} XP
                  </div>
                  <div className="text-xs text-[#57534E] dark:text-[#C4BCB4] mt-0.5">
                    {reason}
                  </div>
                </>
              )}
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Stacked XP Notifications Component
interface XPNotificationStackProps {
  notifications: Array<{
    id: string;
    xp: number;
    reason: string;
    levelUp?: boolean;
    newLevel?: number;
  }>;
  onDismiss: (id: string) => void;
}

export function XPNotificationStack({ notifications, onDismiss }: XPNotificationStackProps) {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
      <AnimatePresence>
        {notifications.map((notification, index) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ 
              opacity: 1, 
              y: index * 80, // Stack notifications
              x: 0 
            }}
            exit={{ opacity: 0, x: 20 }}
            transition={{
              duration: 0.25,
              ease: "easeOut"
            }}
          >
            <XPNotification
              xp={notification.xp}
              reason={notification.reason}
              levelUp={notification.levelUp}
              newLevel={notification.newLevel}
              onDismiss={() => onDismiss(notification.id)}
            />
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

