import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sign In - Easy Outfit App',
  description: 'Sign in to your Easy Outfit App account to access your digital wardrobe, personalized outfit suggestions, and AI-powered style recommendations.',
  robots: {
    index: false, // Login pages typically shouldn't be indexed
    follow: false,
  },
  alternates: {
    canonical: '/signin',
  },
};

export default function SignInLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

