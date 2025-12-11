import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Style Persona - Discover Your Fashion Identity',
  description: 'Discover your unique style persona with our AI-powered style quiz. Get personalized style insights, fashion recommendations, and outfit inspiration based on your preferences.',
  keywords: [
    'style quiz',
    'fashion personality',
    'style persona',
    'fashion identity',
    'style assessment',
    'personal style',
    'fashion quiz',
  ],
  openGraph: {
    title: 'Style Persona - Easy Outfit App',
    description: 'Discover your unique style persona with our AI-powered style quiz and get personalized fashion recommendations.',
    url: 'https://www.easyoutfitapp.com/style-persona',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Style Persona - Easy Outfit App',
    description: 'Discover your unique style persona with our AI-powered style quiz.',
  },
  alternates: {
    canonical: '/style-persona',
  },
};

export default function StylePersonaLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

