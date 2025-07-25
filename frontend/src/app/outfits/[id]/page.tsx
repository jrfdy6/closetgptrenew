"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, RefreshCw, Star, ThumbsUp, ThumbsDown, AlertTriangle, Calendar, Eye, Edit3, X, Plus, Save, RotateCcw, CheckCircle, Sparkles } from "lucide-react";
import Link from "next/link";
import { authenticatedFetch } from '@/lib/utils/auth';
import { OutfitFeedback } from '@/components/OutfitFeedback';
import { OutfitWarnings } from '@/components/ui/OutfitWarnings';
import { useFirebase } from '@/lib/firebase-context';
import { useWardrobe } from '@/hooks/useWardrobe';

interface Outfit {
  id: string;
  occasion: string;
  mood: string;
  style: string;
  description?: string;
  createdAt: string | number;
  items: Array<{
    id: string;
    itemId?: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  pieces?: Array<{
    itemId: string;
    name: string;
    type: string;
    reason: string;
    dominantColors: string[];
    style: string[];
    occasion: string[];
    imageUrl: string;
  }>;
  feedback_summary?: {
    total_feedback: number;
    likes: number;
    dislikes: number;
    issues: number;
    average_rating: number;
    issue_categories?: Record<string, number>;
  };
  warnings?: string[];
  validationErrors?: string[];
  validation_details?: {
    errors?: string[];
    warnings?: string[];
    fixes?: Array<{
      method: string;
      original_error: string;
      applied: boolean;
    }>;
  };
  wasSuccessful?: boolean;
  is_edited?: boolean;
}

export default function OutfitDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useFirebase();
  const { wardrobe } = useWardrobe();
  
