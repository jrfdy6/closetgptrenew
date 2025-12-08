"use client";

import { useState } from 'react';
import Navigation from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Target, TrendingUp, Sparkles } from 'lucide-react';
import ChallengeList from '@/components/gamification/ChallengeList';
import BadgeDisplay from '@/components/gamification/BadgeDisplay';
import { useAuthContext } from '@/contexts/AuthContext';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import dynamic from 'next/dynamic';

// Dynamically import gamification components to avoid SSR issues
const GamificationSummaryCard = dynamic(
  () => import('@/components/gamification/GamificationSummaryCard'),
  { ssr: false, loading: () => <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" /> }
);

const TVECard = dynamic(
  () => import('@/components/gamification/TVECard'),
  { ssr: false, loading: () => <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" /> }
);

const AIFitScoreCard = dynamic(
  () => import('@/components/gamification/AIFitScoreCard'),
  { ssr: false, loading: () => <div className="h-64 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" /> }
);

export default function ChallengesPage() {
  const { user, loading } = useAuthContext();

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-1/3" />
            <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center max-w-md mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Sign In to View Challenges
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              Complete challenges to earn XP, unlock badges, and maximize your wardrobe!
            </p>
            <Link href="/signin">
              <Button>Sign In</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navigation />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Target className="w-8 h-8 text-purple-600" />
            Challenges
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Complete challenges to earn XP, unlock badges, and get the most out of your wardrobe
          </p>
        </div>

        {/* Progress Tracking Section */}
        <div className="mb-8 space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-1">
              <Sparkles className="w-5 h-5 text-purple-600" />
              Your Progress
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Track your wardrobe optimization journey
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <GamificationSummaryCard />
            <TVECard />
            <AIFitScoreCard />
          </div>
        </div>

        {/* Challenge List */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-blue-600" />
            Weekly Challenges
          </h2>
          <ChallengeList />
        </div>

        {/* Badge Showcase */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-[var(--copper-dark)]" />
            Your Badges
          </h2>
          <BadgeDisplay />
        </div>
      </div>
    </div>
  );
}

