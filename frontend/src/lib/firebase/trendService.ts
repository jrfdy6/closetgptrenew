import {
  collection,
  doc,
  getDocs,
  getDoc,
  addDoc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy,
  limit,
  Timestamp,
} from "firebase/firestore";
import { db } from "./index";

// Types
export type TrendCategory =
  | "Quiet Luxury"
  | "Gorpcore"
  | "Old Money"
  | "Grandpacore"
  | "Dark Academia"
  | "Coquette"
  | "Cottagecore"
  | "Mob Wife"
  | "Balletcore"
  | "Gothcore"
  | "Boho Chic"
  | "Preppy";

export type TrendSubCategory =
  | "Knitwear"
  | "Cardigans"
  | "Turtlenecks"
  | "Argyle"
  | "Outerwear"
  | "Henley"
  | "Cargo"
  | "Vintage"
  | "Overcoats"
  | "Earth Tones"
  | "Monochromatic"
  | "Plaid"
  | "Pastel"
  | "Bold Prints"
  | "Neon"
  | "Camouflage"
  | "Tie-Dye"
  | "Color Blocking"
  | "Metallic"
  | "Sneakers"
  | "Loafers"
  | "Combat Boots"
  | "Slip-Ons"
  | "High-Tops"
  | "Espadrilles"
  | "Sandals"
  | "Moccasins"
  | "Chelsea Boots"
  | "Derby Shoes"
  | "Beanies"
  | "Bucket Hats"
  | "Crossbody Bags"
  | "Statement Belts"
  | "Layered Necklaces"
  | "Bracelets"
  | "Sunglasses"
  | "Watches"
  | "Scarves"
  | "Gloves"
  | "Linen"
  | "Shorts Suits"
  | "Layered Outerwear"
  | "Flannel"
  | "Puffer"
  | "Raincoats"
  | "Thermal"
  | "Swim"
  | "Denim"
  | "Track Suits"
  | "Scandinavian"
  | "Italian"
  | "British"
  | "American"
  | "Japanese"
  | "French"
  | "African"
  | "Latin American"
  | "Middle Eastern"
  | "Indian";

export type TrendSeason = "Spring" | "Summer" | "Fall" | "Winter";

export interface TrendFilter {
  category?: TrendCategory;
  subCategory?: TrendSubCategory;
  season?: TrendSeason;
  minPopularity?: number;
  minEngagement?: number;
  gender?: "Men" | "Women" | "Unisex";
  priceRange?: "Budget" | "Mid-Range" | "Luxury";
  sustainable?: boolean;
}

export interface FashionTrend {
  id: string;
  name: string;
  category: TrendCategory;
  subCategories: TrendSubCategory[];
  season: TrendSeason;
  popularity: number;
  description: string;
  keyItems: string[];
  createdAt: Date;
  updatedAt: Date;
  gender: "Men" | "Women" | "Unisex";
  priceRange: "Budget" | "Mid-Range" | "Luxury";
  sustainability: boolean;
  culturalInfluence?: string;
  colorPalette?: string[];
  fabricTypes?: string[];
  imageUrl: string;
}

export interface TrendAnalytics {
  trendId: string;
  popularity: number;
  engagement: number;
  userFeedback: {
    positive: number;
    negative: number;
    neutral: number;
  };
  lastUpdated: Date;
}

// Collection reference
const TRENDS_COLLECTION = "trends";

// Get all trends
export async function getAllTrends(): Promise<FashionTrend[]> {
  console.log("Getting all trends...");
  const trendsRef = collection(db, TRENDS_COLLECTION);
  console.log("Collection reference created");
  try {
    const snapshot = await getDocs(trendsRef);
    console.log("Got snapshot, docs count:", snapshot.docs.length);
    const trends = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
      createdAt: doc.data().createdAt?.toDate(),
      updatedAt: doc.data().updatedAt?.toDate(),
    })) as FashionTrend[];
    console.log("Mapped trends:", trends);
    return trends;
  } catch (error) {
    console.error("Error in getAllTrends:", error);
    throw error;
  }
}

// Get trend by ID
export async function getTrendById(id: string): Promise<FashionTrend | null> {
  const trendRef = doc(db, TRENDS_COLLECTION, id);
  const trendDoc = await getDoc(trendRef);
  if (!trendDoc.exists()) return null;
  return {
    id: trendDoc.id,
    ...trendDoc.data(),
    createdAt: trendDoc.data().createdAt?.toDate(),
    updatedAt: trendDoc.data().updatedAt?.toDate(),
  } as FashionTrend;
}

