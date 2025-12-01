'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  Crown, 
  Zap, 
  Users, 
  Star,
  Clock,
  TrendingUp,
  CheckCircle2,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { subscriptionService, type Subscription } from '@/lib/services/subscriptionService';

interface PremiumTeaserProps {
  variant?: 'default' | 'compact' | 'banner';
  showSocialProof?: boolean;
  showLimitedOffer?: boolean;
  className?: string;
  onClose?: () => void;
  dismissible?: boolean;
}

interface Testimonial {
  name: string;
  text: string;
  rating: number;
}

const TESTIMONIALS: Testimonial[] = [
  {
    name: 'Sarah M.',
    text: 'Unlimited outfits changed how I plan my week!',
    rating: 5
  },
  {
    name: 'Alex T.',
    text: 'The style insights are incredibly accurate.',
    rating: 5
  },
  {
    name: 'Jordan L.',
    text: 'Worth every penny for the time it saves me.',
    rating: 5
  }
];

const PREMIUM_FEATURES = [
  {
    icon: <Sparkles className="h-5 w-5" />,
    title: 'Unlimited Outfits',
    description: 'Generate as many outfits as you want'
  },
  {
    icon: <Crown className="h-5 w-5" />,
    title: 'Advanced Analytics',
    description: 'Deep insights into your style evolution'
  },
  {
    icon: <Zap className="h-5 w-5" />,
    title: 'Priority Support',
    description: '24-hour response time'
  },
  {
    icon: <TrendingUp className="h-5 w-5" />,
    title: 'Early Access',
    description: 'Try new features first'
  }
];

// Mock social proof data (in production, fetch from backend)
const SOCIAL_PROOF = {
  totalUsers: 12500,
  premiumUsers: 1850,
  recentUpgrades: 47 // in last 24 hours
};

