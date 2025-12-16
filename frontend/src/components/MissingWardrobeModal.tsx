"use client";

import React, { useState } from 'react';
import GuidedUploadWizard from './GuidedUploadWizard';

interface MissingWardrobeModalProps {
  userId: string;
  isOpen: boolean;
  onComplete: () => void;
  targetCount?: number;
}

/**
 * Blocking modal that prevents access to Wardrobe, Outfits, and Dashboard pages
 * until the user has uploaded at least 10 items to their wardrobe.
 * 
 * Uses the same GuidedUploadWizard component as the onboarding flow
 * for a consistent user experience.
 */
export default function MissingWardrobeModal({
  userId,
  isOpen,
  onComplete,
  targetCount = 10
}: MissingWardrobeModalProps) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[9999] bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div className="w-full h-full">
        <GuidedUploadWizard
          userId={userId}
          targetCount={targetCount}
          onComplete={onComplete}
          stylePersona="default"
          gender="Male"
        />
      </div>
    </div>
  );
}

