/** @jest-environment node */
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
import { NextRequest } from 'next/server';
import { middleware, config } from './middleware';
const env = { ...process.env };
const pages = ['/dark-mode-test', '/debug-token', '/debug-wardrobe', '/debug/firestore-check', '/personalization-demo', '/personalization-demo-debug', '/test', '/test-flatlay', '/test-personalization'];
beforeEach(() => { process.env = { ...env, NODE_ENV: 'production' }; delete process.env.ENABLE_INTERNAL_DEBUG_PAGES; });
afterAll(() => { process.env = env; });
it.each(pages)('keeps internal page %s covered by production default-deny middleware', path => {
  expect(config.matcher.some(pattern => pattern.endsWith('/:path*') ? path.startsWith(pattern.replace('/:path*', '/')) : path === pattern)).toBe(true);
  const response = middleware(new NextRequest('https://easyoutfit.example' + path));
  expect(response.status).toBe(404);
});
it('does not conflate the development debug policy with production defaults', () => {
  process.env = { ...process.env, NODE_ENV: 'development' };
  expect(middleware(new NextRequest('http://localhost:3102/test')).status).toBe(200);
});
