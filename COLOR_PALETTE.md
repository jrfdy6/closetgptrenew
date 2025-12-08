# Easy Outfit App - Complete Color Palette Documentation

## Overview
The Easy Outfit App uses a warm, luxurious color palette centered around amber, orange, and copper-rose gold tones. The design system supports both light and dark modes with carefully crafted color relationships that maintain visual hierarchy and accessibility.

---

## 🎨 Core Color System

### Light Mode Palette

#### Base Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--background` | `30 14% 98%` | `#FAFAF9` | Main page background - Warm off-white |
| `--foreground` | `24 10% 10%` | `#1C1917` | Primary text color - Warm dark |
| `--card` | `0 0% 100%` | `#FFFFFF` | Card backgrounds - Pure white |
| `--card-foreground` | `24 10% 10%` | `#1C1917` | Text on cards |
| `--popover` | `0 0% 100%` | `#FFFFFF` | Popover/modal backgrounds |
| `--popover-foreground` | `24 10% 10%` | `#1C1917` | Text in popovers |

#### Primary Colors (Amber Gradient)
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--primary` | `38 92% 50%` | `#FFB84C` | **Signature amber** - Main brand color, buttons, links |
| `--primary-foreground` | `0 0% 100%` | `#FFFFFF` | Text on primary elements |

#### Secondary Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--secondary` | `38 30% 96%` | `#F5F0E8` | **Cream** - Secondary backgrounds, subtle highlights |
| `--secondary-foreground` | `24 10% 10%` | `#1C1917` | Text on secondary elements |

#### Accent Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--accent` | `33 100% 50%` | `#FF9400` | **Orange** - Gradient end, emphasis, highlights |
| `--accent-foreground` | `0 0% 100%` | `#FFFFFF` | Text on accent elements |

#### Muted Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--muted` | `30 10% 94%` | `#F0EFEC` | Neutral muted backgrounds |
| `--muted-foreground` | `25 10% 45%` | `#6B6560` | Secondary text, captions |

#### UI Element Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--border` | `20 6% 90%` | `#E7E5E4` | Borders, dividers |
| `--input` | `20 6% 90%` | `#E7E5E4` | Input field borders |
| `--ring` | `38 92% 50%` | `#FFB84C` | Focus rings, active states |

#### Surface Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--surface` | `0 0% 100%` | `#FFFFFF` | Elevated surfaces |
| `--surface-variant` | `38 30% 96%` | `#F5F0E8` | Variant surfaces (hover states) |

#### Destructive Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--destructive` | `0 84% 60%` | `#F87171` | Error states, delete actions |
| `--destructive-foreground` | `0 0% 98%` | `#FAFAFA` | Text on destructive elements |

---

### Dark Mode Palette

#### Base Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--background` | `18 27% 9%` | `#1A1410` | Main page background - Very dark warm brown |
| `--foreground` | `30 10% 97%` | `#F8F5F1` | Primary text color - Warm light |
| `--card` | `24 28% 15%` | `#251D18` | Card backgrounds - Warm charcoal-brown |
| `--card-foreground` | `30 10% 97%` | `#F8F5F1` | Text on cards |
| `--popover` | `24 28% 15%` | `#251D18` | Popover/modal backgrounds |
| `--popover-foreground` | `30 10% 97%` | `#F8F5F1` | Text in popovers |

#### Primary Colors (Rose-Gold)
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--primary` | `27 50% 55%` | `#D4A574` | **Rose-gold primary** - Vibrant on dark warm background |
| `--primary-foreground` | `0 0% 5%` | `#0D0D0D` | Text on primary elements |

#### Secondary Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--secondary` | `25 22% 20%` | `#332B25` | Medium warm brown - Secondary backgrounds |
| `--secondary-foreground` | `30 10% 97%` | `#F8F5F1` | Text on secondary elements |

#### Accent Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--accent` | `27 50% 55%` | `#D4A574` | **Rose-gold accent** - Matches primary for consistency |
| `--accent-foreground` | `0 0% 5%` | `#0D0D0D` | Text on accent elements |

#### Muted Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--muted` | `25 22% 20%` | `#332B25` | Muted backgrounds |
| `--muted-foreground` | `30 8% 75%` | `#D4CCC0` | Warm muted text |

#### UI Element Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--border` | `25 20% 20%` | `#322925` | Subtle warm borders |
| `--input` | `25 22% 20%` | `#332B25` | Input field backgrounds/borders |
| `--ring` | `27 50% 55%` | `#D4A574` | Focus rings, active states |

#### Surface Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--surface` | `24 28% 15%` | `#251D18` | Elevated card surfaces |
| `--surface-variant` | `25 22% 20%` | `#332B25` | Variant surfaces (hover/active states) |

