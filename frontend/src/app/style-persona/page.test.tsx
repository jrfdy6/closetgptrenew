import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import Page from './page';
declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const it: jest.It;
declare const expect: jest.Expect;
const mockUser = { uid: 'owner', getIdToken: async () => 'token' };
const mockRouter = { push: jest.fn() };
jest.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
jest.mock('@/lib/firebase-context', () => ({ useFirebase: () => ({ user: mockUser, loading: false }) }));
jest.mock('@/lib/publicBackendUrl', () => ({ buildPublicBackendUrl: (path: string) => path }));
jest.mock('@/components/Navigation', () => ({ __esModule: true, default: () => null }));
beforeEach(() => { jest.spyOn(console, 'log').mockImplementation(() => {}); });
afterEach(() => jest.restoreAllMocks());

it.each(['classic', 'strategist', 'innovator', 'wanderer'])('retains the server-saved %s persona instead of rescoring it into the partial local catalog', async id => {
  const name = `The ${id[0].toUpperCase()}${id.slice(1)}`;
  global.fetch = jest.fn().mockResolvedValue({ ok: true, json: async () => ({
    userId: 'owner', name: 'Test', email: 'owner@example.test', gender: 'male',
    stylePreferences: ['Minimalist'],
    stylePersona: { id, name, tagline: 'Saved quiz tagline', description: 'Saved quiz description',
      styleMission: 'Saved quiz mission', traits: ['Saved quiz trait'], examples: [] },
  }) });
  render(<Page />);
  expect(await screen.findByRole('heading', { level: 1, name })).toBeVisible();
  expect(screen.queryByRole('heading', { level: 1, name: 'The Architect' })).not.toBeInTheDocument();
  expect(screen.getByText('Saved quiz tagline')).toBeVisible();
  expect(screen.getByText('Saved quiz trait')).toBeVisible();
  expect(screen.getByAltText(`${name} style example`)).toHaveAttribute('src', expect.stringContaining(`/images/style-heroes/${id}-`));
});
