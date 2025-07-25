const fs = require('fs');
const path = require('path');

// Define all outfits with their metadata
const outfits = [
  // 🌿 Cottagecore / Boho - Women (10 outfits)
  { id: "F-CB1", palette: "soft florals", silhouette: "flowy", description: "Floral maxi dress, cropped knit cardigan, leather boots" },
  { id: "F-CB2", palette: "warm earth tones", silhouette: "layered", description: "Peasant blouse, patchwork skirt, vest, floppy hat" },
  { id: "F-CB3", palette: "dusty pastels", silhouette: "loose", description: "Ruffle blouse, wide-leg linen pants, fringe shawl" },
  { id: "F-CB4", palette: "natural earth", silhouette: "easy", description: "Muslin wrap dress, open-toe sandals" },
  { id: "F-CB5", palette: "dried floral mix", silhouette: "romantic", description: "Button-front midi dress, wool capelet, ankle boots" },
  { id: "F-CB6", palette: "warm earth tones", silhouette: "flowy", description: "Crochet top, maxi skirt, leather belt" },
  { id: "F-CB7", palette: "soft pastels", silhouette: "easy", description: "Linen sundress, straw hat, espadrilles" },
  { id: "F-CB8", palette: "mixed earth tones", silhouette: "layered", description: "Embroidered blouse, tiered skirt, vest, jewelry" },
  { id: "F-CB9", palette: "muted florals", silhouette: "flowy", description: "Floral tea dress, cardigan, ankle boots" },
  { id: "F-CB10", palette: "warm neutrals", silhouette: "relaxed", description: "Linen jumpsuit, woven bag, sandals" },

  // 🌿 Cottagecore / Boho - Men (10 outfits)
  { id: "M-CB1", palette: "cream & olive", silhouette: "relaxed", description: "Linen shirt, cargo trousers, fisherman cardigan" },
  { id: "M-CB2", palette: "warm taupe", silhouette: "flowy", description: "Henley, cotton pants, leather sandals" },
  { id: "M-CB3", palette: "vintage neutrals", silhouette: "rustic", description: "Chambray shirt, suspenders, wool vest, canvas boots" },
  { id: "M-CB4", palette: "soft moss green", silhouette: "loose", description: "Pullover tunic, drawstring trousers, woven belt" },
  { id: "M-CB5", palette: "terracotta mix", silhouette: "breezy", description: "Knit tank, patchwork overshirt, rolled linen pants" },
  { id: "M-CB6", palette: "earth tones", silhouette: "relaxed", description: "Linen shirt, khaki pants, leather belt" },
  { id: "M-CB7", palette: "warm neutrals", silhouette: "flowy", description: "Oversized shirt, loose pants, sandals" },
  { id: "M-CB8", palette: "muted earth", silhouette: "rustic", description: "Corduroy shirt, wool vest, canvas pants" },
  { id: "M-CB9", palette: "soft greens", silhouette: "relaxed", description: "Cotton tee, linen pants, woven hat" },
  { id: "M-CB10", palette: "mixed earth", silhouette: "layered", description: "Embroidered shirt, vest, cargo pants, jewelry" },

  // 💼 Old Money / Preppy / Classic - Women (10 outfits)
  { id: "F-OM1", palette: "navy + cream", silhouette: "tailored", description: "Tweed blazer, pleated skirt, loafers" },
  { id: "F-OM2", palette: "rich neutrals", silhouette: "structured", description: "Cable knit over collared blouse, pressed trousers" },
  { id: "F-OM3", palette: "soft jewel tones", silhouette: "sophisticated", description: "Wool coat, dress shirt, midi skirt, heels" },
  { id: "F-OM4", palette: "champagne & blush", silhouette: "elegant", description: "Silk blouse, beige high-waist trousers" },
  { id: "F-OM5", palette: "green & brown", silhouette: "academic", description: "Blazer, check trousers, button-down" },
  { id: "F-OM6", palette: "navy & white", silhouette: "tailored", description: "Polo dress, cardigan, boat shoes" },
  { id: "F-OM7", palette: "monochrome", silhouette: "structured", description: "Trench coat, turtleneck, wide-leg pants" },
  { id: "F-OM8", palette: "tweed tones", silhouette: "academic", description: "Tweed blazer, pleated skirt, oxfords" },
  { id: "F-OM9", palette: "pastel preppy", silhouette: "tailored", description: "Polo shirt, khaki skirt, loafers" },
  { id: "F-OM10", palette: "luxury neutrals", silhouette: "elegant", description: "Silk dress, cashmere cardigan, pearls" },

  // 💼 Old Money / Preppy / Classic - Men (10 outfits)
  { id: "M-OM1", palette: "charcoal & cream", silhouette: "tailored", description: "Double-breasted coat, Oxford, tapered trousers" },
  { id: "M-OM2", palette: "navy + tan", silhouette: "slim", description: "Polo under cardigan, chinos" },
  { id: "M-OM3", palette: "deep burgundy", silhouette: "structured", description: "Knit vest, button-down, wool slacks" },
  { id: "M-OM4", palette: "olive + cream", silhouette: "academic", description: "Houndstooth coat, cashmere sweater, khakis" },
  { id: "M-OM5", palette: "white + camel", silhouette: "elegant", description: "Trench, turtleneck, tailored pants" },
  { id: "M-OM6", palette: "navy & white", silhouette: "slim", description: "Polo shirt, white pants, boat shoes" },
  { id: "M-OM7", palette: "greyscale", silhouette: "tailored", description: "Suit jacket, turtleneck, dress pants" },
  { id: "M-OM8", palette: "tweed browns", silhouette: "academic", description: "Tweed blazer, corduroy pants, oxfords" },
  { id: "M-OM9", palette: "pastel preppy", silhouette: "slim", description: "Pastel polo, khaki pants, loafers" },
  { id: "M-OM10", palette: "luxury neutrals", silhouette: "elegant", description: "Cashmere sweater, silk tie, wool pants" },

  // 🖤 Streetwear / Edgy / Grunge - Women (10 outfits)
  { id: "F-ST1", palette: "black + red", silhouette: "oversized", description: "Bomber, graphic tee, wide-leg cargos, bucket hat" },
  { id: "F-ST2", palette: "muted neutrals", silhouette: "relaxed", description: "Cropped hoodie, parachute pants, combat boots" },
  { id: "F-ST3", palette: "greyscale pop", silhouette: "boxy", description: "Windbreaker, baggy denim, thermal top" },
  { id: "F-ST4", palette: "y2k high contrast", silhouette: "fitted + loud", description: "Mesh top, mini skirt, fur jacket" },
  { id: "F-ST5", palette: "grunge mix", silhouette: "unstructured", description: "Plaid overshirt, destroyed jeans, band tee" },
  { id: "F-ST6", palette: "dark contrast", silhouette: "fitted", description: "Leather jacket, crop top, ripped jeans" },
  { id: "F-ST7", palette: "urban tech", silhouette: "functional", description: "Utility vest, cargo pants, tech sneakers" },
  { id: "F-ST8", palette: "y2k pastels", silhouette: "fitted", description: "Crop top, low-rise jeans, platform shoes" },
  { id: "F-ST9", palette: "grunge earth", silhouette: "relaxed", description: "Flannel shirt, mom jeans, combat boots" },
  { id: "F-ST10", palette: "urban contrast", silhouette: "oversized", description: "Oversized hoodie, bike shorts, chunky sneakers" },

  // 🖤 Streetwear / Edgy / Grunge - Men (10 outfits)
  { id: "M-ST1", palette: "washed black", silhouette: "boxy", description: "Flannel shirt, band tee, black jeans" },
  { id: "M-ST2", palette: "urban muted", silhouette: "oversized", description: "Hoodie, puffer, cargos, Nike Dunks" },
  { id: "M-ST3", palette: "army green & grey", silhouette: "baggy", description: "Longline tee, joggers, beanie" },
  { id: "M-ST4", palette: "denim + contrast", silhouette: "layered", description: "Denim jacket, flannel, hoodie, tee, chains" },
  { id: "M-ST5", palette: "grunge techwear", silhouette: "functional", description: "Harness jacket, tech pants, tactical boots" },
  { id: "M-ST6", palette: "dark urban", silhouette: "fitted", description: "Leather jacket, graphic tee, slim jeans" },
  { id: "M-ST7", palette: "y2k brights", silhouette: "fitted", description: "Bright hoodie, baggy jeans, chunky sneakers" },
  { id: "M-ST8", palette: "grunge earth", silhouette: "relaxed", description: "Distressed flannel, cargo pants, work boots" },
  { id: "M-ST9", palette: "tech urban", silhouette: "functional", description: "Tech vest, utility pants, tech sneakers" },
  { id: "M-ST10", palette: "urban contrast", silhouette: "oversized", description: "Oversized tee, baggy cargos, chunky sneakers" },

  // 🤍 Minimalist / Clean Lines - Women (10 outfits)
  { id: "F-MIN1", palette: "monochrome white", silhouette: "slim", description: "Turtleneck, wide-leg trousers" },
  { id: "F-MIN2", palette: "greyscale", silhouette: "tailored", description: "Cropped blazer, tube top, trousers" },
  { id: "F-MIN3", palette: "soft neutrals", silhouette: "streamlined", description: "Longline tank, A-line skirt" },
  { id: "F-MIN4", palette: "all black", silhouette: "structured", description: "Mock neck top, minimal culottes" },
  { id: "F-MIN5", palette: "beige + grey", silhouette: "clean fit", description: "Short trench, top, tapered pants" },
  { id: "F-MIN6", palette: "cool neutrals", silhouette: "slim", description: "Silk blouse, straight pants, loafers" },
  { id: "F-MIN7", palette: "warm neutrals", silhouette: "relaxed", description: "Linen dress, sandals" },
  { id: "F-MIN8", palette: "monochrome grey", silhouette: "structured", description: "Blazer dress, ankle boots" },
  { id: "F-MIN9", palette: "cream + white", silhouette: "clean fit", description: "Cream blouse, white pants, loafers" },
  { id: "F-MIN10", palette: "cool monochrome", silhouette: "streamlined", description: "Mock neck dress, ankle boots" },

  // 🤍 Minimalist / Clean Lines - Men (10 outfits)
  { id: "M-MIN1", palette: "charcoal + white", silhouette: "slim", description: "T-shirt, cropped pants, white sneakers" },
  { id: "M-MIN2", palette: "tonal beige", silhouette: "relaxed", description: "Overcoat, minimal knit, light trousers" },
  { id: "M-MIN3", palette: "greyscale", silhouette: "tailored", description: "Button-up, pleated pants" },
  { id: "M-MIN4", palette: "cool monochrome", silhouette: "clean", description: "Jacket, tee, trousers — all in same tone" },
  { id: "M-MIN5", palette: "warm neutrals", silhouette: "minimal", description: "Knit top, straight chinos, loafers" },
  { id: "M-MIN6", palette: "cool neutrals", silhouette: "slim", description: "Silk shirt, straight pants, loafers" },
  { id: "M-MIN7", palette: "warm neutrals", silhouette: "relaxed", description: "Linen shirt, cotton pants, sandals" },
  { id: "M-MIN8", palette: "monochrome grey", silhouette: "structured", description: "Blazer, turtleneck, dress pants" },
  { id: "M-MIN9", palette: "cream + white", silhouette: "clean fit", description: "Cream shirt, white pants, loafers" },
  { id: "M-MIN10", palette: "cool monochrome", silhouette: "streamlined", description: "Mock neck sweater, straight pants" }
];

