/** Return only the garment acknowledged by persistent storage, never the staged input. */
export async function persistBatchWardrobeItem(item: Record<string, unknown>, user: { getIdToken: () => Promise<string> }): Promise<Record<string, unknown> & { id: string }> {
  const response = await fetch('/api/wardrobe', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${await user.getIdToken()}` },
    body: JSON.stringify(item),
  });
  let payload: any;
  try { payload = await response.json(); } catch { throw new Error('This item was not confirmed saved. Please retry.'); }
  if (!response.ok || payload?.success !== true || typeof payload.item?.id !== 'string' || !payload.item.id.trim()) {
    throw new Error('This item was not confirmed saved. Please retry.');
  }
  return payload.item;
}
