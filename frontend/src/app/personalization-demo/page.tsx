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
  
  // Form state for testing different combinations
  const [formData, setFormData] = useState({
    occasion: 'Business',
    style: 'Classic',
    mood: 'Bold'
  });

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

      // Prepare request data with actual wardrobe items
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
        wardrobe: wardrobeItems, // Use actual wardrobe items
        user_profile: { id: user.uid }, // Minimal profile - backend will fetch user's actual profile
        baseItemId: null
      };

      // Convert to Pydantic format
      const convertedData = convertToPydanticShape(requestData);
      
      // Now validate with actual wardrobe items
      if (!validateConvertedData(convertedData)) {
        throw new Error('Data validation failed');
      }
      console.log('✅ [Demo] Data validation passed with', wardrobeItems.length, 'wardrobe items');

      // Use the real outfit generation service
      const { generateOutfit } = await import('@/lib/robustApiClient');
      const response = await generateOutfit(convertedData, authToken);
      const outfit = response.data;
      
      console.log('✅ [Demo] Real outfit generated:', outfit);

      if (outfit) {
        setGeneratedOutfit(outfit);
      }
    } catch (err) {
      console.error('❌ [Demo] Real outfit generation failed:', err);
      // Fallback to mock generation for demo purposes
      console.log('🔄 [Demo] Falling back to mock generation');
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
      });

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
                        {/* Professional */}
                        <option value="Business Formal">Business Formal</option>
                        <option value="Business Casual">Business Casual</option>
                        <option value="Work">Work</option>
                        <option value="Interview">Interview</option>
                        
                        {/* Social */}
                        <option value="Casual">Casual</option>
                        <option value="Formal">Formal</option>
                        <option value="Gala">Gala</option>
                        <option value="Party">Party</option>
                        <option value="Date Night">Date Night</option>
                        <option value="First Date">First Date</option>
                        <option value="Brunch">Brunch</option>
                        <option value="Wedding Guest">Wedding Guest</option>
                        <option value="Cocktail">Cocktail</option>
                        <option value="Night Out">Night Out</option>
                        
                        {/* Travel & Leisure */}
                        <option value="Travel">Travel</option>
                        <option value="Airport">Airport</option>
                        <option value="Loungewear">Loungewear</option>
                        <option value="Beach">Beach</option>
                        <option value="Vacation">Vacation</option>
                        <option value="Festival">Festival</option>
                        
                        {/* Weather Specific */}
                        <option value="Rainy Day">Rainy Day</option>
                        <option value="Snow Day">Snow Day</option>
                        <option value="Hot Weather">Hot Weather</option>
                        
                        {/* Fitness & Health */}
                        <option value="Gym">Gym</option>
                        <option value="Going to the gym">Going to the gym</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Style</label>
                      <select
                        value={formData.style}
                        onChange={(e) => setFormData(prev => ({ ...prev, style: e.target.value }))}
                        className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                      >
                        {/* Academic & Intellectual */}
                        <option value="Dark Academia">Dark Academia</option>
                        <option value="Light Academia">Light Academia</option>
                        <option value="Old Money">Old Money</option>
                        
                        {/* Trendy & Modern */}
                        <option value="Y2K">Y2K</option>
                        <option value="Coastal Grandmother">Coastal Grandmother</option>
                        <option value="Clean Girl">Clean Girl</option>
                        <option value="Cottagecore">Cottagecore</option>
                        
                        {/* Artistic & Creative */}
                        <option value="Avant-Garde">Avant-Garde</option>
                        <option value="Artsy">Artsy</option>
                        <option value="Maximalist">Maximalist</option>
                        <option value="Colorblock">Colorblock</option>
                        
                        {/* Professional & Classic */}
                        <option value="Business Casual">Business Casual</option>
                        <option value="Classic">Classic</option>
                        <option value="Preppy">Preppy</option>
                        <option value="Urban Professional">Urban Professional</option>
                        
                        {/* Urban & Street */}
                        <option value="Streetwear">Streetwear</option>
                        <option value="Techwear">Techwear</option>
                        <option value="Grunge">Grunge</option>
                        <option value="Hipster">Hipster</option>
                        
                        {/* Feminine & Romantic */}
                        <option value="Romantic">Romantic</option>
                        <option value="Boho">Boho</option>
                        <option value="French Girl">French Girl</option>
                        <option value="Pinup">Pinup</option>
                        
                        {/* Modern & Minimal */}
                        <option value="Minimalist">Minimalist</option>
                        <option value="Modern">Modern</option>
                        <option value="Scandinavian">Scandinavian</option>
                        
                        {/* Alternative & Edgy */}
                        <option value="Gothic">Gothic</option>
                        <option value="Punk">Punk</option>
                        <option value="Cyberpunk">Cyberpunk</option>
                        <option value="Edgy">Edgy</option>
                        
                        {/* Seasonal & Lifestyle */}
                        <option value="Coastal Chic">Coastal Chic</option>
                        <option value="Athleisure">Athleisure</option>
                        <option value="Casual Cool">Casual Cool</option>
                        <option value="Loungewear">Loungewear</option>
                        <option value="Workout">Workout</option>
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium mb-2">Mood</label>
                      <select
                        value={formData.mood}
                        onChange={(e) => setFormData(prev => ({ ...prev, mood: e.target.value }))}
                        className="w-full p-2 border rounded-md bg-white dark:bg-gray-800"
                      >
                        <option value="Romantic">Romantic</option>
                        <option value="Playful">Playful</option>
                        <option value="Serene">Serene</option>
                        <option value="Dynamic">Dynamic</option>
                        <option value="Bold">Bold</option>
                        <option value="Subtle">Subtle</option>
                      </select>
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
                        Generating {formData.style} {formData.occasion} Outfit...
                      </>
                    ) : (
                      <>
                        <TestTube className="h-4 w-4 mr-2" />
                        Generate {formData.style} {formData.occasion} Outfit
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
                                    e.currentTarget.src = `https://via.placeholder.com/48/666666/FFFFFF?text=${item.type?.charAt(0) || '?'}`;
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