  const [outfit, setOutfit] = useState<Outfit | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedbackSummary, setFeedbackSummary] = useState<any>(null);
  
  // Editing state - always start in edit mode
  const [isEditing, setIsEditing] = useState(true);
  const [editedOutfit, setEditedOutfit] = useState<Outfit | null>(null);
  const [saving, setSaving] = useState(false);
  const [showItemSelector, setShowItemSelector] = useState<string | null>(null); // item ID being replaced
  
  // Wear tracking state
  const [wearCount, setWearCount] = useState<number>(0);
  const [isWearing, setIsWearing] = useState(false);
  const [showWearSuccess, setShowWearSuccess] = useState(false);
  const [wearHistory, setWearHistory] = useState<Array<{date: string, note?: string}>>([]);

  useEffect(() => {
    const fetchOutfit = async () => {
      try {
        setLoading(true);
        const outfitId = params.id as string;
        
        // Fetch outfit details
        const outfitResponse = await authenticatedFetch(`/api/outfit/${outfitId}`);
        if (!outfitResponse.ok) {
          throw new Error('Failed to fetch outfit');
        }
        const outfitData = await outfitResponse.json();
        setOutfit(outfitData);
        // Initialize edited outfit for immediate editing
        setEditedOutfit({ ...outfitData });
        
        // Fetch feedback summary
        try {
          const feedbackResponse = await authenticatedFetch(`/api/feedback/outfit/${outfitId}/summary`);
          if (feedbackResponse.ok) {
            const feedbackData = await feedbackResponse.json();
            setFeedbackSummary(feedbackData.data);
          }
        } catch (error) {
          console.warn('Failed to fetch feedback summary:', error);
        }
        
        // Fetch wear data
        try {
          await fetchWearData();
        } catch (error) {
          console.warn('Failed to fetch wear data:', error);
        }
        
      } catch (err) {
        console.error('Error fetching outfit:', err);
        setError('Failed to load outfit');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchOutfit();
    }
  }, [params.id]);

  const formatDate = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getFeedbackIcon = (type: string) => {
    switch (type) {
      case 'like': return <ThumbsUp className="w-4 h-4 text-green-500" />;
      case 'dislike': return <ThumbsDown className="w-4 h-4 text-red-500" />;
      case 'issue': return <AlertTriangle className="w-4 h-4 text-orange-500" />;
      default: return null;
    }
  };

  const getFeedbackColor = (type: string) => {
    switch (type) {
      case 'like': return "bg-green-100 text-green-800";
      case 'dislike': return "bg-red-100 text-red-800";
      case 'issue': return "bg-orange-100 text-orange-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  // Editing functions
  const startEditing = () => {
    setEditedOutfit({ ...outfit! });
    setIsEditing(true);
  };

  const cancelEditing = () => {
    // Reset to original outfit but stay in edit mode
    setEditedOutfit({ ...outfit! });
    setShowItemSelector(null);
  };

  const removeItem = (itemId: string) => {
    if (!editedOutfit) return;
    setEditedOutfit({
      ...editedOutfit,
      // Remove from items array (for backend validation)
      items: editedOutfit.items.filter(item => item.id !== itemId),
      // Remove from pieces array (for frontend display)
      pieces: editedOutfit.pieces?.filter(piece => piece.itemId !== itemId) || []
    });
  };

  const replaceItem = (oldItemId: string, newItem: any) => {
    if (!editedOutfit) return;
    
    // Find the wardrobe item to get full details
    const wardrobeItem = wardrobe.find(item => item.id === newItem.id);
    if (!wardrobeItem) return;
    
    // Create a piece object with full details
    const newPiece = {
      itemId: wardrobeItem.id,
      name: wardrobeItem.name,
      type: wardrobeItem.type,
      reason: "Replaced item",
      dominantColors: wardrobeItem.metadata?.colorAnalysis?.dominant || [],
      style: wardrobeItem.style || [],
      occasion: wardrobeItem.occasion || [],
      imageUrl: wardrobeItem.imageUrl || ""
    };
    
    setEditedOutfit({
      ...editedOutfit,
      pieces: editedOutfit.pieces?.map(piece => 
        piece.itemId === oldItemId ? newPiece : piece
      ) || [newPiece]
    });
    setShowItemSelector(null);
  };

  const addItem = (newItem: any) => {
    if (!editedOutfit) return;
    
    // Find the wardrobe item to get full details
    const wardrobeItem = wardrobe.find(item => item.id === newItem.id);
    if (!wardrobeItem) return;
    
    // Create a piece object with full details
    const newPiece = {
      itemId: wardrobeItem.id,
      name: wardrobeItem.name,
      type: wardrobeItem.type,
      reason: "Added item",
      dominantColors: wardrobeItem.metadata?.colorAnalysis?.dominant || [],
      style: wardrobeItem.style || [],
      occasion: wardrobeItem.occasion || [],
      imageUrl: wardrobeItem.imageUrl || ""
    };
    
    setEditedOutfit({
      ...editedOutfit,
      pieces: [...(editedOutfit.pieces || []), newPiece]
    });
  };

  const saveChanges = async () => {
    if (!editedOutfit || !user) return;
    
    try {
      setSaving(true);
      
      // Extract only the item IDs for the backend
      const itemIds = (editedOutfit.pieces || editedOutfit.items || []).map(item => {
        if (typeof item === 'string') return item;
        // Check if it's a piece (has itemId) or item (has id)
        return 'itemId' in item ? item.itemId : item.id;
      });
      
      const response = await authenticatedFetch(`/api/outfit/${outfit!.id}/update`, {
        method: 'PUT',
        body: JSON.stringify({
          name: `${outfit!.occasion} Outfit`,
          occasion: outfit!.occasion,
          style: outfit!.style,
          description: outfit!.description || "",
          items: itemIds,
          is_edited: true
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save changes');
      }

      const updatedOutfit = await response.json();
      setOutfit(updatedOutfit);
      // Keep in edit mode after saving
      setEditedOutfit({ ...updatedOutfit });
      setShowItemSelector(null);
    } catch (error) {
      console.error('Error saving changes:', error);
      alert('Failed to save changes. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const getItemsByType = (type: string) => {
    return wardrobe.filter(item => item.type === type);
  };

  // Wear tracking functions - using existing outfit-history system
  const markAsWorn = async (note?: string) => {
    if (!outfit || isWearing) return;
    
    setIsWearing(true);
    try {
      // Use the existing outfit-history endpoint that dashboard uses
      const response = await authenticatedFetch('/api/outfit-history/mark-worn', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          outfitId: outfit.id,
          dateWorn: new Date().toISOString().split('T')[0], // Today's date
          occasion: outfit.occasion,
          mood: outfit.mood,
          notes: note || '',
          weather: {}
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setShowWearSuccess(true);
        
        // Refresh wear data
        await fetchWearData();
        
        // Hide success message after 3 seconds
        setTimeout(() => setShowWearSuccess(false), 3000);
      } else {
        console.error('Failed to mark outfit as worn');
      }
    } catch (error) {
      console.error('Error marking outfit as worn:', error);
    } finally {
      setIsWearing(false);
    }
  };

  const fetchWearData = async () => {
    if (!outfit) return;
    
    try {
      // Get outfit history entries for this outfit
      const response = await authenticatedFetch(`/api/outfit-history?outfit_id=${outfit.id}&limit=10`);
      if (response.ok) {
        const data = await response.json();
        const history = data.outfitHistory || [];
        
        setWearCount(history.length);
        setWearHistory(history.map((entry: any) => ({
          date: new Date(entry.dateWorn).toLocaleDateString(),
          note: entry.notes,
          occasion: entry.occasion,
          mood: entry.mood
        })));
      }
    } catch (error) {
      console.warn('Failed to fetch wear data:', error);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button variant="outline" disabled>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          </div>
          <div className="lg:col-span-1">
            <Card className="animate-pulse">
              <CardHeader>
                <div className="h-5 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    );
  }

  if (error || !outfit) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button variant="outline" onClick={() => router.back()}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </div>
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Error</h1>
          <p className="text-red-600">{error || 'Outfit not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center gap-4 mb-8">
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div className="flex-1">
          <h1 className="text-2xl font-bold">{outfit.occasion} Outfit</h1>
          <p className="text-muted-foreground">
            Created {formatDate(typeof outfit.createdAt === 'string' ? parseInt(outfit.createdAt) : outfit.createdAt)}
            {outfit.is_edited && (
              <span className="ml-2 text-blue-600 text-sm">• Edited</span>
            )}
            <span className="ml-2 text-orange-600 text-sm">• Ready to Edit</span>
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={cancelEditing}
            variant="outline"
            disabled={saving}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Cancel
          </Button>
          <Button 
            onClick={saveChanges}
            disabled={saving}
          >
            <Save className="w-4 h-4 mr-2" />
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Outfit Details */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-xl">{outfit.occasion} Outfit</CardTitle>
                  <CardDescription>
                    {outfit.mood} • {outfit.style}
                  </CardDescription>
                </div>
                
                {/* Feedback Summary Badge */}
                {feedbackSummary && feedbackSummary.total_feedback > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="font-medium">
                        {feedbackSummary.average_rating.toFixed(1)}
                      </span>
                    </div>
                    <Badge variant="secondary">
                      {feedbackSummary.total_feedback} feedback
                    </Badge>
                  </div>
                )}
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="space-y-6">
                {/* NEW: Display warnings and validation details */}
                <OutfitWarnings
                  warnings={outfit.warnings}
                  validationErrors={outfit.validationErrors}
                  validationDetails={outfit.validation_details}
                  wasSuccessful={outfit.wasSuccessful}
                />

                {/* Outfit Metadata */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <div>
                      <div className="font-medium">Occasion</div>
                      <div className="text-sm text-muted-foreground">{outfit.occasion}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Eye className="w-4 h-4 text-muted-foreground" />
                    <div>
                      <div className="font-medium">Mood</div>
                      <div className="text-sm text-muted-foreground">{outfit.mood}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Star className="w-4 h-4 text-muted-foreground" />
                    <div>
                      <div className="font-medium">Style</div>
                      <div className="text-sm text-muted-foreground">{outfit.style}</div>
                    </div>
                  </div>
                </div>
                
                {outfit.description && (
                  <div>
                    <h3 className="font-semibold mb-2">Description</h3>
                    <p className="text-muted-foreground">{outfit.description}</p>
                  </div>
                )}

                {/* Wear This Outfit Section */}
                <div className="border-t pt-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h3 className="font-semibold text-lg">Wear This Outfit</h3>
                      <p className="text-sm text-muted-foreground">
                        {wearCount === 0 
                          ? "Tap 'Wear Now' to help your closet get smarter! We'll track your style journey and optimize for variety, climate, and favorites."
                          : `You've worn this ${wearCount} time${wearCount > 1 ? 's' : ''}. Help us track your unique style journey!`
                        }
                      </p>
                    </div>
                    {wearCount > 0 && (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" />
                        {wearCount} worn
                      </Badge>
                    )}
                  </div>

                  {/* Wear Success Message */}
                  {showWearSuccess && (
                    <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-center gap-3 animate-in slide-in-from-top-2">
                      <Sparkles className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium text-green-800">
                          {wearCount === 1 
                            ? "First time wearing this! 🎉"
                            : `Worn ${wearCount} times! ✨`
                          }
                        </p>
                        <p className="text-sm text-green-700">
                          We'll track this for smarter style tips and recommendations.
                        </p>
                      </div>
                    </div>
                  )}

                  {/* Wear Button */}
                  <div className="flex gap-3">
                    <Button
                      onClick={() => markAsWorn()}
                      disabled={isWearing}
                      className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium py-3"
                    >
                      {isWearing ? (
                        <>
                          <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                          Marking as Worn...
                        </>
                      ) : (
                        <>
                          <CheckCircle className="w-4 h-4 mr-2" />
                          {wearCount === 0 ? 'Wear Now' : 'Wear Again'}
                        </>
                      )}
                    </Button>
                    
                    {/* Optional: Add Note Button */}
                    <Button
                      onClick={() => {
                        const note = prompt('Add a note about wearing this outfit (optional):\n\nWhere did you wear it? How did it feel? Weather?');
                        if (note !== null) {
                          markAsWorn(note);
                        }
                      }}
                      variant="outline"
                      disabled={isWearing}
                      className="px-4"
                    >
                      Add Note
                    </Button>
                  </div>

                  {/* Wear History */}
                  {wearHistory.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium mb-2 text-sm text-muted-foreground">Recent Wears</h4>
                      <div className="space-y-2">
                        {wearHistory.slice(0, 3).map((wear, index) => (
                          <div key={index} className="flex items-center gap-2 text-sm">
                            <Calendar className="w-3 h-3 text-muted-foreground" />
                            <span className="text-muted-foreground">
                              {new Date(wear.date).toLocaleDateString()}
                            </span>
                            {wear.note && (
                              <span className="text-muted-foreground">• {wear.note}</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {/* Feedback Summary */}
                {feedbackSummary && feedbackSummary.total_feedback > 0 && (
                  <div className="border-t pt-6">
                    <h3 className="font-semibold mb-4">Feedback Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-3 bg-green-50 rounded-lg">
                        <div className="flex items-center justify-center gap-1 mb-1">
                          <ThumbsUp className="w-4 h-4 text-green-500" />
                          <span className="font-semibold text-green-700">{feedbackSummary.likes}</span>
                        </div>
                        <div className="text-xs text-green-600">Likes</div>
                      </div>
                      <div className="text-center p-3 bg-red-50 rounded-lg">
                        <div className="flex items-center justify-center gap-1 mb-1">
                          <ThumbsDown className="w-4 h-4 text-red-500" />
                          <span className="font-semibold text-red-700">{feedbackSummary.dislikes}</span>
                        </div>
                        <div className="text-xs text-red-600">Dislikes</div>
                      </div>
                      {feedbackSummary.issues > 0 && (
                        <div className="text-center p-3 bg-orange-50 rounded-lg">
                          <div className="flex items-center justify-center gap-1 mb-1">
                            <AlertTriangle className="w-4 h-4 text-orange-500" />
                            <span className="font-semibold text-orange-700">{feedbackSummary.issues}</span>
                          </div>
                          <div className="text-xs text-orange-600">Issues</div>
                        </div>
                      )}
                      <div className="text-center p-3 bg-blue-50 rounded-lg">
                        <div className="flex items-center justify-center gap-1 mb-1">
                          <Star className="w-4 h-4 text-blue-500" />
                          <span className="font-semibold text-blue-700">
                            {feedbackSummary.average_rating.toFixed(1)}
                          </span>
                        </div>
                        <div className="text-xs text-blue-600">Avg Rating</div>
                      </div>
                    </div>
                    
                    {/* Issue Categories */}
                    {feedbackSummary.issue_categories && Object.keys(feedbackSummary.issue_categories).length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Issue Categories</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(feedbackSummary.issue_categories).map(([category, count]) => (
                            <Badge key={category} variant="outline" className="text-xs">
                              {category.replace(/_/g, ' ')}: {count as number}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Outfit Items */}
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold">
                      Items ({editedOutfit?.pieces?.length || outfit.pieces?.length || editedOutfit?.items?.length || outfit.items?.length || 0})
                    </h3>
                    <Button
                      onClick={() => setShowItemSelector('add-new')}
                      variant="outline"
                      size="sm"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Item
                    </Button>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {(editedOutfit?.pieces || outfit.pieces)?.map((piece, index) => (
                      <div key={piece.itemId || `piece-${index}`} className="border rounded-lg p-4 hover:shadow-md transition-shadow relative">
                        <div className="absolute top-2 right-2 flex gap-1 z-10">
                          <Button
                            onClick={() => setShowItemSelector(piece.itemId)}
                            variant="outline"
                            size="sm"
                            className="h-6 w-6 p-0 bg-white/90 hover:bg-white shadow-sm"
                          >
                            <Edit3 className="w-3 h-3" />
                          </Button>
                          <Button
                            onClick={() => removeItem(piece.itemId)}
                            variant="outline"
                            size="sm"
                            className="h-6 w-6 p-0 text-red-600 hover:text-red-700 bg-white/90 hover:bg-white shadow-sm"
                          >
                            <X className="w-3 h-3" />
                          </Button>
                        </div>
                        
                        {piece.imageUrl && (
                          <div className="mb-3 aspect-square overflow-hidden rounded-md relative">
                            <img
                              src={piece.imageUrl}
                              alt={piece.name}
                              className="object-cover w-full h-full"
                            />
                          </div>
                        )}
                        <div className="font-medium">{piece.name}</div>
                        <div className="text-sm text-gray-500 capitalize">{piece.type}</div>
                      </div>
                    ))}
                  </div>

                  {/* Item Selector Modal */}
                  {showItemSelector && isEditing && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                      <div className="bg-white rounded-lg p-6 max-w-2xl max-h-[80vh] overflow-y-auto">
                        <div className="flex items-center justify-between mb-4">
                          <h3 className="text-lg font-semibold">
                            {showItemSelector === 'add-new' ? 'Add New Item' : 'Replace Item'}
                          </h3>
                          <Button
                            onClick={() => setShowItemSelector(null)}
                            variant="outline"
                            size="sm"
                          >
                            <X className="w-4 h-4" />
                          </Button>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {wardrobe.map((wardrobeItem, index) => (
                            <div
                              key={wardrobeItem.id}
                              className="border rounded-lg p-3 cursor-pointer hover:bg-gray-50"
                              onClick={() => {
                                if (showItemSelector === 'add-new') {
                                  addItem({
                                    id: wardrobeItem.id,
                                    name: wardrobeItem.name,
                                    type: wardrobeItem.type,
                                    imageUrl: wardrobeItem.imageUrl
                                  });
                                } else {
                                  replaceItem(showItemSelector, {
                                    id: wardrobeItem.id,
                                    name: wardrobeItem.name,
                                    type: wardrobeItem.type,
                                    imageUrl: wardrobeItem.imageUrl
                                  });
                                }
                              }}
                            >
                              {wardrobeItem.imageUrl && (
                                <div className="mb-2 aspect-square overflow-hidden rounded-md">
                                  <img
                                    src={wardrobeItem.imageUrl}
                                    alt={wardrobeItem.name}
                                    className="object-cover w-full h-full"
                                  />
                                </div>
                              )}
                              <div className="font-medium text-sm">{wardrobeItem.name}</div>
                              <div className="text-xs text-gray-500 capitalize">{wardrobeItem.type}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Feedback Section */}
        <div className="lg:col-span-1">
          <OutfitFeedback 
            outfitId={outfit.id}
            onFeedbackSubmitted={() => {
              // Refresh feedback summary after submission
              const fetchFeedbackSummary = async () => {
                try {
                  const feedbackResponse = await authenticatedFetch(`/api/feedback/outfit/${outfit.id}/summary`);
                  if (feedbackResponse.ok) {
                    const feedbackData = await feedbackResponse.json();
                    setFeedbackSummary(feedbackData.data);
                  }
                } catch (error) {
                  console.warn('Failed to refresh feedback summary:', error);
                }
              };
              fetchFeedbackSummary();
            }}
          />
        </div>
      </div>
    </div>
  );
} 