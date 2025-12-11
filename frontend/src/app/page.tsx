"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Star, Shield, Camera, TrendingUp } from "lucide-react";
import Script from "next/script";

export default function Home() {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Easy Outfit App",
    "applicationCategory": "LifestyleApplication",
    "operatingSystem": "Web",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    },
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": "5.0",
      "ratingCount": "1000"
    },
    "description": "AI-powered personal stylist that helps you digitize your wardrobe and get personalized outfit suggestions",
    "url": "https://www.easyoutfitapp.com",
    "logo": "https://www.easyoutfitapp.com/logo-horizontal.png",
    "screenshot": "https://www.easyoutfitapp.com/logo-horizontal.png",
    "featureList": [
      "AI-powered outfit generation",
      "Digital wardrobe management",
      "Personalized style recommendations",
      "Weather-based outfit suggestions",
      "Style quiz and personalization"
    ]
  };

  const organizationData = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Easy Outfit App",
    "url": "https://www.easyoutfitapp.com",
    "logo": "https://www.easyoutfitapp.com/logo-horizontal.png",
    "description": "AI-powered personal stylist and digital wardrobe application",
    "sameAs": [
      "https://twitter.com/easyoutfitapp"
    ]
  };

  return (
    <>
      <Script
        id="structured-data-application"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <Script
        id="structured-data-organization"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationData) }}
      />
      <main className="min-h-screen relative overflow-hidden">
      {/* Modern minimal geometric elements - lighter on mobile */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden opacity-35 md:opacity-55" aria-hidden="true">
        <div className="pointer-events-none absolute top-10 md:top-20 left-5 md:left-10 w-24 md:w-32 h-24 md:h-32 bg-primary/25 dark:bg-primary/20 rounded-full blur-3xl"></div>
        <div className="pointer-events-none absolute top-32 md:top-40 right-10 md:right-20 w-20 md:w-24 h-20 md:h-24 bg-primary/20 dark:bg-accent/20 rounded-full blur-2xl"></div>
        <div className="pointer-events-none absolute bottom-20 md:bottom-32 left-1/4 w-16 md:w-20 h-16 md:h-20 bg-secondary/30 dark:bg-muted/50 rounded-full blur-2xl"></div>
        <div className="pointer-events-none absolute bottom-10 md:bottom-20 right-1/3 w-20 md:w-28 h-20 md:h-28 bg-accent/15 dark:bg-primary/25 rounded-full blur-3xl"></div>
      </div>
      
      {/* Hero Section - Mobile Optimized */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16 lg:py-24 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          
          {/* Trust Badge - Mobile First */}
          <div className="flex justify-center mb-4 sm:mb-6">
            <div className="inline-flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-1.5 sm:py-2 rounded-full bg-primary/10 dark:bg-primary/20 border border-primary/20 text-primary text-xs sm:text-sm font-medium">
              <Shield className="w-3 h-3 sm:w-4 sm:h-4" />
              <span>Ad-Free • Unbiased • Reliable</span>
            </div>
          </div>
          
          {/* Logo - Optimized mobile size */}
          <header className="flex justify-center mb-6 sm:mb-8 md:mb-10">
            <Image 
              src="/logo-horizontal.png?v=2" 
              alt="Easy Outfit App - AI-Powered Personal Stylist" 
              width={600} 
              height={150}
              priority
              className="w-auto h-16 sm:h-24 md:h-32 lg:h-40 object-contain"
            />
          </header>
          
          {/* Modern Mobile-First Content Card */}
          <article className="bg-card/85 dark:bg-card/85 backdrop-blur-xl rounded-3xl md:rounded-[2rem] p-6 sm:p-8 md:p-12 mb-6 sm:mb-8 shadow-2xl shadow-primary/10 border border-border/40 dark:border-border/70 animate-fade-in">
            
            {/* Title - Display font for brand moment */}
            <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-foreground mb-4 sm:mb-5 tracking-tight leading-tight">
              Easy Outfit
            </h1>
            
            {/* Tagline - Body font for clarity */}
            <p className="font-body text-lg sm:text-xl md:text-2xl lg:text-3xl text-muted-foreground dark:text-foreground font-light leading-relaxed mb-6 sm:mb-8 px-2">
              Let&apos;s get you dressed ✨
            </p>
            
            {/* Feature badges - Better mobile spacing */}
            <div className="flex flex-wrap gap-2 sm:gap-3 justify-center mb-6 sm:mb-8 px-2" role="list" aria-label="Key features">
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm" role="listitem">
                ✨ AI-Powered
              </span>
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm" role="listitem">
                👔 Personalized
              </span>
              <span className="bg-gradient-to-r from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20 dark:from-[var(--copper-dark)]/30 dark:to-[var(--copper-mid)]/30 px-3 sm:px-4 py-2 sm:py-2.5 rounded-full text-xs sm:text-sm font-semibold text-[var(--copper-dark)] dark:text-[var(--copper-light)] border border-[var(--copper-light)]/50 dark:border-[var(--copper-dark)]/50 shadow-sm backdrop-blur-sm" role="listitem">
                🎨 Style Smart
              </span>
            </div>

            {/* Social proof / Quick stats - Mobile friendly */}
            <div className="flex flex-col sm:flex-row flex-wrap items-center justify-center gap-3 sm:gap-4 md:gap-6 mb-6 sm:mb-8 text-xs sm:text-sm text-muted-foreground" aria-label="User statistics">
              <div className="flex items-center gap-1.5">
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-primary" aria-hidden="true" />
                <span className="font-medium">Over 100,000 outfits generated</span>
              </div>
              <div className="hidden sm:block text-muted-foreground/50">•</div>
              <div className="flex items-center gap-1" aria-label="Rating: 5 out of 5 stars">
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" aria-hidden="true" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" aria-hidden="true" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" aria-hidden="true" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" aria-hidden="true" />
                <Star className="w-4 h-4 fill-[var(--copper-dark)] text-[var(--copper-dark)]" aria-hidden="true" />
                <span className="ml-1 font-medium">5.0 rating</span>
              </div>
            </div>
          </article>
          
          {/* CTA Buttons - Improved mobile layout */}
          <nav className="flex flex-col gap-3 sm:gap-4 justify-center items-stretch sm:items-center max-w-md sm:max-w-none mx-auto mb-6 sm:mb-8" aria-label="Main navigation">
            <Link href="/signup" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                className="w-full sm:w-auto gradient-copper-gold hover:opacity-90 text-[#1A1510] dark:text-white px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-[var(--copper-dark)]/25 hover:shadow-2xl hover:shadow-[var(--copper-dark)]/30 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
                aria-label="Get started free"
              >
                Get Started Free
                <ArrowRight className="ml-2 h-5 w-5" aria-hidden="true" />
              </Button>
            </Link>
            <Link href="/onboarding?mode=guest" className="w-full sm:w-auto">
              <Button 
                size="lg" 
                variant="outline" 
                className="w-full sm:w-auto bg-card/65 dark:bg-card/65 hover:bg-card/80 dark:hover:bg-secondary/80 backdrop-blur-xl border-2 border-border/60 dark:border-border/80 text-[var(--copper-dark)] dark:text-[var(--copper-light)] hover:text-[var(--copper-mid)] dark:hover:text-[var(--copper-mid)] px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                aria-label="Start the 2-minute style quiz"
              >
                Try Style Quiz
                <Sparkles className="ml-2 h-5 w-5" aria-hidden="true" />
              </Button>
            </Link>
          </nav>
          
          {/* Trust indicator - Mobile optimized */}
          <p className="text-xs sm:text-sm text-muted-foreground font-medium text-center">
            Free to start. No credit card required.
          </p>

        </div>
      </section>

      {/* Value Proposition Section - Mobile First */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16 relative z-10">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-display font-bold text-center mb-8 sm:mb-12">
            Your AI stylist in seconds
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 sm:gap-8">
            {/* Upload Wardrobe */}
            <div className="text-center p-6 sm:p-8 rounded-2xl bg-card/50 dark:bg-card/50 backdrop-blur-sm border border-border/40 dark:border-border/60 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                <Camera className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3">Snap & organize</h3>
              <p className="text-sm sm:text-base text-muted-foreground">
                Upload your clothes in seconds. AI automatically categorizes and tags everything.
              </p>
            </div>

            {/* Get AI Suggestions */}
            <div className="text-center p-6 sm:p-8 rounded-2xl bg-card/50 dark:bg-card/50 backdrop-blur-sm border border-border/40 dark:border-border/60 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3">Personalized outfits</h3>
              <p className="text-sm sm:text-base text-muted-foreground">
                Get personalized outfit suggestions based on your style, weather, and occasion.
              </p>
            </div>

            {/* Maximize Closet */}
            <div className="text-center p-6 sm:p-8 rounded-2xl bg-card/50 dark:bg-card/50 backdrop-blur-sm border border-border/40 dark:border-border/60 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6 rounded-full bg-primary/10 dark:bg-primary/20 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 sm:w-8 sm:h-8 text-primary" />
              </div>
              <h3 className="text-lg sm:text-xl font-semibold mb-2 sm:mb-3">Wear smarter</h3>
              <p className="text-sm sm:text-base text-muted-foreground">
                Track what you wear, discover forgotten gems, and maximize your wardrobe.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Enhanced Final CTA Section - Mobile First */}
      <section className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20 relative z-10">
        <div className="max-w-3xl mx-auto text-center">
          <div className="bg-gradient-to-br from-primary/10 via-accent/10 to-primary/10 rounded-3xl p-8 sm:p-12 md:p-16 border border-primary/20 dark:border-primary/30">
            <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
              Ready to transform your mornings?
            </h2>
            <p className="text-base sm:text-lg md:text-xl text-muted-foreground mb-6 sm:mb-8">
              Join thousands of users who never struggle with &quot;what to wear&quot; again
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center items-stretch sm:items-center mb-6 sm:mb-8">
              <Link href="/signup" className="w-full sm:w-auto">
                <Button 
                  size="lg" 
                  className="w-full sm:w-auto gradient-copper-gold hover:opacity-90 text-[#1A1510] dark:text-white px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-[var(--copper-dark)]/25 hover:shadow-2xl hover:shadow-[var(--copper-dark)]/30 transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
                >
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" aria-hidden="true" />
                </Button>
              </Link>
              <Link href="/onboarding?mode=guest" className="w-full sm:w-auto">
                <Button 
                  size="lg" 
                  variant="outline" 
                  className="w-full sm:w-auto bg-card/65 dark:bg-card/65 hover:bg-card/80 dark:hover:bg-secondary/80 backdrop-blur-xl border-2 border-border/60 dark:border-border/80 text-[var(--copper-dark)] dark:text-[var(--copper-light)] hover:text-[var(--copper-mid)] dark:hover:text-[var(--copper-mid)] px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                >
                  Try Style Quiz
                  <Sparkles className="ml-2 h-5 w-5" aria-hidden="true" />
                </Button>
              </Link>
            </div>
            
            <p className="text-xs sm:text-sm text-muted-foreground font-medium">
              Free forever plan • No credit card required
            </p>
          </div>
        </div>
      </section>
    </main>
    </>
  );
}
