"use client";

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Search } from 'lucide-react';

interface OutfitMetadata {
  id: string;
  imageUrl: string;
  styles: Record<string, number>;
  layers: number;
  palette: string;
  silhouette: string;
  formality: string;
  description: string;
  gender: 'male' | 'female' | 'unisex';
}

// Import the outfit bank from the quiz component
const outfitBank: OutfitMetadata[] = [
  // 🌿 Cottagecore / Boho - Women (10 outfits)
  {
    id: "F-CB1",
    imageUrl: "/images/outfit-quiz/F-CB1.png",
    styles: { "Cottagecore": 0.9, "Boho": 0.8, "Romantic": 0.6 },
    layers: 3,
    palette: "soft florals",
    silhouette: "flowy",
    formality: "casual",
    description: "Floral maxi dress, cropped knit cardigan, leather boots",
    gender: "female"
  },
  {
    id: "F-CB2",
    imageUrl: "/images/outfit-quiz/F-CB2.png",
    styles: { "Boho": 0.9, "Cottagecore": 0.7, "Artsy": 0.5 },
    layers: 4,
    palette: "warm neutrals",
    silhouette: "layered",
    formality: "casual",
    description: "Peasant blouse, patchwork skirt, vest, floppy hat",
    gender: "female"
  },
  // Add more outfits here - I'll include a few examples
  {
    id: "F-OM1",
    imageUrl: "/images/outfit-quiz/F-OM1.png",
    styles: { "Old Money": 0.9, "Preppy": 0.8, "Classic": 0.7 },
    layers: 3,
    palette: "navy + cream",
    silhouette: "tailored",
    formality: "business",
    description: "Tweed blazer, pleated skirt, loafers",
    gender: "female"
  },
  {
    id: "M-OM1",
    imageUrl: "/images/outfit-quiz/M-OM1.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Business Casual": 0.7 },
    layers: 3,
    palette: "charcoal & cream",
    silhouette: "tailored",
    formality: "business",
    description: "Double-breasted coat, Oxford, tapered trousers",
    gender: "male"
  },
  {
    id: "F-ST1",
    imageUrl: "/images/outfit-quiz/F-ST1.png",
    styles: { "Streetwear": 0.9, "Edgy": 0.8, "Y2K": 0.6 },
    layers: 4,
    palette: "black + red",
    silhouette: "oversized",
    formality: "casual",
    description: "Bomber, graphic tee, wide-leg cargos, bucket hat",
    gender: "female"
  },
  {
    id: "F-MIN1",
    imageUrl: "/images/outfit-quiz/F-MIN1.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Classic": 0.6 },
    layers: 2,
    palette: "monochrome white",
    silhouette: "slim",
    formality: "smart_casual",
    description: "Turtleneck, wide-leg trousers",
    gender: "female"
  }
];

const styleCategories = [
  { id: 'cottagecore-boho', name: '🌿 Cottagecore & Boho', color: 'bg-green-100' },
  { id: 'old-money-preppy', name: '💼 Old Money & Preppy', color: 'bg-blue-100' },
  { id: 'streetwear-edgy', name: '🖤 Streetwear & Edgy', color: 'bg-gray-100' },
  { id: 'minimalist-clean', name: '🤍 Minimalist & Clean', color: 'bg-white' }
];

export default function AllOutfitsPage() {
  const [selectedGender, setSelectedGender] = useState<'all' | 'male' | 'female'>('all');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredOutfits = outfitBank.filter(outfit => {
    const genderMatch = selectedGender === 'all' || outfit.gender === selectedGender;
    const categoryMatch = selectedCategory === 'all' || 
      (selectedCategory === 'cottagecore-boho' && (outfit.styles['Cottagecore'] || outfit.styles['Boho'])) ||
      (selectedCategory === 'old-money-preppy' && (outfit.styles['Old Money'] || outfit.styles['Preppy'] || outfit.styles['Classic'])) ||
      (selectedCategory === 'streetwear-edgy' && (outfit.styles['Streetwear'] || outfit.styles['Edgy'] || outfit.styles['Grunge'])) ||
      (selectedCategory === 'minimalist-clean' && (outfit.styles['Minimalist'] || outfit.styles['Clean Lines']));
    const searchMatch = outfit.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                       Object.keys(outfit.styles).some(style => style.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return genderMatch && categoryMatch && searchMatch;
  });

  const getTopStyles = (styles: Record<string, number>) => {
    return Object.entries(styles)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 2)
      .map(([style]) => style);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-4">
          All Outfit Matches
        </h1>
        <p className="text-lg text-muted-foreground">
          Explore our complete collection of style outfits organized by categories
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search outfits, styles, or descriptions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <Select value={selectedGender} onValueChange={(value: any) => setSelectedGender(value)}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by gender" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Genders</SelectItem>
            <SelectItem value="female">Women</SelectItem>
            <SelectItem value="male">Men</SelectItem>
          </SelectContent>
        </Select>

        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Filter by style" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Styles</SelectItem>
            {styleCategories.map(category => (
              <SelectItem key={category.id} value={category.id}>
                {category.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Results count */}
      <div className="mb-6">
        <p className="text-muted-foreground">
          Showing {filteredOutfits.length} of {outfitBank.length} outfits
        </p>
      </div>

      {/* Outfits Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredOutfits.map((outfit) => (
          <Card key={outfit.id} className="overflow-hidden hover:shadow-lg transition-shadow">
            <div className="aspect-square relative bg-gray-100">
              <img
                src={outfit.imageUrl}
                alt={outfit.description}
                className="w-full h-full object-cover"
                onError={(e) => {
                  const target = e.target as HTMLImageElement;
                  target.style.display = 'none';
                  target.parentElement!.innerHTML = `
                    <div class="w-full h-full flex items-center justify-center bg-gray-200">
                      <div class="text-center p-4">
                        <div class="text-4xl mb-2">👕</div>
                        <div class="text-sm text-gray-600">${outfit.description}</div>
                      </div>
                    </div>
                  `;
                }}
              />
            </div>
            
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">{outfit.id}</CardTitle>
              <p className="text-sm text-muted-foreground">{outfit.description}</p>
            </CardHeader>
            
            <CardContent className="pt-0">
              <div className="space-y-3">
                {/* Top Styles */}
                <div>
                  <p className="text-xs font-medium text-muted-foreground mb-1">Primary Styles</p>
                  <div className="flex flex-wrap gap-1">
                    {getTopStyles(outfit.styles).map((style) => (
                      <Badge key={style} variant="secondary" className="text-xs">
                        {style}
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Metadata */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-muted-foreground">Palette:</span>
                    <p className="font-medium">{outfit.palette}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Silhouette:</span>
                    <p className="font-medium">{outfit.silhouette}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Layers:</span>
                    <p className="font-medium">{outfit.layers}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Formality:</span>
                    <p className="font-medium capitalize">{outfit.formality.replace('_', ' ')}</p>
                  </div>
                </div>

                {/* Gender Badge */}
                <div className="flex justify-between items-center">
                  <Badge variant={outfit.gender === 'female' ? 'default' : 'outline'}>
                    {outfit.gender === 'female' ? '👩' : '👨'} {outfit.gender}
                  </Badge>
                  <Button variant="ghost" size="sm" className="text-xs">
                    View Details
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredOutfits.length === 0 && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🔍</div>
          <h3 className="text-xl font-semibold mb-2">No outfits found</h3>
          <p className="text-muted-foreground">
            Try adjusting your filters or search terms
          </p>
        </div>
      )}
    </div>
  );
} 