"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Star } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-50 to-orange-50 dark:from-gray-950 dark:via-amber-950 dark:to-orange-950 relative overflow-hidden">
      {/* Modern minimal geometric elements - lighter on mobile */}
      <div className="absolute inset-0 overflow-hidden opacity-40 md:opacity-60">
        <div className="absolute top-10 md:top-20 left-5 md:left-10 w-24 md:w-32 h-24 md:h-32 bg-orange-500/20 rounded-full blur-3xl"></div>
        <div className="absolute top-32 md:top-40 right-10 md:right-20 w-20 md:w-24 h-20 md:h-24 bg-amber-500/20 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 md:bottom-32 left-1/4 w-16 md:w-20 h-16 md:h-20 bg-yellow-500/15 rounded-full blur-2xl"></div>
        <div className="absolute bottom-10 md:bottom-20 right-1/3 w-20 md:w-28 h-20 md:h-28 bg-orange-500/20 rounded-full blur-3xl"></div>
      </div>
      
      {/* Hero Section - Mobile Optimized */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16 lg:py-24 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          
          {/* Logo - Optimized mobile size */}
          <div className="flex justify-center mb-6 sm:mb-8 md:mb-10">
            <Image 
              src="/logo-horizontal.png?v=2" 
              alt="Easy Outfit App Logo" 
              width={600} 
              height={150}
              priority
              className="w-auto h-16 sm:h-24 md:h-32 lg:h-40 object-contain"
            />
          </div>
          
          {/* Modern Mobile-First Content Card */}
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-3xl md:rounded-[2rem] p-6 sm:p-8 md:p-12 mb-6 sm:mb-8 shadow-2xl shadow-amber-500/10 border border-white/20 dark:border-gray-700/30 animate-fade-in">
            
            {/* Title - Larger and bolder for mobile */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold bg-gradient-to-r from-amber-600 via-orange-600 to-amber-700 bg-clip-text text-transparent mb-4 sm:mb-5 tracking-tight leading-tight">
              Easy Outfit App
            </h1>
            
            {/* Tagline - Better mobile readability */}
            <p className="text-lg sm:text-xl md:text-2xl lg:text-3xl text-gray-700 dark:text-gray-300 font-light leading-relaxed mb-6 sm:mb-8 px-2">
              The future of getting dressed
            </p>
            
            {/* Feature badges - Better mobile spacing */}
            <div className="flex flex-wrap gap-2 sm:gap-3 justify-center mb-6 sm:mb-8 px-2">
              <span className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-amber-900 dark:text-amber-100 border border-amber-200/50 dark:border-amber-700/50 shadow-sm backdrop-blur-sm">
                ✨ AI-Powered
              </span>
              <span className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-amber-900 dark:text-amber-100 border border-amber-200/50 dark:border-amber-700/50 shadow-sm backdrop-blur-sm">
                👔 Personalized
              </span>
              <span className="bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-amber-900 dark:text-amber-100 border border-amber-200/50 dark:border-amber-700/50 shadow-sm backdrop-blur-sm">
                🎨 Style Smart
              </span>
            </div>

            {/* Social proof / Quick stats - Mobile friendly */}
            <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 mb-6 sm:mb-8 text-xs sm:text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-1.5">
                <div className="flex -space-x-1">
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 border-2 border-white dark:border-gray-900"></div>
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-orange-400 to-red-500 border-2 border-white dark:border-gray-900"></div>
                  <div className="w-6 h-6 sm:w-7 sm:h-7 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 border-2 border-white dark:border-gray-900"></div>
                </div>
                <span className="font-medium">1000+ Users</span>
              </div>
              <div className="flex items-center gap-1">
                <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                <span className="ml-1 font-medium">5.0</span>
              </div>
            </div>
          </div>
          
          {/* CTA Buttons - Improved mobile layout */}
          <div className="flex flex-col gap-3 sm:gap-4 justify-center items-stretch sm:items-center max-w-md sm:max-w-none mx-auto">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                className="w-full sm:w-auto bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-amber-500/25 hover:shadow-2xl hover:shadow-amber-500/30 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/onboarding" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                variant="outline" 
                className="w-full sm:w-auto bg-white/60 dark:bg-gray-900/60 hover:bg-white/80 dark:hover:bg-gray-900/80 backdrop-blur-xl border-2 border-amber-200 dark:border-amber-800 text-amber-900 dark:text-amber-100 hover:text-amber-950 dark:hover:text-amber-50 px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
              >
                Take Style Quiz
                <Sparkles className="ml-2 h-5 w-5" />
              </Button>
            </Link>
          </div>

          {/* Trust indicators - Mobile optimized */}
          <p className="mt-6 sm:mt-8 text-xs sm:text-sm text-gray-500 dark:text-gray-500 font-medium">
            Free to start • No credit card required
          </p>
        </div>
      </div>
    </div>
  );
}