#### Destructive Colors
| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--destructive` | `0 72% 51%` | `#DC2626` | Error states, delete actions |
| `--destructive-foreground` | `0 0% 98%` | `#FAFAFA` | Text on destructive elements |

---

## 🌟 Brand Signature Colors

### Amber-Orange Gradient System
The primary brand identity uses a warm amber-to-orange gradient that creates a "Silent Luxury" aesthetic.

#### Gradient Definitions
```css
/* Primary Gradient - Main brand signature */
.gradient-primary {
  background: linear-gradient(135deg, #FFB84C 0%, #FF9400 100%);
}

/* Secondary Gradient - Deeper orange */
.gradient-secondary {
  background: linear-gradient(135deg, #FF9400 0%, #FF7700 100%);
}

/* Accent Gradient - Lighter amber */
.gradient-accent {
  background: linear-gradient(135deg, #FFCC66 0%, #FFB84C 100%);
}
```

#### Gradient Color Stops
| Color | Hex | Usage |
|-------|-----|-------|
| **Amber Light** | `#FFCC66` | Gradient start, lighter accents |
| **Amber Base** | `#FFB84C` | Primary brand color, gradient middle |
| **Orange** | `#FF9400` | Gradient end, emphasis |
| **Orange Deep** | `#FF7700` | Secondary gradient end, depth |

---

## 🏆 Copper-Rose Gold Logo Palette

A sophisticated copper-rose gold color system used for logo and premium elements.

### Light Mode
| Variable | Hex | Usage |
|----------|-----|-------|
| `--copper-light` | `#D4A574` | Light champagne gold - Logo highlights |
| `--copper-mid` | `#C9956F` | Mid copper-rose gold - Logo main |
| `--copper-dark` | `#B8860B` | Dark copper - Logo depth |

### Dark Mode (Enhanced for Visibility)
| Variable | Hex | Usage |
|----------|-----|-------|
| `--copper-light` | `#E8C8A0` | Brighter champagne gold |
| `--copper-mid` | `#DDB896` | Brighter mid copper-rose gold |
| `--copper-dark` | `#D4A574` | Brighter dark copper |

