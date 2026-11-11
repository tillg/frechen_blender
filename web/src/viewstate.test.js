// @vitest-environment happy-dom
import { beforeEach, describe, expect, it } from 'vitest';
import { initialQuery, remove, storageKey, write } from './viewstate.js';

describe('viewstate (the saved view per model entry)', () => {
  beforeEach(() => localStorage.clear());
  const key = storageKey('ofen', 'ofen');

  it('keys are prefixed frechenlehen:<page>:<entry>', () => {
    expect(storageKey('index', 'eg')).toBe('frechenlehen:index:eg');
    expect(key).toBe('frechenlehen:ofen:ofen');
  });

  it('URL query wins over storage', () => {
    write(localStorage, key, '?cam=1,2,3&at=0,0,0&look=mass');
    expect(initialQuery('?cam=5,5,5&at=1,1,1&look=full', localStorage, key)).toBe('?cam=5,5,5&at=1,1,1&look=full');
  });

  it('stored query used when the URL has none', () => {
    write(localStorage, key, '?cam=1,2,3&at=0,0,0&look=mass');
    expect(initialQuery('', localStorage, key)).toBe('?cam=1,2,3&at=0,0,0&look=mass');
  });

  it('a URL without view keys (only hires=on) takes the stored view and keeps its own keys', () => {
    write(localStorage, key, '?cam=1,2,3&at=0,0,0&p=2&cut=eg');
    expect(initialQuery('?hires=on', localStorage, key)).toBe('?cam=1,2,3&at=0,0,0&p=2&cut=eg&hires=on');
  });

  it('default when neither', () => {
    expect(initialQuery('', localStorage, key)).toBe('');
    expect(initialQuery('?hires=on', localStorage, key)).toBe('?hires=on');
  });

  it('reset removes the key', () => {
    write(localStorage, key, '?look=mass');
    remove(localStorage, key);
    expect(localStorage.getItem(key)).toBeNull();
    expect(initialQuery('', localStorage, key)).toBe('');
  });

  it('malformed view keys are dropped', () => {
    expect(initialQuery('?cam=abc&at=1,2&p=x&fov=abc&hires=on', localStorage, key)).toBe('?hires=on');
    write(localStorage, key, '?cam=1,2&p=x');
    expect(initialQuery('', localStorage, key)).toBe('');
    expect(initialQuery('?cam=1,2,3&at=0,0,0&p=2&fov=200', null, key)).toBe('?cam=1,2,3&at=0,0,0&p=2');
  });

  it('a malformed URL view falls back to the stored one', () => {
    write(localStorage, key, '?cam=1,2,3&at=0,0,0&look=mass');
    expect(initialQuery('?cam=abc', localStorage, key)).toBe('?cam=1,2,3&at=0,0,0&look=mass');
  });

  it('no storage (blocked in a private window) falls back to the default', () => {
    expect(() => write(null, key, '?look=mass')).not.toThrow();
    expect(() => remove(null, key)).not.toThrow();
    expect(initialQuery('', null, key)).toBe('');
    expect(initialQuery('?look=full', null, key)).toBe('?look=full');
  });
});
