export interface VisualHarmonyRule {
  style: string;
  color_harmony: string[];
  silhouette_balance: string[];
  required_elements: string[];
  forbidden_elements: string[];
  pattern_rules: {
    allowed: string[];
    forbidden: string[];
  };
  material_rules: {
    preferred: string[];
    avoid: string[];
  };
}

export const VISUAL_HARMONY_RULES: Record<string, VisualHarmonyRule> = {
  dark_academia: {
    style: "dark_academia",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Structured", "Layered"],
    required_elements: ["blazer", "turtleneck", "pleated skirt", "oxford shoes", "tweed"],
    forbidden_elements: ["bright colors", "casual items"],
    pattern_rules: {
      allowed: ["tweed", "herringbone", "plaid", "subtle stripes"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["wool", "tweed", "cotton", "leather"],
      avoid: ["synthetic fabrics", "athletic materials"]
    }
  },
  old_money: {
    style: "old_money",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Structured", "Classic"],
    required_elements: ["polo shirt", "pleated trousers", "blazer", "loafers", "cashmere"],
    forbidden_elements: ["logos", "trendy pieces"],
    pattern_rules: {
      allowed: ["subtle stripes", "tweed", "herringbone"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["cashmere", "wool", "cotton", "linen"],
      avoid: ["synthetic fabrics", "athletic materials"]
    }
  },
  streetwear: {
    style: "streetwear",
    color_harmony: ["Complementary", "Triadic"],
    silhouette_balance: ["Oversized", "Layered"],
    required_elements: ["hoodie", "sneakers", "cargo pants", "graphic tee"],
    forbidden_elements: ["formal wear", "preppy items"],
    pattern_rules: {
      allowed: ["graphic prints", "logos", "bold patterns"],
      forbidden: ["traditional patterns", "formal patterns"]
    },
    material_rules: {
      preferred: ["cotton", "denim", "nylon", "technical fabrics"],
      avoid: ["formal fabrics", "delicate materials"]
    }
  },
  y2k: {
    style: "y2k",
    color_harmony: ["Complementary", "Triadic"],
    silhouette_balance: ["Asymmetrical", "Tight Loose"],
    required_elements: ["baby tees", "low-rise jeans", "track jackets", "butterfly clips", "micro mini skirts"],
    forbidden_elements: ["modest cuts", "classic tailoring"],
    pattern_rules: {
      allowed: ["floral prints", "animal prints", "graphic prints", "metallic patterns"],
      forbidden: ["subtle patterns", "classic patterns"]
    },
    material_rules: {
      preferred: ["denim", "pleather", "mesh", "jersey"],
      avoid: ["tweed", "formal fabrics"]
    }
  },
  minimalist: {
    style: "minimalist",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Symmetrical", "Structured Fluid"],
    required_elements: ["white shirt", "structured blazer", "slip dress", "tailored pants"],
    forbidden_elements: ["bold prints", "logos", "excess accessories"],
    pattern_rules: {
      allowed: ["solid colors", "subtle textures"],
      forbidden: ["bold patterns", "graphic prints"]
    },
    material_rules: {
      preferred: ["linen", "cotton", "wool blends"],
      avoid: ["synthetic fabrics", "loud textures"]
    }
  },
  boho: {
    style: "boho",
    color_harmony: ["Analogous", "Split Complementary"],
    silhouette_balance: ["Fluid", "Layered"],
    required_elements: ["flowy maxi dress", "fringed vest", "wide-brim hat", "stacked jewelry"],
    forbidden_elements: ["structured pieces", "minimalist items"],
    pattern_rules: {
      allowed: ["ethnic prints", "tribal patterns", "floral motifs"],
      forbidden: ["geometric patterns", "stripes"]
    },
    material_rules: {
      preferred: ["cotton", "linen", "suede", "fringe"],
      avoid: ["synthetic fabrics", "stiff materials"]
    }
  },
  preppy: {
    style: "preppy",
    color_harmony: ["Complementary", "Analogous"],
    silhouette_balance: ["Structured", "Classic"],
    required_elements: ["polo shirt", "chinos", "blazer", "loafers", "cable knit"],
    forbidden_elements: ["grunge items", "streetwear"],
    pattern_rules: {
      allowed: ["stripes", "tartan", "argyle", "nautical patterns"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["cotton", "wool", "cashmere", "tweed"],
      avoid: ["synthetic fabrics", "athletic materials"]
    }
  },
  grunge: {
    style: "grunge",
    color_harmony: ["Monochromatic", "Complementary"],
    silhouette_balance: ["Oversized", "Layered"],
    required_elements: ["flannel shirt", "ripped jeans", "combat boots", "band t-shirt"],
    forbidden_elements: ["preppy items", "formal wear"],
    pattern_rules: {
      allowed: ["plaid", "distressed", "graphic prints"],
      forbidden: ["floral", "polka dots"]
    },
    material_rules: {
      preferred: ["denim", "flannel", "leather"],
      avoid: ["silk", "satin"]
    }
  },
  classic: {
    style: "classic",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Structured", "Balanced"],
    required_elements: ["blazer", "white shirt", "tailored pants", "pencil skirt"],
    forbidden_elements: ["trendy pieces", "casual items"],
    pattern_rules: {
      allowed: ["stripes", "subtle checks", "solid colors"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["wool", "cotton", "silk"],
      avoid: ["synthetic fabrics", "distressed materials"]
    }
  },
  techwear: {
    style: "techwear",
    color_harmony: ["Monochromatic", "Complementary"],
    silhouette_balance: ["Structured", "Technical"],
    required_elements: ["cargo pants", "technical jacket", "utility vest", "hiking boots"],
    forbidden_elements: ["casual items", "formal wear"],
    pattern_rules: {
      allowed: ["technical patterns", "camo", "solid colors"],
      forbidden: ["floral", "stripes"]
    },
    material_rules: {
      preferred: ["nylon", "gore-tex", "technical fabrics"],
      avoid: ["cotton", "wool"]
    }
  },
  androgynous: {
    style: "androgynous",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Structured", "Fluid"],
    required_elements: ["tailored suit", "structured jacket", "loose pants", "oxford shirt"],
    forbidden_elements: ["overtly feminine pieces", "overtly masculine pieces"],
    pattern_rules: {
      allowed: ["stripes", "checks", "solid colors"],
      forbidden: ["floral", "frills"]
    },
    material_rules: {
      preferred: ["wool", "cotton", "linen"],
      avoid: ["lace", "satin"]
    }
  },
  coastal_grandma: {
    style: "coastal_grandma",
    color_harmony: ["Analogous", "Complementary"],
    silhouette_balance: ["Relaxed", "Layered"],
    required_elements: ["linen dress", "straw hat", "beaded necklace", "sandals"],
    forbidden_elements: ["trendy pieces", "heavy materials"],
    pattern_rules: {
      allowed: ["floral prints", "stripes", "nautical patterns"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["linen", "cotton", "straw"],
      avoid: ["synthetic fabrics", "heavy materials"]
    }
  },
  balanced: {
    style: "balanced",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Symmetrical", "Structured Fluid"],
    required_elements: ["structured blazers", "tailored pants", "button-down shirts", "midi skirts", "quality basics"],
    forbidden_elements: ["oversized items", "distressed items", "trendy pieces"],
    pattern_rules: {
      allowed: ["subtle stripes", "checks", "minimal patterns"],
      forbidden: ["bold prints", "graphic prints"]
    },
    material_rules: {
      preferred: ["cotton", "wool", "linen", "silk"],
      avoid: ["synthetic", "athletic fabrics"]
    }
  },
  coastal_chic: {
    style: "coastal_chic",
    color_harmony: ["Analogous", "Complementary"],
    silhouette_balance: ["Relaxed", "Layered"],
    required_elements: ["linen dress", "straw hat", "beaded necklace", "sandals"],
    forbidden_elements: ["trendy pieces", "heavy materials"],
    pattern_rules: {
      allowed: ["floral prints", "stripes", "nautical patterns"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["linen", "cotton", "straw"],
      avoid: ["synthetic fabrics", "heavy materials"]
    }
  },
  business_casual: {
    style: "business_casual",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Structured", "Balanced"],
    required_elements: ["blazer", "button-down shirt", "chinos", "loafers"],
    forbidden_elements: ["jeans", "sneakers", "casual t-shirts"],
    pattern_rules: {
      allowed: ["subtle stripes", "checks", "solid colors"],
      forbidden: ["bold prints", "graphic patterns"]
    },
    material_rules: {
      preferred: ["cotton", "wool", "linen"],
      avoid: ["denim", "athletic materials"]
    }
  },
  avant_garde: {
    style: "avant_garde",
    color_harmony: ["Complementary", "Triadic"],
    silhouette_balance: ["Asymmetrical", "Experimental"],
    required_elements: ["structured pieces", "unconventional shapes", "artistic elements"],
    forbidden_elements: ["traditional pieces", "basic items"],
    pattern_rules: {
      allowed: ["abstract prints", "geometric patterns", "experimental designs"],
      forbidden: ["traditional patterns", "basic prints"]
    },
    material_rules: {
      preferred: ["unconventional materials", "mixed media", "textured fabrics"],
      avoid: ["basic materials", "traditional fabrics"]
    }
  },
  cottagecore: {
    style: "cottagecore",
    color_harmony: ["Analogous", "Complementary"],
    silhouette_balance: ["Romantic", "Layered"],
    required_elements: ["floral dress", "puff sleeves", "lace details", "straw hat"],
    forbidden_elements: ["modern pieces", "minimalist items"],
    pattern_rules: {
      allowed: ["floral prints", "garden motifs", "vintage patterns"],
      forbidden: ["modern prints", "geometric patterns"]
    },
    material_rules: {
      preferred: ["cotton", "linen", "lace", "floral fabrics"],
      avoid: ["synthetic fabrics", "modern materials"]
    }
  },
  edgy: {
    style: "edgy",
    color_harmony: ["Monochromatic", "Complementary"],
    silhouette_balance: ["Asymmetrical", "Structured"],
    required_elements: ["leather jacket", "ripped jeans", "combat boots", "graphic tee"],
    forbidden_elements: ["preppy items", "sweet pieces"],
    pattern_rules: {
      allowed: ["graphic prints", "distressed", "bold patterns"],
      forbidden: ["floral", "pastel patterns"]
    },
    material_rules: {
      preferred: ["leather", "denim", "metal details"],
      avoid: ["delicate fabrics", "sweet materials"]
    }
  },
  athleisure: {
    style: "athleisure",
    color_harmony: ["Monochromatic", "Complementary"],
    silhouette_balance: ["Structured", "Comfortable"],
    required_elements: ["leggings", "sports bra", "sneakers", "athletic jacket"],
    forbidden_elements: ["formal wear", "heavy materials"],
    pattern_rules: {
      allowed: ["athletic patterns", "sporty prints", "solid colors"],
      forbidden: ["formal patterns", "delicate prints"]
    },
    material_rules: {
      preferred: ["spandex", "nylon", "performance fabrics"],
      avoid: ["formal fabrics", "heavy materials"]
    }
  },
  casual_cool: {
    style: "casual_cool",
    color_harmony: ["Monochromatic", "Analogous"],
    silhouette_balance: ["Relaxed", "Balanced"],
    required_elements: ["denim jacket", "white tee", "sneakers", "relaxed pants"],
    forbidden_elements: ["formal wear", "overly casual items"],
    pattern_rules: {
      allowed: ["subtle patterns", "solid colors", "minimal prints"],
      forbidden: ["bold prints", "formal patterns"]
    },
    material_rules: {
      preferred: ["cotton", "denim", "linen"],
      avoid: ["formal fabrics", "athletic materials"]
    }
  },
  romantic: {
    style: "romantic",
    color_harmony: ["Analogous", "Complementary"],
    silhouette_balance: ["Soft", "Flowing"],
    required_elements: ["floral dress", "lace details", "soft fabrics", "delicate jewelry"],
    forbidden_elements: ["harsh pieces", "minimalist items"],
    pattern_rules: {
      allowed: ["floral prints", "delicate patterns", "soft motifs"],
      forbidden: ["bold prints", "geometric patterns"]
    },
    material_rules: {
      preferred: ["lace", "silk", "cotton", "delicate fabrics"],
      avoid: ["harsh materials", "heavy fabrics"]
    }
  },
  artsy: {
    style: "artsy",
    color_harmony: ["Complementary", "Triadic"],
    silhouette_balance: ["Creative", "Unconventional"],
    required_elements: ["unique pieces", "artistic elements", "creative accessories"],
    forbidden_elements: ["basic items", "traditional pieces"],
    pattern_rules: {
      allowed: ["artistic prints", "creative patterns", "unique designs"],
      forbidden: ["basic patterns", "traditional prints"]
    },
    material_rules: {
      preferred: ["mixed media", "textured fabrics", "artistic materials"],
      avoid: ["basic materials", "traditional fabrics"]
    }
  }
}; 