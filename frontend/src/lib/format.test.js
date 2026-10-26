import { describe, expect, it } from 'vitest';
import { formatRelativeTime, plural } from './format';

describe('formatRelativeTime', () => {
  const now = new Date('2026-11-10T12:00:00Z');

  it.each([
    ['2026-11-10T11:59:30Z', 'just now'],
    ['2026-11-10T11:45:00Z', '15m'],
    ['2026-11-10T09:00:00Z', '3h'],
    ['2026-11-08T12:00:00Z', '2d'],
    ['2026-10-01T12:00:00Z', '1 Oct'],
  ])('%s -> %s', (date, expected) => {
    expect(formatRelativeTime(date, now)).toBe(expected);
  });
});

describe('plural', () => {
  it('only adds an s when needed', () => {
    expect(plural(1, 'like')).toBe('1 like');
    expect(plural(0, 'like')).toBe('0 likes');
  });
});
