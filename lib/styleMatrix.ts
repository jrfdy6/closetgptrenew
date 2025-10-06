// lib/styleMatrix.ts
// Canonical Style Compatibility Matrix
// All keys and values are normalized to lowercase for consistent matching

export const STYLE_COMPATIBILITY: Record<string, string[]> = {
  // Core Professional Styles
  classic: ["classic", "casual", "smart casual", "business casual", "traditional", "preppy", "minimalist", "balanced"],
  business: ["business", "business casual", "professional", "smart casual", "classic", "formal"],
  business_casual: ["business_casual", "business casual", "business", "smart casual", "classic", "casual", "preppy"],
  formal: ["formal", "elegant", "semi-formal", "business", "classic"],
  
  // Casual & Everyday Styles
  casual: ["casual", "classic", "streetwear", "athleisure", "relaxed", "everyday", "casual_cool", "business_casual"],
  casual_cool: ["casual_cool", "casual", "streetwear", "minimalist", "modern"],
  relaxed: ["relaxed", "casual", "everyday", "coastal_grandma", "coastal_chic"],
  everyday: ["everyday", "casual", "relaxed", "balanced", "minimalist"],
  
  // Athletic & Active Styles
  athletic: ["athletic", "sporty", "active", "workout", "athleisure", "techwear"],
  athleisure: ["athleisure", "athletic", "sporty", "casual", "techwear"],
  sporty: ["sporty", "athletic", "athleisure", "active", "workout"],
  
  // Street & Urban Styles
  streetwear: ["streetwear", "urban", "edgy", "trendy", "casual", "grunge"],
  urban: ["urban", "streetwear", "edgy", "modern", "techwear"],
  edgy: ["edgy", "streetwear", "grunge", "urban", "avant_garde"],
  grunge: ["grunge", "edgy", "streetwear", "casual"],
  
  // Vintage & Retro Styles
  vintage: ["vintage", "retro", "classic", "timeless", "old_money", "dark_academia"],
  retro: ["retro", "vintage", "y2k", "classic"],
  timeless: ["timeless", "classic", "vintage", "old_money", "minimalist"],
  
  // Modern & Contemporary Styles
  modern: ["modern", "contemporary", "trendy", "fashion-forward", "minimalist", "casual_cool"],
  contemporary: ["contemporary", "modern", "minimalist", "balanced"],
  trendy: ["trendy", "modern", "streetwear", "y2k"],
  fashion_forward: ["fashion_forward", "modern", "avant_garde", "artsy"],
  
  // Minimalist & Clean Styles
  minimalist: ["minimalist", "simple", "clean", "basic", "classic", "modern", "balanced"],
  simple: ["simple", "minimalist", "clean", "basic"],
  clean: ["clean", "minimalist", "simple", "modern"],
  basic: ["basic", "minimalist", "simple", "casual"],
  
  // Bohemian & Artistic Styles
  bohemian: ["bohemian", "boho", "eclectic", "artistic", "romantic", "cottagecore"],
  boho: ["boho", "bohemian", "eclectic", "romantic", "coastal_grandma"],
  eclectic: ["eclectic", "bohemian", "boho", "artsy", "romantic"],
  artistic: ["artistic", "eclectic", "artsy", "avant_garde", "bohemian"],
  artsy: ["artsy", "artistic", "avant_garde", "eclectic", "creative"],
  
  // Preppy & Traditional Styles
  preppy: ["preppy", "classic", "traditional", "polished", "old_money", "business_casual"],
  traditional: ["traditional", "classic", "preppy", "old_money", "vintage"],
  polished: ["polished", "preppy", "classic", "formal", "business"],
  
  // Specialized Styles
  old_money: ["old_money", "preppy", "classic", "traditional", "polished", "vintage"],
  dark_academia: ["dark_academia", "vintage", "classic", "academic", "traditional"],
  y2k: ["y2k", "retro", "trendy", "edgy", "streetwear"],
  techwear: ["techwear", "athletic", "athleisure", "urban", "modern"],
  androgynous: ["androgynous", "minimalist", "modern", "classic", "balanced"],
  
  // Coastal & Relaxed Styles
  coastal_grandma: ["coastal_grandma", "coastal_chic", "relaxed", "boho", "romantic"],
  coastal_chic: ["coastal_chic", "coastal_grandma", "relaxed", "romantic", "casual"],
  
  // Balanced & Versatile Styles
  balanced: ["balanced", "classic", "minimalist", "modern", "casual", "business_casual"],
  
  // Avant-garde & Experimental Styles
  avant_garde: ["avant_garde", "artsy", "edgy", "experimental", "fashion_forward"],
  experimental: ["experimental", "avant_garde", "artsy", "creative"],
  creative: ["creative", "artsy", "avant_garde", "eclectic"],
  
  // Romantic & Feminine Styles
  romantic: ["romantic", "bohemian", "boho", "cottagecore", "coastal_grandma", "coastal_chic"],
  cottagecore: ["cottagecore", "romantic", "bohemian", "vintage", "coastal_grandma"],
  
  // Elegant & Sophisticated Styles
  elegant: ["elegant", "formal", "classic", "romantic", "sophisticated"],
  sophisticated: ["sophisticated", "elegant", "classic", "formal", "old_money"],
  
  // Professional & Work Styles
  professional: ["professional", "business", "business_casual", "classic", "formal"],
  smart_casual: ["smart_casual", "business_casual", "business", "classic", "casual"],
  
  // Workout & Active Styles
  workout: ["workout", "athletic", "sporty", "athleisure", "active"],
  active: ["active", "athletic", "sporty", "workout", "athleisure"],
  
  // Academic & Intellectual Styles
  academic: ["academic", "dark_academia", "classic", "traditional", "intellectual"],
  intellectual: ["intellectual", "academic", "classic", "dark_academia", "minimalist"],
  
  // Nautical & Maritime Styles
  nautical: ["nautical", "preppy", "coastal_chic", "classic", "casual"],
  maritime: ["maritime", "nautical", "coastal_chic", "preppy"],
  
  // Alternative & Subculture Styles
  alternative: ["alternative", "grunge", "edgy", "streetwear", "punk"],
  punk: ["punk", "edgy", "grunge", "alternative", "streetwear"],
  
  // Seasonal & Themed Styles
  summer: ["summer", "casual", "coastal_chic", "romantic", "bohemian"],
  winter: ["winter", "classic", "dark_academia", "minimalist", "cozy"],
  cozy: ["cozy", "winter", "casual", "relaxed", "cottagecore"],
  
  // Gender-neutral & Inclusive Styles
  unisex: ["unisex", "minimalist", "classic", "modern", "androgynous"],
  gender_neutral: ["gender_neutral", "unisex", "minimalist", "androgynous", "modern"],
};
