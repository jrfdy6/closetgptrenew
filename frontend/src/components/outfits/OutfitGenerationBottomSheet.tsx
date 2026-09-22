"use client";

import { useState, useEffect } from 'react';
import { Sheet, SheetContent, SheetTitle, SheetDescription } from '@/components/ui/sheet';
import { Button } from '@/components/ui/button';
import { Chip } from '@/components/ui/chip';
import { X, Sparkles, Shuffle, Sun, Target } from 'lucide-react';

interface OutfitGenerationBottomSheetProps {
  open: boolean;
  onClose: () => void;
  onGenerate: (options: { occasion: string; style: string; mood: string }) => void;
  onShuffle: () => void;
  generating?: boolean;
  disabled?: boolean;
  inline?: boolean;
  initialOptions?: { occasion?: string; style?: string; mood?: string };
  weather?: { temperature: number; condition: string; location?: string; fallback?: boolean } | null;
  weatherChoice?: string;
  onWeatherChange?: (value: string) => void;
  occasions: string[];
  styles: string[];
  moods: string[];
  baseItem?: any;
  onRemoveBaseItem?: () => void;
  userGender?: string;
}

/** One configuration form, used in a sheet or directly in the first-look journey. */
export default function OutfitGenerationBottomSheet({
  open, onClose, onGenerate, onShuffle, generating = false, disabled = false,
  inline = false, initialOptions, weather, weatherChoice = 'Auto', onWeatherChange,
  occasions, styles, moods, baseItem, onRemoveBaseItem,
}: OutfitGenerationBottomSheetProps) {
  const [selectedOccasion, setSelectedOccasion] = useState(initialOptions?.occasion || '');
  const [selectedStyle, setSelectedStyle] = useState(initialOptions?.style || '');
  const [selectedMood, setSelectedMood] = useState(initialOptions?.mood || '');

  useEffect(() => {
    if (!open && !inline) {
      setSelectedOccasion('');
      setSelectedStyle('');
      setSelectedMood('');
    }
  }, [open, inline]);

  // A profile refresh can change the available styles. Do not submit a hidden value.
  const canGenerate = !disabled && !generating && occasions.includes(selectedOccasion)
    && styles.includes(selectedStyle) && moods.includes(selectedMood);
  const title = inline ? 'What are you dressing for?' : 'Create your outfit';
  const description = 'Choose an occasion, a style and a mood. We’ll use the pieces saved in your closet.';
  const fields = [
    { label: 'Occasion', values: occasions, value: selectedOccasion, select: setSelectedOccasion },
    { label: 'Style', values: styles, value: selectedStyle, select: setSelectedStyle },
    { label: 'Mood', values: moods, value: selectedMood, select: setSelectedMood },
  ];
  const content = (
    <>
      <div className="flex items-start justify-between gap-4 border-b border-stone-200/70 px-5 py-6 sm:px-8 dark:border-stone-700">
        <div>
          {inline ? <h2 className="font-serif text-2xl text-stone-900 dark:text-stone-100">{title}</h2>
            : <SheetTitle className="font-serif text-2xl">{title}</SheetTitle>}
          {inline ? <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
            : <SheetDescription className="mt-2 leading-relaxed">{description}</SheetDescription>}
        </div>
        {!inline && <Button variant="ghost" size="icon" onClick={onClose} aria-label="Close outfit settings" className="shrink-0">
          <X className="h-5 w-5" />
        </Button>}
      </div>
      <div className={`space-y-7 px-5 py-6 sm:px-8 ${inline ? '' : 'min-h-0 flex-1 overflow-y-auto'}`}>
        {baseItem && <div className="flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-950/30">
          <Target className="h-5 w-5 shrink-0 text-amber-800 dark:text-amber-200" aria-hidden="true" />
          <p className="flex-1 text-sm">Building around <strong>{baseItem.name || 'your selected item'}</strong></p>
          {onRemoveBaseItem && <Button variant="ghost" size="sm" onClick={onRemoveBaseItem}>Remove</Button>}
        </div>}
        {fields.map(field => <fieldset key={field.label} disabled={disabled || generating}>
          <legend className="mb-3 text-sm font-semibold text-stone-800 dark:text-stone-200">{field.label} <span className="sr-only">(required)</span></legend>
          <div className="flex flex-wrap gap-2">
            {field.values.map(value => <Chip key={value} selected={field.value === value}
              aria-pressed={field.value === value} onClick={() => field.select(value)}
              className="min-h-11 whitespace-normal px-4 text-sm motion-reduce:transition-none">
              {value}
            </Chip>)}
          </div>
        </fieldset>)}
        <div className="rounded-2xl bg-stone-100/70 p-4 dark:bg-stone-800/60">
          <p className="flex items-start gap-2 text-sm text-stone-700 dark:text-stone-200">
            <Sun className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            {weather && Number.isFinite(weather.temperature)
              ? <span>{weather.fallback ? 'Estimated weather' : 'Current weather'}: {Math.round(weather.temperature)}°F, {weather.condition}{!weather.fallback && weather.location ? ` · ${weather.location}` : ''}</span>
              : <span>Weather is unavailable. You can choose the conditions below.</span>}
          </p>
          {onWeatherChange && <div className="mt-3">
            <label htmlFor={inline ? 'first-look-weather' : 'outfit-sheet-weather'} className="mb-1.5 block text-sm font-medium">Conditions for this look</label>
            <select id={inline ? 'first-look-weather' : 'outfit-sheet-weather'} value={weatherChoice || 'Auto'}
              onChange={event => onWeatherChange(event.target.value)} disabled={disabled || generating}
              className="min-h-11 w-full rounded-xl border border-stone-300 bg-background px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary dark:border-stone-600">
              <option value="Auto">Use available weather</option>
              <option value="Hot">Hot</option><option value="Mild">Mild</option><option value="Cold">Cold</option>
              <option value="Rainy">Rainy</option><option value="Windy">Windy</option>
            </select>
            <p className="mt-2 text-xs leading-relaxed text-muted-foreground">Choose different conditions if the estimate doesn’t match your day.</p>
          </div>}
        </div>
      </div>
      <div className="space-y-3 border-t border-stone-200/70 px-5 py-5 sm:px-8 dark:border-stone-700">
        <Button disabled={!canGenerate} onClick={() => {
          if (canGenerate) onGenerate({ occasion: selectedOccasion, style: selectedStyle, mood: selectedMood });
        }} className="h-12 w-full rounded-xl text-base font-semibold motion-reduce:transition-none">
          <Sparkles className="mr-2 h-5 w-5" aria-hidden="true" />
          {generating ? 'Creating your look…' : inline ? 'Create my first outfit' : 'Create outfit'}
        </Button>
        <Button onClick={onShuffle} disabled={disabled || generating} variant="outline" className="h-11 w-full rounded-xl motion-reduce:transition-none">
          <Shuffle className="mr-2 h-4 w-4" aria-hidden="true" />Surprise me
        </Button>
        {!canGenerate && !generating && <p className="text-center text-xs text-muted-foreground">
          {disabled ? 'Loading your saved wardrobe and style…' : 'Choose all three settings, or let us surprise you.'}
        </p>}
        {inline && <p className="text-center text-xs leading-relaxed text-muted-foreground">Your outfit is saved when it’s created. An AI flatlay is a separate choice with its credit cost shown before you request it.</p>}
      </div>
    </>
  );
  if (inline) return <section aria-label="First outfit configuration" className="overflow-hidden rounded-3xl border border-stone-200 bg-white shadow-sm dark:border-stone-700 dark:bg-stone-900">{content}</section>;
  return <Sheet open={open} onOpenChange={value => { if (!value) onClose(); }}>
    <SheetContent side="bottom" className="flex max-h-[90dvh] flex-col overflow-hidden rounded-t-3xl bg-background p-0">{content}</SheetContent>
  </Sheet>;
}
