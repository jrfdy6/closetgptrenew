import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dashboard - My Style & Outfits',
  description: 'View your personalized dashboard with outfit suggestions, wardrobe insights, style stats, and daily outfit recommendations powered by AI.',
  openGraph: {
    title: 'Dashboard - Easy Outfit App',
    description: 'Your personalized style dashboard with AI-powered outfit suggestions and wardrobe insights.',
    url: 'https://www.easyoutfitapp.com/dashboard',
  },
  twitter: {
    card: 'summary',
    title: 'Dashboard - Easy Outfit App',
    description: 'Your personalized style dashboard with AI-powered outfit suggestions.',
  },
  alternates: {
    canonical: '/dashboard',
  },
  robots: {
    index: false, // Dashboard is user-specific, don't index
    follow: false,
  },
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

