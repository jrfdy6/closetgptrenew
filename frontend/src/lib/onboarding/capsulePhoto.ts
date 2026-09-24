/** Hash the original bytes locally: duplicate checking must not upload a photo. */
export async function photoHash(file: File): Promise<string> {
  const bytes = await new Promise<ArrayBuffer>((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as ArrayBuffer);
    reader.onerror = () => reject(new Error('This photo could not be read. Choose it again.'));
    reader.readAsArrayBuffer(file);
  });
  const digest = await crypto.subtle.digest('SHA-256', bytes);
  return `sha256:${Array.from(new Uint8Array(digest)).map(byte => byte.toString(16).padStart(2, '0')).join('')}`;
}

/** Preserve JPEG/PNG/WebP originals; only convert formats browsers cannot decode. */
export async function prepareCapsulePhoto(file: File): Promise<File> {
  if (!/\.hei[cf]$/i.test(file.name) && !['image/heic', 'image/heif'].includes(file.type)) return file;
  try {
    const convert = (await import('heic2any')).default;
    const output = await convert({ blob: file, toType: 'image/jpeg', quality: 0.9 });
    const photo = Array.isArray(output) ? output[0] : output;
    if (!photo) throw new Error('No photo');
    return new File([photo], file.name.replace(/\.hei[cf]$/i, '.jpg'), { type: 'image/jpeg', lastModified: file.lastModified });
  } catch {
    throw new Error('This HEIC photo could not be read. Export it as JPEG or choose another photo.');
  }
}
