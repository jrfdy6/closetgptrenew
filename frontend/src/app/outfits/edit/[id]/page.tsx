"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useWardrobe } from "@/hooks/useWardrobe";
import { useAuth } from "@/hooks/useAuth";
import { authenticatedFetch } from "@/lib/utils/auth";
import { WardrobeItem } from "@/types/wardrobe";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Plus, X, Search, Filter, Save, RotateCcw } from "lucide-react";
import Image from "next/image";
import { useToast } from "@/components/ui/use-toast";

const OCCASIONS = [
  "Casual", "Business Casual", "Formal", "Gala", "Party", "Date Night", "Work", "Interview", "Brunch", "Wedding Guest", "Cocktail", "Travel", "Airport", "Loungewear", "Beach", "Vacation", "Festival", "Rainy Day", "Snow Day", "Hot Weather", "Cold Weather", "Night Out", "Athletic / Gym", "School", "Holiday", "Concert", "Errands", "Chilly Evening", "Museum / Gallery", "First Date", "Business Formal", "Funeral / Memorial", "Fashion Event", "Outdoor Gathering"
];

const STYLES = [
  "Dark Academia", "Old Money", "Streetwear", "Y2K", "Minimalist", "Boho", "Preppy", "Grunge", "Classic", "Techwear", "Androgynous", "Coastal Chic", "Business Casual", "Avant-Garde", "Cottagecore", "Edgy", "Athleisure", "Casual Cool", "Romantic", "Artsy"
];

interface Outfit {
  id: string;
  name: string;
  occasion: string;
  style: string;
  description?: string;
  items: Array<{
    id: string;
    name: string;
    type: string;
    imageUrl?: string;
  }>;
  createdAt: string | number;
}

