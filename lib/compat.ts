// lib/compat.ts
import { STYLE_COMPATIBILITY } from "./styleMatrix";

export function styleMatches(requestedStyle?: string, itemStyles: string[] = []): boolean {
  if (!requestedStyle) return true;
  const req = requestedStyle.toLowerCase();
  if (itemStyles.map(s => s.toLowerCase()).includes(req)) return true;

  const compatSet = new Set(STYLE_COMPATIBILITY[req] ?? []);
  for (const it of itemStyles) {
    if (compatSet.has(it.toLowerCase())) return true;
  }
  return false;
}

export function moodMatches(requestedMood?: string, itemMoods: string[] = []): boolean {
  if (!requestedMood) return true;
  if (!itemMoods || itemMoods.length === 0) return true;
  const rm = requestedMood.toLowerCase();
  const MOOD_COMPAT: Record<string, string[]> = {
    bold: ["bold","confident","statement","vibrant","expressive"],
    relaxed: ["relaxed","calm","laidback","casual","neutral"],
    romantic: ["romantic","soft","elegant"],
  };
  if (itemMoods.map(m=>m.toLowerCase()).includes(rm)) return true;
  const allowed = new Set(MOOD_COMPAT[rm] ?? []);
  return itemMoods.some(m => allowed.has(m.toLowerCase()));
}

export function occasionMatches(requestedOccasion?: string, itemOccasions: string[] = []): boolean {
  if (!requestedOccasion) return true;
  const ro = requestedOccasion.toLowerCase();
  if (itemOccasions.map(o => o.toLowerCase()).includes(ro)) return true;

  const FALLBACKS: Record<string, string[]> = {
    athletic: ["casual","everyday","sport"],
    casual: ["everyday","casual"],
    business: ["business","business casual","formal","smart casual"],
  };
  const fallback = new Set(FALLBACKS[ro] ?? []);
  return itemOccasions.some(o => fallback.has(o.toLowerCase()));
}
