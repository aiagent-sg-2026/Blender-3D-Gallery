import fs from 'node:fs';
import assert from 'node:assert/strict';
import {launchOptions} from '../../scripts/browser-test-utils.mjs';

// A native Chrome backend is optional for hosts whose bundled SwiftShader capture stalls.
const executablePath=process.env.FISH_CHROME_PATH;
const backend=process.env.FISH_WEBGL_BACKEND||'swiftshader';
assert.ok(['swiftshader','metal'].includes(backend),'Unsupported fish QA WebGL backend');
if(executablePath)assert.ok(fs.existsSync(executablePath),'Configured Chrome executable is missing');
export const fishLaunchOptions=executablePath?{headless:true,executablePath,args:[`--use-angle=${backend}`,'--enable-unsafe-swiftshader',...(backend==='metal'?['--ignore-gpu-blocklist']:[])]}:launchOptions;
export const fishBrowserRuntime={executable:executablePath||'Playwright bundled Chromium',backend:executablePath?backend:'swiftshader'};
