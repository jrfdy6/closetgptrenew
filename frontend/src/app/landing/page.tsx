"use client";

import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { ArrowRight, Sparkles, Star, Shield, Camera, TrendingUp, Zap, Palette, Cloud, Check, Clock, MessageSquare } from "lucide-react";
import Script from "next/script";

export default function LandingPage() {
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
      <main className="min-h-screen">
        {/* Hero Section - Marketing Focus - Mobile First */}
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-primary/10 via-background to-accent/10">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 md:py-20 lg:py-24 relative z-10">
            <div className="max-w-6xl mx-auto">
              {/* Trust Badge - Mobile First */}
              <div className="flex justify-center mb-6 sm:mb-8">
                <div className="inline-flex items-center gap-2 px-4 sm:px-5 py-2 sm:py-2.5 rounded-full bg-primary/10 dark:bg-primary/20 border border-primary/20 text-primary text-sm sm:text-base font-medium">
                  <Shield className="w-4 h-4 sm:w-5 sm:h-5" />
                  <span>Ad-Free • Unbiased • Reliable</span>
                </div>
              </div>

              <div className="text-center mb-8 sm:mb-12">
                {/* Logo */}
                <div className="flex justify-center mb-6 sm:mb-8">
                  <Image 
                    src="/logo-horizontal.png?v=2" 
                    alt="Easy Outfit App" 
                    width={600} 
                    height={150}
                    priority
                    className="w-auto h-16 sm:h-24 md:h-32 lg:h-40 object-contain"
                  />
                </div>

                {/* Headline - Mobile First Typography */}
                <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-display font-bold mb-4 sm:mb-6 leading-tight">
                  Stop wasting time<br className="hidden sm:block" />
                  <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    wondering what to wear
                  </span>
                </h1>
                
                {/* Subheadline */}
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground mb-4 sm:mb-6 max-w-3xl mx-auto">
                  Make the most of your existing wardrobe with unbiased, AI-powered styling advice.
                </p>
                <p className="text-base sm:text-lg md:text-xl text-muted-foreground/80 max-w-2xl mx-auto">
                  No shopping push. No ads. Just honest, personalized outfit suggestions that help you look amazing every day.
                </p>
              </div>

              {/* Social Proof - Mobile First */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 md:gap-6 mb-8 sm:mb-12 text-sm sm:text-base text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                  <span className="font-medium">Over 100,000 outfits generated</span>
                </div>
                <div className="hidden sm:block text-muted-foreground/50">•</div>
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 sm:w-5 sm:h-5 fill-amber-400 text-amber-400" />
                  ))}
                  <span className="ml-1 font-medium">5.0 rating</span>
                </div>
              </div>

              {/* CTAs - Mobile First */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-stretch sm:items-center mb-12 sm:mb-16">
                <Link href="/signup" className="w-full sm:w-auto">
                  <Button 
                    size="lg" 
                    className="w-full sm:w-auto gradient-copper-gold hover:opacity-90 text-[#1A1510] dark:text-white px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-[var(--copper-dark)]/25 hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
                  >
                    Start Free — No Credit Card
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/onboarding?mode=guest" className="w-full sm:w-auto">
                  <Button 
                    size="lg" 
                    variant="outline" 
                    className="w-full sm:w-auto bg-card/65 dark:bg-card/65 hover:bg-card/80 dark:hover:bg-secondary/80 backdrop-blur-xl border-2 border-border/60 dark:border-border/80 text-[var(--copper-dark)] dark:text-[var(--copper-light)] px-8 sm:px-12 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Try Style Quiz First
                  </Button>
                </Link>
              </div>

              {/* Hero Visual Placeholder - Mobile First */}
              <div className="max-w-4xl mx-auto">
                <div className="bg-card/80 backdrop-blur-xl rounded-2xl sm:rounded-3xl p-6 sm:p-8 border border-border/50 shadow-2xl">
                  <div className="aspect-video bg-gradient-to-br from-muted to-muted/50 rounded-xl flex items-center justify-center">
                    <div className="text-center">
                      <Camera className="w-12 h-12 sm:w-16 sm:h-16 text-primary/30 mx-auto mb-4" />
                      <p className="text-muted-foreground text-sm sm:text-base">App Screenshot: Easy Cataloging Interface</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Solve Cold Start Problem Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-background">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-8 sm:mb-12 md:mb-16">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4 sm:mb-6">
                  <Zap className="w-4 h-4" />
                  <span>Automated AI Processing</span>
                </div>
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
                  Catalog your wardrobe in no time
                </h2>
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
                  The biggest barrier? We&apos;ve solved it. Our AI makes cataloging effortless—not a big job.
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-8 sm:gap-12 items-center">
                <div>
                  <h3 className="text-2xl sm:text-3xl font-display font-bold mb-4 sm:mb-6">
                    Snap. Upload. Done.
                  </h3>
                  <p className="text-base sm:text-lg text-muted-foreground mb-6 sm:mb-8">
                    Advanced AI automatically removes backgrounds, analyzes clothing details, and categorizes everything. 
                    Your entire wardrobe becomes accessible at your fingertips—no manual tagging required.
                  </p>
                  <ul className="space-y-3 sm:space-y-4">
                    {[
                      "AI-powered background removal",
                      "Automatic category detection",
                      "Smart color & style analysis",
                      "Batch upload support"
                    ].map((feature, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <Check className="w-5 h-5 sm:w-6 sm:h-6 text-primary flex-shrink-0" />
                        <span className="text-sm sm:text-base">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="bg-muted/50 rounded-2xl p-6 sm:p-8 aspect-square flex items-center justify-center border-2 border-dashed border-muted-foreground/20">
                  <div className="text-center">
                    <Camera className="w-16 h-16 sm:w-20 sm:h-20 text-primary/30 mx-auto mb-4" />
                    <p className="text-muted-foreground text-sm sm:text-base">Visual: Before/After AI Processing</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Unbiased AI Styling Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-8 sm:mb-12 md:mb-16">
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
                  Unbiased AI styling for your existing wardrobe
                </h2>
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto">
                  Unlike other apps that push shopping, we focus on maximizing what you already own. 
                  No affiliate bias. No ads. Just honest, personalized styling advice.
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6 sm:gap-8 mb-12 sm:mb-16">
                {[
                  {
                    icon: Shield,
                    title: "No Shopping Push",
                    description: "We prioritize your existing wardrobe utilization above all else. No affiliate links, no shopping bias."
                  },
                  {
                    icon: Sparkles,
                    title: "Personalized AI",
                    description: "Advanced AI learns your style, weather, and occasion to suggest perfect combinations from your closet."
                  },
                  {
                    icon: TrendingUp,
                    title: "Maximize Utilization",
                    description: "Discover hidden gems, track what you wear, and get insights to make the most of every item."
                  }
                ].map((feature, i) => (
                  <div key={i} className="bg-card p-6 sm:p-8 rounded-2xl border text-center">
                    <feature.icon className="w-10 h-10 sm:w-12 sm:h-12 text-primary mx-auto mb-4 sm:mb-6" />
                    <h3 className="text-xl sm:text-2xl font-semibold mb-3 sm:mb-4">{feature.title}</h3>
                    <p className="text-sm sm:text-base text-muted-foreground">{feature.description}</p>
                  </div>
                ))}
              </div>

              {/* Feature Deep Dive - Mobile First */}
              <div className="grid md:grid-cols-2 gap-8 sm:gap-12 items-center">
                <div className="bg-card/80 backdrop-blur-xl rounded-2xl p-6 sm:p-8 border aspect-video flex items-center justify-center order-2 md:order-1">
                  <p className="text-muted-foreground text-sm sm:text-base">Screenshot: Outfit Suggestions Interface</p>
                </div>
                <div className="order-1 md:order-2">
                  <h3 className="text-2xl sm:text-3xl font-display font-bold mb-4 sm:mb-6">
                    World-class AI outfit generation
                  </h3>
                  <p className="text-base sm:text-lg text-muted-foreground mb-6 sm:mb-8">
                    Our AI analyzes your wardrobe items, style preferences, current weather, and occasion 
                    to suggest perfect outfit combinations. It learns from your feedback to get better over time.
                  </p>
                  <ul className="space-y-3 sm:space-y-4">
                    {[
                      "Weather-aware suggestions",
                      "Style persona matching",
                      "Color harmony analysis",
                      "Occasion-appropriate styling"
                    ].map((feature, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <Check className="w-5 h-5 sm:w-6 sm:h-6 text-primary flex-shrink-0" />
                        <span className="text-sm sm:text-base">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-background">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl mx-auto">
              <div className="text-center mb-8 sm:mb-12 md:mb-16">
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
                  Get started in 3 simple steps
                </h2>
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground">
                  From cataloging to daily outfit confidence
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6 sm:gap-8">
                {[
                  {
                    step: "1",
                    icon: Camera,
                    title: "Upload Your Wardrobe",
                    description: "Snap photos or upload images. AI automatically removes backgrounds, categorizes, and tags everything. Your entire closet becomes digital in minutes."
                  },
                  {
                    step: "2",
                    icon: Sparkles,
                    title: "Discover Your Style",
                    description: "Take our quick style quiz. We'll create your personalized style persona and understand your preferences, body type, and aesthetic goals."
                  },
                  {
                    step: "3",
                    icon: TrendingUp,
                    title: "Get Daily Outfit Suggestions",
                    description: "Receive personalized outfit combinations every day based on weather, occasion, and your style. Track what you wear and maximize your wardrobe."
                  }
                ].map((step, i) => (
                  <div key={i} className="text-center">
                    <div className="w-16 h-16 sm:w-20 sm:h-20 rounded-full bg-gradient-to-br from-primary to-accent text-primary-foreground flex items-center justify-center text-2xl sm:text-3xl font-bold mx-auto mb-4 sm:mb-6 shadow-lg">
                      {step.step}
                    </div>
                    <step.icon className="w-8 h-8 sm:w-10 sm:h-10 text-primary mx-auto mb-4 sm:mb-6" />
                    <h3 className="text-xl sm:text-2xl font-semibold mb-3 sm:mb-4">{step.title}</h3>
                    <p className="text-sm sm:text-base text-muted-foreground">{step.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Features Grid Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-8 sm:mb-12 md:mb-16">
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
                  Everything you need
                </h2>
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground">
                  Powerful features that make getting dressed effortless
                </p>
              </div>

              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
                {[
                  {
                    icon: Zap,
                    title: "AI Outfit Generation",
                    description: "Get personalized outfit suggestions in seconds based on your style and weather"
                  },
                  {
                    icon: Palette,
                    title: "Style Persona",
                    description: "Discover your unique style identity with our AI-powered style quiz"
                  },
                  {
                    icon: Cloud,
                    title: "Weather Integration",
                    description: "Never be underdressed with weather-aware outfit suggestions"
                  },
                  {
                    icon: TrendingUp,
                    title: "Wardrobe Analytics",
                    description: "Track what you wear, discover forgotten gems, and maximize your closet"
                  },
                  {
                    icon: Sparkles,
                    title: "Smart Organization",
                    description: "AI automatically categorizes and tags your clothes as you upload"
                  },
                  {
                    icon: Star,
                    title: "Style Inspiration",
                    description: "Get daily inspiration tailored to your personal style preferences"
                  }
                ].map((feature, i) => (
                  <div key={i} className="p-6 sm:p-8 rounded-2xl bg-card border hover:shadow-lg transition-shadow">
                    <feature.icon className="w-10 h-10 sm:w-12 sm:h-12 text-primary mb-4 sm:mb-6" />
                    <h3 className="text-xl sm:text-2xl font-semibold mb-2 sm:mb-3">{feature.title}</h3>
                    <p className="text-sm sm:text-base text-muted-foreground">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Social Proof/Testimonials Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-background">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-8 sm:mb-12 md:mb-16">
                <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-4 sm:mb-6">
                  Loved by users who value their time
                </h2>
                <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground">
                  Real feedback from people maximizing their wardrobe
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-6 sm:gap-8">
                {[
                  {
                    name: "Sarah M.",
                    role: "Fashion Enthusiast",
                    text: "This app saved me so much time in the morning. The AI suggestions are spot-on and I've discovered so many hidden gems in my closet I'd forgotten about!",
                    highlight: "Quality of AI suggestions"
                  },
                  {
                    name: "James T.",
                    role: "Busy Professional",
                    text: "Finally, a way to actually use all my clothes. The wardrobe insights help me maximize my closet and I never repeat outfits awkwardly. No ads, no shopping push—just honest styling.",
                    highlight: "Organization & utilization"
                  },
                  {
                    name: "Maria L.",
                    role: "Style Blogger",
                    text: "The weather integration is genius. Never underdressed again, and the style persona feature helped me refine my aesthetic. The cataloging was surprisingly easy too!",
                    highlight: "Ease of use & reliability"
                  }
                ].map((testimonial, i) => (
                  <div key={i} className="bg-card p-6 sm:p-8 rounded-2xl border hover:shadow-lg transition-shadow">
                    <div className="flex mb-4 sm:mb-6">
                      {[...Array(5)].map((_, j) => (
                        <Star key={j} className="w-4 h-4 sm:w-5 sm:h-5 fill-amber-400 text-amber-400" />
                      ))}
                    </div>
                    <p className="text-sm sm:text-base text-muted-foreground mb-4 sm:mb-6 leading-relaxed">&quot;{testimonial.text}&quot;</p>
                    <div className="pt-4 border-t">
                      <p className="font-semibold text-sm sm:text-base">{testimonial.name}</p>
                      <p className="text-xs sm:text-sm text-muted-foreground">{testimonial.role}</p>
                      <p className="text-xs text-primary mt-2 font-medium">{testimonial.highlight}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Trust & Reliability Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 bg-muted/30">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto text-center">
              <h2 className="text-3xl sm:text-4xl md:text-5xl font-display font-bold mb-8 sm:mb-12">
                Built for reliability and trust
              </h2>
              <div className="grid md:grid-cols-3 gap-6 sm:gap-8 mb-8 sm:mb-12">
                {[
                  {
                    icon: Shield,
                    title: "Ad-Free Experience",
                    description: "No intrusive ads. No affiliate bias. Just pure styling advice."
                  },
                  {
                    icon: Clock,
                    title: "Stable & Reliable",
                    description: "Built for performance. No glitches, no crashes, just smooth operation."
                  },
                  {
                    icon: Check,
                    title: "Privacy First",
                    description: "Your wardrobe data is encrypted and never shared. Your privacy matters."
                  }
                ].map((feature, i) => (
                  <div key={i} className="p-6 sm:p-8">
                    <feature.icon className="w-10 h-10 sm:w-12 sm:h-12 text-primary mx-auto mb-4 sm:mb-6" />
                    <h3 className="font-semibold text-lg sm:text-xl mb-2 sm:mb-3">{feature.title}</h3>
                    <p className="text-sm sm:text-base text-muted-foreground">{feature.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section - Mobile First */}
        <section className="py-12 sm:py-16 md:py-24 lg:py-32 bg-gradient-to-br from-primary/10 via-accent/10 to-primary/10">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="max-w-3xl mx-auto">
              <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-display font-bold mb-4 sm:mb-6">
                Ready to transform your mornings?
              </h2>
              <p className="text-lg sm:text-xl md:text-2xl text-muted-foreground mb-4 sm:mb-6">
                Join thousands of users who never struggle with &quot;what to wear&quot; again
              </p>
              <p className="text-base sm:text-lg text-muted-foreground/80 mb-8 sm:mb-10">
                Make the most of your existing wardrobe. Look amazing. Save time.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-stretch sm:items-center mb-6 sm:mb-8">
                <Link href="/signup" className="w-full sm:w-auto">
                  <Button 
                    size="lg" 
                    className="w-full sm:w-auto gradient-copper-gold hover:opacity-90 text-[#1A1510] dark:text-white px-8 sm:px-10 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-xl shadow-[var(--copper-dark)]/25 hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] border-0"
                  >
                    Start Free — No Credit Card
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </Link>
                <Link href="/onboarding?mode=guest" className="w-full sm:w-auto">
                  <Button 
                    size="lg" 
                    variant="outline" 
                    className="w-full sm:w-auto bg-card/65 dark:bg-card/65 hover:bg-card/80 dark:hover:bg-secondary/80 backdrop-blur-xl border-2 border-border/60 dark:border-border/80 text-[var(--copper-dark)] dark:text-[var(--copper-light)] px-8 sm:px-10 py-5 sm:py-6 rounded-2xl font-semibold text-base sm:text-lg shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]"
                  >
                    Try Style Quiz First
                  </Button>
                </Link>
              </div>
              <p className="text-xs sm:text-sm text-muted-foreground">
                Free forever plan available • No credit card required • Cancel anytime
              </p>
            </div>
          </div>
        </section>
      </main>
    </>
  );
}

