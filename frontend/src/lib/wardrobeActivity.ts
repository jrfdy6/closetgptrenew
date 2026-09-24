export const WARDROBE_ACTIVITY_EVENT = 'outfitMarkedAsWorn';
export const GAMIFICATION_ACTIVITY_EVENT = 'gamificationActivityChanged';
const notified = new Set<string>();

/** Refresh reward views only after the owning account's item was persisted. */
export function publishWardrobeSaved(uid: string, itemId: string): void {
  window.dispatchEvent(new CustomEvent(GAMIFICATION_ACTIVITY_EVENT, { detail: { uid, itemId } }));
}

/** The rating API, rather than a local estimate, determines the XP announcement. */
export function publishRatingReceipt(uid: string, outfitId: string, receipt: any): void {
  if (receipt?.status !== 'success' && receipt?.success !== true) {
    throw new Error('We could not confirm your feedback. Please retry.');
  }
  window.dispatchEvent(new CustomEvent(GAMIFICATION_ACTIVITY_EVENT, { detail: { uid, outfitId } }));
  const xp = receipt.xp_earned;
  if (!Number.isFinite(xp) || xp <= 0) return;
  const key = `easyoutfit:rating-reward:v1:${uid}:${outfitId}`;
  if (notified.has(key)) return;
  try { if (sessionStorage.getItem(key)) return; } catch { /* memory dedupe still applies */ }
  notified.add(key);
  try { sessionStorage.setItem(key, 'shown'); } catch { /* do not block saved feedback */ }
  window.dispatchEvent(new CustomEvent('xpAwarded', { detail: {
    xp, reason: 'Outfit feedback', level_up: receipt.level_up === true,
    new_level: receipt.new_level,
  } }));
}

/** Publish only an acknowledged server receipt; never calculate rewards locally. */
export function publishWearReceipt(uid: string, receipt: any): void {
  if (receipt?.success !== true || typeof receipt.event_id !== 'string' || !receipt.event_id ||
      typeof receipt.outfit_id !== 'string' || !receipt.outfit_id || !Number.isInteger(receipt.wear_count) || receipt.wear_count < 0) {
    throw new Error('We could not confirm the wear record. Retry to check the same action.');
  }
  const detail = { ...receipt, uid, outfitId: receipt.outfit_id, wearCount: receipt.wear_count };
  window.dispatchEvent(new CustomEvent(WARDROBE_ACTIVITY_EVENT, { detail }));
  window.dispatchEvent(new CustomEvent('outfitWorn', { detail }));
  const xp = receipt.rewards?.xp_awarded ?? receipt.xp_earned;
  if (!Number.isFinite(xp) || xp <= 0 || receipt.undone) return;
  const key = `easyoutfit:wear-reward:v1:${uid}:${receipt.event_id}`;
  if (notified.has(key)) return;
  try { if (sessionStorage.getItem(key)) return; } catch { /* session dedupe still applies */ }
  notified.add(key);
  try { sessionStorage.setItem(key, 'shown'); } catch { /* do not block the acknowledged wear */ }
  window.dispatchEvent(new CustomEvent('xpAwarded', { detail: {
    xp, reason: 'Outfit worn', level_up: receipt.rewards?.level_up ?? receipt.level_up ?? false,
    new_level: receipt.rewards?.new_level ?? receipt.new_level,
  } }));
}
