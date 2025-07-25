# Outfit Image Generation Scripts

This directory contains scripts to generate outfit images using OpenAI's DALL-E 3 API and update the application data.

## Prerequisites

1. **OpenAI API Key**: You need a valid OpenAI API key with access to DALL-E 3
2. **Node.js**: Make sure you have Node.js installed
3. **Dependencies**: Run `npm install` to install required packages

## Setup

1. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```
   
   Or add it to your `.env` file:
   ```
   OPENAI_API_KEY=your-openai-api-key-here
   ```

## Scripts

### 1. Generate All Prompts
```bash
node scripts/generate-all-prompts.js
```
- Generates 80 detailed prompts for all outfits
- Saves prompts in `prompts/` directory
- Each prompt is optimized for DALL-E 3 image generation

### 2. Generate Images with OpenAI (Comprehensive)
```bash
node scripts/generate-and-update-outfits.js
```
- Generates all outfit images using DALL-E 3
- Saves images as PNG files in `public/images/outfit-quiz/`
- Updates outfit data to use PNG extensions
- Includes rate limiting and error handling

### 3. Generate Images Only
```bash
node scripts/generate-outfit-images-with-openai.js
```
- Generates images only (doesn't update data)
- Useful for testing or partial generation

### 4. Update Outfit Data Only
```bash
node scripts/update-outfit-image-urls.js
```
- Updates outfit data to use PNG extensions
- Useful if you already have images

## File Structure

```
frontend/
├── scripts/
│   ├── generate-all-prompts.js
│   ├── generate-and-update-outfits.js
│   ├── generate-outfit-images-with-openai.js
│   ├── update-outfit-image-urls.js
│   └── README-outfit-generation.md
├── prompts/
│   ├── F-CB1-prompt.txt
│   ├── F-CB2-prompt.txt
│   └── ... (80 total prompts)
└── public/
    └── images/
        └── outfit-quiz/
            ├── F-CB1.png
            ├── F-CB2.png
            └── ... (generated images)
```

## Outfit Categories

- **F-CB1 to F-CB10**: Women's Cottagecore/Boho (10 outfits)
- **M-CB1 to M-CB10**: Men's Cottagecore/Boho (10 outfits)
- **F-OM1 to F-OM10**: Women's Old Money/Preppy (10 outfits)
- **M-OM1 to M-OM10**: Men's Old Money/Preppy (10 outfits)
- **F-ST1 to F-ST10**: Women's Streetwear/Edgy (10 outfits)
- **M-ST1 to M-ST10**: Men's Streetwear/Edgy (10 outfits)
- **F-MIN1 to F-MIN10**: Women's Minimalist (10 outfits)
- **M-MIN1 to M-MIN10**: Men's Minimalist (10 outfits)

## Cost Estimation

- **DALL-E 3**: ~$0.04 per image
- **80 images**: ~$3.20 total
- **Processing time**: ~80 minutes (with 1-second delays)

## Troubleshooting

### API Key Issues
- Make sure your OpenAI API key is valid and has DALL-E 3 access
- Check that the environment variable is set correctly

### Rate Limiting
- The script includes 1-second delays between requests
- If you hit rate limits, increase the delay in the script

### Missing Images
- Check the console output for any failed generations
- Failed images will be logged with error messages
- You can re-run the script to generate missing images

### File Permissions
- Make sure the script has write permissions to the output directories
- Create directories manually if needed

## Testing

After generation, test the images by:
1. Running the development server: `npm run dev`
2. Navigating to the onboarding flow
3. Going through the style quiz to see the new images

## Notes

- Images are generated at 1024x1024 resolution
- All images use pure white backgrounds for consistency
- The prompts are optimized for e-commerce product photography style
- Generated images are automatically saved with the correct outfit IDs 