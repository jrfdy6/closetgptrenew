# Dark Mode Color Palette Variations

This document contains 4 alternative dark mode color palettes that replace the current brown/grey tones while preserving the signature amber and gold gradients.

## Current Palette (For Reference)
- Background: `#1A1510` (amber-tinted dark brown)
- Card: `#2C2119` (warm dark brown)
- Secondary/Muted: `#3D2F24` (warm grey-brown)
- Border: `#3D2F24` (warm grey-brown)

---

## Variation 1: Deep Navy Midnight
**Theme:** Sophisticated midnight blue with amber gold accents - like a luxury watch

```css
.dark {
  /* Deep Navy Midnight with Amber Gold */
  --background: 220 30% 8%;            /* #0F1419 - Deep navy */
  --foreground: 30 10% 97%;            /* #F8F5F1 - Warm light (keeps warm text) */

  --card: 220 25% 12%;                 /* #1A2330 - Rich navy surface */
  --card-foreground: 30 10% 97%;

  --popover: 220 25% 12%;
  --popover-foreground: 30 10% 97%;

  /* Primary: Amber (vibrant on dark) */
  --primary: 38 92% 63%;               /* #FFB84C - Signature amber */
  --primary-foreground: 220 30% 8%;

  /* Secondary: Darker navy */
  --secondary: 220 20% 18%;            /* #2A3441 - Navy variant */
  --secondary-foreground: 30 10% 97%;

  --muted: 220 20% 18%;
  --muted-foreground: 30 8% 75%;       /* #D4CCC0 - Warm muted text */

  /* Accent: Orange (vibrant on dark) */
  --accent: 33 100% 56%;               /* #FF9400 - Orange */
  --accent-foreground: 220 30% 8%;

  --destructive: 0 72% 51%;
  --destructive-foreground: 0 0% 98%;

  --border: 220 20% 20%;               /* #2F3A47 - Navy border */
  --input: 220 20% 18%;
  --ring: 38 92% 63%;
  
  --surface: 220 25% 12%;              /* #1A2330 - Cards */
  --surface-variant: 220 20% 18%;      /* #2A3441 - Hover/active */
}
```

**Component Usage:**
- `dark:bg-[#0F1419]` - Background
- `dark:bg-[#1A2330]` - Cards
- `dark:border-[#2F3A47]` - Borders
- `dark:hover:bg-[#2A3441]` - Hover states

---

## Variation 2: Pure Black Luxury
**Theme:** Rich true black with amber gold accents - high contrast, modern, builds on black components you like

```css
.dark {
  /* Pure Black Luxury with Amber Gold */
  --background: 0 0% 5%;               /* #0D0D0D - Almost pure black */
  --foreground: 30 10% 97%;            /* #F8F5F1 - Warm light */

  --card: 0 0% 10%;                    /* #1A1A1A - Rich charcoal-black */
  --card-foreground: 30 10% 97%;

  --popover: 0 0% 10%;
  --popover-foreground: 30 10% 97%;

  /* Primary: Amber (vibrant on dark) */
  --primary: 38 92% 63%;               /* #FFB84C - Signature amber */
  --primary-foreground: 0 0% 5%;

  /* Secondary: Darker charcoal */
  --secondary: 0 0% 15%;               /* #262626 - Charcoal variant */
  --secondary-foreground: 30 10% 97%;

  --muted: 0 0% 15%;
  --muted-foreground: 30 8% 75%;       /* #D4CCC0 - Warm muted text */

  /* Accent: Orange (vibrant on dark) */
  --accent: 33 100% 56%;               /* #FF9400 - Orange */
  --accent-foreground: 0 0% 5%;

  --destructive: 0 72% 51%;
  --destructive-foreground: 0 0% 98%;

  --border: 0 0% 18%;                  /* #2E2E2E - Subtle border */
  --input: 0 0% 15%;
  --ring: 38 92% 63%;
  
  --surface: 0 0% 10%;                 /* #1A1A1A - Cards */
  --surface-variant: 0 0% 15%;         /* #262626 - Hover/active */
}
```

**Component Usage:**
- `dark:bg-[#0D0D0D]` - Background
- `dark:bg-[#1A1A1A]` - Cards
- `dark:border-[#2E2E2E]` - Borders
- `dark:hover:bg-[#262626]` - Hover states

