# Audio Files for Easy Outfit App

## Overview
Audio feedback is **silent by default** (Silent Luxury philosophy). Users must opt-in via Settings.

## Required Sound Files

### 1. `chime.mp3` - Outfit Save Confirmation
**Trigger:** When user taps ❤️ to save outfit  
**Duration:** 150ms  
**Style:** Soft, elegant, minimal (like a soft bell)  
**Frequency:** 300-600Hz mid-range  
**Volume:** 40% of max device volume  
**Reference:** iOS "Note" sound or similar gentle chime

### 2. `celebration.mp3` - Milestone Achievement
**Trigger:** Streaks, first outfit, profile complete  
**Duration:** 1000ms (1 second)  
**Style:** Rising tone with soft sparkle ending  
**Frequency:** Uplifting but not jarring  
**Volume:** 60% of max device volume  
**Reference:** Duolingo success sound (but softer/more sophisticated)

## Production Notes
- File format: MP3 or AAC (compressed)
- File size: <10kb per sound
- Fade in/out: No hard cuts
- Preload: On app launch via Web Audio API
- Fallback: Silently fail if audio can't play

## Implementation Status
✅ Audio system built in `/src/lib/utils/interactions.ts`  
✅ Settings toggle in `AccessibilitySettings.tsx`  
⏳ **TODO:** Add actual audio files (currently using placeholders)

## How to Add Sounds
1. Create/purchase the two sound files
2. Place them in this directory:
   - `frontend/public/sounds/chime.mp3`
   - `frontend/public/sounds/celebration.mp3`
3. Test in browser with sound enabled in settings
4. Verify files are <10kb each

## User Experience
- **Default:** Silent (no embarrassment in public)
- **Opt-in:** User enables in Profile → Settings → Sound Effects
- **Never required:** Visual + haptic feedback is complete without audio
- **Multisensory:** Enhances dopamine loop when enabled
