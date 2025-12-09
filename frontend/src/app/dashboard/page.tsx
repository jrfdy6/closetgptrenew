"use client";

import { useState, useEffect, useMemo } from "react";
import Navigation from "@/components/Navigation";
import ClientOnlyNav from "@/components/ClientOnlyNav";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  Star, 
  Calendar, 
  Palette, 
  Shirt, 
  Sparkles, 
  Users, 
  Zap,
  Heart,
  Target,
  CheckCircle,
  ArrowRight,
  AlertCircle,
  Info,
  RefreshCw,
  Upload,
  X
} from "lucide-react";
import Link from "next/link";
import { useAuthContext } from "@/contexts/AuthContext";
import dynamic from 'next/dynamic';
import { dashboardService, DashboardData, TopItem } from "@/lib/services/dashboardService";
import WardrobeInsightsHub from '@/components/ui/wardrobe-insights-hub';
import SmartWeatherOutfitGenerator from "@/components/SmartWeatherOutfitGenerator";
import { useAutoWeather } from '@/hooks/useWeather';
import PremiumTeaser from '@/components/PremiumTeaser';
import { useGamificationStats } from '@/hooks/useGamificationStats';

// Gamification components removed - shuffle moved to outfit generation page

type WardrobeCategory = "top" | "bottom" | "shoe" | "accessory" | "jacket";

const CATEGORY_CONFIG: Array<{ id: WardrobeCategory; keywords: string[] }> = [
  {
    id: "top",
    keywords: ["top", "shirt", "t-shirt", "tee", "blouse", "sweater", "hoodie", "polo", "tank", "dress", "longsleeve", "long sleeve"],
  },
  {
    id: "bottom",
    keywords: ["bottom", "pant", "pants", "trouser", "jean", "short", "skirt", "chino"],
  },
  {
    id: "shoe",
    keywords: ["shoe", "sneaker", "boot", "footwear", "loafer", "heel", "sandals"],
  },
  {
    id: "accessory",
    keywords: ["accessory", "belt", "watch", "scarf", "hat", "glove", "bag", "bracelet", "necklace", "jewelry", "sunglass", "sunglasses"],
  },
  {
    id: "jacket",
    keywords: ["jacket", "coat", "outerwear", "blazer"],
  },
];

const CATEGORY_LABELS: Record<WardrobeCategory, string> = {
  top: "Top",
  bottom: "Bottom",
  shoe: "Shoes",
  accessory: "Accessory",
  jacket: "Jacket",
};

// Dynamically import components to avoid SSR issues
const WardrobeStats = dynamic(() => import('@/components/WardrobeStats'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading stats...</div>
});

const ForgottenGems = dynamic(() => import('@/components/ForgottenGems'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading forgotten gems...</div>
});

const BatchImageUpload = dynamic(() => import('@/components/BatchImageUpload'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading upload component...</div>
});

// Navigation now handled via ClientOnlyNav wrapper


