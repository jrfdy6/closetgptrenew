import { NextResponse } from 'next/server';
import { NextRequest } from 'next/server';
import { getAuth } from '@clerk/nextjs/server';
import { adminDb } from '@/lib/firebase-admin';
import { Firestore } from 'firebase-admin/firestore';
import { 
  PhotoAnalysis, 
  UserPhotos, 
  OutfitAnalysis,
  GarmentStyle,
  OutfitFormality,
  OutfitOccasion,
  OutfitSeason
} from '@/types/photo-analysis';
import { 
  StyleProfile, 
  ColorPreferences, 
  StylePreferences, 
  FitPreferences, 
  MaterialPreferences 
} from '@/types/style-profile';

export async function POST(req: NextRequest) {
  try {
    // Check if Firebase Admin is initialized
    if (!adminDb) {
      return new NextResponse(
        JSON.stringify({ error: 'Firebase Admin not initialized' }),
        { status: 500, headers: { 'Content-Type': 'application/json' } }
      );
    }

    const { userId } = getAuth(req);
    if (!userId) {
      return new NextResponse('Unauthorized', { status: 401 });
    }

    const userRef = (adminDb as Firestore).collection('users').doc(userId);
    const userDoc = await userRef.get();
    const userData = userDoc.data() as { photos?: UserPhotos; styleProfile?: StyleProfile };

    if (!userData?.photos) {
      return new NextResponse('No photos found', { status: 404 });
    }

    const { photos } = userData;
    const styleProfile: StyleProfile = userData.styleProfile || {
      bodyType: 'rectangle',
      measurements: {
        height: 0,
        shoulderWidth: 0,
        waistWidth: 0,
        hipWidth: 0,
        inseam: 0,
      },
      skinTone: {
        undertone: 'neutral',
        shade: '#F5D0A9',
        season: 'summer',
        contrast: 'medium',
      },
      colorPreferences: {
        primary: [],
        secondary: [],
        accent: [],
        avoid: [],
        seasonal: {
          spring: [],
          summer: [],
          fall: [],
          winter: [],
        },
      },
      stylePreferences: {
        preferredStyles: [],
        preferredFormality: [],
        preferredOccasions: [],
        preferredSeasons: [],
        stylePersonality: {
          classic: 0.5,
          modern: 0.5,
          creative: 0.5,
          minimal: 0.5,
          bold: 0.5,
        },
        styleGoals: [],
      },
      fitPreferences: {
        preferredFits: {
          tops: 'regular',
          bottoms: 'regular',
          dresses: 'regular',
        },
        comfortLevel: {
          tight: 0.5,
          loose: 0.5,
          structured: 0.5,
          relaxed: 0.5,
        },
      },
      materialPreferences: {
        preferred: [],
        avoid: [],
        seasonal: {
          spring: [],
          summer: [],
          fall: [],
          winter: [],
        },
      },
      styleHistory: {
        recentOutfits: [],
        favoriteOutfits: [],
        styleEvolution: [],
      },
      styleInsights: {
        strengths: [],
        areasForImprovement: [],
        recommendations: [],
      },
      lastUpdated: new Date().toISOString(),
    };

    // Update body type and measurements
    if (photos.analyses.fullBody) {
      const { bodyMeasurements } = photos.analyses.fullBody;
      styleProfile.bodyType = bodyMeasurements.bodyType;
      styleProfile.measurements = {
        ...styleProfile.measurements,
        height: bodyMeasurements.height,
        shoulderWidth: bodyMeasurements.shoulderWidth,
        waistWidth: bodyMeasurements.waistWidth,
        hipWidth: bodyMeasurements.hipWidth,
        inseam: bodyMeasurements.inseam,
      };
    }

    // Update color preferences based on outfit analyses
    if (photos.analyses.outfits.length > 0) {
      const colorFrequency: Record<string, number> = {};
      const styleFrequency: Record<string, number> = {};
      const formalityFrequency: Record<string, number> = {};
      const occasionFrequency: Record<string, number> = {};
      const seasonFrequency: Record<string, number> = {};
      const materialFrequency: Record<string, number> = {};

      photos.analyses.outfits.forEach(outfit => {
        // Count color frequencies
        outfit.colorPalette.forEach(color => {
          colorFrequency[color] = (colorFrequency[color] || 0) + 1;
        });

        // Count style frequencies
        outfit.overallStyle.forEach(style => {
          styleFrequency[style] = (styleFrequency[style] || 0) + 1;
        });

        // Count formality frequencies
        formalityFrequency[outfit.formality] = (formalityFrequency[outfit.formality] || 0) + 1;

        // Count occasion frequencies
        occasionFrequency[outfit.occasion] = (occasionFrequency[outfit.occasion] || 0) + 1;

        // Count season frequencies
        seasonFrequency[outfit.season] = (seasonFrequency[outfit.season] || 0) + 1;

        // Count material frequencies
        outfit.garments.forEach(garment => {
          materialFrequency[garment.material] = (materialFrequency[garment.material] || 0) + 1;
        });
      });

      // Update color preferences
      styleProfile.colorPreferences = {
        primary: Object.entries(colorFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([color]) => color),
        secondary: Object.entries(colorFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(5, 10)
          .map(([color]) => color),
        accent: Object.entries(colorFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(10, 15)
          .map(([color]) => color),
        avoid: [], // TODO: Implement color avoidance logic
        seasonal: {
          spring: [], // TODO: Implement seasonal color preferences
          summer: [],
          fall: [],
          winter: [],
        },
      };

      // Update style preferences
      styleProfile.stylePreferences = {
        preferredStyles: Object.entries(styleFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([style]) => style as GarmentStyle),
        preferredFormality: Object.entries(formalityFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([formality]) => formality as OutfitFormality),
        preferredOccasions: Object.entries(occasionFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([occasion]) => occasion as OutfitOccasion),
        preferredSeasons: Object.entries(seasonFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 3)
          .map(([season]) => season as OutfitSeason),
        stylePersonality: {
          classic: calculateStylePersonalityScore(styleFrequency, 'classic'),
          modern: calculateStylePersonalityScore(styleFrequency, 'modern'),
          creative: calculateStylePersonalityScore(styleFrequency, 'creative'),
          minimal: calculateStylePersonalityScore(styleFrequency, 'minimalist'),
          bold: calculateStylePersonalityScore(styleFrequency, 'bold'),
        },
        styleGoals: [], // TODO: Implement style goals based on user preferences
      };

      // Update material preferences
      styleProfile.materialPreferences = {
        preferred: Object.entries(materialFrequency)
          .sort(([, a], [, b]) => b - a)
          .slice(0, 5)
          .map(([material]) => material),
        avoid: [], // TODO: Implement material avoidance logic
        seasonal: {
          spring: [], // TODO: Implement seasonal material preferences
          summer: [],
          fall: [],
          winter: [],
        },
      };
    }

    // Update skin tone information
    if (photos.analyses.fullBody?.colorAnalysis.skinTone) {
      styleProfile.skinTone = {
        ...photos.analyses.fullBody.colorAnalysis.skinTone,
        season: determineColorSeason(photos.analyses.fullBody.colorAnalysis.skinTone),
        contrast: determineContrastLevel(photos.analyses.fullBody.colorAnalysis.skinTone),
      };
    }

    // Update style history
    styleProfile.styleHistory = {
      recentOutfits: photos.outfitPhotos.slice(-5), // Last 5 outfit photos
      favoriteOutfits: [], // TODO: Implement favorite outfits logic
      styleEvolution: [
        {
          date: new Date().toISOString(),
          changes: ['Updated style profile based on photo analysis'],
        },
      ],
    };

    // Generate style insights
    styleProfile.styleInsights = generateStyleInsights(styleProfile);

    // Add last updated timestamp
    styleProfile.lastUpdated = new Date().toISOString();

    // Save updated style profile
    await userRef.set({ styleProfile }, { merge: true });

    return NextResponse.json({ styleProfile });
  } catch (error) {
    console.error('Error updating style profile:', error);
    return new NextResponse(
      JSON.stringify({
        error: 'Failed to update style profile',
        details: error instanceof Error ? error.message : 'Unknown error',
      }),
      {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  }
}

// Helper function to calculate style personality score
const calculateStylePersonalityScore = (
  styleFrequency: Record<string, number>,
  style: string
): number => {
  const totalStyles = Object.values(styleFrequency).reduce((sum, count) => sum + count, 0);
  const styleCount = styleFrequency[style] || 0;
  return totalStyles > 0 ? styleCount / totalStyles : 0.5;
};

// Helper function to determine color season
const determineColorSeason = (skinTone: { undertone: string; shade: string }): 'spring' | 'summer' | 'autumn' | 'winter' => {
  // TODO: Implement proper color season analysis
  return 'summer';
};

// Helper function to determine contrast level
const determineContrastLevel = (skinTone: { undertone: string; shade: string }): 'high' | 'medium' | 'low' => {
  // TODO: Implement proper contrast analysis
  return 'medium';
};

// Helper function to generate style insights
const generateStyleInsights = (styleProfile: StyleProfile): StyleProfile['styleInsights'] => {
  const insights: StyleProfile['styleInsights'] = {
    strengths: [],
    areasForImprovement: [],
    recommendations: [],
  };

  // Analyze color preferences
  if (styleProfile.colorPreferences.primary.length > 0) {
    insights.strengths.push('Clear color preferences');
  } else {
    insights.areasForImprovement.push('Diversify color choices');
  }

  // Analyze style preferences
  if (styleProfile.stylePreferences.preferredStyles.length > 0) {
    insights.strengths.push('Defined style direction');
  } else {
    insights.areasForImprovement.push('Explore different style options');
  }

  // Generate recommendations based on analysis
  if (insights.areasForImprovement.includes('Diversify color choices')) {
    insights.recommendations.push('Try incorporating more colors from your seasonal palette');
  }
  if (insights.areasForImprovement.includes('Explore different style options')) {
    insights.recommendations.push('Experiment with different style combinations');
  }

  return insights;
}; 