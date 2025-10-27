"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
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
    <nav className="sticky top-0 z-50 glass-navbar glass-blur-strong glass-shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-18">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link
              href="/"
              className="group flex items-center space-x-3 text-lg sm:text-xl font-serif font-bold text-stone-900 dark:text-stone-100 hover:text-stone-700 dark:hover:text-stone-300 transition-all duration-300 ease-out hover:-translate-y-0.5"
            >
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-stone-900 dark:bg-stone-100 rounded-full flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg">
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white dark:text-stone-900 transition-transform duration-300 group-hover:rotate-12" />
              </div>
              <span className="transition-all duration-300">ClosetGPT</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="group relative flex items-center space-x-3 px-6 py-3 rounded-full text-sm font-medium text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 hover:bg-white/30 dark:hover:bg-white/10 backdrop-blur-xl glass-transition hover:-translate-y-0.5 hover:shadow-md"
                  >
                    <Icon className="w-5 h-5 transition-transform duration-200 group-hover:scale-110" />
                    <span>{item.label}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="text-xs bg-stone-200 dark:bg-stone-700 text-stone-800 dark:text-stone-200 border-0 transition-all duration-200 group-hover:scale-105">
                        {item.badge}
                      </Badge>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side - Theme Toggle and Sign Out */}
          <div className="hidden md:flex items-center space-x-4">
            <ThemeToggle />
            {user && (
              <Button
                onClick={handleSignOut}
                variant="outline"
                size="sm"
                className="rounded-full glass-button-secondary px-6 py-2"
              >
                Sign Out
              </Button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-3">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-3 rounded-full text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 hover:bg-white/30 dark:hover:bg-white/10 backdrop-blur-xl focus:outline-none focus:ring-2 focus:ring-stone-500/20 focus:ring-offset-2 glass-transition min-h-[44px] min-w-[44px]"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {isMenuOpen ? (
                <X className="block h-6 w-6" aria-hidden="true" />
              ) : (
                <Menu className="block h-6 w-6" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation with Glass Overlay */}
      {isMenuOpen && (
        <div className="md:hidden animate-in slide-in-from-top duration-200">
          <div className="px-4 pt-4 pb-6 space-y-3 glass-strong glass-blur-mega glass-border">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center space-x-4 px-6 py-4 rounded-2xl text-base font-medium text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 hover:bg-white/30 dark:hover:bg-white/10 backdrop-blur-xl glass-transition min-h-[44px]"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <Badge variant="secondary" className="text-xs bg-stone-200 dark:bg-stone-700 text-stone-800 dark:text-stone-200 border-0 ml-auto">
                      {item.badge}
                    </Badge>
                  )}
                </Link>
              );
            })}
            {user && (
              <button
                onClick={() => {
                  handleSignOut();
                  setIsMenuOpen(false);
                }}
                className="flex items-center space-x-4 w-full text-left px-6 py-4 rounded-2xl text-base font-medium text-stone-700 dark:text-stone-300 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50/50 dark:hover:bg-red-900/20 backdrop-blur-xl glass-transition min-h-[44px]"
              >
                <span className="w-5 h-5" />
                <span>Sign Out</span>
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
} 