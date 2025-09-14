"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-gray-800 to-slate-900 dark:from-slate-900 dark:via-gray-800 dark:to-slate-900">
      {/* Minimalistic geometric elements inspired by graffiti */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-20 w-24 h-24 bg-red-500/10 rounded-full blur-2xl"></div>
        <div className="absolute bottom-32 left-1/4 w-20 h-20 bg-yellow-500/10 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 right-1/3 w-28 h-28 bg-pink-500/10 rounded-full blur-3xl"></div>
      </div>
      {/* Hero Section */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 lg:py-32 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-6 sm:mb-8 text-white tracking-tight leading-tight">
            ClosetGPT
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-gray-300 mb-12 sm:mb-16 font-light leading-relaxed px-4">
            Your AI-powered personal stylist
          </p>
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center px-4">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto bg-orange-500 hover:bg-orange-600 text-white px-8 sm:px-12 py-4 sm:py-6 rounded-lg font-medium text-lg sm:text-xl transition-all duration-300 hover:scale-105 shadow-lg">
                Get Started
                <ArrowRight className="ml-2 sm:ml-3 h-5 w-5 sm:h-6 sm:w-6" />
              </Button>
            </Link>
            <Link href="/onboarding" className="w-full sm:w-auto">
              <Button size="lg" variant="outline" className="w-full sm:w-auto px-8 sm:px-12 py-4 sm:py-6 rounded-lg font-medium text-lg sm:text-xl border-2 border-gray-400 hover:border-white text-gray-300 hover:text-white hover:bg-white/10 transition-all duration-300 hover:scale-105">
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
