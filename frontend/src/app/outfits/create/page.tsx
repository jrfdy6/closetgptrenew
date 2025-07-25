"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useWardrobe } from "@/hooks/useWardrobe";
import { useAuth } from "@/hooks/useAuth";
import { authenticatedFetch } from "@/lib/utils/auth";
import { ClothingItem } from "../../../types/wardrobe";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Plus, X, Search, Filter } from "lucide-react";
import Image from "next/image";
import { useToast } from "@/components/ui/use-toast";

const OCCASIONS = [
  "Casual",
  "Business Casual",
  "Formal",
  "Gala",
  "Party",
  "Date Night",
  "Work",
  "Interview",
  "Brunch",
  "Wedding Guest",
  "Cocktail",
  "Travel",
  "Airport",
  "Loungewear",
  "Beach",
  "Vacation",
  "Festival",
  "Rainy Day",
  "Snow Day",
  "Hot Weather",
  "Cold Weather",
  "Night Out",
  "Athletic / Gym",
  "School",
  "Holiday",
  "Concert",
  "Errands",
  "Chilly Evening",
  "Museum / Gallery",
  "First Date",
  "Business Formal",
  "Funeral / Memorial",
  "Fashion Event",
  "Outdoor Gathering"
];

const STYLES = [
  "Dark Academia",
  "Old Money",
  "Streetwear",
  "Y2K",
  "Minimalist",
  "Boho",
  "Preppy",
  "Grunge",
  "Classic",
  "Techwear",
  "Androgynous",
  "Coastal Chic",
  "Business Casual",
  "Avant-Garde",
  "Cottagecore",
  "Edgy",
  "Athleisure",
  "Casual Cool",
  "Romantic",
  "Artsy"
];

interface OutfitFormData {
  name: string;
  occasion: string;
  style: string;
  description: string;
}

export default function CreateOutfitPage() {
  const router = useRouter();
  const { user } = useAuth();
  const { wardrobe, loading: wardrobeLoading } = useWardrobe();
  const { toast } = useToast();
  
  const [selectedItems, setSelectedItems] = useState<ClothingItem[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [selectedColor, setSelectedColor] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<OutfitFormData>({
    name: "",
    occasion: "",
    style: "",
    description: ""
  });

  // Get unique types and colors from wardrobe
  const itemTypes = [...new Set(wardrobe?.map(item => item.type) || [])];
  const itemColors = [...new Set(wardrobe?.map(item => item.color) || [])];

  // Filter wardrobe items based on search and filters
  const filteredWardrobe = wardrobe?.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.color.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = !selectedType || item.type === selectedType;
    const matchesColor = !selectedColor || item.color === selectedColor;
    
    return matchesSearch && matchesType && matchesColor;
  }) || [];

  const handleItemSelect = (item: ClothingItem) => {
    if (selectedItems.find(selected => selected.id === item.id)) {
      setSelectedItems(selectedItems.filter(selected => selected.id !== item.id));
    } else {
      setSelectedItems([...selectedItems, item]);
    }
  };

  const handleItemRemove = (itemId: string) => {
    setSelectedItems(selectedItems.filter(item => item.id !== itemId));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (selectedItems.length === 0) {
      toast({
        title: "No items selected",
        description: "Please select at least one item for your outfit.",
        variant: "destructive"
      });
      return;
    }

    if (!formData.name.trim()) {
      toast({
        title: "Outfit name required",
        description: "Please give your outfit a name.",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    try {
      const payload = {
        name: formData.name,
        occasion: formData.occasion || "Casual",
        style: formData.style || "Casual",
        description: formData.description,
        items: selectedItems.map(item => ({
          id: item.id,
          name: item.name,
          type: item.type,
          imageUrl: item.imageUrl
        })),
        createdAt: Date.now()
      };

      const response = await authenticatedFetch("/api/outfit/create", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to create outfit");
      }

      const data = await response.json();
      
      toast({
        title: "Outfit created!",
        description: "Your custom outfit has been saved successfully.",
      });

      router.push(`/outfits/${data.id}`);
    } catch (error) {
      console.error("Error creating outfit:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create outfit",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearchQuery("");
    setSelectedType("");
    setSelectedColor("");
  };

  if (wardrobeLoading) {
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

  return (
    <div className="container mx-auto py-8">
      <div className="flex items-center gap-4 mb-8">
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Create Custom Outfit</h1>
          <p className="text-muted-foreground">
            Select items from your wardrobe to create a custom outfit
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left side - Wardrobe items */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Select Items</CardTitle>
              <CardDescription>
                Choose items from your wardrobe to include in your outfit
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
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Types</SelectItem>
                      {itemTypes.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  
                  <Select value={selectedColor} onValueChange={setSelectedColor}>
                    <SelectTrigger className="w-40">
                      <SelectValue placeholder="Color" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All Colors</SelectItem>
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
                      ? "No items in your wardrobe yet. Add some items first!"
                      : "No items match your search criteria."
                    }
                  </p>
                  {wardrobe?.length === 0 && (
                    <Button 
                      className="mt-4" 
                      onClick={() => router.push('/wardrobe')}
                    >
                      Go to Wardrobe
                    </Button>
                  )}
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {filteredWardrobe.map((item) => {
                    const isSelected = selectedItems.find(selected => selected.id === item.id);
                    return (
                      <Card
                        key={item.id}
                        className={`cursor-pointer transition-all hover:shadow-md ${
                          isSelected ? 'ring-2 ring-primary' : ''
                        }`}
                        onClick={() => handleItemSelect(item)}
                      >
                        <CardContent className="p-4">
                          <div className="aspect-square relative mb-2 bg-gray-100 rounded-lg overflow-hidden">
                            {item.imageUrl ? (
                              <Image
                                src={item.imageUrl}
                                alt={item.name}
                                fill
                                className="object-cover"
                              />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-gray-400">
                                <span className="text-xs">No image</span>
                              </div>
                            )}
                            {isSelected && (
                              <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1">
                                <Plus className="w-3 h-3" />
                              </div>
                            )}
                          </div>
                          <div className="space-y-1">
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
                        </CardContent>
                      </Card>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right side - Outfit details and selected items */}
        <div className="space-y-6">
          {/* Outfit form */}
          <Card>
            <CardHeader>
              <CardTitle>Outfit Details</CardTitle>
              <CardDescription>
                Add details about your custom outfit
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="name">Outfit Name *</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                    placeholder="e.g., Summer Casual, Work Outfit"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="occasion">Occasion</Label>
                  <Select value={formData.occasion} onValueChange={(value) => setFormData({...formData, occasion: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select occasion" />
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
                  <Select value={formData.style} onValueChange={(value) => setFormData({...formData, style: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select style" />
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
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="Optional notes about this outfit..."
                    rows={3}
                  />
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Selected items */}
          <Card>
            <CardHeader>
              <CardTitle>Selected Items ({selectedItems.length})</CardTitle>
              <CardDescription>
                Items in your custom outfit
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedItems.length === 0 ? (
                <p className="text-muted-foreground text-center py-4">
                  No items selected yet
                </p>
              ) : (
                <div className="space-y-3">
                  {selectedItems.map((item) => (
                    <div key={item.id} className="flex items-center gap-3 p-2 border rounded-lg">
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
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleItemRemove(item.id)}
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Create button */}
          <Button
            onClick={handleSubmit}
            disabled={loading || selectedItems.length === 0 || !formData.name.trim()}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                Creating Outfit...
              </>
            ) : (
              `Create Outfit (${selectedItems.length} items)`
            )}
          </Button>
        </div>
      </div>
    </div>
  );
} 