---

## Variation 3: Deep Plum Elegance
**Theme:** Rich deep purple/plum with amber gold accents - elegant and warm but distinct from brown

```css
.dark {
  /* Deep Plum Elegance with Amber Gold */
  --background: 280 25% 8%;            /* #1A141D - Deep plum */
  --foreground: 30 10% 97%;            /* #F8F5F1 - Warm light */

  --card: 280 20% 12%;                 /* #251F2B - Rich plum surface */
  --card-foreground: 30 10% 97%;

  --popover: 280 20% 12%;
  --popover-foreground: 30 10% 97%;

  /* Primary: Amber (vibrant on dark) */
  --primary: 38 92% 63%;               /* #FFB84C - Signature amber */
  --primary-foreground: 280 25% 8%;

  /* Secondary: Darker plum */
  --secondary: 280 15% 18%;            /* #342D3D - Plum variant */
  --secondary-foreground: 30 10% 97%;

  --muted: 280 15% 18%;
  --muted-foreground: 30 8% 75%;       /* #D4CCC0 - Warm muted text */

  /* Accent: Orange (vibrant on dark) */
  --accent: 33 100% 56%;               /* #FF9400 - Orange */
  --accent-foreground: 280 25% 8%;

  --destructive: 0 72% 51%;
  --destructive-foreground: 0 0% 98%;

  --border: 280 15% 20%;               /* #3A3244 - Plum border */
  --input: 280 15% 18%;
  --ring: 38 92% 63%;
  
  --surface: 280 20% 12%;              /* #251F2B - Cards */
  --surface-variant: 280 15% 18%;      /* #342D3D - Hover/active */
}
```

**Component Usage:**
- `dark:bg-[#1A141D]` - Background
- `dark:bg-[#251F2B]` - Cards
- `dark:border-[#3A3244]` - Borders
- `dark:hover:bg-[#342D3D]` - Hover states

---

## Variation 4: Charcoal Slate Modern
**Theme:** Clean charcoal slate with amber gold accents - modern and professional, cleaner than warm greys

```css
.dark {
  /* Charcoal Slate Modern with Amber Gold */
  --background: 210 15% 8%;            /* #121618 - Deep charcoal */
  --foreground: 30 10% 97%;            /* #F8F5F1 - Warm light */

  --card: 210 12% 12%;                 /* #1C2225 - Slate surface */
  --card-foreground: 30 10% 97%;

  --popover: 210 12% 12%;
  --popover-foreground: 30 10% 97%;

  /* Primary: Amber (vibrant on dark) */
  --primary: 38 92% 63%;               /* #FFB84C - Signature amber */
  --primary-foreground: 210 15% 8%;

  /* Secondary: Darker slate */
  --secondary: 210 10% 18%;            /* #2B3236 - Slate variant */
  --secondary-foreground: 30 10% 97%;

  --muted: 210 10% 18%;
  --muted-foreground: 30 8% 75%;       /* #D4CCC0 - Warm muted text */

  /* Accent: Orange (vibrant on dark) */
  --accent: 33 100% 56%;               /* #FF9400 - Orange */
  --accent-foreground: 210 15% 8%;

  --destructive: 0 72% 51%;
  --destructive-foreground: 0 0% 98%;

  --border: 210 10% 20%;               /* #31383D - Slate border */
  --input: 210 10% 18%;
  --ring: 38 92% 63%;
  
  --surface: 210 12% 12%;              /* #1C2225 - Cards */
  --surface-variant: 210 10% 18%;      /* #2B3236 - Hover/active */
}
```

**Component Usage:**
- `dark:bg-[#121618]` - Background
- `dark:bg-[#1C2225]` - Cards
- `dark:border-[#31383D]` - Borders
- `dark:hover:bg-[#2B3236]` - Hover states

---

## Quick Implementation Guide

### Step 1: Update CSS Variables in `globals.css`

1. Open `frontend/src/app/globals.css`
2. Find the `.dark` section (around line 292-335)
3. Replace the entire `.dark` block with one of the variations from `dark-mode-variations.css`
4. Find `.dark body` section (around line 360-363)
5. Replace the gradient with the matching gradient from your chosen variation
6. Save the file

### Step 2: Update Component-Level Hardcoded Colors

