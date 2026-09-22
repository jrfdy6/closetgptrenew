declare const beforeEach: jest.Lifecycle;
declare const afterEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import React from 'react';
import { act, fireEvent, render, screen } from '@testing-library/react';
import Onboarding from './page';

const mockUser = { uid: 'qa-user', getIdToken: jest.fn() };
const mockRouter = { push: jest.fn(), replace: jest.fn() };
jest.mock('next/navigation', () => ({ useRouter: () => mockRouter }));
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser, loading: false, getIdToken: mockUser.getIdToken }) }));
jest.mock('@/components/BodyPositiveMessage', () => ({ __esModule: true, default: () => null }));
jest.mock('@/components/GuidedUploadWizard', () => ({ __esModule: true, default: ({ targetCount }: { targetCount: number }) => <div data-testid="capsule-target">{targetCount}</div> }));

beforeEach(() => { jest.useFakeTimers(); window.history.replaceState({}, '', '/onboarding'); sessionStorage.clear(); });
afterEach(() => { jest.clearAllTimers(); jest.useRealTimers(); });
const advanceTimer = (ms = 300) => act(() => { jest.advanceTimersByTime(ms); });
const choose = (name: string) => fireEvent.click(screen.getByRole('button', { name }));

it('manual Next after a choice advances once even after its auto timer would fire', () => {
  render(<Onboarding />);
  choose('Male');
  choose('Next');
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  advanceTimer(1000);
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  choose('Rectangle');
  choose('Next');
  advanceTimer(1000);
  expect(screen.getByText('Question 3 of 25')).toBeVisible();
  expect(screen.getByRole('slider', { name: 'Skin tone depth' })).toBeVisible();
});

it('changing a choice replaces its timer and does not skip the following question', () => {
  render(<Onboarding />);
  choose('Male');
  advanceTimer();
  choose('Rectangle');
  advanceTimer(200);
  choose('Oval');
  advanceTimer(100);
  expect(screen.getByText('Question 2 of 25')).toBeVisible();
  advanceTimer(200);
  expect(screen.getByText('Question 3 of 25')).toBeVisible();
  advanceTimer(1000);
  expect(screen.getByText('Question 3 of 25')).toBeVisible();
});

it('Previous cancels a pending auto-advance from the question being left', () => {
  render(<Onboarding />);
  choose('Male');
  advanceTimer();
  choose('Rectangle');
  choose('Previous');
  advanceTimer(1000);
  expect(screen.getByText('Getting started')).toBeVisible();
});

it('still starts a ten-item capsule after the authenticated quiz continuation', () => {
  window.history.replaceState({}, '', '/onboarding?resume=uploads');
  render(<Onboarding />);
  expect(screen.getByTestId('capsule-target')).toHaveTextContent('10');
});
