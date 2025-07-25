"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useFirebase } from '@/lib/firebase-context';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { doc, getDoc, updateDoc } from 'firebase/firestore';
import { db } from '@/lib/firebase/config';
import { useToast } from '@/components/ui/use-toast';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  User, 
  Heart, 
  Ruler, 
  Star,
  RefreshCw,
  Edit3,
  Check,
  X
} from 'lucide-react';

// Extended interface to match the comprehensive onboarding data structure
interface ExtendedUserProfile {
  id: string;
  name: string;
  email: string;
  gender?: string;
  
  // Basic Info
  heightFeetInches?: string;
  weight?: string;
  bodyType?: string;
  skinTone?: {
    depth: string;
    undertone: string;
    palette: string[];
    id: string;
    color: string;
  };
  
  // Measurements
  topSize?: string;
  bottomSize?: string;
  shoeSize?: string;
  dressSize?: string;
  jeanWaist?: string;
  braSize?: string;
  
  // Style Preferences
  stylePreferences?: string[];
  occasions?: string[];
  preferredColors?: string[];
  formality?: string;
  budget?: string;
  preferredBrands?: string[];
  fitPreferences?: string[];
  
  // New Quiz-First Flow Data
  quizResponses?: Array<{
    questionId: string;
    answer: string | string[];
    confidence: number;
  }>;
  colorPalette?: {
    primary: string[];
    secondary: string[];
    accent: string[];
    neutral: string[];
    avoid: string[];
  };
  
  // Legacy fields for backward compatibility
  measurements?: {
    height: number;
    weight: number;
    bodyType: string;
    skinTone?: string;
  };
  preferences?: {
    style: string[];
    colors: string[];
    occasions: string[];
    formality?: string;
  };
  selfieUrl?: string;
  hybridStyleName?: string;
  createdAt?: number;
  updatedAt?: number;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const { toast } = useToast();
  const { resetOnboarding } = useOnboardingStore();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState<ExtendedUserProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState('');

