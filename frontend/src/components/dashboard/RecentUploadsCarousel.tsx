'use client';

import { useState, useEffect } from 'react';
import { useWardrobe } from '@/hooks/useWardrobe';
import { WardrobeItem } from '@/types/wardrobe';

export default function RecentUploadsCarousel() {
  const { wardrobe } = useWardrobe();
  const [recentItems, setRecentItems] = useState<WardrobeItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (!wardrobe) return;

    // Sort items by creation date and take the 5 most recent
    const sorted = [...wardrobe].sort((a, b) => b.createdAt - a.createdAt).slice(0, 5);
    setRecentItems(sorted);
  }, [wardrobe]);

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % recentItems.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + recentItems.length) % recentItems.length);
  };

  if (!recentItems.length) {
    return (
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">📸 Recent Uploads</h2>
        <div className="text-gray-500">No recent uploads found.</div>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">📸 Recent Uploads</h2>
      <div className="relative">
        <div className="overflow-hidden rounded-lg">
          <div
            className="flex transition-transform duration-300 ease-in-out"
            style={{ transform: `translateX(-${currentIndex * 100}%)` }}
          >
            {recentItems.map((item) => (
              <div
                key={item.id}
                className="w-full flex-shrink-0"
              >
                <div className="relative aspect-square">
                  <img
                    src={item.imageUrl}
                    alt={item.name}
                    className="w-full h-full object-cover rounded-lg"
                  />
                  <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/60 to-transparent rounded-b-lg">
                    <h3 className="text-white font-semibold">{item.name}</h3>
                    <p className="text-white/80 text-sm capitalize">{item.type}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {recentItems.length > 1 && (
          <>
            <button
              onClick={prevSlide}
              className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg"
            >
              ←
            </button>
            <button
              onClick={nextSlide}
              className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg"
            >
              →
            </button>
          </>
        )}

        <div className="flex justify-center mt-4 space-x-2">
          {recentItems.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentIndex(index)}
              className={`w-2 h-2 rounded-full ${
                index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
    </section>
  );
} 