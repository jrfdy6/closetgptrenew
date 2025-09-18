'use client';

import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User, Save, Palette, Heart, Settings, Sparkles } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import { useRouter } from 'next/navigation';


interface UserProfile {
  id?: string;
  userId?: string;
  name: string;
  email: string;
  gender?: string;
  
  // Style preferences
  stylePreferences?: string[];
  preferences?: {
    style: string[];
    colors: string[];
    occasions: string[];
  };
  
  // Measurements
  measurements?: {
    height?: number;
    weight?: number;
    bodyType?: string;
    skinTone?: string;
    heightFeetInches?: string;
    topSize?: string;
    bottomSize?: string;
    shoeSize?: string;
    dressSize?: string;
    jeanWaist?: string;
    braSize?: string;
    inseam?: string;
    waist?: string;
    chest?: string;
    shoulderWidth?: number;
    waistWidth?: number;
    hipWidth?: number;
    armLength?: number;
    neckCircumference?: number;
    thighCircumference?: number;
    calfCircumference?: number;
  };
  
  // Body type and fit
  bodyType?: string;
  skinTone?: string;
  fitPreference?: string;
  sizePreference?: string;
  
  // Color preferences
  colorPalette?: {
    primary: string[];
    secondary: string[];
    accent: string[];
    neutral: string[];
    avoid: string[];
  };
  
  // Style personality scores
  stylePersonality?: {
    classic: number;
    modern: number;
    creative: number;
    minimal: number;
    bold: number;
  };
  
  // Style persona
  stylePersona?: {
    id: string;
    name: string;
    tagline: string;
    description: string;
    styleMission: string;
    traits: string[];
    examples: string[];
  };
  
  // Material preferences
  materialPreferences?: {
    preferred: string[];
    avoid: string[];
    seasonal: {
      spring: string[];
      summer: string[];
      fall: string[];
      winter: string[];
    };
  };
  
  // Fit preferences
  fitPreferences?: {
    tops: string;
    bottoms: string;
    dresses: string;
  };
  
  // Comfort levels
  comfortLevel?: {
    tight: number;
    loose: number;
    structured: number;
    relaxed: number;
  };
  
  // Brand preferences
  preferredBrands?: string[];
  
  // Budget preference
  budget?: string;
  
  // Timestamps
  createdAt?: number;
  updatedAt?: number;
  created_at?: string;
  updated_at?: string;
  
  // Legacy fields for backward compatibility
  onboardingCompleted?: boolean;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<UserProfile>>({});

  useEffect(() => {
    if (user && !authLoading) {
      fetchProfile();
    }
  }, [user, authLoading, fetchProfile]);

