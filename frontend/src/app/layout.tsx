import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Providers } from "@/components/providers";
import ToastContainer from "@/components/Toast";
import { Toaster } from "@/components/ui/toaster";

// Body/UI font - Clean, neutral, readable
const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

// Display font - Fashion-forward, editorial moments
const spaceGrotesk = Space_Grotesk({ 
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://www.easyoutfitapp.com"),
  title: "Easy Outfit App",
  description: "Your AI-powered personal stylist - Transform getting dressed into a daily ritual",
  keywords: [
    "Easy Outfit App",
    "AI stylist",
    "digital wardrobe",
    "personalized outfits",
    "outfit planner",
  ],
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Easy Outfit App • Effortless AI Outfit Planning",
    description:
      "Digitize your closet and get polished, personalized outfit combinations in seconds with the Easy Outfit App.",
    url: "/",
    siteName: "Easy Outfit App",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/logo-horizontal.png",
        width: 1200,
        height: 630,
        alt: "Easy Outfit App logo with curated wardrobe imagery",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Easy Outfit App • Effortless AI Outfit Planning",
    description:
      "Let the Easy Outfit App bring your wardrobe to life with tailored looks, styling tips, and daily outfit inspiration.",
    site: "@easyoutfitapp",
    creator: "@easyoutfitapp",
    images: ["/logo-horizontal.png"],
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/logo-horizontal.png",
  },
  other: {
    "og:image:width": "1200",
    "og:image:height": "630",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${inter.variable} ${spaceGrotesk.variable} ${inter.className}`}>
        <Script
          id="suppress-firebase-errors"
          strategy="beforeInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                if (typeof window === 'undefined') return;
                const originalError = console.error;
                const originalWarn = console.warn;
                
                const shouldSuppress = function(args) {
                  try {
                    const message = Array.from(args).map(function(arg) {
                      return typeof arg === 'string' ? arg : 
                             typeof arg === 'object' && arg !== null ? String(arg) : 
                             String(arg);
                    }).join(' ');
                    return message.includes('Cross-Origin-Opener-Policy') || 
                           message.includes('window.closed call') ||
                           message.includes('COOP');
                  } catch(e) {
                    return false;
                  }
                };
                
                console.error = function() {
                  if (!shouldSuppress(arguments)) {
                    originalError.apply(console, arguments);
                  }
                };
                
                console.warn = function() {
                  if (!shouldSuppress(arguments)) {
                    originalWarn.apply(console, arguments);
                  }
                };
              })();
            `,
          }}
        />
        {/* Skip to content link for keyboard users */}
        <a href="#main-content" className="skip-to-content">
          Skip to main content
        </a>
        
        <Providers>
          <div id="main-content">
            {children}
          </div>
          <ToastContainer />
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
