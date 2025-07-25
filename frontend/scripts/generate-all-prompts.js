console.log('Script created');

const fs = require('fs');
const path = require('path');

// All outfits from the outfit bank
const outfits = [
  // 🌿 Cottagecore / Boho - Women (10 outfits)
  {
    id: "F-CB1",
    items: ["Floral maxi dress", "Cropped knit cardigan", "Leather boots"],
    palette: "soft florals",
    colors: ["Soft pink (#FFB3BA)", "Lavender (#E6B3FF)", "Light green (#B3FFB3)", "Cream (#FFF2CC)"],
    style: "Cottagecore/Boho aesthetic with romantic, flowy elements",
    layout: "2x2"
  },
  {
    id: "F-CB2",
    items: ["Peasant blouse", "Patchwork skirt", "Vest", "Floppy hat"],
    palette: "warm neutrals",
    colors: ["Warm brown (#8B4513)", "Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#CD853F)"],
    style: "Boho aesthetic with layered, natural elements",
    layout: "2x2"
  },
  {
    id: "F-CB3",
    items: ["Ruffle blouse", "Wide-leg linen pants", "Fringe shawl"],
    palette: "dusty pastels",
    colors: ["Dusty pink (#DDA0DD)", "Light green (#B3FFB3)", "Light blue (#87CEEB)", "Cream (#FFF2CC)"],
    style: "Cottagecore aesthetic with romantic, loose elements",
    layout: "2x2"
  },
  {
    id: "F-CB4",
    items: ["Muslin wrap dress", "Open-toe sandals"],
    palette: "natural earth",
    colors: ["Brown (#8B4513)", "Green (#228B22)", "Cream (#F5DEB3)", "Tan (#D2B48C)"],
    style: "Cottagecore aesthetic with natural, easy elements",
    layout: "2x2"
  },
  {
    id: "F-CB5",
    items: ["Button-front midi dress", "Wool capelet", "Ankle boots"],
    palette: "dried floral mix",
    colors: ["Dried red (#CD5C5C)", "Light green (#B3FFB3)", "Soft pink (#FFB3BA)", "Cream (#FFF2CC)"],
    style: "Cottagecore aesthetic with romantic, layered elements",
    layout: "2x2"
  },
  {
    id: "F-CB6",
    items: ["Crochet top", "Maxi skirt", "Leather belt"],
    palette: "warm earth tones",
    colors: ["Brown (#8B4513)", "Green (#6B8E23)", "Red (#CD5C5C)", "Cream (#F5DEB3)"],
    style: "Boho aesthetic with natural, flowy elements",
    layout: "2x2"
  },
  {
    id: "F-CB7",
    items: ["Linen sundress", "Straw hat", "Espadrilles"],
    palette: "soft pastels",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "White (#FFFFFF)"],
    style: "Cottagecore aesthetic with romantic, easy elements",
    layout: "2x2"
  },
  {
    id: "F-CB8",
    items: ["Embroidered blouse", "Tiered skirt", "Vest", "Jewelry"],
    palette: "mixed earth tones",
    colors: ["Brown (#8B4513)", "Green (#6B8E23)", "Red (#CD5C5C)", "Cream (#F5DEB3)"],
    style: "Boho aesthetic with artsy, layered elements",
    layout: "2x3"
  },
  {
    id: "F-CB9",
    items: ["Floral tea dress", "Cardigan", "Ankle boots"],
    palette: "muted florals",
    colors: ["Soft pink (#FFB3BA)", "Light green (#B3FFB3)", "Cream (#FFF2CC)", "Lavender (#DDA0DD)"],
    style: "Cottagecore aesthetic with natural, flowy elements",
    layout: "2x2"
  },
  {
    id: "F-CB10",
    items: ["Linen jumpsuit", "Woven bag", "Sandals"],
    palette: "warm neutrals",
    colors: ["Cream (#F5DEB3)", "Brown (#8B4513)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Boho aesthetic with natural, relaxed elements",
    layout: "2x2"
  },

  // 🌿 Cottagecore / Boho - Men (10 outfits)
  {
    id: "M-CB1",
    items: ["Linen shirt", "Cargo trousers", "Fisherman cardigan"],
    palette: "cream & olive",
    colors: ["Cream (#FFF2CC)", "Olive green (#6B8E23)"],
    style: "Cottagecore aesthetic with natural, relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-CB2",
    items: ["Henley", "Cotton pants", "Leather sandals"],
    palette: "warm taupe",
    colors: ["Warm taupe (#D2B48C)"],
    style: "Boho aesthetic with natural, flowy elements",
    layout: "2x2"
  },
  {
    id: "M-CB3",
    items: ["Chambray shirt", "Suspenders", "Wool vest", "Canvas boots"],
    palette: "vintage neutrals",
    colors: ["Brown (#8B4513)", "Cream (#F5DEB3)", "Tan (#D2B48C)"],
    style: "Cottagecore aesthetic with vintage, rustic elements",
    layout: "2x3"
  },
  {
    id: "M-CB4",
    items: ["Pullover tunic", "Drawstring trousers", "Woven belt"],
    palette: "soft moss green",
    colors: ["Soft moss green (#B3FFB3)"],
    style: "Cottagecore aesthetic with natural, loose elements",
    layout: "2x2"
  },
  {
    id: "M-CB5",
    items: ["Knit tank", "Patchwork overshirt", "Rolled linen pants"],
    palette: "terracotta mix",
    colors: ["Terracotta (#CD5C5C)", "Brown (#8B4513)"],
    style: "Boho aesthetic with natural, breezy elements",
    layout: "2x2"
  },
  {
    id: "M-CB6",
    items: ["Linen shirt", "Khaki pants", "Leather belt"],
    palette: "earth tones",
    colors: ["Brown (#8B4513)", "Green (#228B22)", "Cream (#F5DEB3)"],
    style: "Cottagecore aesthetic with natural, relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-CB7",
    items: ["Oversized shirt", "Loose pants", "Sandals"],
    palette: "warm neutrals",
    colors: ["Cream (#F5DEB3)", "Brown (#8B4513)", "Beige (#FFF2CC)"],
    style: "Boho aesthetic with natural, flowy elements",
    layout: "2x2"
  },
  {
    id: "M-CB8",
    items: ["Corduroy shirt", "Wool vest", "Canvas pants"],
    palette: "muted earth",
    colors: ["Brown (#8B4513)", "Cream (#F5DEB3)", "Tan (#D2B48C)"],
    style: "Cottagecore aesthetic with rustic elements",
    layout: "2x2"
  },
  {
    id: "M-CB9",
    items: ["Cotton tee", "Linen pants", "Woven hat"],
    palette: "soft greens",
    colors: ["Soft green (#B3FFB3)", "Green (#228B22)"],
    style: "Cottagecore aesthetic with natural, relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-CB10",
    items: ["Embroidered shirt", "Vest", "Cargo pants", "Jewelry"],
    palette: "mixed earth",
    colors: ["Brown (#8B4513)", "Green (#6B8E23)", "Red (#CD5C5C)"],
    style: "Boho aesthetic with artsy, layered elements",
    layout: "2x3"
  },

  // 💼 Old Money / Preppy / Classic - Women (10 outfits)
  {
    id: "F-OM1",
    items: ["Tweed blazer", "Pleated skirt", "Loafers"],
    palette: "navy + cream",
    colors: ["Navy blue (#000080)", "Cream (#FFF2CC)", "White (#FFFFFF)"],
    style: "Old Money aesthetic with tailored, sophisticated elements",
    layout: "2x2"
  },
  {
    id: "F-OM2",
    items: ["Cable knit sweater", "Collared blouse", "Pressed trousers"],
    palette: "rich neutrals",
    colors: ["Brown (#8B4513)", "Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Old Money aesthetic with structured, sophisticated elements",
    layout: "2x2"
  },
  {
    id: "F-OM3",
    items: ["Wool coat", "Dress shirt", "Midi skirt", "Heels"],
    palette: "soft jewel tones",
    colors: ["Burgundy (#8B0000)", "Navy (#000080)", "Green (#228B22)", "Cream (#FFF2CC)"],
    style: "Old Money aesthetic with sophisticated, elegant elements",
    layout: "2x3"
  },
  {
    id: "F-OM4",
    items: ["Silk blouse", "Beige high-waist trousers"],
    palette: "champagne & blush",
    colors: ["Champagne (#F7E7CE)", "Blush pink (#FFB3BA)", "Cream (#FFF2CC)"],
    style: "Old Money aesthetic with elegant elements",
    layout: "2x2"
  },
  {
    id: "F-OM5",
    items: ["Blazer", "Check trousers", "Button-down shirt"],
    palette: "green & brown",
    colors: ["Green (#228B22)", "Brown (#8B4513)", "Cream (#F5DEB3)"],
    style: "Old Money aesthetic with academic elements",
    layout: "2x2"
  },
  {
    id: "F-OM6",
    items: ["Polo dress", "Cardigan", "Boat shoes"],
    palette: "navy & white",
    colors: ["Navy blue (#000080)", "White (#FFFFFF)"],
    style: "Preppy aesthetic with tailored elements",
    layout: "2x2"
  },
  {
    id: "F-OM7",
    items: ["Trench coat", "Turtleneck", "Wide-leg pants"],
    palette: "monochrome",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Old Money aesthetic with structured elements",
    layout: "2x2"
  },
  {
    id: "F-OM8",
    items: ["Tweed blazer", "Pleated skirt", "Oxfords"],
    palette: "tweed tones",
    colors: ["Brown (#8B4513)", "Cream (#F5DEB3)", "Green (#6B8E23)"],
    style: "Old Money aesthetic with academic elements",
    layout: "2x2"
  },
  {
    id: "F-OM9",
    items: ["Polo shirt", "Khaki skirt", "Loafers"],
    palette: "pastel preppy",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "White (#FFFFFF)"],
    style: "Preppy aesthetic with tailored elements",
    layout: "2x2"
  },
  {
    id: "F-OM10",
    items: ["Silk dress", "Cashmere cardigan", "Pearls"],
    palette: "luxury neutrals",
    colors: ["Cream (#FFF2CC)", "Cream (#F5DEB3)", "Brown (#8B4513)", "Tan (#D2B48C)"],
    style: "Old Money aesthetic with elegant elements",
    layout: "2x2"
  },

  // 💼 Old Money / Preppy / Classic - Men (10 outfits)
  {
    id: "M-OM1",
    items: ["Double-breasted coat", "Oxford shirt", "Tapered trousers"],
    palette: "charcoal & cream",
    colors: ["Charcoal (#36454F)", "Cream (#FFF2CC)", "Black (#000000)"],
    style: "Old Money aesthetic with tailored, sophisticated elements",
    layout: "2x2"
  },
  {
    id: "M-OM2",
    items: ["Polo shirt", "Cardigan", "Chinos"],
    palette: "navy + tan",
    colors: ["Navy blue (#000080)", "Tan (#D2B48C)", "White (#FFFFFF)"],
    style: "Preppy aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "M-OM3",
    items: ["Knit vest", "Button-down shirt", "Wool slacks"],
    palette: "deep burgundy",
    colors: ["Burgundy (#8B0000)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Old Money aesthetic with structured elements",
    layout: "2x2"
  },
  {
    id: "M-OM4",
    items: ["Houndstooth coat", "Cashmere sweater", "Khakis"],
    palette: "olive + cream",
    colors: ["Olive green (#6B8E23)", "Cream (#FFF2CC)", "Brown (#8B4513)"],
    style: "Old Money aesthetic with academic elements",
    layout: "2x2"
  },
  {
    id: "M-OM5",
    items: ["Trench coat", "Turtleneck", "Tailored pants"],
    palette: "white + camel",
    colors: ["White (#FFFFFF)", "Camel (#C19A6B)", "Cream (#FFF2CC)"],
    style: "Old Money aesthetic with elegant elements",
    layout: "2x2"
  },
  {
    id: "M-OM6",
    items: ["Polo shirt", "White pants", "Boat shoes"],
    palette: "navy & white",
    colors: ["Navy blue (#000080)", "White (#FFFFFF)"],
    style: "Preppy aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "M-OM7",
    items: ["Suit jacket", "Turtleneck", "Dress pants"],
    palette: "greyscale",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Old Money aesthetic with tailored elements",
    layout: "2x2"
  },
  {
    id: "M-OM8",
    items: ["Tweed blazer", "Corduroy pants", "Oxfords"],
    palette: "tweed browns",
    colors: ["Brown (#8B4513)", "Cream (#F5DEB3)", "Green (#6B8E23)"],
    style: "Old Money aesthetic with academic elements",
    layout: "2x2"
  },
  {
    id: "M-OM9",
    items: ["Pastel polo", "Khaki pants", "Loafers"],
    palette: "pastel preppy",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "White (#FFFFFF)"],
    style: "Preppy aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "M-OM10",
    items: ["Cashmere sweater", "Silk tie", "Wool pants"],
    palette: "luxury neutrals",
    colors: ["Cream (#FFF2CC)", "Cream (#F5DEB3)", "Brown (#8B4513)", "Tan (#D2B48C)"],
    style: "Old Money aesthetic with elegant elements",
    layout: "2x2"
  },

  // 🖤 Streetwear / Edgy / Grunge - Women (10 outfits)
  {
    id: "F-ST1",
    items: ["Bomber jacket", "Graphic tee", "Wide-leg cargos", "Bucket hat"],
    palette: "black + red",
    colors: ["Black (#000000)", "Red (#FF0000)", "White (#FFFFFF)"],
    style: "Streetwear aesthetic with oversized, edgy elements",
    layout: "2x3"
  },
  {
    id: "F-ST2",
    items: ["Cropped hoodie", "Parachute pants", "Combat boots"],
    palette: "muted neutrals",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)", "Cream (#F5DEB3)"],
    style: "Streetwear aesthetic with relaxed, edgy elements",
    layout: "2x2"
  },
  {
    id: "F-ST3",
    items: ["Windbreaker", "Baggy denim", "Thermal top"],
    palette: "greyscale pop",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Streetwear aesthetic with boxy, edgy elements",
    layout: "2x2"
  },
  {
    id: "F-ST4",
    items: ["Mesh top", "Mini skirt", "Fur jacket"],
    palette: "y2k high contrast",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "Black (#000000)"],
    style: "Y2K aesthetic with fitted, loud elements",
    layout: "2x2"
  },
  {
    id: "F-ST5",
    items: ["Plaid overshirt", "Destroyed jeans", "Band tee"],
    palette: "grunge mix",
    colors: ["Black (#000000)", "Brown (#8B4513)", "Green (#6B8E23)", "Gray (#808080)"],
    style: "Grunge aesthetic with unstructured elements",
    layout: "2x2"
  },
  {
    id: "F-ST6",
    items: ["Leather jacket", "Crop top", "Ripped jeans"],
    palette: "dark contrast",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Red (#FF0000)"],
    style: "Streetwear aesthetic with fitted, edgy elements",
    layout: "2x2"
  },
  {
    id: "F-ST7",
    items: ["Utility vest", "Cargo pants", "Tech sneakers"],
    palette: "urban tech",
    colors: ["Black (#000000)", "Gray (#808080)", "Green (#6B8E23)", "White (#FFFFFF)"],
    style: "Techwear aesthetic with functional elements",
    layout: "2x2"
  },
  {
    id: "F-ST8",
    items: ["Crop top", "Low-rise jeans", "Platform shoes"],
    palette: "y2k pastels",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "White (#FFFFFF)"],
    style: "Y2K aesthetic with fitted elements",
    layout: "2x2"
  },
  {
    id: "F-ST9",
    items: ["Flannel shirt", "Mom jeans", "Combat boots"],
    palette: "grunge earth",
    colors: ["Brown (#8B4513)", "Green (#6B8E23)", "Black (#000000)", "Cream (#F5DEB3)"],
    style: "Grunge aesthetic with relaxed elements",
    layout: "2x2"
  },
  {
    id: "F-ST10",
    items: ["Oversized hoodie", "Bike shorts", "Chunky sneakers"],
    palette: "urban contrast",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Streetwear aesthetic with oversized elements",
    layout: "2x2"
  },

  // 🖤 Streetwear / Edgy / Grunge - Men (10 outfits)
  {
    id: "M-ST1",
    items: ["Flannel shirt", "Band tee", "Black jeans"],
    palette: "washed black",
    colors: ["Black (#000000)", "Gray (#808080)", "White (#FFFFFF)"],
    style: "Grunge aesthetic with boxy elements",
    layout: "2x2"
  },
  {
    id: "M-ST2",
    items: ["Hoodie", "Puffer jacket", "Cargo pants", "Nike Dunks"],
    palette: "urban muted",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)", "Cream (#F5DEB3)"],
    style: "Streetwear aesthetic with oversized elements",
    layout: "2x3"
  },
  {
    id: "M-ST3",
    items: ["Longline tee", "Joggers", "Beanie"],
    palette: "army green & grey",
    colors: ["Green (#6B8E23)", "Gray (#808080)", "Black (#000000)"],
    style: "Streetwear aesthetic with baggy elements",
    layout: "2x2"
  },
  {
    id: "M-ST4",
    items: ["Denim jacket", "Flannel shirt", "Hoodie", "Tee", "Chains"],
    palette: "denim + contrast",
    colors: ["Denim blue (#4169E1)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Streetwear aesthetic with layered elements",
    layout: "2x3"
  },
  {
    id: "M-ST5",
    items: ["Harness jacket", "Tech pants", "Tactical boots"],
    palette: "grunge techwear",
    colors: ["Black (#000000)", "Green (#6B8E23)", "Gray (#808080)"],
    style: "Techwear aesthetic with functional elements",
    layout: "2x2"
  },
  {
    id: "M-ST6",
    items: ["Leather jacket", "Graphic tee", "Slim jeans"],
    palette: "dark urban",
    colors: ["Black (#000000)", "Gray (#808080)", "White (#FFFFFF)"],
    style: "Streetwear aesthetic with fitted elements",
    layout: "2x2"
  },
  {
    id: "M-ST7",
    items: ["Bright hoodie", "Baggy jeans", "Chunky sneakers"],
    palette: "y2k brights",
    colors: ["Soft pink (#FFB3BA)", "Light blue (#87CEEB)", "Light yellow (#FFFF99)", "White (#FFFFFF)"],
    style: "Y2K aesthetic with fitted elements",
    layout: "2x2"
  },
  {
    id: "M-ST8",
    items: ["Distressed flannel", "Cargo pants", "Work boots"],
    palette: "grunge earth",
    colors: ["Brown (#8B4513)", "Green (#6B8E23)", "Black (#000000)", "Cream (#F5DEB3)"],
    style: "Grunge aesthetic with relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-ST9",
    items: ["Tech vest", "Utility pants", "Tech sneakers"],
    palette: "tech urban",
    colors: ["Black (#000000)", "Gray (#808080)", "Green (#6B8E23)"],
    style: "Techwear aesthetic with functional elements",
    layout: "2x2"
  },
  {
    id: "M-ST10",
    items: ["Oversized tee", "Baggy cargos", "Chunky sneakers"],
    palette: "urban contrast",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Streetwear aesthetic with oversized elements",
    layout: "2x2"
  },

  // 🤍 Minimalist / Clean Lines - Women (10 outfits)
  {
    id: "F-MIN1",
    items: ["Turtleneck", "Wide-leg trousers"],
    palette: "monochrome white",
    colors: ["White (#FFFFFF)", "Cream (#FFF2CC)"],
    style: "Minimalist aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "F-MIN2",
    items: ["Cropped blazer", "Tube top", "Trousers"],
    palette: "greyscale",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Minimalist aesthetic with tailored elements",
    layout: "2x2"
  },
  {
    id: "F-MIN3",
    items: ["Longline tank", "A-line skirt"],
    palette: "soft neutrals",
    colors: ["Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Minimalist aesthetic with streamlined elements",
    layout: "2x2"
  },
  {
    id: "F-MIN4",
    items: ["Mock neck top", "Minimal culottes"],
    palette: "all black",
    colors: ["Black (#000000)"],
    style: "Minimalist aesthetic with structured elements",
    layout: "2x2"
  },
  {
    id: "F-MIN5",
    items: ["Short trench", "Top", "Tapered pants"],
    palette: "beige + grey",
    colors: ["Cream (#F5DEB3)", "Gray (#808080)", "Beige (#FFF2CC)"],
    style: "Minimalist aesthetic with clean fit elements",
    layout: "2x2"
  },
  {
    id: "F-MIN6",
    items: ["Silk blouse", "Straight pants", "Loafers"],
    palette: "cool neutrals",
    colors: ["Gray (#808080)", "White (#FFFFFF)", "Black (#000000)"],
    style: "Minimalist aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "F-MIN7",
    items: ["Linen dress", "Sandals"],
    palette: "warm neutrals",
    colors: ["Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Minimalist aesthetic with relaxed elements",
    layout: "2x2"
  },
  {
    id: "F-MIN8",
    items: ["Blazer dress", "Ankle boots"],
    palette: "monochrome grey",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with structured elements",
    layout: "2x2"
  },
  {
    id: "F-MIN9",
    items: ["Cream blouse", "White pants", "Loafers"],
    palette: "cream + white",
    colors: ["Cream (#FFF2CC)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with clean fit elements",
    layout: "2x2"
  },
  {
    id: "F-MIN10",
    items: ["Mock neck dress", "Ankle boots"],
    palette: "cool monochrome",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with streamlined elements",
    layout: "2x2"
  },

  // 🤍 Minimalist / Clean Lines - Men (10 outfits)
  {
    id: "M-MIN1",
    items: ["T-shirt", "Cropped pants", "White sneakers"],
    palette: "charcoal + white",
    colors: ["Charcoal (#36454F)", "White (#FFFFFF)", "Black (#000000)"],
    style: "Minimalist aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "M-MIN2",
    items: ["Overcoat", "Minimal knit", "Light trousers"],
    palette: "tonal beige",
    colors: ["Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Minimalist aesthetic with relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-MIN3",
    items: ["Button-up shirt", "Pleated pants"],
    palette: "greyscale",
    colors: ["Black (#000000)", "White (#FFFFFF)", "Gray (#808080)"],
    style: "Minimalist aesthetic with tailored elements",
    layout: "2x2"
  },
  {
    id: "M-MIN4",
    items: ["Jacket", "Tee", "Trousers"],
    palette: "cool monochrome",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with clean elements",
    layout: "2x2"
  },
  {
    id: "M-MIN5",
    items: ["Knit top", "Straight chinos", "Loafers"],
    palette: "warm neutrals",
    colors: ["Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Minimalist aesthetic with minimal elements",
    layout: "2x2"
  },
  {
    id: "M-MIN6",
    items: ["Silk shirt", "Straight pants", "Loafers"],
    palette: "cool neutrals",
    colors: ["Gray (#808080)", "White (#FFFFFF)", "Black (#000000)"],
    style: "Minimalist aesthetic with slim elements",
    layout: "2x2"
  },
  {
    id: "M-MIN7",
    items: ["Linen shirt", "Cotton pants", "Sandals"],
    palette: "warm neutrals",
    colors: ["Cream (#F5DEB3)", "Beige (#FFF2CC)", "Tan (#D2B48C)"],
    style: "Minimalist aesthetic with relaxed elements",
    layout: "2x2"
  },
  {
    id: "M-MIN8",
    items: ["Blazer", "Turtleneck", "Dress pants"],
    palette: "monochrome grey",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with structured elements",
    layout: "2x2"
  },
  {
    id: "M-MIN9",
    items: ["Cream shirt", "White pants", "Loafers"],
    palette: "cream + white",
    colors: ["Cream (#FFF2CC)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with clean fit elements",
    layout: "2x2"
  },
  {
    id: "M-MIN10",
    items: ["Mock neck sweater", "Straight pants"],
    palette: "cool monochrome",
    colors: ["Gray (#808080)", "Black (#000000)", "White (#FFFFFF)"],
    style: "Minimalist aesthetic with streamlined elements",
    layout: "2x2"
  }
];

function generatePrompt(outfit) {
  const layoutText = outfit.layout === "2x2" ? "2x2 grid" : "2x3 vertical grid";
  const itemsText = outfit.items.map((item, index) => {
    const position = outfit.layout === "2x2" 
      ? index === 0 ? "Top Left" : index === 1 ? "Top Right" : index === 2 ? "Bottom Left" : "Bottom Right"
      : index === 0 ? "Row 1 Left" : index === 1 ? "Row 1 Right" : index === 2 ? "Row 2 Left" : index === 3 ? "Row 2 Right" : index === 4 ? "Row 3 Left" : "Row 3 Right";
    return `${position}: ${item}, flat lay photography`;
  }).join("\n");

  return `Create an e-commerce product photography image for a clothing app's style quiz. The image should be:

**Technical Requirements:**
- Square aspect ratio (1:1) for mobile app display
- Pure white background (#FFFFFF)
- High quality, professional e-commerce photography style
- Standard mobile-optimized resolution (800x800px or similar)
- Clean, minimal composition

**Layout Style:**
- Individual clothing items displayed in separate rectangular boxes/containers
- ${layoutText} on pure white background
- Flat lay photography style - items photographed from above on white surface
- Each item box should have subtle borders or shadows to separate items
- No additional styling, props, or decorative elements
- Professional product photography lighting and angles

**Outfit Details:**
# ${outfit.id}: ${outfit.items.join(", ")}

**Layout:** ${layoutText} on pure white background

${itemsText}

**Color Palette:** ${outfit.palette}
**Colors:** ${outfit.colors.join(", ")}
**Style:** ${outfit.style}

**Style Guidelines:**
- E-commerce product photography aesthetic
- Clean, professional presentation
- Items clearly visible and well-lit
- No text, logos, or watermarks
- Focus on the clothing items themselves
- Consistent lighting and photography style across all items
- Layout should be similar but doesn't need to be 100% identical across different outfits

**App Context:**
This image will be displayed in a mobile app quiz where users swipe like/dislike on outfits to determine their style preferences. The layout should mimic how items will be displayed in the actual app interface.`;
}

// Create prompts directory
const promptsDir = path.join(__dirname, '../prompts');
if (!fs.existsSync(promptsDir)) {
  fs.mkdirSync(promptsDir, { recursive: true });
}

// Generate prompts for all outfits
outfits.forEach(outfit => {
  const prompt = generatePrompt(outfit);
  const filePath = path.join(promptsDir, `${outfit.id}-prompt.txt`);
  fs.writeFileSync(filePath, prompt);
  console.log(`Generated prompt: ${outfit.id}-prompt.txt`);
});

console.log(`\nGenerated ${outfits.length} outfit prompts in: ${promptsDir}`);
console.log('\nInstructions:');
console.log('1. Use these prompts with GPT-4o or DALL·E 3 to generate outfit images');
console.log('2. Save the generated images as PNG files with the outfit ID as filename');
console.log('3. Place the images in: public/images/outfit-quiz/');
console.log('4. Update the imageUrl in the outfit data to use .png extension');
