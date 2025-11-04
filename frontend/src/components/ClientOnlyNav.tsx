"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";

// Dynamically import with no SSR
const BottomNav = dynamic(() => import("@/components/BottomNav"), {
  ssr: false,
});

const FloatingActionButton = dynamic(() => import("@/components/FloatingActionButton"), {
  ssr: false,
});

interface ClientOnlyNavProps {
  onFabClick: () => void;
  fabLabel?: string;
}

export default function ClientOnlyNav({ onFabClick, fabLabel }: ClientOnlyNavProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render anything during SSR or before hydration
  if (!mounted) {
    return null;
  }

  return (
    <>
      <BottomNav />
      <FloatingActionButton onClick={onFabClick} ariaLabel={fabLabel} />
    </>
  );
}

