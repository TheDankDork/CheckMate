import sharp from 'sharp';
import { readFileSync, writeFileSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const logoPath = path.join(__dirname, '../public/logo.png');

const buffer = readFileSync(logoPath);
const trimmed = await sharp(buffer)
  .trim({ threshold: 15 })
  .toBuffer();

writeFileSync(logoPath, trimmed);
console.log('Logo trimmed and saved.');
