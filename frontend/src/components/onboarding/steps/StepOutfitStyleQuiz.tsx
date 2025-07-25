'use client';

import { useState, useEffect, useCallback } from 'react';
import { useOnboardingStore, type StylePreference } from '@/lib/store/onboardingStore';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Heart, X, ArrowRight, Sparkles } from 'lucide-react';
import type { StepProps } from '../StepWizard';

interface OutfitMetadata {
  id: string;
  imageUrl: string;
  styles: Record<string, number>; // Style name -> confidence score (0-1)
  layers: number;
  palette: string;
  silhouette: 'fitted' | 'oversized' | 'boxy' | 'relaxed' | 'flowy' | 'layered' | 'loose' | 'easy' | 'romantic' | 'rustic' | 'breezy' | 'tailored' | 'structured' | 'sophisticated' | 'elegant' | 'academic' | 'slim' | 'streamlined' | 'clean fit' | 'minimal' | 'clean' | 'fitted + loud' | 'unstructured' | 'functional' | 'baggy';
  formality: 'casual' | 'smart_casual' | 'business' | 'formal';
  description: string;
  gender: 'male' | 'female' | 'unisex';
}

interface StyleScore {
  style: string;
  score: number;
  confidence: number;
}

interface StyleArchetype {
  id: string;
  name: string;
  description: string;
  primaryStyles: StylePreference[];
  secondaryStyles: StylePreference[];
  traits: string[];
  aesthetic: string;
}

interface StyleConfidence {
  style: string;
  confidence: number;
  likes: number;
  total: number;
}

