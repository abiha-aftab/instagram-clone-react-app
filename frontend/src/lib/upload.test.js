import { describe, expect, it } from 'vitest';
import { MAX_IMAGE_BYTES, validateImage } from './upload';

const fileOf = (type, size = 10) => new File([new Uint8Array(size)], 'f', { type });

describe('validateImage', () => {
  it('accepts a small png', () => {
    expect(validateImage(fileOf('image/png'))).toBeNull();
  });

  it('requires a file', () => {
    expect(validateImage(undefined)).toMatch(/choose a photo/i);
  });

  it('rejects other types', () => {
    expect(validateImage(fileOf('application/pdf'))).toMatch(/JPG, PNG/);
    expect(validateImage(fileOf('image/svg+xml'))).toMatch(/JPG, PNG/);
  });

  it('rejects files over 5 MB', () => {
    expect(validateImage(fileOf('image/jpeg', MAX_IMAGE_BYTES + 1))).toMatch(/over 5 MB/);
  });
});
