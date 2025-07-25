# Avatar Images

This directory contains avatar images used in the profile page, organized by gender, skin tone, and body type.

## Directory Structure

```
avatars/
├── female/
│   ├── light/
│   │   └── [body-type-specific avatars]
│   ├── medium-light/
│   │   └── [body-type-specific avatars]
│   ├── medium/
│   │   └── [body-type-specific avatars]
│   ├── medium-dark/
│   │   └── [body-type-specific avatars]
│   ├── dark/
│   │   └── [body-type-specific avatars]
│   └── deep/
│       └── [body-type-specific avatars]
└── male/
    ├── light/
    │   └── [body-type-specific avatars]
    ├── medium-light/
    │   └── [body-type-specific avatars]
    ├── medium/
    │   └── [body-type-specific avatars]
    ├── medium-dark/
    │   └── [body-type-specific avatars]
    ├── dark/
    │   └── [body-type-specific avatars]
    └── deep/
        └── [body-type-specific avatars]
```

## Image Requirements

1. Square aspect ratio (1:1)
2. PNG format with transparent background
3. At least 200x200 pixels in size
4. Named according to the body type convention
5. Available in all skin tone variations

### Skin Tone Variations
- `light` - Light skin tone (#FFE0BD)
- `medium-light` - Medium light skin tone (#E6C7A9)
- `medium` - Medium skin tone (#D4B483)
- `medium-dark` - Medium dark skin tone (#B38B6D)
- `dark` - Dark skin tone (#8B5A2B)
- `deep` - Deep skin tone (#5C4033)

### Female Body Types
- `hourglass.png` - Balanced bust and hips with a defined waist
- `pear.png` - Hips wider than shoulders and bust
- `apple.png` - Carries weight in the midsection; slim legs
- `rectangle.png` - Bust, waist, and hips are similar; less definition
- `inverted-triangle.png` - Shoulders or bust are broader than hips
- `petite.png` - Shorter stature, typically under 5'4"
- `tall.png` - Generally over 5'8", proportions vary
- `plus-curvy.png` - Fuller figure, curves emphasized at bust and/or hips
- `lean-column.png` - Slender, straight figure with minimal curves

### Male Body Types
- `rectangle.png` - Shoulders, waist, and hips are roughly the same width
- `triangle.png` - Wider waist and hips compared to shoulders
- `inverted-triangle.png` - Broad shoulders and narrow waist/hips
- `oval.png` - Weight concentrated around the midsection
- `trapezoid.png` - Broad shoulders, narrow waist, average hips
- `slim.png` - Slender build with narrow frame and low body fat
- `stocky.png` - Muscular build, thicker limbs, solid torso
- `tall.png` - Long limbs and torso, typically over 6'0"
- `short.png` - Under 5'6", with varying proportions

## Adding New Avatars

To add new avatars:

1. Create your avatar image following the requirements above
2. Name it according to the body type convention
3. Create versions for each skin tone variation
4. Place them in the appropriate gender and skin tone directories
5. Update the `FEMALE_AVATARS` or `MALE_AVATARS` array in `frontend/src/components/AvatarSelector.tsx` if you add new body types

## Image Guidelines

- Use neutral poses that work well in a circular frame
- Ensure the avatar is centered in the image
- Keep file sizes under 100KB for optimal performance
- Use consistent styling across all avatars
- Consider accessibility by ensuring good contrast and clear silhouettes
- Maintain consistent proportions across all body types
- Use appropriate clothing that doesn't distract from the body type
- Consider cultural diversity in avatar representation
- Ensure consistent lighting and shading across all skin tone variations
- Use appropriate color palettes for each skin tone
- Maintain consistent features and proportions across all skin tone variations 