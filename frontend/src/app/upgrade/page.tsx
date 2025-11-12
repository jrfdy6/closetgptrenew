import Navigation from '@/components/Navigation';
import ClientOnlyNav from '@/components/ClientOnlyNav';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Crown, Sparkles } from 'lucide-react';

const tiers = [
  {
    id: 'tier1',
    name: 'Style Starter',
    description: 'Everything you need to catalogue outfits and start building your personal lookbook.',
    price: '$0',
    cadence: 'Included',
    highlight: 'New wardrobe creators',
    perks: [
      '1 premium flat lay credit each week',
      'Unlimited manual outfits',
      'Wardrobe organization and tagging',
      'Mobile-friendly outfit builder'
    ],
    cta: 'You’re here now'
  },
  {
    id: 'tier2',
    name: 'Style Plus',
    description: 'Upgrade for weekly outfit visuals, priority processing, and deeper personalization.',
    price: '$6',
    cadence: 'per month',
    annual: '$36 per year (save 50%)',
    highlight: 'Style enthusiasts',
    perks: [
      '7 premium flat lay credits per week',
      'Priority flat lay rendering queue',
      'Unlimited saved outfits & notes',
      'Occasion-based wardrobe insights',
      'Early access to styling experiments'
    ],
    cta: 'Join Style Plus'
  },
  {
    id: 'tier3',
    name: 'Style Premium',
    description: 'For creators and teams who want premium visuals on demand and concierge support.',
    price: '$10',
    cadence: 'per month',
    highlight: 'Creators & stylists',
    perks: [
      '30 premium flat lay credits per week',
      'Concierge flat lay rush requests',
      'Branded export-ready visuals',
      'Shared workspaces & collaboration',
      'Quarterly wardrobe performance review'
    ],
    cta: 'Request access'
  }
];

export default function UpgradePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100 dark:from-amber-950 dark:via-amber-900 dark:to-orange-950">
      <Navigation />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
        <section className="text-center space-y-4">
          <Badge className="bg-amber-600 text-white rounded-full px-4 py-1 text-xs uppercase tracking-wide">
            Premium Flat Lays
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-serif font-bold text-stone-900 dark:text-stone-100">
            Choose your styling pace
          </h1>
          <p className="text-stone-600 dark:text-stone-300 text-base sm:text-lg max-w-2xl mx-auto">
            Easy Outfit caters to every type of closet. Keep your free plan for casual outfit saving or
            upgrade for magazine-ready flat lays, priority rendering, and concierge support.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-3">
          {tiers.map((tier) => (
            <Card
              key={tier.id}
              className={`relative overflow-hidden border-2 ${
                tier.id === 'tier2'
                  ? 'border-amber-500 shadow-xl shadow-amber-500/10'
                  : 'border-transparent shadow-md'
              }`}
            >
              {tier.id === 'tier2' && (
                <div className="absolute -top-5 left-1/2 -translate-x-1/2 bg-amber-500 text-white px-4 py-1 rounded-full text-xs font-semibold flex items-center gap-1">
                  <Sparkles className="h-3 w-3" />
                  Most loved
                </div>
              )}
              {tier.id === 'tier3' && (
                <div className="absolute top-4 right-4 text-amber-500">
                  <Crown className="h-6 w-6" />
                </div>
              )}

              <CardHeader className="space-y-2">
                <CardTitle className="text-2xl font-serif">{tier.name}</CardTitle>
                <p className="text-sm text-stone-600 dark:text-stone-300">{tier.description}</p>
              </CardHeader>

              <CardContent className="space-y-6">
                <div>
                  <span className="text-3xl font-bold text-stone-900 dark:text-stone-100">
                    {tier.price}
                  </span>
                  <span className="text-sm text-stone-500 dark:text-stone-400 ml-2">
                    {tier.cadence}
                  </span>
                  {tier.annual && (
                    <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
                      {tier.annual}
                    </p>
                  )}
                </div>

                <ul className="space-y-3 text-sm text-stone-700 dark:text-stone-200">
                  {tier.perks.map((perk) => (
                    <li key={perk} className="flex items-start gap-2">
                      <Check className="h-4 w-4 mt-0.5 text-amber-500" />
                      <span>{perk}</span>
                    </li>
                  ))}
                </ul>

                <div className="pt-2">
                  {tier.id === 'tier1' ? (
                    <Button disabled className="w-full bg-stone-300 text-stone-600" variant="secondary">
                      {tier.cta}
                    </Button>
                  ) : (
                    <Button asChild className="w-full bg-stone-900 text-white hover:bg-stone-800">
                      <a href="mailto:hello@easyoutfitapp.com" target="_blank" rel="noopener noreferrer">
                        {tier.cta}
                      </a>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </section>

        <section className="grid gap-6 lg:grid-cols-2">
          <Card className="border-2 border-stone-200 dark:border-stone-700">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                What counts as a premium flat lay?
              </CardTitle>
            </CardHeader>
            <CardContent className="text-sm text-stone-600 dark:text-stone-300 space-y-2">
              <p>
                Every time you request a premium flat lay we stitch together your real garment photos,
                apply background removal, drop shadows, and deliver a cohesive, share-worthy visual for
                your outfit.
              </p>
              <p>
                Credits reset weekly so you can experiment with new outfits every few days without
                worrying about running out mid-month.
              </p>
            </CardContent>
          </Card>

          <Card className="border-2 border-stone-200 dark:border-stone-700">
            <CardHeader>
              <CardTitle className="text-xl font-semibold text-stone-900 dark:text-stone-100">
                Need more than 30 flat lays a week?
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-stone-600 dark:text-stone-300">
              <p>
                Agencies, stylists, and wardrobe teams can partner with Easy Outfit for enterprise-level
                support, custom branding, and SLA-backed turnaround times.
              </p>
              <Button asChild variant="outline" className="w-fit">
                <a href="mailto:hello@easyoutfitapp.com" target="_blank" rel="noopener noreferrer">
                  Talk with our team
                </a>
              </Button>
            </CardContent>
          </Card>
        </section>
      </main>

      <ClientOnlyNav />
    </div>
  );
}

