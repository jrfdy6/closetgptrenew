"use client";

import React from 'react';
import { Heart, Sparkles, Star, Sun } from 'lucide-react';

interface BodyPositiveMessageProps {
  variant?: 'default' | 'outfit' | 'profile' | 'wardrobe';
  className?: string;
}

const BODY_POSITIVE_MESSAGES = {
  default: [
    "You are beautiful exactly as you are! ✨",
    "Your body is perfect for you! 💕",
    "Style is about confidence, not size! 🌟",
    "You deserve to feel amazing in your clothes! 💖",
    "Every body is a good body! 🌈"
  ],
  outfit: [
    "This outfit looks amazing on you! ✨",
    "You're rocking this look! 💫",
    "Confidence is your best accessory! 💕",
    "You look absolutely stunning! 🌟",
    "This style suits you perfectly! 💖"
  ],
  profile: [
    "Your unique style is beautiful! ✨",
    "Embrace your authentic self! 💕",
    "You are worthy of feeling confident! 🌟",
    "Your body tells your story beautifully! 💖",
    "Style is about expressing who you are! 🌈"
  ],
  wardrobe: [
    "Your wardrobe celebrates you! ✨",
    "Every piece you choose is perfect for you! 💕",
    "You have amazing style! 🌟",
    "Your clothes should make you feel confident! 💖",
    "You're building a wardrobe that loves you back! 🌈"
  ]
};

export default function BodyPositiveMessage({ 
  variant = 'default', 
  className = '' 
}: BodyPositiveMessageProps) {
  const messages = BODY_POSITIVE_MESSAGES[variant];
  const randomMessage = messages[Math.floor(Math.random() * messages.length)];
  
  const icons = {
    default: <Heart className="w-4 h-4 text-pink-500" />,
    outfit: <Sparkles className="w-4 h-4 text-yellow-500" />,
    profile: <Star className="w-4 h-4 text-blue-500" />,
    wardrobe: <Sun className="w-4 h-4 text-orange-500" />
  };

  return (
    <div className={`flex items-center gap-2 text-sm text-gray-700 bg-gradient-to-r from-pink-50 to-purple-50 p-3 rounded-lg border border-pink-200 ${className}`}>
      {icons[variant]}
      <span className="font-medium">{randomMessage}</span>
    </div>
  );
}

// Hook for getting random body positive messages
export function useBodyPositiveMessage(variant: keyof typeof BODY_POSITIVE_MESSAGES = 'default') {
  const messages = BODY_POSITIVE_MESSAGES[variant];
  return messages[Math.floor(Math.random() * messages.length)];
}







