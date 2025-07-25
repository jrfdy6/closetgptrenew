import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Gift, Heart, Star, Users, ArrowRight } from "lucide-react";

export default function GiftCardsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <section className="border-b bg-background">
        <div className="container px-4 md:px-6 py-8">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <h1 className="text-3xl font-bold">Gift Cards</h1>
          </div>
        </div>
      </section>

      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-br from-pink-50 to-purple-100 dark:from-pink-950 dark:to-purple-900">
        <div className="absolute inset-0 bg-gradient-to-r from-pink-600/10 to-purple-600/10 dark:from-pink-400/10 dark:to-purple-400/10"></div>
        <div className="relative z-10 max-w-4xl mx-auto">
          <Gift className="w-16 h-16 text-pink-600 mx-auto mb-6" />
          <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl bg-gradient-to-r from-pink-600 to-purple-600 dark:from-pink-400 dark:to-purple-400 bg-clip-text text-transparent">
            Gift the Perfect Style
          </h1>
          <p className="max-w-[600px] mx-auto text-lg text-muted-foreground sm:text-xl mt-6">
            Give the gift of confidence and style. Perfect for birthdays, holidays, or just because.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row justify-center mt-8">
            <Button asChild size="lg" className="bg-primary hover:bg-primary/90 text-lg px-8 py-3">
              <Link href="/style-quiz">
                Buy a Gift Card
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button variant="outline" size="lg" asChild className="text-lg px-8 py-3">
              <Link href="/signup">Learn More</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Gift Card Options */}
      <section className="w-full py-24 bg-white">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Choose Your Gift
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Perfect for any style-conscious friend or family member
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3 max-w-5xl mx-auto">
            <Card className="text-center p-8 border-2 border-pink-100 bg-pink-50/30">
              <div className="w-16 h-16 bg-pink-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">$</span>
              </div>
              <CardTitle className="text-xl mb-4">Starter Pack</CardTitle>
              <CardDescription className="mb-6">
                Perfect for someone new to personal styling
              </CardDescription>
              <div className="text-3xl font-bold text-pink-600 mb-6">$49</div>
              <ul className="text-sm text-muted-foreground mb-6 space-y-2">
                <li>• Style Quiz & Profile</li>
                <li>• 30 Days Premium Access</li>
                <li>• Personalized Recommendations</li>
                <li>• Email Support</li>
              </ul>
              <Button className="w-full">Buy Now</Button>
            </Card>
            
            <Card className="text-center p-8 border-2 border-purple-100 bg-purple-50/30 relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <span className="bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                  Most Popular
                </span>
              </div>
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">$$</span>
              </div>
              <CardTitle className="text-xl mb-4">Style Transformation</CardTitle>
              <CardDescription className="mb-6">
                Complete style makeover with premium features
              </CardDescription>
              <div className="text-3xl font-bold text-purple-600 mb-6">$99</div>
              <ul className="text-sm text-muted-foreground mb-6 space-y-2">
                <li>• Everything in Starter Pack</li>
                <li>• 90 Days Premium Access</li>
                <li>• AI Wardrobe Analysis</li>
                <li>• Priority Support</li>
                <li>• Style Consultation</li>
              </ul>
              <Button className="w-full bg-purple-600 hover:bg-purple-700">Buy Now</Button>
            </Card>
            
            <Card className="text-center p-8 border-2 border-green-100 bg-green-50/30">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-2xl font-bold text-white">$$$</span>
              </div>
              <CardTitle className="text-xl mb-4">Luxury Experience</CardTitle>
              <CardDescription className="mb-6">
                Ultimate styling experience with personal touch
              </CardDescription>
              <div className="text-3xl font-bold text-green-600 mb-6">$199</div>
              <ul className="text-sm text-muted-foreground mb-6 space-y-2">
                <li>• Everything in Style Transformation</li>
                <li>• 1 Year Premium Access</li>
                <li>• Personal Style Coach</li>
                <li>• Custom Style Rules</li>
                <li>• VIP Support</li>
              </ul>
              <Button className="w-full bg-green-600 hover:bg-green-700">Buy Now</Button>
            </Card>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="w-full py-24 bg-gray-50">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Why Gift ClosetGPT?
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              The perfect gift for anyone who wants to look and feel their best
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4 max-w-6xl mx-auto">
            <Card className="text-center p-6">
              <Heart className="w-12 h-12 text-pink-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Thoughtful Gift</CardTitle>
              <CardDescription>
                Show you care about their confidence and style
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <Star className="w-12 h-12 text-yellow-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Lasting Impact</CardTitle>
              <CardDescription>
                Skills and confidence that last a lifetime
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <Users className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Personal Growth</CardTitle>
              <CardDescription>
                Help them discover their unique style identity
              </CardDescription>
            </Card>
            
            <Card className="text-center p-6">
              <Gift className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <CardTitle className="text-lg mb-2">Easy to Give</CardTitle>
              <CardDescription>
                Digital delivery, no shipping required
              </CardDescription>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="flex flex-col items-center justify-center space-y-8 px-4 py-24 text-center bg-gradient-to-r from-pink-600 to-purple-600 text-white">
        <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
          Ready to Give the Gift of Style?
        </h2>
        <p className="max-w-[600px] text-lg opacity-90">
          Help someone you love discover their perfect style with ClosetGPT.
        </p>
        <Button size="lg" variant="secondary" asChild className="text-lg px-8 py-3">
          <Link href="/signup">
            Buy Gift Card Now
          </Link>
        </Button>
      </section>
    </div>
  );
} 