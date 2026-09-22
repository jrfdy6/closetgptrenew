import fixtures from '../../../backend/tests/fixtures/garment-generation-metadata.json';
import { convertToPydanticShape, FrontendOutfitRequest } from './outfitDataConverter';
import { DataValidator } from './dataValidator';
import { generateOutfit, RobustApiClient } from './robustApiClient';

declare const expect: jest.Expect;
declare const it: jest.It;

const requestFor = (item: Record<string, unknown>) => ({
  occasion: 'Casual', style: 'Minimalist', mood: 'Serene',
  weather: { temperature: 72, condition: 'Clear' },
  wardrobe: [item], user_profile: { id: 'owner' },
} as FrontendOutfitRequest);

describe('saved garment generation handoff', () => {
  beforeEach(() => { jest.spyOn(console, 'log').mockImplementation(() => {}); });
  afterEach(() => { jest.restoreAllMocks(); });

  it.each(fixtures)('$name survives conversion and request sanitization', fixture => {
    const original = JSON.parse(JSON.stringify(fixture.item));
    const converted = convertToPydanticShape(requestFor(fixture.item));
    const validation = DataValidator.getInstance().validateOutfitRequest(converted);
    expect(validation.isValid).toBe(true);
    const item = validation.sanitizedValue.wardrobe[0];
    expect(item.metadata.visualAttributes).toEqual(fixture.expectedVisual);
    expect(item.metadata).toMatchObject(fixture.expectedMetadata);
    expect(item.analysis).toEqual(fixture.item.analysis);
    expect(fixture.item).toEqual(original);
  });

  it('posts the merged facts and raw analysis to the actual active endpoint', async () => {
    const originalFetch = global.fetch;
    const fetchMock = jest.fn().mockResolvedValue({
      ok: true, status: 200, statusText: 'OK', headers: new Headers(), json: async () => ({ id: 'look', items: [] }),
    } as Response);
    global.fetch = fetchMock;
    (RobustApiClient as unknown as { instance?: RobustApiClient }).instance = undefined;
    try {
      await generateOutfit(convertToPydanticShape(requestFor(fixtures[1].item)), 'fixture-token');
      expect(fetchMock.mock.calls[0][0]).toMatch(/\/api\/outfits-existing-data\/generate-personalized$/);
      const sent = JSON.parse(fetchMock.mock.calls[0][1]!.body as string);
      expect(sent.wardrobe[0].metadata.visualAttributes).toEqual(fixtures[1].expectedVisual);
      expect(sent.wardrobe[0].analysis).toEqual(fixtures[1].item.analysis);
    } finally {
      global.fetch = originalFetch;
      (RobustApiClient as unknown as { instance?: RobustApiClient }).instance = undefined;
    }
  });

  it('does not invent visual facts when capture has not supplied any', () => {
    const converted = convertToPydanticShape(requestFor({ id: 'shirt', name: 'Pending shirt', type: 'shirt', color: 'unknown' }));
    expect(converted.wardrobe[0].metadata.visualAttributes).toBeUndefined();
  });

  it.each([
    [{ fallback: true, isManualOverride: false, isRealWeather: false, isFallbackWeather: true }, 'estimated'],
    [{ fallback: true, isManualOverride: true }, 'manual'],
    [{ fallback: false, isRealWeather: true, observedAt: '2026-09-22T16:00:00Z' }, 'observed'],
    [{ fallback: false }, 'unknown'],
    [{}, 'unknown'],
    [{ source: 'cached observation', fallback: false }, 'cached observation'],
  ])('preserves weather provenance %j through both request boundaries', (provenance, source) => {
    const request = requestFor(fixtures[0].item);
    request.weather = { ...request.weather, ...provenance };
    const converted = convertToPydanticShape(request);
    const validation = DataValidator.getInstance().validateOutfitRequest(converted);
    expect(validation.isValid).toBe(true);
    expect(validation.sanitizedValue.weather).toMatchObject({ ...provenance, source });
    expect(validation.sanitizedValue.weather.temperature).toBe(72);
  });

  it.each([
    ['Overcast', 'Overcast'], ['Light Rain', 'Rainy'], ['Heavy Rain', 'Rainy'],
    ['Partly Cloudy', 'Cloudy'], ['Light Snow', 'Snowy'], ['drizzle', 'Rainy'],
    ['Unknown provider condition', 'Unknown'],
  ])('preserves %s instead of claiming Clear weather', (rawCondition, condition) => {
    const request = requestFor(fixtures[0].item);
    request.weather = { ...request.weather, condition: rawCondition };
    const validation = DataValidator.getInstance().validateOutfitRequest(convertToPydanticShape(request));
    expect(validation.isValid).toBe(true);
    expect(validation.sanitizedValue.weather).toMatchObject({ rawCondition, condition });
  });
});
