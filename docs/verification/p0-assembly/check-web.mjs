import {chromium} from 'playwright';
import fs from 'node:fs';
const dir=new URL('./',import.meta.url); const expected=JSON.parse(fs.readFileSync(new URL('measurements.json',dir)));
const browser=await chromium.launch({headless:true,args:['--use-gl=angle','--use-angle=swiftshader']});
const results=[];
for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
 const page=await browser.newPage({viewport,deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error') errors.push(m.text())});page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
 await page.goto(process.env.CORRIDOR_URL??'http://127.0.0.1:4173/docs/verification/p0-assembly/',{waitUntil:'networkidle'}); await page.waitForFunction(()=>document.querySelector('#status').dataset.ready,{timeout:30000});
 const result=await page.evaluate(()=>({ready:document.querySelector('#status').dataset.ready,status:document.querySelector('#status').textContent,fit:window.fitStudy,canvas:{width:document.querySelector('canvas').width,height:document.querySelector('canvas').height}}));
 await page.screenshot({path:new URL(`web-${viewport.width}.png`,dir).pathname});
 const before=await page.evaluate(()=>window.fitCamera.position.toArray());
 await page.mouse.move(viewport.width*.5,viewport.height*.5); await page.mouse.down(); await page.mouse.move(viewport.width*.65,viewport.height*.55,{steps:8}); await page.mouse.up(); await page.waitForTimeout(300);
 const after=await page.evaluate(()=>window.fitCamera.position.toArray()); result.orbitMoved=Math.hypot(...after.map((v,i)=>v-before[i]))>0.05;
 await page.getByRole('button',{name:'Underside',exact:true}).click(); await page.waitForTimeout(150);
 await page.screenshot({path:new URL(`web-underside-${viewport.width}.png`,dir).pathname});
 await page.getByRole('button',{name:'Column joint',exact:true}).click(); await page.waitForTimeout(150);
 await page.screenshot({path:new URL(`web-collar-${viewport.width}.png`,dir).pathname});
 result.viewsWorked=await page.evaluate(()=>window.fitCamera.position.y<1.01);
 let differences=[];
 if(result.fit){for(const exp of expected.objects){const b=result.fit.records[exp.name.replaceAll('.','')];if(!b){differences.push(`missing ${exp.name}`);continue} const mn=exp.bounds_min_blender_m,mx=exp.bounds_max_blender_m;const targetMin=[mn[0],mn[2],-mx[1]],targetMax=[mx[0],mx[2],-mn[1]];for(let j=0;j<3;j++)if(Math.abs(b.min[j]-targetMin[j])>0.002||Math.abs(b.max[j]-targetMax[j])>0.002)differences.push(`${exp.name} axis ${j}: ${b.min[j]},${b.max[j]} vs ${targetMin[j]},${targetMax[j]}`)}}
 results.push({viewport,...result,errors,differences}); await page.close();
}
await browser.close(); fs.writeFileSync(new URL('web-results.json',dir),JSON.stringify(results,null,2)+'\n');
for(const r of results)console.log(`${r.viewport.width}: ${r.status}; meshes ${r.fit?.meshCount}; bounds mismatches ${r.differences.length}; orbit ${r.orbitMoved}; errors ${r.errors.length}`,r.differences.slice(0,5),r.errors);
if(results.some(r=>r.ready!=='true'||!r.orbitMoved||!r.viewsWorked||r.errors.length||r.differences.length||!r.fit||Object.keys(r.fit.records).length!==expected.objects.length))process.exitCode=1;