// Color palette definitions
const colorPalettes = {
  "soft florals": ["#FFB3BA", "#E6B3FF", "#B3FFB3", "#FFF2CC"],
  "warm earth tones": ["#8B4513", "#F5DEB3", "#FFF2CC", "#CD853F", "#6B8E23"],
  "dusty pastels": ["#DDA0DD", "#B3FFB3", "#87CEEB", "#FFF2CC"],
  "natural earth": ["#8B4513", "#228B22", "#F5DEB3", "#D2B48C"],
  "dried floral mix": ["#CD5C5C", "#B3FFB3", "#FFB3BA", "#FFF2CC"],
  "mixed earth tones": ["#8B4513", "#6B8E23", "#CD5C5C", "#F5DEB3"],
  "muted florals": ["#FFB3BA", "#B3FFB3", "#FFF2CC", "#DDA0DD"],
  "warm neutrals": ["#F5DEB3", "#8B4513", "#FFF2CC", "#D2B48C"],
  "navy + cream": ["#000080", "#FFF2CC", "#FFFFFF"],
  "rich neutrals": ["#8B4513", "#F5DEB3", "#FFF2CC", "#D2B48C"],
  "soft jewel tones": ["#8B0000", "#000080", "#228B22", "#FFF2CC"],
  "champagne & blush": ["#F7E7CE", "#FFB3BA", "#FFF2CC"],
  "green & brown": ["#228B22", "#8B4513", "#F5DEB3"],
  "pastel preppy": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "luxury neutrals": ["#FFF2CC", "#F5DEB3", "#8B4513", "#D2B48C"],
  "black + red": ["#000000", "#FF0000", "#FFFFFF"],
  "muted neutrals": ["#808080", "#000000", "#FFFFFF", "#F5DEB3"],
  "greyscale pop": ["#000000", "#FFFFFF", "#808080"],
  "y2k high contrast": ["#FFB3BA", "#87CEEB", "#FFFF99", "#000000"],
  "grunge mix": ["#000000", "#8B4513", "#6B8E23", "#808080"],
  "dark contrast": ["#000000", "#FFFFFF", "#FF0000"],
  "urban tech": ["#000000", "#808080", "#6B8E23", "#FFFFFF"],
  "y2k pastels": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "grunge earth": ["#8B4513", "#6B8E23", "#000000", "#F5DEB3"],
  "urban contrast": ["#000000", "#FFFFFF", "#808080"],
  "washed black": ["#000000", "#808080", "#FFFFFF"],
  "urban muted": ["#808080", "#000000", "#FFFFFF", "#F5DEB3"],
  "army green & grey": ["#6B8E23", "#808080", "#000000"],
  "denim + contrast": ["#4169E1", "#000000", "#FFFFFF"],
  "grunge techwear": ["#000000", "#6B8E23", "#808080"],
  "dark urban": ["#000000", "#808080", "#FFFFFF"],
  "y2k brights": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "tech urban": ["#000000", "#808080", "#6B8E23"],
  "monochrome white": ["#FFFFFF", "#FFF2CC"],
  "greyscale": ["#000000", "#FFFFFF", "#808080"],
  "soft neutrals": ["#F5DEB3", "#FFF2CC", "#D2B48C"],
  "all black": ["#000000"],
  "beige + grey": ["#F5DEB3", "#808080", "#FFF2CC"],
  "cool neutrals": ["#808080", "#FFFFFF", "#000000"],
  "monochrome grey": ["#808080", "#000000", "#FFFFFF"],
  "cream + white": ["#FFF2CC", "#FFFFFF"],
  "cool monochrome": ["#808080", "#000000", "#FFFFFF"],
  "charcoal + white": ["#36454F", "#FFFFFF", "#000000"],
  "navy + tan": ["#000080", "#D2B48C", "#FFFFFF"],
  "deep burgundy": ["#8B0000", "#000000", "#FFFFFF"],
  "olive + cream": ["#6B8E23", "#FFF2CC", "#8B4513"],
  "white + camel": ["#FFFFFF", "#C19A6B", "#FFF2CC"],
  "tweed tones": ["#8B4513", "#F5DEB3", "#6B8E23"],
  "tweed browns": ["#8B4513", "#F5DEB3", "#6B8E23"],
  "tonal beige": ["#F5DEB3", "#FFF2CC", "#D2B48C"],
  "cream & olive": ["#FFF2CC", "#6B8E23"],
  "warm taupe": ["#D2B48C"],
  "vintage neutrals": ["#8B4513", "#F5DEB3", "#D2B48C"],
  "soft moss green": ["#B3FFB3"],
  "terracotta mix": ["#CD5C5C", "#8B4513"],
  "earth tones": ["#8B4513", "#228B22", "#F5DEB3"],
  "muted earth": ["#8B4513", "#F5DEB3", "#D2B48C"],
  "soft greens": ["#B3FFB3", "#228B22"],
  "mixed earth": ["#8B4513", "#6B8E23", "#CD5C5C"],
  "rich neutrals": ["#8B4513", "#F5DEB3", "#FFF2CC", "#D2B48C"],
  "soft jewel tones": ["#8B0000", "#000080", "#228B22", "#FFF2CC"],
  "champagne & blush": ["#F7E7CE", "#FFB3BA", "#FFF2CC"],
  "green & brown": ["#228B22", "#8B4513", "#F5DEB3"],
  "pastel preppy": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "luxury neutrals": ["#FFF2CC", "#F5DEB3", "#8B4513", "#D2B48C"],
  "navy & white": ["#000080", "#FFFFFF"],
  "monochrome": ["#000000", "#FFFFFF", "#808080"],
  "tweed tones": ["#8B4513", "#F5DEB3", "#6B8E23"],
  "pastel preppy": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "luxury neutrals": ["#FFF2CC", "#F5DEB3", "#8B4513", "#D2B48C"],
  "muted neutrals": ["#808080", "#000000", "#FFFFFF", "#F5DEB3"],
  "greyscale pop": ["#000000", "#FFFFFF", "#808080"],
  "y2k high contrast": ["#FFB3BA", "#87CEEB", "#FFFF99", "#000000"],
  "grunge mix": ["#000000", "#8B4513", "#6B8E23", "#808080"],
  "dark contrast": ["#000000", "#FFFFFF", "#FF0000"],
  "urban tech": ["#000000", "#808080", "#6B8E23", "#FFFFFF"],
  "y2k pastels": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "grunge earth": ["#8B4513", "#6B8E23", "#000000", "#F5DEB3"],
  "urban contrast": ["#000000", "#FFFFFF", "#808080"],
  "washed black": ["#000000", "#808080", "#FFFFFF"],
  "urban muted": ["#808080", "#000000", "#FFFFFF", "#F5DEB3"],
  "army green & grey": ["#6B8E23", "#808080", "#000000"],
  "denim + contrast": ["#4169E1", "#000000", "#FFFFFF"],
  "grunge techwear": ["#000000", "#6B8E23", "#808080"],
  "dark urban": ["#000000", "#808080", "#FFFFFF"],
  "y2k brights": ["#FFB3BA", "#87CEEB", "#FFFF99", "#FFFFFF"],
  "tech urban": ["#000000", "#808080", "#6B8E23"],
  "monochrome white": ["#FFFFFF", "#FFF2CC"],
  "greyscale": ["#000000", "#FFFFFF", "#808080"],
  "soft neutrals": ["#F5DEB3", "#FFF2CC", "#D2B48C"],
  "all black": ["#000000"],
  "beige + grey": ["#F5DEB3", "#808080", "#FFF2CC"],
  "cool neutrals": ["#808080", "#FFFFFF", "#000000"],
  "monochrome grey": ["#808080", "#000000", "#FFFFFF"],
  "cream + white": ["#FFF2CC", "#FFFFFF"],
  "cool monochrome": ["#808080", "#000000", "#FFFFFF"],
  "charcoal + white": ["#36454F", "#FFFFFF", "#000000"],
  "navy + tan": ["#000080", "#D2B48C", "#FFFFFF"],
  "deep burgundy": ["#8B0000", "#000000", "#FFFFFF"],
  "olive + cream": ["#6B8E23", "#FFF2CC", "#8B4513"],
  "white + camel": ["#FFFFFF", "#C19A6B", "#FFF2CC"],
  "tweed tones": ["#8B4513", "#F5DEB3", "#6B8E23"],
  "tweed browns": ["#8B4513", "#F5DEB3", "#6B8E23"],
  "tonal beige": ["#F5DEB3", "#FFF2CC", "#D2B48C"]
};

