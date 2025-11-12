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
    success: "bg-[#ECFDF5]/95 border-[#6EE7B7]/40 text-[#0F172A] dark:bg-[#1F3D32]/90 dark:border-[#15803D]/40 dark:text-[#D1FAE5]",
    info: "bg-[#FFF7E6]/95 border-[#FFB84C]/40 text-[#7C3E0A] dark:bg-[#3D2F24]/90 dark:border-[#FF9400]/35 dark:text-[#FDE68A]",
    error: "bg-[#FFF0EC]/95 border-[#FF6F61]/40 text-[#7F1D1D] dark:bg-[#3D211F]/90 dark:border-[#FF6F61]/35 dark:text-[#FCA5A5]"
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

