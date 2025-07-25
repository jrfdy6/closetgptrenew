import StyleRules from '@/components/style/StyleRules';

export default function StyleRulesPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold mb-4">Style Rules</h1>
          <p className="text-muted-foreground text-sm sm:text-base">
            Create custom style rules to guide your outfit generation. These rules will help the AI understand your preferences
            for different occasions, weather conditions, and seasons.
          </p>
        </div>
        <StyleRules />
      </div>
    </div>
  );
} 