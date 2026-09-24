declare const beforeEach: jest.Lifecycle;
declare const expect: jest.Expect;
declare const it: jest.It;
import { POST as save } from './save/route';
import { POST as style } from '../user/style-profile/route';
import { POST as updateStyle } from '../update-style-profile/route';
import { POST as upload } from '../upload-photo/route';
import { DELETE as remove } from '../delete-photo/route';
import { POST as migrate } from '../migrate/route';

jest.mock('next/server', () => ({ NextResponse: { json: (body: unknown, init: ResponseInit) => ({
  status: init.status, headers: new Headers(init.headers), json: async () => body,
}) } }));

beforeEach(() => { global.fetch = jest.fn(); });

it.each([['profile/save', save], ['user/style-profile', style], ['update-style-profile', updateStyle],
  ['upload-photo', upload], ['delete-photo', remove], ['migrate', migrate]] as const)(
  'retires %s without reading a supplied identity/photo or contacting a service', async (_name, handler) => {
    const request = { json: jest.fn(), formData: jest.fn(),
      url: 'https://example.test/api/retired?url=https://foreign.test/private-photo',
      headers: new Headers({ Authorization: 'Bearer forged', 'x-user-id': 'foreign' }),
    } as unknown as Request;
    const response = await handler(request);
    expect(response.status).toBe(410);
    expect(response.headers.get('Cache-Control')).toBe('private, no-store');
    expect(await response.json()).toEqual({ error: 'This endpoint has been retired.' });
    expect(request.json).not.toHaveBeenCalled();
    expect(request.formData).not.toHaveBeenCalled();
    expect(fetch).not.toHaveBeenCalled();
  },
);
