import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://www.easyoutfitapp.com"),
  title: "Easy Outfit App - AI-Powered Digital Wardrobe",
  description: "Digitize your wardrobe and get personalized outfit suggestions using AI",
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