import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import Nav from './ClientOnlyNav';
declare const it: jest.It;
declare const expect: jest.Expect;
let mockPath = '/dashboard';
jest.mock('next/navigation', () => ({ useRouter: () => ({ push: jest.fn() }), usePathname: () => mockPath }));
jest.mock('next/dynamic', () => ({ __esModule: true, default: (loader: () => unknown) => loader.toString().includes('BottomNav') ? () => <nav>Bottom navigation</nav> : () => <button>Floating generation</button> }));
it.each(['/outfits/saved-look', '/outfits/create', '/outfits/generate'])('keeps navigation and avoids a floating control over existing outfit actions at %s', path => {
  mockPath = path; render(<Nav />);
  expect(screen.getByText('Bottom navigation')).toBeVisible();
  expect(screen.queryByText('Floating generation')).not.toBeInTheDocument();
});
it('preserves the existing generation shortcut on the dashboard', () => {
  mockPath = '/dashboard'; render(<Nav />);
  expect(screen.getByRole('button', { name: 'Floating generation' })).toBeVisible();
});
