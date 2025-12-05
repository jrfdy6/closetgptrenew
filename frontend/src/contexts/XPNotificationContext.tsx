"use client";

import { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { XPNotificationStack } from '@/components/gamification';

interface XPNotification {
  id: string;
  xp: number;
  reason: string;
  levelUp?: boolean;
  newLevel?: number;
}

interface XPNotificationContextType {
  showNotification: (xp: number, reason: string, levelUp?: boolean, newLevel?: number) => void;
}

const XPNotificationContext = createContext<XPNotificationContextType | undefined>(undefined);

export function XPNotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<XPNotification[]>([]);

  useEffect(() => {
    console.log('🔔 XPNotificationProvider mounted');
    return () => console.log('🔔 XPNotificationProvider unmounted');
  }, []);

  const showNotification = useCallback((xp: number, reason: string, levelUp?: boolean, newLevel?: number) => {
    const id = `xp-${Date.now()}-${Math.random()}`;
    console.log(`🔔 Showing XP notification: +${xp} XP (${reason})`, { levelUp, newLevel });
    
    setNotifications(prev => [
      ...prev,
      { id, xp, reason, levelUp, newLevel }
    ]);

    // Auto-dismiss after 3 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 3500);
  }, []);

  const handleDismiss = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  // Listen for XP award events from various sources
  useEffect(() => {
    console.log('🔔 XPNotificationProvider: Setting up xpAwarded event listener');
    
    const handleXPAwarded = (event: CustomEvent) => {
      console.log('🔔 XPNotificationProvider: Received xpAwarded event', event.detail);
      const { xp, reason, level_up, new_level } = event.detail;
      showNotification(xp, reason, level_up, new_level);
    };

    window.addEventListener('xpAwarded', handleXPAwarded as EventListener);
    console.log('🔔 XPNotificationProvider: Event listener added');
    
    return () => {
      console.log('🔔 XPNotificationProvider: Removing event listener');
      window.removeEventListener('xpAwarded', handleXPAwarded as EventListener);
    };
  }, [showNotification]);

  return (
    <XPNotificationContext.Provider value={{ showNotification }}>
      {children}
      <XPNotificationStack notifications={notifications} onDismiss={handleDismiss} />
    </XPNotificationContext.Provider>
  );
}

export function useXPNotification() {
  const context = useContext(XPNotificationContext);
  if (!context) {
    throw new Error('useXPNotification must be used within XPNotificationProvider');
  }
  return context;
}

