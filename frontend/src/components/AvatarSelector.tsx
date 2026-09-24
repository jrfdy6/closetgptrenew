"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

interface AvatarSelectorProps {
  currentAvatar: string | null;
  onAvatarChange: (url: string) => void;
  initialGender?: "male" | "female";
  onComplete?: () => void;
}

// Retain the legacy component contract and any stored avatar. The former
// customization controls depended on absent generator and upload modules.
export default function AvatarSelector({ currentAvatar, onComplete }: AvatarSelectorProps) {
  const [failedAvatar, setFailedAvatar] = useState<string | null>(null);

  return (
    <div className="space-y-4">
      {currentAvatar && currentAvatar !== failedAvatar ? (
        <img
          src={currentAvatar}
          alt="Your current avatar"
          className="h-48 w-48 rounded-lg object-contain"
          onError={() => setFailedAvatar(currentAvatar)}
        />
      ) : currentAvatar ? (
        <p className="text-sm text-muted-foreground">Your saved avatar could not be displayed.</p>
      ) : null}
      <p role="status" className="text-sm text-muted-foreground">
        Avatar customization and uploads are currently unavailable.
      </p>
      <Button disabled={!currentAvatar} onClick={() => { if (currentAvatar) onComplete?.(); }}>
        Continue
      </Button>
    </div>
  );
}
