"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-stone-100 to-orange-50 dark:from-stone-900 dark:via-amber-900 dark:to-orange-900 relative overflow-hidden">
      {/* Enhanced geometric elements with glass effect */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-32 h-32 bg-orange-500/20 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-red-500/20 rounded-full blur-2xl"></div>
        <div className="absolute bottom-32 left-1/4 w-20 h-20 bg-yellow-500/20 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 right-1/3 w-28 h-28 bg-pink-500/20 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-40 h-40 bg-blue-500/15 rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute top-1/3 right-1/4 w-24 h-24 bg-purple-500/20 rounded-full blur-2xl"></div>
      </div>
      
      {/* Hero Section with Liquid Glass Card */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 lg:py-32 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Glass hero card */}
          <div className="glass-float-hover p-8 sm:p-12 mb-8 animate-fade-in glass-shadow-strong">
            <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-6 sm:mb-8 text-stone-900 dark:text-stone-100 tracking-tight leading-tight">
              ClosetGPT
            </h1>
            <p className="text-lg sm:text-xl md:text-2xl text-stone-600 dark:text-stone-400 mb-8 font-light leading-relaxed">
              Your AI-powered personal stylist
            </p>
            
            {/* Feature badges with glass effect */}
            <div className="flex flex-wrap gap-3 justify-center mb-8">
              <span className="glass-light px-4 py-2 rounded-full text-sm font-medium text-stone-700 dark:text-stone-300 glass-transition hover:bg-white/40 dark:hover:bg-gray-900/40 hover:scale-105">
                ✨ AI-Powered
              </span>
              <span className="glass-light px-4 py-2 rounded-full text-sm font-medium text-stone-700 dark:text-stone-300 glass-transition hover:bg-white/40 dark:hover:bg-gray-900/40 hover:scale-105">
                👔 Personalized
              </span>
              <span className="glass-light px-4 py-2 rounded-full text-sm font-medium text-stone-700 dark:text-stone-300 glass-transition hover:bg-white/40 dark:hover:bg-gray-900/40 hover:scale-105">
                🎨 Style Smart
              </span>
            </div>
          </div>
          
          {/* Glass buttons */}
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center px-4">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto glass-button-primary px-8 sm:px-12 py-4 sm:py-6 rounded-2xl font-medium text-lg sm:text-xl glass-transition hover:scale-105 glass-shadow-strong">
                Get Started
                <ArrowRight className="ml-2 sm:ml-3 h-5 w-5 sm:h-6 sm:w-6" />
              </Button>
            </Link>
            <Link href="/onboarding" className="w-full sm:w-auto">
              <Button size="lg" variant="outline" className="w-full sm:w-auto glass-button-secondary px-8 sm:px-12 py-4 sm:py-6 rounded-2xl font-medium text-lg sm:text-xl text-stone-700 dark:text-stone-300 hover:text-stone-900 dark:hover:text-stone-100 glass-transition hover:scale-105">
                Take Style Quiz
                <Sparkles className="ml-2 sm:ml-3 h-5 w-5 sm:h-6 sm:w-6" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
