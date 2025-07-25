import { useState } from 'react';
import { useOnboardingStore } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Sparkles, Briefcase, Skateboard, Leaf, Dumbbell, Users } from 'lucide-react';
import type { StepProps } from '../StepWizard';

interface StyleCluster {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  styles: string[];
  traits: string[];
  imageUrl: string;
}

const styleClusters: StyleCluster[] = [
  {
    id: 'artistic-expressive',
    name: 'Artistic & Expressive',
    icon: <Sparkles className="w-6 h-6" />,
    description: 'Creative, bold, asymmetrical, or conceptual',
    styles: ['Artsy', 'Avant-Garde', 'Boho', 'Romantic'],
    traits: ['Flowy, experimental silhouettes', 'Layered textures', 'Nontraditional color pairings', 'Emotional mood'],
    imageUrl: '/images/style-clusters/artistic-expressive.jpg'
  },
  {
    id: 'polished-elevated',
    name: 'Polished & Elevated',
    icon: <Briefcase className="w-6 h-6" />,
    description: 'Refined lines, clean fits, structured layers',
    styles: ['Old Money', 'Classic', 'Business Casual', 'Minimalist'],
    traits: ['Tailoring', 'Quality basics', 'Neutral palettes', 'Muted elegance', 'Focus on materials and fit'],
    imageUrl: '/images/style-clusters/polished-elevated.jpg'
  },
  {
    id: 'street-inspired',
    name: 'Street-Inspired & Subcultural',
    icon: <Skateboard className="w-6 h-6" />,
    description: 'Edgy, urban, layered, cultural signals',
    styles: ['Streetwear', 'Grunge', 'Y2K', 'Edgy'],
    traits: ['Sneakers', 'Baggy fits', 'Graphic elements', 'Layering freedom', 'Youth-oriented styling'],
    imageUrl: '/images/style-clusters/street-inspired.jpg'
  },
  {
    id: 'natural-relaxed',
    name: 'Natural & Relaxed',
    icon: <Leaf className="w-6 h-6" />,
    description: 'Earthy, laid-back, breezy, soft',
    styles: ['Cottagecore', 'Coastal Chic', 'Casual Cool'],
    traits: ['Soft fabrics', 'Neutral/natural palettes', 'Summer vibes', 'Simplicity with personality'],
    imageUrl: '/images/style-clusters/natural-relaxed.jpg'
  },
  {
    id: 'active-practical',
    name: 'Active & Practical',
    icon: <Dumbbell className="w-6 h-6" />,
    description: 'Sporty, performance-oriented, body-conscious',
    styles: ['Athleisure', 'Techwear'],
    traits: ['Functional silhouettes', 'Sleek lines', 'Synthetic fabrics', 'Zip pockets', 'Dynamic layering'],
    imageUrl: '/images/style-clusters/active-practical.jpg'
  },
  {
    id: 'identity-driven',
    name: 'Identity-Driven & Modern',
    icon: <Users className="w-6 h-6" />,
    description: 'Blending structure with fluidity, often minimal or rule-bending',
    styles: ['Androgynous', 'Dark Academia', 'Preppy'],
    traits: ['Gender-fluid fits', 'Vintage or intellectual cues', 'Blazers', 'Oxfords', 'Moody or scholarly palettes'],
    imageUrl: '/images/style-clusters/identity-driven.jpg'
  }
];

export function StepVisualStyleQuiz({ onNext }: StepProps) {
  const { setStylePreferences } = useOnboardingStore();
  const [selectedClusters, setSelectedClusters] = useState<string[]>([]);

  const handleClusterToggle = (clusterId: string) => {
    setSelectedClusters(prev => 
      prev.includes(clusterId)
        ? prev.filter(id => id !== clusterId)
        : [...prev, clusterId]
    );
  };

  const handleContinue = () => {
    if (selectedClusters.length === 0) {
      return; // Don't proceed if no clusters selected
    }

    // Convert selected clusters to style preferences for foundation
    const selectedStyles = selectedClusters.flatMap(clusterId => {
      const cluster = styleClusters.find(c => c.id === clusterId);
      return cluster ? cluster.styles : [];
    });

    // Filter to ensure styles match the StylePreference type
    const validStyles = selectedStyles.filter(style => [
      'Dark Academia', 'Old Money', 'Streetwear', 'Y2K', 'Minimalist', 
      'Boho', 'Preppy', 'Grunge', 'Classic', 'Techwear', 'Androgynous', 
      'Coastal Chic', 'Business Casual', 'Avant-Garde', 'Cottagecore', 
      'Edgy', 'Athleisure', 'Casual Cool', 'Romantic', 'Artsy'
    ].includes(style)) as any[];

    // Save the foundation style preferences
    setStylePreferences({ stylePreferences: validStyles });
    onNext();
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-4">
        <h2 className="text-3xl font-bold">Discover Your Style Foundation</h2>
        <p className="text-muted-foreground text-lg">
          Start by selecting the style clusters that resonate with you. This gives us a foundation to build upon with more specific outfit preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {styleClusters.map((cluster) => (
          <Card
            key={cluster.id}
            className={`p-4 cursor-pointer transition-all hover:shadow-lg border-2 ${
              selectedClusters.includes(cluster.id)
                ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                : 'border-border hover:border-primary/50'
            }`}
            onClick={() => handleClusterToggle(cluster.id)}
          >
            <div className="space-y-4">
              {/* Image */}
              <div className="relative aspect-[4/3] bg-gray-100 rounded-lg overflow-hidden">
                <img
                  src={cluster.imageUrl}
                  alt={cluster.name}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    // Fallback to a colored background if image fails to load
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    target.parentElement!.style.backgroundColor = getClusterColor(cluster.id);
                  }}
                />
                {selectedClusters.includes(cluster.id) && (
                  <div className="absolute top-2 right-2">
                    <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}
              </div>

              {/* Content */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="text-primary">
                    {cluster.icon}
                  </div>
                  <h3 className="font-semibold text-lg">{cluster.name}</h3>
                </div>
                
                <p className="text-sm text-muted-foreground">
                  {cluster.description}
                </p>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Includes styles:</p>
                  <div className="flex flex-wrap gap-1">
                    {cluster.styles.map((style) => (
                      <Badge key={style} variant="secondary" className="text-xs">
                        {style}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">Key traits:</p>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    {cluster.traits.slice(0, 3).map((trait, index) => (
                      <li key={index} className="flex items-center">
                        <span className="w-1 h-1 bg-muted-foreground rounded-full mr-2"></span>
                        {trait}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="text-center space-y-4">
        <div className="flex justify-center">
          <p className="text-sm text-muted-foreground">
            Selected: {selectedClusters.length} cluster{selectedClusters.length !== 1 ? 's' : ''}
          </p>
        </div>
        
        <Button
          onClick={handleContinue}
          disabled={selectedClusters.length === 0}
          className="px-8"
        >
          Continue to Outfit Quiz
        </Button>
      </div>
    </div>
  );
}

// Helper function to get fallback colors for clusters
function getClusterColor(clusterId: string): string {
  const colors = {
    'artistic-expressive': '#fce7f3', // Pink
    'polished-elevated': '#f3f4f6',   // Gray
    'street-inspired': '#1f2937',     // Dark gray
    'natural-relaxed': '#f0fdf4',     // Green
    'active-practical': '#dbeafe',    // Blue
    'identity-driven': '#fef3c7'      // Yellow
  };
  return colors[clusterId as keyof typeof colors] || '#f3f4f6';
} 