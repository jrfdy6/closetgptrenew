/** @jest-environment node */
declare const expect: jest.Expect;
import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();

function runtimeSources(directory: string): string[] {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) return runtimeSources(file);
    return /\.[cm]?[jt]sx?$/.test(file) && !/\.(test|spec)\./.test(file) ? [file] : [];
  });
}

test('the Vercel runtime and its dependency graph cannot initialize Firebase Admin', () => {
  const forbidden = /firebase-admin|FIREBASE_PRIVATE_KEY|FIREBASE_CLIENT_EMAIL|FIREBASE_SERVICE_ACCOUNT|GOOGLE_APPLICATION_CREDENTIALS/;
  const consumers = runtimeSources(path.join(root, 'src')).filter(file => forbidden.test(fs.readFileSync(file, 'utf8')));
  expect(consumers.map(file => path.relative(root, file))).toEqual([]);
  const manifest = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));
  const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'));
  expect(manifest.dependencies['firebase-admin']).toBeUndefined();
  expect(Object.keys(lock.packages).filter(key => /(^|\/)firebase-admin($|\/)/.test(key))).toEqual([]);
  expect(manifest.dependencies['server-only']).toBeTruthy();
});

test('backend destinations and bearer forwarding remain restricted to server modules', () => {
  for (const name of ['backendUrl.ts', 'backendProxy.ts']) {
    const source = fs.readFileSync(path.join(root, 'src/lib/server', name), 'utf8');
    expect(source).toMatch(/^import ['"]server-only['"];/);
  }
});
