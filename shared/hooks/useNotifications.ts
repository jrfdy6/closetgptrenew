import { useState, useCallback } from 'react';

export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  message: string;
  duration?: number;
}

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);

  const addNotification = useCallback(
    (notification: Omit<Notification, 'id'>) => {
      const id = Math.random().toString(36).substring(2);
      const newNotification = { ...notification, id };
      setNotifications((prev) => [...prev, newNotification]);

      if (notification.duration !== 0) {
        setTimeout(() => {
          removeNotification(id);
        }, notification.duration || 5000);
      }

      return id;
    },
    []
  );

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((notification) => notification.id !== id));
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  const success = useCallback(
    (message: string, duration?: number) => {
      return addNotification({ type: 'success', message, duration });
    },
    [addNotification]
  );

  const error = useCallback(
    (message: string, duration?: number) => {
      return addNotification({ type: 'error', message, duration });
    },
    [addNotification]
  );

  const warning = useCallback(
    (message: string, duration?: number) => {
      return addNotification({ type: 'warning', message, duration });
    },
    [addNotification]
  );

  const info = useCallback(
    (message: string, duration?: number) => {
      return addNotification({ type: 'info', message, duration });
    },
    [addNotification]
  );

  return {
    notifications,
    addNotification,
    removeNotification,
    clearNotifications,
    success,
    error,
    warning,
    info,
  };
}; 