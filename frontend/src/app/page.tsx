import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowRight, Clock, DollarSign, Sparkles, Users, Zap } from "lucide-react";

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-blue-950 dark:to-indigo-900">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 dark:from-blue-400/10 dark:to-purple-400/10"></div>
        <div className="relative z-10 max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400 bg-clip-text text-transparent">
            AI Personal Styling That Gets You
          </h1>
          <p className="max-w-[600px] mx-auto text-lg text-muted-foreground sm:text-xl mt-6">
            Your style, delivered. Get your first month free.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row justify-center mt-8">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-lg px-8 py-3">
              <Link href="/style-quiz">
                Take Your Style Quiz
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild className="text-lg px-8 py-3">
              <Link href="/signin">Sign In</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* 3-Step Process */}
      <section className="w-full py-24 bg-background">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              How It Works
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Three simple steps to your perfect style
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
            <Card className="text-center p-8 border-2 border-blue-100 bg-blue-50/30 dark:border-blue-800 dark:bg-blue-950/30">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">1</span>
              </div>
              <CardTitle className="text-xl mb-4">Take the style quiz</CardTitle>
              <CardDescription className="text-base">
                Tell us your fit, budget, and personal style preferences.
              </CardDescription>
            </Card>
            
            <Card className="text-center p-8 border-2 border-purple-100 bg-purple-50/30 dark:border-purple-800 dark:bg-purple-950/30">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">2</span>
              </div>
              <CardTitle className="text-xl mb-4">Upload your wardrobe</CardTitle>
              <CardDescription className="text-base">
                Add photos of your existing clothes to your digital closet.
              </CardDescription>
            </Card>
            
            <Card className="text-center p-8 border-2 border-green-100 bg-green-50/30 dark:border-green-800 dark:bg-green-950/30">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <CardTitle className="text-xl mb-4">Generate perfect outfits</CardTitle>
              <CardDescription className="text-base">
                Our AI creates personalized outfit combinations from your own clothes.
              </CardDescription>
            </Card>
          </div>
        </div>
      </section>

      {/* AI Outfit Transformations */}
      <section className="w-full bg-muted/50 py-24">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              AI-Powered Outfit Magic
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              See how our AI transforms your existing clothes into stunning new combinations
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 max-w-6xl mx-auto">
            <Card className="overflow-hidden">
              <div className="grid grid-cols-2 gap-4 p-6">
                <div className="text-center">
                  <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 rounded-lg flex items-center justify-center mb-3">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-gray-400 rounded-full flex items-center justify-center mx-auto mb-2">
                        <span className="text-sm font-bold text-white">👕</span>
                      </div>
                      <p className="text-xs text-muted-foreground">Before</p>
                    </div>
                  </div>
                  <p className="text-sm font-medium">Basic Wardrobe Items</p>
                  <p className="text-xs text-muted-foreground">Jeans, t-shirt, jacket</p>
                </div>
                <div className="text-center">
                  <div className="aspect-square bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900 dark:to-blue-800 rounded-lg flex items-center justify-center mb-3">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-2">
                        <span className="text-sm font-bold text-white">✨</span>
                      </div>
                      <p className="text-xs text-muted-foreground">After</p>
                    </div>
                  </div>
                  <p className="text-sm font-medium">Polished Streetwear</p>
                  <p className="text-xs text-muted-foreground">Layered & styled</p>
                </div>
              </div>
              <CardContent className="p-6 pt-0">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">Streetwear</Badge>
                  <Badge variant="secondary">Layered</Badge>
                  <Badge variant="secondary">Modern</Badge>
                </div>
              </CardContent>
            </Card>
            
            <Card className="overflow-hidden">
              <div className="grid grid-cols-2 gap-4 p-6">
                <div className="text-center">
                  <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 rounded-lg flex items-center justify-center mb-3">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-gray-400 rounded-full flex items-center justify-center mx-auto mb-2">
                        <span className="text-sm font-bold text-white">👗</span>
                      </div>
                      <p className="text-xs text-muted-foreground">Before</p>
                    </div>
                  </div>
                  <p className="text-sm font-medium">Simple Pieces</p>
                  <p className="text-xs text-muted-foreground">Dress, cardigan, accessories</p>
                </div>
                <div className="text-center">
                  <div className="aspect-square bg-gradient-to-br from-purple-100 to-pink-200 dark:from-purple-900 dark:to-pink-800 rounded-lg flex items-center justify-center mb-3">
                    <div className="text-center">
                      <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-2">
                        <span className="text-sm font-bold text-white">✨</span>
                      </div>
                      <p className="text-xs text-muted-foreground">After</p>
                    </div>
                  </div>
                  <p className="text-sm font-medium">Boho Minimalist</p>
                  <p className="text-xs text-muted-foreground">Styled with flair</p>
                </div>
              </div>
              <CardContent className="p-6 pt-0">
                <div className="flex flex-wrap gap-2">
                  <Badge variant="secondary">Boho</Badge>
                  <Badge variant="secondary">Minimalist</Badge>
                  <Badge variant="secondary">Neutral</Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="w-full py-24 bg-background">
        <div className="container px-4 md:px-6">
          <div className="max-w-4xl mx-auto text-center">
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 p-8 rounded-2xl border border-blue-100 dark:border-blue-800">
              <div className="flex justify-center mb-4">
                <div className="flex space-x-1">
                  {[...Array(5)].map((_, i) => (
                    <Sparkles key={i} className="w-5 h-5 text-yellow-500 fill-current" />
                  ))}
                </div>
              </div>
              <blockquote className="text-xl font-medium text-foreground mb-4">
                "ClosetGPT helps me show up better — without wasting hours shopping."
              </blockquote>
              <cite className="text-sm text-muted-foreground">
                – Jessica R., user since 2024
              </cite>
            </div>
          </div>
        </div>
      </section>

      {/* Style Fingerprint Section */}
      <section className="w-full bg-gradient-to-r from-purple-600 to-blue-600 py-24 text-white">
        <div className="container px-4 md:px-6">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-6">
              Discover Your Style Fingerprint
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Reveal your unique style DNA and explore your 5 dominant style types
            </p>
            <div className="grid gap-6 md:grid-cols-3 mb-8">
              <div className="bg-white/10 p-6 rounded-lg">
                <h3 className="font-semibold mb-2">Personalized Analysis</h3>
                <p className="text-sm opacity-80">AI-powered style assessment</p>
              </div>
              <div className="bg-white/10 p-6 rounded-lg">
                <h3 className="font-semibold mb-2">Style Breakdown</h3>
                <p className="text-sm opacity-80">5 dominant style types revealed</p>
              </div>
              <div className="bg-white/10 p-6 rounded-lg">
                <h3 className="font-semibold mb-2">Share & Update</h3>
                <p className="text-sm opacity-80">Share it or update it anytime</p>
              </div>
            </div>
            <Button asChild size="lg" variant="secondary" className="text-lg px-8 py-3">
              <Link href="/style-quiz">
                Get Your Style Fingerprint
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="w-full py-24 bg-muted/30">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Why Choose ClosetGPT?
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Transform your existing wardrobe with AI-powered styling
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto">
            <Card className="text-center p-6">
              <Clock className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Save 40+ hours/year</CardTitle>
              <CardDescription>
                No more decision fatigue - get outfit suggestions instantly
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <DollarSign className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Zero additional cost</CardTitle>
              <CardDescription>
                Use what you already own - no new purchases needed
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <Zap className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Unlimited combinations</CardTitle>
              <CardDescription>
                Discover new ways to wear your existing clothes
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <Users className="w-12 h-12 text-orange-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Personalized for you</CardTitle>
              <CardDescription>
                AI learns your style preferences and body type
              </CardDescription>
            </Card>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-700 dark:to-purple-700 text-white">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Ready to Transform Your Style?
        </h2>
        <p className="max-w-[600px] text-lg opacity-90">
          Join thousands of users who have already discovered their perfect style with ClosetGPT.
        </p>
        <div className="flex flex-col gap-4 sm:flex-row">
          <Button size="lg" variant="secondary" asChild className="text-lg px-8 py-3">
            <Link href="/style-quiz">
              Take Your Style Quiz
              <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild className="text-lg px-8 py-3 border-white text-white hover:bg-white hover:text-blue-600">
            <Link href="/signup">Start Your Style Journey</Link>
          </Button>
        </div>
      </section>
    </div>
  );
}
