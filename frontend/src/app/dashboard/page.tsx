"use client";

import { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, TrendingUp, Star, Calendar, Palette, Shirt, Camera, Sparkles, Upload, Users, Zap } from "lucide-react";
import Link from "next/link";
import { useFirebase } from "@/lib/firebase-context";
import dynamic from 'next/dynamic';

// Dynamically import components to avoid SSR issues
const WardrobeGrid = dynamic(() => import('@/components/WardrobeGrid'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading wardrobe...</div>
});

const UploadForm = dynamic(() => import('@/components/UploadForm'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading upload form...</div>
});

const BatchImageUpload = dynamic(() => import('@/components/BatchImageUpload'), {
  ssr: false,
  loading: () => <div className="animate-pulse space-y-4">Loading batch upload...</div>
});

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview");
  const [isLoading, setIsLoading] = useState(true);
  const [showUploadForm, setShowUploadForm] = useState(false);
  const [showBatchUpload, setShowBatchUpload] = useState(false);
  const { user, loading } = useFirebase();

  // Mock data for demonstration - replace with real data from your backend
  const [wardrobeItems, setWardrobeItems] = useState([
    {
      id: '1',
      name: 'Blue Denim Jacket',
      type: 'jacket',
      color: 'blue',
      imageUrl: '/placeholder.jpg',
      wearCount: 5,
      favorite: true
    },
    {
      id: '2', 
      name: 'White T-Shirt',
      type: 'shirt',
      color: 'white',
      imageUrl: '/placeholder.jpg',
      wearCount: 12,
      favorite: false
    }
  ]);
  const [recentOutfits, setRecentOutfits] = useState([
    {
      id: '1',
      name: 'Casual Weekend',
      occasion: 'casual',
      description: 'Perfect for a relaxed weekend outing'
    },
    {
      id: '2',
      name: 'Office Professional',
      occasion: 'business',
      description: 'Smart and professional for the workplace'
    }
  ]);

  useEffect(() => {
    // Add a small delay to ensure everything is loaded
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  // Debug information
  console.log("Dashboard render:", { user, loading, isLoading });

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
              Auth state: {loading ? "Loading..." : "Loaded"} | User: {user ? "Signed in" : "Not signed in"}
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

  // Main dashboard - user is authenticated and loaded
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-emerald-100 to-blue-100 dark:from-emerald-900/20 dark:to-blue-900/20 border-b border-emerald-200 dark:border-emerald-700 px-4 py-3 text-center">
        <p className="text-emerald-800 dark:text-emerald-200 font-medium">
          Welcome back, {user.email}! Your AI stylist is ready to help.
        </p>
      </div>
      
      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Quick Actions Bar */}
        <div className="flex flex-wrap gap-4 mb-8">
          <Button 
            onClick={() => setShowUploadForm(!showUploadForm)}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
          >
            <Upload className="w-4 h-4 mr-2" />
            Add Single Item
          </Button>
          
          <Button 
            onClick={() => setShowBatchUpload(!showBatchUpload)}
            variant="outline"
            className="border-emerald-300 text-emerald-700 hover:bg-emerald-50"
          >
            <Camera className="w-4 h-4 mr-2" />
            Batch Upload
          </Button>
          
          <Link href="/onboarding">
            <Button variant="outline">
              <Sparkles className="w-4 h-4 mr-2" />
              Style Quiz
            </Button>
          </Link>
          
          <Button variant="outline">
            <Zap className="w-4 h-4 mr-2" />
            Generate Outfit
          </Button>
        </div>

        {/* Upload Forms */}
        {showUploadForm && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Add New Item</CardTitle>
              <CardDescription>Upload a single clothing item to your wardrobe</CardDescription>
            </CardHeader>
            <CardContent>
              <UploadForm />
            </CardContent>
          </Card>
        )}

        {showBatchUpload && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Batch Upload</CardTitle>
              <CardDescription>Upload multiple clothing items at once</CardDescription>
            </CardHeader>
            <CardContent>
              <BatchImageUpload 
                onUploadComplete={(items) => {
                  console.log('Batch upload complete:', items);
                  setWardrobeItems(prev => [...prev, ...items]);
                  setShowBatchUpload(false);
                }}
                onError={(message) => {
                  console.error('Batch upload error:', message);
                  // You can add toast notification here
                }}
                userId={user.uid}
              />
            </CardContent>
          </Card>
        )}

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 p-1 rounded-lg mb-8">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === "overview"
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("wardrobe")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === "wardrobe"
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            }`}
          >
            Wardrobe
          </button>
          <button
            onClick={() => setActiveTab("outfits")}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === "outfits"
                ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            }`}
          >
            Outfits
          </button>
        </div>

        {/* Tab Content */}
        {activeTab === "overview" && (
          <div className="space-y-8">
            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                  <Shirt className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{wardrobeItems.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {wardrobeItems.length === 0 ? "Start building your wardrobe!" : "Items in your collection"}
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Outfits Created</CardTitle>
                  <Star className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{recentOutfits.length}</div>
                  <p className="text-xs text-muted-foreground">
                    {recentOutfits.length === 0 ? "Create your first outfit!" : "AI-generated combinations"}
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Style Score</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">8.7</div>
                  <p className="text-xs text-muted-foreground">
                    +0.3 from last week
                  </p>
                </CardContent>
              </Card>

              <Card className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Streak</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">5</div>
                  <p className="text-xs text-muted-foreground">
                    Days using ClosetGPT
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Getting Started */}
            {wardrobeItems.length === 0 && (
              <Card className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-700">
                <CardHeader>
                  <CardTitle className="text-blue-900 dark:text-blue-100">Getting Started</CardTitle>
                  <CardDescription className="text-blue-700 dark:text-blue-300">
                    Welcome to ClosetGPT! Here's how to get started:
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                      <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Camera className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                      </div>
                      <h3 className="font-semibold text-blue-900 dark:text-blue-100 mb-2">1. Upload Items</h3>
                      <p className="text-sm text-blue-700 dark:text-blue-300">Take photos of your clothes and add them to your wardrobe</p>
                    </div>
                    
                    <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                      <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Sparkles className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                      </div>
                      <h3 className="font-semibold text-purple-900 dark:text-purple-100 mb-2">2. Take Style Quiz</h3>
                      <p className="text-sm text-purple-700 dark:text-purple-300">Help us understand your style preferences</p>
                    </div>
                    
                    <div className="text-center p-4 bg-white/50 dark:bg-gray-800/50 rounded-lg">
                      <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-3">
                        <Palette className="w-6 h-6 text-green-600 dark:text-green-400" />
                      </div>
                      <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">3. Get Outfits</h3>
                      <p className="text-sm text-green-700 dark:text-green-300">AI generates perfect outfits for any occasion</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recent Activity */}
            {wardrobeItems.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                  <CardDescription>Your latest wardrobe updates and outfit choices</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Added new blue sweater to wardrobe
                      </span>
                      <span className="text-xs text-gray-400">2h ago</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Created "Weekend Casual" outfit
                      </span>
                      <span className="text-xs text-gray-400">1d ago</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        Wore favorite jeans outfit
                      </span>
                      <span className="text-xs text-gray-400">2d ago</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}

        {activeTab === "wardrobe" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Wardrobe</h2>
              <div className="flex gap-2">
                <Button 
                  onClick={() => setShowUploadForm(true)}
                  size="sm"
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Item
                </Button>
              </div>
            </div>
            
            {wardrobeItems.length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <Shirt className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Your wardrobe is empty</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Start building your wardrobe by uploading photos of your clothes
                  </p>
                  <Button 
                    onClick={() => setShowUploadForm(true)}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <Upload className="w-4 h-4 mr-2" />
                    Upload First Item
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <WardrobeGrid 
                items={wardrobeItems}
                loading={false}
                onItemClick={(item) => console.log('Item clicked:', item)}
                onGenerateOutfit={(item) => console.log('Generate outfit for:', item)}
                showActions={true}
              />
            )}
          </div>
        )}

        {activeTab === "outfits" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Your Outfits</h2>
              <Button 
                onClick={() => console.log('Generate new outfit')}
                className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Outfit
              </Button>
            </div>
            
            {recentOutfits.length === 0 ? (
              <Card className="text-center py-12">
                <CardContent>
                  <Palette className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No outfits yet</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Generate your first outfit by selecting items from your wardrobe
                  </p>
                  <Button 
                    onClick={() => console.log('Generate outfit')}
                    className="bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700"
                  >
                    <Sparkles className="w-4 h-4 mr-2" />
                    Create First Outfit
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recentOutfits.map((outfit, index) => (
                  <Card key={index} className="hover:shadow-lg transition-all duration-300 hover:-translate-y-1">
                    <CardHeader>
                      <CardTitle className="text-lg">{outfit.name}</CardTitle>
                      <CardDescription>{outfit.occasion}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                        {outfit.description}
                      </p>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm">View Details</Button>
                        <Button variant="outline" size="sm">Wear This</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