interface ColorConfidence {
  color: string;
  confidence: number;
  frequency: number;
}

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
  {
    id: "F-CB3",
    imageUrl: "/images/outfit-quiz/F-CB3.png",
    styles: { "Cottagecore": 0.9, "Romantic": 0.7, "Boho": 0.6 },
    layers: 3,
    palette: "dusty pastels",
    silhouette: "loose",
    formality: "casual",
    description: "Ruffle blouse, wide-leg linen pants, fringe shawl",
    gender: "female"
  },
  {
    id: "F-CB4",
    imageUrl: "/images/outfit-quiz/F-CB4.png",
    styles: { "Cottagecore": 0.9, "Natural": 0.8, "Minimalist": 0.4 },
    layers: 2,
    palette: "natural earth",
    silhouette: "easy",
    formality: "casual",
    description: "Muslin wrap dress, open-toe sandals",
    gender: "female"
  },
  {
    id: "F-CB5",
    imageUrl: "/images/outfit-quiz/F-CB5.png",
    styles: { "Cottagecore": 0.9, "Romantic": 0.8, "Boho": 0.5 },
    layers: 4,
    palette: "dried floral mix",
    silhouette: "romantic",
    formality: "casual",
    description: "Button-front midi dress, wool capelet, ankle boots",
    gender: "female"
  },
  {
    id: "F-CB6",
    imageUrl: "/images/outfit-quiz/F-CB6.png",
    styles: { "Boho": 0.9, "Cottagecore": 0.6, "Natural": 0.7 },
    layers: 3,
    palette: "warm earth tones",
    silhouette: "flowy",
    formality: "casual",
    description: "Crochet top, maxi skirt, leather belt",
    gender: "female"
  },
  {
    id: "F-CB7",
    imageUrl: "/images/outfit-quiz/F-CB7.png",
    styles: { "Cottagecore": 0.9, "Romantic": 0.7, "Natural": 0.6 },
    layers: 2,
    palette: "soft pastels",
    silhouette: "easy",
    formality: "casual",
    description: "Linen sundress, straw hat, espadrilles",
    gender: "female"
  },
  {
    id: "F-CB8",
    imageUrl: "/images/outfit-quiz/F-CB8.png",
    styles: { "Boho": 0.9, "Artsy": 0.7, "Cottagecore": 0.5 },
    layers: 4,
    palette: "mixed earth tones",
    silhouette: "layered",
    formality: "casual",
    description: "Embroidered blouse, tiered skirt, vest, jewelry",
    gender: "female"
  },
  {
    id: "F-CB9",
    imageUrl: "/images/outfit-quiz/F-CB9.png",
    styles: { "Cottagecore": 0.9, "Natural": 0.8, "Romantic": 0.6 },
    layers: 3,
    palette: "muted florals",
    silhouette: "flowy",
    formality: "casual",
    description: "Floral tea dress, cardigan, ankle boots",
    gender: "female"
  },
  {
    id: "F-CB10",
    imageUrl: "/images/outfit-quiz/F-CB10.png",
    styles: { "Boho": 0.9, "Natural": 0.7, "Cottagecore": 0.6 },
    layers: 3,
    palette: "warm neutrals",
    silhouette: "relaxed",
    formality: "casual",
    description: "Linen jumpsuit, woven bag, sandals",
    gender: "female"
  },

  // 🌿 Cottagecore / Boho - Men (10 outfits)
  {
    id: "M-CB1",
    imageUrl: "/images/outfit-quiz/M-CB1.png",
    styles: { "Cottagecore": 0.9, "Natural": 0.8, "Boho": 0.6 },
    layers: 3,
    palette: "cream & olive",
    silhouette: "relaxed",
    formality: "casual",
    description: "Linen shirt, cargo trousers, fisherman cardigan",
    gender: "male"
  },
  {
    id: "M-CB2",
    imageUrl: "/images/outfit-quiz/M-CB2.png",
    styles: { "Boho": 0.9, "Natural": 0.7, "Cottagecore": 0.5 },
    layers: 2,
    palette: "warm taupe",
    silhouette: "flowy",
    formality: "casual",
    description: "Henley, cotton pants, leather sandals",
    gender: "male"
  },
  {
    id: "M-CB3",
    imageUrl: "/images/outfit-quiz/M-CB3.png",
    styles: { "Cottagecore": 0.9, "Vintage": 0.7, "Boho": 0.6 },
    layers: 4,
    palette: "vintage neutrals",
    silhouette: "rustic",
    formality: "casual",
    description: "Chambray shirt, suspenders, wool vest, canvas boots",
    gender: "male"
  },
  {
    id: "M-CB4",
    imageUrl: "/images/outfit-quiz/M-CB4.png",
    styles: { "Cottagecore": 0.9, "Natural": 0.8, "Boho": 0.5 },
    layers: 3,
    palette: "soft moss green",
    silhouette: "loose",
    formality: "casual",
    description: "Pullover tunic, drawstring trousers, woven belt",
    gender: "male"
  },
  {
    id: "M-CB5",
    imageUrl: "/images/outfit-quiz/M-CB5.png",
    styles: { "Boho": 0.9, "Cottagecore": 0.7, "Artsy": 0.6 },
    layers: 3,
    palette: "terracotta mix",
    silhouette: "breezy",
    formality: "casual",
    description: "Knit tank, patchwork overshirt, rolled linen pants",
    gender: "male"
  },
  {
    id: "M-CB6",
    imageUrl: "/images/outfit-quiz/M-CB6.png",
    styles: { "Natural": 0.9, "Cottagecore": 0.7, "Boho": 0.6 },
    layers: 2,
    palette: "earth tones",
    silhouette: "relaxed",
    formality: "casual",
    description: "Linen shirt, khaki pants, leather belt",
    gender: "male"
  },
  {
    id: "M-CB7",
    imageUrl: "/images/outfit-quiz/M-CB7.png",
    styles: { "Boho": 0.9, "Natural": 0.7, "Cottagecore": 0.5 },
    layers: 3,
    palette: "warm neutrals",
    silhouette: "flowy",
    formality: "casual",
    description: "Oversized shirt, loose pants, sandals",
    gender: "male"
  },
  {
    id: "M-CB8",
    imageUrl: "/images/outfit-quiz/M-CB8.png",
    styles: { "Cottagecore": 0.9, "Vintage": 0.7, "Natural": 0.6 },
    layers: 3,
    palette: "muted earth",
    silhouette: "rustic",
    formality: "casual",
    description: "Corduroy shirt, wool vest, canvas pants",
    gender: "male"
  },
  {
    id: "M-CB9",
    imageUrl: "/images/outfit-quiz/M-CB9.png",
    styles: { "Natural": 0.9, "Boho": 0.7, "Cottagecore": 0.6 },
    layers: 2,
    palette: "soft greens",
    silhouette: "relaxed",
    formality: "casual",
    description: "Cotton tee, linen pants, woven hat",
    gender: "male"
  },
  {
    id: "M-CB10",
    imageUrl: "/images/outfit-quiz/M-CB10.png",
    styles: { "Boho": 0.9, "Artsy": 0.7, "Natural": 0.6 },
    layers: 4,
    palette: "mixed earth",
    silhouette: "layered",
    formality: "casual",
    description: "Embroidered shirt, vest, cargo pants, jewelry",
    gender: "male"
  },

  // 💼 Old Money / Preppy / Classic - Women (10 outfits)
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
    id: "F-OM2",
    imageUrl: "/images/outfit-quiz/F-OM2.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Preppy": 0.6 },
    layers: 2,
    palette: "rich neutrals",
    silhouette: "structured",
    formality: "business",
    description: "Cable knit over collared blouse, pressed trousers",
    gender: "female"
  },
  {
    id: "F-OM3",
    imageUrl: "/images/outfit-quiz/F-OM3.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Business Casual": 0.7 },
    layers: 4,
    palette: "soft jewel tones",
    silhouette: "sophisticated",
    formality: "business",
    description: "Wool coat, dress shirt, midi skirt, heels",
    gender: "female"
  },
  {
    id: "F-OM4",
    imageUrl: "/images/outfit-quiz/F-OM4.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Elegant": 0.7 },
    layers: 2,
    palette: "champagne & blush",
    silhouette: "elegant",
    formality: "business",
    description: "Silk blouse, beige high-waist trousers",
    gender: "female"
  },
  {
    id: "F-OM5",
    imageUrl: "/images/outfit-quiz/F-OM5.png",
    styles: { "Old Money": 0.9, "Preppy": 0.8, "Academic": 0.7 },
    layers: 3,
    palette: "green & brown",
    silhouette: "academic",
    formality: "business",
    description: "Blazer, check trousers, button-down",
    gender: "female"
  },
  {
    id: "F-OM6",
    imageUrl: "/images/outfit-quiz/F-OM6.png",
    styles: { "Preppy": 0.9, "Classic": 0.8, "Old Money": 0.6 },
    layers: 2,
    palette: "navy & white",
    silhouette: "tailored",
    formality: "business",
    description: "Polo dress, cardigan, boat shoes",
    gender: "female"
  },
  {
    id: "F-OM7",
    imageUrl: "/images/outfit-quiz/F-OM7.png",
    styles: { "Classic": 0.9, "Old Money": 0.7, "Elegant": 0.8 },
    layers: 3,
    palette: "monochrome",
    silhouette: "structured",
    formality: "business",
    description: "Trench coat, turtleneck, wide-leg pants",
    gender: "female"
  },
  {
    id: "F-OM8",
    imageUrl: "/images/outfit-quiz/F-OM8.png",
    styles: { "Old Money": 0.9, "Academic": 0.7, "Classic": 0.8 },
    layers: 3,
    palette: "tweed tones",
    silhouette: "academic",
    formality: "business",
    description: "Tweed blazer, pleated skirt, oxfords",
    gender: "female"
  },
  {
    id: "F-OM9",
    imageUrl: "/images/outfit-quiz/F-OM9.png",
    styles: { "Preppy": 0.9, "Classic": 0.7, "Old Money": 0.6 },
    layers: 2,
    palette: "pastel preppy",
    silhouette: "tailored",
    formality: "business",
    description: "Polo shirt, khaki skirt, loafers",
    gender: "female"
  },
  {
    id: "F-OM10",
    imageUrl: "/images/outfit-quiz/F-OM10.png",
    styles: { "Elegant": 0.9, "Old Money": 0.8, "Classic": 0.7 },
    layers: 3,
    palette: "luxury neutrals",
    silhouette: "elegant",
    formality: "business",
    description: "Silk dress, cashmere cardigan, pearls",
    gender: "female"
  },

  // 💼 Old Money / Preppy / Classic - Men (10 outfits)
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
    id: "M-OM2",
    imageUrl: "/images/outfit-quiz/M-OM2.png",
    styles: { "Preppy": 0.9, "Old Money": 0.7, "Classic": 0.6 },
    layers: 2,
    palette: "navy + tan",
    silhouette: "slim",
    formality: "business",
    description: "Polo under cardigan, chinos",
    gender: "male"
  },
  {
    id: "M-OM3",
    imageUrl: "/images/outfit-quiz/M-OM3.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Business Casual": 0.6 },
    layers: 3,
    palette: "deep burgundy",
    silhouette: "structured",
    formality: "business",
    description: "Knit vest, button-down, wool slacks",
    gender: "male"
  },
  {
    id: "M-OM4",
    imageUrl: "/images/outfit-quiz/M-OM4.png",
    styles: { "Old Money": 0.9, "Academic": 0.8, "Classic": 0.7 },
    layers: 4,
    palette: "olive + cream",
    silhouette: "academic",
    formality: "business",
    description: "Houndstooth coat, cashmere sweater, khakis",
    gender: "male"
  },
  {
    id: "M-OM5",
    imageUrl: "/images/outfit-quiz/M-OM5.png",
    styles: { "Old Money": 0.9, "Classic": 0.8, "Elegant": 0.7 },
    layers: 3,
    palette: "white + camel",
    silhouette: "elegant",
    formality: "business",
    description: "Trench, turtleneck, tailored pants",
    gender: "male"
  },
  {
    id: "M-OM6",
    imageUrl: "/images/outfit-quiz/M-OM6.png",
    styles: { "Preppy": 0.9, "Classic": 0.7, "Old Money": 0.6 },
    layers: 2,
    palette: "navy & white",
    silhouette: "slim",
    formality: "business",
    description: "Polo shirt, white pants, boat shoes",
    gender: "male"
  },
  {
    id: "M-OM7",
    imageUrl: "/images/outfit-quiz/M-OM7.png",
    styles: { "Classic": 0.9, "Old Money": 0.7, "Business Casual": 0.8 },
    layers: 3,
    palette: "greyscale",
    silhouette: "tailored",
    formality: "business",
    description: "Suit jacket, turtleneck, dress pants",
    gender: "male"
  },
  {
    id: "M-OM8",
    imageUrl: "/images/outfit-quiz/M-OM8.png",
    styles: { "Academic": 0.9, "Old Money": 0.7, "Classic": 0.8 },
    layers: 3,
    palette: "tweed browns",
    silhouette: "academic",
    formality: "business",
    description: "Tweed blazer, corduroy pants, oxfords",
    gender: "male"
  },
  {
    id: "M-OM9",
    imageUrl: "/images/outfit-quiz/M-OM9.png",
    styles: { "Preppy": 0.9, "Classic": 0.7, "Old Money": 0.6 },
    layers: 2,
    palette: "pastel preppy",
    silhouette: "slim",
    formality: "business",
    description: "Pastel polo, khaki pants, loafers",
    gender: "male"
  },
  {
    id: "M-OM10",
    imageUrl: "/images/outfit-quiz/M-OM10.png",
    styles: { "Elegant": 0.9, "Old Money": 0.8, "Classic": 0.7 },
    layers: 3,
    palette: "luxury neutrals",
    silhouette: "elegant",
    formality: "business",
    description: "Cashmere sweater, silk tie, wool pants",
    gender: "male"
  },

  // 🖤 Streetwear / Edgy / Grunge - Women (10 outfits)
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
    id: "F-ST2",
    imageUrl: "/images/outfit-quiz/F-ST2.png",
    styles: { "Streetwear": 0.9, "Edgy": 0.7, "Techwear": 0.5 },
    layers: 3,
    palette: "muted neutrals",
    silhouette: "relaxed",
    formality: "casual",
    description: "Cropped hoodie, parachute pants, combat boots",
    gender: "female"
  },
  {
    id: "F-ST3",
    imageUrl: "/images/outfit-quiz/F-ST3.png",
    styles: { "Streetwear": 0.9, "Techwear": 0.7, "Edgy": 0.6 },
    layers: 5,
    palette: "greyscale pop",
    silhouette: "boxy",
    formality: "casual",
    description: "Windbreaker, baggy denim, thermal top",
    gender: "female"
  },
  {
    id: "F-ST4",
    imageUrl: "/images/outfit-quiz/F-ST4.png",
    styles: { "Y2K": 0.9, "Edgy": 0.8, "Streetwear": 0.6 },
    layers: 3,
    palette: "y2k high contrast",
    silhouette: "fitted + loud",
    formality: "casual",
    description: "Mesh top, mini skirt, fur jacket",
    gender: "female"
  },
  {
    id: "F-ST5",
    imageUrl: "/images/outfit-quiz/F-ST5.png",
    styles: { "Grunge": 0.9, "Edgy": 0.8, "Streetwear": 0.5 },
    layers: 4,
    palette: "grunge mix",
    silhouette: "unstructured",
    formality: "casual",
    description: "Plaid overshirt, destroyed jeans, band tee",
    gender: "female"
  },
  {
    id: "F-ST6",
    imageUrl: "/images/outfit-quiz/F-ST6.png",
    styles: { "Edgy": 0.9, "Streetwear": 0.7, "Grunge": 0.6 },
    layers: 3,
    palette: "dark contrast",
    silhouette: "fitted",
    formality: "casual",
    description: "Leather jacket, crop top, ripped jeans",
    gender: "female"
  },
  {
    id: "F-ST7",
    imageUrl: "/images/outfit-quiz/F-ST7.png",
    styles: { "Techwear": 0.9, "Streetwear": 0.7, "Edgy": 0.6 },
    layers: 4,
    palette: "urban tech",
    silhouette: "functional",
    formality: "casual",
    description: "Utility vest, cargo pants, tech sneakers",
    gender: "female"
  },
  {
    id: "F-ST8",
    imageUrl: "/images/outfit-quiz/F-ST8.png",
    styles: { "Y2K": 0.9, "Streetwear": 0.6, "Edgy": 0.7 },
    layers: 3,
    palette: "y2k pastels",
    silhouette: "fitted",
    formality: "casual",
    description: "Crop top, low-rise jeans, platform shoes",
    gender: "female"
  },
  {
    id: "F-ST9",
    imageUrl: "/images/outfit-quiz/F-ST9.png",
    styles: { "Grunge": 0.9, "Streetwear": 0.6, "Edgy": 0.7 },
    layers: 3,
    palette: "grunge earth",
    silhouette: "relaxed",
    formality: "casual",
    description: "Flannel shirt, mom jeans, combat boots",
    gender: "female"
  },
  {
    id: "F-ST10",
    imageUrl: "/images/outfit-quiz/F-ST10.png",
    styles: { "Streetwear": 0.9, "Edgy": 0.7, "Y2K": 0.5 },
    layers: 4,
    palette: "urban contrast",
    silhouette: "oversized",
    formality: "casual",
    description: "Oversized hoodie, bike shorts, chunky sneakers",
    gender: "female"
  },

  // 🖤 Streetwear / Edgy / Grunge - Men (10 outfits)
  {
    id: "M-ST1",
    imageUrl: "/images/outfit-quiz/M-ST1.png",
    styles: { "Grunge": 0.9, "Edgy": 0.8, "Streetwear": 0.6 },
    layers: 3,
    palette: "washed black",
    silhouette: "boxy",
    formality: "casual",
    description: "Flannel shirt, band tee, black jeans",
    gender: "male"
  },
  {
    id: "M-ST2",
    imageUrl: "/images/outfit-quiz/M-ST2.png",
    styles: { "Streetwear": 0.9, "Edgy": 0.7, "Urban": 0.6 },
    layers: 4,
    palette: "urban muted",
    silhouette: "oversized",
    formality: "casual",
    description: "Hoodie, puffer, cargos, Nike Dunks",
    gender: "male"
  },
  {
    id: "M-ST3",
    imageUrl: "/images/outfit-quiz/M-ST3.png",
    styles: { "Streetwear": 0.9, "Techwear": 0.7, "Edgy": 0.6 },
    layers: 3,
    palette: "army green & grey",
    silhouette: "baggy",
    formality: "casual",
    description: "Longline tee, joggers, beanie",
    gender: "male"
  },
  {
    id: "M-ST4",
    imageUrl: "/images/outfit-quiz/M-ST4.png",
    styles: { "Streetwear": 0.9, "Grunge": 0.8, "Edgy": 0.7 },
    layers: 5,
    palette: "denim + contrast",
    silhouette: "layered",
    formality: "casual",
    description: "Denim jacket, flannel, hoodie, tee, chains",
    gender: "male"
  },
  {
    id: "M-ST5",
    imageUrl: "/images/outfit-quiz/M-ST5.png",
    styles: { "Techwear": 0.9, "Grunge": 0.7, "Edgy": 0.6 },
    layers: 4,
    palette: "grunge techwear",
    silhouette: "functional",
    formality: "casual",
    description: "Harness jacket, tech pants, tactical boots",
    gender: "male"
  },
  {
    id: "M-ST6",
    imageUrl: "/images/outfit-quiz/M-ST6.png",
    styles: { "Edgy": 0.9, "Streetwear": 0.7, "Grunge": 0.6 },
    layers: 3,
    palette: "dark urban",
    silhouette: "fitted",
    formality: "casual",
    description: "Leather jacket, graphic tee, slim jeans",
    gender: "male"
  },
  {
    id: "M-ST7",
    imageUrl: "/images/outfit-quiz/M-ST7.png",
    styles: { "Y2K": 0.9, "Streetwear": 0.7, "Edgy": 0.6 },
    layers: 3,
    palette: "y2k brights",
    silhouette: "fitted",
    formality: "casual",
    description: "Bright hoodie, baggy jeans, chunky sneakers",
    gender: "male"
  },
  {
    id: "M-ST8",
    imageUrl: "/images/outfit-quiz/M-ST8.png",
    styles: { "Grunge": 0.9, "Streetwear": 0.6, "Edgy": 0.7 },
    layers: 3,
    palette: "grunge earth",
    silhouette: "relaxed",
    formality: "casual",
    description: "Distressed flannel, cargo pants, work boots",
    gender: "male"
  },
  {
    id: "M-ST9",
    imageUrl: "/images/outfit-quiz/M-ST9.png",
    styles: { "Techwear": 0.9, "Streetwear": 0.7, "Edgy": 0.6 },
    layers: 4,
    palette: "tech urban",
    silhouette: "functional",
    formality: "casual",
    description: "Tech vest, utility pants, tech sneakers",
    gender: "male"
  },
  {
    id: "M-ST10",
    imageUrl: "/images/outfit-quiz/M-ST10.png",
    styles: { "Streetwear": 0.9, "Edgy": 0.7, "Y2K": 0.5 },
    layers: 4,
    palette: "urban contrast",
    silhouette: "oversized",
    formality: "casual",
    description: "Oversized tee, baggy cargos, chunky sneakers",
    gender: "male"
  },

  // 🤍 Minimalist / Clean Lines - Women (10 outfits)
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
  },
  {
    id: "F-MIN2",
    imageUrl: "/images/outfit-quiz/F-MIN2.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Business Casual": 0.6 },
    layers: 3,
    palette: "greyscale",
    silhouette: "tailored",
    formality: "smart_casual",
    description: "Cropped blazer, tube top, trousers",
    gender: "female"
  },
  {
    id: "F-MIN3",
    imageUrl: "/images/outfit-quiz/F-MIN3.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Casual Cool": 0.5 },
    layers: 2,
    palette: "soft neutrals",
    silhouette: "streamlined",
    formality: "casual",
    description: "Longline tank, A-line skirt",
    gender: "female"
  },
  {
    id: "F-MIN4",
    imageUrl: "/images/outfit-quiz/F-MIN4.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Modern": 0.6 },
    layers: 2,
    palette: "all black",
    silhouette: "structured",
    formality: "smart_casual",
    description: "Mock neck top, minimal culottes",
    gender: "female"
  },
  {
    id: "F-MIN5",
    imageUrl: "/images/outfit-quiz/F-MIN5.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Classic": 0.6 },
    layers: 3,
    palette: "beige + grey",
    silhouette: "clean fit",
    formality: "smart_casual",
    description: "Short trench, top, tapered pants",
    gender: "female"
  },
  {
    id: "F-MIN6",
    imageUrl: "/images/outfit-quiz/F-MIN6.png",
    styles: { "Clean Lines": 0.9, "Minimalist": 0.8, "Modern": 0.7 },
    layers: 2,
    palette: "cool neutrals",
    silhouette: "slim",
    formality: "smart_casual",
    description: "Silk blouse, straight pants, loafers",
    gender: "female"
  },
  {
    id: "F-MIN7",
    imageUrl: "/images/outfit-quiz/F-MIN7.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Casual Cool": 0.6 },
    layers: 2,
    palette: "warm neutrals",
    silhouette: "relaxed",
    formality: "casual",
    description: "Linen dress, sandals",
    gender: "female"
  },
  {
    id: "F-MIN8",
    imageUrl: "/images/outfit-quiz/F-MIN8.png",
    styles: { "Modern": 0.9, "Minimalist": 0.8, "Clean Lines": 0.7 },
    layers: 3,
    palette: "monochrome grey",
    silhouette: "structured",
    formality: "smart_casual",
    description: "Blazer dress, ankle boots",
    gender: "female"
  },
  {
    id: "F-MIN9",
    imageUrl: "/images/outfit-quiz/F-MIN9.png",
    styles: { "Clean Lines": 0.9, "Minimalist": 0.8, "Classic": 0.6 },
    layers: 2,
    palette: "cream + white",
    silhouette: "clean fit",
    formality: "smart_casual",
    description: "Cream blouse, white pants, loafers",
    gender: "female"
  },
  {
    id: "F-MIN10",
    imageUrl: "/images/outfit-quiz/F-MIN10.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Modern": 0.6 },
    layers: 2,
    palette: "cool monochrome",
    silhouette: "streamlined",
    formality: "smart_casual",
    description: "Mock neck dress, ankle boots",
    gender: "female"
  },

  // 🤍 Minimalist / Clean Lines - Men (10 outfits)
  {
    id: "M-MIN1",
    imageUrl: "/images/outfit-quiz/M-MIN1.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Casual Cool": 0.6 },
    layers: 2,
    palette: "charcoal + white",
    silhouette: "slim",
    formality: "casual",
    description: "T-shirt, cropped pants, white sneakers",
    gender: "male"
  },
  {
    id: "M-MIN2",
    imageUrl: "/images/outfit-quiz/M-MIN2.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Classic": 0.6 },
    layers: 3,
    palette: "tonal beige",
    silhouette: "relaxed",
    formality: "smart_casual",
    description: "Overcoat, minimal knit, light trousers",
    gender: "male"
  },
  {
    id: "M-MIN3",
    imageUrl: "/images/outfit-quiz/M-MIN3.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Business Casual": 0.6 },
    layers: 2,
    palette: "greyscale",
    silhouette: "tailored",
    formality: "smart_casual",
    description: "Button-up, pleated pants",
    gender: "male"
  },
  {
    id: "M-MIN4",
    imageUrl: "/images/outfit-quiz/M-MIN4.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Modern": 0.6 },
    layers: 3,
    palette: "cool monochrome",
    silhouette: "clean",
    formality: "smart_casual",
    description: "Jacket, tee, trousers — all in same tone",
    gender: "male"
  },
  {
    id: "M-MIN5",
    imageUrl: "/images/outfit-quiz/M-MIN5.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Classic": 0.6 },
    layers: 2,
    palette: "warm neutrals",
    silhouette: "minimal",
    formality: "smart_casual",
    description: "Knit top, straight chinos, loafers",
    gender: "male"
  },
  {
    id: "M-MIN6",
    imageUrl: "/images/outfit-quiz/M-MIN6.png",
    styles: { "Clean Lines": 0.9, "Minimalist": 0.8, "Modern": 0.7 },
    layers: 2,
    palette: "cool neutrals",
    silhouette: "slim",
    formality: "smart_casual",
    description: "Silk shirt, straight pants, loafers",
    gender: "male"
  },
  {
    id: "M-MIN7",
    imageUrl: "/images/outfit-quiz/M-MIN7.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Casual Cool": 0.6 },
    layers: 2,
    palette: "warm neutrals",
    silhouette: "relaxed",
    formality: "casual",
    description: "Linen shirt, cotton pants, sandals",
    gender: "male"
  },
  {
    id: "M-MIN8",
    imageUrl: "/images/outfit-quiz/M-MIN8.png",
    styles: { "Modern": 0.9, "Minimalist": 0.8, "Clean Lines": 0.7 },
    layers: 3,
    palette: "monochrome grey",
    silhouette: "structured",
    formality: "smart_casual",
    description: "Blazer, turtleneck, dress pants",
    gender: "male"
  },
  {
    id: "M-MIN9",
    imageUrl: "/images/outfit-quiz/M-MIN9.png",
    styles: { "Clean Lines": 0.9, "Minimalist": 0.8, "Classic": 0.6 },
    layers: 2,
    palette: "cream + white",
    silhouette: "clean fit",
    formality: "smart_casual",
    description: "Cream shirt, white pants, loafers",
    gender: "male"
  },
  {
    id: "M-MIN10",
    imageUrl: "/images/outfit-quiz/M-MIN10.png",
    styles: { "Minimalist": 0.9, "Clean Lines": 0.8, "Modern": 0.6 },
    layers: 2,
    palette: "cool monochrome",
    silhouette: "streamlined",
    formality: "smart_casual",
    description: "Mock neck sweater, straight pants",
    gender: "male"
  }
];

