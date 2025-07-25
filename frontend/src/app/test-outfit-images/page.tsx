'use client';

import React from 'react';

const testOutfits = [
  { id: 'M-CB1', imageUrl: '/images/outfit-quiz/M-CB1.png', description: 'Linen shirt, cargo trousers, fisherman cardigan' },
  { id: 'F-CB1', imageUrl: '/images/outfit-quiz/F-CB1.png', description: 'Floral maxi dress, cropped knit cardigan, leather boots' },
  { id: 'M-CB2', imageUrl: '/images/outfit-quiz/M-CB2.png', description: 'Henley, cotton pants, leather sandals' },
  { id: 'F-CB2', imageUrl: '/images/outfit-quiz/F-CB2.png', description: 'Peasant blouse, patchwork skirt, vest, floppy hat' },
];

export default function TestOutfitImages() {
  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Outfit Image Test</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {testOutfits.map((outfit) => (
          <div key={outfit.id} className="border rounded-lg overflow-hidden">
            <div className="aspect-square bg-gray-100">
              <img
                src={`${outfit.imageUrl}?v=2`}
                alt={outfit.description}
                className="w-full h-full object-contain"
                onError={(e) => {
                  console.error('Image failed to load:', outfit.imageUrl);
                  e.currentTarget.style.display = 'none';
                }}
                onLoad={() => {
                  console.log('Image loaded successfully:', outfit.imageUrl);
                }}
              />
            </div>
            <div className="p-4">
              <h3 className="font-semibold text-sm">{outfit.id}</h3>
              <p className="text-xs text-gray-600 mt-1">{outfit.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
} 