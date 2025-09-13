"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-32">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-8xl font-serif font-bold mb-8 text-stone-900 dark:text-stone-100 tracking-tight">
            ClosetGPT
          </h1>
          <p className="text-2xl text-stone-600 dark:text-stone-400 mb-16 font-light leading-relaxed">
            Your AI-powered personal stylist
          </p>
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link href="/signin">
              <Button size="lg" className="bg-stone-900 hover:bg-stone-800 text-white px-12 py-6 rounded-full font-medium text-xl transition-all duration-300 hover:scale-105 shadow-lg">
                Get Started
                <ArrowRight className="ml-3 h-6 w-6" />
              </Button>
            </Link>
            <Link href="/onboarding">
              <Button size="lg" variant="outline" className="px-12 py-6 rounded-full font-medium text-xl border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 transition-all duration-300 hover:scale-105">
                Take Style Quiz
                <Sparkles className="ml-3 h-6 w-6" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
