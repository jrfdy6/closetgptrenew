'use client';

import { useState } from 'react';
import Image from 'next/image';
import { ImageOff } from 'lucide-react';

interface WardrobeCardImageProps {
  itemId: string;
  alt: string;
  thumbnailUrl?: string;
  backgroundRemovedUrl?: string;
  imageUrl: string;
}

export default function WardrobeCardImage({
  itemId, alt, thumbnailUrl, backgroundRemovedUrl, imageUrl,
}: WardrobeCardImageProps) {
  const sources = Array.from(new Set(
    [thumbnailUrl, backgroundRemovedUrl, imageUrl]
      .filter((source): source is string => typeof source === 'string' && source.trim().length > 0),
  ));

  // A newly processed asset or different garment gets a fresh attempt sequence.
  return <ImageWithFallback key={JSON.stringify([itemId, ...sources])} sources={sources} alt={alt} />;
}

function ImageWithFallback({ sources, alt }: { sources: string[]; alt: string }) {
  const [sourceIndex, setSourceIndex] = useState(0);
  const source = sources[sourceIndex];

  if (!source) return (
    <div role="img" aria-label={`${alt} image unavailable`} className="flex h-full w-full flex-col items-center justify-center gap-2 px-4 text-center text-sm text-muted-foreground">
      <ImageOff className="h-8 w-8" aria-hidden="true" />
      <span>Image unavailable</span>
    </div>
  );

  return <Image
    key={source}
    src={source}
    alt={alt}
    fill
    sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, (max-width: 1024px) 25vw, 20vw"
    className="object-cover transition-all duration-300 group-hover:scale-105"
    onError={() => {
      // Repeated or late errors from an older image must not skip the next URL.
      setSourceIndex(current => current === sourceIndex ? current + 1 : current);
    }}
  />;
}
