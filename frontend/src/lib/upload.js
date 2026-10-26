// Mirrors the API's limits so people get feedback before a slow upload.
export const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
export const MAX_IMAGE_BYTES = 5 * 1024 * 1024;

export function validateImage(file) {
  if (!file) return 'Choose a photo to share.';
  if (!IMAGE_TYPES.includes(file.type)) return 'Use a JPG, PNG, WebP or GIF image.';
  if (file.size > MAX_IMAGE_BYTES) return 'That image is over 5 MB. Try a smaller one.';
  return null;
}
