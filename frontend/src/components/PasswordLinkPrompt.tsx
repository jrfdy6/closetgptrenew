"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Lock, AlertCircle, CheckCircle } from "lucide-react";
import { linkEmailPassword } from "@/lib/auth";

interface PasswordLinkPromptProps {
  email: string;
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function PasswordLinkPrompt({
  email,
  open,
  onClose,
  onSuccess,
}: PasswordLinkPromptProps) {
  const [password, setPassword] = useState("");
  const [isLinking, setIsLinking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [showSkipOption, setShowSkipOption] = useState(false);

  const handleLink = async () => {
    if (!password) {
      setError("Please enter your password");
      return;
    }

    setIsLinking(true);
    setError(null);

    try {
      const result = await linkEmailPassword(email, password);
      if (result.success) {
        setSuccess(true);
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 1500);
      } else {
        setError(result.error || "Failed to link password. Please check your password and try again.");
      }
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred");
    } finally {
      setIsLinking(false);
    }
  };

  const handleClose = () => {
    setPassword("");
    setError(null);
    setSuccess(false);
    setShowSkipOption(false);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={() => {}}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Lock className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            Complete Your Sign-In
          </DialogTitle>
          <DialogDescription>
            To enable both sign-in methods, please enter your password to link your account. This is a one-time step.
          </DialogDescription>
        </DialogHeader>

        {success ? (
          <div className="py-4">
            <div className="flex items-center gap-3 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400 flex-shrink-0" />
              <p className="text-sm text-green-700 dark:text-green-300">
                Password successfully linked! You can now use either Google or password to sign in.
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="link-password">Enter your password</Label>
              <Input
                id="link-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !isLinking) {
                    handleLink();
                  }
                }}
                disabled={isLinking}
                autoFocus
              />
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Enter your password to complete account linking. After this, you can use either Google or password to sign in.
              </p>
              <button
                type="button"
                onClick={() => setShowSkipOption(true)}
                className="text-xs text-amber-700 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-300 underline mt-1"
              >
                I don't remember my password
              </button>
            </div>

            {showSkipOption && (
              <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
                <p className="text-sm text-amber-800 dark:text-amber-200 mb-2">
                  No problem! You can link your password later in your profile settings.
                </p>
                <p className="text-xs text-amber-700 dark:text-amber-300">
                  Go to your profile after signing in to link your password account. You can also use "Forgot password" to reset it.
                </p>
              </div>
            )}

            {error && (
              <div className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          {success ? (
            <Button onClick={handleClose} className="w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white">
              Continue
            </Button>
          ) : showSkipOption ? (
            <Button
              type="button"
              onClick={handleClose}
              className="w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white"
            >
              Continue Without Linking
            </Button>
          ) : (
            <Button
              type="button"
              onClick={handleLink}
              disabled={isLinking || !password}
              className="w-full bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white"
            >
              {isLinking ? "Linking..." : "Complete Sign-In"}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