const styleArchetypes: StyleArchetype[] = [
  // Romantic + Intellectual Combinations
  {
    id: 'soft-intellectual',
    name: 'The Soft Intellectual',
    description: 'Romantic academia with a gentle, thoughtful approach to style',
    primaryStyles: ['Romantic', 'Dark Academia'],
    secondaryStyles: ['Classic', 'Preppy'],
    traits: ['Vintage blazers', 'Soft fabrics', 'Moody palettes', 'Literary references'],
    aesthetic: 'Thoughtful elegance with a dreamy edge'
  },
  {
    id: 'poetic-scholar',
    name: 'The Poetic Scholar',
    description: 'Dark Academia meets Romantic with artistic flourishes',
    primaryStyles: ['Dark Academia', 'Romantic'],
    secondaryStyles: ['Artsy', 'Classic'],
    traits: ['Tweed with lace', 'Victorian details', 'Bookish accessories', 'Moody colors'],
    aesthetic: 'Academic romance with artistic soul'
  },

  // Minimalist + Urban Combinations
  {
    id: 'urban-minimalist',
    name: 'The Urban Minimalist',
    description: 'Clean lines meet street culture with sophisticated simplicity',
    primaryStyles: ['Minimalist', 'Streetwear'],
    secondaryStyles: ['Classic', 'Business Casual'],
    traits: ['Clean sneakers', 'Structured basics', 'Neutral palettes', 'Quality materials'],
    aesthetic: 'Sophisticated street style with clean precision'
  },
  {
    id: 'refined-street',
    name: 'The Refined Street',
    description: 'Streetwear elevated with minimalist principles',
    primaryStyles: ['Streetwear', 'Minimalist'],
    secondaryStyles: ['Techwear', 'Business Casual'],
    traits: ['Premium streetwear', 'Clean silhouettes', 'Monochrome looks', 'Quality basics'],
    aesthetic: 'Street culture with refined sophistication'
  },

  // Natural + Artistic Combinations
  {
    id: 'whimsical-naturalist',
    name: 'The Whimsical Naturalist',
    description: 'Cottagecore meets artistic expression with natural elements',
    primaryStyles: ['Cottagecore', 'Artsy'],
    secondaryStyles: ['Romantic', 'Casual Cool'],
    traits: ['Floral prints', 'Handmade details', 'Natural fabrics', 'Artistic touches'],
    aesthetic: 'Nature-inspired creativity with whimsical charm'
  },
  {
    id: 'artistic-earth-child',
    name: 'The Artistic Earth Child',
    description: 'Boho meets Artsy with natural, creative expression',
    primaryStyles: ['Boho', 'Artsy'],
    secondaryStyles: ['Cottagecore', 'Romantic'],
    traits: ['Handmade jewelry', 'Natural dyes', 'Creative layering', 'Organic textures'],
    aesthetic: 'Creative bohemian with natural soul'
  },

  // Classic + Modern Combinations
  {
    id: 'timeless-modernist',
    name: 'The Timeless Modernist',
    description: 'Classic elegance with contemporary sophistication',
    primaryStyles: ['Classic', 'Minimalist'],
    secondaryStyles: ['Business Casual', 'Old Money'],
    traits: ['Tailored pieces', 'Quality materials', 'Clean lines', 'Sophisticated neutrals'],
    aesthetic: 'Timeless elegance with modern precision'
  },
  {
    id: 'sophisticated-classic',
    name: 'The Sophisticated Classic',
    description: 'Old Money meets Classic with refined luxury',
    primaryStyles: ['Old Money', 'Classic'],
    secondaryStyles: ['Business Casual', 'Minimalist'],
    traits: ['Luxury materials', 'Tailored fits', 'Neutral palettes', 'Quality craftsmanship'],
    aesthetic: 'Refined luxury with timeless appeal'
  },

  // Edgy + Intellectual Combinations
  {
    id: 'dark-intellectual',
    name: 'The Dark Intellectual',
    description: 'Dark Academia meets Edgy with sophisticated rebellion',
    primaryStyles: ['Dark Academia', 'Edgy'],
    secondaryStyles: ['Grunge', 'Classic'],
    traits: ['Leather accents', 'Moody palettes', 'Intellectual details', 'Rebellious touches'],
    aesthetic: 'Sophisticated rebellion with intellectual depth'
  },
  {
    id: 'rebellious-scholar',
    name: 'The Rebellious Scholar',
    description: 'Edgy meets Dark Academia with intellectual edge',
    primaryStyles: ['Edgy', 'Dark Academia'],
    secondaryStyles: ['Grunge', 'Avant-Garde'],
    traits: ['Distressed elements', 'Academic details', 'Dark aesthetics', 'Intellectual edge'],
    aesthetic: 'Intellectual rebellion with dark sophistication'
  },

  // Coastal + Casual Combinations
  {
    id: 'effortless-coastal',
    name: 'The Effortless Coastal',
    description: 'Coastal Chic meets Casual Cool with natural ease',
    primaryStyles: ['Coastal Chic', 'Casual Cool'],
    secondaryStyles: ['Cottagecore', 'Minimalist'],
    traits: ['Linen fabrics', 'Ocean colors', 'Relaxed fits', 'Natural textures'],
    aesthetic: 'Effortless coastal living with natural charm'
  },
  {
    id: 'natural-coastal',
    name: 'The Natural Coastal',
    description: 'Casual Cool meets Coastal Chic with organic simplicity',
    primaryStyles: ['Casual Cool', 'Coastal Chic'],
    secondaryStyles: ['Cottagecore', 'Romantic'],
    traits: ['Breathable fabrics', 'Earth tones', 'Relaxed silhouettes', 'Organic materials'],
    aesthetic: 'Natural coastal living with casual elegance'
  },

  // Tech + Street Combinations
  {
    id: 'urban-tech',
    name: 'The Urban Tech',
    description: 'Techwear meets Streetwear with futuristic urban edge',
    primaryStyles: ['Techwear', 'Streetwear'],
    secondaryStyles: ['Athleisure', 'Edgy'],
    traits: ['Utility pockets', 'Technical fabrics', 'Urban aesthetics', 'Functional design'],
    aesthetic: 'Futuristic urban style with technical precision'
  },
  {
    id: 'street-tech',
    name: 'The Street Tech',
    description: 'Streetwear meets Techwear with urban functionality',
    primaryStyles: ['Streetwear', 'Techwear'],
    secondaryStyles: ['Athleisure', 'Y2K'],
    traits: ['Street aesthetics', 'Technical elements', 'Urban functionality', 'Modern edge'],
    aesthetic: 'Urban street style with technical innovation'
  },

  // Y2K + Modern Combinations
  {
    id: 'retro-futurist',
    name: 'The Retro Futurist',
    description: 'Y2K meets Modern with nostalgic innovation',
    primaryStyles: ['Y2K', 'Minimalist'],
    secondaryStyles: ['Streetwear', 'Techwear'],
    traits: ['Nostalgic elements', 'Clean lines', 'Modern twists', 'Retro-futuristic'],
    aesthetic: 'Nostalgic innovation with modern precision'
  },
  {
    id: 'millennial-modern',
    name: 'The Millennial Modern',
    description: 'Y2K meets Contemporary with generational style',
    primaryStyles: ['Y2K', 'Business Casual'],
    secondaryStyles: ['Minimalist', 'Streetwear'],
    traits: ['Millennial aesthetics', 'Modern professionalism', 'Nostalgic touches', 'Contemporary edge'],
    aesthetic: 'Millennial nostalgia with modern sophistication'
  },

  // Grunge + Classic Combinations
  {
    id: 'refined-grunge',
    name: 'The Refined Grunge',
    description: 'Grunge meets Classic with sophisticated edge',
    primaryStyles: ['Grunge', 'Classic'],
    secondaryStyles: ['Edgy', 'Dark Academia'],
    traits: ['Distressed classics', 'Sophisticated edge', 'Moody palettes', 'Quality grunge'],
    aesthetic: 'Sophisticated rebellion with classic foundation'
  },
  {
    id: 'classic-grunge',
    name: 'The Classic Grunge',
    description: 'Classic meets Grunge with timeless edge',
    primaryStyles: ['Classic', 'Grunge'],
    secondaryStyles: ['Dark Academia', 'Edgy'],
    traits: ['Timeless grunge', 'Classic edge', 'Moody sophistication', 'Quality rebellion'],
    aesthetic: 'Timeless edge with classic rebellion'
  },

  // Androgynous + Modern Combinations
  {
    id: 'fluid-modernist',
    name: 'The Fluid Modernist',
    description: 'Androgynous meets Modern with gender-fluid sophistication',
    primaryStyles: ['Androgynous', 'Minimalist'],
    secondaryStyles: ['Business Casual', 'Classic'],
    traits: ['Gender-fluid fits', 'Clean lines', 'Modern tailoring', 'Sophisticated simplicity'],
    aesthetic: 'Gender-fluid sophistication with modern precision'
  },
  {
    id: 'modern-androgynous',
    name: 'The Modern Androgynous',
    description: 'Modern meets Androgynous with contemporary fluidity',
    primaryStyles: ['Minimalist', 'Androgynous'],
    secondaryStyles: ['Business Casual', 'Techwear'],
    traits: ['Contemporary fluidity', 'Modern edge', 'Gender-neutral design', 'Sophisticated innovation'],
    aesthetic: 'Modern fluidity with contemporary sophistication'
  },

  // Avant-Garde + Artistic Combinations
  {
    id: 'artistic-visionary',
    name: 'The Artistic Visionary',
    description: 'Avant-Garde meets Artsy with creative innovation',
    primaryStyles: ['Avant-Garde', 'Artsy'],
    secondaryStyles: ['Romantic', 'Edgy'],
    traits: ['Creative innovation', 'Artistic expression', 'Experimental design', 'Visionary aesthetics'],
    aesthetic: 'Creative innovation with artistic vision'
  },
  {
    id: 'visionary-artist',
    name: 'The Visionary Artist',
    description: 'Artsy meets Avant-Garde with artistic innovation',
    primaryStyles: ['Artsy', 'Avant-Garde'],
    secondaryStyles: ['Romantic', 'Edgy'],
    traits: ['Artistic innovation', 'Creative vision', 'Experimental expression', 'Visionary creativity'],
    aesthetic: 'Artistic vision with creative innovation'
  },

  // Preppy + Modern Combinations
  {
    id: 'modern-prep',
    name: 'The Modern Prep',
    description: 'Preppy meets Modern with contemporary sophistication',
    primaryStyles: ['Preppy', 'Minimalist'],
    secondaryStyles: ['Business Casual', 'Classic'],
    traits: ['Contemporary prep', 'Clean sophistication', 'Modern classics', 'Refined tradition'],
    aesthetic: 'Contemporary prep with modern sophistication'
  },
  {
    id: 'sophisticated-prep',
    name: 'The Sophisticated Prep',
    description: 'Preppy meets Business Casual with refined tradition',
    primaryStyles: ['Preppy', 'Business Casual'],
    secondaryStyles: ['Classic', 'Minimalist'],
    traits: ['Refined tradition', 'Professional prep', 'Sophisticated classics', 'Modern tradition'],
    aesthetic: 'Refined tradition with professional sophistication'
  },

  // Athleisure + Street Combinations
  {
    id: 'street-athlete',
    name: 'The Street Athlete',
    description: 'Athleisure meets Streetwear with urban performance',
    primaryStyles: ['Athleisure', 'Streetwear'],
    secondaryStyles: ['Techwear', 'Casual Cool'],
    traits: ['Urban performance', 'Street athletics', 'Functional style', 'Active urban'],
    aesthetic: 'Urban performance with street athleticism'
  },
  {
    id: 'athletic-street',
    name: 'The Athletic Street',
    description: 'Streetwear meets Athleisure with street performance',
    primaryStyles: ['Streetwear', 'Athleisure'],
    secondaryStyles: ['Techwear', 'Casual Cool'],
    traits: ['Street performance', 'Athletic urban', 'Functional street', 'Active culture'],
    aesthetic: 'Street performance with athletic urbanism'
  },
];

