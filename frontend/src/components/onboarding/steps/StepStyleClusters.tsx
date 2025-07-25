import { useState } from 'react';
import { useOnboardingStore, type StylePreference } from '@/lib/store/onboardingStore';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Check, Sparkles, Briefcase, Keyboard, Leaf, Dumbbell, Users } from 'lucide-react';
import type { StepProps } from '../StepWizard';
import { useToast } from '@/components/ui/use-toast';

interface StyleCluster {
  id: string;
  name: string;
  icon: React.ReactNode;
  description: string;
  styles: StylePreference[];
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
    icon: <Keyboard className="w-6 h-6" />,
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

export function StepStyleClusters({ onNext, onPrevious }: StepProps) {
  const { stylePreferences, setStylePreferences } = useOnboardingStore();
  const { toast } = useToast();
  const [selectedClusters, setSelectedClusters] = useState<string[]>([]);

  const handleClusterToggle = (clusterId: string) => {
    setSelectedClusters(prev => 
      prev.includes(clusterId)
        ? prev.filter(id => id !== clusterId)
        : [...prev, clusterId]
    );
  };

  const handleNext = () => {
    if (selectedClusters.length === 0) {
      toast({
        title: "Please select at least one style cluster",
        description: "This helps us understand your style foundation.",
        variant: "destructive",
      });
      return;
    }

    // Convert selected clusters to style preferences for foundation
    const selectedStyles = selectedClusters.flatMap(clusterId => {
      const cluster = styleClusters.find(c => c.id === clusterId);
      return cluster ? cluster.styles : [];
    });

    // Remove duplicates
    const uniqueStyles = Array.from(new Set(selectedStyles));

    // Save the foundation style preferences
    setStylePreferences({ stylePreferences: uniqueStyles });
    onNext();
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Discover Your Style Foundation
        </h2>
        <p className="text-lg text-gray-600">
          Start by selecting the style clusters that resonate with you. This gives us a foundation to build upon with more specific outfit preferences.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {styleClusters.map((cluster) => (
          <Card
            key={cluster.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedClusters.includes(cluster.id) ? 'ring-2 ring-purple-500 bg-purple-50' : ''
            }`}
            onClick={() => handleClusterToggle(cluster.id)}
          >
            <CardContent className="p-6">
              <div className="space-y-4">
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
                
                <div>
                  <h3 className="text-xl font-semibold mb-2">{cluster.name}</h3>
                  <p className="text-gray-600 mb-3">{cluster.description}</p>
                  
                  <div className="space-y-2">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Includes styles:</h4>
                      <p className="text-sm text-gray-600">{cluster.styles.join(', ')}</p>
                    </div>
                    
                    <div>
                      <h4 className="text-sm font-medium text-gray-700">Key traits:</h4>
                      <ul className="text-sm text-gray-600">
                        {cluster.traits.slice(0, 3).map((trait, index) => (
                          <li key={index}>• {trait}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="text-center mt-6">
        <p className="text-sm text-gray-500">
          Selected: {selectedClusters.length} cluster{selectedClusters.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="flex justify-between mt-8">
        <Button variant="outline" onClick={onPrevious}>
          Previous
        </Button>
        <Button onClick={handleNext} disabled={selectedClusters.length === 0}>
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