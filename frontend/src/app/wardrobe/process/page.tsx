'use client';

import React from 'react';
import { WardrobeProcessor } from '@/components/WardrobeProcessor';

export default function ProcessWardrobePage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Wardrobe Processing</h1>
      <WardrobeProcessor />
    </div>
  );
} 