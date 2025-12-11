import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign Up - Easy Outfit App',
  description: 'Create your free Easy Outfit App account to start digitizing your wardrobe and getting AI-powered outfit suggestions. Free to start, no credit card required.',
  openGraph: {
    title: 'Sign Up - Easy Outfit App',
    description: 'Create your free account to start getting AI-powered outfit suggestions. Free to start, no credit card required.',
    url: 'https://www.easyoutfitapp.com/signup',
  },
  twitter: {
    card: 'summary',
    title: 'Sign Up - Easy Outfit App',
    description: 'Create your free account to start getting AI-powered outfit suggestions.',
  },
  alternates: {
    canonical: '/signup',
  },
};

export default function SignUpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

