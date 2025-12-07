"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Info, XCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToastProps {
  message: string;
  type: "success" | "info" | "error";
  onClose: () => void;
}

function ToastItem({ message, type, onClose }: ToastProps) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 3000); // Auto-dismiss after 3s

    return () => clearTimeout(timer);
  }, [onClose]);

  const icons = {
    success: CheckCircle,
    info: Info,
    error: XCircle
  };

  const colors = {
    success: "bg-green-50/95 border-green-200/40 text-green-900 dark:bg-green-900/90 dark:border-green-700/40 dark:text-green-100",
    info: "bg-secondary/95 border-primary/40 text-accent dark:bg-muted/90 dark:border-accent/35 dark:text-accent-foreground",
    error: "bg-destructive/10 border-destructive/40 text-destructive dark:bg-destructive/20 dark:border-destructive/35 dark:text-destructive-foreground"
  };

  const Icon = icons[type];

  return (
    <div
      role="status"
      aria-live={type === "error" ? "assertive" : "polite"}
      className={cn(
        "flex items-center gap-3 p-4 rounded-2xl border shadow-xl backdrop-blur-xl",
        "animate-slide-up",
        colors[type]
      )}
    >
      <div className="w-9 h-9 rounded-full bg-white/50 dark:bg-white/10 flex items-center justify-center shadow-inner">
        <Icon className="w-5 h-5 flex-shrink-0" />
      </div>
      <span className="text-sm font-semibold flex-1 leading-snug">{message}</span>
      <button
        onClick={onClose}
        className="p-1.5 rounded-lg text-current/70 hover:text-current hover:bg-white/30 dark:hover:bg-white/10 transition-colors"
        aria-label="Close"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState<Array<{ id: number; message: string; type: "success" | "info" | "error" }>>([]);

  useEffect(() => {
    const handleShowToast = (event: CustomEvent) => {
      const { message, type } = event.detail;
      const id = Date.now();
      
      setToasts(prev => [...prev, { id, message, type }]);
    };

    window.addEventListener("show-toast" as any, handleShowToast);
    
    return () => {
      window.removeEventListener("show-toast" as any, handleShowToast);
    };
  }, []);

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  return (
    <div
      className="fixed top-24 right-6 z-[200] flex flex-col gap-3 max-w-sm"
      role="region"
      aria-live="polite"
      aria-label="Notifications"
    >
      {toasts.map(toast => (
        <ToastItem
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  );
}

