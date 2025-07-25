"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { doc, getDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { 
  Sparkles, 
  TrendingUp, 
  Heart, 
  ShoppingBag, 
  Plus, 
  Target, 
  Palette, 
  Calendar, 
  ArrowRight,
  Zap,
  Star,
  User
} from 'lucide-react';
import { Suspense } from 'react';
import Link from 'next/link';

// Import dashboard components with lazy loading
import { 
  LazyWardrobeInsights,
  LazyStyleGoalsProgress,
  LazyWardrobeGapAnalysis,
  LazyForgottenGems,
  LazyTodaysOutfitRecommendation
} from '@/lib/utils/dynamic-imports';
import { useWardrobeStats } from '@/lib/hooks/useWardrobeStats';
import { PageLoadingSkeleton } from '@/components/ui/loading-states';

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const { toast } = useToast();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const stats = useWardrobeStats();

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      router.push('/signin');
      return;
    }

    const fetchProfile = async () => {
      if (!db) return;
      
      try {
        const profileDoc = await getDoc(doc(db, 'profiles', user.uid));
        if (profileDoc.exists()) {
          setProfile(profileDoc.data());
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [user, authLoading, router]);

  if (authLoading || loading) {
    return (
      <div className="container-readable py-8">
        <PageLoadingSkeleton 
          showHero={true}
          showStats={true}
          showContent={true}
        />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container-readable py-8">
        <Card className="max-w-2xl mx-auto card-enhanced">
          <CardContent className="p-8">
            <div className="text-center space-y-6">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 rounded-2xl flex items-center justify-center mx-auto">
                <User className="w-8 h-8 text-emerald-600" />
              </div>
              <div>
                <h1 className="text-hero text-foreground mb-2">Complete Your Profile</h1>
                <p className="text-secondary">
                  Let's personalize your AI styling experience.
                </p>
              </div>
              <Button 
                onClick={() => router.push('/onboarding')}
                className="shadow-md hover:shadow-lg"
              >
                Get Started
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-section py-8">
      {/* Hero Header */}
      <div className="gradient-hero rounded-2xl p-6 sm:p-8 mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-6">
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
              </div>
              <h1 className="text-2xl sm:text-hero text-foreground">Welcome back!</h1>
            </div>
            <p className="text-secondary text-base sm:text-lg">Ready to explore your wardrobe and create amazing outfits.</p>
          </div>
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full sm:w-auto">
            <Button asChild className="shadow-md hover:shadow-lg w-full sm:w-auto">
              <Link href="/upload">
                <Plus className="w-4 h-4 mr-2" />
                Add Item
              </Link>
            </Button>
            <Button variant="outline" asChild className="shadow-md hover:shadow-lg w-full sm:w-auto">
              <Link href="/outfits">
                View All Outfits
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
        <Card className="card-hover animate-fade-in stagger-1">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">Total Items</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500/20 to-emerald-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <TrendingUp className="h-5 w-5 text-emerald-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : stats.totalItems}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 'In your wardrobe'}
            </p>
          </CardContent>
        </Card>
        
        <Card className="card-hover animate-fade-in stagger-2">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">Favorites</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-yellow-500/20 to-yellow-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <Heart className="h-5 w-5 text-yellow-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : stats.favoritesCount}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 'Based on your usage'}
            </p>
          </CardContent>
        </Card>
        
        <Card className="card-hover animate-fade-in stagger-3">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">Style Goals</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-violet-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <Target className="h-5 w-5 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : `${stats.styleGoalsCompleted}/${stats.totalStyleGoals}`}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 
                stats.totalStyleGoals > 0 ? 
                  `${Math.round((stats.styleGoalsCompleted / stats.totalStyleGoals) * 100)}% completed` :
                  'No goals set'
              }
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover animate-fade-in stagger-4">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">AI Insights</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500/20 to-yellow-500/20 rounded-xl flex items-center justify-center icon-bounce">
              <Zap className="h-5 w-5 text-emerald-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              <span className="text-emerald-600">24/7</span>
            </div>
            <p className="text-secondary">
              Smart insights
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="space-section">
        {/* Side by Side - Today's Outfit and Forgotten Gems */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Left Column - Today's Outfit */}
          <div>
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <Zap className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-subheader font-semibold">Today's AI Recommendation</h2>
              <Badge variant="secondary" className="bg-gradient-to-r from-yellow-500 to-yellow-600 text-white border-0">
                Fresh
              </Badge>
            </div>
            <LazyTodaysOutfitRecommendation />
          </div>
          
          {/* Right Column - Forgotten Gems */}
          <div>
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-lg flex items-center justify-center">
                <Star className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-subheader font-semibold">Forgotten Gems</h2>
              <Badge variant="outline" className="text-xs">
                Rediscover
              </Badge>
            </div>
            <Suspense fallback={
              <Card className="card-enhanced p-8">
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-emerald-200 border-t-emerald-600"></div>
                  <span className="ml-3 text-muted-foreground">Finding your hidden treasures...</span>
                </div>
              </Card>
            }>
              <LazyForgottenGems />
            </Suspense>
          </div>
        </div>
        
        {/* Gap Analysis and Goals - Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column - Gap Analysis */}
          <div className="lg:col-span-2 space-section">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-lg flex items-center justify-center">
                <Palette className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-subheader font-semibold">Wardrobe Gap Analysis</h2>
            </div>
            
            <Suspense fallback={
              <Card className="card-enhanced p-6">
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-2 border-emerald-200 border-t-emerald-600"></div>
                  <span className="ml-2 text-sm text-muted-foreground">Analyzing...</span>
                </div>
              </Card>
            }>
              <LazyWardrobeGapAnalysis />
            </Suspense>
          </div>

          {/* Right Column - Goals */}
          <div className="space-section">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-violet-600 rounded-lg flex items-center justify-center">
                <Target className="w-4 h-4 text-white" />
              </div>
              <h2 className="text-subheader font-semibold">Style Goals & Progress</h2>
            </div>
            <Suspense fallback={
              <Card className="card-enhanced p-8">
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-8 w-8 border-2 border-emerald-200 border-t-emerald-600"></div>
                  <span className="ml-3 text-muted-foreground">Loading your goals...</span>
                </div>
              </Card>
            }>
              <LazyStyleGoalsProgress />
            </Suspense>
          </div>
        </div>

        {/* Full Width - Wardrobe Insights */}
        <div className="mb-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-4 h-4 text-white" />
            </div>
            <h2 className="text-subheader font-semibold">Wardrobe Insights</h2>
            <Badge variant="secondary" className="bg-gradient-to-r from-blue-500 to-blue-600 text-white border-0">
              Analytics
            </Badge>
          </div>
          <Suspense fallback={
            <Card className="card-enhanced p-6">
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-6 w-6 border-2 border-emerald-200 border-t-emerald-600"></div>
                <span className="ml-2 text-sm text-muted-foreground">Loading insights...</span>
              </div>
            </Card>
          }>
            <LazyWardrobeInsights />
          </Suspense>
        </div>
      </div>
    </div>
  );
} // Force fresh deployment with @ alias imports
