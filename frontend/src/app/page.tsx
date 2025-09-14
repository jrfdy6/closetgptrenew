"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-gray-900 dark:from-gray-900 dark:via-slate-800 dark:to-gray-900" style={{
      backgroundImage: `url('/images/style-heroes/rebel-graffiti-alley.jpg')`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundAttachment: 'fixed'
    }}>
      <div className="absolute inset-0 bg-gradient-to-br from-gray-900/40 via-slate-800/30 to-gray-900/40"></div>
      {/* Hero Section */}
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24 lg:py-32 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold mb-6 sm:mb-8 text-white tracking-tight leading-tight drop-shadow-2xl" style={{
            textShadow: '2px 2px 4px rgba(0,0,0,0.8), 0 0 20px rgba(255,255,255,0.3)',
            fontFamily: 'system-ui, -apple-system, sans-serif'
          }}>
            ClosetGPT
          </h1>
          <p className="text-lg sm:text-xl md:text-2xl text-white/95 mb-12 sm:mb-16 font-medium leading-relaxed px-4 drop-shadow-lg">
            Your AI-powered personal stylist
          </p>
          <div className="flex flex-col sm:flex-row gap-4 sm:gap-6 justify-center items-center px-4">
            <Link href="/signin" className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white px-8 sm:px-12 py-4 sm:py-6 rounded-none font-bold text-lg sm:text-xl transition-all duration-300 hover:scale-105 shadow-2xl border-2 border-orange-400/50">
                Get Started
                <ArrowRight className="ml-2 sm:ml-3 h-5 w-5 sm:h-6 sm:w-6" />
              </Button>
            </Link>
            <Link href="/onboarding" className="w-full sm:w-auto">
              <Button size="lg" variant="outline" className="w-full sm:w-auto px-8 sm:px-12 py-4 sm:py-6 rounded-none font-bold text-lg sm:text-xl border-2 border-white/60 hover:border-white text-white hover:text-white hover:bg-white/20 transition-all duration-300 hover:scale-105 backdrop-blur-sm shadow-xl">
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