  const fetchProfile = async () => {
    if (!db || !user) return;
    
    try {
      // Fetch from the users collection (new source)
      const userDoc = await getDoc(doc(db, 'users', user.uid));
      
      if (userDoc.exists()) {
        const userData = userDoc.data();
        console.log('Profile Debug - Raw Firestore data:', userData);
        
        // Convert Firestore Timestamp to number for createdAt/updatedAt
        const profileData = {
          ...userData,
          id: user.uid,
          createdAt: userData.createdAt?.toMillis?.() || userData.createdAt || Date.now(),
          updatedAt: userData.updatedAt?.toMillis?.() || userData.updatedAt || Date.now(),
        } as ExtendedUserProfile;
        
        console.log('Profile Debug - Processed profile data:', profileData);
        console.log('Profile Debug - Hybrid Style Name:', profileData.hybridStyleName);
        console.log('Profile Debug - Style Preferences:', profileData.stylePreferences);
        console.log('Profile Debug - Legacy Preferences:', profileData.preferences?.style);
        console.log('Profile Debug - Style Preferences Length:', profileData.stylePreferences?.length);
        console.log('Profile Debug - Legacy Preferences Length:', profileData.preferences?.style?.length);
        
        setProfile(profileData);
      } else {
        console.log('Profile Debug - No user document found');
        setProfile(null);
      }
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast({
        title: "Error",
        description: "Failed to load profile data",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
              router.push('/signin');
      return;
    }

    fetchProfile();
  }, [user, authLoading, router, toast]);

  const handleReonboard = () => {
    resetOnboarding();
    router.push('/onboarding');
  };

  const handleStartEdit = () => {
    setEditName(profile?.name || '');
    setEditing(true);
  };

  const handleCancelEdit = () => {
    setEditing(false);
    setEditName('');
  };

  const handleSaveEdit = async () => {
    if (!profile || !user) return;
    
    try {
      // Update the profile in Firestore
      const userRef = doc(db, 'users', user.uid);
      await updateDoc(userRef, {
        name: editName,
        updatedAt: new Date().toISOString()
      });
      
      // Update local state
      setProfile({
        ...profile,
        name: editName,
        updatedAt: Date.now()
      });
      
      setEditing(false);
      setEditName('');
      
      toast({
        title: "Profile Updated",
        description: "Your name has been updated successfully.",
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        title: "Error",
        description: "Failed to update profile",
        variant: "destructive",
      });
    }
  };



  const formatSkinTone = (skinTone: string | { depth: string; undertone: string } | undefined) => {
    if (typeof skinTone === 'string') return skinTone;
    if (skinTone?.depth && skinTone?.undertone) {
      return `${skinTone.depth} ${skinTone.undertone}`;
    }
    return 'Not specified';
  };

  // Fallback: Generate a hybrid style name from style preferences if missing
  const getFallbackHybridStyleName = (profile: ExtendedUserProfile) => {
    if (profile.hybridStyleName && profile.hybridStyleName.trim() !== '') {
      return profile.hybridStyleName;
    }
    
    // Try to generate from style preferences
    if (profile.stylePreferences && profile.stylePreferences.length > 0) {
      const topStyles = profile.stylePreferences.slice(0, 2);
      if (topStyles.length >= 2) {
        return `${topStyles[0]} ${topStyles[1]}`;
      } else if (topStyles.length === 1) {
        return topStyles[0];
      }
    }
    
    // Try legacy preferences
    if (profile.preferences?.style && profile.preferences.style.length > 0) {
      const topStyles = profile.preferences.style.slice(0, 2);
      if (topStyles.length >= 2) {
        return `${topStyles[0]} ${topStyles[1]}`;
      } else if (topStyles.length === 1) {
        return topStyles[0];
      }
    }
    
    return 'Personal Style';
  };

  if (authLoading || loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-4xl mx-auto p-6">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
          </div>
        </Card>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="max-w-2xl mx-auto p-6">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold">Profile Not Found</h1>
            <p className="text-muted-foreground">
              It seems you haven't completed your profile yet.
            </p>
            <Button onClick={handleReonboard}>
              Complete Your Profile
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="max-w-4xl mx-auto p-6">
        <div className="space-y-8">
          {/* Profile Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-20 w-20">
                <AvatarImage src={profile.selfieUrl} />
                <AvatarFallback>
                  <User className="h-8 w-8" />
                </AvatarFallback>
              </Avatar>
              <div>
                {editing ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="text-3xl font-bold h-12 text-2xl"
                        placeholder="Enter your name"
                      />
                      <Button onClick={handleSaveEdit} size="sm" className="h-8 w-8 p-0">
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button onClick={handleCancelEdit} size="sm" variant="outline" className="h-8 w-8 p-0">
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center gap-2">
                    <h1 className="text-3xl font-bold">{profile.name || 'Your Profile'}</h1>
                    <Button onClick={handleStartEdit} size="sm" variant="ghost" className="h-8 w-8 p-0">
                      <Edit3 className="h-4 w-4" />
                    </Button>
                  </div>
                )}
                <p className="text-xl font-semibold text-purple-600 mb-2">
                  {getFallbackHybridStyleName(profile)}
                </p>
                <p className="text-muted-foreground flex items-center gap-2">
                  <span>{profile.gender || 'Not specified'}</span>
                  <span>•</span>
                  <span>{profile.heightFeetInches || profile.measurements?.height || 'N/A'}"</span>
                  <span>•</span>
                  <span>{profile.weight || profile.measurements?.weight || 'N/A'} lbs</span>
                </p>
              </div>
            </div>
            <Button onClick={handleReonboard} variant="outline" className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4" />
              Update Profile
            </Button>
          </div>

          <Separator />

          {/* Style Preferences */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Heart className="h-6 w-6" />
              Style Preferences
            </h2>
            <div className="flex flex-wrap gap-2">
              {/* Show new style preferences first */}
              {profile.stylePreferences?.length ? (
                profile.stylePreferences.map((preference) => (
                  <Badge key={preference} variant="outline">
                    {preference}
                  </Badge>
                ))
              ) : profile.preferences?.style?.length ? (
                /* Show legacy style preferences if no new ones */
                profile.preferences.style.map((preference) => (
                  <Badge key={preference} variant="outline">
                    {preference}
                  </Badge>
                ))
              ) : (
                /* Show debug info when no preferences found */
                <div className="text-sm text-muted-foreground">
                  No style preferences found. Debug: 
                  stylePreferences length: {profile.stylePreferences?.length || 0}, 
                  legacy preferences length: {profile.preferences?.style?.length || 0}
                </div>
              )}
            </div>
          </div>

          {/* Measurements */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <Ruler className="h-6 w-6" />
              Measurements & Sizes
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium">Basic Info</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Height:</span>
                    <span>{profile.heightFeetInches || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Weight:</span>
                    <span>{profile.weight || 'Not specified'} lbs</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Body Type:</span>
                    <span>{profile.bodyType || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Skin Tone:</span>
                    <span>{formatSkinTone(profile.skinTone)}</span>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Clothing Sizes</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Top Size:</span>
                    <span>{profile.topSize || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Bottom Size:</span>
                    <span>{profile.bottomSize || 'Not specified'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Shoe Size:</span>
                    <span>{profile.shoeSize || 'Not specified'}</span>
                  </div>
                  {profile.dressSize && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Dress Size:</span>
                      <span>{profile.dressSize}</span>
                    </div>
                  )}
                  {profile.jeanWaist && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Jean Waist:</span>
                      <span>{profile.jeanWaist}</span>
                    </div>
                  )}
                  {profile.braSize && (
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Bra Size:</span>
                      <span>{profile.braSize}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                <h3 className="font-medium">Fit Preferences</h3>
                <div className="space-y-2">
                  {profile.fitPreferences?.length ? (
                    <div className="flex flex-wrap gap-2">
                      {profile.fitPreferences.map((fit) => (
                        <Badge key={fit} variant="outline" className="capitalize">
                          {fit}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <span className="text-muted-foreground">Not specified</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Quiz Responses */}
          {profile.quizResponses?.length && (
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold flex items-center gap-2">
                <Star className="h-6 w-6" />
                Style Quiz Responses
              </h2>
              
              <div className="space-y-4">
                {profile.quizResponses.map((response, index) => (
                  <div key={index} className="p-4 border rounded-lg">
                    <h3 className="font-medium mb-2">Question {index + 1}</h3>
                    <div className="space-y-2">
                      <p className="text-sm text-muted-foreground">Question ID: {response.questionId}</p>
                      <p className="text-sm">
                        <span className="font-medium">Answer:</span> {
                          Array.isArray(response.answer) 
                            ? response.answer.join(', ') 
                            : response.answer
                        }
                      </p>
                      <p className="text-sm">
                        <span className="font-medium">Confidence:</span> {response.confidence}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Personal Information */}
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <User className="h-6 w-6" />
              Personal Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="font-medium">Contact Details</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Full Name:</span>
                    <span className="font-medium">{profile.name || 'Not provided'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Email:</span>
                    <span className="font-medium">{profile.email || 'Not provided'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Gender:</span>
                    <span className="font-medium capitalize">{profile.gender || 'Not specified'}</span>
                  </div>
                </div>
              </div>
              <div className="space-y-4">
                <h3 className="font-medium">Account Details</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created:</span>
                    <span>{profile.createdAt ? new Date(profile.createdAt).toLocaleDateString() : 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span>{profile.updatedAt ? new Date(profile.updatedAt).toLocaleDateString() : 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Profile Status:</span>
                    <Badge variant="outline" className="text-green-600 border-green-600">
                      Complete
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="pt-6 space-y-4">
            <Button
              onClick={handleReonboard}
              className="w-full"
              size="lg"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Update Profile
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
} 