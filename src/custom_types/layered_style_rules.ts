// This is a layered fashion rules matrix for an outfit generation engine.
// It defines what must be avoided, should be avoided, and can optionally work
// depending on context, based on StyleType + Subtype combos.

import { StyleType } from './style_types';
import { ActivitySubtype, WeatherSubtype, FormalitySubtype } from './style_types';

export type StyleSubtype = ActivitySubtype | WeatherSubtype | FormalitySubtype;

export interface LayeredStyleRule {
  styleType: StyleType;
  subtypes: StyleSubtype[];
  mustNeverInclude: string[]; // Hard constraint
  shouldAvoid: string[];      // Soft constraint
  canSometimesWork: string[]; // Situationally valid
  notes?: string;
  metadata?: {
    importance?: 'strict' | 'moderate' | 'loose';
    riskLevel?: 'high' | 'medium' | 'low';
  };
}

export const layeredStyleRules: LayeredStyleRule[] = [
  {
    styleType: "Romantic",
    subtypes: ["Office"],
    mustNeverInclude: ["corsets", "lace bralettes"],
    shouldAvoid: ["tulle skirts"],
    canSometimesWork: ["silk blouse", "delicate pearl accessories"],
    notes: "Keep it dreamy but office-appropriate.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Boho",
    subtypes: ["Rainy Day"],
    mustNeverInclude: ["fringe sandals", "flowy maxis dragging on ground"],
    shouldAvoid: ["crochet cardigans"],
    canSometimesWork: ["wide-brim rain hat", "embroidered rainproof poncho"],
    notes: "Preserve boho vibe while staying dry.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Grunge",
    subtypes: ["Hot Weather"],
    mustNeverInclude: ["leather pants", "heavy flannel layers"],
    shouldAvoid: ["combat boots all day"],
    canSometimesWork: ["distressed denim shorts", "band tee"],
    notes: "Tone down layers, keep the attitude.",
    metadata: { importance: "moderate", riskLevel: "low" }
  },
  {
    styleType: "Techwear",
    subtypes: ["Date Night"],
    mustNeverInclude: ["tactical vests", "utility pouches"],
    shouldAvoid: ["overly baggy silhouettes"],
    canSometimesWork: ["sleek modular jacket", "dark tech-fabric joggers"],
    notes: "Channel sleekness, not survival mode.",
    metadata: { importance: "strict", riskLevel: "medium" }
  },
  {
    styleType: "Dark Academia",
    subtypes: ["Office"],
    mustNeverInclude: ["wool blazers", "dark tights"],
    shouldAvoid: ["layered knits"],
    canSometimesWork: ["linen poet blouse", "earthy midi skirt"],
    notes: "Make academia breathable and poetic outdoors.",
    metadata: { importance: "moderate", riskLevel: "low" }
  },
  {
    styleType: "Old Money",
    subtypes: ["Business"],
    mustNeverInclude: ["logos", "trendy pieces"],
    shouldAvoid: ["casual items"],
    canSometimesWork: ["polo shirt", "pleated trousers"],
    notes: "Keep it classic and refined.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Streetwear",
    subtypes: ["Casual"],
    mustNeverInclude: ["formal wear", "preppy items"],
    shouldAvoid: ["traditional pieces"],
    canSometimesWork: ["hoodie", "sneakers"],
    notes: "Keep it urban and trendy.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Y2K",
    subtypes: ["Party"],
    mustNeverInclude: ["modest cuts", "classic tailoring"],
    shouldAvoid: ["formal wear"],
    canSometimesWork: ["baby tees", "low-rise jeans"],
    notes: "Embrace the Y2K aesthetic.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Minimalist",
    subtypes: ["Business Casual"],
    mustNeverInclude: ["bold prints", "excess accessories"],
    shouldAvoid: ["trendy pieces"],
    canSometimesWork: ["white shirt", "tailored pants"],
    notes: "Keep it clean and simple.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Boho",
    subtypes: ["Casual"],
    mustNeverInclude: ["structured pieces", "minimalist items"],
    shouldAvoid: ["formal wear"],
    canSometimesWork: ["flowy maxi dress", "fringed vest"],
    notes: "Embrace the bohemian spirit.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Preppy",
    subtypes: ["Business Casual"],
    mustNeverInclude: ["grunge items", "streetwear"],
    shouldAvoid: ["casual items"],
    canSometimesWork: ["polo shirt", "chinos"],
    notes: "Keep it classic and polished.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Grunge",
    subtypes: ["Casual"],
    mustNeverInclude: ["preppy items", "formal wear"],
    shouldAvoid: ["sweet pieces"],
    canSometimesWork: ["flannel shirt", "ripped jeans"],
    notes: "Keep the grunge aesthetic.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Classic",
    subtypes: ["Business"],
    mustNeverInclude: ["trendy pieces", "casual items"],
    shouldAvoid: ["bold prints"],
    canSometimesWork: ["blazer", "white shirt"],
    notes: "Keep it timeless and elegant.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Techwear",
    subtypes: ["Casual"],
    mustNeverInclude: ["casual items", "formal wear"],
    shouldAvoid: ["traditional pieces"],
    canSometimesWork: ["cargo pants", "technical jacket"],
    notes: "Keep it technical and functional.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Androgynous",
    subtypes: ["Business"],
    mustNeverInclude: ["overtly feminine pieces", "overtly masculine pieces"],
    shouldAvoid: ["gender-specific items"],
    canSometimesWork: ["tailored suit", "structured jacket"],
    notes: "Keep it gender-neutral and sophisticated.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Coastal Chic",
    subtypes: ["Casual"],
    mustNeverInclude: ["trendy pieces", "heavy materials"],
    shouldAvoid: ["formal wear"],
    canSometimesWork: ["linen dress", "straw hat"],
    notes: "Keep it breezy and coastal.",
    metadata: { importance: "moderate", riskLevel: "low" }
  },
  {
    styleType: "Business Casual",
    subtypes: ["Business"],
    mustNeverInclude: ["jeans", "sneakers", "casual t-shirts"],
    shouldAvoid: ["formal wear"],
    canSometimesWork: ["blazer", "button-down shirt"],
    notes: "Keep it professional yet relaxed.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Avant-Garde",
    subtypes: ["Special Occasion"],
    mustNeverInclude: ["traditional pieces", "basic items"],
    shouldAvoid: ["conventional items"],
    canSometimesWork: ["structured pieces", "unconventional shapes"],
    notes: "Keep it artistic and innovative.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    styleType: "Cottagecore",
    subtypes: ["Casual"],
    mustNeverInclude: ["modern pieces", "minimalist items"],
    shouldAvoid: ["urban items"],
    canSometimesWork: ["floral dress", "puff sleeves"],
    notes: "Keep it romantic and rustic.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Edgy",
    subtypes: ["Casual"],
    mustNeverInclude: ["preppy items", "sweet pieces"],
    shouldAvoid: ["traditional pieces"],
    canSometimesWork: ["leather jacket", "ripped jeans"],
    notes: "Keep it bold and rebellious.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Athleisure",
    subtypes: ["Casual"],
    mustNeverInclude: ["formal wear", "heavy materials"],
    shouldAvoid: ["traditional pieces"],
    canSometimesWork: ["leggings", "sports bra"],
    notes: "Keep it sporty and comfortable.",
    metadata: { importance: "moderate", riskLevel: "low" }
  },
  {
    styleType: "Casual Cool",
    subtypes: ["Casual"],
    mustNeverInclude: ["formal wear", "overly casual items"],
    shouldAvoid: ["trendy pieces"],
    canSometimesWork: ["denim jacket", "white tee"],
    notes: "Keep it relaxed yet stylish.",
    metadata: { importance: "moderate", riskLevel: "low" }
  },
  {
    styleType: "Romantic",
    subtypes: ["Special Occasion"],
    mustNeverInclude: ["harsh pieces", "minimalist items"],
    shouldAvoid: ["masculine pieces"],
    canSometimesWork: ["floral dress", "lace details"],
    notes: "Keep it soft and feminine.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    styleType: "Artsy",
    subtypes: ["Special Occasion"],
    mustNeverInclude: ["basic items", "traditional pieces"],
    shouldAvoid: ["conventional items"],
    canSometimesWork: ["unique pieces", "artistic elements"],
    notes: "Keep it creative and unique.",
    metadata: { importance: "strict", riskLevel: "high" }
  }
];

