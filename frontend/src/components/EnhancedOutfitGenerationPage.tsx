/**
 * Enhanced Outfit Generation Page
 * ===============================
 * 
 * Example of how to integrate the existing data personalization system
 * into your current outfit generation page.
 */

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Sparkles, 
  Brain, 
  ArrowLeft,
  RefreshCw,
  Heart,
  TrendingUp
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import PersonalizedOutfitGenerator from '@/components/PersonalizedOutfitGenerator';
import PersonalizationStatusCard from '@/components/PersonalizationStatusCard';
import { PersonalizedOutfit } from '@/lib/services/existingDataPersonalizationService';

export default function EnhancedOutfitGenerationPage() {
  const router = useRouter();
  const { user } = useFirebase();
  const [generatedOutfit, setGeneratedOutfit] = useState<PersonalizedOutfit | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleOutfitGenerated = (outfit: PersonalizedOutfit) => {
    setGeneratedOutfit(outfit);
    setError(null);
    console.log('✅ Enhanced outfit generated:', outfit);
  };

  const handleError = (error: string) => {
    setError(error);
    setGeneratedOutfit(null);
    console.error('❌ Enhanced outfit generation error:', error);
  };

  const handleSaveOutfit = async () => {
    if (!generatedOutfit || !user) return;

    try {
      // Here you would integrate with your existing outfit saving logic
      // For example, using your existing OutfitService
      console.log('💾 Saving enhanced outfit:', generatedOutfit);
      
      // Example integration:
      // const outfitData = {
      //   name: generatedOutfit.name,
      //   occasion: generatedOutfit.occasion,
      //   style: generatedOutfit.style,
      //   mood: generatedOutfit.mood,
      //   items: generatedOutfit.items.map(item => ({
      //     id: item.id,
      //     name: item.name,
      //     category: item.type,
      //     color: item.color,
      //     imageUrl: item.imageUrl || '',
      //     user_id: user.uid
      //   })),
      //   description: `Enhanced outfit with personalization score: ${generatedOutfit.personalization_score}`,
      //   user_id: user.uid
      // };
      // 
      // const savedOutfit = await OutfitService.createOutfit(user, outfitData);
      // router.push(`/outfits/${savedOutfit.id}`);
      
    } catch (err) {
      console.error('❌ Error saving outfit:', err);
      setError('Failed to save outfit');
    }
  };

  const handleWearOutfit = async () => {
    if (!generatedOutfit || !user) return;

    try {
      // Here you would integrate with your existing wear tracking logic
      console.log('👕 Marking outfit as worn:', generatedOutfit);
      
      // Example integration:
      // await OutfitService.markOutfitAsWorn(user, generatedOutfit.id);
      // 
      // // Show success and navigate
      // router.push('/outfits');
      
    } catch (err) {
      console.error('❌ Error wearing outfit:', err);
      setError('Failed to mark outfit as worn');
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="container mx-auto p-6">
          <div className="text-center">
            <Brain className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to use enhanced outfit generation</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
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
              <Brain className="h-10 w-10 text-blue-500" />
              Enhanced Outfit Generation
            </h1>
            <p className="text-stone-600 dark:text-stone-400 font-light text-lg mt-2">
              AI-powered outfit creation with personalization from your existing data
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Personalization Status */}
          <div className="lg:col-span-1">
            <PersonalizationStatusCard 
              className="mb-6"
              showRefreshButton={true}
              compact={false}
            />
          </div>

          {/* Right Column: Outfit Generation */}
          <div className="lg:col-span-2">
            <PersonalizedOutfitGenerator
              onOutfitGenerated={handleOutfitGenerated}
              onError={handleError}
              initialRequest={{
                occasion: 'Casual',
                style: 'Classic',
                mood: 'Confident',
                weather: {
                  temperature: 72,
                  condition: 'Clear',
                  humidity: 50,
                  wind_speed: 5,
                  location: 'Current Location'
                }
              }}
            />
          </div>
        </div>

        {/* Generated Outfit Actions */}
        {generatedOutfit && (
          <Card className="mt-8">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="h-5 w-5 text-red-500" />
                Generated Outfit Actions
                {generatedOutfit.personalization_applied && (
                  <Badge variant="default" className="ml-2">
                    Personalized
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div>
                  <div className="text-sm font-medium text-muted-foreground mb-1">Outfit Details</div>
                  <div className="space-y-1">
                    <div><strong>Name:</strong> {generatedOutfit.name}</div>
                    <div><strong>Style:</strong> {generatedOutfit.style}</div>
                    <div><strong>Occasion:</strong> {generatedOutfit.occasion}</div>
                    <div><strong>Mood:</strong> {generatedOutfit.mood}</div>
                    <div><strong>Items:</strong> {generatedOutfit.items.length}</div>
                  </div>
                </div>
                
                {generatedOutfit.personalization_applied && (
                  <div>
                    <div className="text-sm font-medium text-muted-foreground mb-1">Personalization</div>
                    <div className="space-y-1">
                      <div><strong>Score:</strong> {generatedOutfit.personalization_score?.toFixed(2) || 'N/A'}</div>
                      <div><strong>Interactions:</strong> {generatedOutfit.user_interactions}</div>
                      <div><strong>Data Source:</strong> {generatedOutfit.data_source}</div>
                      <div><strong>Applied:</strong> {generatedOutfit.personalization_applied ? 'Yes' : 'No'}</div>
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-3">
                <Button onClick={handleSaveOutfit} className="flex-1">
                  <Heart className="h-4 w-4 mr-2" />
                  Save Outfit
                </Button>
                <Button onClick={handleWearOutfit} variant="outline" className="flex-1">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Wear This Outfit
                </Button>
                <Button 
                  onClick={() => router.push('/outfits')} 
                  variant="outline"
                >
                  View All Outfits
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Card className="mt-6 border-red-200 bg-red-50 dark:bg-red-900/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-2 text-red-600">
                <RefreshCw className="h-4 w-4" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Integration Info */}
        <Card className="mt-8 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800">
          <CardContent className="p-6">
            <h3 className="font-semibold text-blue-800 dark:text-blue-200 mb-2">
              🎯 Enhanced Personalization Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-700 dark:text-blue-300">
              <div>
                <div className="font-medium mb-1">Uses Your Existing Data:</div>
                <ul className="space-y-1 text-xs">
                  <li>• Wardrobe item favorites</li>
                  <li>• Item wear counts</li>
                  <li>• Outfit favorites</li>
                  <li>• Style profile preferences</li>
                </ul>
              </div>
              <div>
                <div className="font-medium mb-1">Benefits:</div>
                <ul className="space-y-1 text-xs">
                  <li>• No data duplication</li>
                  <li>• Immediate personalization</li>
                  <li>• Better recommendations</li>
                  <li>• Transparent insights</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
