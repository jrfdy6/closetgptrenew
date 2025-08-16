"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Plus, 
  TrendingUp, 
  Star, 
  Calendar, 
  Palette, 
  Shirt, 
  Camera, 
  Sparkles, 
  Upload, 
  Users, 
  Zap,
  Heart,
  Target,
  CheckCircle,
  ArrowRight,
  AlertCircle,
  Info,
  RefreshCw
} from "lucide-react";
import Link from "next/link";
import { useFirebase } from "@/lib/firebase-context";
import dynamic from 'next/dynamic';
import { dashboardService, DashboardData } from "@/lib/services/dashboardService";

// Dynamically import components to avoid SSR issues
const WardrobeStats = dynamic(() => import('@/components/WardrobeStats'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading stats...</div>
});

const ForgottenGems = dynamic(() => import('@/components/ForgottenGems'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading forgotten gems...</div>
});

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const { user, loading } = useFirebase();

  // Fetch real dashboard data
  useEffect(() => {
    if (user && !loading) {
      fetchDashboardData();
    }
  }, [user, loading]);

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
      
      setDashboardData(data);
    } catch (err) {
      console.error('🔍 DEBUG: Dashboard: Error fetching data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetry = () => {
    if (user) {
      fetchDashboardData();
    }
  };

  // Debug information
  console.log("Dashboard render:", { user, loading, isLoading, dashboardData, error });
  console.log("🔍 DEBUG: Dashboard data details:", {
    totalItems: dashboardData?.totalItems,
    hasData: !!dashboardData,
    dataKeys: dashboardData ? Object.keys(dashboardData) : [],
    fullData: dashboardData
  });

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
            <Button onClick={handleRetry} className="mr-4">
              <RefreshCw className="w-4 h-4 mr-2" />
              Retry
            </Button>
            <Link href="/profile">
              <Button variant="outline">Go to Profile</Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Main dashboard - user is authenticated and data is loaded
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back!
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Ready to explore your wardrobe and create amazing outfits.
          </p>
        </div>

        {/* Quick Actions */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Button 
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Item
          </Button>
          
          <Link href="/outfits">
            <Button variant="outline">
              <Palette className="w-4 h-4 mr-2" />
              View All Outfits
            </Button>
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Items</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {dashboardData?.totalItems || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">In your wardrobe</p>
                </div>
                <Shirt className="h-8 w-8 text-blue-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Favorites</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {dashboardData?.favorites || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Loved items</p>
                </div>
                <Heart className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Style Goals</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {dashboardData?.styleGoalsCompleted || 0}/{dashboardData?.totalStyleGoals || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Completed</p>
                </div>
                <Target className="h-8 w-8 text-green-600" />
              </div>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-all duration-300">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">This Week</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {dashboardData?.outfitsThisWeek || 0}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Outfits worn</p>
                </div>
                <Calendar className="h-8 w-8 text-purple-600" />
              </div>
            </CardContent>
          </Card>
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
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Today's Outfit</CardTitle>
            <CardDescription>Perfect for your day ahead</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
                {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' })}
              </p>
              <p className="text-gray-500 dark:text-gray-500 mb-6">
                No outfit generated yet
              </p>
              <Button className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700">
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Outfit
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Wardrobe Insights */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">📊 Wardrobe Insights</CardTitle>
            <CardDescription>Your top items will appear here based on:</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.topItems && dashboardData.topItems.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.topItems.map((item, index) => (
                  <div key={item.id} className="flex items-center space-x-4 p-3 border rounded-lg">
                    <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                      <Shirt className="w-6 h-6 text-gray-600" />
                    </div>
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
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Style Goals</CardTitle>
            <CardDescription>Personalized goals based on your style preferences • Enhanced with feedback insights</CardDescription>
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
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Style Expansion</CardTitle>
            <CardDescription>Your clothing items will allow you to explore the following areas as well</CardDescription>
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

        {/* Seasonal Balance */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Seasonal Balance</CardTitle>
            <CardDescription>Maintain balanced wardrobe across all seasons</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {dashboardData?.seasonalBalance.score || 0}%
                </span>
                <Badge variant={dashboardData?.seasonalBalance.score && dashboardData.seasonalBalance.score < 80 ? "destructive" : "secondary"}>
                  {dashboardData?.seasonalBalance.status || "Unknown"}
                </Badge>
              </div>
              <Progress value={dashboardData?.seasonalBalance.score || 0} className="w-full" />
              <div className="text-sm text-gray-600 dark:text-gray-400">
                <p className="mb-2">Consider adding items for: Winter ({dashboardData?.seasonalBalance.winterItems || 0} items, {dashboardData?.seasonalBalance.winterPercentage || 0}%)</p>
                <p>Focus on: {dashboardData?.seasonalBalance.recommendations?.join(", ") || "seasonal items"}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Color Variety */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Color Variety</CardTitle>
            <CardDescription>Build a diverse color palette</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-semibold text-gray-900 dark:text-white">
                  {dashboardData?.colorVariety.current || 0}/{dashboardData?.colorVariety.target || 0}
                </span>
                <Badge variant="secondary">Progress</Badge>
              </div>
              <Progress 
                value={(dashboardData?.colorVariety.current || 0) / (dashboardData?.colorVariety.target || 1) * 100} 
                className="w-full" 
              />
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {dashboardData?.colorVariety.status || "Building color variety..."}
              </p>
              {dashboardData?.colorVariety.colors && dashboardData.colorVariety.colors.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {dashboardData.colorVariety.colors.map((color, index) => (
                    <Badge key={index} variant="outline" className="capitalize">
                      {color}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Wardrobe Gap Analysis */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Wardrobe Gap Analysis</CardTitle>
            <CardDescription>Identify areas where your wardrobe could be improved</CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData?.wardrobeGaps && dashboardData.wardrobeGaps.length > 0 ? (
              <div className="space-y-4">
                {dashboardData.wardrobeGaps.map((gap, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{gap.category}</h4>
                      <Badge variant={gap.priority === 'high' ? 'destructive' : gap.priority === 'medium' ? 'secondary' : 'outline'}>
                        {gap.priority} priority
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{gap.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {gap.suggestedItems.map((item, itemIndex) => (
                        <Badge key={itemIndex} variant="outline">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-500 mb-4">No wardrobe gaps found!</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Your wardrobe is well-balanced. Great job!
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Forgotten Gems */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-xl">Forgotten Gems</CardTitle>
            <CardDescription>Rediscover items you haven't worn in a while</CardDescription>
          </CardHeader>
          <CardContent>
            <ForgottenGems />
          </CardContent>
        </Card>

        {/* Upload Form */}
        {showUploadForm && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Add New Item</CardTitle>
              <CardDescription>Upload a single clothing item to your wardrobe</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Upload className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-500 mb-4">Upload form component will go here</p>
                <Button onClick={() => setShowUploadForm(false)} variant="outline">
                  Close
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