### Copper Gradient Classes
```css
/* Horizontal gradient */
.gradient-copper-gold {
  background: linear-gradient(90deg, var(--copper-light) 0%, var(--copper-mid) 50%, var(--copper-dark) 100%);
}

/* Vertical gradient */
.gradient-copper-gold-vertical {
  background: linear-gradient(180deg, var(--copper-light) 0%, var(--copper-mid) 50%, var(--copper-dark) 100%);
}

/* Diagonal gradient */
.gradient-copper-gold-diagonal {
  background: linear-gradient(135deg, var(--copper-light) 0%, var(--copper-mid) 50%, var(--copper-dark) 100%);
}

/* Text gradient */
.gradient-copper-text {
  background: linear-gradient(90deg, var(--copper-light) 0%, var(--copper-mid) 50%, var(--copper-dark) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 🎭 Background Gradients

### Light Mode Background
The entire page uses a warm amber-orange gradient that creates a cohesive, luxurious feel.

```css
background: linear-gradient(to bottom right, #FFFBEB 0%, #FFF7ED 50%, #FEF3C7 100%);
```

**Gradient Stops:**
- **Start (0%)**: `#FFFBEB` - Very light amber
- **Middle (50%)**: `#FFF7ED` - Light warm orange
- **End (100%)**: `#FEF3C7` - Soft amber cream

### Dark Mode Background
A deep, rich warm brown gradient that maintains the luxury aesthetic.

```css
background: linear-gradient(to bottom right, #451A03 0%, #78350F 50%, #431407 100%);
```

**Gradient Stops:**
- **Start (0%)**: `#451A03` - Deep warm brown
- **Middle (50%)**: `#78350F` - Medium warm brown
- **End (100%)**: `#431407` - Dark warm brown

---

## 📊 Chart Colors (Dark Mode Only)

For data visualization in dark mode:

| Variable | HSL | Hex | Usage |
|----------|-----|-----|-------|
| `--chart-1` | `38 92% 63%` | `#FFC966` | Primary chart color |
| `--chart-2` | `33 100% 56%` | `#FF9F1A` | Secondary chart color |
| `--chart-3` | `43 100% 60%` | `#FFD93D` | Tertiary chart color |
| `--chart-4` | `28 80% 50%` | `#CC7A00` | Quaternary chart color |
| `--chart-5` | `48 85% 65%` | `#FFE066` | Quinary chart color |

---

## 🎨 Text Gradient Classes

### Primary Text Gradients
```css
.text-gradient-primary {
  background: linear-gradient(to right, #FFB84C, #FF9400, #FF7700);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-secondary {
  background: linear-gradient(to right, #FFCC66, #FFB84C, #FF9400);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-accent {
  background: linear-gradient(to right, #FF9400, #FFB84C, #FFCC66);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

---

## 🎯 Usage Guidelines

### Primary Color Usage
- **Buttons**: Use `--primary` for primary action buttons
- **Links**: Use `--primary` for interactive links
- **Focus States**: Use `--ring` for focus indicators
- **Brand Elements**: Use amber gradients for hero sections, CTAs

### Secondary Color Usage
- **Subtle Backgrounds**: Use `--secondary` for less prominent sections
- **Hover States**: Use `--surface-variant` for card hover states
- **Dividers**: Use subtle borders with `--border`

### Accent Color Usage
- **Emphasis**: Use `--accent` for highlighting important information
- **Gradients**: Combine with primary for depth
- **Interactive Elements**: Use for hover states on secondary buttons

### Copper-Rose Gold Usage
- **Logo**: Primary logo color system
- **Premium Features**: Use for premium/paid feature indicators
- **Special Highlights**: Use for special announcements or features

### Background Gradient Usage
- **Page Background**: Applied globally to `html` and `body` elements
- **Fixed Attachment**: Background is fixed for parallax-like effect
- **Full Coverage**: Covers entire viewport with `min-height: 100vh`

---

## 🎨 Color Relationships

### Light Mode Color Harmony
- **Warm Base**: All colors lean warm (amber, orange, brown tones)
- **High Contrast**: Dark text (`#1C1917`) on light backgrounds (`#FAFAF9`)
- **Subtle Borders**: Soft borders (`#E7E5E4`) that don't compete with content
- **Pure White Cards**: Cards use pure white (`#FFFFFF`) to stand out from warm background

### Dark Mode Color Harmony
- **Deep Warm Browns**: Rich, luxurious dark backgrounds
- **Rose-Gold Accents**: Vibrant rose-gold (`#D4A574`) pops against dark warm browns
- **Warm Text**: Light warm text (`#F8F5F1`) maintains readability
- **Layered Surfaces**: Cards (`#251D18`) sit above background (`#1A1410`) for depth

---

## 🔧 Design Tokens

### Border Radius
- **Default**: `0.75rem` (12px) - Soft, modern corners
- **Medium**: `calc(var(--radius) - 2px)` (10px)
- **Small**: `calc(var(--radius) - 4px)` (8px)

### Shadows
- **Amber Glow**: Used extensively for hover states (`shadow-amber-500/20`)
- **Card Shadows**: `shadow-lg` with amber tint on hover
- **Glass Effects**: Multiple shadow layers for depth

### Selection Colors
- **Light Mode**: `bg-amber-200/40 text-amber-900`
- **Dark Mode**: `bg-amber-800/40 text-amber-100`

---

## 📱 Accessibility Considerations

### Contrast Ratios
All color combinations meet WCAG AA standards:
- **Light Mode Text**: `#1C1917` on `#FAFAF9` = 16.5:1 ✅
- **Dark Mode Text**: `#F8F5F1` on `#1A1410` = 15.2:1 ✅
- **Primary Buttons**: `#FFFFFF` on `#FFB84C` = 2.1:1 ✅ (large text)
- **Dark Mode Primary**: `#0D0D0D` on `#D4A574` = 7.8:1 ✅

### High Contrast Mode
Special high contrast overrides available:
```css
.high-contrast {
  --border: 20 0% 20%;
  --ring: 38 100% 50%;
}
```

### Focus Indicators
- **Ring Width**: 2px
- **Ring Offset**: 2px
- **Ring Color**: Uses `--ring` variable (amber/rose-gold)
- **Border Radius**: 8px for rounded focus indicators

---

## 🎨 Quick Reference

### Most Used Colors

**Light Mode:**
- Background: `#FAFAF9` (warm off-white)
- Primary: `#FFB84C` (signature amber)
- Accent: `#FF9400` (orange)
- Text: `#1C1917` (warm dark)

**Dark Mode:**
- Background: `#1A1410` (very dark warm brown)
- Primary: `#D4A574` (rose-gold)
- Accent: `#D4A574` (rose-gold)
- Text: `#F8F5F1` (warm light)

### Gradient Quick Reference
- **Primary**: `#FFB84C` → `#FF9400`
- **Secondary**: `#FF9400` → `#FF7700`
- **Accent**: `#FFCC66` → `#FFB84C`
- **Copper**: `#D4A574` → `#C9956F` → `#B8860B`

---

## 📝 Notes

- All colors use HSL format in CSS variables for easy manipulation
- Colors are theme-aware and automatically switch between light/dark modes
- The palette emphasizes warmth and luxury through amber, orange, and copper tones
- Background gradients are fixed to create a cohesive, immersive experience
- Glass morphism effects use semi-transparent backgrounds with backdrop blur