function generateSVG(outfit) {
  const colors = colorPalettes[outfit.palette] || ["#808080"];
  const isFemale = outfit.id.startsWith('F-');
  
  // Create realistic outfit silhouette based on gender and style
  const svg = `
<svg width="200" height="300" viewBox="0 0 200 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-${outfit.id}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${colors[0]};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${colors[1] || colors[0]};stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="200" height="300" fill="#f8f9fa" rx="10"/>
  
  <!-- Outfit silhouette -->
  <g transform="translate(100, 150)">
    ${generateOutfitSilhouette(outfit, colors, isFemale)}
  </g>
  
  <!-- Outfit ID -->
  <text x="100" y="280" text-anchor="middle" 
        font-family="Arial, sans-serif" font-size="10" fill="#666">
    ${outfit.id}
  </text>
</svg>`;

  return svg;
}

function generateOutfitSilhouette(outfit, colors, isFemale) {
  const silhouette = outfit.silhouette;
  
  if (isFemale) {
    return generateFemaleSilhouette(silhouette, colors, outfit);
  } else {
    return generateMaleSilhouette(silhouette, colors, outfit);
  }
}

function generateFemaleSilhouette(silhouette, colors, outfit) {
  switch (silhouette) {
    case "flowy":
      return `
        <!-- Dress -->
        <path d="M -25 -60 Q 0 -50 25 -60 L 30 40 Q 0 50 -30 40 Z" 
              fill="url(#bg-${outfit.id})" stroke="#333" stroke-width="1"/>
        <!-- Cardigan -->
        <path d="M -35 -40 Q 0 -30 35 -40 L 40 20 Q 0 30 -40 20 Z" 
              fill="${colors[1] || colors[0]}" opacity="0.8" stroke="#333" stroke-width="1"/>
        <!-- Boots -->
        <rect x="-15" y="35" width="30" height="15" fill="#333" rx="2"/>
      `;
      
    case "layered":
      return `
        <!-- Blouse -->
        <path d="M -20 -50 Q 0 -40 20 -50 L 25 10 Q 0 20 -25 10 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Skirt -->
        <path d="M -30 5 Q 0 15 30 5 L 35 45 Q 0 55 -35 45 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Vest -->
        <path d="M -25 -30 Q 0 -20 25 -30 L 30 0 Q 0 10 -30 0 Z" 
              fill="${colors[2] || colors[0]}" opacity="0.7" stroke="#333" stroke-width="1"/>
      `;
      
    case "tailored":
      return `
        <!-- Blazer -->
        <path d="M -30 -50 Q 0 -40 30 -50 L 35 20 Q 0 30 -35 20 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Skirt -->
        <path d="M -25 15 Q 0 25 25 15 L 30 45 Q 0 55 -30 45 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Collar -->
        <path d="M -15 -45 L 15 -45 L 10 -35 L -10 -35 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
      
    case "structured":
      return `
        <!-- Coat -->
        <path d="M -35 -60 Q 0 -50 35 -60 L 40 30 Q 0 40 -40 30 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Pants -->
        <path d="M -20 25 L 20 25 L 25 55 L -25 55 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Belt -->
        <rect x="-20" y="20" width="40" height="5" fill="#333"/>
      `;
      
    case "oversized":
      return `
        <!-- Oversized top -->
        <path d="M -40 -40 Q 0 -30 40 -40 L 45 20 Q 0 30 -45 20 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Cargo pants -->
        <path d="M -25 15 L 25 15 L 30 55 L -30 55 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Cargo pockets -->
        <rect x="-20" y="25" width="8" height="12" fill="${colors[2] || colors[0]}" opacity="0.8"/>
        <rect x="12" y="25" width="8" height="12" fill="${colors[2] || colors[0]}" opacity="0.8"/>
      `;
      
    default:
      return `
        <!-- Simple dress -->
        <path d="M -25 -50 Q 0 -40 25 -50 L 30 40 Q 0 50 -30 40 Z" 
              fill="url(#bg-${outfit.id})" stroke="#333" stroke-width="1"/>
        <!-- Neckline -->
        <path d="M -10 -45 Q 0 -40 10 -45" 
              fill="none" stroke="#333" stroke-width="1"/>
      `;
  }
}

function generateMaleSilhouette(silhouette, colors, outfit) {
  switch (silhouette) {
    case "tailored":
      return `
        <!-- Suit jacket -->
        <path d="M -30 -50 Q 0 -40 30 -50 L 35 20 Q 0 30 -35 20 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Pants -->
        <path d="M -20 15 L 20 15 L 25 55 L -25 55 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Collar -->
        <path d="M -15 -45 L 15 -45 L 10 -35 L -10 -35 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
      
    case "relaxed":
      return `
        <!-- Shirt -->
        <path d="M -25 -45 Q 0 -35 25 -45 L 30 15 Q 0 25 -30 15 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Pants -->
        <path d="M -20 10 L 20 10 L 25 50 L -25 50 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Cardigan -->
        <path d="M -30 -35 Q 0 -25 30 -35 L 35 5 Q 0 15 -35 5 Z" 
              fill="${colors[2] || colors[0]}" opacity="0.8" stroke="#333" stroke-width="1"/>
      `;
      
    case "oversized":
      return `
        <!-- Oversized hoodie -->
        <path d="M -35 -40 Q 0 -30 35 -40 L 40 20 Q 0 30 -40 20 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Hood -->
        <path d="M -20 -45 Q 0 -55 20 -45 Q 0 -35 -20 -45 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Cargo pants -->
        <path d="M -25 15 L 25 15 L 30 55 L -30 55 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
      
    case "boxy":
      return `
        <!-- Flannel shirt -->
        <path d="M -25 -45 Q 0 -35 25 -45 L 30 15 Q 0 25 -30 15 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Plaid pattern -->
        <line x1="-25" y1="-35" x2="25" y2="-35" stroke="#333" stroke-width="0.5"/>
        <line x1="-25" y1="-25" x2="25" y2="-25" stroke="#333" stroke-width="0.5"/>
        <line x1="-15" y1="-45" x2="-15" y2="15" stroke="#333" stroke-width="0.5"/>
        <line x1="5" y1="-45" x2="5" y2="15" stroke="#333" stroke-width="0.5"/>
        <!-- Jeans -->
        <path d="M -20 10 L 20 10 L 25 50 L -25 50 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
      
    case "slim":
      return `
        <!-- Slim shirt -->
        <path d="M -20 -45 Q 0 -35 20 -45 L 25 15 Q 0 25 -25 15 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Slim pants -->
        <path d="M -15 10 L 15 10 L 20 50 L -20 50 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
      
    default:
      return `
        <!-- Basic shirt -->
        <path d="M -25 -45 Q 0 -35 25 -45 L 30 15 Q 0 25 -30 15 Z" 
              fill="${colors[0]}" stroke="#333" stroke-width="1"/>
        <!-- Basic pants -->
        <path d="M -20 10 L 20 10 L 25 50 L -25 50 Z" 
              fill="${colors[1] || colors[0]}" stroke="#333" stroke-width="1"/>
      `;
  }
}

// Ensure directory exists
const outputDir = path.join(__dirname, '../public/images/outfit-quiz');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Generate SVG files for all outfits
outfits.forEach(outfit => {
  const svg = generateSVG(outfit);
  const filePath = path.join(outputDir, `${outfit.id}.svg`);
  fs.writeFileSync(filePath, svg);
  console.log(`Generated: ${outfit.id}.svg`);
});

console.log(`\nGenerated ${outfits.length} outfit SVG images in: ${outputDir}`);
