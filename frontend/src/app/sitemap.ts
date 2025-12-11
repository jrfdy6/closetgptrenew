import { MetadataRoute } from 'next'

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = 'https://www.easyoutfitapp.com'
  
  // Static pages
  const routes = [
    '',
    '/signin',
    '/signup',
    '/onboarding',
    '/dashboard',
    '/outfits',
    '/wardrobe',
    '/style-persona',
    '/style-inspiration',
    '/profile',
    '/challenges',
    '/subscription',
  ].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'daily' as const,
    priority: route === '' ? 1.0 : route === '/dashboard' || route === '/outfits' ? 0.9 : 0.7,
  }))

  return routes
}