// Add new trend
export async function addTrend(
  trend: Omit<FashionTrend, "id">
): Promise<string> {
  const trendsRef = collection(db, TRENDS_COLLECTION);
  const docRef = await addDoc(trendsRef, {
    ...trend,
    createdAt: Timestamp.now(),
    updatedAt: Timestamp.now(),
  });
  return docRef.id;
}

// Update trend
export async function updateTrend(
  id: string,
  trend: Partial<FashionTrend>
): Promise<void> {
  const trendRef = doc(db, TRENDS_COLLECTION, id);
  await updateDoc(trendRef, {
    ...trend,
    updatedAt: Timestamp.now(),
  });
}

// Delete trend
export async function deleteTrend(id: string): Promise<void> {
  const trendRef = doc(db, TRENDS_COLLECTION, id);
  await deleteDoc(trendRef);
}

// Get trends by filter
export async function getTrendsByFilter(
  filter: TrendFilter
): Promise<FashionTrend[]> {
  const trendsRef = collection(db, TRENDS_COLLECTION);
  let q = query(trendsRef);

  if (filter.category) {
    q = query(q, where("category", "==", filter.category));
  }
  if (filter.subCategory) {
    q = query(q, where("subCategories", "array-contains", filter.subCategory));
  }
  if (filter.season) {
    q = query(q, where("season", "==", filter.season));
  }
  if (filter.gender) {
    q = query(q, where("gender", "==", filter.gender));
  }
  if (filter.priceRange) {
    q = query(q, where("priceRange", "==", filter.priceRange));
  }
  if (filter.sustainable !== undefined) {
    q = query(q, where("sustainability", "==", filter.sustainable));
  }
  if (filter.minPopularity) {
    q = query(q, where("popularity", ">=", filter.minPopularity));
  }

  const snapshot = await getDocs(q);
  return snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
    createdAt: doc.data().createdAt?.toDate(),
    updatedAt: doc.data().updatedAt?.toDate(),
  })) as FashionTrend[];
}

// Get trending items
export async function getTrendingItems(limitCount: number): Promise<FashionTrend[]> {
  const trendsRef = collection(db, TRENDS_COLLECTION);
  const q = query(
    trendsRef,
    orderBy("popularity", "desc"),
    limit(limitCount)
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((doc) => ({
    id: doc.id,
    ...doc.data(),
    createdAt: doc.data().createdAt?.toDate(),
    updatedAt: doc.data().updatedAt?.toDate(),
  })) as FashionTrend[];
}

// Get trends by season
export async function getTrendsBySeason(season: TrendSeason): Promise<FashionTrend[]> {
  return getTrendsByFilter({ season });
}

// Add test trend if collection is empty
export async function addTestTrendIfEmpty(): Promise<void> {
  console.log("Checking if trends collection is empty...");
  const trendsRef = collection(db, TRENDS_COLLECTION);
  
  try {
    const snapshot = await getDocs(trendsRef);
    console.log("Got snapshot, empty:", snapshot.empty);
    
    if (snapshot.empty) {
      console.log("Trends collection is empty, adding test trend...");
      const testTrend: Omit<FashionTrend, "id"> = {
        name: "Test Trend",
        category: "Quiet Luxury",
        subCategories: ["Knitwear", "Cardigans"],
        season: "Winter",
        popularity: 100,
        description: "A test trend for development",
        keyItems: ["Knit sweater", "Cardigan"],
        createdAt: new Date(),
        updatedAt: new Date(),
        gender: "Unisex",
        priceRange: "Mid-Range",
        sustainability: true,
        imageUrl: "https://via.placeholder.com/400x600/CCCCCC/666666?text=Test+Trend"
      };
      
      try {
        const docRef = await addDoc(trendsRef, {
          ...testTrend,
          createdAt: Timestamp.now(),
          updatedAt: Timestamp.now(),
        });
        console.log("Test trend added successfully with ID:", docRef.id);
      } catch (error) {
        console.error("Error adding test trend:", error);
        throw error;
      }
    } else {
      console.log("Trends collection is not empty, skipping test trend creation");
    }
  } catch (error) {
    console.error("Error checking trends collection:", error);
    throw error;
  }
} 