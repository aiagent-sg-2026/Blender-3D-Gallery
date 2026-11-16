import fs from 'node:fs/promises';
import { validateBytes } from 'gltf-validator';

const variants = ['terra', 'sol', 'astra'];
const validatorPackage = JSON.parse(await fs.readFile('node_modules/gltf-validator/package.json', 'utf8'));
for (const variant of variants) {
  const root = `models/gjh-chibi-visitor/${variant}`;
  const id = `gjh-chibi-visitor-${variant}`;
  const bytes = await fs.readFile(`${root}/exports/${id}.glb`);
  const result = await validateBytes(new Uint8Array(bytes));
  const metadataPath = `${root}/metadata.json`;
  const metadata = JSON.parse(await fs.readFile(metadataPath, 'utf8'));
  metadata.validation = {
    errors: result.issues.numErrors,
    warnings: result.issues.numWarnings,
    validator: validatorPackage.version,
  };
  await fs.writeFile(metadataPath, `${JSON.stringify(metadata, null, 2)}\n`);
  console.log(`${variant}: ${bytes.length} bytes; ${result.issues.numErrors} errors; ${result.issues.numWarnings} warnings`);
  if (result.issues.numErrors || result.issues.numWarnings) {
    throw new Error(`Khronos glTF validation failed for ${variant}`);
  }
}
