'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Lock, Sparkles, Crown, BookOpen, Shirt } from 'lucide-react';

interface UpgradePromptProps {
  feature: 'semantic_filtering' | 'style_persona' | 'advanced_features' | 'learn_from_outfit' | 'forgotten_gems' | 'outfit_limit_reached' | 'item_limit_reached';
  currentTier?: 'tier1' | 'tier2' | 'tier3';
  className?: string;
  limitType?: 'outfit' | 'item';
  currentCount?: number;
  limit?: number;
  resetDate?: string;
}

const FEATURE_INFO = {
  semantic_filtering: {
    title: 'Advanced Outfit Filtering',
    description: 'Unlock semantic search and smart filtering for better outfit recommendations',
    icon: <Sparkles className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'Semantic style matching',
      'Smart occasion filtering',
      'Advanced compatibility detection',
      'Intelligent outfit suggestions'
    ]
  },
  style_persona: {
    title: 'Style Persona Analysis',
    description: 'Get deep insights into your personal style with AI-powered analysis',
    icon: <Crown className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'Deep style profiling',
      'AI-powered style analysis',
      'Personal style recommendations',
      'Style evolution tracking'
    ]
  },
  advanced_features: {
    title: 'Premium Features',
    description: 'Access advanced features for a better experience',
    icon: <Sparkles className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'All advanced features',
      'Priority support',
      'Early access to new features'
    ]
  },
  learn_from_outfit: {
    title: 'Learn from This Outfit',
    description: 'Unlock AI-powered style insights to understand what makes outfits work',
    icon: <BookOpen className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'AI-powered outfit analysis',
      'Color strategy insights',
      'Texture and pattern balance tips',
      'Style synergy explanations',
      'Personalized style recommendations'
    ]
  },
  forgotten_gems: {
    title: 'Forgotten Gems',
    description: 'Rediscover items in your wardrobe you haven\'t worn in a while',
    icon: <Sparkles className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'Rediscover unworn wardrobe items',
      'AI-powered rediscovery potential scoring',
      'Personalized outfit suggestions',
      'Wardrobe analytics and insights',
      'Save money by using existing items'
    ]
  },
  outfit_limit_reached: {
    title: 'Monthly Limit Reached',
    description: 'You\'ve reached your monthly outfit generation limit',
    icon: <Sparkles className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'Unlimited outfit generations',
      'No monthly limits',
      'Generate as many outfits as you want',
      'All premium features included'
    ]
  },
  item_limit_reached: {
    title: 'Monthly Limit Reached',
    description: 'You\'ve reached your monthly wardrobe item limit',
    icon: <Shirt className="h-6 w-6" />,
    requiredTier: 'tier2',
    features: [
      'Unlimited wardrobe items',
      'No monthly limits',
      'Add as many items as you want',
      'All premium features included'
    ]
  }
};

export default function UpgradePrompt({ 
  feature, 
  currentTier = 'tier1',
  className = '',
  limitType,
  currentCount,
  limit,
  resetDate
}: UpgradePromptProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  
  const featureInfo = FEATURE_INFO[feature];
  const canAccess = currentTier === 'tier2' || currentTier === 'tier3';
  
  // If user already has access, don't show prompt
  if (canAccess) {
    return null;
  }
  
  // For limit-based prompts, customize the description
  let description = featureInfo.description;
  if (feature === 'outfit_limit_reached' && currentCount !== undefined && limit !== undefined) {
    description = `You've used ${currentCount} of ${limit} outfit generations this month.`;
    if (resetDate) {
      description += ` Resets on ${resetDate}.`;
    }
  } else if (feature === 'item_limit_reached' && currentCount !== undefined && limit !== undefined) {
    description = `You've added ${currentCount} of ${limit} wardrobe items this month.`;
    if (resetDate) {
      description += ` Resets on ${resetDate}.`;
    }
  }
  
  const handleUpgrade = () => {
    setLoading(true);
    router.push('/subscription');
  };
  
  const tierNames = {
    tier1: 'Free',
    tier2: 'Pro',
    tier3: 'Premium'
  };
  
  const requiredTierName = featureInfo.requiredTier === 'tier2' ? 'Pro' : 'Premium';
  
  return (
    <Card className={`border-primary/20 ${className}`}>
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="rounded-full bg-primary/10 p-3">
            {featureInfo.icon}
          </div>
        </div>
        <CardTitle className="text-2xl">{featureInfo.title}</CardTitle>
        <CardDescription className="text-base">
          {description}
        </CardDescription>
        <div className="flex justify-center mt-4">
          <Badge variant="secondary" className="gap-2">
            <Lock className="h-4 w-4" />
            Requires {requiredTierName} Subscription
          </Badge>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">What you'll get:</h4>
          <ul className="space-y-2">
            {featureInfo.features.map((feat, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-primary mt-0.5">✓</span>
                <span>{feat}</span>
              </li>
            ))}
          </ul>
        </div>
        
        <div className="pt-4 border-t">
          <Button 
            onClick={handleUpgrade}
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? 'Loading...' : `Upgrade to ${requiredTierName}`}
          </Button>
          <p className="text-xs text-center text-muted-foreground mt-2">
            You're currently on <strong>{tierNames[currentTier]}</strong> plan
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// Compact version for inline use
export function UpgradePromptInline({ 
  feature, 
  currentTier = 'tier1' 
}: UpgradePromptProps) {
  const router = useRouter();
  const featureInfo = FEATURE_INFO[feature];
  const canAccess = currentTier === 'tier2' || currentTier === 'tier3';
  
  if (canAccess) {
    return null;
  }
  
  const requiredTierName = featureInfo.requiredTier === 'tier2' ? 'Pro' : 'Premium';
  
  return (
    <div className="flex items-center justify-between p-4 bg-primary/5 rounded-lg border border-primary/20">
      <div className="flex items-center gap-3">
        <Lock className="h-5 w-5 text-primary" />
        <div>
          <p className="font-semibold">{featureInfo.title}</p>
          <p className="text-sm text-muted-foreground">
            Requires {requiredTierName} subscription
          </p>
        </div>
      </div>
      <Button 
        onClick={() => router.push('/subscription')}
        variant="outline"
        size="sm"
      >
        Upgrade
      </Button>
    </div>
  );
}