export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingAsWorn, setMarkingAsWorn] = useState(false);
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [windowWidth, setWindowWidth] = useState<number>(0);
  const { user, loading } = useAuthContext();
  
  // Weather hook for automatic location detection
  const { weather, fetchWeatherByLocation } = useAutoWeather();
  
  // Gamification stats for Level and AI Fit Score
  const { stats: gamificationStats } = useGamificationStats();
  
  const topItemsByCategory = useMemo(() => {
    if (!dashboardData?.topItems) return [];

    const usedIds = new Set<string>();
    const results: Array<TopItem & { category: WardrobeCategory }> = [];

    CATEGORY_CONFIG.forEach(({ id, keywords }) => {
      const match = dashboardData.topItems.find((item) => {
        if (!item || usedIds.has(item.id)) return false;
        const typeRaw = (item.type || "").toLowerCase();
        const nameRaw = (item.name || "").toLowerCase();
        const type = (item.type || "").toLowerCase().replace(/\s+/g, "");
        const keywordMatchesType = keywords.some((keyword) => type.includes(keyword.replace(/\s+/g, "")));
        if (keywordMatchesType) return true;

        if (
          id === "top" &&
          keywords.some((keyword) => typeRaw.includes(keyword.toLowerCase()) || nameRaw.includes(keyword.toLowerCase()))
        ) {
          return true;
        }

        return keywords.some((keyword) => nameRaw.includes(keyword.toLowerCase()));
      });

      if (match) {
        usedIds.add(match.id);
        results.push({ ...match, category: id });
      }
    });

    return results;
  }, [dashboardData?.topItems]);
  
  console.log('🔍 Dashboard mounted, weather state:', weather?.location);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const query = window.matchMedia('(max-width: 640px)');
    const update = (event: MediaQueryList | MediaQueryListEvent) => {
      if ('matches' in event) {
        setIsMobile(event.matches);
      } else {
        setIsMobile(event.currentTarget ? event.currentTarget.matches : query.matches);
      }
    };
    update(query);
    const handler = (event: MediaQueryListEvent) => update(event);
    query.addEventListener('change', handler);
    return () => query.removeEventListener('change', handler);
  }, []);

  // Track window width for responsive grid
  useEffect(() => {
    if (typeof window === 'undefined') return;
    const updateWidth = () => setWindowWidth(window.innerWidth);
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  // Automatic location prompt when dashboard loads
  useEffect(() => {
    console.log('🔍 Dashboard location prompt check:', { user: !!user, weather: weather?.location, hasAsked: sessionStorage.getItem('has-asked-for-location') });
    
    if (user && weather && (weather.location === "Unknown Location" || weather.location === "Default Location")) {
      // Check if we've already asked for location in this session
      const hasAskedForLocation = sessionStorage.getItem('has-asked-for-location');
      
      if (!hasAskedForLocation) {
        console.log('🌤️ Showing location prompt');
        // Show a simple browser prompt for location
        const shouldGetLocation = confirm(
          "🌤️ Get accurate weather data for better outfit recommendations?\n\n" +
          "We need your location to provide weather-perfect outfit suggestions.\n" +
          "Click OK to use your current location, or Cancel to skip."
        );
        
        // Mark that we've asked for location in this session
        sessionStorage.setItem('has-asked-for-location', 'true');
        
        if (shouldGetLocation) {
          console.log('🌤️ User accepted location prompt, fetching location...');
          fetchWeatherByLocation();
        } else {
          console.log('🌤️ User declined location prompt');
        }
      } else {
        console.log('🌤️ Already asked for location in this session');
      }
    }
  }, [user, weather, fetchWeatherByLocation]);

  // Fetch real dashboard data
  useEffect(() => {
    if (!loading) {
      fetchDashboardData();
    }
  }, [user, loading]);

  // Listen for outfit marked as worn events to refresh dashboard
  useEffect(() => {
    const handleOutfitMarkedAsWorn = (event: CustomEvent) => {
      console.log('🔄 Dashboard: Outfit marked as worn, refreshing data...', event.detail);
      // Add a small delay to allow Firestore write to propagate
      // This ensures the query picks up the newly created outfit_history entry
      setTimeout(() => {
        console.log('🔄 Dashboard: Fetching fresh data from server...');
        if (user) {
          fetchDashboardDataFresh();
        }
      }, 2000); // 2 second delay for Firestore consistency
    };

    window.addEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    
    return () => {
      window.removeEventListener('outfitMarkedAsWorn', handleOutfitMarkedAsWorn as EventListener);
    };
  }, [user]); // Only depend on user, not fetchDashboardData

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('🔍 DEBUG: Dashboard: Starting to fetch real data...');
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      const data = await dashboardService.getDashboardData(user);
      console.log('🔍 DEBUG: Dashboard: Real data received:', data);
      console.log('🔍 DEBUG: Dashboard: Data type:', typeof data);
      console.log('🔍 DEBUG: Dashboard: Data keys:', Object.keys(data || {}));
      console.log('🔍 DEBUG: Dashboard: Total items value:', data?.totalItems);
      
      setDashboardData(data);
      console.log('🔍 DEBUG: Dashboard: State update called with:', data);
    } catch (err) {
      console.error('🔍 DEBUG: Dashboard: Error fetching data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDashboardDataFresh = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('🔍 DEBUG: Dashboard: Starting to fetch FRESH data (bypassing cache)...');
      
      if (!user) {
        throw new Error('User not authenticated');
      }
      
      const data = await dashboardService.getDashboardData(user, true); // Force fresh
      console.log('🔍 DEBUG: Dashboard: FRESH data received:', data);
      console.log('🔍 DEBUG: Dashboard: FRESH outfitsThisWeek:', data?.outfitsThisWeek);
      
      setDashboardData(data);
      console.log('🔍 DEBUG: Dashboard: State update called with FRESH data:', data);
    } catch (err) {
      console.error('🔍 DEBUG: Dashboard: Error fetching FRESH data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAsWorn = async () => {
    if (!user || !(dashboardData?.todaysOutfit as any)?.suggestionId) return;
    
    try {
      setMarkingAsWorn(true);
      const success = await dashboardService.markSuggestionAsWorn(user, (dashboardData.todaysOutfit as any).suggestionId);
      
      if (success) {
        // Refresh dashboard data to show updated state
        await fetchDashboardData();
      } else {
        setError('Failed to mark outfit as worn');
      }
    } catch (err) {
      console.error('Error marking outfit as worn:', err);
      setError('Failed to mark outfit as worn');
    } finally {
      setMarkingAsWorn(false);
    }
  };

  // Clean, simple analytics - no complex initialization functions needed
  // Force browser cache refresh - removed all handleInitializeStats references


  const handleRetry = () => {
    if (user) {
      fetchDashboardData();
    }
  };


  // Show loading state while authentication is resolving
  if (loading || isLoading) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-emerald-600 mx-auto"></div>
            <p className="mt-4 text-lg text-gray-600 dark:text-gray-400">Loading your dashboard...</p>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-500">
              Fetching real-time data from your wardrobe...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Show authentication required if no user
  if (!user) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Authentication Required</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">Please sign in to access your dashboard.</p>
            <Link href="/signin">
              <Button>Sign In</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Show error state if data fetching failed
  if (error) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Dashboard Error</h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button onClick={handleRetry}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Retry
              </Button>
              <Link href="/wardrobe">
                <Button variant="outline">Go to Wardrobe</Button>
              </Link>
              <Link href="/profile">
                <Button variant="outline">Go to Profile</Button>
              </Link>
            </div>
            <p className="mt-4 text-sm text-gray-500 dark:text-gray-400 max-w-md mx-auto">
              If you continue to see this error, please check the browser console (F12) for detailed debug information.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const totalStyleGoals = dashboardData?.totalStyleGoals ?? 0;
  const styleGoalsCompleted = dashboardData?.styleGoalsCompleted ?? 0;
  const clampedStyleGoalsCompleted = totalStyleGoals > 0
    ? Math.min(styleGoalsCompleted, totalStyleGoals)
    : styleGoalsCompleted;

  // Main dashboard - user is authenticated and data is loaded
  return (
    <div className="min-h-screen">
      <Navigation />
      
      {/* Main Content - Mobile Optimized - Bottom padding for nav */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12 pb-[120px] overflow-x-hidden">
        
        {/* Welcome Section - "Silent Luxury" Design */}
        <div className="mb-6 sm:mb-8">
          <div className="component-card p-6 sm:p-8 sm:rounded-3xl">
            <h1 className="heading-xl gradient-copper-text mb-2 sm:mb-3 component-text-primary">
              Let&apos;s get you dressed ✨
            </h1>
            <p className="text-body-lg component-text-secondary">
              Your look today is ready when you are.
            </p>
            <div className="mt-6 flex flex-col sm:flex-row gap-3">
            <Button
              onClick={() => {
                const element = document.getElementById('smart-weather-outfit');
                if (element) {
                  element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
              }}
              className="gradient-copper-gold text-primary-foreground px-6 py-3 rounded-2xl font-semibold shadow-lg shadow-[var(--copper-dark)]/25 hover:opacity-90 transition-all duration-200 sm:hover:scale-[1.02] active:scale-[0.98]"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Generate today&apos;s fit
            </Button>
            <Button
                onClick={() => setShowBatchUpload(true)}
                className="component-button-outline px-6 py-3"
              >
                <Upload className="w-5 h-5 mr-2" />
                Add items with AI
              </Button>
            </div>
          </div>
        </div>


        {/* Modern Stats Cards - Mobile First Grid */}
        <div 
          className="grid gap-3 sm:gap-4 lg:gap-6 mb-6 sm:mb-8" 
          style={{ 
            gridTemplateColumns: windowWidth >= 1024 ? 'repeat(6, minmax(0, 1fr))' : 'repeat(3, minmax(0, 1fr))' 
          }}
        >

          {/* Style Goals Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[var(--copper-mid)]/35 to-[var(--copper-mid)]/40 dark:from-[var(--copper-light)]/20 dark:to-[var(--copper-mid)]/25 rounded-xl flex items-center justify-center shadow-inner">
                <Target className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-light)]" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">Style Goals</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-copper-text component-text-primary">
                  {totalStyleGoals > 0 ? Math.round((clampedStyleGoalsCompleted / totalStyleGoals) * 100) : 0}%
                </p>
              </div>
            </div>
          </div>

          {/* Wardrobe Optimization Journey Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[var(--copper-mid)]/30 to-[var(--copper-mid)]/30 dark:from-[var(--copper-mid)]/25 dark:to-[var(--copper-mid)]/25 rounded-xl flex items-center justify-center shadow-inner">
                <Zap className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-light)]" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">Your Progress</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold gradient-copper-text component-text-primary">
                  Level {gamificationStats?.level?.level || 1}
                </p>
              </div>
            </div>
          </div>

          {/* AI Fit Score Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[var(--copper-mid)]/30 to-primary/35 dark:from-[var(--copper-mid)]/20 dark:to-primary/25 rounded-xl flex items-center justify-center shadow-inner">
                <Star className="h-5 w-5 sm:h-6 sm:w-6 text-primary/80 dark:text-primary/70" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">AI Fit Score</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#E8A4A4] to-[#D4A574] bg-clip-text text-transparent mb-0.5">
                  {Math.round(gamificationStats?.ai_fit_score?.total_score || 0)}
                </p>
                <p className="text-xs sm:text-sm component-text-secondary">
                  {gamificationStats?.ai_fit_score?.total_score === undefined || gamificationStats?.ai_fit_score?.total_score === 0 
                    ? 'Getting Started' 
                    : gamificationStats?.ai_fit_score?.total_score >= 75 
                      ? 'AI Master' 
                      : gamificationStats?.ai_fit_score?.total_score >= 50 
                        ? 'AI Apprentice' 
                        : 'Learning'}
                </p>
              </div>
            </div>
          </div>

          {/* Total Items Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[#E8C8A0]/35 to-[#C9956F]/35 dark:from-[#D4A574]/20 dark:to-[#C9956F]/20 rounded-xl flex items-center justify-center shadow-inner">
                <Shirt className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">Total items</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#D4A574] to-[#C9956F] bg-clip-text text-transparent">
                  {dashboardData?.totalItems || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Favorites Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[var(--copper-mid)]/30 to-primary/35 dark:from-[var(--copper-mid)]/20 dark:to-primary/25 rounded-xl flex items-center justify-center shadow-inner">
                <Heart className="h-5 w-5 sm:h-6 sm:w-6 text-primary/80 dark:text-primary/70" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">Favorites</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#E8A4A4] to-[#D4A574] bg-clip-text text-transparent">
                  {dashboardData?.favorites || 0}
                </p>
              </div>
            </div>
          </div>

          {/* This Week Card */}
          <div className="component-card p-4 sm:p-6">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-[#D4A574]/30 to-[#C9956F]/30 dark:from-[#C9956F]/25 dark:to-[#B8860B]/25 rounded-xl flex items-center justify-center shadow-inner">
                <Calendar className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium component-text-secondary mb-1">This week</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-[#C9956F] to-[#D4A574] bg-clip-text text-transparent">
                  {dashboardData?.outfitsThisWeek || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

          {/* Usage Indicator - Full */}
          <div className="mb-6 sm:mb-8">

          {/* Premium Teaser */}
          <PremiumTeaser 
            variant="default" 
            showSocialProof={true}
            className="mb-8"
          />
        </div>

        {/* Smart Weather Outfit Generator */}
        <div id="smart-weather-outfit" className="mb-6 sm:mb-12">
                  <SmartWeatherOutfitGenerator 
                    onOutfitGenerated={(outfit) => {
                      console.log('🎯 Smart weather outfit generated:', outfit);
                    }}
                  />
                    </div>

        {/* Backend Status Message - Show when no items loaded */}
        {dashboardData && dashboardData.totalItems === 0 && !isLoading && (
          <Card className="mb-8">
            <CardContent className="p-6">
              <div className="flex items-start space-x-3">
                <Info className="h-6 w-6 text-[var(--copper-mid)] dark:text-[var(--copper-mid)] flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h3 className="text-lg font-display font-semibold text-card-foreground mb-2">
                    {isMobile ? 'Connection Issue' : 'Backend setup in progress'}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {isMobile 
                      ? 'Unable to load wardrobe items. This may be due to a slow mobile connection. Please try refreshing or check your network connection.'
                      : 'Your dashboard is live. Wardrobe data will appear as soon as the backend endpoints finish syncing.'}
                  </p>
                  <Button
                    onClick={() => {
                      fetchDashboardData();
                    }}
                    variant="outline"
                    size="sm"
                    className="border-[var(--copper-mid)]/30 text-[var(--copper-mid)] hover:bg-[var(--copper-mid)]/10"
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry Loading
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Today's Outfit Section - Only show if we have backend suggestion data AND no weather generator outfit */}
        {dashboardData?.todaysOutfit && (dashboardData.todaysOutfit as any)?.suggestionId && (
        <div className="component-card mb-6 sm:mb-8 lg:mb-12 sm:rounded-3xl">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-border/60 dark:border-border/70">
            <h2 className="text-xl sm:text-2xl font-display font-semibold text-card-foreground mb-1 sm:mb-2">Today&apos;s outfit suggestion</h2>
            <p className="text-sm sm:text-base text-muted-foreground">Powered by your Easy Outfit stylist</p>
          </div>
          <div className="p-4 sm:p-6 lg:p-8">
            {dashboardData?.todaysOutfit ? (
              <div className="space-y-4 sm:space-y-6">
                {/* Outfit Header */}
                <div className="component-card-nested text-center p-4 sm:p-6 rounded-xl sm:rounded-2xl">
                  <p className="text-sm sm:text-base font-medium text-muted-foreground mb-2">
                    {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                  </p>
                  <Badge variant="secondary" className="text-xs sm:text-sm font-bold uppercase tracking-wide mb-3 sm:mb-4">
                    {dashboardData.todaysOutfit.occasion}
                  </Badge>
                </div>

                {/* Outfit Details */}
                <div className="space-y-3 sm:space-y-4">
                  <div className="component-card-nested rounded-xl sm:rounded-2xl p-4 sm:p-5">
                    <div className="flex items-center space-x-4 mb-3">
                      <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-[var(--copper-mid)]/35 to-[var(--copper-mid)]/40 dark:from-[var(--copper-light)]/20 dark:to-[var(--copper-mid)]/25 rounded-xl flex items-center justify-center shadow-inner flex-shrink-0">
                        <Shirt className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-light)]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm sm:text-base font-semibold text-card-foreground mb-1">
                          {dashboardData.todaysOutfit.outfitName}
                        </h4>
                        <p className="text-xs sm:text-sm text-muted-foreground">
                          Mood: {dashboardData.todaysOutfit.mood}
                        </p>
                        {dashboardData.todaysOutfit.weather && dashboardData.todaysOutfit.weather.condition && (
                          <p className="text-xs sm:text-sm text-muted-foreground">
                            Weather: {dashboardData.todaysOutfit.weather.condition}, {dashboardData.todaysOutfit.weather.temperature}°C
                          </p>
                        )}
                      </div>
                      <div className="text-right flex-shrink-0">
                        {(dashboardData.todaysOutfit as any).isSuggestion && !(dashboardData.todaysOutfit as any).isWorn ? (
                          <Button 
                            onClick={handleMarkAsWorn}
                            disabled={markingAsWorn}
                            className="gradient-copper-gold text-primary-foreground"
                            size="sm"
                          >
                            {markingAsWorn ? (
                              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                            ) : (
                              <CheckCircle className="w-4 h-4 mr-2" />
                            )}
                            {markingAsWorn ? 'Marking...' : 'Wear This'}
                          </Button>
                        ) : (dashboardData.todaysOutfit as any).isWorn ? (
                          <Badge variant="default" className="bg-[var(--copper-light)]/20 text-[var(--copper-dark)] dark:bg-[var(--copper-dark)]/30 dark:text-[var(--copper-light)]">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Worn Today
                          </Badge>
                        ) : (
                          <Button size="sm" className="component-button-outline">
                            <Calendar className="w-4 h-4 mr-2" />
                            View Details
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Outfit Items */}
                  {(dashboardData.todaysOutfit as any).items && (dashboardData.todaysOutfit as any).items.length > 0 && (
                    <div className="space-y-3 sm:space-y-4">
                      <h3 className="text-base sm:text-lg font-display font-semibold text-card-foreground">Outfit items</h3>
                      <div className="space-y-2">
                        {(dashboardData.todaysOutfit as any).items.map((item: any, index: number) => (
                          <div key={index} className="component-card-nested rounded-xl sm:rounded-2xl p-4 sm:p-5">
                            <div className="flex items-center space-x-3">
                              {item.imageUrl ? (
                                <div className="component-image-container w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                                  <img 
                                    src={item.imageUrl} 
                                    alt={item.name || 'Wardrobe item'}
                                    className="w-full h-full object-cover"
                                    onError={(e) => {
                                      const target = e.target as HTMLImageElement;
                                      target.style.display = 'none';
                                      const parent = target.parentElement;
                                      if (parent) {
                                        parent.innerHTML = `
                                          <div class="w-12 h-12 bg-gradient-to-br from-[#E8C8A0]/30 to-[#C9956F]/30 dark:from-[#B8860B]/30 dark:to-[#C9956F]/30 rounded-md flex items-center justify-center">
                                            <svg class="w-6 h-6 text-[var(--copper-dark)] dark:text-[var(--copper-light)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                            </svg>
                                          </div>
                                        `;
                                      }
                                    }}
                                  />
                                </div>
                              ) : (
                                <div className="w-12 h-12 bg-gradient-to-br from-[#E8C8A0]/35 to-[#C9956F]/35 dark:from-[#D4A574]/20 dark:to-[#C9956F]/25 rounded-lg flex items-center justify-center flex-shrink-0">
                                  <Shirt className="w-6 h-6 text-[var(--copper-mid)] dark:text-[var(--copper-mid)]" />
                                </div>
                              )}
                              <div className="flex-1 min-w-0">
                                <h4 className="text-sm sm:text-base font-semibold text-card-foreground mb-1">
                                  {item.name || 'Wardrobe Item'}
                                </h4>
                                <p className="text-xs sm:text-sm text-muted-foreground">
                                  {item.type || 'clothing'} {item.color && `• ${item.color}`}
                                </p>
                              </div>
                              {item.brand && (
                                <Badge variant="outline" className="text-xs sm:text-sm flex-shrink-0">
                                  {item.brand}
                                </Badge>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {dashboardData.todaysOutfit.notes && (
                  <div className="component-card-nested rounded-xl sm:rounded-2xl p-4 sm:p-5">
                    <p className="text-xs sm:text-sm text-muted-foreground">
                      <span className="mr-2">💡</span>{dashboardData.todaysOutfit.notes}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-sm sm:text-base text-muted-foreground mb-4">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                </p>
                <div className="w-12 h-12 sm:w-16 sm:h-16 bg-gradient-to-br from-[var(--copper-mid)]/35 to-[var(--copper-mid)]/40 dark:from-[var(--copper-light)]/20 dark:to-[var(--copper-mid)]/25 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-inner">
                  <Sparkles className="h-5 w-5 sm:h-6 sm:w-6 text-[var(--copper-mid)] dark:text-[var(--copper-light)]" />
                </div>
                <p className="text-sm sm:text-base text-muted-foreground mb-2 font-medium">
                  Smart weather-perfect outfits
                </p>
                <p className="text-xs sm:text-sm text-muted-foreground mb-6 max-w-md mx-auto">
                  Use the Smart Weather Outfit Generator above for instant, weather-matched looks.
                </p>
                <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
                  <div className="w-2 h-2 bg-[var(--copper-mid)] rounded-full"></div>
                  <span>Automatic location detection</span>
                  <div className="w-2 h-2 bg-[var(--copper-mid)] rounded-full ml-3"></div>
                  <span>Real weather data</span>
                  <div className="w-2 h-2 bg-[var(--copper-mid)] rounded-full ml-3"></div>
                  <span>Perfect outfit matching</span>
                </div>
              </div>
            )}
          </div>
        </div>
        )}

        {/* Wardrobe Insights - Mobile Optimized */}
        <div className="component-card mb-6 sm:mb-8 lg:mb-12 sm:rounded-3xl">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-border/60 dark:border-border/70">
            <h2 className="text-xl sm:text-2xl font-display font-semibold text-card-foreground mb-1 sm:mb-2">Wardrobe insights</h2>
            <p className="text-sm sm:text-base text-muted-foreground">Your top items will appear here based on:</p>
          </div>
          <div className="p-4 sm:p-6 lg:p-8">
            {topItemsByCategory.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
                {topItemsByCategory.map((item) => (
                  <div key={item.id} className="component-card-nested rounded-xl sm:rounded-2xl overflow-hidden">
                    {/* Item Image */}
                    <div className="relative bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
                      {item.imageUrl && item.imageUrl !== '' && !item.imageUrl.includes('placeholder') ? (
                        <img 
                          src={item.imageUrl} 
                          alt={item.name}
                          className="w-full h-32 sm:h-full sm:aspect-square object-cover"
                          onError={(e) => {
                            // Hide broken images and show fallback icon
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const parent = target.parentElement;
                            if (parent && !parent.querySelector('.fallback-icon')) {
                              const fallbackDiv = document.createElement('div');
                              fallbackDiv.className = 'fallback-icon w-full h-full flex items-center justify-center';
                              fallbackDiv.innerHTML = '<svg class="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>';
                              parent.appendChild(fallbackDiv);
                            }
                          }}
                        />
                      ) : (
                        <div className="w-full h-32 sm:h-full sm:aspect-square flex items-center justify-center bg-gradient-to-br from-[var(--copper-light)]/20 to-[var(--copper-mid)]/20">
                          <Sparkles className="h-8 w-8 sm:h-12 sm:w-12 text-[var(--copper-mid)]/70" />
                        </div>
                      )}
                      <div className="absolute top-3 left-3">
                        <Badge variant="secondary" className="text-xs uppercase tracking-wide">
                          {CATEGORY_LABELS[item.category]}
                        </Badge>
                      </div>
                    </div>
                    
                    {/* Item Details - Mobile Optimized */}
                    <div className="p-3 sm:p-4">
                      <h4 className="font-semibold text-sm sm:text-base text-gray-900 dark:text-white mb-0.5 sm:mb-1 truncate">
                        {item.name}
                      </h4>
                      <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400 capitalize mb-2 sm:mb-3">
                        {item.type}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-xs sm:text-sm text-[var(--copper-dark)] dark:text-[var(--copper-light)]">
                          <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4" />
                          <span className="font-medium">{item.wearCount}</span>
                        </div>
                        
                        <div className="flex items-center gap-0.5 sm:gap-1">
                          <span className="text-xs sm:text-sm font-semibold text-gray-900 dark:text-white">
                            {item.rating}
                          </span>
                          <Star className={`h-3 w-3 sm:h-4 sm:w-4 ${item.rating >= 4 ? 'text-[var(--copper-dark)] fill-[var(--copper-dark)]' : 'text-gray-300'}`} />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="component-card-nested text-center py-8 sm:py-12 border-2 border-dashed rounded-xl sm:rounded-2xl">
                <Sparkles className="w-12 h-12 sm:w-16 sm:h-16 text-[var(--copper-mid)]/70 dark:text-[var(--copper-mid)]/70 mx-auto mb-3 sm:mb-4" />
                <p className="text-base sm:text-lg font-semibold text-card-foreground mb-1 sm:mb-2">No top items yet</p>
                <p className="text-sm sm:text-base text-muted-foreground mb-4 px-4">
                  Wear pieces from your closet to see your top performers here.
                </p>
                <div className="component-card-nested mt-4 p-4 max-w-md mx-auto">
                  <p className="text-sm sm:text-base text-card-foreground">
                    <span className="mr-2">💡</span>Add a few favorites and generate looks to unlock insights.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Style Goals - Mobile Optimized */}
        <div className="component-card mb-6 sm:mb-8 lg:mb-12 sm:rounded-3xl">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-border/60 dark:border-border/70">
            <h2 className="text-xl sm:text-2xl font-display font-semibold text-card-foreground mb-1 sm:mb-2">Style goals</h2>
            <p className="text-sm sm:text-base text-muted-foreground">Personalized targets based on your look history</p>
          </div>
          <div className="p-4 sm:p-6 lg:p-8">
            <div className="space-y-4 sm:space-y-6">
              {/* Overall Progress */}
              <div className="component-card-nested text-center p-4 sm:p-6 rounded-xl sm:rounded-2xl">
                <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-[#D4A574] to-[#C9956F] bg-clip-text text-transparent mb-2">
                  {dashboardData?.overallProgress || 0}%
                </div>
                <p className="text-sm sm:text-base font-medium text-muted-foreground mb-3 sm:mb-4">Overall progress</p>
                <Progress value={dashboardData?.overallProgress || 0} className="w-full max-w-md mx-auto h-2 sm:h-3" />
              </div>

              {/* Style Collections */}
              <div className="space-y-3 sm:space-y-4">
                <h3 className="text-base sm:text-lg font-display font-semibold text-card-foreground">Style collections</h3>
                {dashboardData?.styleCollections.map((collection, index) => (
                  <div key={index} className="component-card-nested rounded-xl sm:rounded-2xl p-4 sm:p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm sm:text-base font-semibold text-card-foreground">{collection.name}</h4>
                      <Badge variant="secondary" className="text-xs sm:text-sm font-bold uppercase tracking-wide">
                        {collection.progress}/{collection.target}
                      </Badge>
                    </div>
                    <Progress 
                      value={(collection.progress / collection.target) * 100} 
                      className="mb-2 sm:mb-3 h-2 sm:h-2.5" 
                    />
                    <p className="text-xs sm:text-sm text-muted-foreground">{collection.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Wardrobe Insights Hub - Unified component with Style Expansion, Gap Analysis, and Shopping */}
        <WardrobeInsightsHub
          styleExpansions={dashboardData?.styleExpansions || []}
          gaps={dashboardData?.wardrobeGaps || []}
          shoppingRecommendations={dashboardData?.shoppingRecommendations}
          onRefresh={fetchDashboardData}
          className="mb-12"
        />

        {/* Forgotten Gems - Mobile Optimized */}
        <div className="component-card mb-6 sm:mb-8 lg:mb-12 sm:rounded-3xl">
          <div className="p-4 sm:p-6 lg:p-8">
            <ForgottenGems />
          </div>
        </div>

        {/* Batch Upload Modal */}
        {showBatchUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="glass-modal rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-serif text-gray-900 dark:text-white">Add Items with AI</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowBatchUpload(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
              <div className="p-6">
                <BatchImageUpload 
                  userId={user?.uid || ''}
                  onUploadComplete={() => {
                    setShowBatchUpload(false);
                    // Refresh dashboard data to show new items
                    fetchDashboardData();
                  }}
                />
              </div>
            </div>
          </div>
        )}

      </main>
      
      {/* Client-Only Navigation - No Props to Avoid Serialization */}
      <ClientOnlyNav />
    </div>
  );
}
