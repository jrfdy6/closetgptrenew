"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/use-toast';
import { doc, getDoc, collection, getDocs, query, limit } from 'firebase/firestore';
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
  const [firestoreError, setFirestoreError] = useState(false);
  const [hasExistingData, setHasExistingData] = useState(false);
  const stats = useWardrobeStats();

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      router.push('/signin');
      return;
    }

    const checkExistingData = async () => {
      if (!db) {
        console.log('🎯 DASHBOARD: No Firestore db available');
        setFirestoreError(true);
        setLoading(false);
        return;
      }
      
      try {
        console.log('🎯 DASHBOARD: Checking for existing data for user:', user.uid);
        
        // Check for profile first
        const profileDoc = await getDoc(doc(db, 'users', user.uid));
        if (profileDoc.exists()) {
          const profileData = profileDoc.data();
          console.log('🎯 DASHBOARD: Profile found:', profileData);
          setProfile(profileData);
          
          // If profile exists and onboarding is completed, we're good
          if (profileData.onboardingCompleted) {
            console.log('🎯 DASHBOARD: Profile exists and onboarding completed');
            setHasExistingData(true);
            setLoading(false);
            return;
          }
        }
        
        // If no profile or onboarding not completed, check for wardrobe items
        console.log('🎯 DASHBOARD: Checking for wardrobe items...');
        const wardrobeQuery = query(collection(db, 'wardrobe'), limit(1));
        const wardrobeSnapshot = await getDocs(wardrobeQuery);
        
        if (!wardrobeSnapshot.empty) {
          console.log('🎯 DASHBOARD: Found wardrobe items, user has existing data');
          setHasExistingData(true);
          // Create a default profile for existing users
          setProfile({
            onboardingCompleted: true,
            name: user.displayName || 'User',
            email: user.email
          });
        } else {
          // Check for outfits as well
          console.log('🎯 DASHBOARD: Checking for outfits...');
          const outfitsQuery = query(collection(db, 'outfits'), limit(1));
          const outfitsSnapshot = await getDocs(outfitsQuery);
          
          if (!outfitsSnapshot.empty) {
            console.log('🎯 DASHBOARD: Found outfits, user has existing data');
            setHasExistingData(true);
            // Create a default profile for existing users
            setProfile({
              onboardingCompleted: true,
              name: user.displayName || 'User',
              email: user.email
            });
          } else {
            console.log('🎯 DASHBOARD: No existing data found, showing onboarding');
            setHasExistingData(false);
          }
        }
      } catch (error) {
        console.error('Error checking existing data:', error);
        setFirestoreError(true);
        // Assume user has existing data if we can't check
        setHasExistingData(true);
        setProfile({
          onboardingCompleted: true,
          name: user.displayName || 'User',
          email: user.email
        });
      } finally {
        setLoading(false);
      }
    };

    checkExistingData();
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

  // Debug: Log profile data
  console.log('🎯 DASHBOARD: Profile check - profile exists:', !!profile);
  console.log('🎯 DASHBOARD: Profile data:', profile);
  console.log('🎯 DASHBOARD: onboardingCompleted:', profile?.onboardingCompleted);
  console.log('🎯 DASHBOARD: Firestore error:', firestoreError);
  console.log('🎯 DASHBOARD: Has existing data:', hasExistingData);

  // Show onboarding prompt only if no profile, no onboarding completed, and no existing data
  if (!profile || (!profile.onboardingCompleted && !hasExistingData)) {
    console.log('🎯 DASHBOARD: Showing onboarding prompt - no profile, no onboarding, no existing data');
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
                  {firestoreError 
                    ? "Let's get you started with your AI styling experience."
                    : "Let's personalize your AI styling experience."
                  }
                </p>
                {firestoreError && (
                  <p className="text-sm text-orange-600 mt-2">
                    Note: Some features may be limited due to connection issues.
                  </p>
                )}
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
            <div className="w-10 h-10 bg-gradient-to-br from-red-500/20 to-red-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <Heart className="h-5 w-5 text-red-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : stats.favoritesCount}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 'Loved items'}
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover animate-fade-in stagger-3">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">Style Goals</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500/20 to-purple-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <Target className="h-5 w-5 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : `${stats.styleGoalsCompleted}/${stats.totalStyleGoals}`}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 'Completed'}
            </p>
          </CardContent>
        </Card>

        <Card className="card-hover animate-fade-in stagger-4">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-subheader font-medium">This Week</CardTitle>
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500/20 to-blue-600/20 rounded-xl flex items-center justify-center icon-bounce">
              <Calendar className="h-5 w-5 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {stats.loading ? '...' : stats.outfitsThisWeek}
            </div>
            <p className="text-secondary">
              {stats.loading ? 'Loading...' : 'Outfits worn'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Rest of dashboard content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        <Suspense fallback={<Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded"></div></CardContent></Card>}>
          <LazyTodaysOutfitRecommendation />
        </Suspense>
        
        <Suspense fallback={<Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded"></div></CardContent></Card>}>
          <LazyWardrobeInsights />
        </Suspense>
        
        <Suspense fallback={<Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded"></div></CardContent></Card>}>
          <LazyStyleGoalsProgress />
        </Suspense>
        
        <Suspense fallback={<Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded"></div></CardContent></Card>}>
          <LazyWardrobeGapAnalysis />
        </Suspense>
        
        <Suspense fallback={<Card><CardContent className="p-6"><div className="animate-pulse h-64 bg-gray-200 rounded"></div></CardContent></Card>}>
          <LazyForgottenGems />
        </Suspense>
      </div>
    </div>
  );
}
