'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User, Save, Palette, Heart, Settings } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import { useRouter } from 'next/navigation';
import InclusiveSizingGuide from '@/components/InclusiveSizingGuide';

console.log('🔍 DEBUG: Profile page file loaded');

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
  console.log('🔍 DEBUG: ProfilePage component rendered');
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<UserProfile>>({});

  useEffect(() => {
    console.log('🔍 DEBUG: useEffect triggered, user:', !!user, 'authLoading:', authLoading);
    if (user && !authLoading) {
      console.log('🔍 DEBUG: Calling fetchProfile');
      fetchProfile();
    }
  }, [user, authLoading]);

  const fetchProfile = async () => {
    try {
      console.log('🔍 DEBUG: fetchProfile called, user:', !!user);
      
      if (!user) {
        console.log('🔍 DEBUG: No user, setting error');
        setError('Please sign in to view your profile');
        setLoading(false);
        return;
      }

      setLoading(true);
      setError(null);
      
      // Get Firebase ID token for authentication
      console.log('🔍 DEBUG: Getting Firebase token...');
      const token = await user.getIdToken();
      console.log('🔍 DEBUG: Got token, length:', token.length);
      console.log('🔍 DEBUG: Token starts with:', token.substring(0, 20) + '...');
      
      // Decode token on client side to see what's in it
      try {
        const tokenParts = token.split('.');
        console.log('🔍 DEBUG: Client - Token parts count:', tokenParts.length);
        if (tokenParts.length === 3) {
          // Firebase tokens use URL-safe base64, so we need to convert it
          const base64Payload = tokenParts[1].replace(/-/g, '+').replace(/_/g, '/');
          // Add padding if needed
          const paddedPayload = base64Payload + '='.repeat((4 - base64Payload.length % 4) % 4);
          const payload = JSON.parse(atob(paddedPayload));
          console.log('🔍 DEBUG: Client - Token payload:', payload);
          console.log('🔍 DEBUG: Client - Available payload keys:', Object.keys(payload));
          console.log('🔍 DEBUG: Client - Email from token:', payload.email);
          console.log('🔍 DEBUG: Client - User ID from token:', payload.user_id || payload.sub);
        }
      } catch (tokenError) {
        console.log('🔍 DEBUG: Client - Could not decode token:', tokenError);
      }
      
      console.log('🔍 DEBUG: Making fetch request to /api/user/profile');
      const response = await fetch('/api/user/profile', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      console.log('🔍 DEBUG: Response status:', response.status);
      console.log('🔍 DEBUG: Response ok:', response.ok);
      
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
      console.log('🔍 DEBUG: Response data:', data);
      
      // Handle different response structures - backend returns data directly or nested under 'profile'
      const profileData = data.profile || data;
      console.log('🔍 DEBUG: Profile data being set:', profileData);
      console.log('🔍 DEBUG: Profile measurements:', profileData?.measurements);
      console.log('🔍 DEBUG: Profile stylePreferences:', profileData?.stylePreferences);
      
      setProfile(profileData);
      setFormData(profileData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profile');
    } finally {
      setLoading(false);
    }
  };

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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <Navigation />
      <div className="container mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold">My Profile</h1>
          <p className="text-muted-foreground">Manage your style preferences and personal information</p>
        </div>
        <Button onClick={() => setIsEditing(!isEditing)} variant={isEditing ? "outline" : "default"}>
          {isEditing ? "Cancel" : "Edit Profile"}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personal Information */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="h-5 w-5 mr-2" />
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Palette className="h-5 w-5 mr-2" />
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
                <p className="text-sm text-muted-foreground capitalize">{profile.stylePreferences?.[0]}</p>
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Measurements & Sizes
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Height</Label>
                <p className="text-sm text-muted-foreground">
                  {profile.measurements?.heightFeetInches || 'Not specified'}
                </p>
              </div>
              <div className="space-y-2">
                <Label>Weight</Label>
                <p className="text-sm text-muted-foreground">
                  {profile.measurements?.weight ? `${profile.measurements.weight} lbs` : 'Not specified'}
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

        {/* Inclusive Sizing Guide */}
        <InclusiveSizingGuide />

        {/* Style Quiz Responses */}
        {profile.preferences?.style && profile.preferences.style.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Heart className="h-5 w-5 mr-2" />
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
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
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
                {new Date(profile.createdAt || profile.created_at || '').toLocaleDateString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Last Updated</span>
              <span className="text-sm text-muted-foreground">
                {new Date(profile.updatedAt || profile.updated_at || '').toLocaleDateString()}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Heart className="h-5 w-5 mr-2" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              <Palette className="h-4 w-4 mr-2" />
              Style Quiz
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
        <div className="mt-6 flex justify-end space-x-3">
          <Button variant="outline" onClick={() => setIsEditing(false)}>
            Cancel
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      )}
      </div>
    </div>
  );
}