export default function PremiumTeaser({
  variant = 'default',
  showSocialProof = true,
  showLimitedOffer = true,
  className = '',
  onClose,
  dismissible = true
}: PremiumTeaserProps) {
  const { user } = useFirebase();
  const router = useRouter();
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  // Check if user already has premium
  useEffect(() => {
    if (user) {
      subscriptionService.getCurrentSubscription(user)
        .then(sub => {
          setSubscription(sub);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [user]);

  // Countdown timer for limited offer (24 hours from now)
  useEffect(() => {
    if (!showLimitedOffer) return;

    const endTime = new Date();
    endTime.setHours(endTime.getHours() + 24);

    const updateTimer = () => {
      const now = new Date();
      const diff = endTime.getTime() - now.getTime();

      if (diff <= 0) {
        setTimeRemaining('');
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeRemaining(`${hours}h ${minutes}m ${seconds}s`);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [showLimitedOffer]);

  // Rotate testimonials
  useEffect(() => {
    if (!showSocialProof) return;

    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % TESTIMONIALS.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [showSocialProof]);

  const handleUpgrade = async () => {
    if (!user) {
      router.push('/signin');
      return;
    }

    try {
      const { checkout_url } = await subscriptionService.createCheckoutSession(user, 'tier2');
      window.location.href = checkout_url;
    } catch (error) {
      console.error('Failed to start checkout:', error);
    }
  };

  const handleDismiss = () => {
    setDismissed(true);
    if (onClose) {
      onClose();
    }
    // Store dismissal in localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('premium-teaser-dismissed', Date.now().toString());
    }
  };

  // Don't show if user already has premium
  if (loading || subscription?.tier === 'tier2' || subscription?.tier === 'tier3') {
    return null;
  }

  // Check if dismissed in localStorage
  if (typeof window !== 'undefined') {
    const dismissedTime = localStorage.getItem('premium-teaser-dismissed');
    if (dismissedTime) {
      const dismissedDate = parseInt(dismissedTime);
      const hoursSinceDismiss = (Date.now() - dismissedDate) / (1000 * 60 * 60);
      // Show again after 7 days
      if (hoursSinceDismiss < 168) {
        return null;
      }
    }
  }

  if (dismissed) {
    return null;
  }

  // Banner variant
  if (variant === 'banner') {
    return (
      <AnimatePresence>
        {!dismissed && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`relative bg-gradient-to-r from-purple-600 to-pink-600 text-white p-4 ${className}`}
          >
            <div className="container mx-auto flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Crown className="h-5 w-5" />
                <div>
                  <p className="font-semibold">Try Premium Free for 30 Days</p>
                  {showLimitedOffer && timeRemaining && (
                    <p className="text-sm opacity-90">Limited time: {timeRemaining} left</p>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleUpgrade}
                  variant="secondary"
                  size="sm"
                >
                  Start Free Trial
                </Button>
                {dismissible && (
                  <Button
                    onClick={handleDismiss}
                    variant="ghost"
                    size="sm"
                    className="text-white hover:bg-white/20"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    );
  }

  // Compact variant
  if (variant === 'compact') {
    return (
      <Card className={`border-primary/20 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 ${className}`}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-full bg-primary/10 p-2">
                <Crown className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="font-semibold text-sm">Unlock Premium Features</p>
                {showLimitedOffer && timeRemaining && (
                  <p className="text-xs text-muted-foreground">
                    <Clock className="h-3 w-3 inline mr-1" />
                    {timeRemaining} left
                  </p>
                )}
              </div>
            </div>
            <Button onClick={handleUpgrade} size="sm">
              Try Free
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Default variant
  return (
    <AnimatePresence>
      {!dismissed && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className={className}
        >
          <Card className="border-primary/20 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20 overflow-hidden">
            {dismissible && (
              <div className="absolute top-2 right-2 z-10">
                <Button
                  onClick={handleDismiss}
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            )}

            <CardHeader className="text-center pb-4">
              <div className="flex justify-center mb-4">
                <div className="rounded-full bg-gradient-to-br from-purple-500 to-pink-500 p-4">
                  <Crown className="h-8 w-8 text-white" />
                </div>
              </div>
              <CardTitle className="text-2xl">Try Premium Free</CardTitle>
              <CardDescription className="text-base">
                30-day free trial • Cancel anytime
              </CardDescription>
              {showLimitedOffer && timeRemaining && (
                <Badge variant="destructive" className="mt-2">
                  <Clock className="h-3 w-3 mr-1" />
                  Limited time: {timeRemaining} left
                </Badge>
              )}
            </CardHeader>

            <CardContent className="space-y-6">
              {/* Premium Features Preview */}
              <div>
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Premium Features
                </h4>
                <div className="grid grid-cols-2 gap-3">
                  {PREMIUM_FEATURES.map((feature, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2 p-2 rounded-lg bg-white/50 dark:bg-gray-900/50"
                    >
                      <div className="text-primary mt-0.5">{feature.icon}</div>
                      <div>
                        <p className="text-sm font-medium">{feature.title}</p>
                        <p className="text-xs text-muted-foreground">{feature.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Social Proof */}
              {showSocialProof && (
                <div className="space-y-3 pt-4 border-t">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Users className="h-4 w-4 text-primary" />
                      <span className="font-medium">
                        {SOCIAL_PROOF.premiumUsers.toLocaleString()}+ Premium Users
                      </span>
                    </div>
                    {SOCIAL_PROOF.recentUpgrades > 0 && (
                      <Badge variant="secondary" className="text-xs">
                        {SOCIAL_PROOF.recentUpgrades} joined today
                      </Badge>
                    )}
                  </div>

                  {/* Testimonials */}
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentTestimonial}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="p-3 bg-white/50 dark:bg-gray-900/50 rounded-lg"
                    >
                      <div className="flex items-center gap-1 mb-1">
                        {[...Array(TESTIMONIALS[currentTestimonial].rating)].map((_, i) => (
                          <Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                        ))}
                      </div>
                      <p className="text-sm italic">"{TESTIMONIALS[currentTestimonial].text}"</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        — {TESTIMONIALS[currentTestimonial].name}
                      </p>
                    </motion.div>
                  </AnimatePresence>
                </div>
              )}

              {/* CTA Button */}
              <div className="pt-4">
                <Button
                  onClick={handleUpgrade}
                  className="w-full bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700"
                  size="lg"
                >
                  <Crown className="h-5 w-5 mr-2" />
                  Start 30-Day Free Trial
                </Button>
                <p className="text-xs text-center text-muted-foreground mt-2">
                  No credit card required • Cancel anytime
                </p>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

