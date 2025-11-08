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
  const [showOutfitGenerator, setShowOutfitGenerator] = useState(false);
  const { user, loading } = useAuthContext();
  
  // Weather hook for automatic location detection
  const { weather, fetchWeatherByLocation } = useAutoWeather();
  
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
      <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
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
      <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
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
      <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
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
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
      <Navigation />
      
      {/* Main Content - Mobile Optimized - Bottom padding for nav */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8 lg:py-12 pb-24">
        
        {/* Welcome Section - "Silent Luxury" Design */}
        <div className="mb-6 sm:mb-8">
          <div className="card-surface backdrop-blur-xl rounded-2xl sm:rounded-3xl p-6 sm:p-8 shadow-lg border border-gray-200/50 dark:border-[#3D2F24]/50">
            <h1 className="heading-xl bg-gradient-to-r from-[#FFB84C] to-[#FF9400] bg-clip-text text-transparent mb-2 sm:mb-3">
              Welcome back
            </h1>
            <p className="text-body-lg text-gray-600 dark:text-[#C4BCB4]">
              Ready to explore your wardrobe and create amazing outfits.
            </p>
          </div>
        </div>

        {/* Quick Actions - Better mobile buttons */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6 sm:mb-8">
          <Button 
            onClick={() => setShowBatchUpload(true)}
            className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white px-6 py-3 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-[1.02]"
          >
            <Upload className="w-5 h-5 mr-2" />
            Add Items with AI
          </Button>
        </div>

        {/* Modern Stats Cards - Mobile First Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 lg:gap-6 mb-6 sm:mb-8">
          {/* Total Items Card */}
          <div className="card-surface backdrop-blur-xl rounded-2xl p-4 sm:p-6 shadow-lg border border-gray-200/50 dark:border-[#3D2F24]/50 hover:shadow-xl transition-all duration-200 hover:scale-[1.02]">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900/30 dark:to-orange-900/30 rounded-xl flex items-center justify-center">
                <Shirt className="h-5 w-5 sm:h-6 sm:w-6 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Items</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent">
                  {dashboardData?.totalItems || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Favorites Card */}
          <div className="card-surface backdrop-blur-xl rounded-2xl p-4 sm:p-6 shadow-lg border border-gray-200/50 dark:border-[#3D2F24]/50 hover:shadow-xl transition-all duration-200 hover:scale-[1.02]">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-orange-100 to-red-100 dark:from-orange-900/30 dark:to-red-900/30 rounded-xl flex items-center justify-center">
                <Heart className="h-5 w-5 sm:h-6 sm:w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Favorites</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
                  {dashboardData?.favorites || 0}
                </p>
              </div>
            </div>
          </div>

          {/* Style Goals Card */}
          <div className="card-surface backdrop-blur-xl rounded-2xl p-4 sm:p-6 shadow-lg border border-gray-200/50 dark:border-[#3D2F24]/50 hover:shadow-xl transition-all duration-200 hover:scale-[1.02]">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-900/30 dark:to-yellow-900/30 rounded-xl flex items-center justify-center">
                <Target className="h-5 w-5 sm:h-6 sm:w-6 text-amber-600 dark:text-amber-400" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Goals</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-amber-600 to-yellow-600 bg-clip-text text-transparent">
                  {clampedStyleGoalsCompleted}/{totalStyleGoals || 0}
                </p>
              </div>
            </div>
          </div>

          {/* This Week Card */}
          <div className="card-surface backdrop-blur-xl rounded-2xl p-4 sm:p-6 shadow-lg border border-gray-200/50 dark:border-[#3D2F24]/50 hover:shadow-xl transition-all duration-200 hover:scale-[1.02]">
            <div className="flex flex-col space-y-3">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-900/30 dark:to-amber-900/30 rounded-xl flex items-center justify-center">
                <Calendar className="h-5 w-5 sm:h-6 sm:w-6 text-orange-600 dark:text-orange-400" />
              </div>
              <div>
                <p className="text-xs sm:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">This Week</p>
                <p className="text-2xl sm:text-3xl lg:text-4xl font-bold bg-gradient-to-r from-orange-600 to-amber-600 bg-clip-text text-transparent">
                  {dashboardData?.outfitsThisWeek || 0}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Smart Weather Outfit Generator */}
        <div className="mb-12">
          <SmartWeatherOutfitGenerator 
            onOutfitGenerated={(outfit) => {
              console.log('🎯 Smart weather outfit generated:', outfit);
              // Could trigger dashboard refresh or show success message
            }}
          />
        </div>

        {/* Backend Status Message */}
        {dashboardData && dashboardData.totalItems === 0 && (
          <Card className="mb-8 border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-900/20">
            <CardContent className="p-6">
              <div className="flex items-center space-x-3">
                <Info className="h-6 w-6 text-amber-600 dark:text-amber-400" />
                <div>
                  <h3 className="text-lg font-semibold text-amber-800 dark:text-amber-200">
                    Backend Setup in Progress
                  </h3>
                  <p className="text-amber-700 dark:text-amber-300">
                    Your dashboard is working, but the backend data endpoints are still being configured. 
                    This is normal for new deployments. Your wardrobe data will appear here once the backend is fully set up.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Today's Outfit Section - Only show if we have backend suggestion data AND no weather generator outfit */}
        {dashboardData?.todaysOutfit && (dashboardData.todaysOutfit as any)?.suggestionId && (
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Today's Outfit Suggestion</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Daily outfit recommendation from our backend</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.todaysOutfit ? (
              <div className="space-y-4">
                <div className="text-center mb-4">
                  <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">
                    {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                  </p>
                  <Badge variant="secondary" className="mb-3">
                    {dashboardData.todaysOutfit.occasion}
                  </Badge>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center space-x-4 p-4 border rounded-lg bg-gray-50 dark:bg-gray-800">
                    <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900 dark:to-orange-900 rounded-lg flex items-center justify-center">
                      <Shirt className="w-8 h-8 text-amber-600 dark:text-amber-400" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white text-lg">
                        {dashboardData.todaysOutfit.outfitName}
                      </h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Mood: {dashboardData.todaysOutfit.mood}
                      </p>
                      {dashboardData.todaysOutfit.weather && dashboardData.todaysOutfit.weather.condition && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Weather: {dashboardData.todaysOutfit.weather.condition}, {dashboardData.todaysOutfit.weather.temperature}°C
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      {(dashboardData.todaysOutfit as any).isSuggestion && !(dashboardData.todaysOutfit as any).isWorn ? (
                        <Button 
                          onClick={handleMarkAsWorn}
                          disabled={markingAsWorn}
                          className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 text-white"
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
                        <Badge variant="default" className="bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Worn Today
                        </Badge>
                      ) : (
                        <Button variant="outline" size="sm">
                          <Calendar className="w-4 h-4 mr-2" />
                          View Details
                        </Button>
                      )}
                    </div>
                  </div>

                  {/* Outfit Items */}
                  {(dashboardData.todaysOutfit as any).items && (dashboardData.todaysOutfit as any).items.length > 0 && (
                    <div className="space-y-3">
                      <h5 className="font-medium text-gray-900 dark:text-white text-sm">Outfit Items:</h5>
                      <div className="grid gap-2">
                        {(dashboardData.todaysOutfit as any).items.map((item: any, index: number) => (
                          <div key={index} className="flex items-center space-x-3 p-3 glass-inner rounded-lg">
                            {item.imageUrl ? (
                              <div className="w-12 h-12 rounded-md overflow-hidden flex-shrink-0">
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
                                        <div class="w-12 h-12 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900 dark:to-orange-900 rounded-md flex items-center justify-center">
                                          <svg class="w-6 h-6 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                          </svg>
                                        </div>
                                      `;
                                    }
                                  }}
                                />
                              </div>
                            ) : (
                              <div className="w-12 h-12 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900 dark:to-orange-900 rounded-md flex items-center justify-center flex-shrink-0">
                                <Shirt className="w-6 h-6 text-amber-600 dark:text-amber-400" />
                              </div>
                            )}
                            <div className="flex-1">
                              <p className="font-medium text-gray-900 dark:text-white text-sm">
                                {item.name || 'Wardrobe Item'}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {item.type || 'clothing'} {item.color && `• ${item.color}`}
                              </p>
                            </div>
                            {item.brand && (
                              <Badge variant="outline" className="text-xs">
                                {item.brand}
                              </Badge>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {dashboardData.todaysOutfit.notes && (
                  <div className="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
                    <p className="text-amber-800 dark:text-amber-200 text-sm">
                      💡 {dashboardData.todaysOutfit.notes}
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
                  {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
                </p>
                <div className="w-16 h-16 bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-900 dark:to-orange-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-amber-600 dark:text-amber-400" />
                </div>
                <p className="text-gray-500 dark:text-gray-500 mb-2 font-medium">
                  Smart Weather-Perfect Outfits
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-600 mb-6 max-w-md mx-auto">
                  Use the Smart Weather Outfit Generator above to get instant, location-based outfit recommendations that are perfect for today's weather!
                </p>
                <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                  <span>Automatic location detection</span>
                  <div className="w-2 h-2 bg-orange-500 rounded-full ml-3"></div>
                  <span>Real weather data</span>
                  <div className="w-2 h-2 bg-amber-600 rounded-full ml-3"></div>
                  <span>Perfect outfit matching</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
        )}

        {/* Wardrobe Insights - Mobile Optimized */}
        <div className="mb-6 sm:mb-8 lg:mb-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200/50 dark:border-gray-800/50">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-gray-200/50 dark:border-gray-800/50">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">Wardrobe Insights</h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Your top items will appear here based on:</p>
          </div>
          <div className="p-4 sm:p-6 lg:p-8">
            {topItemsByCategory.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3 sm:gap-4">
                {topItemsByCategory.map((item) => (
                  <div key={item.id} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl sm:rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-200 hover:scale-[1.02]">
                    {/* Item Image */}
                    <div className="aspect-square bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 relative">
                      {item.imageUrl && item.imageUrl !== '' && !item.imageUrl.includes('placeholder') ? (
                        <img 
                          src={item.imageUrl} 
                          alt={item.name}
                          className="w-full h-full object-cover"
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
                        <div className="w-full h-full flex items-center justify-center">
                          <Sparkles className="h-8 w-8 sm:h-12 sm:w-12 text-gray-400" />
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
                        <div className="flex items-center gap-1 text-xs sm:text-sm text-amber-600 dark:text-amber-400">
                          <TrendingUp className="h-3 w-3 sm:h-4 sm:w-4" />
                          <span className="font-medium">{item.wearCount}</span>
                        </div>
                        
                        <div className="flex items-center gap-0.5 sm:gap-1">
                          <span className="text-xs sm:text-sm font-semibold text-gray-900 dark:text-white">
                            {item.rating}
                          </span>
                          <Star className={`h-3 w-3 sm:h-4 sm:w-4 ${item.rating >= 4 ? 'text-yellow-500 fill-yellow-500' : 'text-gray-300'}`} />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 sm:py-12 border-2 border-dashed border-gray-300 dark:border-gray-700 rounded-xl sm:rounded-2xl">
                <Sparkles className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 dark:text-gray-600 mx-auto mb-3 sm:mb-4" />
                <p className="text-base sm:text-lg font-semibold text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">No top items yet</p>
                <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400 mb-4 px-4">
                  Wear your wardrobe items to see your top performers here
                </p>
                <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl max-w-md mx-auto">
                  <p className="text-amber-800 dark:text-amber-200 text-sm sm:text-base">
                    💡 Add items to your wardrobe and use them in outfits!
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Style Goals - Mobile Optimized */}
        <div className="mb-6 sm:mb-8 lg:mb-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200/50 dark:border-gray-800/50">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-gray-200/50 dark:border-gray-800/50">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">Style Goals</h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Personalized goals based on your style</p>
          </div>
          <div className="p-4 sm:p-6 lg:p-8">
            <div className="space-y-4 sm:space-y-6">
              {/* Overall Progress */}
              <div className="text-center p-4 sm:p-6 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 rounded-xl sm:rounded-2xl">
                <div className="text-3xl sm:text-4xl font-bold bg-gradient-to-r from-amber-600 to-orange-600 bg-clip-text text-transparent mb-2">
                  {dashboardData?.overallProgress || 0}%
                </div>
                <p className="text-sm sm:text-base font-medium text-gray-700 dark:text-gray-300 mb-3 sm:mb-4">Overall Progress</p>
                <Progress value={dashboardData?.overallProgress || 0} className="w-full max-w-md mx-auto h-2 sm:h-3" />
              </div>

              {/* Style Collections */}
              <div className="space-y-3 sm:space-y-4">
                <h3 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white">Style Collections</h3>
                {dashboardData?.styleCollections.map((collection, index) => (
                  <div key={index} className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl sm:rounded-2xl p-4 sm:p-5 hover:shadow-lg transition-shadow duration-200">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm sm:text-base font-semibold text-gray-900 dark:text-white">{collection.name}</h4>
                      <Badge variant="secondary" className="text-xs sm:text-sm font-bold">
                        {collection.progress}/{collection.target}
                      </Badge>
                    </div>
                    <Progress 
                      value={(collection.progress / collection.target) * 100} 
                      className="mb-2 sm:mb-3 h-2 sm:h-2.5" 
                    />
                    <p className="text-xs sm:text-sm text-gray-600 dark:text-gray-400">{collection.status}</p>
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
        <div className="mb-6 sm:mb-8 lg:mb-12 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl rounded-2xl sm:rounded-3xl shadow-lg border border-gray-200/50 dark:border-gray-800/50">
          <div className="p-4 sm:p-6 lg:p-8 border-b border-gray-200/50 dark:border-gray-800/50">
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white mb-1 sm:mb-2">Forgotten Gems</h2>
            <p className="text-sm sm:text-base text-gray-600 dark:text-gray-400">Rediscover items you haven't worn in a while</p>
          </div>
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
