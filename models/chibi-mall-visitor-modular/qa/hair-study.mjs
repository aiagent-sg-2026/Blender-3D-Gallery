/* Match the pinned head-study camera. Store a secondary clay and pigment diagnostic
   for the actual exported surface alongside the normal material turn. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
const dir=path.resolve(process.argv[2]),reference=process.argv[3];
const sha=b=>createHash('sha256').update(b).digest('hex');
const glb=await fs.readFile(path.join(dir,'visitor.glb'));
const preview=await fs.readFile(path.join(dir,'preview.html'));
const embedded=preview.toString().match(/id="asset">([^<]+)<\/script>/);
if(!embedded||!glb.equals(Buffer.from(embedded[1],'base64')))throw Error('Unbound preview');
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const folder=path.join(dir,'qa');await fs.mkdir(folder,{recursive:true});
try{
  const page=await browser.newPage({viewport:{width:292,height:280},deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(dir,'preview.html')).href+'?qa=1');
  await page.addStyleTag({content:'main{display:block}aside{display:none}#stage{width:100vw;height:100vh}'});
  const angles=[0,-35,90,180,-90,-135,135,35];
  const records=[];
  for(const mode of ['material','clay','pigment','geometry-lighting']){
    const data=await page.evaluate(async({angles,mode})=>{
      const v=await window.visitorReady;
      const c=document.createElement('canvas');c.width=292*4;c.height=300*2;
      const ctx=c.getContext('2d');ctx.fillStyle='#f4f1f5';ctx.fillRect(0,0,c.width,c.height);
      const hair=v.meshes.find(m=>m.userData.partSlot==='Hair');const original=hair.material;
      let probe;
      if(mode==='clay')probe=new v.THREE.MeshStandardMaterial({color:0x87818a,roughness:.78});
      if(mode==='geometry-lighting'){probe=original.clone();probe.normalMap=null;probe.needsUpdate=true;}
      if(mode==='pigment')probe=new v.THREE.MeshBasicMaterial({map:original.map,toneMapped:false});
      if(probe)hair.material=probe;
      v.ground.visible=false;
      for(const [i,angle] of angles.entries()){
        v.view(angle,.61,1.055,0);v.draw();const x=i%4*292,y=Math.floor(i/4)*300;
        ctx.drawImage(v.renderer.domElement,x,y,292,280);ctx.fillStyle='#342d38';
        ctx.font='14px sans-serif';ctx.fillText(angle+'° · '+mode,x+7,y+295);
      }
      hair.material=original;probe?.dispose();return c.toDataURL();
    },{angles,mode});
    const file='hair-'+mode+'.png',bytes=Buffer.from(data.split(',')[1],'base64');
    await fs.writeFile(path.join(folder,file),bytes);records.push({file,sha256:sha(bytes),mode,angles,span:.61,height:1.055,pitch:0,viewport:[292,280]});
  }
  await fs.writeFile(path.join(folder,'hair-study.json'),JSON.stringify({artifactSha256:sha(glb),previewSha256:sha(preview),rendererSha256:sha(await fs.readFile(new URL('../preview/viewer.js',import.meta.url))),captureSha256:sha(await fs.readFile(new URL(import.meta.url))),referenceSha256:reference?sha(await fs.readFile(reference)):null,records},null,2)+'\n');
}finally{await browser.close();}
