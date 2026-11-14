// Preserve the original Pool Table QA entry point and evidence destination.
process.env.MODEL_QA_ID = 'pool-table';
process.env.MODEL_QA_OUTPUT ||= 'output/playwright/model-qa/MODEL-0001';
await import('./test-model-qa-browser.mjs');
