import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Providers } from "@/components/providers";
import ToastContainer from "@/components/Toast";
import { Toaster } from "@/components/ui/toaster";

// Force Vercel rebuild - XP notifications URGENT - Dec 5 2025

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
  title: {
    default: "Easy Outfit App - AI-Powered Personal Stylist & Digital Wardrobe",
    template: "%s | Easy Outfit App",
  },
  description: "Your AI-powered personal stylist - Transform getting dressed into a daily ritual. Digitize your wardrobe, get personalized outfit suggestions, and discover your perfect style with AI technology.",
  keywords: [
    "Easy Outfit App",
    "AI stylist",
    "digital wardrobe",
    "personalized outfits",
    "outfit planner",
    "AI fashion",
    "virtual wardrobe",
    "style assistant",
    "outfit generator",
    "fashion AI",
    "wardrobe organizer",
    "personal stylist app",
    "outfit suggestions",
    "style recommendations",
  ],
  authors: [{ name: "Easy Outfit App" }],
  creator: "Easy Outfit App",
  publisher: "Easy Outfit App",
  alternates: {
    canonical: "/",
  },
  openGraph: {
    title: "Easy Outfit App • Effortless AI Outfit Planning",
    description:
      "Digitize your closet and get polished, personalized outfit combinations in seconds with the Easy Outfit App. AI-powered styling for your everyday wardrobe.",
    url: "https://www.easyoutfitapp.com",
    siteName: "Easy Outfit App",
    locale: "en_US",
    type: "website",
    images: [
      {
        url: "/logo-horizontal.png",
        width: 1200,
        height: 630,
        alt: "Easy Outfit App logo with curated wardrobe imagery",
        type: "image/png",
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
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/logo-horizontal.png",
  },
  manifest: "/manifest.json",
  other: {
    "og:image:width": "1200",
    "og:image:height": "630",
    "application-name": "Easy Outfit App",
    "apple-mobile-web-app-title": "Easy Outfit",
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "default",
    "mobile-web-app-capable": "yes",
    "theme-color": "#D4A574",
  },
  viewport: {
    width: "device-width",
    initialScale: 1,
    maximumScale: 5,
    userScalable: true,
  },
  verification: {
    // Add your verification codes here when available
    // google: "your-google-verification-code",
    // yandex: "your-yandex-verification-code",
    // bing: "your-bing-verification-code",
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
                
                // Store original methods
                const originalError = console.error.bind(console);
                const originalWarn = console.warn.bind(console);
                const originalLog = console.log.bind(console);
                
                // More aggressive filter that checks all possible message formats
                const shouldSuppress = function(args) {
                  try {
                    // Convert all arguments to string and check
                    const fullMessage = Array.prototype.slice.call(args).map(function(arg) {
                      if (typeof arg === 'string') return arg;
                      if (arg && typeof arg === 'object') {
                        try {
                          return JSON.stringify(arg);
                        } catch(e) {
                          return String(arg);
                        }
                      }
                      return String(arg);
                    }).join(' ');
                    
                    // Check for any variation of the COOP error
                    const lowerMessage = fullMessage.toLowerCase();
                    return lowerMessage.includes('cross-origin-opener-policy') || 
                           lowerMessage.includes('window.closed') ||
                           lowerMessage.includes('window.close') ||
                           lowerMessage.includes('coop') ||
                           fullMessage.includes('Cross-Origin-Opener-Policy') ||
                           fullMessage.includes('would block');
                  } catch(e) {
                    return false;
                  }
                };
                
                // Override console methods
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
                
                // Also filter console.log in case Firebase uses it
                console.log = function() {
                  if (!shouldSuppress(arguments)) {
                    originalLog.apply(console, arguments);
                  }
                };
                
                // Prevent the error from propagating
                window.addEventListener('error', function(e) {
                  if (e.message && (
                    e.message.includes('Cross-Origin-Opener-Policy') ||
                    e.message.includes('window.closed') ||
                    e.message.includes('window.close')
                  )) {
                    e.preventDefault();
                    e.stopPropagation();
                    return false;
                  }
                }, true);
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
