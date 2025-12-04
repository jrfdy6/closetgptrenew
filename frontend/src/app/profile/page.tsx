'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { User, Save, Palette, Heart, Settings, Sparkles } from 'lucide-react';
import { useFirebase } from '@/lib/firebase-context';
import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { useRouter } from 'next/navigation';
import { getLinkedProviders, hasPasswordLinked, linkEmailPassword } from '@/lib/auth';
import { Lock, CheckCircle, XCircle } from 'lucide-react';
import SpendingRangesCard from '@/components/SpendingRangesCard';

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
  console.log('🔍 DEBUG: ProfilePage component rendered');
  const router = useRouter();
  const { user, loading: authLoading } = useFirebase();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState<Partial<UserProfile>>({});
  const [signInMethods, setSignInMethods] = useState<string[]>([]);
  const [isLinkingPassword, setIsLinkingPassword] = useState(false);
  const [linkPasswordEmail, setLinkPasswordEmail] = useState('');
  const [linkPasswordPassword, setLinkPasswordPassword] = useState('');
  const [linkPasswordError, setLinkPasswordError] = useState<string | null>(null);
  const [linkPasswordSuccess, setLinkPasswordSuccess] = useState(false);

  useEffect(() => {
    console.log('🔍 DEBUG: useEffect triggered, user:', !!user, 'authLoading:', authLoading);
    if (user && !authLoading) {
      console.log('🔍 DEBUG: Calling fetchProfile');
      fetchProfile();
    }
  }, [user, authLoading]);

  // Separate useEffect for sign-in methods to ensure it runs after user is set
  useEffect(() => {
    if (user && !authLoading) {
      // Get providers directly from user object
      const providers = user.providerData.map(provider => provider.providerId);
      console.log('🔍 DEBUG: Sign-in methods from user:', providers);
      console.log('🔍 DEBUG: User providerData:', user.providerData);
      setSignInMethods(providers);
    } else {
      setSignInMethods([]);
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
      console.log('🔍 DEBUG: Timestamp values:', {
        createdAt: profileData.createdAt,
        created_at: profileData.created_at,
        updatedAt: profileData.updatedAt,
        updated_at: profileData.updated_at
      });
      
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-[#1A1510] dark:via-[#1A1510] dark:to-[#1A1510]">
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-[#1A1510] dark:via-[#1A1510] dark:to-[#1A1510]">
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-[#1A1510] dark:via-[#1A1510] dark:to-[#1A1510]">
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
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-[#1A1510] dark:via-[#1A1510] dark:to-[#1A1510]">
        <Navigation />
      <div className="container mx-auto p-6">
          <div className="text-center">
            <User className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Profile Not Found</h2>
            <p className="text-muted-foreground mb-4">Please complete your profile setup</p>
            <Button onClick={() => router.push('/onboarding')}>Complete Style Quiz</Button>
          </div>
        </div>
      </div>
    );
  }

  // Check if profile is incomplete (missing key fields)
  const isProfileIncomplete = !profile.measurements || !profile.stylePreferences || 
    (Array.isArray(profile.stylePreferences) && profile.stylePreferences.length === 0);
  
  if (isProfileIncomplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-[#1A1510] dark:via-[#1A1510] dark:to-[#1A1510]">
        <Navigation />
      <div className="container mx-auto p-8">
          <div className="max-w-2xl mx-auto">
            <Card className="border border-amber-200 dark:border-[#3D2F24]/70 bg-amber-50/50 dark:bg-[#2C2119]/85 backdrop-blur-sm">
              <CardHeader className="pb-6">
                <CardTitle className="flex items-center text-2xl font-serif text-amber-900 dark:text-amber-100">
                  <Sparkles className="h-8 w-8 mr-3 text-amber-600 dark:text-amber-400" />
                  Complete Your Style Profile
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <p className="text-[#57534E] dark:text-[#C4BCB4] text-lg leading-relaxed">
                    Your profile is incomplete! To get personalized outfit recommendations and make the most of Easy Outfit, 
                    please complete your style quiz.
                  </p>
                  
                  <div className="bg-white/85 dark:bg-[#2C2119]/85 rounded-2xl p-6 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 shadow-lg">
                    <h3 className="font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-4">Current profile status</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">Basic information</span>
                        <span className="text-[#4CAF50] dark:text-[#79E2A6] font-medium">✓ Complete</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">Style preferences</span>
                        <span className="text-[#FF9400] dark:text-amber-300 font-medium">
                          {profile.stylePreferences && Array.isArray(profile.stylePreferences) && profile.stylePreferences.length > 0 ? '✓ Complete' : '○ Incomplete'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">Measurements & sizes</span>
                        <span className="text-[#FF9400] dark:text-amber-300 font-medium">
                          {profile.measurements ? '✓ Complete' : '○ Incomplete'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-3 pt-4">
                    <Button 
                      onClick={() => router.push('/onboarding')}
                      className="flex-1 bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-6 py-3 rounded-2xl font-semibold transition-transform duration-200 hover:scale-[1.02] shadow-lg shadow-amber-500/20"
                    >
                      <Sparkles className="h-5 w-5 mr-2" />
                      Complete style quiz
                    </Button>
                    <Button 
                      variant="outline"
                      onClick={() => router.push('/dashboard')}
                      className="flex-1 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] px-6 py-3 rounded-2xl font-semibold transition-transform duration-200 hover:scale-[1.02]"
                    >
                      Back to dashboard
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF9] dark:bg-[#1A1510]">
      <Navigation />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 pb-24">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-12 bg-white/85 dark:bg-[#2C2119]/85 border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 rounded-3xl p-6 sm:p-8 backdrop-blur-xl shadow-lg">
        <div>
          <h1 className="text-4xl font-display font-semibold text-[#1C1917] dark:text-[#F8F5F1] mb-3">My profile</h1>
          <p className="text-[#57534E] dark:text-[#C4BCB4] text-base leading-relaxed">
            Tune your preferences so every look feels like you.
          </p>
        </div>
        <Button 
          onClick={() => setIsEditing(!isEditing)} 
          className={isEditing 
            ? "border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] px-6 py-3 rounded-2xl font-semibold transition-transform duration-200 hover:scale-[1.02]"
            : "bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-6 py-3 rounded-2xl font-semibold shadow-lg shadow-amber-500/20 transition-transform duration-200 hover:scale-[1.02] active:scale-[0.98]"
          }
        >
          {isEditing ? "Cancel" : "Edit profile"}
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Personal Information */}
        <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
              <User className="h-6 w-6 mr-3 text-[#FFB84C]" />
              Personal information
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
        <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
              <Palette className="h-6 w-6 mr-3 text-[#FFB84C]" />
              Style preferences
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
        <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
              <Settings className="h-6 w-6 mr-3 text-[#FFB84C]" />
              Measurements & sizes
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
          <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
            <CardHeader className="pb-6">
              <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
                <Heart className="h-6 w-6 mr-3 text-[#FFB84C]" />
                Style quiz responses
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Style preferences</Label>
                <div className="flex flex-wrap gap-2">
                  {profile.preferences.style.map((style, index) => (
                    <span key={index} className="px-3 py-1 rounded-full text-caption bg-[#FFF7E6] text-[#B45309]">
                      {style}
                    </span>
                  ))}
                </div>
              </div>
              {profile.preferences.colors && profile.preferences.colors.length > 0 && (
                <div className="space-y-2">
                  <Label>Color palette</Label>
                  <div className="flex flex-wrap gap-2">
                    {profile.preferences.colors.map((color, index) => (
                      <span key={index} className="px-3 py-1 rounded-full text-caption border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4]">
                        {color}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Spending Ranges */}
        <SpendingRangesCard />

        {/* Account Status */}
        <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
              <Settings className="h-6 w-6 mr-3 text-[#FFB84C]" />
              Account status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">Profile status</span>
              <span className="text-sm font-semibold text-[#4CAF50] dark:text-[#79E2A6]">Complete</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">Member since</span>
              <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
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
              <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">Last updated</span>
              <span className="text-sm text-[#57534E] dark:text-[#C4BCB4]">
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
            {user && (
              <div className="flex items-center justify-between pt-2 border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
                <span className="text-sm font-medium text-[#57534E] dark:text-[#C4BCB4]">Sign-in methods</span>
                <div className="flex items-center gap-2">
                  {signInMethods.length === 0 ? (
                    <span className="text-xs text-[#57534E] dark:text-[#C4BCB4]">Loading...</span>
                  ) : (
                    <>
                      {signInMethods.includes('google.com') && (
                        <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded">Google</span>
                      )}
                      {signInMethods.includes('password') ? (
                        <span className="text-xs px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded flex items-center gap-1">
                          <CheckCircle className="h-3 w-3" />
                          Password
                        </span>
                      ) : (
                        <span className="text-xs px-2 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded flex items-center gap-1">
                          <XCircle className="h-3 w-3" />
                          No password
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>
            )}
            {signInMethods.includes('google.com') && !signInMethods.includes('password') && (
              <div className="pt-4 border-t border-[#F5F0E8]/60 dark:border-[#3D2F24]/70">
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm text-[#57534E] dark:text-[#C4BCB4]">
                    <Lock className="h-4 w-4" />
                    <span>Link your password to sign in with email and password</span>
                  </div>
                  {linkPasswordSuccess ? (
                    <div className="p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                      <p className="text-sm text-green-700 dark:text-green-300">
                        Password successfully linked! You can now sign in with your email and password.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <div>
                        <Label htmlFor="link-email" className="text-xs text-[#57534E] dark:text-[#C4BCB4]">Email</Label>
                        <Input
                          id="link-email"
                          type="email"
                          value={linkPasswordEmail}
                          onChange={(e) => setLinkPasswordEmail(e.target.value)}
                          placeholder={user?.email || 'your@email.com'}
                          className="mt-1"
                          disabled={isLinkingPassword}
                        />
                      </div>
                      <div>
                        <Label htmlFor="link-password" className="text-xs text-[#57534E] dark:text-[#C4BCB4]">Password</Label>
                        <Input
                          id="link-password"
                          type="password"
                          value={linkPasswordPassword}
                          onChange={(e) => setLinkPasswordPassword(e.target.value)}
                          placeholder="Enter your password"
                          className="mt-1"
                          disabled={isLinkingPassword}
                        />
                      </div>
                      {linkPasswordError && (
                        <p className="text-xs text-red-600 dark:text-red-400">{linkPasswordError}</p>
                      )}
                      <Button
                        onClick={async () => {
                          if (!linkPasswordEmail || !linkPasswordPassword) {
                            setLinkPasswordError('Please enter both email and password');
                            return;
                          }
                          setIsLinkingPassword(true);
                          setLinkPasswordError(null);
                          setLinkPasswordSuccess(false);
                          const result = await linkEmailPassword(linkPasswordEmail, linkPasswordPassword);
                          if (result.success) {
                            setLinkPasswordSuccess(true);
                            setLinkPasswordPassword('');
                            const providers = getLinkedProviders();
                            setSignInMethods(providers);
                          } else {
                            setLinkPasswordError(result.error || 'Failed to link password');
                          }
                          setIsLinkingPassword(false);
                        }}
                        disabled={isLinkingPassword}
                        className="w-full text-sm"
                        size="sm"
                      >
                        {isLinkingPassword ? 'Linking...' : 'Link Password'}
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 bg-white/85 dark:bg-[#2C2119]/85 backdrop-blur-xl rounded-3xl shadow-lg">
          <CardHeader className="pb-6">
            <CardTitle className="flex items-center text-xl font-display text-[#1C1917] dark:text-[#F8F5F1]">
              <Heart className="h-6 w-6 mr-3 text-[#FFB84C]" />
              Quick actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button 
              variant="outline" 
              className="w-full justify-start border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]"
              onClick={() => router.push('/onboarding')}
            >
              <Palette className="h-4 w-4 mr-2" />
              Style quiz
            </Button>
            <Button 
              variant="outline" 
              className="w-full justify-start border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]"
              onClick={() => router.push('/style-persona')}
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Style persona
            </Button>
            <Button variant="outline" className="w-full justify-start border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]">
              <Heart className="h-4 w-4 mr-2" />
              Favorite items
            </Button>
            <Button variant="outline" className="w-full justify-start border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] hover:text-[#1C1917] dark:hover:text-[#F8F5F1]">
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
            className="border border-[#F5F0E8]/60 dark:border-[#3D2F24]/70 text-[#57534E] dark:text-[#C4BCB4] hover:text-[#1C1917] dark:hover:text-[#F8F5F1] hover:bg-[#F5F0E8] dark:hover:bg-[#2C2119] px-8 py-3 rounded-2xl font-semibold transition-transform duration-200 hover:scale-[1.02]"
          >
            Cancel
          </Button>
          <Button 
            onClick={handleSave}
            className="bg-gradient-to-r from-[#FFB84C] to-[#FF9400] text-[#1A1510] dark:text-white px-8 py-3 rounded-2xl font-semibold transition-transform duration-200 hover:scale-[1.02] shadow-lg shadow-amber-500/20"
          >
            <Save className="h-5 w-5 mr-3" />
            Save changes
          </Button>
        </div>
      )}

      </div>
      
      {/* Client-Only Navigation - No Props to Avoid Serialization */}
      <ClientOnlyNav />
    </div>
  );
}

