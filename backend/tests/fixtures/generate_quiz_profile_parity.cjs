// Regenerate only when the accepted questionnaire/mapping contract changes.
// Run from repo root: node backend/tests/fixtures/generate_quiz_profile_parity.cjs
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '../../..');
const ts = require(process.env.TYPESCRIPT_MODULE || path.join(root, 'frontend/node_modules/typescript'));
const mappingPath = 'frontend/src/lib/server/quizProfile.ts';
const questionsPath = 'frontend/src/lib/onboarding/questions.ts';
const mappingSource = fs.readFileSync(path.join(root, mappingPath), 'utf8');
const questionsSource = fs.readFileSync(path.join(root, questionsPath), 'utf8');
const instant = 1790100000000;
function compile(source) {
  const exports = {};
  const result = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 } });
  vm.runInNewContext(result.outputText, {
    exports, require: name => {
      if (name === '@/lib/server/debug') return { serverDebugLog: () => {} };
      throw new Error(`Unexpected import ${name}`);
    }, Date: { now: () => instant },
  });
  return exports;
}
const { mapQuizAnswersToProfile } = compile(mappingSource);
const { fullQuizQuestions } = compile(questionsSource);
const genders = ['Male', 'Female', 'Non-binary', 'Prefer not to say'];
const required = Object.fromEntries(genders.map(gender => [gender, fullQuizQuestions(gender).map(q => q.id)]));
const personasText = mappingSource.match(/const STYLE_PERSONAS: Record<string, any> = (\{[\s\S]*?\n  \});\n\n  \/\/ Score/)[1];
const personas = vm.runInNewContext(`(${personasText})`);
const digest = source => crypto.createHash('sha256').update(source).digest('hex');
const data = { source_sha256: { [mappingPath]: digest(mappingSource), [questionsPath]: digest(questionsSource) }, required_question_ids: required, personas };
fs.writeFileSync(path.join(root, 'backend/src/services/quiz_profile_data.json'), JSON.stringify(data, null, 2) + '\n');
const cases = [];
const activities = ['Office work and meetings', 'Creative work and casual meetings', 'Active lifestyle and sports', 'Mix of everything'];
const elements = ['Clean lines and minimal details', 'Rich textures and patterns', 'Classic and timeless pieces', 'Bold and statement pieces'];
const styles = [[], ['Minimalist'], ['Clean Minimal'], ['Street Style'], ['Urban Street'], ['Classic Elegant'], ['Old Money'], ['Cottagecore'], ['Natural Boho'], ['Minimalist', 'Classic Elegant', 'Old Money', 'Street Style', 'Cottagecore'], ['Minimalist', 'Minimalist']];
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key => [key, canonical(value[key])]));
  return value;
}
function add(name, answers, preferences, colors, colorAnalysis, spendingRanges) {
  const input = { answers, stylePreferences: preferences, colorPreferences: colors, colorAnalysis, spending_ranges: spendingRanges };
  const hashInput = { answers, stylePreferences: preferences || [], colorPreferences: colors || [], colorAnalysis: colorAnalysis || null, spendingRanges: spendingRanges || null };
  cases.push({ name, input, canonical: JSON.stringify(canonical(hashInput)), hash: digest(JSON.stringify(canonical(hashInput))),
    profile: mapQuizAnswersToProfile(answers, colorAnalysis, preferences || [], colors || [], 'Alex Élan', 'alex@example.test', 'verified-owner', spendingRanges || null) });
}
for (const gender of genders) {
  const answers = Object.fromEntries(fullQuizQuestions(gender).map(q => [q.id, q.id === 'gender' ? gender : q.options[0]]));
  answers.skin_tone = 'skin_tone_43';
  add(`full-${gender}`, answers, ['Minimalist'], ['navy', 'cream', 'tan', 'green', 'blue', 'black', 'gray', 'red', 'white', 'purple'], { colorCounts: { navy: 3, cream: 1 }, likedStyles: ['Minimalist'], topColors: ['navy'] }, { tops: '$100-$250', pants: '$0-$100', shoes: '$250-$500' });
}
for (const activity of activities) for (const element of elements) for (const preference of styles) {
  add(`scores-${activity}-${element}-${preference.join(',')}`, { gender: 'Male', daily_activities: activity, style_elements: element }, preference, [], null, null);
}
for (const skin_tone of ['skin_tone_0', 'skin_tone_00', 'skin_tone_9', 'skin_tone_99', 'skin_tone_100', 'skin_tone_101', 'warm', '']) {
  add(`skin-${skin_tone}`, { skin_tone, height: '', weight: '', shoe_size: 'Prefer not to say' }, [], [], { palette: { primary: ['navy', '', 'cream', 'navy'], secondary: ['tan', 'green', 'blue'], accents: ['red', 'pink', 'gray'] } }, {});
}
add('nested-hash-js-serialization', { gender: 'Male', '10': 'ten', '2': 'two', '𐀀': 'astral', '': 'bmp' }, [], [], {
  z: [-0, 1.0, 1e-7, 1e-6, 1e20, 1e21, 1.2345678901234567, 1000000000000000128],
  '10': 'ten', '2': 'two', '01': 'not-index', '4294967295': 'not-index', nested: { '𐀀': '😀', '': '\ud800', z: '\n\t\u0000', a: ['\u2028', '\u2029'] },
}, { tops: '£100–250', '10': 10, '2': 2 });
const fixture = { source_sha256: data.source_sha256, now_seconds: instant / 1000, required_question_ids: required, cases };
fs.writeFileSync(path.join(__dirname, 'quiz-profile-parity.json'), JSON.stringify(fixture, null, 2) + '\n');
console.log(JSON.stringify({ cases: cases.length, required_counts: Object.fromEntries(Object.entries(required).map(([k, v]) => [k, v.length])) }));
