"use client";

import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { signOutUser } from "@/lib/auth";
import { useFirebase } from "@/lib/firebase-context";
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { Menu, X, Sparkles, Home, Shirt, Palette, User, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import dynamic from 'next/dynamic';

const ThemeToggle = dynamic(() => import('@/components/ThemeToggle'), {
  ssr: false,
  loading: () => (
    <div className="w-8 h-8 bg-muted rounded-xl animate-pulse" />
  ),
});

export default function Navigation() {
  const router = useRouter();
  const { user } = useFirebase();
  const pathname = usePathname();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);

  // Ensure component is mounted on client before rendering Portal
  useEffect(() => {
    setIsMounted(true);
    return () => setIsMounted(false);
  }, []);

  const handleSignOut = async () => {
    try {
      await signOutUser();
      router.push("/signin");
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen((prev) => {
      const newState = !prev;
      console.log(' Menu toggle clicked! State changing from', prev, 'to', newState);
      return newState;
    });
  };

  // Handle body scroll lock when menu opens/closes
  useEffect(() => {
    if (typeof document !== 'undefined') {
      if (isMenuOpen) {
        // Lock body scroll when menu is open
        document.body.style.overflow = 'hidden';
        console.log('✅ Menu opened - body scroll locked');
      } else {
        // Restore body scroll when menu closes
        document.body.style.overflow = '';
        console.log('✅ Menu closed - body scroll restored');
      }
    }
    
    // Cleanup function
    return () => {
      if (typeof document !== 'undefined') {
        document.body.style.overflow = '';
      }
    };
  }, [isMenuOpen]);


  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: Home },
    { href: "/wardrobe", label: "Wardrobe", icon: Shirt },
    { href: "/outfits", label: "Outfits", icon: Palette },
    { href: "/profile", label: "Profile", icon: User },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-[#FAFAF9]/90 dark:bg-[#2C2119]/85 backdrop-blur-2xl border-b border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-18">
          {/* Logo - Cleaner mobile version */}
          <div className="flex-shrink-0">
            <Link
              href="/"
              className="flex items-center space-x-2 transition-opacity duration-200 hover:opacity-70"
            >
              <Image
                src="/logo-horizontal.png?v=2"
                alt="Easy Outfit App"
                width={150}
                height={40}
                priority
                className="h-8 sm:h-10 w-auto object-contain"
              />
              <span className="hidden sm:inline text-lg font-semibold bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent">
                Easy Outfit
              </span>
            </Link>
          </div>

          {/* Desktop Navigation - Modern pill design */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={cn(
                      "group flex items-center space-x-2 px-4 py-2.5 min-h-[44px] h-[44px] rounded-xl text-sm font-medium transition-all duration-200",
                      "text-[#57534E] dark:text-[#C4BCB4]",
                      "hover:text-[#1C1917] dark:hover:text-[#F8F5F1]",
                      "hover:bg-[#F5F0E8] dark:hover:bg-[#3D2F24]",
                      isActive && "text-[#1C1917] dark:text-[#F8F5F1] bg-[#F5F0E8] dark:bg-[#3D2F24]"
                    )}
                  >
                    <Icon className={cn(
                      "w-4 h-4 transition-transform duration-200",
                      isActive ? "text-[#FFB84C]" : "group-hover:scale-110"
                    )} />
                    <span>{item.label}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="text-xs ml-1">
                        {item.badge}
                      </Badge>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side - Cleaner design */}
          <div className="hidden md:flex items-center space-x-3">
            <ThemeToggle />
            {user && (
              <Button
                onClick={handleSignOut}
                variant="outline"
                size="sm"
                className="rounded-xl border-[#F5F0E8]/70 dark:border-[#3D2F24]/80 text-[#57534E] dark:text-[#C4BCB4] hover:text-red-600 dark:hover:text-red-400 hover:border-red-300 dark:hover:border-red-600 transition-colors"
              >
                Sign Out
              </Button>
            )}
          </div>

          {/* Mobile menu button - Larger touch target */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                toggleMenu();
              }}
              type="button"
              className="inline-flex items-center justify-center p-2.5 rounded-xl text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#3D2F24] transition-all duration-200 min-h-[44px] min-w-[44px] relative z-[100]"
              aria-expanded={isMenuOpen}
              aria-label="Toggle menu"
            >
              {isMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Modern Mobile Navigation - Rendered via Portal for proper z-index */}
      {isMounted && isMenuOpen && typeof document !== 'undefined' && createPortal(
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] md:hidden transition-opacity duration-200"
            onClick={() => {
              console.log('🔴 Backdrop clicked, closing menu');
              setIsMenuOpen(false);
            }}
            aria-hidden="true"
          />
          
          {/* Menu Panel */}
          <div 
            className="fixed inset-x-0 top-16 bottom-0 bg-[#FAFAF9] dark:bg-[#1A1510] z-[70] md:hidden overflow-y-auto shadow-2xl"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Navigation menu"
          >
            {/* Menu Header with Close Button */}
            <div className="sticky top-0 z-[71] bg-[#FAFAF9] dark:bg-[#1A1510] border-b border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 px-4 py-3 flex justify-between items-center">
              <span className="font-semibold text-lg text-[#1C1917] dark:text-[#F8F5F1]">Menu</span>
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  console.log('🔴 Close button clicked');
                  setIsMenuOpen(false);
                }}
                className="inline-flex items-center justify-center p-2 rounded-xl text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#3D2F24] transition-all duration-200 min-h-[44px] min-w-[44px]"
                aria-label="Close menu"
                type="button"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <div className="p-4 space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center space-x-4 px-5 py-4 rounded-2xl text-base font-semibold transition-all duration-200 min-h-[56px] h-[56px] border-2 border-transparent text-[#1C1917] dark:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] hover:border-[#FFB84C]/60 dark:hover:border-[#FF9400]/50"
                    onClick={() => {
                      console.log('🔴 Menu link clicked:', item.href);
                      setIsMenuOpen(false);
                    }}
                  >
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFCC66]/40 to-[#FF9400]/40 dark:from-[#FFB84C]/20 dark:to-[#FF9400]/20 flex items-center justify-center">
                      <Icon className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                    </div>
                    <span className="flex-1">{item.label}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </Link>
                );
              })}
              
              {/* Divider */}
              {user && (
                <div className="border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 my-4" />
              )}
              
              {user && (
                <button
                  onClick={() => {
                    handleSignOut();
                    setIsMenuOpen(false);
                  }}
                  className="flex items-center space-x-4 w-full text-left px-5 py-4 rounded-2xl text-base font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200 min-h-[56px] border-2 border-transparent hover:border-red-200 dark:hover:border-red-700"
                >
                  <div className="w-10 h-10 rounded-xl bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </div>
                  <span className="flex-1">Sign Out</span>
                </button>
              )}
            </div>
          </div>
        </>,
        document.body
      )}
    </nav>
  );
} 