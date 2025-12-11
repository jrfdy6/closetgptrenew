import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'My Wardrobe - Digital Closet Management',
  description: 'Manage your digital wardrobe with AI-powered organization. Upload, organize, and discover your clothing items with smart categorization and style insights.',
  keywords: [
    'digital wardrobe',
    'closet organizer',
    'wardrobe management',
    'clothing organizer',
    'virtual closet',
    'wardrobe app',
  ],
  openGraph: {
    title: 'My Wardrobe - Easy Outfit App',
    description: 'Manage your digital wardrobe with AI-powered organization and style insights.',
    url: 'https://www.easyoutfitapp.com/wardrobe',
  },
  twitter: {
    card: 'summary',
    title: 'My Wardrobe - Easy Outfit App',
    description: 'Manage your digital wardrobe with AI-powered organization.',
  },
  alternates: {
    canonical: '/wardrobe',
  },
  robots: {
    index: false, // User-specific content
    follow: false,
  },
};

export default function WardrobeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

