import { describe, expect, it } from 'vitest';
import { dataBase, pick, versionHref, versionLabel } from './versions.js';

const LIST = [{ id: '2026-12-01', name: 'Später' }, { id: '2026-11-25', name: 'Nach Vincent & Silvia-Ideen' }];

describe('plan versions (#59)', () => {
  it('picks the version of ?v=, else Aktuell (null)', () => {
    expect(pick(LIST, '?cam=1,2,3&v=2026-11-25')).toBe(LIST[1]);
    expect(pick(LIST, '?cam=1,2,3')).toBeNull();
    expect(pick(LIST, '?v=1999-01-01')).toBeNull();                 // unknown id: Aktuell
    expect(pick([], '?v=2026-11-25')).toBeNull();
  });

  it('takes a version\'s files from v/<id>/, Aktuell\'s from the base', () => {
    expect(dataBase('/frechen_blender/', LIST[1])).toBe('/frechen_blender/v/2026-11-25/');
    expect(dataBase('/', null)).toBe('/');
  });

  it('sets or removes v and keeps the rest of the query as it is', () => {
    expect(versionHref('?cam=1,2,3&at=4,5,6&p=4', '2026-11-25')).toBe('?cam=1,2,3&at=4,5,6&p=4&v=2026-11-25');
    expect(versionHref('?cam=1,2,3&v=2026-11-25', '2026-12-01')).toBe('?cam=1,2,3&v=2026-12-01');
    expect(versionHref('?cam=1,2,3&v=2026-11-25', null)).toBe('?cam=1,2,3');
    expect(versionHref('?v=2026-11-25', null)).toBe('');
    expect(versionHref('', '2026-11-25')).toBe('?v=2026-11-25');
  });

  it('labels a version by date and name', () => {
    expect(versionLabel(LIST[1])).toBe('2026-11-25 Nach Vincent & Silvia-Ideen');
  });
});
