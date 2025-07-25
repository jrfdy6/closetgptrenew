// DiceBear API base URL
const DICEBEAR_API = "https://api.dicebear.com/7.x";

// Map our skin tones to DiceBear skin colors
const SKIN_TONE_MAP = {
  light: "f5d0a9",
  "medium-light": "e6c7a9",
  medium: "d4b483",
  "medium-dark": "b38b6d",
  dark: "8b5a2b",
  deep: "5c4033",
};

// Map our body types to DiceBear styles
const BODY_TYPE_STYLES = {
  // Female styles
  female: {
    hourglass: "avataaars",
    pear: "avataaars",
    apple: "avataaars",
    rectangle: "avataaars",
    "inverted-triangle": "avataaars",
    petite: "avataaars",
    tall: "avataaars",
    "plus-curvy": "avataaars",
    "lean-column": "avataaars",
  },
  // Male styles
  male: {
    rectangle: "avataaars",
    triangle: "avataaars",
    "inverted-triangle": "avataaars",
    oval: "avataaars",
    trapezoid: "avataaars",
    slim: "avataaars",
    stocky: "avataaars",
    tall: "avataaars",
    short: "avataaars",
  },
};

// Hair style options for each gender
const HAIR_STYLES = {
  female: [
    { id: "female-long-straight", label: "Long Straight", value: "longHairStraight" },
    { id: "female-long-wavy", label: "Long Wavy", value: "longHairCurly" },
    { id: "female-medium-straight", label: "Medium Straight", value: "shortHairShortFlat" },
    { id: "female-medium-wavy", label: "Medium Wavy", value: "shortHairShortWaved" },
    { id: "female-short-straight", label: "Short Straight", value: "shortHairShortRound" },
    { id: "female-short-wavy", label: "Short Wavy", value: "shortHairShortCurly" },
    { id: "female-bob", label: "Bob", value: "shortHairBob" },
    { id: "female-pixie", label: "Pixie", value: "shortHairPixie" },
  ],
  male: [
    { id: "male-short-classic", label: "Short Classic", value: "shortHairShortFlat" },
    { id: "male-short-messy", label: "Short Messy", value: "shortHairShortWaved" },
    { id: "male-medium-straight", label: "Medium Straight", value: "shortHairShortRound" },
    { id: "male-medium-wavy", label: "Medium Wavy", value: "shortHairShortCurly" },
    { id: "male-long-straight", label: "Long Straight", value: "longHairStraight" },
    { id: "male-long-wavy", label: "Long Wavy", value: "longHairCurly" },
    { id: "male-buzz", label: "Buzz Cut", value: "shortHairBuzzCut" },
    { id: "male-fade", label: "Fade", value: "shortHairFade" },
  ],
};

// Hair color options
const HAIR_COLORS = [
  { id: "black", label: "Black", value: "000000" },
  { id: "brown-dark", label: "Dark Brown", value: "3c2a21" },
  { id: "brown-medium", label: "Medium Brown", value: "6b4423" },
  { id: "brown-light", label: "Light Brown", value: "a67c52" },
  { id: "blonde-dark", label: "Dark Blonde", value: "b88b4a" },
  { id: "blonde-light", label: "Light Blonde", value: "e6c99f" },
  { id: "red", label: "Red", value: "a55728" },
  { id: "gray", label: "Gray", value: "808080" },
];

interface AvatarOptions {
  gender: "female" | "male";
  bodyType: string;
  skinTone: keyof typeof SKIN_TONE_MAP;
  hairStyle?: string;
  hairColor?: string;
  seed?: string;
}

export function generateAvatarUrl({ 
  gender, 
  bodyType, 
  skinTone, 
  hairStyle = "shortHairShortFlat",
  hairColor = "3c2a21",
  seed 
}: AvatarOptions): string {
  const style = BODY_TYPE_STYLES[gender][bodyType as keyof typeof BODY_TYPE_STYLES[typeof gender]];
  const skinColor = SKIN_TONE_MAP[skinTone];
  
  const avatarSeed = seed || `${gender}-${bodyType}-${skinTone}-${hairStyle}-${hairColor}`;
  
  const url = new URL(`${DICEBEAR_API}/${style}/svg`);
  url.searchParams.append("seed", avatarSeed);
  url.searchParams.append("backgroundColor", "transparent");
  
  // Avataaars-specific parameters
  url.searchParams.append("top", hairStyle);
  url.searchParams.append("topChance", "100");
  url.searchParams.append("topColor", hairColor);
  url.searchParams.append("skinColor", skinColor);
  url.searchParams.append("clothing", gender === "female" ? "blazerShirt" : "shirtCrewNeck");
  url.searchParams.append("clothingColor", gender === "female" ? "65a9e6" : "3b82f6");
  url.searchParams.append("mouth", "default");
  url.searchParams.append("eyes", "default");
  url.searchParams.append("eyebrows", "default");
  url.searchParams.append("accessories", "none");
  url.searchParams.append("accessoriesColor", "000000");
  url.searchParams.append("facialHair", "none");
  url.searchParams.append("facialHairColor", "000000");

  return url.toString();
}

// Export the hair style and color options
export { HAIR_STYLES, HAIR_COLORS };

// Helper function to get all possible avatar combinations
export function getAllAvatarCombinations() {
  const combinations: AvatarOptions[] = [];
  
  // Female combinations
  Object.keys(BODY_TYPE_STYLES.female).forEach((bodyType) => {
    Object.keys(SKIN_TONE_MAP).forEach((skinTone) => {
      combinations.push({
        gender: "female",
        bodyType,
        skinTone: skinTone as keyof typeof SKIN_TONE_MAP,
      });
    });
  });
  
  // Male combinations
  Object.keys(BODY_TYPE_STYLES.male).forEach((bodyType) => {
    Object.keys(SKIN_TONE_MAP).forEach((skinTone) => {
      combinations.push({
        gender: "male",
        bodyType,
        skinTone: skinTone as keyof typeof SKIN_TONE_MAP,
      });
    });
  });
  
  return combinations;
} 