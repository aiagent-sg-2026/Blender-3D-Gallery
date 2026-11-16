import test from'node:test';import assert from'node:assert/strict';import fs from'node:fs';import{execFileSync}from'node:child_process';
const p='models/passenger-lift/';
test('repaired passenger lift retains five exact clips, two separate modes and real swept clearances',()=>{
 execFileSync(process.execPath,[p+'validate.mjs'],{stdio:'pipe'});const r=JSON.parse(fs.readFileSync(p+'reports/mechanism.json'));
 assert.equal(r.triangles,7652);assert.equal(r.clips.length,5);assert.equal(r.modes_mutually_exclusive,true);assert.equal(r.sweep_samples_per_mode,121);
});
test('saved lift wall translation/material edit preserves every mesh payload and all clips',()=>{
 execFileSync(process.execPath,[p+'verify_source_edit.mjs'],{stdio:'pipe'});const r=JSON.parse(fs.readFileSync(p+'reports/source-edit-export-proof.json'));
 assert.equal(r.mesh_payloads_unchanged,80);assert.equal(r.five_clip_payloads_unchanged,true);assert.ok(Math.abs(r.glb_node_delta_x-.123)<1e-6);
});
test('current lift handoff manifest identifies the actual shipped files',async()=>{
 const{createHash}=await import('node:crypto');const rows=JSON.parse(fs.readFileSync(p+'reports/producer-handoff-manifest.json'));assert.ok(rows.length>0);
 for(const row of rows)assert.equal(createHash('sha256').update(fs.readFileSync(p+row.path)).digest('hex'),row.sha256,row.path);
});
