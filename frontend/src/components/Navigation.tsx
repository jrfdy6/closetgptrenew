"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { signOutUser } from "@/lib/auth";
import { useFirebase } from "@/lib/firebase-context";
import { useState } from "react";
import { Menu, X, Sparkles, Home, Shirt, Palette, User, Wand2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
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
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const handleSignOut = async () => {
    try {
      await signOutUser();
      router.push("/signin");
    } catch (error) {
      console.error("Error signing out:", error);
    }
  };

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const navItems = [
    { href: "/dashboard", label: "Dashboard", icon: Home },
    { href: "/wardrobe", label: "Wardrobe", icon: Shirt },
    { href: "/outfits", label: "Outfits", icon: Palette },
    { href: "/profile", label: "Profile", icon: User },
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-2xl border-b border-gray-200/50 dark:border-gray-800/50 shadow-sm">
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
              <span className="hidden sm:inline text-lg font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                Easy Outfit
              </span>
            </Link>
          </div>

          {/* Desktop Navigation - Modern pill design */}
          <div className="hidden md:block">
            <div className="flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="group flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-all duration-200"
                  >
                    <Icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" />
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
                className="rounded-xl border-gray-300 dark:border-gray-700 hover:border-red-400 dark:hover:border-red-600 hover:text-red-600 dark:hover:text-red-400"
              >
                Sign Out
              </Button>
            )}
          </div>

          {/* Mobile menu button - Larger touch target */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2.5 rounded-xl text-gray-700 dark:text-gray-300 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-900/20 transition-all duration-200 min-h-[44px] min-w-[44px]"
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

      {/* Modern Mobile Navigation - Full screen overlay */}
      {isMenuOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 md:hidden animate-in fade-in duration-200"
            onClick={() => setIsMenuOpen(false)}
          />
          
          {/* Menu Panel */}
          <div className="fixed inset-x-0 top-16 bottom-0 bg-white dark:bg-gray-900 z-50 md:hidden animate-in slide-in-from-top duration-300 overflow-y-auto">
            <div className="p-4 space-y-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="flex items-center space-x-4 px-5 py-4 rounded-2xl text-base font-semibold text-gray-900 dark:text-gray-100 hover:bg-gradient-to-r hover:from-amber-50 hover:to-orange-50 dark:hover:from-amber-900/20 dark:hover:to-orange-900/20 transition-all duration-200 min-h-[56px] border-2 border-transparent hover:border-amber-200 dark:hover:border-amber-800"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900/30 dark:to-orange-900/30 flex items-center justify-center">
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
                <div className="border-t border-gray-200 dark:border-gray-800 my-4" />
              )}
              
              {user && (
                <button
                  onClick={() => {
                    handleSignOut();
                    setIsMenuOpen(false);
                  }}
                  className="flex items-center space-x-4 w-full text-left px-5 py-4 rounded-2xl text-base font-semibold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-all duration-200 min-h-[56px] border-2 border-transparent hover:border-red-200 dark:hover:border-red-800"
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
        </>
      )}
    </nav>
  );
} 