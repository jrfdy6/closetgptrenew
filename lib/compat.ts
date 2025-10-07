// lib/compat.ts
import { STYLE_COMPATIBILITY } from "./styleMatrix";

export function styleMatches(requestedStyle: string | undefined, itemStyles: string[] = []) {
  if (!requestedStyle) return true;
  const req = requestedStyle.toLowerCase();
  // exact or contained
  if (itemStyles.map(s=>s.toLowerCase()).includes(req)) return true;
  // check group compatibility
  const compatSet = new Set(STYLE_COMPATIBILITY[req] ?? []);
  for (const it of itemStyles) {
    if (compatSet.has(it.toLowerCase())) return true;
  }
  return false;
}

export function moodMatches(requestedMood: string | undefined, itemMoods: string[] = []) {
  if (!requestedMood) return true;  // optional filter by default
  if (!itemMoods || itemMoods.length === 0) return true; // treat missing mood as universal
  const rm = requestedMood.toLowerCase();
  // small mood alias table
  const MOOD_COMPAT: Record<string, string[]> = {
    bold: ["bold","confident","statement","vibrant","expressive"],
    relaxed: ["relaxed","calm","laidback","casual","neutral"],
    romantic: ["romantic","soft","elegant"],
    // extend as needed
  };
  if (itemMoods.map(m=>m.toLowerCase()).includes(rm)) return true;
  const allowed = new Set(MOOD_COMPAT[rm] ?? []);
  return itemMoods.some(m=>allowed.has(m.toLowerCase()));
}

export function occasionMatches(requestedOccasion: string | undefined, itemOccasions: string[] = []) {
  if (!requestedOccasion) return true;
  const ro = requestedOccasion.toLowerCase();
  if (itemOccasions.map(o=>o.toLowerCase()).includes(ro)) return true;
  // optionally allow some fallbacks: e.g. athletic <-> casual?
  const FALLBACKS: Record<string, string[]> = {
    athletic: ["casual","everyday","sport"],
    casual: ["everyday","casual"],
    business: ["business","business casual","formal","smart casual"],
  };
  const fallback = new Set(FALLBACKS[ro] ?? []);
  return itemOccasions.some(o => fallback.has(o.toLowerCase()));
}
