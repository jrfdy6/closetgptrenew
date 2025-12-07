"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Star } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Modern minimal geometric elements - lighter on mobile */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-35 md:opacity-55">
        <div className="pointer-events-none absolute top-10 md:top-20 left-5 md:left-10 w-24 md:w-32 h-24 md:h-32 bg-primary/25 dark:bg-primary/20 rounded-full blur-3xl"></div>
        <div className="pointer-events-none absolute top-32 md:top-40 right-10 md:right-20 w-20 md:w-24 h-20 md:h-24 bg-primary/20 dark:bg-accent/20 rounded-full blur-2xl"></div>
        <div className="pointer-events-none absolute bottom-20 md:bottom-32 left-1/4 w-16 md:w-20 h-16 md:h-20 bg-secondary/30 dark:bg-muted/50 rounded-full blur-2xl"></div>
        <div className="pointer-events-none absolute bottom-10 md:bottom-20 right-1/3 w-20 md:w-28 h-20 md:h-28 bg-accent/15 dark:bg-primary/25 rounded-full blur-3xl"></div>
      </div>
      
      {/* Hero Section - Mobile Optimized */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16 lg:py-24 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          
          {/* Logo - Optimized mobile size */}
          <div className="flex justify-center mb-6 sm:mb-8 md:mb-10">
            <Image 
              src="/logo-horizontal.png?v=2" 
              alt="Easy Outfit Logo" 
              width={600} 
              height={150}
              priority
              className="w-auto h-16 sm:h-24 md:h-32 lg:h-40 object-contain"
            />
          </div>
          
          {/* Modern Mobile-First Content Card */}
          <div className="bg-card/85 dark:bg-card/85 backdrop-blur-xl rounded-3xl md:rounded-[2rem] p-6 sm:p-8 md:p-12 mb-6 sm:mb-8 shadow-2xl shadow-primary/10 border border-border/40 dark:border-border/70 animate-fade-in">
            
            {/* Title - Display font for brand moment */}
            <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-4 sm:mb-5 tracking-tight leading-tight">
              Easy Outfit
            </h1>
            
            {/* Tagline - Body font for clarity */}
            <p className="font-body text-lg sm:text-xl md:text-2xl lg:text-3xl text-muted-foreground dark:text-foreground font-light leading-relaxed mb-6 sm:mb-8 px-2">
              Let&apos;s get you dressed ✨
            </p>
            
            {/* Feature badges - Better mobile spacing */}
            <div className="flex flex-wrap gap-2 sm:gap-3 justify-center mb-6 sm:mb-8 px-2">
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm">
                ✨ AI-Powered
              </span>
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm">
                👔 Personalized
              </span>
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm">
                🎨 Style Smart
              </span>
            </div>

            {/* Social proof / Quick stats - Mobile friendly */}
            <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 mb-6 sm:mb-8 text-xs sm:text-sm text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <div className="flex -space-x-1">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-[var(--copper-light)] to-[var(--copper-dark)] border-2 border-white dark:border-gray-900"></div>
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-[var(--copper-mid)] to-[var(--copper-dark)] border-2 border-white dark:border-gray-900"></div>
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-[var(--copper-light)] to-[var(--copper-mid)] border-2 border-white dark:border-gray-900"></div>
                </div>
                <span className="font-medium">1000+ Users</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" />
                <span className="ml-1 font-medium">5.0</span>
              </div>
            </div>
          </div>
          
          {/* CTA Buttons - Improved mobile layout */}
          <div className="flex flex-col gap-3 sm:gap-4 justify-center items-stretch sm:items-center max-w-md sm:max-w-none mx-auto">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                className="w-full sm:w-auto gradient-copper-gold hover:opacity-90 text-[#1A1510] dark:text-white px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-[var(--copper-dark)]/25 hover:shadow-2xl hover:shadow-[var(--copper-dark)]/30 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
              >
                Generate Today&apos;s Fit
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/onboarding?mode=guest" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                variant="outline" 
                className="w-full sm:w-auto bg-card/65 dark:bg-card/65 hover:bg-card/80 dark:hover:bg-secondary/80 backdrop-blur-xl border-2 border-border/60 dark:border-border/80 text-[var(--copper-dark)] dark:text-[var(--copper-light)] hover:text-[var(--copper-mid)] dark:hover:text-[var(--copper-mid)] px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              >
                Start the 2-minute style quiz
                <Sparkles className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>

          {/* Trust indicators - Mobile optimized */}
          <p className="mt-6 sm:mt-8 text-xs sm:text-sm text-muted-foreground font-medium">
            Free to start. No credit card required.
          </p>
        </div>
      </div>
    </div>
  );
}
