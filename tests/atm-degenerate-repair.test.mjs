import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{execFileSync}from'node:child_process';
const p='models/atm-kiosk/';
test('repaired ATM retains its actual service-door clip, endpoints and opening clearance',()=>{
 execFileSync(process.execPath,[p+'validate.mjs'],{stdio:'pipe'});const r=JSON.parse(fs.readFileSync(p+'reports/assets.json'));
 assert.equal(r.triangles,2452);assert.equal(r.primitives,15);assert.equal(r.animations,1);assert.match(r.animationTest,/PASS/);
});
test('ATM saved-source edit changes one mesh while preserving siblings and service-door animation',()=>{
 execFileSync(process.execPath,[p+'verify_source_edit.mjs'],{stdio:'pipe'});const r=JSON.parse(fs.readFileSync(p+'reports/source-edit-export-proof.json'));
 assert.equal(r.unchanged_sibling_meshes,14);assert.equal(r.exact_clip_payload_preserved,true);
});