export default function EditOutfitPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
  const { wardrobe, loading: wardrobeLoading } = useWardrobe();
  const { toast } = useToast();
  
  const [originalOutfit, setOriginalOutfit] = useState<Outfit | null>(null);
  const [editedOutfit, setEditedOutfit] = useState<Outfit | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [selectedColor, setSelectedColor] = useState<string>("");
  const [showWardrobe, setShowWardrobe] = useState(false);
  const [itemToReplace, setItemToReplace] = useState<string | null>(null);

  // Get unique types and colors from wardrobe
  const itemTypes = [...new Set(wardrobe?.map(item => item.type) || [])];
  const itemColors = [...new Set(wardrobe?.map(item => item.color) || [])];

  // Filter wardrobe items based on search and filters
  const filteredWardrobe = wardrobe?.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.color.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !selectedType || selectedType === "all" || item.type === selectedType;
    const matchesColor = !selectedColor || selectedColor === "all" || item.color === selectedColor;
    
    return matchesSearch && matchesType && matchesColor;
  }) || [];

  useEffect(() => {
    const fetchOutfit = async () => {
      try {
        setLoading(true);
        const outfitId = params.id as string;
        
        const response = await authenticatedFetch(`/api/outfit/${outfitId}`);
        if (!response.ok) {
          throw new Error('Failed to fetch outfit');
        }
        
        const outfitData = await response.json();
        setOriginalOutfit(outfitData);
        setEditedOutfit(outfitData);
      } catch (err) {
        console.error('Error fetching outfit:', err);
        toast({
          title: "Error",
          description: "Failed to load outfit",
          variant: "destructive"
        });
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchOutfit();
    }
  }, [params.id, toast]);

  const handleItemRemove = (itemId: string) => {
    if (!editedOutfit) return;
    
    setEditedOutfit({
      ...editedOutfit,
      items: editedOutfit.items.filter(item => item.id !== itemId)
    });
  };

  const handleItemAdd = (item: WardrobeItem) => {
    if (!editedOutfit) return;
    
    const newItem = {
      id: item.id || "",
      name: item.name || "",
      type: item.type || "unknown",
      imageUrl: item.imageUrl || ""
    };
    
    setEditedOutfit({
      ...editedOutfit,
      items: [...editedOutfit.items, newItem]
    });
    
    setShowWardrobe(false);
    setSearchQuery("");
    setSelectedType("all");
    setSelectedColor("all");
  };

  const handleItemReplace = (item: WardrobeItem) => {
    if (!editedOutfit || !itemToReplace) return;
    
    const newItem = {
      id: item.id || "",
      name: item.name || "",
      type: item.type || "unknown",
      imageUrl: item.imageUrl || ""
    };
    
    setEditedOutfit({
      ...editedOutfit,
      items: editedOutfit.items.map(existingItem => 
        existingItem.id === itemToReplace ? newItem : existingItem
      )
    });
    
    setItemToReplace(null);
    setShowWardrobe(false);
    setSearchQuery("");
    setSelectedType("all");
    setSelectedColor("all");
  };

  const handleSave = async () => {
    if (!editedOutfit) return;
    
    setSaving(true);
    try {
      const response = await authenticatedFetch(`/api/outfit/${editedOutfit.id}/update`, {
        method: "PUT",
        body: JSON.stringify({
          name: editedOutfit.name,
          occasion: editedOutfit.occasion,
          style: editedOutfit.style,
          description: editedOutfit.description,
          items: editedOutfit.items
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update outfit');
      }

      toast({
        title: "Success",
        description: "Outfit updated successfully",
      });

      router.push(`/outfits/${editedOutfit.id}`);
    } catch (error) {
      console.error('Error updating outfit:', error);
      toast({
        title: "Error",
        description: "Failed to update outfit",
        variant: "destructive"
      });
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (originalOutfit) {
      setEditedOutfit(originalOutfit);
      toast({
        title: "Reset",
        description: "Outfit reset to original state",
      });
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedType("all");
    setSelectedColor("all");
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
        </div>
      </div>
    );
  }

  if (!editedOutfit) {
    return (
      <div className="container mx-auto py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4">Outfit Not Found</h1>
          <p className="text-muted-foreground mb-4">The outfit you're looking for doesn't exist.</p>
          <Button onClick={() => router.back()}>
            Go Back
          </Button>
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
          <h1 className="text-2xl font-bold">Edit Outfit</h1>
          <p className="text-muted-foreground">
            Modify your outfit by adding, removing, or replacing items
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleReset}>
            <RotateCcw className="w-4 h-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                Saving...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left side - Outfit details and current items */}
        <div className="lg:col-span-2 space-y-6">
          {/* Outfit Details Form */}
          <Card>
            <CardHeader>
              <CardTitle>Outfit Details</CardTitle>
              <CardDescription>
                Update the basic information for your outfit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Outfit Name</Label>
                  <Input
                    id="name"
                    value={editedOutfit.name}
                    onChange={(e) => setEditedOutfit({...editedOutfit, name: e.target.value})}
                    placeholder="e.g., Summer Casual, Work Outfit"
                  />
                </div>
                
                <div>
                  <Label htmlFor="occasion">Occasion</Label>
                  <Select value={editedOutfit.occasion} onValueChange={(value) => setEditedOutfit({...editedOutfit, occasion: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {OCCASIONS.map(occasion => (
                        <SelectItem key={occasion} value={occasion}>{occasion}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="style">Style</Label>
                  <Select value={editedOutfit.style} onValueChange={(value) => setEditedOutfit({...editedOutfit, style: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {STYLES.map(style => (
                        <SelectItem key={style} value={style}>{style}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={editedOutfit.description || ""}
                    onChange={(e) => setEditedOutfit({...editedOutfit, description: e.target.value})}
                    placeholder="Optional notes about this outfit..."
                    rows={3}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Current Items */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Current Items ({editedOutfit.items.length})</CardTitle>
                  <CardDescription>
                    Items in your outfit
                  </CardDescription>
                </div>
                <Button 
                  variant="outline" 
                  onClick={() => setShowWardrobe(true)}
                  disabled={wardrobeLoading}
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Item
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {editedOutfit.items.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  No items in this outfit yet. Add some items to get started!
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {editedOutfit.items.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      {item.imageUrl && (
                        <div className="mb-3 aspect-square overflow-hidden rounded-md relative">
                          <Image
                            src={item.imageUrl}
                            alt={item.name}
                            fill
                            className="object-cover"
                          />
                        </div>
                      )}
                      <div className="font-medium">{item.name}</div>
                      <div className="text-sm text-gray-500 capitalize">{item.type}</div>
                      <div className="flex gap-2 mt-3">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setItemToReplace(item.id)}
                        >
                          Replace
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleItemRemove(item.id)}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right side - Wardrobe selection */}
        <div className="lg:col-span-1">
          {showWardrobe && (
            <Card>
              <CardHeader>
                <CardTitle>
                  {itemToReplace ? "Replace Item" : "Add Item from Wardrobe"}
                </CardTitle>
                <CardDescription>
                  Select an item from your wardrobe
                </CardDescription>
                
                {/* Search and filters */}
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search items..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => clearFilters()}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                  
                  <div className="flex gap-2 flex-wrap">
                    <Select value={selectedType} onValueChange={setSelectedType}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        {itemTypes.map(type => (
                          <SelectItem key={type} value={type}>{type}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    
                    <Select value={selectedColor} onValueChange={setSelectedColor}>
                      <SelectTrigger className="w-32">
                        <SelectValue placeholder="Color" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Colors</SelectItem>
                        {itemColors.map(color => (
                          <SelectItem key={color} value={color}>{color}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent>
                {filteredWardrobe.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-muted-foreground">
                      {wardrobe?.length === 0 
                        ? "No items in your wardrobe yet."
                        : "No items match your search criteria."
                      }
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {filteredWardrobe.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
                        onClick={() => itemToReplace ? handleItemReplace(item) : handleItemAdd(item)}
                      >
                        <div className="w-12 h-12 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                          {item.imageUrl ? (
                            <Image
                              src={item.imageUrl}
                              alt={item.name}
                              width={48}
                              height={48}
                              className="object-cover w-full h-full"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-gray-400">
                              <span className="text-xs">No image</span>
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">{item.name}</p>
                          <div className="flex gap-1">
                            <Badge variant="outline" className="text-xs">
                              {item.type}
                            </Badge>
                            <Badge variant="outline" className="text-xs">
                              {item.color}
                            </Badge>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Plus className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="mt-4 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowWardrobe(false);
                      setItemToReplace(null);
                      clearFilters();
                    }}
                    className="w-full"
                  >
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
} 