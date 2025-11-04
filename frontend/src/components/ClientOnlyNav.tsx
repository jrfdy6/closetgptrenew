"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import dynamic from "next/dynamic";

// Dynamically import with no SSR
const BottomNav = dynamic(() => import("@/components/BottomNav"), {
  ssr: false,
});

const FloatingActionButton = dynamic(() => import("@/components/FloatingActionButton"), {
  ssr: false,
});

// NO PROPS - All logic handled internally to avoid serialization
export default function ClientOnlyNav() {
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render anything during SSR or before hydration
  if (!mounted) {
    return null;
  }

  // Handle FAB click - always navigates to outfit generation
  const handleFabClick = () => {
    router.push('/outfits/generate');
  };

  // Dynamic aria label based on page
  const getFabLabel = () => {
    if (pathname?.includes('/dashboard')) return "Generate outfit for today";
    if (pathname?.includes('/wardrobe')) return "Generate outfit from your wardrobe";
    if (pathname?.includes('/outfits')) return "Generate new outfit";
    if (pathname?.includes('/profile')) return "Generate outfit";
    return "Generate outfit";
  };

  return (
    <>
      <BottomNav />
      <FloatingActionButton 
        onClick={handleFabClick} 
        ariaLabel={getFabLabel()} 
      />
    </>
  );
}

