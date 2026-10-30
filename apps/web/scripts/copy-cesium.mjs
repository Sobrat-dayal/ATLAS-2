import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const appWebDir = path.resolve(__dirname, '..');
const possibleSources = [
  path.join(appWebDir, 'node_modules', 'cesium', 'Build', 'Cesium'),
  path.join(appWebDir, '..', '..', 'node_modules', 'cesium', 'Build', 'Cesium'),
];

let sourceDir = null;
for (const p of possibleSources) {
  if (fs.existsSync(p)) {
    sourceDir = p;
    break;
  }
}

if (!sourceDir) {
  console.warn('[copy-cesium] Warning: Cesium build directory not found. Skipping asset copy.');
  process.exit(0);
}

const targetDir = path.join(appWebDir, 'public', 'cesium');
fs.mkdirSync(targetDir, { recursive: true });

const foldersToCopy = ['Workers', 'ThirdParty', 'Assets', 'Widgets'];

for (const folder of foldersToCopy) {
  const src = path.join(sourceDir, folder);
  const dest = path.join(targetDir, folder);
  if (fs.existsSync(src)) {
    fs.cpSync(src, dest, { recursive: true });
    console.log(`[copy-cesium] Copied ${folder} -> ${dest}`);
  } else {
    console.warn(`[copy-cesium] Folder not found: ${src}`);
  }
}

console.log('[copy-cesium] Successfully copied Cesium assets to public/cesium.');

