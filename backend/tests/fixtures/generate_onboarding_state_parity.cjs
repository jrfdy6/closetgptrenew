// Frozen pre-migration source oracle. No Firebase, browser, credentials or network.
// Run from repo root: node backend/tests/fixtures/generate_onboarding_state_parity.cjs
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '../../..');
const baseline = '3ed2ecc472a77406ad13bd1182ac6cf6bf1e797f';
const sourcePath = 'frontend/src/lib/onboarding/state.ts';
const source = execFileSync('git', ['show', `${baseline}:${sourcePath}`], { cwd: root, encoding: 'utf8' });
const ts = require(process.env.TYPESCRIPT_MODULE || path.join(root, 'frontend/node_modules/typescript'));
const oracle = {};
vm.runInNewContext(ts.transpileModule(source + '\nexport { timestamp };\n', {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
}).outputText, { exports: oracle, Date });
const cases = [];
function revive(value) {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    if (Object.keys(value).length === 1 && '$date' in value) return new Date(value.$date);
    if (Object.keys(value).length === 1 && '$number' in value) return Number(value.$number);
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, revive(item)]));
  }
  return Array.isArray(value) ? value.map(revive) : value;
}
function add(fn, name, input, extra) {
  const args = extra === undefined ? [revive(input)] : [revive(input), extra];
  cases.push({ fn, name, input, ...(extra === undefined ? {} : { extra }), expected: oracle[fn](...args) });
}
const item = (id, type, extra = {}) => ({ id, type, imageUrl: `https://example.invalid/${id}.jpg`, ...extra });
const capsule = ['shirt', 'sweater', 'hoodie', 'pants', 'chinos', 'skirt', 'jacket', 'cardigan', 'shoes', 'boots'].map((type, i) => item(`g${i}`, type));
const state = (extra = {}) => ({ wardrobe: [], outfits: [], ...extra });
const profile = { stylePersona: { id: 'architect' }, styleQuizCompletedAt: 1790100000 };
const draft = (selected = 'Male', extra = {}) => ({ answers: [{ question_id: 'gender', selected_option: selected }], currentQuestionId: 'height', ...extra });

for (const [name, input] of Object.entries({
  empty: state(), 'legacy-quiz-flag-only': state({ profile: { onboardingCompleted: true } }),
  'profile-only': state({ profile }), 'ten-no-style': state({ wardrobe: capsule }),
  'ten-ready': state({ wardrobe: capsule, profile }), 'nine-not-ready': state({ wardrobe: capsule.slice(0, 9), profile }),
  'ten-shirts': state({ wardrobe: capsule.map(g => ({ ...g, type: 'shirt' })), profile }),
  'one-piece-ready': state({ wardrobe: capsule.map((g, i) => ({ ...g, type: i === 0 ? 'dress' : i === 1 ? 'shoes' : 'accessory' })), profile }),
  'historical-capsule-empty-wardrobe': state({ stored: { milestones: { capsuleCompletedAt: '2025-01-01T00:00:00.000Z' } } }),
  'historical-look-empty-wardrobe': state({ stored: { milestones: { firstOutfitId: 'old-look' } } }),
  'historic-look-inferred-ids': state({ wardrobe: capsule, outfits: [{ id: 'empty-row', items: [] }, { id: 'real-look', items: ['g0', 'g3', 'g8'] }] }),
  'historic-look-inferred-embedded': state({ outfits: [{ id: 'real-look', items: [{ type: 'dress' }, { type: 'shoes' }] }] }),
  'historic-coverage-missing': state({ wardrobe: capsule, outfits: [{ id: 'bad-look', items: ['g0', 'g3'] }] }),
  'historic-item-overrides-catalog': state({ wardrobe: capsule, outfits: [{ id: 'changed-look', items: [{ id: 'g0', type: 'hat' }, 'g3', 'g8'] }] }),
  'historic-first-idless-coverage': state({ wardrobe: capsule, outfits: [{ items: ['g0', 'g3', 'g8'] }, { id: 'later-look', items: ['g0', 'g3', 'g8'] }] }),
  'empty-dashboards-not-complete': state({ outfits: [{ id: 'empty-a', items: [] }, { id: 'empty-b', items: null }] }),
  'saved-draft-resumes': state({ stored: { revision: 4, draft: draft(), milestones: {} } }),
  'protected-first-look-wins': state({ stored: { milestones: { firstOutfitId: 'saved-look' } }, wardrobe: capsule, outfits: [{ id: 'inferred-look', items: ['g0', 'g3', 'g8'] }] }),
  'style-milestone-only': state({ stored: { milestones: { styleCompletedAt: 'saved-date' } } }),
  'style-milestone-fallback': state({ profile, stored: { milestones: { styleCompletedAt: '   ' } } }),
  'empty-map-style-milestone': state({ stored: { milestones: { styleCompletedAt: {} } } }),
  'empty-list-capsule-milestone': state({ stored: { milestones: { capsuleCompletedAt: [] } } }),
})) add('deriveOnboardingState', name, input);

