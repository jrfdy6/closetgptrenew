import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Easy Outfit App - Stop Wasting Time Wondering What to Wear',
  description: 'Make the most of your existing wardrobe with unbiased, AI-powered styling advice. No shopping push, no ads—just honest, personalized outfit suggestions that help you look amazing every day.',
  keywords: [
    'AI stylist',
    'digital wardrobe',
    'outfit suggestions',
    'personal stylist app',
    'wardrobe organizer',
    'AI fashion',
    'outfit generator',
    'style assistant',
    'unbiased styling',
    'wardrobe management',
  ],
  openGraph: {
    title: 'Easy Outfit App - Stop Wasting Time Wondering What to Wear',
    description: 'Make the most of your existing wardrobe with unbiased, AI-powered styling. No shopping push, no ads—just honest outfit suggestions.',
    url: 'https://www.easyoutfitapp.com/landing',
    siteName: 'Easy Outfit App',
    locale: 'en_US',
    type: 'website',
    images: [
      {
        url: '/logo-horizontal.png',
        width: 1200,
        height: 630,
        alt: 'Easy Outfit App - AI-Powered Personal Stylist',
        type: 'image/png',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Easy Outfit App - Stop Wasting Time Wondering What to Wear',
    description: 'Make the most of your existing wardrobe with unbiased, AI-powered styling advice.',
    site: '@easyoutfitapp',
    creator: '@easyoutfitapp',
    images: ['/logo-horizontal.png'],
  },
  alternates: {
    canonical: '/landing',
  },
};

export default function LandingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

