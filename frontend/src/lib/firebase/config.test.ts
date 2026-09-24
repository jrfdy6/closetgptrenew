export {};
declare const beforeEach: jest.Lifecycle;
declare const afterAll: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
const mockAuthEmulator = jest.fn();
const mockFirestoreEmulator = jest.fn();
jest.mock('firebase/app', () => ({ initializeApp: () => ({}) }));
jest.mock('firebase/auth', () => ({ getAuth: () => ({}), connectAuthEmulator: (...args: unknown[]) => mockAuthEmulator(...args) }));
jest.mock('firebase/firestore', () => ({ getFirestore: () => ({}), connectFirestoreEmulator: (...args: unknown[]) => mockFirestoreEmulator(...args) }));
const env = { ...process.env };
beforeEach(() => { jest.clearAllMocks(); jest.resetModules(); process.env = { ...env, NODE_ENV: 'development', NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'demo-easyoutfit-full-release', NEXT_PUBLIC_USE_FIREBASE_EMULATORS: 'true' }; });
afterAll(() => { process.env = env; });
it('connects only the local demo development session to the specified emulators', () => {
  jest.isolateModules(() => { require('./config'); });
  expect(mockAuthEmulator).toHaveBeenCalledWith({}, 'http://127.0.0.1:9099', { disableWarnings: true });
  expect(mockFirestoreEmulator).toHaveBeenCalledWith({}, '127.0.0.1', 8202);
});
it.each([{ NODE_ENV: 'production' as const }, { NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'closetgptrenew' }])('fails closed for a production build or real project %j', override => {
  process.env = { ...process.env, ...override };
  expect(() => jest.isolateModules(() => { require('./config'); })).toThrow('local development server');
  expect(mockAuthEmulator).not.toHaveBeenCalled(); expect(mockFirestoreEmulator).not.toHaveBeenCalled();
});
it('keeps the normal configuration when the explicit flag is absent', () => {
  delete process.env.NEXT_PUBLIC_USE_FIREBASE_EMULATORS;
  jest.isolateModules(() => { require('./config'); });
  expect(mockAuthEmulator).not.toHaveBeenCalled(); expect(mockFirestoreEmulator).not.toHaveBeenCalled();
});