for (const revision of [null, 0, 1, -1, 1.5, '3', true, 9007199254740991, 9007199254740992, { $number: '7.0' }, { $number: 'NaN' }, { $number: 'Infinity' }])
  add('deriveOnboardingState', `revision-${JSON.stringify(revision)}`, state({ stored: { revision } }));

for (const [name, input] of Object.entries({
  empty: [], valid: capsule, duplicateId: [...capsule, { ...capsule[0], type: 'shoes' }],
  duplicateUrl: capsule.map((g, i) => i === 8 ? { ...g, imageUrl: capsule[0].imageUrl } : g),
  duplicateHash: capsule.map((g, i) => ({ ...g, ...(i === 0 || i === 8 ? { imageHash: 'same-photo' } : {}) })),
  duplicateAcrossHashAliases: [item('a', 'shirt', { contentHash: 'shared' }), item('b', 'pants', { image_hash: 'shared' }), item('c', 'shoes')],
  transitiveDuplicates: [item('a', 'shirt', { imageHash: 'A' }), item('b', 'pants', { imageHash: 'A', imageUrl: 'https://example.invalid/B.jpg' }), item('c', 'shoes', { imageUrl: 'https://example.invalid/B.jpg' })],
  unknownFirstDuplicateId: [item('a', 'unknown'), item('a', 'shirt'), item('b', 'pants'), item('c', 'shoes')],
  deleteBoolean: capsule.map((g, i) => i === 0 ? { ...g, deleted: true } : g),
  deleteStringNotBoolean: capsule.map((g, i) => i === 0 ? { ...g, deleted: 'true' } : g),
  deletedAtEmptyMap: capsule.map((g, i) => i === 0 ? { ...g, deletedAt: {} } : g),
  deletedAtZero: capsule.map((g, i) => i === 0 ? { ...g, deletedAt: 0 } : g),
  originalsAndSnakeCase: [item('a', 'shirt', { imageUrl: '', originalImageUrl: 'https://example.invalid/a-original.jpg' }), item('b', 'pants', { imageUrl: '', image_url: 'https://example.invalid/b-original.jpg' }), item('c', 'shoes')],
  unknownDoesNotCount: [item('a', 'anything', { name: 'shirt' }), item('b', 'pants'), item('c', 'shoes')],
  malformedEntriesIgnored: [null, 'garment', [], {}, { id: 'no-image', type: 'shirt' }],
  analysisFallback: [item('a', 'other', { analysis: { category: 'top' } }), item('b', 'pants'), item('c', 'shoes')],
  whitespaceIdDuplicate: [item(' a ', 'shirt'), item('a', 'pants'), item('c', 'shoes')],
  bomIdDuplicate: [item('\ufeffa\ufeff', 'shirt'), item('a', 'pants'), item('c', 'shoes')],
})) add('evaluateCapsule', name, input);

const aliases = JSON.parse(fs.readFileSync(path.join(__dirname, 'onboarding-readiness-fixtures.json'), 'utf8')).aliases;
for (const { type } of aliases) add('classifyGarment', `alias-${type}`, { type });
for (const value of [' ClothingType.SHIRT ', '\ufeffshirt\ufeff', '_shirt_', 'dress---shirt', 'dress\tshirt', '\u001cshirt\u001c', 3, null, ['shirt']]) add('classifyGarment', `normalization-${JSON.stringify(value)}`, { type: value });
add('classifyGarment', 'priority-type-before-category', { type: 'shirt', category: 'shoes', analysis: { type: 'dress' } });
add('classifyGarment', 'analysis-category-fallback', { type: 'other', category: '', analysis: { category: 'dress-shoes' } });

for (const [name, input] of Object.entries({
  camelOwner: { userId: 'owner' }, snakeOwner: { user_id: 'owner' }, bothMatch: { userId: 'owner', user_id: 'owner' },
  conflictingOwners: { userId: 'owner', user_id: 'other' }, absent: {}, blankCamel: { userId: ' ', user_id: 'owner' },
  nullCamel: { userId: null, user_id: 'owner' }, numericOwner: { userId: 7 }, whitespace: { userId: ' owner ' }, bom: { userId: '\ufeffowner\ufeff' },
})) add('ownedBy', name, input, 'owner');

