import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowRight, Heart, Sparkles, Star, TrendingUp, Zap, Users } from "lucide-react";

export default function WomenPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-br from-pink-50 to-purple-100 dark:from-pink-950 dark:to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-r from-pink-600/10 to-purple-600/10 dark:from-pink-400/10 dark:to-purple-400/10"></div>
        <div className="relative z-10 max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
            Women's Style, Reimagined
          </h1>
          <p className="max-w-[600px] mx-auto text-lg text-muted-foreground sm:text-xl mt-6">
            AI-powered styling for the modern woman. Discover your unique style and build a wardrobe that reflects your personality.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row justify-center mt-8">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-lg px-8 py-3">
              <Link href="/style-quiz">
                Take Your Style Quiz
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild className="text-lg px-8 py-3">
              <Link href="/signup">Get Started</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Popular Styles for Women */}
      <section className="w-full py-24 bg-background">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Popular Women's Styles
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Discover styles that match your personality and lifestyle
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-pink-100 to-pink-200 dark:from-pink-900 dark:to-pink-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Boho Chic</h3>
                    <p className="text-sm text-muted-foreground">Free-spirited and artistic</p>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-purple-100 to-purple-200 dark:from-purple-900 dark:to-purple-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Minimalist</h3>
                    <p className="text-sm text-muted-foreground">Clean and essential</p>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-blue-100 to-blue-200 dark:from-blue-900 dark:to-blue-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Coastal Chic</h3>
                    <p className="text-sm text-muted-foreground">Relaxed and sophisticated</p>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-green-100 to-green-200 dark:from-green-900 dark:to-green-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Athleisure</h3>
                    <p className="text-sm text-muted-foreground">Comfort meets style</p>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-orange-100 to-orange-200 dark:from-orange-900 dark:to-orange-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Romantic</h3>
                    <p className="text-sm text-muted-foreground">Feminine and dreamy</p>
                  </div>
                </div>
              </div>
            </Card>
            
            <Card className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-square bg-gradient-to-br from-red-100 to-red-200 dark:from-red-900 dark:to-red-800 relative">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold">Edgy</h3>
                    <p className="text-sm text-muted-foreground">Bold and confident</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits for Women */}
      <section className="w-full py-24 bg-muted/30">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Why Women Choose ClosetGPT
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Smart styling solutions for the modern woman
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
            <Card className="text-center p-8">
              <TrendingUp className="w-12 h-12 text-pink-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Style Confidence</CardTitle>
              <CardDescription className="text-base">
                Feel beautiful and confident in every outfit
              </CardDescription>
            </Card>
            
            <Card className="text-center p-8">
              <Zap className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Time-Saving</CardTitle>
              <CardDescription className="text-base">
                No more outfit stress - get ready with ease
              </CardDescription>
            </Card>
            
            <Card className="text-center p-8">
              <Users className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Versatile Wardrobe</CardTitle>
              <CardDescription className="text-base">
                Mix and match pieces for endless combinations
              </CardDescription>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-700 dark:to-purple-700 text-white">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Ready to Discover Your Style?
        </h2>
        <p className="max-w-[600px] text-lg opacity-90">
          Join thousands of women who have transformed their wardrobe with AI-powered styling.
        </p>
        <Button size="lg" variant="secondary" asChild className="text-lg px-8 py-3">
          <Link href="/style-quiz">
            Start Your Style Quiz
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </Button>
      </section>
    </div>
  );
} 