After updating the CSS variables, you need to update hardcoded colors in components. Use find & replace:

**Find these patterns in your components:**
- `dark:bg-[#2C2119]` (card backgrounds)
- `dark:border-[#3D2F24]` (borders)
- `dark:bg-[#3D2F24]` (secondary backgrounds)
- `dark:hover:bg-[#2C2119]` (hover states)
- `dark:bg-[#1A1510]` (page backgrounds)

**Replace with your chosen variation** (see mapping tables below)

### Step 3: Test in Dark Mode

1. Toggle dark mode in your app
2. Check all pages and components
3. Verify amber/gold accents still look good
4. Test hover states and interactions

## Component-Level Color Replacement Tables

### Variation 1: Deep Navy Midnight
| Find | Replace With |
|------|--------------|
| `dark:bg-[#1A1510]` | `dark:bg-[#0F1419]` |
| `dark:bg-[#2C2119]` | `dark:bg-[#1A2330]` |
| `dark:bg-[#3D2F24]` | `dark:bg-[#2A3441]` |
| `dark:border-[#3D2F24]` | `dark:border-[#2F3A47]` |
| `dark:hover:bg-[#2C2119]` | `dark:hover:bg-[#2A3441]` |
| `dark:bg-[#2C2119]/85` | `dark:bg-[#1A2330]/85` |

### Variation 2: Pure Black Luxury
| Find | Replace With |
|------|--------------|
| `dark:bg-[#1A1510]` | `dark:bg-[#0D0D0D]` |
| `dark:bg-[#2C2119]` | `dark:bg-[#1A1A1A]` |
| `dark:bg-[#3D2F24]` | `dark:bg-[#262626]` |
| `dark:border-[#3D2F24]` | `dark:border-[#2E2E2E]` |
| `dark:hover:bg-[#2C2119]` | `dark:hover:bg-[#262626]` |
| `dark:bg-[#2C2119]/85` | `dark:bg-[#1A1A1A]/85` |

### Variation 3: Deep Plum Elegance
| Find | Replace With |
|------|--------------|
| `dark:bg-[#1A1510]` | `dark:bg-[#1A141D]` |
| `dark:bg-[#2C2119]` | `dark:bg-[#251F2B]` |
| `dark:bg-[#3D2F24]` | `dark:bg-[#342D3D]` |
| `dark:border-[#3D2F24]` | `dark:border-[#3A3244]` |
| `dark:hover:bg-[#2C2119]` | `dark:hover:bg-[#342D3D]` |
| `dark:bg-[#2C2119]/85` | `dark:bg-[#251F2B]/85` |

### Variation 4: Charcoal Slate Modern
| Find | Replace With |
|------|--------------|
| `dark:bg-[#1A1510]` | `dark:bg-[#121618]` |
| `dark:bg-[#2C2119]` | `dark:bg-[#1C2225]` |
| `dark:bg-[#3D2F24]` | `dark:bg-[#2B3236]` |
| `dark:border-[#3D2F24]` | `dark:border-[#31383D]` |
| `dark:hover:bg-[#2C2119]` | `dark:hover:bg-[#2B3236]` |
| `dark:bg-[#2C2119]/85` | `dark:bg-[#1C2225]/85` |

**Note:** Text colors like `dark:text-[#F8F5F1]` and `dark:text-[#C4BCB4]` work well with all variations and don't need to be changed.

---

## Color Reference Quick Guide

| Variation | Background | Card | Border | Secondary/Hover |
|-----------|-----------|------|--------|----------------|
| **1. Navy** | `#0F1419` | `#1A2330` | `#2F3A47` | `#2A3441` |
| **2. Pure Black** | `#0D0D0D` | `#1A1A1A` | `#2E2E2E` | `#262626` |
| **3. Plum** | `#1A141D` | `#251F2B` | `#3A3244` | `#342D3D` |
| **4. Slate** | `#121618` | `#1C2225` | `#31383D` | `#2B3236` |

All variations keep:
- **Amber Primary**: `#FFB84C` (38 92% 63%)
- **Orange Accent**: `#FF9400` (33 100% 56%)
- **Warm Text**: `#F8F5F1` (30 10% 97%)
- **Warm Muted Text**: `#D4CCC0` (30 8% 75%)