for (const [name, input] of Object.entries({
  empty: {}, timestamp: { styleQuizCompletedAt: 1 }, timestampZero: { styleQuizCompletedAt: 0 }, personaId: { stylePersona: { id: 'classic' } },
  personaName: { stylePersona: { name: 'Classic' } }, personaString: { stylePersona: 'Classic' }, prefsCamel: { stylePreferences: ['Minimalist'] },
  prefsSnake: { style_preferences: ['Minimalist'] }, prefsNested: { preferences: { style: ['Minimalist'] } }, emptyLists: { stylePreferences: [] },
  blankPrefs: { stylePreferences: [' ', '\t'] }, bomPrefs: { stylePreferences: ['\ufeff'] }, recordTimestamp: { styleQuizCompletedAt: {} }, listTimestamp: { styleQuizCompletedAt: [] },
})) add('hasStyleProfile', name, input);

for (const [name, input] of Object.entries({
  empty: { answers: [], currentQuestionId: null }, valid: draft(), cursorOmitted: { answers: [] }, cursorNumeric: draft('Male', { currentQuestionId: 1 }),
  cursorLong: draft('Male', { currentQuestionId: 'a'.repeat(101) }), cursorUppercase: draft('Male', { currentQuestionId: 'Height' }),
  duplicate: { answers: [...draft().answers, ...draft().answers], currentQuestionId: null }, invalidAnswerId: { answers: [{ question_id: 'MixedCase', selected_option: 'Yes' }], currentQuestionId: null },
  extraFieldsStripped: { ...draft(), debug: true, answers: [{ ...draft().answers[0], extra: 'ignored' }] },
  maxAnswers: { answers: Array.from({ length: 80 }, (_, i) => ({ question_id: `q${i}`, selected_option: 'Yes' })), currentQuestionId: null },
  tooManyAnswers: { answers: Array.from({ length: 81 }, (_, i) => ({ question_id: `q${i}`, selected_option: 'Yes' })), currentQuestionId: null },
  asciiAtLimit: draft('a'.repeat(2000)), asciiOverLimit: draft('a'.repeat(2001)), astralAtLimit: draft('😀'.repeat(1000)), astralOverLimit: draft('😀'.repeat(1001)),
  mixedUtf16AtLimit: draft('😀'.repeat(999) + 'ab'), mixedUtf16OverLimit: draft('😀'.repeat(999) + 'abc'), loneSurrogate: draft('\ud800'),
  whitespace: draft(' \t\n'), bomWhitespace: draft('\ufeff'), pythonOnlyWhitespace: draft('\u001c'), malformedAnswer: { answers: [null], currentQuestionId: null },
})) add('parseDraft', name, input);

for (const value of [null, true, 0, 1790100000, 1790100000123, 1.2345, 1.2349999, -0.0001, -1.2345, 999999999999, 1000000000000, 8640000000000000, 8640000000000001,
  '', ' 2026-09-22T00:00:00Z ', 'legacy-date', '\ufeff', { seconds: 1790100000, nanoseconds: 999999999 }, { seconds: 1.2349999 }, { seconds: '1790100000' },
  { $date: '2026-09-22T12:34:56.789Z' }, { $date: 'invalid' }, { $number: 'NaN' }, { $number: 'Infinity' }, { $number: '-Infinity' }]) add('timestamp', `date-${JSON.stringify(value)}`, value);

// Negative numeric timestamps use the accepted legacy seconds heuristic.
// Exercise TimeClip's lower edge, year zero and the Gregorian 400-year cycle.
for (const [name, value] of Object.entries({
  'negative-TimeClip-boundary': -8640000000000,
  'negative-outside-TimeClip': -8640000000000.001,
  'year-zero': Date.parse('0000-01-01T00:00:00.000Z') / 1000,
  'year-zero-leap-day': Date.parse('0000-02-29T00:00:00.000Z') / 1000,
  'negative-expanded-year': Date.parse('-000001-01-01T00:00:00.000Z') / 1000,
  'four-century-leap-day': Date.parse('1600-02-29T23:59:59.999Z') / 1000,
  'nonleap-century': Date.parse('1900-03-01T00:00:00.000Z') / 1000,
})) add('timestamp', name, value);

const fixture = { baseline, source_path: sourcePath, source_sha256: crypto.createHash('sha256').update(source).digest('hex'), cases };
fs.writeFileSync(path.join(__dirname, 'onboarding-state-parity.json'), JSON.stringify(fixture) + '\n');
console.log(JSON.stringify({ cases: cases.length, bytes: fs.statSync(path.join(__dirname, 'onboarding-state-parity.json')).size }));
