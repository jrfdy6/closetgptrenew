'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Menu, 
  X, 
  Home, 
  Shirt, 
  Sparkles, 
  User, 
  Settings,
  Bell,
  Search
} from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface MobileOptimizedNavProps {
  user?: any;
  notificationCount?: number;
  onSearchClick?: () => void;
}

export default function MobileOptimizedNav({ 
  user, 
  notificationCount = 0,
  onSearchClick 
}: MobileOptimizedNavProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: Home },
    { href: '/wardrobe', label: 'Wardrobe', icon: Shirt },
    { href: '/outfits', label: 'My Looks', icon: Sparkles },
    { href: '/profile', label: 'Profile', icon: User },
  ];

  const isActive = (href: string) => {
    if (href === '/dashboard') return pathname === '/dashboard';
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden bg-[#FAFAF9]/95 dark:bg-[#1A1A1A]/90 border-b border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 px-4 py-3 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-[#1C1917] dark:text-[#F8F5F1]">Easy Outfit</span>
          </Link>

          {/* Right side controls */}
          <div className="flex items-center gap-2">
            {/* Search Button */}
            {onSearchClick && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onSearchClick}
                className="p-2 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#262626]"
              >
                <Search className="h-5 w-5" />
              </Button>
            )}

            {/* Notifications */}
            {notificationCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="p-2 relative text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#262626]"
              >
                <Bell className="h-5 w-5" />
                <Badge 
                  variant="destructive" 
                  className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 flex items-center justify-center text-xs"
                >
                  {notificationCount}
                </Badge>
              </Button>
            )}

            {/* Menu Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#262626]"
            >
              {isOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {isOpen && (
        <div className="lg:hidden fixed inset-0 z-50">
          <div 
            className="absolute inset-0 bg-black/50" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 top-0 h-full w-80 max-w-[85vw] bg-[#FAFAF9] dark:bg-[#0D0D0D] border-l border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70 shadow-xl">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/25">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <span className="font-semibold text-lg text-[#1C1917] dark:text-[#F8F5F1]">Easy Outfit</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="p-2 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#262626]"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* User Info */}
              {user && (
                <div className="mb-6 p-4 bg-[#F5F0E8] dark:bg-[#1A1A1A] rounded-xl border border-[#F5F0E8]/70 dark:border-[#2E2E2E]/70">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-full flex items-center justify-center shadow-md shadow-amber-500/20">
                      <span className="text-white font-semibold text-sm">
                        {user.displayName?.charAt(0) || user.email?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-[#1C1917] dark:text-[#F8F5F1]">
                        {user.displayName || 'User'}
                      </p>
                      <p className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
                        {user.email}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Navigation Items */}
              <nav className="space-y-2">
                {navItems.map((item) => {
                  const Icon = item.icon;
                  const active = isActive(item.href);
                  
                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => setIsOpen(false)}
                      className={`flex items-center gap-3 px-4 py-3 rounded-xl border transition-all duration-200 ${
                        active
                          ? 'border-[#FFB84C]/60 bg-[#F5F0E8] dark:bg-[#1A1A1A] text-[#1C1917] dark:text-[#F8F5F1]'
                          : 'border-transparent text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#262626] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Quick Actions */}
              <div className="mt-8 pt-6 border-t border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
                <h3 className="text-sm font-medium text-[#8A827A] dark:text-[#C4BCB4] mb-3 uppercase tracking-wide">
                  Quick Actions
                </h3>
                <div className="space-y-2">
                  <Link
                    href="/outfits/generate"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white shadow-lg shadow-amber-500/20 hover:from-[#FFB84C] hover:to-[#FF7700] transition-all duration-200"
                  >
                    <Sparkles className="h-5 w-5" />
                    <span className="font-medium">Generate Outfit</span>
                  </Link>
                  <Link
                    href="/wardrobe"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#262626] rounded-xl transition-all duration-200"
                  >
                    <Shirt className="h-5 w-5" />
                    <span className="font-medium">Add Items</span>
                  </Link>
                </div>
              </div>

              {/* Settings */}
              <div className="mt-6 pt-6 border-t border-[#F5F0E8]/60 dark:border-[#2E2E2E]/70">
                <Link
                  href="/settings"
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#262626] rounded-xl transition-all duration-200"
                >
                  <Settings className="h-5 w-5" />
                  <span className="font-medium">Settings</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Navigation (hidden on mobile) */}
      <div className="hidden lg:block">
        {/* Your existing desktop navigation component */}
      </div>
    </>
  );
}
