"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 lg:py-32">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-serif font-bold mb-6 sm:mb-8 text-stone-900 dark:text-stone-100 tracking-tight leading-tight">
            ClosetGPT
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-stone-600 dark:text-stone-400 mb-12 sm:mb-16 font-light leading-relaxed px-4">
            Your AI-powered personal stylist
          </p>
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center px-4">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto bg-stone-900 hover:bg-stone-800 text-white px-8 sm:px-12 py-4 sm:py-6 rounded-full font-medium text-lg sm:text-xl transition-all duration-300 hover:scale-105 shadow-lg">
                Get Started
                <ArrowRight className="ml-2 sm:ml-3 h-5 w-5 sm:h-6 sm:w-6" />
              </Button>
            </Link>
            <Link href="/onboarding" className="w-full sm:w-auto">
              <Button size="lg" variant="outline" className="w-full sm:w-auto px-8 sm:px-12 py-4 sm:py-6 rounded-full font-medium text-lg sm:text-xl border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 transition-all duration-300 hover:scale-105">
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
