import { before, after, beforeEach, test } from 'node:test';
import { readFileSync } from 'node:fs';
import { initializeTestEnvironment, assertFails, assertSucceeds } from '@firebase/rules-unit-testing';
import { doc, getDoc, setDoc, updateDoc, deleteDoc, deleteField, setLogLevel } from 'firebase/firestore';

setLogLevel('silent');
let env;
before(async () => {
  if (!process.env.FIRESTORE_EMULATOR_HOST) throw new Error('Run with npm run test:firestore-rules; never against production');
  env = await initializeTestEnvironment({ projectId: 'demo-easyoutfit-rules', firestore: { rules: readFileSync('firestore.rules', 'utf8') } });
});
after(async () => { if (env) await env.cleanup(); });
beforeEach(async () => {
  await env.clearFirestore();
  await env.withSecurityRulesDisabled(async context => {
    const db = context.firestore();
    await setDoc(doc(db, 'users/owner'), { name: 'Owner', quotas: { flatlaysRemaining: 0 }, subscription: { role: 'tier1' } });
    await setDoc(doc(db, 'wardrobe/shirt'), { userId: 'owner', user_id: 'owner', name: 'Shirt' });
    await setDoc(doc(db, 'outfits/look'), { user_id: 'owner', name: 'Look', items: [{ id: 'shirt' }], notes: '', isFavorite: false, flat_lay_status: 'done', flat_lay_url: '/trusted.png', metadata: { flatLayUrl: '/trusted.png' } });
  });
});
const own = () => env.authenticatedContext('owner').firestore();
const other = () => env.authenticatedContext('other').firestore();

test('only the owner can read account and outfit documents', async () => {
  for (const path of ['users/owner', 'wardrobe/shirt', 'outfits/look']) {
    await assertSucceeds(getDoc(doc(own(), path)));
    await assertFails(getDoc(doc(other(), path)));
    await assertFails(getDoc(doc(env.unauthenticatedContext().firestore(), path)));
  }
});
test('owner cannot alter account credit, tier, identity, profile or delete/recreate the account', async () => {
  const ref = doc(own(), 'users/owner');
  for (const patch of [{ 'quotas.flatlaysRemaining': 99 }, { quotas: {} }, { 'subscription.role': 'tier3' }, { subscription: deleteField() }, { firebase_uid: 'other' }, { name: 'Via direct client' }]) {
    await assertFails(updateDoc(ref, patch));
  }
  await assertFails(setDoc(ref, { quotas: { flatlaysRemaining: 30 } }));
  await assertFails(deleteDoc(ref));
  await assertFails(setDoc(doc(env.authenticatedContext('new-user').firestore(), 'users/new-user'), { subscription: { role: 'tier3' } }));
  await assertFails(setDoc(doc(own(), 'profiles/owner'), { subscription: { role: 'tier3' } }));
});
test('admin claims do not grant client access to account authority', async () => {
  const db = env.authenticatedContext('owner', { admin: true }).firestore();
  await assertFails(updateDoc(doc(db, 'users/owner'), { 'quotas.flatlaysRemaining': 99 }));
});
test('wardrobe editing works, but ownership cannot be reassigned or aliased', async () => {
  await assertSucceeds(updateDoc(doc(own(), 'wardrobe/shirt'), { name: 'Blue shirt' }));
  for (const patch of [{ userId: 'other' }, { user_id: 'other' }, { user_id: deleteField() }]) await assertFails(updateDoc(doc(own(), 'wardrobe/shirt'), patch));
  await assertFails(updateDoc(doc(other(), 'wardrobe/shirt'), { name: 'Stolen' }));
  await assertSucceeds(setDoc(doc(own(), 'wardrobe/new'), { userId: 'owner', name: 'Top' }));
  await assertFails(setDoc(doc(own(), 'wardrobe/bad'), { userId: 'owner', user_id: 'other' }));
});
test('favorites and notes remain compatible without touching generated authority', async () => {
  await assertSucceeds(updateDoc(doc(own(), 'outfits/look'), { isFavorite: true, notes: 'For Monday', updatedAt: new Date() }));
  await assertFails(updateDoc(doc(other(), 'outfits/look'), { isFavorite: true }));
  await assertFails(updateDoc(doc(own(), 'outfits/look'), { isFavorite: 'true' }));
  await assertFails(updateDoc(doc(own(), 'outfits/look'), { notes: { role: 'tier3' } }));
});
test('outfit creation, deletion, ownership, item changes and every preview alias require the server', async () => {
  const ref = doc(own(), 'outfits/look');
  for (const patch of [
    { user_id: 'other' }, { userId: 'other' }, { items: [] }, { flat_lay_url: '/forged.png' }, { flatLayUrl: '/forged.png' },
    { flat_lay_status: 'processing' }, { flatLayStatus: 'done' }, { flat_lay_requested: true }, { flatLayRequested: true },
    { 'metadata.flat_lay_url': '/forged.png' }, { 'metadata.flatLayUrl': '/forged.png' }, { metadata: {} },
    { flat_lay_request_allowed: true }, { flat_lay_error: null }, { flatLayError: null },
  ]) await assertFails(updateDoc(ref, patch));
  await assertFails(setDoc(doc(own(), 'outfits/new'), { user_id: 'owner', flat_lay_status: 'done' }));
  await assertFails(deleteDoc(ref));
});
test('history and suggestions cannot be moved to another owner', async () => {
  for (const collection of ['outfit_history', 'daily_outfit_suggestions']) {
    const ref = doc(own(), `${collection}/one`);
    await assertSucceeds(setDoc(ref, { user_id: 'owner', notes: 'Mine' }));
    await assertSucceeds(updateDoc(ref, { notes: 'Updated' }));
    await assertFails(updateDoc(ref, { user_id: 'other' }));
  }
});
test('private generation, payment, reconciliation and unknown ledgers deny every client', async () => {
  for (const collection of ['flat_lay_requests', 'stripe_webhook_events', 'stripe_reconciliation_locks', 'stripe_customers', 'payment_events', 'stripe_events', 'account_reconciliation', 'unknown_private']) {
    await env.withSecurityRulesDisabled(context => setDoc(doc(context.firestore(), `${collection}/one`), { user_id: 'owner' }));
    for (const db of [own(), other(), env.authenticatedContext('owner', { admin: true }).firestore(), env.unauthenticatedContext().firestore()]) {
      const ref = doc(db, `${collection}/one`);
      await assertFails(getDoc(ref));
      await assertFails(setDoc(ref, { user_id: 'owner', complete: true }));
      await assertFails(deleteDoc(ref));
    }
  }
});
