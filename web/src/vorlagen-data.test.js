import { describe, expect, it } from 'vitest';
import { pageUrl, pickBereich } from './vorlagen-data.js';

const M = { bereiche: [{ key: 'stube', title: 'Stube' }, { key: 'garderobe', title: 'Garderobe & Gäste-WC' }] };

describe('Vorlagen pages', () => {
  it('pageUrl: relative, the index without a key', () => {
    expect(pageUrl('stube')).toBe('vorlagen.html?b=stube');
    expect(pageUrl()).toBe('vorlagen.html');
  });
  it('pickBereich: ?b=<key>, else null (index)', () => {
    expect(pickBereich(M, '?b=garderobe').title).toBe('Garderobe & Gäste-WC');
    expect(pickBereich(M, '')).toBe(null);
    expect(pickBereich(M, '?b=nix')).toBe(null);
  });
});

