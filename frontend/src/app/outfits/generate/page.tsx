'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { 
  Sparkles, 
  Palette, 
  Calendar, 
  MapPin, 
  Clock, 
  Zap,
  Shirt,
  Heart,
  RefreshCw,
  ArrowLeft
} from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import { useRouter } from 'next/navigation';
import OutfitService from '@/lib/services/outfitService';

interface OutfitGenerationForm {
  occasion: string;
  style: string;
  mood: string;
  weather: string;
  description: string;
}

interface GeneratedOutfit {
  id: string;
  name: string;
  style: string;
  mood: string;
  occasion: string;
  confidence_score: number;
  score_breakdown?: any;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
    color: string;
  }>;
  reasoning: string;
  createdAt: string;
}

interface OutfitRating {
  rating: number;
  isLiked: boolean;
  isDisliked: boolean;
  feedback?: string;
}

export default function OutfitGenerationPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const [baseItem, setBaseItem] = useState<any>(null);
  const [wardrobeItems, setWardrobeItems] = useState<any[]>([]);
  const [wardrobeLoading, setWardrobeLoading] = useState(false);
  
  // Extract base item ID from URL parameters
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const baseItemId = urlParams.get('baseItemId');
    
    if (baseItemId) {
      console.log('🔍 Base item ID from URL:', baseItemId);
      // We'll find the full item when wardrobe loads
      setBaseItem({ id: baseItemId });
    }
  }, []);

  // Fetch wardrobe items when user is available
  useEffect(() => {
    const fetchWardrobeItems = async () => {
      if (!user) return;
      
      try {
        setWardrobeLoading(true);
        const token = await user.getIdToken();
        const response = await fetch('/api/wardrobe', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          // Handle the wardrobe API response structure
          const items = data.items || data;
          setWardrobeItems(items);
          console.log('🔍 Wardrobe items loaded:', items.length);
          
          // Get base item ID from URL params directly (in case state hasn't been set yet)
          const urlParams = new URLSearchParams(window.location.search);
          const baseItemId = urlParams.get('baseItemId');
          
          // If we have a baseItem ID, find the full item in wardrobe
          if (baseItemId) {
            const fullItem = items.find((item: any) => item.id === baseItemId);
            if (fullItem) {
              console.log('🔍 Found base item in wardrobe with full metadata:', fullItem.name);
              console.log('🔍 Rich metadata includes:', {
                dominantColors: fullItem.dominantColors?.length || 0,
                matchingColors: fullItem.matchingColors?.length || 0,
                metadata: fullItem.metadata ? 'present' : 'missing',
                material: fullItem.metadata?.visualAttributes?.material,
                texture: fullItem.metadata?.visualAttributes?.textureStyle,
                silhouette: fullItem.metadata?.visualAttributes?.silhouette,
                fit: fullItem.metadata?.visualAttributes?.fit
              });
              console.log('🔍 Setting base item to:', {
                id: fullItem.id,
                name: fullItem.name,
                imageUrl: fullItem.imageUrl || fullItem.image_url,
                type: fullItem.type
              });
              setBaseItem(fullItem);
            } else {
              console.warn('🔍 Base item not found in wardrobe:', baseItemId);
              setBaseItem(null);
            }
          }
        } else {
          console.error('🔍 Failed to fetch wardrobe items:', response.status);
        }
      } catch (error) {
        console.error('🔍 Error fetching wardrobe items:', error);
      } finally {
        setWardrobeLoading(false);
      }
    };

    if (user) {
      fetchWardrobeItems();
    }
  }, [user]);
  
  // Backend API base URL
  const API_BASE = 'http://localhost:3001'; // Temporarily use local backend for testing
  const [formData, setFormData] = useState<OutfitGenerationForm>({
    occasion: '',
    style: '',
    mood: '',
    weather: '',
    description: ''
  });
  const [generating, setGenerating] = useState(false);
  const [generatedOutfit, setGeneratedOutfit] = useState<GeneratedOutfit | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [outfitRating, setOutfitRating] = useState<OutfitRating>({
    rating: 0,
    isLiked: false,
    isDisliked: false,
    feedback: ''
  });
  const [ratingSubmitted, setRatingSubmitted] = useState(false);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [filteredStyles, setFilteredStyles] = useState<string[]>([]);

  const occasions = [
    // Everyday
    'Casual', 'Weekend', 'Errands', 'Loungewear',
    // Professional
    'Business', 'Business Casual', 'Office', 'Interview',
    // Social
    'Party', 'Cocktail', 'Date Night', 'Brunch', 'Dinner',
    // Special Events
    'Wedding', 'Gala', 'Formal', 'Black Tie',
    // Active & Outdoor
    'Sporty', 'Athletic', 'Outdoor', 'Beach', 'Travel',
    // Creative & Cultural
    'Creative', 'Art Gallery', 'Museum', 'Concert', 'Festival',
    // Seasonal
    'Summer', 'Winter', 'Spring', 'Fall',
    // Lifestyle
    'Coastal', 'Urban', 'Country', 'Resort'
  ];

  const styles = [
    // Academic & Intellectual
    'Dark Academia', 'Light Academia', 'Old Money',
    // Trendy & Modern
    'Y2K', 'Coastal Grandmother', 'Clean Girl', 'Cottagecore',
    // Artistic & Creative
    'Avant-Garde', 'Artsy', 'Maximalist', 'Colorblock',
    // Professional & Classic
    'Business Casual', 'Classic', 'Preppy', 'Urban Professional',
    // Urban & Street
    'Streetwear', 'Techwear', 'Grunge', 'Hipster',
    // Feminine & Romantic
    'Romantic', 'Boho', 'French Girl', 'Pinup',
    // Modern & Minimal
    'Minimalist', 'Modern', 'Scandinavian',
    // Alternative & Edgy
    'Gothic', 'Punk', 'Cyberpunk', 'Edgy',
    // Seasonal & Lifestyle
    'Coastal Chic', 'Athleisure', 'Casual Cool', 'Loungewear'
  ];

  const moods = [
    // Personality & Attitude
    'Confident', 'Bold', 'Mysterious', 'Playful', 'Sophisticated',
    // Energy Levels
    'Energetic', 'Relaxed', 'Calm', 'Dynamic', 'Serene',
    // Emotional States
    'Romantic', 'Dreamy', 'Powerful', 'Edgy', 'Whimsical',
    // Style Attitudes
    'Classic', 'Trendy', 'Artistic', 'Minimalist', 'Maximalist',
    // Social Vibes
    'Approachable', 'Intimidating', 'Friendly', 'Professional', 'Casual'
  ];

  const weatherOptions = [
    'sunny', 'rainy', 'cloudy', 'cold', 'warm', 'hot', 'mild'
  ];

  // ENHANCED: Gender-aware style filtering
  const filterStylesByGender = (styles: string[], gender: string) => {
    // If no gender is provided, default to male filtering (since user is male)
    const effectiveGender = gender || 'male';
    
    const feminineStyles = [
      'French Girl', 'Romantic', 'Pinup', 'Boho', 'Cottagecore',
      'Coastal Grandmother', 'Clean Girl'
    ];
    
    const masculineStyles = [
      'Techwear', 'Grunge', 'Streetwear'
    ];
    
    if (effectiveGender.toLowerCase() === 'male') {
      const filtered = styles.filter(style => !feminineStyles.includes(style));
      console.log('🔍 Filtered styles for male user:', filtered.length, 'of', styles.length);
      return filtered;
    } else if (effectiveGender.toLowerCase() === 'female') {
      return styles.filter(style => !masculineStyles.includes(style));
    }
    
    return styles;
  };

  // Fetch user profile and filter styles
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!user) {
        console.log('🔍 No user authenticated, skipping profile fetch');
        return;
      }
      
      console.log('🔍 Fetching profile for user:', user.uid);
      try {
        const token = await user.getIdToken();
        const response = await fetch('/api/user/profile', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        
        if (response.ok) {
          const profile = await response.json();
          console.log('🔍 User profile fetched:', profile);
          setUserProfile(profile);
          
          // Filter styles based on gender
          const filtered = filterStylesByGender(styles, profile.gender);
          console.log('🔍 Filtered styles for gender:', profile.gender, ':', filtered);
          setFilteredStyles(filtered);
          
          // If current style is not compatible, reset it
          if (formData.style && !filtered.includes(formData.style)) {
            console.log('🔍 Resetting incompatible style:', formData.style);
            setFormData(prev => ({ ...prev, style: '' }));
          }
        } else {
          console.error('🔍 Profile fetch failed:', response.status, response.statusText);
          // Fallback to male-appropriate styles for 502 errors
          if (response.status === 502) {
            console.log('🔍 Backend error (502), using male-appropriate styles as fallback');
            const maleStyles = filterStylesByGender(styles, 'male');
            setFilteredStyles(maleStyles);
          } else {
            // For other errors, use all styles
            setFilteredStyles(styles);
          }
        }
              } catch (error) {
          console.error('🔍 Error fetching user profile:', error);
          // Fallback to filtered styles for male users (since you're male)
          console.log('🔍 Falling back to male-appropriate styles due to profile fetch error');
          const maleStyles = filterStylesByGender(styles, 'male');
          setFilteredStyles(maleStyles);
        }
    };

    fetchUserProfile();
  }, [user]);

  const handleInputChange = (field: keyof OutfitGenerationForm, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleGenerateOutfit = async () => {
    if (!user) {
      setError('Please sign in to generate outfits');
      return;
    }

    if (!formData.occasion || !formData.style || !formData.mood) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setGenerating(true);
      setError(null);
      
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      
      // Prepare request data with all required fields
      const requestData = {
        occasion: formData.occasion,
        style: formData.style,
        mood: formData.mood,
        weather: {
          temperature: 20, // Default temperature
          condition: formData.weather || "Sunny",
          location: "Default"
        },
        wardrobe: Array.isArray(wardrobeItems) ? wardrobeItems : (wardrobeItems as any)?.items || [],
        user_profile: {
          id: user.uid,
          name: user.displayName || "User",
          email: user.email || "",
          gender: userProfile?.gender || "male",
          age: userProfile?.age || 25,
          style_preferences: userProfile?.style_preferences || [],
          size_preferences: userProfile?.size_preferences || [],
          color_preferences: userProfile?.color_preferences || []
        },
        likedOutfits: [],
        trendingStyles: [],
        ...(baseItem && { baseItemId: baseItem.id })
      };
      
      console.log('🔍 DEBUG: Request data being sent:', {
        occasion: requestData.occasion,
        style: requestData.style,
        mood: requestData.mood,
        wardrobeCount: requestData.wardrobe?.length,
        wardrobeType: typeof requestData.wardrobe,
        wardrobeKeys: requestData.wardrobe ? Object.keys(requestData.wardrobe) : null,
        baseItem: baseItem ? { id: baseItem.id, name: baseItem.name, type: baseItem.type } : null,
        baseItemId: baseItem ? baseItem.id : null,
        baseItemName: baseItem ? baseItem.name : null
      });
      
      // Additional debug to show the full request data
      console.log('🔍 DEBUG: Full request data:', requestData);
      console.log('🔍 DEBUG: baseItemId in request:', requestData.baseItemId);
      
      console.log('🔍 DEBUG: Making API call to /api/outfits');
      const response = await fetch('/api/outfits', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });
      console.log('🔍 DEBUG: API response status:', response.status);
      console.log('🔍 DEBUG: API response URL:', response.url);
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to generate outfits.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data = await response.json();
      console.log('🔍 DEBUG: Generated outfit data:', data);
      console.log('🔍 DEBUG: Items with images:', data.items?.map(item => ({ name: item.name, imageUrl: item.imageUrl })));
      setGeneratedOutfit(data);
      
      // Auto-save the generated outfit so it has an ID for ratings
      if (user) {
        try {
          // Skip auto-save if outfit already has an ID (already saved by backend)
          if (data.id) {
            console.log('🔍 DEBUG: Skipping auto-save - outfit already has ID:', data.id);
            
            // Outfit saved successfully - user can now interact with it
            // No auto-navigation - let user decide when to go to outfits page
            return;
          }
          
          // Validate minimum items before saving
          if (!data.items || data.items.length < 3) {
            console.warn('🔍 DEBUG: Skipping auto-save - need at least 3 items to save outfit');
            return;
          }
          
          const token = await user.getIdToken();
          const saveResponse = await fetch('/api/outfits', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              name: data.name,
              occasion: data.occasion || formData.occasion, 
              style: data.style,
              description: data.reasoning,
              items: data.items.map((item: any) => ({
                ...item,
                userId: user.uid,  // Required: inject from Firebase auth
                subType: item.subType || item.category || item.type || "item",  // Required: fallback chain
                style: [data.style] || ["casual"],  // Required: List[str] from parent outfit
                occasion: [data.occasion || formData.occasion] || ["casual"],  // Required: List[str] from parent
                imageUrl: item.imageUrl || item.image_url || item.image || "",  // Normalize image field
                color: item.color || "unknown",  // Ensure color is provided
                type: item.type || "item",  // Ensure type is provided
                
                // Required ClothingItem fields that were missing:
                season: ["All"],                               // fallback if no season logic yet
                tags: [],                                      // default empty array
                dominantColors: [],                            // default empty array
                matchingColors: [],                            // default empty array
                createdAt: new Date().toISOString(),      // ISO timestamp for consistency
                updatedAt: new Date().toISOString(),      // ISO timestamp for consistency
              })),
              createdAt: new Date().toISOString()
            }),
          });
          
          if (saveResponse.ok) {
            const savedOutfit = await saveResponse.json();
            // Update the outfit with the new ID
            setGeneratedOutfit(prev => prev ? {
              ...prev,
              id: savedOutfit.id || savedOutfit.outfitId
            } : null);
            console.log('🔍 DEBUG: Outfit auto-saved with ID:', savedOutfit.id || savedOutfit.outfitId);
            
            // Outfit saved successfully - user can now interact with it
            // No auto-navigation - let user decide when to go to outfits page
          }
        } catch (err) {
          console.log('🔍 DEBUG: Auto-save failed, but outfit generation succeeded');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate outfit');
    } finally {
      setGenerating(false);
    }
  };

  const handleWearOutfit = async () => {
    if (!generatedOutfit || !user) return;
    
    // Validate minimum items before wearing
    if (!generatedOutfit.items || generatedOutfit.items.length < 3) {
      setError('Need at least 3 items to wear an outfit');
      return;
    }
    
    try {
      // Use OutfitService to mark as worn - this updates both database and local state
      await OutfitService.markOutfitAsWorn(user, generatedOutfit.id);
      
      // Dispatch event to notify dashboard of outfit being marked as worn
      const event = new CustomEvent('outfitMarkedAsWorn', {
        detail: {
          outfitId: generatedOutfit.id,
          outfitName: generatedOutfit.name,
          timestamp: new Date().toISOString()
        }
      });
      window.dispatchEvent(event);
      console.log('🔄 [Generate] Dispatched outfitMarkedAsWorn event for dashboard refresh');
      
      // Show success message and navigate to outfits page
      setError(null);
      // Show success message briefly before navigating
      setGeneratedOutfit(prev => prev ? {
        ...prev,
        isWorn: true,
        lastWorn: new Date().toISOString()
      } : null);
      
      // Navigate after a short delay to show success
      setTimeout(() => {
        // Add timestamp to force refresh of outfits page
        const timestamp = Date.now();
        console.log('🔄 [Generate] Navigating to outfits page with forced refresh');
        router.push(`/outfits?refresh=${timestamp}`);
      }, 1500);
    } catch (err) {
      console.error('Error wearing outfit:', err);
      setError('Failed to wear outfit');
    }
  };

  const handleRegenerate = () => {
    setGeneratedOutfit(null);
    setError(null);
    setOutfitRating({ rating: 0, isLiked: false, isDisliked: false, feedback: '' });
    setRatingSubmitted(false);
  };

  const handleRatingChange = (rating: number) => {
    setOutfitRating(prev => ({ ...prev, rating }));
    // Auto-submit after a short delay to allow user to see their selection
    setTimeout(() => {
      if (rating > 0) {
        handleSubmitRating();
      }
    }, 500);
  };

  const handleLikeToggle = () => {
    setOutfitRating(prev => ({ 
      ...prev, 
      isLiked: !prev.isLiked, 
      isDisliked: false 
    }));
    // Auto-submit like/dislike changes
    setTimeout(() => {
      handleSubmitRating();
    }, 300);
  };

  const handleDislikeToggle = () => {
    setOutfitRating(prev => ({ 
      ...prev, 
      isDisliked: !prev.isDisliked, 
      isLiked: false 
    }));
    // Auto-submit like/dislike changes
    setTimeout(() => {
      handleSubmitRating();
    }, 300);
  };

  const handleFeedbackChange = (feedback: string) => {
    setOutfitRating(prev => ({ ...prev, feedback }));
    // Auto-submit feedback after user stops typing (debounced)
    clearTimeout((window as any).feedbackTimeout);
    (window as any).feedbackTimeout = setTimeout(() => {
      if (feedback.trim() && outfitRating.rating > 0) {
        handleSubmitRating();
      }
    }, 1000);
  };

  const handleSubmitRating = async () => {
    if (!generatedOutfit || !user) return;
    
    // Only submit if there's actual rating data
    if (outfitRating.rating === 0 && !outfitRating.isLiked && !outfitRating.isDisliked && !outfitRating.feedback.trim()) {
      console.log('🔍 DEBUG: No rating data to submit, skipping');
      return;
    }
    
    try {
      const token = await user.getIdToken();
      
      // If outfit doesn't have an ID yet, save it first
      let outfitId = generatedOutfit.id;
      console.log('🔍 DEBUG: Checking outfit ID for rating:', { 
        outfitId, 
        hasId: !!outfitId,
        outfitName: generatedOutfit.name 
      });
      
      if (!outfitId) {
        console.log('🔍 DEBUG: No outfit ID found, will save outfit first');
        // Validate minimum items before saving for rating
        if (!generatedOutfit.items || generatedOutfit.items.length < 3) {
          setError('Need at least 3 items to save and rate an outfit');
          return;
        }
        
        const outfitPayload = {
          name: generatedOutfit.name,
          occasion: generatedOutfit.occasion || formData.occasion,
          style: generatedOutfit.style,
          description: generatedOutfit.reasoning,
          items: generatedOutfit.items.map((item: any) => ({
            ...item,
            userId: user.uid,  // Required: inject from Firebase auth
            subType: item.subType || item.category || item.type || "item",  // Required: fallback chain
            style: [generatedOutfit.style] || ["casual"],  // Required: List[str] from parent outfit
            occasion: [generatedOutfit.occasion || formData.occasion] || ["casual"],  // Required: List[str] from parent
            imageUrl: item.imageUrl || item.image_url || item.image || "",  // Normalize image field
            color: item.color || "unknown",  // Ensure color is provided
            type: item.type || "item",  // Ensure type is provided
            
            // Required ClothingItem fields that were missing:
            season: ["All"],                               // fallback if no season logic yet
            tags: [],                                      // default empty array
            dominantColors: [],                            // default empty array
            matchingColors: [],                            // default empty array
            createdAt: Math.floor(Date.now() / 1000),      // timestamp in seconds
            updatedAt: Math.floor(Date.now() / 1000),      // timestamp in seconds
          })),
          createdAt: Math.floor(Date.now() / 1000)
        };
        
        console.log('🔍 DEBUG: Outfit creation payload:', JSON.stringify(outfitPayload, null, 2));
        
        const saveResponse = await fetch('/api/outfits', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(outfitPayload),
        });
        
        if (saveResponse.ok) {
          const savedOutfit = await saveResponse.json();
          outfitId = savedOutfit.id || savedOutfit.outfitId;
          
          console.log('✅ [Generate] Outfit saved successfully:', savedOutfit);
          
          // Update the generated outfit with the new ID
          setGeneratedOutfit(prev => prev ? {
            ...prev,
            id: outfitId
          } : null);
        } else {
          console.error('❌ [Generate] Failed to save outfit:', saveResponse.status, await saveResponse.text());
          setError('Failed to save outfit for rating');
          return;
        }
      }
      
      // Prepare rating payload - only include rating if stars were selected
      const ratingPayload: any = {
        outfitId: outfitId,
        isLiked: outfitRating.isLiked,
        isDisliked: outfitRating.isDisliked,
        feedback: outfitRating.feedback
      };
      
      // Only include rating if stars were actually selected (1-5)
      if (outfitRating.rating > 0) {
        ratingPayload.rating = outfitRating.rating;
      }
      
      console.log('🔍 DEBUG: Submitting rating payload:', ratingPayload);
      
      // Submit rating to backend
      const response = await fetch('/api/outfits/rate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ratingPayload),
      });
      
      if (response.ok) {
        setRatingSubmitted(true);
        // Update the generated outfit with rating data
        setGeneratedOutfit(prev => prev ? {
          ...prev,
          rating: outfitRating.rating,
          isLiked: outfitRating.isLiked,
          isDisliked: outfitRating.isDisliked
        } : null);
        console.log('✅ Rating submitted successfully');
        console.log('🔄 [Generate] Rating submitted - outfit should now be available in outfits list');
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Rating submission failed:', errorData);
        setError(`Failed to submit rating: ${errorData.detail || errorData.error || 'Unknown error'}`);
      }
    } catch (err) {
      console.error('❌ Error submitting rating:', err);
      setError('Failed to submit rating');
    }
  };

  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Authenticating...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <Palette className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to generate outfits</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-8">
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => router.push('/outfits')}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Outfits
          </Button>
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Sparkles className="h-8 w-8 text-emerald-500" />
              Generate New Outfit
            </h1>
            <p className="text-muted-foreground">AI-powered outfit creation based on your preferences</p>
          </div>
        </div>

        {/* Base Item Indicator */}
        {baseItem && (
          <Card className="mb-6 border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-900/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-lg overflow-hidden flex-shrink-0">
                  <img
                    src={baseItem.imageUrl || baseItem.image_url || '/placeholder.jpg'}
                    alt={baseItem.name || 'Base item'}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      const target = e.target as HTMLImageElement;
                      target.src = '/placeholder.jpg';
                    }}
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    Generating outfit with: {baseItem.name || 'Unknown item'}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    This item will be included as the base layer in your outfit
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setBaseItem(null);
                    // Remove base item from URL
                    const url = new URL(window.location.href);
                    url.searchParams.delete('baseItem');
                    window.history.replaceState({}, '', url.toString());
                  }}
                >
                  Remove
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Generation Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Palette className="h-5 w-5" />
                Outfit Preferences
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Occasion *</label>
                  <Select value={formData.occasion} onValueChange={(value) => handleInputChange('occasion', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
                    </SelectTrigger>
                    <SelectContent>
                      {occasions.map((occasion) => (
                        <SelectItem key={occasion} value={occasion}>
                          {occasion.charAt(0).toUpperCase() + occasion.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Style *</label>
                  <Select value={formData.style} onValueChange={(value) => handleInputChange('style', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select style" />
                    </SelectTrigger>
                    <SelectContent>
                      {(filteredStyles.length > 0 ? filteredStyles : styles).map((style) => (
                        <SelectItem key={style} value={style}>
                          {style.charAt(0).toUpperCase() + style.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {userProfile?.gender && filteredStyles.length < styles.length && (
                    <p className="text-xs text-muted-foreground">
                      Styles filtered for {userProfile.gender} users
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Mood *</label>
                  <Select value={formData.mood} onValueChange={(value) => handleInputChange('mood', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select mood" />
                    </SelectTrigger>
                    <SelectContent>
                      {moods.map((mood) => (
                        <SelectItem key={mood} value={mood}>
                          {mood.charAt(0).toUpperCase() + mood.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Weather</label>
                  <Select value={formData.weather} onValueChange={(value) => handleInputChange('weather', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select weather" />
                    </SelectTrigger>
                    <SelectContent>
                      {weatherOptions.map((weather) => (
                        <SelectItem key={weather} value={weather}>
                          {weather.charAt(0).toUpperCase() + weather.slice(1)}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Additional Details</label>
                <Textarea
                  placeholder="Any specific preferences, colors, or details you'd like to include..."
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  rows={3}
                />
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <Button 
                onClick={handleGenerateOutfit} 
                disabled={generating || wardrobeLoading || !formData.occasion || !formData.style || !formData.mood}
                className="w-full"
                size="lg"
              >
                {generating ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Generating Outfit...
                  </>
                ) : wardrobeLoading ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Loading Wardrobe...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Generate Outfit
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Generated Outfit Display */}
          <div className="space-y-6">
            {generatedOutfit ? (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>Generated Outfit</span>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Zap className="h-3 w-3" />
                      {Math.round(generatedOutfit.confidence_score * 100)}% Match
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{generatedOutfit.name}</h3>
                    <div className="flex flex-wrap gap-2 mb-3">
                      <Badge variant="outline">{generatedOutfit.style}</Badge>
                      <Badge variant="outline">{generatedOutfit.mood}</Badge>
                      <Badge variant="outline">{generatedOutfit.occasion}</Badge>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium mb-2">Items ({generatedOutfit.items.length})</h4>
                    <div className="space-y-2">
                      {generatedOutfit.items.map((item, index) => (
                        <div key={index} className="flex items-center gap-3 p-2 bg-gray-50 dark:bg-gray-800 rounded-md">
                          {/* Show actual item image if available, otherwise fallback icon */}
                          {(item.imageUrl || item.image_url || item.image) ? (
                            <img 
                              src={item.imageUrl || item.image_url || item.image} 
                              alt={item.name}
                              className="w-12 h-12 object-cover rounded-md border border-gray-200"
                              onError={(e) => {
                                // Fallback to icon if image fails to load
                                e.currentTarget.style.display = 'none';
                                e.currentTarget.nextElementSibling.style.display = 'block';
                              }}
                            />
                          ) : null}
                          <Shirt 
                            className={`h-12 w-12 text-gray-500 ${(item.imageUrl || item.image_url || item.image) ? 'hidden' : ''}`}
                            style={{ display: (item.imageUrl || item.image_url || item.image) ? 'none' : 'block' }}
                          />
                          <div className="flex-1">
                            <p className="font-medium text-sm">{item.name}</p>
                            <p className="text-xs text-muted-foreground capitalize">{item.type} • {item.color}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Score Breakdown */}
                  {generatedOutfit.score_breakdown && (
                    <div>
                      <h4 className="font-medium mb-2">Outfit Score Breakdown</h4>
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
                          <div className="text-sm font-medium text-blue-700 dark:text-blue-300">Total Score</div>
                          <div className="text-2xl font-bold text-blue-800 dark:text-blue-200">
                            {generatedOutfit.score_breakdown.total_score}
                          </div>
                          <div className="text-xs text-blue-600 dark:text-blue-400">
                            Grade: {generatedOutfit.score_breakdown.grade}
                          </div>
                        </div>
                        <div className="bg-green-50 dark:bg-green-900/20 p-3 rounded-md">
                          <div className="text-sm font-medium text-green-700 dark:text-green-300">Confidence</div>
                          <div className="text-2xl font-bold text-green-800 dark:text-green-200">
                            {Math.round(generatedOutfit.confidence_score * 100)}%
                          </div>
                        </div>
                      </div>
                      
                      {/* Component Scores */}
                      <div className="space-y-2">
                        {Object.entries(generatedOutfit.score_breakdown).map(([key, value]) => {
                          if (key === 'total_score' || key === 'grade' || key === 'score_interpretation') return null;
                          return (
                            <div key={key} className="flex justify-between items-center text-sm">
                              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
                              <span className="font-medium">{value}</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}

                  {generatedOutfit.reasoning && (
                    <div>
                      <h4 className="font-medium mb-2">AI Reasoning</h4>
                      <p className="text-sm text-muted-foreground bg-blue-50 dark:bg-blue-900/20 p-3 rounded-md">
                        {generatedOutfit.reasoning}
                      </p>
                    </div>
                  )}

                  {/* Outfit Rating Section */}
                  <div className="border-t pt-4">
                    <h4 className="font-medium mb-3">Rate This Outfit</h4>
                    
                    {/* Star Rating */}
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-sm text-muted-foreground">Rating:</span>
                      <div className="flex gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            onClick={() => handleRatingChange(star)}
                            className={`text-2xl transition-colors ${
                              star <= outfitRating.rating
                                ? 'text-yellow-400 fill-current'
                                : 'text-gray-300 dark:text-gray-600'
                            }`}
                          >
                            ★
                          </button>
                        ))}
                      </div>
                      {outfitRating.rating > 0 && (
                        <span className="text-sm text-muted-foreground ml-2">
                          {outfitRating.rating} star{outfitRating.rating !== 1 ? 's' : ''}
                        </span>
                      )}
                    </div>

                    {/* Like/Dislike Buttons */}
                    <div className="flex gap-3 mb-3">
                      <Button
                        variant={outfitRating.isLiked ? "default" : "outline"}
                        size="sm"
                        onClick={handleLikeToggle}
                        className="flex items-center gap-2"
                      >
                        <Heart className={`h-4 w-4 ${outfitRating.isLiked ? 'fill-current' : ''}`} />
                        {outfitRating.isLiked ? 'Liked' : 'Like'}
                      </Button>
                      <Button
                        variant={outfitRating.isDisliked ? "destructive" : "outline"}
                        size="sm"
                        onClick={handleDislikeToggle}
                        className="flex items-center gap-2"
                      >
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.912c.163 0 .326.02.485.06L17 5a2 2 0 011 1.732v5.268A2 2 0 0117 14h-3.764a2 2 0 01-1.789-2.894l3.5-7A2 2 0 0013.264 3H8.348a2 2 0 00-1.789 2.894l3.5 7A2 2 0 005.236 14H10" />
                        </svg>
                        {outfitRating.isDisliked ? 'Disliked' : 'Dislike'}
                      </Button>
                    </div>

                    {/* Feedback Text */}
                    <div className="mb-3">
                      <Textarea
                        placeholder="Optional: Share what you think about this outfit..."
                        value={outfitRating.feedback}
                        onChange={(e) => handleFeedbackChange(e.target.value)}
                        rows={2}
                        className="text-sm"
                      />
                    </div>

                    {/* Auto-submit info */}
                    {outfitRating.rating > 0 && (
                      <div className="text-xs text-muted-foreground text-center mb-3">
                        ✓ Rating automatically submitted
                      </div>
                    )}

                    {/* Rating Submitted Confirmation */}
                    {ratingSubmitted && (
                      <div className="p-3 bg-green-50 border border-green-200 rounded-md mb-3">
                        <p className="text-sm text-green-600 text-center">
                          ✓ Rating submitted! This helps improve future outfit suggestions.
                        </p>
                      </div>
                    )}
                    
                    {/* Outfit Worn Confirmation */}
                    {generatedOutfit?.isWorn && (
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded-md mb-3">
                        <p className="text-sm text-blue-600 text-center">
                          ✓ Outfit marked as worn! Redirecting to outfits page...
                        </p>
                      </div>
                    )}
                  </div>

                  <div className="flex gap-3 pt-4">
                    {/* Show different buttons based on state */}
                    {generatedOutfit?.isWorn ? (
                      // After outfit is worn, show navigation button
                      <Button 
                        onClick={() => router.push(`/outfits?refresh=${Date.now()}`)} 
                        className="flex-1"
                      >
                        <Shirt className="h-4 w-4 mr-2" />
                        View My Outfits
                      </Button>
                    ) : ratingSubmitted ? (
                      // After rating is submitted, show both options
                      <>
                        <Button onClick={handleWearOutfit} className="flex-1">
                          <Calendar className="h-4 w-4 mr-2" />
                          Wear Outfit
                        </Button>
                        <Button 
                          variant="outline" 
                          onClick={() => router.push(`/outfits?refresh=${Date.now()}`)}
                        >
                          <Shirt className="h-4 w-4 mr-2" />
                          View Outfits
                        </Button>
                      </>
                    ) : (
                      // Default state: wear outfit and regenerate
                      <>
                        <Button onClick={handleWearOutfit} className="flex-1">
                          <Calendar className="h-4 w-4 mr-2" />
                          Wear Outfit
                        </Button>
                        <Button variant="outline" onClick={handleRegenerate}>
                          <RefreshCw className="h-4 w-4 mr-2" />
                          Regenerate
                        </Button>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ) : (
              <Card className="border-dashed">
                <CardContent className="p-12 text-center">
                  <Sparkles className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Ready to Generate</h3>
                  <p className="text-muted-foreground">
                    Fill out the form and click "Generate Outfit" to create your AI-powered style combination
                  </p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
