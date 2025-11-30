"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { X, Lock, Link2 } from "lucide-react";
import { getLinkedProviders } from "@/lib/auth";

interface PasswordLinkBannerProps {
  email: string;
  onLinkClick: () => void;
}

const STORAGE_KEY = "password-link-banner-dismissed";

export default function PasswordLinkBanner({
  email,
  onLinkClick,
}: PasswordLinkBannerProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if user has permanently dismissed this banner
    if (typeof window === "undefined") return;
    
    const dismissed = localStorage.getItem(STORAGE_KEY) === "true";
    if (dismissed) {
      setIsDismissed(true);
      return;
    }

    // Check if password is already linked
    const providers = getLinkedProviders();
    if (providers.includes("password")) {
      return; // Password already linked, don't show banner
    }

    // Show banner if password isn't linked
    setIsVisible(true);
  }, []);

  const handleDismiss = () => {
    setIsVisible(false);
  };

  const handleNeverShow = () => {
    localStorage.setItem(STORAGE_KEY, "true");
    setIsVisible(false);
    setIsDismissed(true);
  };

  const handleLinkNow = () => {
    setIsVisible(false);
    onLinkClick();
  };

  if (!isVisible || isDismissed) {
    return null;
  }

  return (
    <div className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 w-full max-w-md px-4">
      <div className="bg-amber-50 dark:bg-amber-900/30 border border-amber-200 dark:border-amber-800 rounded-lg shadow-lg p-4">
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0 mt-0.5">
            <Lock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-amber-900 dark:text-amber-100 mb-1">
              Link Your Password Account
            </h3>
            <p className="text-xs text-amber-800 dark:text-amber-200 mb-3">
              Link your password to use both Google and password sign-in methods.
            </p>
            <div className="flex items-center gap-2 flex-wrap">
              <Button
                type="button"
                onClick={handleLinkNow}
                size="sm"
                className="bg-amber-600 hover:bg-amber-700 text-white text-xs h-7 px-3"
              >
                <Link2 className="h-3 w-3 mr-1.5" />
                Link Now
              </Button>
              <button
                type="button"
                onClick={handleDismiss}
                className="text-xs text-amber-700 dark:text-amber-300 hover:text-amber-900 dark:hover:text-amber-100 underline"
              >
                Maybe later
              </button>
              <button
                type="button"
                onClick={handleNeverShow}
                className="text-xs text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 underline"
              >
                Never show again
              </button>
            </div>
          </div>
          <button
            type="button"
            onClick={handleDismiss}
            className="flex-shrink-0 text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-200 transition-colors"
            aria-label="Dismiss"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

