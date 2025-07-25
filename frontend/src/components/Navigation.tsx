"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { signOut } from "firebase/auth";
import { auth } from "@/lib/firebase/config";
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
      await signOut(auth);
      router.push("/login");
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
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/50 dark:border-gray-700/50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-14 sm:h-16">
          {/* Logo */}
          <div className="flex-shrink-0">
            <Link
              href="/"
              className="group flex items-center space-x-2 text-lg sm:text-xl font-bold bg-gradient-to-r from-emerald-600 to-emerald-700 bg-clip-text text-transparent hover:from-emerald-700 hover:to-emerald-800 transition-all duration-300 ease-out hover:-translate-y-0.5"
            >
              <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg">
                <Sparkles className="w-3 h-3 sm:w-4 sm:h-4 text-white transition-transform duration-300 group-hover:rotate-12" />
              </div>
              <span className="transition-all duration-300 group-hover:text-emerald-600">ClosetGPT</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:block">
            <div className="ml-10 flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className="group relative flex items-center space-x-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 transition-all duration-300 ease-out hover:-translate-y-0.5 hover:shadow-md"
                  >
                    <Icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" />
                    <span>{item.label}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="text-xs bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-0 transition-all duration-200 group-hover:scale-105">
                        {item.badge}
                      </Badge>
                    )}
                    <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-emerald-100/50 to-yellow-100/50 opacity-0 group-hover:opacity-100 transition-all duration-300 ease-out" />
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Right side - Theme Toggle and Sign Out */}
          <div className="hidden md:flex items-center space-x-3">
            <ThemeToggle />
            {user && (
              <Button
                onClick={handleSignOut}
                variant="outline"
                size="sm"
                className="rounded-xl border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-emerald-300 dark:hover:border-emerald-600 transition-all duration-200"
              >
                Sign Out
              </Button>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center space-x-2">
            <ThemeToggle />
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-xl text-gray-700 dark:text-gray-300 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:ring-offset-2 transition-all duration-200 min-h-[44px] min-w-[44px]"
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

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden animate-in slide-in-from-top duration-200">
          <div className="px-4 pt-2 pb-4 space-y-2 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md border-t border-gray-200/50 dark:border-gray-700/50">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex items-center space-x-3 px-4 py-3 rounded-xl text-base font-medium text-gray-700 dark:text-gray-300 hover:text-emerald-600 dark:hover:text-emerald-400 hover:bg-emerald-50 dark:hover:bg-emerald-950/20 transition-all duration-200 min-h-[44px]"
                  onClick={() => setIsMenuOpen(false)}
                >
                  <Icon className="w-5 h-5" />
                  <span>{item.label}</span>
                  {item.badge && (
                    <Badge variant="secondary" className="text-xs bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-0 ml-auto">
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
                className="flex items-center space-x-3 w-full text-left px-4 py-3 rounded-xl text-base font-medium text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/10 transition-all duration-200 min-h-[44px]"
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