import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, Mail, MessageCircle, Phone } from "lucide-react";

export default function HelpPage() {
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
            <h1 className="text-3xl font-bold">Help & Support</h1>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="w-full py-24 bg-white">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Frequently Asked Questions
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Find answers to common questions about ClosetGPT
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-2 max-w-4xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle>How does the style quiz work?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Our AI-powered style quiz asks you about your preferences, lifestyle, and goals to create a personalized style profile. It takes about 5-10 minutes to complete.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Can I use my own clothes?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Yes! ClosetGPT is designed to work with your existing wardrobe. Upload photos of your clothes and get personalized outfit recommendations.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>How accurate are the recommendations?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Our AI learns from your preferences and feedback to provide increasingly accurate recommendations over time. The more you use it, the better it gets.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Is my data secure?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Absolutely. We use industry-standard encryption and never share your personal information with third parties without your consent.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>Can I change my style preferences?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Yes! You can update your style preferences anytime through your profile settings or by retaking the style quiz.
                </CardDescription>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader>
                <CardTitle>What if I don't like the recommendations?</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription>
                  Provide feedback on recommendations to help our AI learn your preferences better. You can also adjust your style profile anytime.
                </CardDescription>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="w-full py-24 bg-gray-50">
        <div className="container px-4 md:px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl mb-4">
              Still Need Help?
            </h2>
            <p className="max-w-[600px] mx-auto text-lg text-muted-foreground">
              Our support team is here to help you get the most out of ClosetGPT
            </p>
          </div>
          
          <div className="grid gap-8 md:grid-cols-3 max-w-4xl mx-auto">
            <Card className="text-center p-8">
              <Mail className="w-12 h-12 text-blue-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Email Support</CardTitle>
              <CardDescription className="mb-4">
                Get help via email within 24 hours
              </CardDescription>
              <Button variant="outline" asChild>
                <Link href="mailto:support@closetgpt.com">
                  support@closetgpt.com
                </Link>
              </Button>
            </Card>
            
            <Card className="text-center p-8">
              <MessageCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Live Chat</CardTitle>
              <CardDescription className="mb-4">
                Chat with our support team in real-time
              </CardDescription>
              <Button variant="outline">
                Start Chat
              </Button>
            </Card>
            
            <Card className="text-center p-8">
              <Phone className="w-12 h-12 text-purple-600 mx-auto mb-4" />
              <CardTitle className="text-xl mb-4">Phone Support</CardTitle>
              <CardDescription className="mb-4">
                Call us for immediate assistance
              </CardDescription>
              <Button variant="outline" asChild>
                <Link href="tel:+1-800-CLOSETGPT">
                  1-800-CLOSETGPT
                </Link>
              </Button>
            </Card>
          </div>
        </div>
      </section>
    </div>
  );
} 