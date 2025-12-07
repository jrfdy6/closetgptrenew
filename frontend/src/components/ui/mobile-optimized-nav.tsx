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
      <div className="lg:hidden bg-background/95 dark:bg-card/90 border-b border-border/60 dark:border-border/70 px-4 py-3 backdrop-blur-xl">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/25">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="font-semibold text-lg text-card-foreground">Easy Outfit</span>
          </Link>

          {/* Right side controls */}
          <div className="flex items-center gap-2">
            {/* Search Button */}
            {onSearchClick && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onSearchClick}
                className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary"
              >
                <Search className="h-5 w-5" />
              </Button>
            )}

            {/* Notifications */}
            {notificationCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="p-2 relative text-muted-foreground hover:text-foreground hover:bg-secondary"
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
              className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary"
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
          <div className="absolute right-0 top-0 h-full w-80 max-w-[85vw] bg-background dark:bg-background border-l border-border/60 dark:border-border/70 shadow-xl">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-8">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-lg flex items-center justify-center shadow-lg shadow-amber-500/25">
                    <Sparkles className="h-5 w-5 text-white" />
                  </div>
                  <span className="font-semibold text-lg text-card-foreground">Easy Outfit</span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="p-2 text-muted-foreground hover:text-foreground hover:bg-secondary"
                >
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* User Info */}
              {user && (
                <div className="mb-6 p-4 bg-secondary dark:bg-card rounded-xl border border-border/70 dark:border-border/70">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] rounded-full flex items-center justify-center shadow-md shadow-amber-500/20">
                      <span className="text-white font-semibold text-sm">
                        {user.displayName?.charAt(0) || user.email?.charAt(0) || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-card-foreground">
                        {user.displayName || 'User'}
                      </p>
                      <p className="text-sm text-muted-foreground">
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
                          ? 'border-primary/60 bg-secondary dark:bg-card text-card-foreground'
                          : 'border-transparent text-muted-foreground hover:bg-secondary hover:text-foreground'
                      }`}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Quick Actions */}
              <div className="mt-8 pt-6 border-t border-border/60 dark:border-border/70">
                <h3 className="text-sm font-medium text-muted-foreground mb-3 uppercase tracking-wide">
                  Quick Actions
                </h3>
                <div className="space-y-2">
                  <Link
                    href="/outfits/generate"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-amber-500/20 hover:from-primary hover:to-accent/90 transition-all duration-200"
                  >
                    <Sparkles className="h-5 w-5" />
                    <span className="font-medium">Generate Outfit</span>
                  </Link>
                  <Link
                    href="/wardrobe"
                    onClick={() => setIsOpen(false)}
                    className="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:bg-secondary rounded-xl transition-all duration-200"
                  >
                    <Shirt className="h-5 w-5" />
                    <span className="font-medium">Add Items</span>
                  </Link>
                </div>
              </div>

              {/* Settings */}
              <div className="mt-6 pt-6 border-t border-border/60 dark:border-border/70">
                <Link
                  href="/settings"
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 text-muted-foreground hover:bg-secondary rounded-xl transition-all duration-200"
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
