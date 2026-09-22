import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const canonical = path.join(root, 'frontend/firestore.rules');
for (const configPath of ['frontend/firebase.json', 'frontend/firebase.emulator.json', 'backend/firebase.json']) {
  const absolute = path.join(root, configPath);
  const config = JSON.parse(readFileSync(absolute, 'utf8'));
  assert.equal(path.resolve(path.dirname(absolute), config.firestore.rules), canonical, `${configPath} must use canonical frontend/firestore.rules`);
}
assert.ok(!existsSync(path.join(root, 'backend/firebase/firestore.rules')), 'Do not create a second Firestore rules source');
assert.ok(readFileSync(canonical, 'utf8').includes("rules_version = '2'"));
console.log('All Firebase deployment and emulator configurations use the canonical rules source.');
