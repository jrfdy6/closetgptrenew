"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, Shirt, Palette, User } from "lucide-react";
import { cn } from "@/lib/utils";

export default function BottomNav() {
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);

  // Only render on client to avoid SSR issues
  useEffect(() => {
    setMounted(true);
  }, []);

  const navItems = [
    { 
      href: "/dashboard", 
      label: "Home", 
      icon: Home,
      active: pathname === "/dashboard"
    },
    { 
      href: "/wardrobe", 
      label: "Closet", 
      icon: Shirt,
      active: pathname === "/wardrobe"
    },
    { 
      href: "/outfits", 
      label: "Looks", 
      icon: Palette,
      active: pathname === "/outfits" || pathname?.startsWith("/outfits/")
    },
    { 
      href: "/profile", 
      label: "Profile", 
      icon: User,
      active: pathname === "/profile"
    },
  ];

  if (!mounted) {
    return null;
  }

  return (
    <nav 
      className="fixed bottom-0 left-0 right-0 z-40 border-t border-border/50 dark:border-border bg-card/80 dark:bg-card/80 backdrop-blur-2xl"
      aria-label="Bottom navigation"
    >
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-4 h-14">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = item.active;
            
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex flex-col items-center justify-center gap-1 transition-all duration-200",
                  "min-h-[44px]", // WCAG touch target
                  isActive 
                    ? "text-primary" 
                    : "text-muted-foreground hover:text-foreground"
                )}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon 
                  className={cn(
                    "w-6 h-6 transition-transform duration-200",
                    isActive && "scale-110"
                  )} 
                />
                <span className={cn(
                  "text-[11px] font-medium",
                  isActive && "font-semibold"
                )}>
                  {item.label}
                </span>
                
                {/* Active indicator */}
                {isActive && (
                  <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-t-full" />
                )}
              </Link>
            );
          })}
        </div>
      </div>
      
      {/* Safe area spacer for iOS */}
      <div className="h-[env(safe-area-inset-bottom)]" />
    </nav>
  );
}

