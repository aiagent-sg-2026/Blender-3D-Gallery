import fs from 'node:fs/promises';
const here=new URL('./',import.meta.url);
const base='https://yapweijun1996.github.io/Blender-3D-Gallery/';
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
for(;;){
 let state;try{state=JSON.parse(await fs.readFile(new URL('deployment-latest.json',here),'utf8'));}catch{await sleep(10000);continue;}
 if(state.status!=='completed'||state.superseded||state.awaitingReplacement){await sleep(10000);continue;}
 if(state.conclusion!=='success')throw new Error(`Deployment concluded ${state.conclusion}; live acceptance not started`);
 console.log('Deployment succeeded',state.headSha);break;
}
let ready=false;
for(let i=0;i<20;i++){
 try{
  const html=await fetch(base,{headers:{'Cache-Control':'no-cache'},signal:AbortSignal.timeout(20000)}).then(r=>r.text());
  const script=html.match(/<script[^>]*src="([^"]+)"/i)?.[1];
  if(script){const js=await fetch(new URL(script,base),{signal:AbortSignal.timeout(20000)}).then(r=>r.text());const viewer=js.match(/viewer-[A-Za-z0-9_-]+\.js/)?.[0];let cleanup=false;if(viewer){const code=await fetch(new URL(viewer,new URL(script,base)),{signal:AbortSignal.timeout(20000)}).then(r=>r.text());cleanup=code.includes('model viewer renderer is already in use');}ready=js.includes('fish-barramundi')&&js.includes('fish-tiger-barb')&&cleanup;}
  if(ready){console.log('Production catalog contains fish; starting 180 browser cases');break;}
 }catch(e){console.log('Propagation check',e.name);}
 await sleep(15000);
}
if(!ready)throw new Error('Deployment succeeded but the public catalog has not propagated');
delete process.env.FISH_QA_SMOKE;
await import('./test-live-swimming.mjs');