  const fetchProfile = useCallback(async () => {
    try {
      if (!user) {
        setError('Please sign in to view your profile');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      
      // Get Firebase ID token for authentication
      const token = await user.getIdToken();
      const response = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to view this profile.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }
      
      const data = await response.json();
      
      // Handle different response structures - backend returns data directly or nested under 'profile'
      const profileData = data.profile || data;
      
      // Ensure we have valid profile data before setting state
      if (profileData && typeof profileData === 'object') {
        setProfile(profileData);
        setFormData(profileData);
      } else {
        throw new Error('Invalid profile data received from server');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  }, [user]);

  const handleSave = async () => {
    try {
      if (!user) {
        setError('Please sign in to save your profile');
        return;
      }

      const token = await user.getIdToken();
      
      const response = await fetch('/api/user/profile', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Authentication failed. Please sign in again.');
        } else if (response.status === 403) {
          throw new Error('Access denied. You do not have permission to update this profile.');
        } else if (response.status >= 500) {
          throw new Error('Backend server error. Please try again later.');
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      }

      const data = await response.json();
      // Handle different response structures - backend returns data directly or nested under 'profile'
      const profileData = data.profile || data;
      setProfile(profileData);
      setFormData(profileData);
      setIsEditing(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">
                {authLoading ? 'Authenticating...' : 'Loading your profile...'}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <User className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Unable to Load Profile</h2>
            <p className="text-muted-foreground mb-4">{error}</p>
            <Button onClick={fetchProfile}>Try Again</Button>
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
            <User className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Authentication Required</h2>
            <p className="text-muted-foreground mb-4">Please sign in to view your profile</p>
          </div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Navigation />
        <div className="container mx-auto p-6">
          <div className="text-center">
            <User className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Profile Not Found</h2>
            <p className="text-muted-foreground mb-4">Please complete your profile setup</p>
            <Button onClick={() => setIsEditing(true)}>Create Profile</Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-stone-50 via-white to-stone-100 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      <div className="container mx-auto p-8">
      <div className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-serif font-bold text-stone-900 dark:text-stone-100 mb-4">My Profile</h1>
          <p className="text-stone-600 dark:text-stone-400 font-light text-lg">Manage your style preferences and personal information</p>
        </div>
        <Button 
          onClick={() => setIsEditing(!isEditing)} 
          variant={isEditing ? "outline" : "default"}
          className={isEditing ? "border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 px-6 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105" : "bg-stone-900 hover:bg-stone-800 text-white px-6 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105 shadow-lg"}
        >
          {isEditing ? "Cancel" : "Edit Profile"}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Personal Information */}
        <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
              <User className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
              Personal Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              {isEditing ? (
                <Input
                  id="name"
                  value={formData.name || ''}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              ) : (
                <p className="text-sm text-muted-foreground">{profile.name}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <p className="text-sm text-muted-foreground">{profile.email}</p>
            </div>
          </CardContent>
        </Card>

        {/* Style Preferences */}
        <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
              <Palette className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
              Style Preferences
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              {isEditing ? (
                <Select
                  value={formData.gender || ''}
                  onValueChange={(value) => setFormData({ ...formData, gender: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="unisex">Unisex</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <p className="text-sm text-muted-foreground capitalize">{profile.gender}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="style">Preferred Style</Label>
              {isEditing ? (
                <Select
                  value={formData.stylePreferences?.[0] || ''}
                  onValueChange={(value) => setFormData({
                    ...formData,
                    stylePreferences: [value]
                  })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Dark Academia">Dark Academia</SelectItem>
                    <SelectItem value="Y2K">Y2K</SelectItem>
                    <SelectItem value="Coastal Grandmother">Coastal Grandmother</SelectItem>
                    <SelectItem value="Clean Girl">Clean Girl</SelectItem>
                    <SelectItem value="Cottagecore">Cottagecore</SelectItem>
                    <SelectItem value="Old Money">Old Money</SelectItem>
                    <SelectItem value="Streetwear">Streetwear</SelectItem>
                    <SelectItem value="Minimalist">Minimalist</SelectItem>
                    <SelectItem value="Boho">Boho</SelectItem>
                    <SelectItem value="Preppy">Preppy</SelectItem>
                    <SelectItem value="Grunge">Grunge</SelectItem>
                    <SelectItem value="Classic">Classic</SelectItem>
                    <SelectItem value="Techwear">Techwear</SelectItem>
                    <SelectItem value="Business Casual">Business Casual</SelectItem>
                    <SelectItem value="Romantic">Romantic</SelectItem>
                    <SelectItem value="Casual">Casual</SelectItem>
                  </SelectContent>
                </Select>
              ) : (
                <p className="text-sm text-muted-foreground capitalize">
                  {profile.stylePersona?.name || profile.stylePreferences?.[0] || 'Not specified'}
                </p>
              )}
            </div>
            {profile.stylePreferences && profile.stylePreferences.length > 1 && (
              <div className="space-y-2">
                <Label>Additional Styles</Label>
                <div className="flex flex-wrap gap-2">
                  {profile.stylePreferences.slice(1).map((style, index) => (
                    <span key={index} className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs">
                      {style}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Measurements & Sizes */}
        <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
              <Settings className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
              Measurements & Sizes
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Height</Label>
                <p className="text-sm text-muted-foreground">
                  {profile.height || profile.measurements?.height || profile.measurements?.heightFeetInches || 'Not specified'}
                </p>
              </div>
              <div className="space-y-2">
                <Label>Weight</Label>
                <p className="text-sm text-muted-foreground">
                  {profile.weight || profile.measurements?.weight || 'Not specified'}
                </p>
              </div>
              <div className="space-y-2">
                <Label>Body Type</Label>
                <p className="text-sm text-muted-foreground capitalize">
                  {profile.measurements?.bodyType || 'Not specified'}
                </p>
              </div>
              <div className="space-y-2">
                <Label>Skin Tone</Label>
                <p className="text-sm text-muted-foreground capitalize">
                  {profile.measurements?.skinTone || 'Not specified'}
                </p>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-sm">Clothing Sizes</h4>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs">Top Size</Label>
                  <p className="text-sm text-muted-foreground">
                    {profile.measurements?.topSize || 'Not specified'}
                  </p>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Bottom Size</Label>
                  <p className="text-sm text-muted-foreground">
                    {profile.measurements?.bottomSize || 'Not specified'}
                  </p>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Shoe Size</Label>
                  <p className="text-sm text-muted-foreground">
                    {profile.measurements?.shoeSize || 'Not specified'}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Style Quiz Responses */}
        {profile.preferences?.style && profile.preferences.style.length > 0 && (
          <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
            <CardHeader className="pb-6">
              <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
                <Heart className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
                Style Quiz Responses
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Style Preferences</Label>
                <div className="flex flex-wrap gap-2">
                  {profile.preferences.style.map((style, index) => (
                    <span key={index} className="px-2 py-1 bg-primary/10 text-primary rounded-md text-xs">
                      {style}
                    </span>
                  ))}
                </div>
              </div>
              {profile.preferences.colors && profile.preferences.colors.length > 0 && (
                <div className="space-y-2">
                  <Label>Color Preferences</Label>
                  <div className="flex flex-wrap gap-2">
                    {profile.preferences.colors.map((color, index) => (
                      <span key={index} className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-xs">
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Account Status */}
        <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
              <Settings className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
              Account Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Profile Status</span>
              <span className="text-sm text-green-600 font-medium">Complete</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Member Since</span>
              <span className="text-sm text-muted-foreground">
                {(() => {
                  // Prioritize created_at over createdAt since created_at is the newer field
                  const timestamp = profile.created_at || profile.createdAt || 0;
                  // created_at is always Unix timestamp in seconds, so multiply by 1000
                  // createdAt might be in milliseconds, so check if it's very large
                  const date = timestamp > 1000000000000 ? new Date(timestamp) : new Date(timestamp * 1000);
                  return date.toLocaleDateString();
                })()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Last Updated</span>
              <span className="text-sm text-muted-foreground">
                {(() => {
                  // Prioritize updated_at over updatedAt since updated_at is the newer field
                  const timestamp = profile.updated_at || profile.updatedAt || 0;
                  // updated_at is always Unix timestamp in seconds, so multiply by 1000
                  // updatedAt might be in milliseconds, so check if it's very large
                  const date = timestamp > 1000000000000 ? new Date(timestamp) : new Date(timestamp * 1000);
                  return date.toLocaleDateString();
                })()}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border border-stone-200 dark:border-stone-700 bg-white/50 dark:bg-stone-900/50 backdrop-blur-sm">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-serif text-stone-900 dark:text-stone-100">
              <Heart className="h-6 w-6 mr-3 text-stone-600 dark:text-stone-400" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => router.push('/onboarding')}
            >
              <Palette className="h-4 w-4 mr-2" />
              Style Quiz
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start"
              onClick={() => router.push('/style-persona')}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Style Persona
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Heart className="h-4 w-4 mr-2" />
              Favorite Items
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Settings className="h-4 w-4 mr-2" />
              Preferences
            </Button>
          </CardContent>
        </Card>
      </div>

      {isEditing && (
        <div className="mt-12 flex justify-end space-x-4">
          <Button 
            variant="outline" 
            onClick={() => setIsEditing(false)}
            className="border-2 border-stone-300 hover:border-stone-400 text-stone-700 hover:text-stone-900 hover:bg-stone-50 px-8 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            className="bg-stone-900 hover:bg-stone-800 text-white px-8 py-3 rounded-full font-medium transition-all duration-300 hover:scale-105 shadow-lg"
          >
            <Save className="h-5 w-5 mr-3" />
            Save Changes
          </Button>
        </div>
      )}

      </div>
    </div>
  );
}

