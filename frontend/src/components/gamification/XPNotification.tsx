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
          initial={{ opacity: 0, y: -50, x: 50 }}
          animate={{ opacity: 1, y: 0, x: 0 }}
          exit={{ opacity: 0, x: 100 }}
          transition={{
            type: "spring",
            stiffness: 300,
            damping: 25
          }}
          className="fixed top-4 right-4 z-50 pointer-events-auto"
        >
          <div className={`rounded-lg shadow-lg p-4 min-w-[280px] ${
            levelUp 
              ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' 
              : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700'
          }`}>
            <div className="flex items-center gap-3">
              {levelUp ? (
                <motion.div
                  animate={{
                    scale: [1, 1.2, 1],
                    rotate: [0, 10, -10, 0]
                  }}
                  transition={{
                    duration: 0.5,
                    repeat: 2
                  }}
                >
                  <Award className="w-6 h-6" />
                </motion.div>
              ) : (
                <motion.div
                  animate={{
                    rotate: [0, 360],
                    scale: [1, 1.1, 1]
                  }}
                  transition={{
                    duration: 0.6,
                    ease: "easeInOut"
                  }}
                >
                  <Sparkles className="w-6 h-6 text-amber-500" />
                </motion.div>
              )}
              
              <div className="flex-1">
                {levelUp ? (
                  <>
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 0.2 }}
                      className="font-bold text-lg"
                    >
                      Level Up! 🎉
                    </motion.div>
                    <div className="text-sm opacity-90">
                      You're now Level {newLevel}!
                    </div>
                  </>
                ) : (
                  <>
                    <div className="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                      <motion.span
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ 
                          type: "spring",
                          stiffness: 500,
                          damping: 15,
                          delay: 0.1
                        }}
                        className="text-amber-600 dark:text-amber-400 font-bold"
                      >
                        +{xp} XP
                      </motion.span>
                      <TrendingUp className="w-4 h-4 text-green-500" />
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                      {reason}
                    </div>
                  </>
                )}
              </div>
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
            initial={{ opacity: 0, y: -50, x: 50 }}
            animate={{ 
              opacity: 1, 
              y: index * 80, // Stack notifications
              x: 0 
            }}
            exit={{ opacity: 0, x: 100 }}
            transition={{
              type: "spring",
              stiffness: 300,
              damping: 25
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