const calculateAlignmentScore = (styleScores: Record<string, number>, likedOutfits: string[]): number => {
  if (likedOutfits.length === 0) return 0;
  
  // Calculate total possible score (assuming max 0.9 per outfit)
  const totalPossibleScore = likedOutfits.length * 0.9;
  const actualScore = Object.values(styleScores).reduce((sum, score) => sum + score, 0);
  
  // Normalize to 0-1 range
  return Math.min(actualScore / totalPossibleScore, 1);
};

export function StepOutfitStyleQuiz({ onNext }: StepProps) {
  const { gender, setStylePreferences, clearCache } = useOnboardingStore();
  const [currentOutfitIndex, setCurrentOutfitIndex] = useState(0);
  const [likedOutfits, setLikedOutfits] = useState<string[]>([]);
  const [dislikedOutfits, setDislikedOutfits] = useState<string[]>([]);
  const [styleConfidence, setStyleConfidence] = useState<StyleConfidence[]>([]);
  const [colorConfidence, setColorConfidence] = useState<ColorConfidence[]>([]);
  const [showResults, setShowResults] = useState(false);
  const [quizComplete, setQuizComplete] = useState(false);
  const [confidenceThreshold] = useState(0.75); // 75% confidence threshold
  const [minOutfitsForConfidence] = useState(8); // Minimum outfits to show before early completion
  const [styleExposure, setStyleExposure] = useState<Record<string, number>>({}); // Track how many outfits from each style shown

  // Clear cache on component mount to ensure fresh results
  useEffect(() => {
    clearCache();
    // Force a fresh start by resetting all state
    setCurrentOutfitIndex(0);
    setLikedOutfits([]);
    setDislikedOutfits([]);
    setStyleConfidence([]);
    setColorConfidence([]);
    setShowResults(false);
    setQuizComplete(false);
    setStyleExposure({});
  }, [clearCache]);

  // Filter outfits based on user's gender
  const genderFilteredOutfits = outfitBank.filter(outfit => {
    // If gender is 'prefer-not-to-say' or 'non-binary', show all outfits
    if (gender === 'prefer-not-to-say' || gender === 'non-binary') {
      return true;
    }
    // Otherwise, filter by gender or unisex
    return outfit.gender === gender || outfit.gender === "unisex";
  });

  // Get all unique styles from the filtered outfits
  const allStyles = new Set<string>();
  genderFilteredOutfits.forEach(outfit => {
    Object.keys(outfit.styles).forEach(style => allStyles.add(style));
  });

  console.log('Debug outfit filtering:', {
    gender,
    totalOutfits: outfitBank.length,
    filteredOutfits: genderFilteredOutfits.length,
    currentIndex: currentOutfitIndex,
    currentOutfit: genderFilteredOutfits[currentOutfitIndex],
    allStyles: Array.from(allStyles),
    styleExposure
  });

  const currentOutfit = genderFilteredOutfits[currentOutfitIndex];

  // Add error handling for missing outfit
  if (!currentOutfit) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Quiz Error
          </h2>
          <p className="text-gray-600 mb-4">
            {genderFilteredOutfits.length === 0 
              ? "No outfits found for your gender preference. Please update your gender selection."
              : "Unable to load outfit data. Please refresh the page and try again."
            }
          </p>
          <div className="text-sm text-gray-500">
            Debug info: Gender: {gender}, Index: {currentOutfitIndex}, Total outfits: {genderFilteredOutfits.length}
          </div>
          {genderFilteredOutfits.length === 0 && (
            <div className="mt-4">
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Refresh Page
              </button>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Extract colors from palette string
  const extractColorsFromPalette = (palette: string): string[] => {
    const colorMap: { [key: string]: string[] } = {
      "soft florals": ["pink", "lavender", "sage", "cream"],
      "warm earth tones": ["brown", "beige", "cream", "terracotta", "olive"],
      "dusty pastels": ["mauve", "sage", "dusty blue", "cream"],
      "natural earth": ["brown", "green", "beige", "tan"],
      "dried floral mix": ["rust", "sage", "dusty pink", "cream"],
      "mixed earth tones": ["brown", "olive", "rust", "beige"],
      "muted florals": ["dusty pink", "sage", "cream", "mauve"],
      "warm neutrals": ["beige", "brown", "cream", "tan"],
      "navy + cream": ["navy", "cream", "white"],
      "rich neutrals": ["brown", "beige", "cream", "tan"],
      "soft jewel tones": ["burgundy", "navy", "emerald", "cream"],
      "champagne & blush": ["champagne", "blush", "cream"],
      "green & brown": ["green", "brown", "beige"],
      "pastel preppy": ["pink", "blue", "yellow", "white"],
      "luxury neutrals": ["cream", "beige", "brown", "tan"],
      "black + red": ["black", "red", "white"],
      "muted neutrals": ["grey", "black", "white", "beige"],
      "greyscale pop": ["black", "white", "grey"],
      "y2k high contrast": ["pink", "blue", "yellow", "black"],
      "grunge mix": ["black", "brown", "olive", "grey"],
      "dark contrast": ["black", "white", "red"],
      "urban tech": ["black", "grey", "olive", "white"],
      "y2k pastels": ["pink", "blue", "yellow", "white"],
      "grunge earth": ["brown", "olive", "black", "beige"],
      "urban contrast": ["black", "white", "grey"],
      "washed black": ["black", "grey", "white"],
      "urban muted": ["grey", "black", "white", "beige"],
      "army green & grey": ["olive", "grey", "black"],
      "denim + contrast": ["blue", "black", "white"],
      "grunge techwear": ["black", "olive", "grey"],
      "dark urban": ["black", "grey", "white"],
      "y2k brights": ["pink", "blue", "yellow", "white"],
      "tech urban": ["black", "grey", "olive"],
      "monochrome white": ["white", "cream"],
      "greyscale": ["black", "white", "grey"],
      "soft neutrals": ["beige", "cream", "tan"],
      "all black": ["black"],
      "beige + grey": ["beige", "grey", "cream"],
      "cool neutrals": ["grey", "white", "black"],
      "monochrome grey": ["grey", "black", "white"],
      "cream + white": ["cream", "white"],
      "cool monochrome": ["grey", "black", "white"],
      "charcoal + white": ["charcoal", "white", "black"],
      "navy + tan": ["navy", "tan", "white"],
      "deep burgundy": ["burgundy", "black", "white"],
      "olive + cream": ["olive", "cream", "brown"],
      "white + camel": ["white", "camel", "cream"],
      "tweed tones": ["brown", "beige", "olive"],
      "tweed browns": ["brown", "beige", "olive"],
      "tonal beige": ["beige", "cream", "tan"],
      // Add missing palette mappings
      "cream & olive": ["cream", "olive", "brown"],
      "warm taupe": ["taupe", "beige", "brown"],
      "vintage neutrals": ["beige", "brown", "cream", "tan"],
      "soft moss green": ["green", "sage", "olive"],
      "terracotta mix": ["terracotta", "brown", "rust"],
      "earth tones": ["brown", "beige", "olive", "tan"],
      "muted earth": ["brown", "beige", "olive", "grey"],
      "soft pastels": ["pink", "blue", "lavender", "cream"]
    };
    
    return colorMap[palette] || [palette];
  };

  // Calculate style confidence in real-time
  const calculateStyleConfidence = useCallback(() => {
    const styleScores: { [key: string]: { likes: number; total: number; score: number } } = {};
    
    // Count likes and calculate scores for each style
    likedOutfits.forEach(outfitId => {
      const outfit = genderFilteredOutfits.find(o => o.id === outfitId);
      if (outfit) {
        Object.entries(outfit.styles).forEach(([style, weight]) => {
          if (!styleScores[style]) {
            styleScores[style] = { likes: 0, total: 0, score: 0 };
          }
          styleScores[style].likes += weight;
          styleScores[style].total += 1;
          styleScores[style].score += weight;
        });
      }
    });

    // Calculate confidence for each style
    const confidence: StyleConfidence[] = Object.entries(styleScores)
      .map(([style, data]) => ({
        style,
        confidence: data.likes / Math.max(data.total, 1),
        likes: data.likes,
        total: data.total
      }))
      .filter(item => item.total >= 2) // Only include styles with at least 2 likes
      .sort((a, b) => b.confidence - a.confidence);

    setStyleConfidence(confidence);
    return confidence;
  }, [likedOutfits, genderFilteredOutfits]);

  // Calculate color confidence in real-time
  const calculateColorConfidence = useCallback(() => {
    const colorScores: { [key: string]: { frequency: number; total: number } } = {};
    
    likedOutfits.forEach(outfitId => {
      const outfit = genderFilteredOutfits.find(o => o.id === outfitId);
      if (outfit) {
        const colors = extractColorsFromPalette(outfit.palette);
        colors.forEach((color: string) => {
          if (!colorScores[color]) {
            colorScores[color] = { frequency: 0, total: 0 };
          }
          colorScores[color].frequency += 1;
          colorScores[color].total += 1;
        });
      }
    });

    const confidence: ColorConfidence[] = Object.entries(colorScores)
      .map(([color, data]) => ({
        color,
        confidence: data.frequency / Math.max(data.total, 1),
        frequency: data.frequency
      }))
      .filter(item => item.frequency >= 2) // Only include colors with at least 2 occurrences
      .sort((a, b) => b.confidence - a.confidence);

    setColorConfidence(confidence);
    return confidence;
  }, [likedOutfits, genderFilteredOutfits]);

  // Check if we have high confidence in primary styles
  const checkHighConfidence = useCallback(() => {
    const styleConf = calculateStyleConfidence();
    const colorConf = calculateColorConfidence();
    
    // Check if we have high confidence in at least 2 primary styles
    const highConfidenceStyles = styleConf.filter(s => s.confidence >= confidenceThreshold);
    const highConfidenceColors = colorConf.filter(c => c.confidence >= confidenceThreshold);
    
    // Check if we've shown at least 2 outfits from each style
    const minExposurePerStyle = 2;
    const hasSeenAllStyles = Array.from(allStyles).every(style => 
      (styleExposure[style] || 0) >= minExposurePerStyle
    );
    
    // Early completion conditions
    const hasEnoughOutfits = likedOutfits.length >= minOutfitsForConfidence;
    const hasHighStyleConfidence = highConfidenceStyles.length >= 2;
    const hasHighColorConfidence = highConfidenceColors.length >= 3;
    const hasMinimumStyleExposure = hasSeenAllStyles;
    
    console.log('=== QUIZ COMPLETION CHECK ===');
    console.log('Has enough outfits:', hasEnoughOutfits, `(${likedOutfits.length}/${minOutfitsForConfidence})`);
    console.log('Has high style confidence:', hasHighStyleConfidence, `(${highConfidenceStyles.length} styles)`);
    console.log('Has high color confidence:', hasHighColorConfidence, `(${highConfidenceColors.length} colors)`);
    console.log('Has minimum style exposure:', hasMinimumStyleExposure);
    console.log('Style exposure:', styleExposure);
    console.log('================================');
    
    // Require both minimum exposure AND either high confidence or enough outfits
    return hasMinimumStyleExposure && (hasEnoughOutfits || hasHighStyleConfidence || hasHighColorConfidence);
  }, [likedOutfits, confidenceThreshold, minOutfitsForConfidence, calculateStyleConfidence, calculateColorConfidence, allStyles, styleExposure]);

  // Handle outfit like/dislike
  const handleOutfitReaction = (liked: boolean) => {
    if (liked) {
      setLikedOutfits(prev => [...prev, currentOutfit.id]);
    } else {
      setDislikedOutfits(prev => [...prev, currentOutfit.id]);
    }

    // Update style exposure tracking
    setStyleExposure(prev => {
      const newExposure = { ...prev };
      Object.keys(currentOutfit.styles).forEach(style => {
        newExposure[style] = (newExposure[style] || 0) + 1;
      });
      return newExposure;
    });

    // Check for high confidence after each reaction
    setTimeout(() => {
      if (checkHighConfidence()) {
        setShowResults(true);
        setQuizComplete(true);
      } else if (currentOutfitIndex < genderFilteredOutfits.length - 1) {
        setCurrentOutfitIndex(prev => prev + 1);
      } else {
        // Reached end of outfits
        setShowResults(true);
        setQuizComplete(true);
      }
    }, 100);
  };

  // Get primary and secondary styles
  const getPrimaryStyles = () => {
    return styleConfidence
      .filter(s => s.confidence >= confidenceThreshold)
      .slice(0, 2)
      .map(s => s.style);
  };

  const getSecondaryStyles = () => {
    return styleConfidence
      .filter(s => s.confidence >= 0.4 && s.confidence < confidenceThreshold)
      .slice(0, 2)
      .map(s => s.style);
  };

  // Get primary colors
  const getPrimaryColors = () => {
    // Get colors from high confidence outfits
    const highConfidenceColors = colorConfidence
      .filter(c => c.confidence >= confidenceThreshold)
      .slice(0, 8) // Get more colors
      .map(c => c.color);
    
    // Always extract colors from liked outfits' palettes as fallback
    const paletteColors = new Set<string>();
    
    // Extract colors from liked outfits' palettes
    likedOutfits.forEach(outfitId => {
      const outfit = outfitBank.find(o => o.id === outfitId);
      if (outfit) {
        const colors = extractColorsFromPalette(outfit.palette);
        colors.forEach(color => paletteColors.add(color));
      }
    });
    
    // Combine high confidence colors with palette colors
    const allColors = [...new Set([...highConfidenceColors, ...Array.from(paletteColors)])];
    
    // If we still don't have enough colors, add some from all outfits
    if (allColors.length < 3) {
      const allPaletteColors = new Set<string>();
      genderFilteredOutfits.forEach(outfit => {
        const colors = extractColorsFromPalette(outfit.palette);
        colors.forEach(color => allPaletteColors.add(color));
      });
      
      const additionalColors = Array.from(allPaletteColors).slice(0, 5);
      allColors.push(...additionalColors);
    }
    
    // Return unique colors, prioritizing high confidence ones
    const finalColors = [...new Set(allColors)].slice(0, 8);
    
    // Debug logging
    console.log('=== COLOR EXTRACTION DEBUG ===');
    console.log('High confidence colors:', highConfidenceColors);
    console.log('Palette colors from liked outfits:', Array.from(paletteColors));
    console.log('All combined colors:', allColors);
    console.log('Final colors returned:', finalColors);
    console.log('================================');
    
    return finalColors;
  };

  // Creative Style Archetype Mapping
  const getCreativeArchetypeName = (primaryStyles: string[]): string => {
    if (primaryStyles.length < 2) {
      return primaryStyles[0] || "The Style Pioneer";
    }

    const style1 = primaryStyles[0];
    const style2 = primaryStyles[1];

    // Creative archetype mappings - ULTRA SNazzy Edition! ✨🌟
    const archetypeMap: Record<string, string> = {
      // Old Money combinations - The Elite Circle
      "Old Money Classic": "The Legacy Curator",
      "Classic Old Money": "The Legacy Curator",
      "Old Money Preppy": "The Ivy League Aristocrat",
      "Preppy Old Money": "The Ivy League Aristocrat",
      "Old Money Business Casual": "The Boardroom Royal",
      "Business Casual Old Money": "The Boardroom Royal",
      "Old Money Elegant": "The Gilded Sophisticate",
      "Elegant Old Money": "The Gilded Sophisticate",
      "Old Money Academic": "The Scholarly Elite",
      "Academic Old Money": "The Scholarly Elite",
      "Old Money Natural": "The Aristocratic Naturalist",
      "Natural Old Money": "The Aristocratic Naturalist",
      "Old Money Cottagecore": "The Aristocratic Gardener",
      "Cottagecore Old Money": "The Aristocratic Gardener",
      "Old Money Streetwear": "The Street Aristocrat",
      "Streetwear Old Money": "The Street Aristocrat",
      "Old Money Y2K": "The Millennial Aristocrat",
      "Y2K Old Money": "The Millennial Aristocrat",
      "Old Money Minimalist": "The Minimalist Aristocrat",
      "Minimalist Old Money": "The Minimalist Aristocrat",
      "Old Money Coastal Chic": "The Coastal Aristocrat",
      "Coastal Chic Old Money": "The Coastal Aristocrat",
      "Old Money Techwear": "The Tech Aristocrat",
      "Techwear Old Money": "The Tech Aristocrat",
      "Old Money Grunge": "The Refined Rebel",
      "Grunge Old Money": "The Refined Rebel",
      "Old Money Androgynous": "The Gender-Fluid Aristocrat",
      "Androgynous Old Money": "The Gender-Fluid Aristocrat",
      "Old Money Romantic": "The Romantic Aristocrat",
      "Romantic Old Money": "The Romantic Aristocrat",
      "Old Money Artsy": "The Artistic Aristocrat",
      "Artsy Old Money": "The Artistic Aristocrat",
      "Old Money Bohemian": "The Bohemian Aristocrat",
      "Bohemian Old Money": "The Bohemian Aristocrat",
      "Old Money Athleisure": "The Athletic Aristocrat",
      "Athleisure Old Money": "The Athletic Aristocrat",

      // Dark Academia combinations - The Intellectual Edge
      "Dark Academia Romantic": "The Gothic Poet",
      "Romantic Dark Academia": "The Gothic Poet",
      "Dark Academia Edgy": "The Rebel Scholar",
      "Edgy Dark Academia": "The Rebel Scholar",
      "Dark Academia Classic": "The Victorian Modernist",
      "Classic Dark Academia": "The Victorian Modernist",
      "Dark Academia Streetwear": "The Street Scholar",
      "Streetwear Dark Academia": "The Street Scholar",
      "Dark Academia Y2K": "The Cyber Scholar",
      "Y2K Dark Academia": "The Cyber Scholar",
      "Dark Academia Minimalist": "The Minimalist Scholar",
      "Minimalist Dark Academia": "The Minimalist Scholar",
      "Dark Academia Coastal Chic": "The Coastal Scholar",
      "Coastal Chic Dark Academia": "The Coastal Scholar",
      "Dark Academia Techwear": "The Digital Scholar",
      "Techwear Dark Academia": "The Digital Scholar",
      "Dark Academia Grunge": "The Scholarly Punk",
      "Grunge Dark Academia": "The Scholarly Punk",
      "Dark Academia Androgynous": "The Gender-Fluid Scholar",
      "Androgynous Dark Academia": "The Gender-Fluid Scholar",
      "Dark Academia Artsy": "The Artistic Scholar",
      "Artsy Dark Academia": "The Artistic Scholar",
      "Dark Academia Bohemian": "The Bohemian Scholar",
      "Bohemian Dark Academia": "The Bohemian Scholar",
      "Dark Academia Athleisure": "The Athletic Scholar",
      "Athleisure Dark Academia": "The Athletic Scholar",

      // Minimalist combinations - The Clean Slate
      "Minimalist Streetwear": "The Urban Purist",
      "Streetwear Minimalist": "The Urban Purist",
      "Minimalist Classic": "The Timeless Minimalist",
      "Classic Minimalist": "The Timeless Minimalist",
      "Minimalist Business Casual": "The Corporate Zen",
      "Business Casual Minimalist": "The Corporate Zen",
      "Minimalist Y2K": "The Retro Minimalist",
      "Y2K Minimalist": "The Retro Minimalist",
      "Minimalist Coastal Chic": "The Coastal Minimalist",
      "Coastal Chic Minimalist": "The Coastal Minimalist",
      "Minimalist Techwear": "The Digital Minimalist",
      "Techwear Minimalist": "The Digital Minimalist",
      "Minimalist Grunge": "The Minimalist Rebel",
      "Grunge Minimalist": "The Minimalist Rebel",
      "Minimalist Androgynous": "The Gender-Fluid Minimalist",
      "Androgynous Minimalist": "The Gender-Fluid Minimalist",
      "Minimalist Romantic": "The Romantic Minimalist",
      "Romantic Minimalist": "The Romantic Minimalist",
      "Minimalist Artsy": "The Artistic Minimalist",
      "Artsy Minimalist": "The Artistic Minimalist",
      "Minimalist Bohemian": "The Bohemian Minimalist",
      "Bohemian Minimalist": "The Bohemian Minimalist",
      "Minimalist Athleisure": "The Athletic Minimalist",
      "Athleisure Minimalist": "The Athletic Minimalist",

      // Coastal Chic combinations - The Ocean's Call
      "Coastal Chic Casual Cool": "The Ocean Breeze",
      "Casual Cool Coastal Chic": "The Ocean Breeze",
      "Coastal Chic Cottagecore": "The Seaside Dreamer",
      "Cottagecore Coastal Chic": "The Seaside Dreamer",
      "Coastal Chic Streetwear": "The Beach Rebel",
      "Streetwear Coastal Chic": "The Beach Rebel",
      "Coastal Chic Y2K": "The Coastal Y2K",
      "Y2K Coastal Chic": "The Coastal Y2K",
      "Coastal Chic Techwear": "The Digital Beach",
      "Techwear Coastal Chic": "The Digital Beach",
      "Coastal Chic Grunge": "The Beach Punk",
      "Grunge Coastal Chic": "The Beach Punk",
      "Coastal Chic Androgynous": "The Gender-Fluid Beach",
      "Androgynous Coastal Chic": "The Gender-Fluid Beach",
      "Coastal Chic Romantic": "The Romantic Beach",
      "Romantic Coastal Chic": "The Romantic Beach",
      "Coastal Chic Artsy": "The Artistic Beach",
      "Artsy Coastal Chic": "The Artistic Beach",
      "Coastal Chic Bohemian": "The Bohemian Beach",
      "Bohemian Coastal Chic": "The Bohemian Beach",
      "Coastal Chic Athleisure": "The Athletic Beach",
      "Athleisure Coastal Chic": "The Athletic Beach",

      // Techwear combinations - The Future is Now
      "Techwear Streetwear": "The Digital Nomad",
      "Streetwear Techwear": "The Digital Nomad",
      "Techwear Athleisure": "The Future Athlete",
      "Athleisure Techwear": "The Future Athlete",
      "Techwear Y2K": "The Cyber Y2K",
      "Y2K Techwear": "The Cyber Y2K",
      "Techwear Grunge": "The Cyber Punk",
      "Grunge Techwear": "The Cyber Punk",
      "Techwear Androgynous": "The Gender-Fluid Tech",
      "Androgynous Techwear": "The Gender-Fluid Tech",
      "Techwear Romantic": "The Romantic Tech",
      "Romantic Techwear": "The Romantic Tech",
      "Techwear Artsy": "The Artistic Tech",
      "Artsy Techwear": "The Artistic Tech",
      "Techwear Bohemian": "The Bohemian Tech",
      "Bohemian Techwear": "The Bohemian Tech",

      // Y2K combinations - The Retro Revival
      "Y2K Business Casual": "The Millennial Executive",
      "Business Casual Y2K": "The Millennial Executive",
      "Y2K Streetwear": "The Retro Rebel",
      "Streetwear Y2K": "The Retro Rebel",
      "Y2K Grunge": "The Retro Punk",
      "Grunge Y2K": "The Retro Punk",
      "Y2K Androgynous": "The Gender-Fluid Y2K",
      "Androgynous Y2K": "The Gender-Fluid Y2K",
      "Y2K Romantic": "The Romantic Y2K",
      "Romantic Y2K": "The Romantic Y2K",
      "Y2K Artsy": "The Artistic Y2K",
      "Artsy Y2K": "The Artistic Y2K",
      "Y2K Bohemian": "The Bohemian Y2K",
      "Bohemian Y2K": "The Bohemian Y2K",
      "Y2K Athleisure": "The Athletic Y2K",
      "Athleisure Y2K": "The Athletic Y2K",

      // Grunge combinations - The Rebel Spirit
      "Grunge Classic": "The Refined Rebel",
      "Classic Grunge": "The Refined Rebel",
      "Grunge Androgynous": "The Gender-Fluid Punk",
      "Androgynous Grunge": "The Gender-Fluid Punk",
      "Grunge Romantic": "The Romantic Punk",
      "Romantic Grunge": "The Romantic Punk",
      "Grunge Artsy": "The Artistic Punk",
      "Artsy Grunge": "The Artistic Punk",
      "Grunge Bohemian": "The Bohemian Punk",
      "Bohemian Grunge": "The Bohemian Punk",
      "Grunge Athleisure": "The Athletic Punk",
      "Athleisure Grunge": "The Athletic Punk",

      // Androgynous combinations - The Gender Fluid
      "Androgynous Romantic": "The Gender-Fluid Romantic",
      "Romantic Androgynous": "The Gender-Fluid Romantic",
      "Androgynous Artsy": "The Gender-Fluid Artist",
      "Artsy Androgynous": "The Gender-Fluid Artist",
      "Androgynous Bohemian": "The Gender-Fluid Bohemian",
      "Bohemian Androgynous": "The Gender-Fluid Bohemian",
      "Androgynous Athleisure": "The Gender-Fluid Athlete",
      "Athleisure Androgynous": "The Gender-Fluid Athlete",

      // Romantic combinations - The Dreamer
      "Romantic Artsy": "The Creative Romantic",
      "Artsy Romantic": "The Creative Romantic",
      "Romantic Bohemian": "The Bohemian Romantic",
      "Bohemian Romantic": "The Bohemian Romantic",
      "Romantic Athleisure": "The Athletic Romantic",
      "Athleisure Romantic": "The Athletic Romantic",

      // Streetwear combinations - The Urban Edge
      "Streetwear Grunge": "The Street Punk",
      "Grunge Streetwear": "The Street Punk",
      "Streetwear Athleisure": "The Urban Athlete",
      "Athleisure Streetwear": "The Urban Athlete",
      "Streetwear Androgynous": "The Gender-Fluid Street",
      "Androgynous Streetwear": "The Gender-Fluid Street",
      "Streetwear Romantic": "The Romantic Street",
      "Romantic Streetwear": "The Romantic Street",
      "Streetwear Artsy": "The Artistic Street",
      "Artsy Streetwear": "The Artistic Street",
      "Streetwear Bohemian": "The Bohemian Street",
      "Bohemian Streetwear": "The Bohemian Street",

      // Cottagecore combinations - The Whimsical
      "Cottagecore Artsy": "The Whimsical Artist",
      "Artsy Cottagecore": "The Whimsical Artist",
      "Cottagecore Natural": "The Earth Child",
      "Natural Cottagecore": "The Earth Child",
      "Cottagecore Androgynous": "The Gender-Fluid Cottage",
      "Androgynous Cottagecore": "The Gender-Fluid Cottage",
      "Cottagecore Romantic": "The Whimsical Dreamer",
      "Romantic Cottagecore": "The Whimsical Dreamer",
      "Cottagecore Bohemian": "The Bohemian Cottage",
      "Bohemian Cottagecore": "The Bohemian Cottage",
      "Cottagecore Athleisure": "The Athletic Cottage",
      "Athleisure Cottagecore": "The Athletic Cottage",

      // Edgy combinations - The Sophisticated Edge
      "Edgy Business Casual": "The Corporate Rebel",
      "Business Casual Edgy": "The Corporate Rebel",
      "Edgy Classic": "The Sophisticated Edge",
      "Classic Edgy": "The Sophisticated Edge",
      "Edgy Androgynous": "The Gender-Fluid Edge",
      "Androgynous Edgy": "The Gender-Fluid Edge",
      "Edgy Romantic": "The Romantic Edge",
      "Romantic Edgy": "The Romantic Edge",
      "Edgy Artsy": "The Artistic Edge",
      "Artsy Edgy": "The Artistic Edge",
      "Edgy Bohemian": "The Bohemian Edge",
      "Bohemian Edgy": "The Bohemian Edge",
      "Edgy Athleisure": "The Athletic Edge",
      "Athleisure Edgy": "The Athletic Edge",

      // Preppy combinations - The Collegiate
      "Preppy Minimalist": "The Sophisticated Minimalist",
      "Minimalist Preppy": "The Sophisticated Minimalist",
      "Preppy Classic": "The Ivy League Classic",
      "Classic Preppy": "The Ivy League Classic",
      "Preppy Androgynous": "The Gender-Fluid Preppy",
      "Androgynous Preppy": "The Gender-Fluid Preppy",
      "Preppy Romantic": "The Romantic Preppy",
      "Romantic Preppy": "The Romantic Preppy",
      "Preppy Artsy": "The Artistic Preppy",
      "Artsy Preppy": "The Artistic Preppy",
      "Preppy Bohemian": "The Bohemian Preppy",
      "Bohemian Preppy": "The Bohemian Preppy",
      "Preppy Athleisure": "The Athletic Preppy",
      "Athleisure Preppy": "The Athletic Preppy",

      // Elegant combinations - The Sophisticated
      "Elegant Classic": "The Timeless Elegance",
      "Classic Elegant": "The Timeless Elegance",
      "Elegant Androgynous": "The Gender-Fluid Elegance",
      "Androgynous Elegant": "The Gender-Fluid Elegance",
      "Elegant Romantic": "The Romantic Elegance",
      "Romantic Elegant": "The Romantic Elegance",
      "Elegant Artsy": "The Artistic Elegance",
      "Artsy Elegant": "The Artistic Elegance",
      "Elegant Bohemian": "The Bohemian Elegance",
      "Bohemian Elegant": "The Bohemian Elegance",
      "Elegant Athleisure": "The Athletic Elegance",
      "Athleisure Elegant": "The Athletic Elegance",

      // Academic combinations - The Intellectual
      "Academic Classic": "The Scholarly Classic",
      "Classic Academic": "The Scholarly Classic",
      "Academic Androgynous": "The Gender-Fluid Academic",
      "Androgynous Academic": "The Gender-Fluid Academic",
      "Academic Romantic": "The Romantic Academic",
      "Romantic Academic": "The Romantic Academic",
      "Academic Artsy": "The Artistic Academic",
      "Artsy Academic": "The Artistic Academic",
      "Academic Bohemian": "The Bohemian Academic",
      "Bohemian Academic": "The Bohemian Academic",
      "Academic Athleisure": "The Athletic Academic",
      "Athleisure Academic": "The Athletic Academic",

      // Artsy combinations - The Creative
      "Artsy Bohemian": "The Creative Free Spirit",
      "Bohemian Artsy": "The Creative Free Spirit",
      "Artsy Natural": "The Artistic Naturalist",
      "Natural Artsy": "The Artistic Naturalist",
      "Artsy Androgynous": "The Gender-Fluid Artist",
      "Androgynous Artsy": "The Gender-Fluid Artist",
      "Artsy Romantic": "The Creative Romantic",
      "Romantic Artsy": "The Creative Romantic",
      "Artsy Athleisure": "The Athletic Artist",
      "Athleisure Artsy": "The Athletic Artist",

      // Bohemian combinations - The Free Spirit
      "Bohemian Natural": "The Free Spirit",
      "Natural Bohemian": "The Free Spirit",
      "Bohemian Androgynous": "The Gender-Fluid Bohemian",
      "Androgynous Bohemian": "The Gender-Fluid Bohemian",
      "Bohemian Romantic": "The Bohemian Romantic",
      "Romantic Bohemian": "The Bohemian Romantic",
      "Bohemian Athleisure": "The Athletic Bohemian",
      "Athleisure Bohemian": "The Athletic Bohemian",

      // Natural combinations - The Earth Conscious
      "Natural Androgynous": "The Gender-Fluid Naturalist",
      "Androgynous Natural": "The Gender-Fluid Naturalist",
      "Natural Romantic": "The Romantic Naturalist",
      "Romantic Natural": "The Romantic Naturalist",
      "Natural Athleisure": "The Athletic Naturalist",
      "Athleisure Natural": "The Athletic Naturalist",

      // Casual Cool combinations - The Effortless
      "Casual Cool Androgynous": "The Gender-Fluid Casual",
      "Androgynous Casual Cool": "The Gender-Fluid Casual",
      "Casual Cool Romantic": "The Romantic Casual",
      "Romantic Casual Cool": "The Romantic Casual",
      "Casual Cool Artsy": "The Artistic Casual",
      "Artsy Casual Cool": "The Artistic Casual",
      "Casual Cool Bohemian": "The Bohemian Casual",
      "Bohemian Casual Cool": "The Bohemian Casual",
      "Casual Cool Athleisure": "The Athletic Casual",
      "Athleisure Casual Cool": "The Athletic Casual",

      // Athleisure combinations - The Active
      "Athleisure Androgynous": "The Gender-Fluid Athlete",
      "Androgynous Athleisure": "The Gender-Fluid Athlete",
      "Athleisure Romantic": "The Athletic Romantic",
      "Romantic Athleisure": "The Athletic Romantic",
      "Athleisure Artsy": "The Athletic Artist",
      "Artsy Athleisure": "The Athletic Artist",
      "Athleisure Bohemian": "The Athletic Bohemian",
      "Bohemian Athleisure": "The Athletic Bohemian",

      // Additional Ultra-Snazzy Combinations
      "Business Casual Classic": "The Corporate Classic",
      "Classic Business Casual": "The Corporate Classic",
      "Business Casual Elegant": "The Sophisticated Professional",
      "Elegant Business Casual": "The Sophisticated Professional",
      "Business Casual Academic": "The Intellectual Professional",
      "Academic Business Casual": "The Intellectual Professional",
      "Business Casual Preppy": "The Collegiate Professional",
      "Preppy Business Casual": "The Collegiate Professional",
      "Business Casual Natural": "The Natural Professional",
      "Natural Business Casual": "The Natural Professional",
      "Business Casual Cottagecore": "The Cottage Professional",
      "Cottagecore Business Casual": "The Cottage Professional",
      "Business Casual Coastal Chic": "The Coastal Professional",
      "Coastal Chic Business Casual": "The Coastal Professional",
      "Business Casual Techwear": "The Tech Professional",
      "Techwear Business Casual": "The Tech Professional",
      "Business Casual Y2K": "The Millennial Professional",
      "Y2K Business Casual": "The Millennial Professional",
      "Business Casual Grunge": "The Corporate Rebel",
      "Grunge Business Casual": "The Corporate Rebel",
      "Business Casual Androgynous": "The Gender-Fluid Professional",
      "Androgynous Business Casual": "The Gender-Fluid Professional",
      "Business Casual Romantic": "The Romantic Professional",
      "Romantic Business Casual": "The Romantic Professional",
      "Business Casual Artsy": "The Artistic Professional",
      "Artsy Business Casual": "The Artistic Professional",
      "Business Casual Bohemian": "The Bohemian Professional",
      "Bohemian Business Casual": "The Bohemian Professional",
      "Business Casual Athleisure": "The Active Professional",
      "Athleisure Business Casual": "The Active Professional",

      // Classic combinations - The Timeless
      "Classic Elegant": "The Timeless Elegance",
      "Elegant Classic": "The Timeless Elegance",
      "Classic Academic": "The Scholarly Classic",
      "Academic Classic": "The Scholarly Classic",
      "Classic Preppy": "The Ivy League Classic",
      "Preppy Classic": "The Ivy League Classic",
      "Classic Natural": "The Natural Classic",
      "Natural Classic": "The Natural Classic",
      "Classic Cottagecore": "The Cottage Classic",
      "Cottagecore Classic": "The Cottage Classic",
      "Classic Coastal Chic": "The Coastal Classic",
      "Coastal Chic Classic": "The Coastal Classic",
      "Classic Techwear": "The Tech Classic",
      "Techwear Classic": "The Tech Classic",
      "Classic Y2K": "The Y2K Classic",
      "Y2K Classic": "The Y2K Classic",
      "Classic Grunge": "The Refined Rebel",
      "Grunge Classic": "The Refined Rebel",
      "Classic Androgynous": "The Gender-Fluid Classic",
      "Androgynous Classic": "The Gender-Fluid Classic",
      "Classic Romantic": "The Romantic Classic",
      "Romantic Classic": "The Romantic Classic",
      "Classic Artsy": "The Artistic Classic",
      "Artsy Classic": "The Artistic Classic",
      "Classic Bohemian": "The Bohemian Classic",
      "Bohemian Classic": "The Bohemian Classic",
      "Classic Athleisure": "The Athletic Classic",
      "Athleisure Classic": "The Athletic Classic",

      // Elegant combinations - The Sophisticated
      "Elegant Academic": "The Scholarly Elegance",
      "Academic Elegant": "The Scholarly Elegance",
      "Elegant Preppy": "The Preppy Elegance",
      "Preppy Elegant": "The Preppy Elegance",
      "Elegant Natural": "The Natural Elegance",
      "Natural Elegant": "The Natural Elegance",
      "Elegant Cottagecore": "The Cottage Elegance",
      "Cottagecore Elegant": "The Cottage Elegance",
      "Elegant Coastal Chic": "The Coastal Elegance",
      "Coastal Chic Elegant": "The Coastal Elegance",
      "Elegant Techwear": "The Tech Elegance",
      "Techwear Elegant": "The Tech Elegance",
      "Elegant Y2K": "The Y2K Elegance",
      "Y2K Elegant": "The Y2K Elegance",
      "Elegant Grunge": "The Grunge Elegance",
      "Grunge Elegant": "The Grunge Elegance",
      "Elegant Androgynous": "The Gender-Fluid Elegance",
      "Androgynous Elegant": "The Gender-Fluid Elegance",
      "Elegant Romantic": "The Romantic Elegance",
      "Romantic Elegant": "The Romantic Elegance",
      "Elegant Artsy": "The Artistic Elegance",
      "Artsy Elegant": "The Artistic Elegance",
      "Elegant Bohemian": "The Bohemian Elegance",
      "Bohemian Elegant": "The Bohemian Elegance",
      "Elegant Athleisure": "The Athletic Elegance",
      "Athleisure Elegant": "The Athletic Elegance"
    };

    const key = `${style1} ${style2}`;
    const reverseKey = `${style2} ${style1}`;

    // Try exact matches first
    if (archetypeMap[key]) {
      return archetypeMap[key];
    }
    
    if (archetypeMap[reverseKey]) {
      return archetypeMap[reverseKey];
    }

    // Try partial matches for more flexible matching
    const allKeys = Object.keys(archetypeMap);
    const style1Lower = style1.toLowerCase();
    const style2Lower = style2.toLowerCase();
    
    // Look for keys that contain both style names (in any order)
    for (const mapKey of allKeys) {
      const mapKeyLower = mapKey.toLowerCase();
      if (mapKeyLower.includes(style1Lower) && mapKeyLower.includes(style2Lower)) {
        return archetypeMap[mapKey];
      }
    }

    // Fallback: create a creative name based on the styles
    const styleAdjectives: Record<string, string> = {
      'minimalist': 'Refined',
      'preppy': 'Elite',
      'streetwear': 'Urban',
      'grunge': 'Rebel',
      'classic': 'Timeless',
      'elegant': 'Sophisticated',
      'academic': 'Intellectual',
      'artsy': 'Creative',
      'bohemian': 'Free-Spirited',
      'romantic': 'Dreamy',
      'athleisure': 'Athletic',
      'techwear': 'Digital',
      'y2k': 'Retro',
      'coastal': 'Oceanic',
      'cottagecore': 'Whimsical',
      'natural': 'Earth-Conscious',
      'androgynous': 'Gender-Fluid',
      'casual': 'Effortless',
      'business': 'Professional',
      'formal': 'Distinguished'
    };

    const adj1 = styleAdjectives[style1Lower] || style1;
    const adj2 = styleAdjectives[style2Lower] || style2;
    
    return `The ${adj1} ${adj2}`;
  };

  // Handle quiz completion
  const handleComplete = () => {
    // Clear any cached data and start fresh
    const timestamp = Date.now();
    
    const primaryStyles = getPrimaryStyles();
    const secondaryStyles = getSecondaryStyles();
    const primaryColors = getPrimaryColors();
    
    // Create creative hybrid style name with cache-busting
    const hybridStyle = getCreativeArchetypeName(primaryStyles);

    // Calculate alignment score
    const totalLikes = likedOutfits.length;
    const totalOutfits = likedOutfits.length + dislikedOutfits.length;
    const alignmentScore = totalOutfits > 0 ? (totalLikes / totalOutfits) * 100 : 0;

    // Create structured color palette
    const colorPalette = {
      primary: primaryColors.slice(0, 4),
      secondary: primaryColors.slice(4, 6),
      accent: primaryColors.slice(6, 8),
      neutral: [],
      avoid: []
    };

    console.log('=== OUTFIT QUIZ COMPLETION DEBUG (FRESH) ===');
    console.log('Timestamp:', timestamp);
    console.log('Primary styles detected:', primaryStyles);
    console.log('Secondary styles detected:', secondaryStyles);
    console.log('Primary colors detected:', primaryColors);
    console.log('Generated hybrid style name:', hybridStyle);
    console.log('=====================================');

    setStylePreferences({
      stylePreferences: primaryStyles as any,
      preferredColors: primaryColors,
      quizResponses: [
        {
          questionId: "outfit_quiz",
          answer: likedOutfits,
          confidence: Math.round(Math.max(...styleConfidence.map(s => s.confidence)) * 100)
        }
      ],
      colorPalette: colorPalette, // Save structured color palette
      hybridStyleName: hybridStyle, // Save the hybrid style name
      alignmentScore: alignmentScore // Save the alignment score
    });

    // Since this is now the final step, call onNext to complete onboarding
    onNext();
  };

  // Show confidence indicators
  const renderConfidenceIndicators = () => {
    if (likedOutfits.length < 3) return null;

    const highConfidenceStyles = styleConfidence.filter(s => s.confidence >= confidenceThreshold);
    const highConfidenceColors = colorConfidence.filter(c => c.confidence >= confidenceThreshold);

    // Calculate style exposure progress
    const minExposurePerStyle = 2;
    const styleProgress = Array.from(allStyles).map(style => ({
      style,
      exposure: styleExposure[style] || 0,
      complete: (styleExposure[style] || 0) >= minExposurePerStyle
    }));

    const completedStyles = styleProgress.filter(s => s.complete).length;
    const totalStyles = styleProgress.length;

    return (
      <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h3 className="text-sm font-semibold text-blue-800 mb-2">
          🎯 Style Detection Progress
        </h3>
        <div className="space-y-2">
          {/* Style Exposure Progress */}
          <div className="flex items-center gap-2">
            <span className="text-blue-600">📊</span>
            <span className="text-sm text-blue-700">
              Style exposure: {completedStyles}/{totalStyles} styles seen ({minExposurePerStyle} outfits each)
            </span>
          </div>
          
          {/* Style Progress Bars */}
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mt-3">
            {styleProgress.map(({ style, exposure, complete }) => (
              <div key={style} className="flex items-center gap-2">
                <span className={`text-xs ${complete ? 'text-green-600' : 'text-gray-500'}`}>
                  {complete ? '✓' : '○'}
                </span>
                <span className="text-xs text-gray-700 truncate">{style}</span>
                <span className="text-xs text-gray-500">({exposure}/{minExposurePerStyle})</span>
              </div>
            ))}
          </div>

          {highConfidenceStyles.length > 0 && (
            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-blue-200">
              <span className="text-green-600">✓</span>
              <span className="text-sm text-blue-700">
                High confidence in: {highConfidenceStyles.map(s => s.style).join(", ")}
              </span>
            </div>
          )}
          {highConfidenceColors.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-green-600">✓</span>
              <span className="text-sm text-blue-700">
                Color preferences detected: {highConfidenceColors.map(c => c.color).join(", ")}
              </span>
            </div>
          )}
          {quizComplete && (
            <div className="flex items-center gap-2 mt-2">
              <span className="text-green-600 font-bold">🎉</span>
              <span className="text-sm font-semibold text-green-700">
                High confidence reached! Quiz complete.
              </span>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (showResults) {
    const primaryStyles = getPrimaryStyles();
    const secondaryStyles = getSecondaryStyles();
    const primaryColors = getPrimaryColors();
    const hybridStyle = getCreativeArchetypeName(primaryStyles);

    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
            🎉 Your Style Profile Complete!
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            We've analyzed your preferences and detected your unique style signature.
          </p>
        </div>

        <div className="space-y-6">
          {/* Hybrid Style */}
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 dark:from-purple-950 dark:to-pink-950 p-6 rounded-lg border border-purple-200 dark:border-purple-800">
            <h3 className="text-lg font-semibold text-purple-800 dark:text-purple-200 mb-2">
              Your Style Archetype
            </h3>
            <div className="text-3xl font-bold text-purple-900 dark:text-purple-100 mb-2">
              {hybridStyle}
            </div>
            <p className="text-purple-700 dark:text-purple-300">
              A unique blend of {primaryStyles.join(" and ")} aesthetics
            </p>
          </div>

          {/* Color Palette - Made More Prominent */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 p-6 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                <span className="text-white text-lg">🎨</span>
              </div>
              <h3 className="text-xl font-bold text-blue-900 dark:text-blue-100">Your Signature Color Palette</h3>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {primaryColors.map(color => (
                <div key={color} className="text-center">
                  <div className="w-12 h-12 mx-auto mb-2 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-500 flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-700 dark:text-gray-300">●</span>
                  </div>
                  <span className="text-sm font-medium text-blue-800 dark:text-blue-200">{color}</span>
                </div>
              ))}
            </div>
            <p className="text-blue-700 dark:text-blue-300 text-sm mt-4 text-center">
              These colors reflect your natural preferences and will guide your style choices
            </p>
          </div>

          {/* Style Breakdown */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border dark:border-gray-700">
              <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Primary Styles</h4>
              <div className="space-y-1">
                {primaryStyles.map(style => (
                  <div key={style} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">{style}</span>
                    <span className="text-xs bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 px-2 py-1 rounded">
                      High Confidence
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 p-4 rounded-lg border dark:border-gray-700">
              <h4 className="font-semibold text-gray-800 dark:text-gray-200 mb-2">Secondary Influences</h4>
              <div className="space-y-1">
                {secondaryStyles.map(style => (
                  <div key={style} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-400">{style}</span>
                    <span className="text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 px-2 py-1 rounded">
                      Moderate
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8 flex justify-center">
          <button
            onClick={handleComplete}
            className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Complete Onboarding
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
          Style Discovery Quiz
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Like or dislike outfits to help us understand your style preferences. We'll show you at least 2 outfits from each style category to ensure you get a complete understanding of your preferences!
        </p>
      </div>

      {/* Progress indicator */}
      <div className="flex items-center justify-center gap-2 mb-4">
        <span className="text-sm text-gray-600 dark:text-gray-400">
          Progress: {currentOutfitIndex + 1} of {genderFilteredOutfits.length}
        </span>
        <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
          <div 
            className="bg-purple-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentOutfitIndex + 1) / genderFilteredOutfits.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Confidence indicators */}
      {renderConfidenceIndicators()}

      {/* Current Outfit */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 shadow-sm overflow-hidden">
        <div className="aspect-square bg-gray-100 dark:bg-gray-700 flex items-center justify-center relative">
          {/* Debug info - remove in production */}
          <div className="absolute top-2 left-2 text-xs text-gray-500 dark:text-gray-400 bg-white dark:bg-gray-800 px-2 py-1 rounded opacity-75 z-10">
            {currentOutfit.id} - {currentOutfit.imageUrl}
          </div>
          
          <img
            src={`${currentOutfit.imageUrl}?v=2`}
            alt={currentOutfit.description}
            className="w-full h-full object-contain"
            onError={(e) => {
              console.error('Image failed to load:', currentOutfit.imageUrl);
              e.currentTarget.style.display = 'none';
              // Show fallback content
              const fallback = document.createElement('div');
              fallback.className = 'flex flex-col items-center justify-center text-gray-500 dark:text-gray-400 p-4';
              fallback.innerHTML = `
                <div class="text-6xl mb-4">👕</div>
                <div class="text-center">
                  <div class="text-sm font-medium mb-2">${currentOutfit.description}</div>
                  <div class="text-xs text-gray-400 dark:text-gray-500">Image not available</div>
                </div>
              `;
              e.currentTarget.parentNode?.appendChild(fallback);
            }}
            onLoad={() => {
              console.log('Image loaded successfully:', currentOutfit.imageUrl);
            }}
          />
        </div>
        
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
            {currentOutfit.description}
          </h3>
          
          <div className="flex flex-wrap gap-2 mb-4">
            {Object.entries(currentOutfit.styles).map(([style, weight]) => (
              <span
                key={style}
                className="px-2 py-1 text-xs rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
              >
                {style}
              </span>
            ))}
          </div>

          <div className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            <p><strong>Palette:</strong> {currentOutfit.palette}</p>
            <p><strong>Silhouette:</strong> {currentOutfit.silhouette}</p>
            <p><strong>Formality:</strong> {currentOutfit.formality}</p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => handleOutfitReaction(false)}
              className="flex-1 bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-300 py-3 px-4 rounded-lg font-semibold hover:bg-red-100 dark:hover:bg-red-900 transition-colors border border-red-200 dark:border-red-800"
            >
              👎 Not My Style
            </button>
            <button
              onClick={() => handleOutfitReaction(true)}
              className="flex-1 bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 py-3 px-4 rounded-lg font-semibold hover:bg-green-100 dark:hover:bg-green-900 transition-colors border border-green-200 dark:border-green-800"
            >
              👍 Love This!
            </button>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="mt-6 flex justify-between">
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {likedOutfits.length} liked • {dislikedOutfits.length} disliked
        </div>
      </div>
    </div>
  );
} 