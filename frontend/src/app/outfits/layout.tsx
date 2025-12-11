import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Outfits - AI-Generated Outfit Suggestions',
  description: 'Browse and manage your AI-generated outfit combinations. Get personalized outfit suggestions based on your wardrobe, style preferences, and weather.',
  keywords: [
    'outfit suggestions',
    'AI outfits',
    'outfit combinations',
    'style recommendations',
    'wardrobe outfits',
    'personalized outfits',
  ],
  openGraph: {
    title: 'My Outfits - Easy Outfit App',
    description: 'Browse AI-generated outfit combinations tailored to your style and wardrobe.',
    url: 'https://www.easyoutfitapp.com/outfits',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'My Outfits - Easy Outfit App',
    description: 'Browse AI-generated outfit combinations tailored to your style.',
  },
  alternates: {
    canonical: '/outfits',
  },
  robots: {
    index: false, // User-specific content
    follow: false,
  },
};

export default function OutfitsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

