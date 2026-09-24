/** @jest-environment node */

declare const expect: jest.Expect;
declare const it: jest.It;
declare const describe: jest.Describe;
declare const beforeAll: jest.Lifecycle;

import postcss, { type Root } from 'postcss';
import tailwindcss from 'tailwindcss';

const config = require('../../tailwind.config');

describe('image aspect-ratio CSS with the legacy plugin enabled', () => {
  let css: Root;

  beforeAll(async () => {
    const result = await postcss([
      tailwindcss({
        ...config,
        content: [{
          raw: 'aspect-auto aspect-square aspect-video aspect-w-1 aspect-h-1',
          extension: 'html',
        }],
      }),
    ]).process('@tailwind components; @tailwind utilities;', { from: undefined });
    css = result.root;
  });

  function declarations(selector: string) {
    const values: Record<string, string> = {};
    css.walkRules(selector, (rule) => {
      rule.walkDecls((declaration) => {
        values[declaration.prop] = declaration.value;
      });
    });
    return values;
  }

  it('emits native sizing for the named utilities used by image containers', () => {
    // A JSX class alone is insufficient: the plugin previously replaced these
    // theme keys, so production omitted the actual sizing declarations.
    expect(declarations('.aspect-auto')['aspect-ratio']).toBe('auto');
    expect(declarations('.aspect-square')['aspect-ratio']).toBe('1 / 1');
    expect(declarations('.aspect-video')['aspect-ratio']).toBe('16 / 9');
  });

  it('preserves the legacy plugin and its numeric ratio utilities', () => {
    expect(declarations('.aspect-w-1')).toMatchObject({
      position: 'relative',
      '--tw-aspect-w': '1',
    });
    expect(declarations('.aspect-h-1')['--tw-aspect-h']).toBe('1');
  });
});