export interface MaterialLayeringRule {
  baseMaterial: string;
  mustNeverLayerWith: string[];  // Hard constraint
  shouldAvoidLayeringWith: string[];  // Soft constraint
  canSometimesLayerWith: string[];  // Situationally valid
  notes?: string;
  metadata?: {
    importance?: 'strict' | 'moderate' | 'loose';
    riskLevel?: 'high' | 'medium' | 'low';
  };
}

export const materialLayeringRules: MaterialLayeringRule[] = [
  {
    baseMaterial: "silk",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["light wool", "cashmere", "light cotton"],
    notes: "Silk is delicate and requires careful layering to prevent damage.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "wool",
    mustNeverLayerWith: ["silk", "delicate fabrics"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick denim"],
    canSometimesLayerWith: ["cotton", "linen", "light knits"],
    notes: "Wool can be scratchy and may damage delicate fabrics.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    baseMaterial: "leather",
    mustNeverLayerWith: ["silk", "delicate fabrics", "light wool"],
    shouldAvoidLayeringWith: ["heavy knits", "thick wool"],
    canSometimesLayerWith: ["denim", "cotton", "synthetic fabrics"],
    notes: "Leather is durable but can damage delicate fabrics.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "denim",
    mustNeverLayerWith: ["silk", "delicate fabrics"],
    shouldAvoidLayeringWith: ["heavy wool", "thick knits"],
    canSometimesLayerWith: ["cotton", "leather", "synthetic fabrics"],
    notes: "Denim is durable but can be rough on delicate fabrics.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    baseMaterial: "cotton",
    mustNeverLayerWith: [],
    shouldAvoidLayeringWith: ["heavy wool", "thick knits"],
    canSometimesLayerWith: ["denim", "linen", "light wool", "silk"],
    notes: "Cotton is versatile and works well with most fabrics.",
    metadata: { importance: "loose", riskLevel: "low" }
  },
  {
    baseMaterial: "linen",
    mustNeverLayerWith: ["rough wool", "denim"],
    shouldAvoidLayeringWith: ["heavy knits", "thick wool"],
    canSometimesLayerWith: ["cotton", "silk", "light wool"],
    notes: "Linen is breathable but can be damaged by rough fabrics.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    baseMaterial: "cashmere",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["silk", "light wool", "cotton"],
    notes: "Cashmere is luxurious but requires careful layering.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "synthetic",
    mustNeverLayerWith: [],
    shouldAvoidLayeringWith: ["delicate fabrics", "silk"],
    canSometimesLayerWith: ["cotton", "denim", "wool"],
    notes: "Synthetic fabrics are durable but can cause static.",
    metadata: { importance: "loose", riskLevel: "low" }
  },
  {
    baseMaterial: "knit",
    mustNeverLayerWith: ["silk", "delicate fabrics"],
    shouldAvoidLayeringWith: ["heavy wool", "thick denim"],
    canSometimesLayerWith: ["cotton", "light wool", "synthetic fabrics"],
    notes: "Knits can be bulky and may damage delicate fabrics.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    baseMaterial: "velvet",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["silk", "light wool", "cotton"],
    notes: "Velvet is delicate and requires careful layering.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "suede",
    mustNeverLayerWith: ["silk", "delicate fabrics", "light wool"],
    shouldAvoidLayeringWith: ["heavy knits", "thick wool"],
    canSometimesLayerWith: ["cotton", "denim", "synthetic fabrics"],
    notes: "Suede is delicate and can be damaged by rough fabrics.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "fleece",
    mustNeverLayerWith: ["silk", "delicate fabrics"],
    shouldAvoidLayeringWith: ["heavy wool", "thick denim"],
    canSometimesLayerWith: ["cotton", "synthetic fabrics", "light wool"],
    notes: "Fleece is warm but can cause static with certain fabrics.",
    metadata: { importance: "moderate", riskLevel: "medium" }
  },
  {
    baseMaterial: "sequin",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["silk", "light wool", "cotton"],
    notes: "Sequins can damage delicate fabrics and snag on rough materials.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "lace",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["silk", "light wool", "cotton"],
    notes: "Lace is delicate and requires careful layering.",
    metadata: { importance: "strict", riskLevel: "high" }
  },
  {
    baseMaterial: "satin",
    mustNeverLayerWith: ["rough wool", "denim", "leather"],
    shouldAvoidLayeringWith: ["heavy cotton", "thick knits"],
    canSometimesLayerWith: ["silk", "light wool", "cotton"],
    notes: "Satin is delicate and requires careful layering.",
    metadata: { importance: "strict", riskLevel: "high" }
  }
]; 