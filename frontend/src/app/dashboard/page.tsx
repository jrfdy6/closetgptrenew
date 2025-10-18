"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
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
import { dashboardService, DashboardData } from "@/lib/services/dashboardService";
import EnhancedWardrobeGapAnalysis from '@/components/ui/enhanced-wardrobe-gap-analysis';
import SmartWeatherOutfitGenerator from "@/components/SmartWeatherOutfitGenerator";
import { useAutoWeather } from '@/hooks/useWeather';

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


export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [markingAsWorn, setMarkingAsWorn] = useState(false);
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  const { user, loading } = useAuthContext();
  
  // Weather hook for automatic location detection
  const { weather, fetchWeatherByLocation } = useAutoWeather();
  
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
      // Call fetchDashboardData with force fresh to bypass cache
      if (user) {
        fetchDashboardDataFresh();
      }
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
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

  // Main dashboard - user is authenticated and data is loaded
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-purple-900/20 dark:to-indigo-900/20 relative overflow-hidden">
      {/* Enhanced Background Elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-10 w-40 h-40 bg-purple-400/30 rounded-full blur-3xl"></div>
        <div className="absolute top-40 right-20 w-32 h-32 bg-blue-400/25 rounded-full blur-2xl"></div>
        <div className="absolute bottom-32 left-1/4 w-28 h-28 bg-emerald-400/20 rounded-full blur-2xl"></div>
        <div className="absolute bottom-20 right-1/3 w-36 h-36 bg-orange-400/25 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 w-60 h-60 bg-violet-400/15 rounded-full blur-3xl transform -translate-x-1/2 -translate-y-1/2"></div>
        <div className="absolute top-1/3 right-1/4 w-24 h-24 bg-rose-400/20 rounded-full blur-2xl"></div>
      </div>
      
      <Navigation />
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        
        {/* Welcome Section */}
        <div className="mb-12 relative z-10">
          <div className="glass-card-hover glass-shadow-strong p-8 animate-fade-in">
            <h1 className="text-5xl font-serif font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-indigo-600 bg-clip-text text-transparent mb-4">
              Welcome back
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 font-light">
              Ready to explore your wardrobe and create amazing outfits.
            </p>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-6 mb-12">
          <Button 
            onClick={() => setShowBatchUpload(true)}
            className="glass-button-primary px-8 py-3 rounded-full font-medium glass-transition hover:scale-105"
          >
            <Upload className="w-5 h-5 mr-3" />
            Add Items with AI
          </Button>
          
          {/* Clean, simple analytics - no complex initialization needed */}
        </div>

        {/* Enhanced Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12 relative z-10">
          <Card className="glass-card-hover glass-shadow-strong border-0 animate-fade-in stagger-1">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Total Items</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-1">
                    {dashboardData?.totalItems || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 font-light">In your wardrobe</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-r from-blue-500/20 to-indigo-500/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Shirt className="h-7 w-7 text-blue-600 dark:text-blue-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card-hover glass-shadow-strong border-0 animate-fade-in stagger-2">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Favorites</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-pink-600 to-rose-600 bg-clip-text text-transparent mb-1">
                    {dashboardData?.favorites || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 font-light">Loved items</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-r from-pink-500/20 to-rose-500/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Heart className="h-7 w-7 text-pink-600 dark:text-pink-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card-hover glass-shadow-strong border-0 animate-fade-in stagger-3">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">Style Goals</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent mb-1">
                    {dashboardData?.styleGoalsCompleted || 0}/{dashboardData?.totalStyleGoals || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 font-light">Completed</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Target className="h-7 w-7 text-emerald-600 dark:text-emerald-400" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card-hover glass-shadow-strong border-0 animate-fade-in stagger-4">
            <CardContent className="p-8">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">This Week</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-violet-600 bg-clip-text text-transparent mb-1">
                    {dashboardData?.outfitsThisWeek || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500 font-light">Outfits worn</p>
                </div>
                <div className="w-14 h-14 bg-gradient-to-r from-purple-500/20 to-violet-500/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                  <Calendar className="h-7 w-7 text-purple-600 dark:text-purple-400" />
                </div>
              </div>
            </CardContent>
          </Card>
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

        {/* Today's Outfit Section */}
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Today's Weather-Perfect Outfit</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Your smart outfit generator above creates perfect weather-based recommendations</CardDescription>
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
                    <div className="w-16 h-16 bg-gradient-to-br from-emerald-100 to-blue-100 dark:from-emerald-900 dark:to-blue-900 rounded-lg flex items-center justify-center">
                      <Shirt className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
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
                          className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white"
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
                        <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
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
                                        <div class="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 rounded-md flex items-center justify-center">
                                          <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                          </svg>
                                        </div>
                                      `;
                                    }
                                  }}
                                />
                              </div>
                            ) : (
                              <div className="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900 dark:to-pink-900 rounded-md flex items-center justify-center flex-shrink-0">
                                <Shirt className="w-6 h-6 text-purple-600 dark:text-purple-400" />
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
                  <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-blue-800 dark:text-blue-200 text-sm">
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
                <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <p className="text-gray-500 dark:text-gray-500 mb-2 font-medium">
                  Smart Weather-Perfect Outfits
                </p>
                <p className="text-sm text-gray-400 dark:text-gray-600 mb-6 max-w-md mx-auto">
                  Use the Smart Weather Outfit Generator above to get instant, location-based outfit recommendations that are perfect for today's weather!
                </p>
                <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>Automatic location detection</span>
                  <div className="w-2 h-2 bg-blue-500 rounded-full ml-3"></div>
                  <span>Real weather data</span>
                  <div className="w-2 h-2 bg-purple-500 rounded-full ml-3"></div>
                  <span>Perfect outfit matching</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Wardrobe Insights */}
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Wardrobe Insights</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Your top items will appear here based on:</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.topItems && dashboardData.topItems.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.topItems.map((item, index) => (
                  <div key={item.id} className="flex items-center space-x-4 p-3 border rounded-lg">
                    {item.imageUrl ? (
                      <div className="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0">
                        <img 
                          src={item.imageUrl} 
                          alt={item.name}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            // Fallback to icon if image fails to load
                            const target = e.target as HTMLImageElement;
                            target.style.display = 'none';
                            const parent = target.parentElement;
                            if (parent) {
                              parent.innerHTML = `
                                <div class="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                                  <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                                  </svg>
                                </div>
                              `;
                            }
                          }}
                        />
                      </div>
                    ) : (
                      <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Shirt className="w-6 h-6 text-gray-600" />
                      </div>
                    )}
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900 dark:text-white">{item.name}</h4>
                      <p className="text-sm text-gray-600 dark:text-gray-400">{item.type}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900 dark:text-white">{item.wearCount} wears</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Rating: {item.rating}/5</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-500 mb-4">No top items yet</p>
                <div className="text-left max-w-md mx-auto space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <p>• How often items appear in outfits</p>
                  <p>• Your feedback ratings</p>
                  <p>• How often you view/edit items</p>
                  <p>• Style preference matches</p>
                  <p>• Base item usage</p>
                </div>
                <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <p className="text-blue-800 dark:text-blue-200 text-sm">
                    💡 Tip: Add items to your wardrobe and use them in outfits to start seeing your top items!
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Style Goals */}
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Style Goals</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Personalized goals based on your style preferences • Enhanced with feedback insights</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Overall Progress */}
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {dashboardData?.overallProgress || 0}%
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Overall Progress</p>
                <Progress value={dashboardData?.overallProgress || 0} className="w-full max-w-md mx-auto" />
              </div>

              {/* Style Collections */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Style Collections</h3>
                {dashboardData?.styleCollections.map((collection, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{collection.name}</h4>
                      <Badge variant="secondary">
                        {collection.progress}/{collection.target}
                      </Badge>
                    </div>
                    <Progress 
                      value={(collection.progress / collection.target) * 100} 
                      className="mb-2" 
                    />
                    <p className="text-sm text-gray-600 dark:text-gray-400">{collection.status}</p>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Style Expansion */}
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Style Expansion</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Your clothing items will allow you to explore the following areas as well</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.styleExpansions && dashboardData.styleExpansions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {dashboardData.styleExpansions.map((expansion, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <span className="font-medium text-gray-900 dark:text-white capitalize">
                      {expansion.name}
                    </span>
                    <Badge variant="outline">{expansion.direction}</Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 dark:text-gray-500">No style expansions available yet</p>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                  Add more diverse items to your wardrobe to unlock new style directions
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Wardrobe Gap Analysis with Shopping Recommendations */}
        <EnhancedWardrobeGapAnalysis
          gaps={dashboardData?.wardrobeGaps || []}
          shoppingRecommendations={dashboardData?.shoppingRecommendations}
          onRefresh={fetchDashboardData}
          className="mb-8"
        />

        {/* Forgotten Gems */}
        <Card className="mb-12 border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="text-2xl font-serif text-stone-900 dark:text-stone-100">Forgotten Gems</CardTitle>
            <CardDescription className="text-stone-600 dark:text-stone-400 font-light">Rediscover items you haven't worn in a while</CardDescription>
          </CardHeader>
          <CardContent>
            <ForgottenGems />
          </CardContent>
        </Card>

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
    </div>
  );
}
