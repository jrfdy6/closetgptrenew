import type { User } from 'firebase/auth';
import { shoppingService, type ShoppingRecommendationsResponse } from './shoppingService';

const user: User = {
  uid: 'test-owner', email: null, emailVerified: false, displayName: null,
  isAnonymous: false, phoneNumber: null, photoURL: null, providerData: [],
  providerId: 'firebase', tenantId: null, metadata: {}, refreshToken: 'test-refresh',
  delete: jest.fn(), getIdToken: jest.fn().mockResolvedValue('test-token'),
  getIdTokenResult: jest.fn(), reload: jest.fn(), toJSON: () => ({}),
};
const response: ShoppingRecommendationsResponse = {
  success: true, recommendations: [], store_recommendations: [],
  shopping_strategy: { total_items_needed: 0, high_priority_items: 0, estimated_total_cost: 0, budget_range: 'medium', shopping_phases: [], tips: [] },
  total_estimated_cost: 0, budget_range: 'medium',
};
const originalFetch = global.fetch;
afterEach(() => { global.fetch = originalFetch; });

it('preserves an older cached response without manufacturing a generation timestamp', async () => {
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ success: true, data: { shopping_recommendations: response } }) });
  const result = await shoppingService.getShoppingRecommendations(user);
  expect(result).toEqual(response);
  expect(result?.generated_at).toBeUndefined();
});

it('does not expose the backend failure envelope as shopping recommendations', async () => {
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({ success: true, data: { shopping_recommendations: { success: false, recommendations: [], store_recommendations: [], shopping_strategy: {} } } }) });
  expect(await shoppingService.getShoppingRecommendations(user)).toBeNull();
});
