import React, { StrictMode } from 'react';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SmartWeatherOutfitGenerator from './SmartWeatherOutfitGenerator';
import { dailyOutfitKey } from '@/lib/dailyOutfitAttempt';

declare const expect: jest.Expect;
declare const it: jest.It;

let mockUser = { uid: 'owner', displayName: 'Owner', email: 'owner@example.test', getIdToken: jest.fn(async () => 'token') };
const mockWeather = { temperature: 72, condition: 'Clear', location: 'Test City' };
const mockFetchWeather = jest.fn();
const mockGenerate = jest.fn();
jest.mock('@/contexts/AuthContext', () => ({ useAuthContext: () => ({ user: mockUser }) }));
jest.mock('@/hooks/useWeather', () => ({ useAutoWeather: () => ({ weather: mockWeather, loading: false, fetchWeatherByLocation: mockFetchWeather }) }));
jest.mock('@/lib/weather', () => ({ formatWeatherForDisplay: () => ({ temperature: '72°F', condition: 'Clear' }) }));
jest.mock('@/lib/outfitDataConverter', () => ({ convertToPydanticShape: (data: unknown) => data, validateConvertedData: () => true }));
jest.mock('@/lib/robustApiClient', () => ({ generateOutfit: (...args: unknown[]) => mockGenerate(...args) }));
const items = [
  { id: 'shirt', type: 'shirt', name: 'Plain tee', imageUrl: 'https://example.test/tee.jpg', color: 'White' },
  { id: 'pants', type: 'pants', name: 'Chinos', color: 'Beige' },
  { id: 'shoes', type: 'shoes', name: 'Sneakers', color: 'Navy' },
];
const response = (body: unknown, ok = true) => ({ ok, json: async () => body }) as Response;
let account = 0;
beforeEach(() => {
  account += 1;
  mockUser = { ...mockUser, uid: `owner-${account}` };
  localStorage.clear();
  sessionStorage.clear();
  mockGenerate.mockReset().mockResolvedValue({ data: { id: 'look', name: 'Saved look', items, confidence: .8 } });
  global.fetch = jest.fn().mockResolvedValue(response(items));
  jest.spyOn(console, 'log').mockImplementation(() => undefined);
  jest.spyOn(console, 'error').mockImplementation(() => undefined);
  jest.spyOn(console, 'warn').mockImplementation(() => undefined);
});
afterEach(() => jest.restoreAllMocks());

it('does not fetch or generate for an empty, loading or failed capsule', async () => {
  const view = render(<SmartWeatherOutfitGenerator generationEnabled={false} readinessMessage="Loading saved wardrobe…" />);
  await act(async () => undefined);
  view.rerender(<SmartWeatherOutfitGenerator generationEnabled={false} readinessMessage="We couldn't load your wardrobe." />);
  await act(async () => undefined);
  expect(mockGenerate).not.toHaveBeenCalled();
  expect(fetch).not.toHaveBeenCalled();
  expect(screen.getByText("We couldn't load your wardrobe.")).toBeInTheDocument();
});

it('rejects a newly empty wardrobe instead of POSTing generation', async () => {
  (fetch as jest.Mock).mockResolvedValue(response([]));
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  await screen.findByRole('alert');
  expect(mockGenerate).not.toHaveBeenCalled();
  expect(localStorage.getItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()))).toBeNull();
});

it('reports failed wardrobe reads rather than treating them as empty successful recommendations', async () => {
  (fetch as jest.Mock).mockResolvedValue(response({}, false));
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  expect(await screen.findByRole('alert')).toHaveTextContent("We couldn't load your wardrobe");
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('generates at most once through StrictMode, parent rerenders and remounts', async () => {
  const callback = jest.fn();
  const view = render(<StrictMode><SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} /></StrictMode>);
  await waitFor(() => expect(callback).toHaveBeenCalledTimes(1));
  view.rerender(<StrictMode><SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} /></StrictMode>);
  view.unmount();
  render(<SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} />);
  await screen.findByAltText('Plain tee');
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  expect(callback).toHaveBeenCalledTimes(1);
});

it('keeps a failed attempt claimed across remounts and retries only after a click', async () => {
  mockGenerate.mockRejectedValueOnce(new Error('Generation unavailable'));
  const view = render(<SmartWeatherOutfitGenerator generationEnabled />);
  expect(await screen.findByRole('alert')).toHaveTextContent('Generation unavailable');
  view.unmount();
  render(<SmartWeatherOutfitGenerator generationEnabled />);
  await act(async () => undefined);
  expect(mockGenerate).toHaveBeenCalledTimes(1);
  fireEvent.click(screen.getByRole('button', { name: "Generate today's outfit" }));
  await screen.findByAltText('Plain tee');
  expect(mockGenerate).toHaveBeenCalledTimes(2);
});

it('does not cache or announce a successful empty server result', async () => {
  mockGenerate.mockResolvedValue({ data: { id: 'empty-look', items: [] } });
  const callback = jest.fn();
  render(<SmartWeatherOutfitGenerator generationEnabled onOutfitGenerated={callback} />);
  expect(await screen.findByRole('alert')).toHaveTextContent("couldn't create a complete saved outfit");
  expect(callback).not.toHaveBeenCalled();
  expect(localStorage.getItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()))).toBeNull();
});

it('still shows an owned cached dress-and-shoes look when the current capsule is incomplete', async () => {
  const cached = { id: 'legacy-look', name: 'Saved dress', userId: mockUser.uid, confidence: .8,
    generatedAt: new Date().toISOString(), weather: mockWeather, reasoning: '',
    items: [{ id: 'dress', type: 'dress', name: 'Summer dress', imageUrl: 'https://example.test/dress.jpg' }, items[2]] };
  localStorage.setItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()), JSON.stringify(cached));
  render(<SmartWeatherOutfitGenerator generationEnabled={false} />);
  await screen.findByAltText('Summer dress');
  expect(mockGenerate).not.toHaveBeenCalled();
});

it('does not display cached data without matching account ownership', async () => {
  localStorage.setItem(dailyOutfitKey(mockUser.uid, new Date().toDateString()), JSON.stringify({
    id: 'foreign', userId: 'other-owner', name: 'Foreign look', items, confidence: .8,
  }));
  render(<SmartWeatherOutfitGenerator generationEnabled={false} />);
  await act(async () => undefined);
  expect(screen.queryByText('Plain tee')).not.toBeInTheDocument();
  expect(mockGenerate).not.toHaveBeenCalled();
});
