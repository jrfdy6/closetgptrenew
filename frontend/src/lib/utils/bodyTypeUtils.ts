import { Gender, BodyType } from '@/lib/store/onboardingStore';

/**
 * Get body types based on gender selection
 * Non-binary users get access to all body types from both men's and women's categories
 */
export const getBodyTypes = (gender: Gender): BodyType[] => {
  if (gender === 'male') {
    return ['Athletic', 'Ectomorph', 'Mesomorph', 'Endomorph', 'Rectangular', 'Inverted Triangle'];
  } else if (gender === 'female') {
    return ['Athletic', 'Curvy', 'Rectangular', 'Hourglass', 'Pear', 'Apple', 'Inverted Triangle'];
  } else {
    // For non-binary or prefer-not-to-say, show all body types
    return [
      'Athletic', 'Curvy', 'Rectangular', 'Hourglass', 'Pear', 'Apple', 
      'Ectomorph', 'Mesomorph', 'Endomorph', 'Inverted Triangle'
    ];
  }
};

/**
 * Get body type description
 */
export const getBodyTypeDescription = (bodyType: BodyType): string => {
  const descriptions: Record<BodyType, string> = {
    'Athletic': 'Muscular and toned physique',
    'Curvy': 'Fuller figure with defined curves',
    'Rectangular': 'Straight, balanced proportions',
    'Hourglass': 'Curved with defined waist',
    'Pear': 'Fuller hips and thighs',
    'Apple': 'Fuller midsection',
    'Ectomorph': 'Naturally thin and lean',
    'Mesomorph': 'Naturally muscular build',
    'Endomorph': 'Naturally fuller build',
    'Inverted Triangle': 'Broader shoulders and chest',
  };
  
  return descriptions[bodyType] || 'Body type description';
}; 