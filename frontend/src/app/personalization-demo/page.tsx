'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Brain, 
  TestTube, 
  ArrowLeft,
  RefreshCw, 
  Heart, 
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Info,
  Shield,
  Eye
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { useExistingDataPersonalization } from '@/lib/hooks/useExistingDataPersonalization';
import { PersonalizedOutfit } from '@/lib/services/existingDataPersonalizationService';
import { convertToPydanticShape, validateConvertedData } from '@/lib/outfitDataConverter';
import Navigation from '@/components/Navigation';

export default function PersonalizationDemoPage() {
  const router = useRouter();
  const { user } = useFirebase();
  const {
    personalizationStatus,
    userPreferences,
    isLoading,
    error,
    isReadyForPersonalization,
    hasExistingData,
    totalInteractions,
    topColors,
    topStyles,
    topOccasions,
    favoriteItemsCount,
    mostWornItemsCount,
    generatePersonalizedOutfit,
    refreshPersonalizationData
  } = useExistingDataPersonalization();

  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<PersonalizedOutfit | null>(null);
  const [testMode, setTestMode] = useState(false);
  const [selectedGenerator, setSelectedGenerator] = useState<'simple-minimal' | 'robust'>('simple-minimal');
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [debugAnalysis, setDebugAnalysis] = useState<any>(null);
  const [semanticFlag, setSemanticFlag] = useState(false);
  
  // Form state for testing different combinations
  const [formData, setFormData] = useState({
    occasion: 'Business',
    style: 'Classic',
    mood: 'Bold'
  });

  const handleDebugFiltering = async () => {
    try {
      setGenerating(true);
      
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Get Firebase ID token
      const authToken = await user.getIdToken();
      console.log('🔍 [Debug] Running debug filtering analysis...');

      // First, fetch the user's actual wardrobe items
      const wardrobeResponse = await fetch('/api/wardrobe', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (!wardrobeResponse.ok) {
        throw new Error('Failed to fetch wardrobe items');
      }
      
      const wardrobeData = await wardrobeResponse.json();
      const wardrobeItems = wardrobeData.items || wardrobeData;
      console.log('✅ [Debug] Fetched wardrobe items:', wardrobeItems.length);

      // Call debug endpoint with semantic flag
      const debugResponse = await fetch(`/api/outfits/debug-filter?semantic=${semanticFlag}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          occasion: formData.occasion,
          style: formData.style,
          mood: formData.mood,
          wardrobe: wardrobeItems,
          user_profile: { id: user.uid }
        }),
      });

      if (!debugResponse.ok) {
        throw new Error(`Debug analysis failed: ${debugResponse.statusText}`);
      }

      const debugResult = await debugResponse.json();
      console.log('✅ [Debug] Debug analysis complete:', debugResult);
      
      setDebugAnalysis(debugResult.debug_analysis);
      setShowDebugPanel(true);
      
    } catch (error) {
      console.error('❌ [Debug] Debug analysis failed:', error);
      alert(`Debug analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateOutfit = async () => {
    try {
      setGenerating(true);
      
      if (!user) {
        throw new Error('User not authenticated');
      }

      // Get Firebase ID token
      const authToken = await user.getIdToken();
      console.log('🔍 [Demo] Using real outfit generation with auth token');

      // First, fetch the user's actual wardrobe items
      console.log('🔍 [Demo] Fetching user wardrobe items...');
      const wardrobeResponse = await fetch('/api/wardrobe', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      if (!wardrobeResponse.ok) {
        throw new Error('Failed to fetch wardrobe items');
      }
      
      const wardrobeData = await wardrobeResponse.json();
      const wardrobeItems = wardrobeData.items || wardrobeData;
      console.log('✅ [Demo] Fetched wardrobe items:', wardrobeItems.length);

      // Fetch the user's complete profile data for advanced validation
      console.log('🔍 [Demo] Fetching user profile data...');
      const profileResponse = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${authToken}`,
        },
      });
      
      let userProfile = { id: user.uid };
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        userProfile = profileData;
        console.log('✅ [Demo] Fetched user profile:', {
          bodyType: profileData.bodyType,
          skinTone: profileData.skinTone,
          height: profileData.height,
          weight: profileData.weight,
          gender: profileData.gender,
          stylePreferences: profileData.stylePreferences?.length || 0,
          colorPreferences: profileData.colorPreferences?.length || 0
        });
      } else {
        console.log('⚠️ [Demo] Could not fetch user profile, using minimal profile');
      }

      // Fetch user's outfit history and preferences for advanced personalization
      console.log('🔍 [Demo] Fetching outfit history and preferences...');
      let likedOutfits = [];
      let outfitHistory = [];
      let recentlyWornItems = new Set();
      
      try {
        const outfitsResponse = await fetch('/api/outfit-history', {
          headers: {
            'Authorization': `Bearer ${authToken}`,
          },
        });
        
        if (outfitsResponse.ok) {
          const outfitsData = await outfitsResponse.json();
          console.log('🔍 [Demo] Raw outfit history response:', outfitsData);
          
          // Handle the actual backend response structure
          const outfitHistoryEntries = outfitsData.outfitHistory || [];
          
          // Extract liked outfits and history from outfit history entries
          likedOutfits = outfitHistoryEntries
            .filter(entry => entry.rating >= 4 || entry.favorite)
            .map(entry => entry.outfitId);
          
          outfitHistory = outfitHistoryEntries
            .map(entry => ({
              id: entry.outfitId,
              items: [], // Outfit history entries don't contain item details
              wearCount: 1, // Each entry represents one wear
              rating: entry.rating || 0,
              occasion: entry.occasion,
              style: entry.style || 'Unknown',
              dateWorn: entry.dateWorn
            }));
          
          // Extract recently worn items (last 7 days) for wardrobe rotation
          const sevenDaysAgo = new Date();
          sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
          
          outfitHistoryEntries
            .filter(entry => {
              const dateWorn = entry.dateWorn;
              if (typeof dateWorn === 'number') {
                return new Date(dateWorn) > sevenDaysAgo;
              }
              return false;
            })
            .forEach(entry => {
              // Since outfit history entries don't contain item details,
              // we'll need to get this from a separate call or mark the outfit as recently worn
              if (entry.outfitId) {
                recentlyWornItems.add(entry.outfitId);
              }
            });
          
          console.log('✅ [Demo] Fetched outfit data:', {
            totalOutfitHistory: outfitHistoryEntries.length,
            likedOutfits: likedOutfits.length,
            outfitHistory: outfitHistory.length,
            recentlyWornItems: recentlyWornItems.size
          });
        }
      } catch (error) {
        console.log('⚠️ [Demo] Could not fetch outfit history, continuing without it');
      }

      // Apply wardrobe diversity scoring to promote unworn items
      console.log('🔄 [Demo] Applying wardrobe diversity scoring...');
      const enhancedWardrobeItems = wardrobeItems.map(item => {
        let diversityScore = 0;
        let diversityReason = '';
        
        // Check if item is recently worn
        const isRecentlyWorn = recentlyWornItems.has(item.id);
        const wearCount = item.wearCount || 0;
        const isFavorite = item.isFavorite || item.favorite || false;
        
        if (wearCount === 0) {
          // Never worn - highest priority
          diversityScore = 10;
          diversityReason = 'Never worn - high priority';
        } else if (wearCount <= 2 && !isRecentlyWorn) {
          // Lightly worn and not recent - good priority
          diversityScore = 7;
          diversityReason = 'Lightly worn, not recent';
        } else if (isFavorite && !isRecentlyWorn) {
          // Favorite but not recent - medium priority
          diversityScore = 5;
          diversityReason = 'Favorite item, not recent';
        } else if (isRecentlyWorn) {
          // Recently worn - lower priority
          diversityScore = -3;
          diversityReason = 'Recently worn - lower priority';
        } else {
          // Normal scoring
          diversityScore = 0;
          diversityReason = 'Normal priority';
        }
        
        return {
          ...item,
          diversityScore,
          diversityReason,
          isRecentlyWorn,
          wearCount,
          isFavorite
        };
      });
      
      // Sort wardrobe by diversity score (unworn items first)
      enhancedWardrobeItems.sort((a, b) => {
        // First sort by diversity score (higher is better)
        if (a.diversityScore !== b.diversityScore) {
          return b.diversityScore - a.diversityScore;
        }
        // Then by favorites
        if (a.isFavorite !== b.isFavorite) {
          return b.isFavorite - a.isFavorite;
        }
        // Then by lower wear count
        return a.wearCount - b.wearCount;
      });
      
      console.log('✅ [Demo] Wardrobe diversity analysis:', {
        neverWorn: enhancedWardrobeItems.filter(item => item.wearCount === 0).length,
        lightlyWorn: enhancedWardrobeItems.filter(item => item.wearCount <= 2 && !item.isRecentlyWorn).length,
        favorites: enhancedWardrobeItems.filter(item => item.isFavorite).length,
        recentlyWorn: enhancedWardrobeItems.filter(item => item.isRecentlyWorn).length
      });

      // Prepare request data with enhanced wardrobe diversity for smart rotation
      console.log('🔍 [Demo] Form data being sent:', formData);
      const requestData = {
        occasion: formData.occasion,
        style: formData.style,
        mood: formData.mood,
        weather: {
          temperature: 72,
          condition: 'Clear',
          humidity: 50,
          wind_speed: 5,
          location: 'Demo Location'
        },
        wardrobe: enhancedWardrobeItems, // Enhanced wardrobe with diversity scoring and rotation logic
        user_profile: userProfile, // Complete profile with body type, skin tone, height, weight, gender, preferences
        likedOutfits: likedOutfits, // Previously liked outfits for style matching
        outfit_history: outfitHistory, // Wear history for diversity and preference learning
        recently_worn_items: Array.from(recentlyWornItems), // Items worn in last 7 days for rotation
        wardrobe_diversity_enabled: true, // Flag to enable diversity scoring in backend
        baseItemId: null
      };

      // Convert to Pydantic format
      const convertedData = convertToPydanticShape(requestData);
      
      // Now validate with actual wardrobe items
      if (!validateConvertedData(convertedData)) {
        throw new Error('Data validation failed');
      }
      console.log('✅ [Demo] Data validation passed with', wardrobeItems.length, 'wardrobe items');

      // Use the selected outfit generation service
      console.log(`🔍 [Demo] Using ${selectedGenerator} generator`);
      
      // Use the main hybrid endpoint with robust generation
      console.log('🔄 [Demo] Calling main hybrid outfit generation endpoint');
      
      // Add generation_mode to the request data
      const requestWithMode = {
        ...convertedData,
        generation_mode: selectedGenerator
      };
      
      const response = await fetch('/api/outfits/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`,
        },
        body: JSON.stringify(requestWithMode),
      });
      
      if (!response.ok) {
        throw new Error(`Main hybrid generator failed: ${response.status} ${response.statusText}`);
      }
      
      const outfit = await response.json();
      console.log(`✅ [Demo] ${selectedGenerator} outfit generated via main hybrid endpoint:`, outfit);

      if (outfit) {
        setGeneratedOutfit(outfit);
      }
    } catch (err) {
      console.error('❌ [Demo] Real outfit generation failed:', err);
      // Fallback to existing data personalization for demo purposes
      console.log('🔄 [Demo] Falling back to existing data personalization');
      const outfit = await generatePersonalizedOutfit({
        occasion: formData.occasion,
        style: formData.style,
        mood: formData.mood,
        weather: {
          temperature: 72,
          condition: 'Clear',
          humidity: 50,
          wind_speed: 5,
          location: 'Demo Location'
        }
      }, selectedGenerator);

      if (outfit) {
        setGeneratedOutfit(outfit);
      }
    } finally {
      setGenerating(false);
    }
  };

  const handleRefreshData = async () => {
    await refreshPersonalizationData();
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to view the personalization demo</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      <div className="container mx-auto p-8">
        {/* Header */}
        <div className="flex items-center gap-6 mb-12">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push('/outfits')}
            className="flex items-center gap-3 border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 px-6 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105"
          >
            <ArrowLeft className="h-5 w-5" />
            Back to Outfits
          </Button>
          <div>
            <h1 className="text-4xl font-serif font-bold flex items-center gap-4 text-stone-900 dark:text-stone-100">
              <TestTube className="h-10 w-10 text-blue-500" />
              Personalization Demo
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-lg mt-2">
              Safe testing environment - won't affect your existing app
            </p>
          </div>
        </div>

        {/* Safety Notice */}
        <Card className="mb-8 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Shield className="h-6 w-6 text-green-600 mt-1" />
              <div>
                <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">
                  🛡️ Safe Testing Environment
                </h3>
                <p className="text-green-700 dark:text-green-300 text-sm mb-3">
                  This is a completely separate demo page that won't affect your existing outfit generation.
                  You can test the personalization features safely without any risk to your current app.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="font-medium text-green-800 dark:text-green-200 mb-1">What's Safe:</div>
                    <ul className="space-y-1 text-green-700 dark:text-green-300">
                      <li>• Read-only access to your existing data</li>
                      <li>• No changes to your current outfit generation</li>
                      <li>• Separate demo environment</li>
                      <li>• No impact on your main app</li>
                    </ul>
                  </div>
                  <div>
                    <div className="font-medium text-green-800 dark:text-green-200 mb-1">What You Can Test:</div>
                    <ul className="space-y-1 text-green-700 dark:text-green-300">
                      <li>• Personalization status from your data</li>
                      <li>• User preferences extraction</li>
                      <li>• Personalized outfit generation</li>
                      <li>• System integration</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Personalization Status */}
          <div className="space-y-6">
            {/* Personalization Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-500" />
                  Your Personalization Status
                  {isReadyForPersonalization ? (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  ) : (
                    <AlertCircle className="h-4 w-4 text-yellow-500" />
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Status Overview */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <div className="text-xl font-bold text-blue-600 dark:text-blue-400">
                      {totalInteractions}
                    </div>
                    <div className="text-sm text-blue-600 dark:text-blue-400">Total Interactions</div>
                  </div>
                  
                  <div className="text-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <div className="text-xl font-bold text-green-600 dark:text-green-400">
                      {favoriteItemsCount + mostWornItemsCount}
                    </div>
                    <div className="text-sm text-green-600 dark:text-green-400">Engaged Items</div>
                  </div>
                </div>

                {/* Readiness Status */}
                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="font-medium">Personalization Ready</span>
                  <Badge variant={isReadyForPersonalization ? "default" : "secondary"}>
                    {isReadyForPersonalization ? "Yes" : "Not Yet"}
                  </Badge>
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                  <span className="font-medium">Has Existing Data</span>
                  <Badge variant={hasExistingData ? "default" : "secondary"}>
                    {hasExistingData ? "Yes" : "No"}
                  </Badge>
                </div>

                {/* Top Preferences */}
                {topColors.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-2">Your Top Colors</div>
                    <div className="flex flex-wrap gap-1">
                      {topColors.slice(0, 5).map((color, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {color}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {topStyles.length > 0 && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-2">Your Top Styles</div>
                    <div className="flex flex-wrap gap-1">
                      {topStyles.slice(0, 5).map((style, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {style}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2">
                  <Button 
                    onClick={handleRefreshData}
                    variant="outline" 
                    size="sm"
                    disabled={isLoading}
                    className="flex-1"
                  >
                    <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                    Refresh Data
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Data Sources */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Eye className="h-5 w-5 text-purple-500" />
                  Data Sources Used
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">Wardrobe Favorites</span>
                    <Badge variant="outline">{favoriteItemsCount}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">Most Worn Items</span>
                    <Badge variant="outline">{mostWornItemsCount}</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">Style Profiles</span>
                    <Badge variant="outline">✓</Badge>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded">
                    <span className="text-sm">Item Analytics</span>
                    <Badge variant="outline">✓</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Demo Generation */}
          <div className="space-y-6">
            {/* Demo Generation */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TestTube className="h-5 w-5 text-purple-500" />
                  Demo Outfit Generation
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {error ? (
                  <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <AlertCircle className="h-4 w-4 text-red-500" />
                    <span className="text-red-600">Error: {error}</span>
                  </div>
                ) : !hasExistingData ? (
                  <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                    <Info className="h-4 w-4 text-yellow-500" />
                    <span className="text-yellow-600">No existing data found. Personalization will be limited.</span>
                  </div>
                ) : !isReadyForPersonalization ? (
                  <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <Info className="h-4 w-4 text-blue-500" />
                    <span className="text-blue-600">
                      Learning from your data... ({totalInteractions} interactions)
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-green-600">Ready for personalized recommendations!</span>
                  </div>
                )}

                {/* Form for testing different combinations */}
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Occasion</label>
                      <select
                        value={formData.occasion}
                        onChange={(e) => setFormData(prev => ({ ...prev, occasion: e.target.value }))}
                        className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                      >
                        {/* Backend-accepted occasions only */}
                        <option value="">Select Occasion</option>
                        <option value="Casual">Casual</option>
                        <option value="Business">Business</option>
                        <option value="Formal">Formal</option>
                        <option value="Athletic">Athletic</option>
                        <option value="Party">Party</option>
                        <option value="Date">Date</option>
                        <option value="Interview">Interview</option>
                        <option value="Weekend">Weekend</option>
                        <option value="Loungewear">Loungewear</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Style</label>
                      <select
                        value={formData.style}
                        onChange={(e) => setFormData(prev => ({ ...prev, style: e.target.value }))}
                        className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                      >
                        {/* Backend-accepted styles only */}
                        <option value="">Select Style</option>
                        <option value="Classic">Classic</option>
                        <option value="Modern">Modern</option>
                        <option value="Vintage">Vintage</option>
                        <option value="Bohemian">Bohemian</option>
                        <option value="Minimalist">Minimalist</option>
                        <option value="Grunge">Grunge</option>
                        <option value="Preppy">Preppy</option>
                        <option value="Streetwear">Streetwear</option>
                        <option value="Dark Academia">Dark Academia</option>
                        <option value="Light Academia">Light Academia</option>
                        <option value="Old Money">Old Money</option>
                        <option value="Y2K">Y2K</option>
                        <option value="Avant-Garde">Avant-Garde</option>
                        <option value="Artsy">Artsy</option>
                        <option value="Maximalist">Maximalist</option>
                        <option value="Colorblock">Colorblock</option>
                        <option value="Business Casual">Business Casual</option>
                        <option value="Urban Professional">Urban Professional</option>
                        <option value="Techwear">Techwear</option>
                        <option value="Hipster">Hipster</option>
                        <option value="Scandinavian">Scandinavian</option>
                        <option value="Gothic">Gothic</option>
                        <option value="Punk">Punk</option>
                        <option value="Cyberpunk">Cyberpunk</option>
                        <option value="Edgy">Edgy</option>
                        <option value="Coastal Chic">Coastal Chic</option>
                        <option value="Athleisure">Athleisure</option>
                        <option value="Casual Cool">Casual Cool</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Mood</label>
                      <select
                        value={formData.mood}
                        onChange={(e) => setFormData(prev => ({ ...prev, mood: e.target.value }))}
                        className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                      >
                        {/* Backend-accepted moods only */}
                        <option value="">Select Mood</option>
                        <option value="Confident">Confident</option>
                        <option value="Relaxed">Relaxed</option>
                        <option value="Energetic">Energetic</option>
                        <option value="Professional">Professional</option>
                        <option value="Romantic">Romantic</option>
                        <option value="Playful">Playful</option>
                        <option value="Serene">Serene</option>
                        <option value="Dynamic">Dynamic</option>
                        <option value="Bold">Bold</option>
                        <option value="Subtle">Subtle</option>
                      </select>
                    </div>
                  </div>

                  {/* Generator Selection Toggle */}
                  <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <label className="block text-sm font-medium mb-3">Outfit Generator</label>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="simple-minimal"
                          name="generator"
                          value="simple-minimal"
                          checked={selectedGenerator === 'simple-minimal'}
                          onChange={(e) => setSelectedGenerator(e.target.value as 'simple-minimal' | 'robust')}
                          className="mr-2"
                        />
                        <label htmlFor="simple-minimal" className="text-sm font-medium">
                          Simple-Minimal
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="robust"
                          name="generator"
                          value="robust"
                          checked={selectedGenerator === 'robust'}
                          onChange={(e) => setSelectedGenerator(e.target.value as 'simple-minimal' | 'robust')}
                          className="mr-2"
                        />
                        <label htmlFor="robust" className="text-sm font-medium">
                          Robust Generator
                        </label>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                      {selectedGenerator === 'simple-minimal' 
                        ? '✅ Reliable, handles edge cases gracefully, good for testing'
                        : '🔄 Advanced features, body type optimization, multiple strategies'
                      }
                    </div>
                  </div>

                  {/* Semantic Matching Toggle */}
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <label className="block text-sm font-medium mb-3 text-blue-800 dark:text-blue-200">
                      🧠 Semantic Matching (Experimental)
                    </label>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="semantic-off"
                          name="semantic"
                          value="false"
                          checked={!semanticFlag}
                          onChange={() => setSemanticFlag(false)}
                          className="mr-2"
                        />
                        <label htmlFor="semantic-off" className="text-sm font-medium text-blue-700 dark:text-blue-300">
                          Traditional (Exact Match)
                        </label>
                      </div>
                      <div className="flex items-center">
                        <input
                          type="radio"
                          id="semantic-on"
                          name="semantic"
                          value="true"
                          checked={semanticFlag}
                          onChange={() => setSemanticFlag(true)}
                          className="mr-2"
                        />
                        <label htmlFor="semantic-on" className="text-sm font-medium text-blue-700 dark:text-blue-300">
                          Semantic (Compatible Styles)
                        </label>
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-blue-600 dark:text-blue-400">
                      {!semanticFlag 
                        ? '🔍 Traditional: Exact style/occasion matches only'
                        : '🎯 Semantic: Compatible styles (e.g., Classic ≈ Business Casual)'
                      }
                    </div>
                  </div>

                  <Button 
                    onClick={handleGenerateOutfit}
                    disabled={generating || isLoading}
                    className="w-full"
                  >
                    {generating ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Generating {formData.style} {formData.occasion} Outfit ({selectedGenerator})...
                      </>
                    ) : (
                      <>
                        <TestTube className="h-4 w-4 mr-2" />
                        Generate {formData.style} {formData.occasion} Outfit ({selectedGenerator})
                      </>
                    )}
                  </Button>
                  
                  {/* Debug Button */}
                  <Button 
                    onClick={handleDebugFiltering}
                    disabled={generating}
                    variant="outline"
                    className="w-full mt-2"
                  >
                    {generating ? (
                      <>
                        <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                        Analyzing Filtering...
                      </>
                    ) : (
                      <>
                        <Eye className="h-4 w-4 mr-2" />
                        Debug Item Filtering
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Generated Outfit */}
            {generatedOutfit && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Heart className="h-5 w-5 text-red-500" />
                    Generated Demo Outfit
                    {generatedOutfit.personalization_applied && (
                      <Badge variant="default" className="ml-2">
                        Personalized
                      </Badge>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {/* Outfit Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Style</div>
                        <div className="font-semibold">{generatedOutfit.style}</div>
                      </div>
                      <div>
                        <div className="text-sm font-medium text-muted-foreground">Occasion</div>
                        <div className="font-semibold">{generatedOutfit.occasion}</div>
                      </div>
                    </div>

                    {/* Personalization Info */}
                    {generatedOutfit.personalization_applied && (
                      <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                        <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-2">
                          Personalization Applied
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-muted-foreground">Score:</span>
                            <span className="ml-2 font-medium">
                              {generatedOutfit.personalization_score?.toFixed(2) || 'N/A'}
                            </span>
                          </div>
                          <div>
                            <span className="text-muted-foreground">Interactions:</span>
                            <span className="ml-2 font-medium">{generatedOutfit.user_interactions}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Wardrobe Diversity Info */}
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                      <div className="text-sm font-medium text-green-600 dark:text-green-400 mb-2">
                        Wardrobe Rotation Applied
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Strategy:</span>
                          <span className="ml-2 font-medium">
                            {generatedOutfit.items?.some(item => item.wearCount === 0) 
                              ? 'Never Worn Priority' 
                              : 'Diversity Balanced'
                            }
                          </span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Rotation:</span>
                          <span className="ml-2 font-medium">
                            {generatedOutfit.items?.filter(item => item.diversityScore > 0).length || 0} Enhanced
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Generator Comparison Metrics */}
                    <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <div className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-2">
                        Generator: {selectedGenerator === 'simple-minimal' ? 'Simple-Minimal' : 'Robust'}
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex justify-between">
                          <span>Items Generated:</span>
                          <span className="font-medium">{generatedOutfit.items?.length || 0}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Confidence:</span>
                          <span className="font-medium">{generatedOutfit.confidence_score ? `${Math.round(generatedOutfit.confidence_score * 100)}%` : 'N/A'}</span>
                        </div>
                        {generatedOutfit.metadata && (
                          <>
                            <div className="flex justify-between">
                              <span>Validation Applied:</span>
                              <span className="font-medium">{generatedOutfit.metadata.validation_applied ? '✅' : '❌'}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Requirements Met:</span>
                              <span className="font-medium">{generatedOutfit.metadata.occasion_requirements_met ? '✅' : '❌'}</span>
                            </div>
                            {generatedOutfit.metadata.deduplication_applied && (
                              <div className="flex justify-between">
                                <span>Deduplication:</span>
                                <span className="font-medium">✅</span>
                              </div>
                            )}
                            {generatedOutfit.metadata.unique_items_count && (
                              <div className="flex justify-between">
                                <span>Unique Items:</span>
                                <span className="font-medium">{generatedOutfit.metadata.unique_items_count}</span>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>

                    {/* Items */}
                    <div>
                      <div className="text-sm font-medium text-muted-foreground mb-2">
                        Items ({generatedOutfit.items.length})
                      </div>
                      <div className="space-y-2">
                        {generatedOutfit.items.map((item, index) => (
                          <div key={index} className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            {/* Item Thumbnail */}
                            <div className="flex-shrink-0">
                              {item.imageUrl ? (
                                <img 
                                  src={item.imageUrl} 
                                  alt={item.name}
                                  className="w-12 h-12 object-cover rounded-md border border-gray-200 dark:border-gray-700"
                                  onError={(e) => {
                                    // Fallback to placeholder if image fails to load
                                    e.currentTarget.src = `https://placehold.co/48x48/666666/FFFFFF?text=${item.type?.charAt(0) || '?'}`;
                                  }}
                                />
                              ) : (
                                <div className="w-12 h-12 bg-gray-200 dark:bg-gray-700 rounded-md border border-gray-200 dark:border-gray-700 flex items-center justify-center">
                                  <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                                    {item.type?.charAt(0) || '?'}
                                  </span>
                                </div>
                              )}
                            </div>
                            
                            {/* Item Details */}
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-sm truncate">{item.name}</div>
                              <div className="text-xs text-muted-foreground">{item.type} • {item.color}</div>
                              {/* Diversity Info */}
                              {item.diversityScore !== undefined && (
                                <div className="text-xs mt-1">
                                  {item.diversityScore > 0 && (
                                    <span className="text-green-600 dark:text-green-400">
                                      ⭐ {item.diversityReason}
                                    </span>
                                  )}
                                  {item.diversityScore < 0 && (
                                    <span className="text-orange-600 dark:text-orange-400">
                                      ⚠️ {item.diversityReason}
                                    </span>
                                  )}
                                  {item.wearCount > 0 && (
                                    <span className="text-gray-500 ml-2">
                                      Worn {item.wearCount}x
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                            
                            {/* Color Badge */}
                            <Badge variant="outline" className="flex-shrink-0">
                              {item.color}
                            </Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Debug Panel */}
            {showDebugPanel && debugAnalysis && (
              <Card className="mt-6 bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                      🔍 Debug Analysis: Item Filtering Results
                    </CardTitle>
                    <Button 
                      onClick={() => setShowDebugPanel(false)}
                      variant="ghost"
                      size="sm"
                    >
                      ✕
                    </Button>
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Analysis of why items were accepted or rejected during filtering
                    {semanticFlag && (
                      <span className="ml-2 px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                        🧠 Semantic Mode Active
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Summary Stats */}
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{debugAnalysis.total_items}</div>
                      <div className="text-sm text-gray-600">Total Items</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{debugAnalysis.filtered_items}</div>
                      <div className="text-sm text-gray-600">Passed Filters</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">{debugAnalysis.hard_rejected}</div>
                      <div className="text-sm text-gray-600">Hard Rejected</div>
                    </div>
                    <div className="text-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{debugAnalysis.weather_rejected}</div>
                      <div className="text-sm text-gray-600">Weather Rejected</div>
                    </div>
                  </div>

                  {/* Debug Output Information */}
                  {debugAnalysis.debug_output && (
                    <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                      <h4 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
                        🚩 Feature Flags & System Info
                      </h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-blue-700 dark:text-blue-300">Filtering Mode:</span>
                          <span className="ml-2 font-medium text-blue-800 dark:text-blue-200">
                            {debugAnalysis.debug_output.filtering_mode || 'Unknown'}
                          </span>
                        </div>
                        <div>
                          <span className="text-blue-700 dark:text-blue-300">Semantic Filtering:</span>
                          <span className="ml-2 font-medium text-blue-800 dark:text-blue-200">
                            {debugAnalysis.debug_output.semantic_filtering_used ? '✅ Enabled' : '❌ Disabled'}
                          </span>
                        </div>
                        {debugAnalysis.debug_output.feature_flags && (
                          <>
                            <div>
                              <span className="text-blue-700 dark:text-blue-300">Semantic Match:</span>
                              <span className="ml-2 font-medium text-blue-800 dark:text-blue-200">
                                {debugAnalysis.debug_output.feature_flags.semantic_match_enabled ? '✅' : '❌'}
                              </span>
                            </div>
                            <div>
                              <span className="text-blue-700 dark:text-blue-300">Debug Output:</span>
                              <span className="ml-2 font-medium text-blue-800 dark:text-blue-200">
                                {debugAnalysis.debug_output.feature_flags.debug_output_enabled ? '✅' : '❌'}
                              </span>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Item Analysis */}
                  <div className="space-y-3 max-h-96 overflow-auto">
                    {debugAnalysis.debug_analysis?.map((item: any, index: number) => (
                      <div key={item.id || index} className="p-3 bg-white dark:bg-gray-800 rounded-lg border">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <strong className="text-sm">{item.name}</strong>
                              <span className="text-xs text-gray-500">({item.type})</span>
                              {item.valid ? (
                                <Badge variant="outline" className="text-green-600 border-green-600">
                                  ✅ Valid
                                </Badge>
                              ) : (
                                <Badge variant="outline" className="text-red-600 border-red-600">
                                  ❌ Rejected
                                </Badge>
                              )}
                            </div>
                            
                            {/* Item Metadata */}
                            <div className="text-xs text-gray-500 mb-2">
                              <div>Occasions: {JSON.stringify(item.item_data?.occasion || [])}</div>
                              <div>Styles: {JSON.stringify(item.item_data?.style || [])}</div>
                              <div>Mood: {JSON.stringify(item.item_data?.mood || [])}</div>
                            </div>
                            
                            {/* Rejection Reasons */}
                            {!item.valid && item.reasons && item.reasons.length > 0 && (
                              <div className="mt-2">
                                <div className="text-xs font-medium text-red-600 mb-1">Rejection Reasons:</div>
                                <ul className="text-xs text-red-500 space-y-1">
                                  {item.reasons.map((reason: string, reasonIndex: number) => {
                                    // Enhanced reason parsing for semantic matching
                                    const enhancedReason = reason
                                      .replace(/Style mismatch: item styles \[(.*?)\]/g, (match, styles) => {
                                        if (semanticFlag) {
                                          return `Style mismatch: item styles [${styles}] (no semantic compatibility found)`;
                                        }
                                        return match;
                                      })
                                      .replace(/Occasion mismatch: item occasions \[(.*?)\]/g, (match, occasions) => {
                                        if (semanticFlag) {
                                          return `Occasion mismatch: item occasions [${occasions}] (no semantic compatibility found)`;
                                        }
                                        return match;
                                      })
                                      .replace(/Mood mismatch: item moods \[(.*?)\]/g, (match, moods) => {
                                        if (semanticFlag) {
                                          return `Mood mismatch: item moods [${moods}] (no semantic compatibility found)`;
                                        }
                                        return match;
                                      });
                                    
                                    return (
                                      <li key={reasonIndex} className="flex items-start gap-1">
                                        <span>•</span>
                                        <span>{enhancedReason}</span>
                                      </li>
                                    );
                                  })}
                                </ul>
                              </div>
                            )}
                            
                            {/* Success Reasons for Valid Items */}
                            {item.valid && semanticFlag && (
                              <div className="mt-2">
                                <div className="text-xs font-medium text-green-600 mb-1">✅ Semantic Match Found:</div>
                                <div className="text-xs text-green-500">
                                  This item passed semantic compatibility checks
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        {/* Integration Info */}
        <Card className="mt-8 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
              🎯 Safe Integration Approach
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700 dark:text-blue-300">
              <div>
                <div className="font-medium mb-1">Why This is Safe:</div>
                <ul className="space-y-1 text-xs">
                  <li>• Separate demo page - no impact on existing app</li>
                  <li>• Read-only access to your existing data</li>
                  <li>• No changes to current outfit generation</li>
                  <li>• Test all features without risk</li>
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">Next Steps:</div>
                <ul className="space-y-1 text-xs">
                  <li>• Test personalization features here first</li>
                  <li>• Verify everything works with your data</li>
                  <li>• When ready, integrate into main app</li>
                  <li>• Gradual rollout approach</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
