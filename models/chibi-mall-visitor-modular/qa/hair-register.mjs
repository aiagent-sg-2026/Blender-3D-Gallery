/* Orthographic measurements of the exported hair in reference-sheet coordinates. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
const dir=path.resolve(process.argv[2]),ref=process.argv[3];
const sha=b=>createHash('sha256').update(b).digest('hex');
const glb=await fs.readFile(path.join(dir,'visitor.glb')),html=await fs.readFile(path.join(dir,'preview.html'));
if(!glb.equals(Buffer.from(html.toString().match(/id="asset">([^<]+)<\/script>/)[1],'base64')))throw Error('Export/preview differ');
const target=path.join(dir,'qa','registration');await fs.mkdir(target,{recursive:true});
const browser=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
try{
  const page=await browser.newPage({viewport:{width:480,height:416},deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(dir,'preview.html')).href+'?qa=1');
  await page.addStyleTag({content:'main{display:block}aside{display:none}#stage{width:100vw;height:100vh}'});
  const views=[['front',0,390.5],['profile',90,856.5],['back',180,1080.5],['quarter',-28,145],['opposite',-90,856.5]];
  const files={};
  for(const [name,angle] of views){
    const sets=await page.evaluate(async(angle)=>{
      const v=await window.visitorReady,T=v.THREE;
      v.motion('');v.face('default');v.ground.visible=false;v.view(angle,208/(451/1.3),(505-153)/(451/1.3),0);v.draw();
      const rgb=v.renderer.domElement.toDataURL();const source=new Map(v.meshes.map(m=>[m,m.material]));
      const hair=v.meshes.find(m=>m.userData.partSlot==='Hair');const bg=v.scene.background;
      const black=new T.MeshBasicMaterial({color:0x000000,toneMapped:false,side:T.DoubleSide});
      const white=new T.MeshBasicMaterial({color:0xffffff,toneMapped:false,side:T.DoubleSide});
      for(const m of v.meshes)m.material=m===hair?white:black;
      v.scene.background=new T.Color(0);v.draw();
      const mask=v.renderer.domElement.toDataURL();
      const lookup=new T.ShaderMaterial({side:T.DoubleSide,toneMapped:false,vertexShader:
        'varying vec2 chart;void main(){chart=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
        fragmentShader:'varying vec2 chart;void main(){float x=clamp(floor(chart.x*1024.0)-512.0,0.,511.);float y=clamp(floor(chart.y*1024.0),0.,511.);float q=1.+x+512.*y;gl_FragColor=vec4(mod(q,256.),mod(floor(q/256.),256.),floor(q/65536.),255.)/255.;}'});
      hair.material=lookup;v.draw();const uv=v.renderer.domElement.toDataURL();
      for(const [m,old] of source)m.material=old;
      v.scene.background=bg;black.dispose();white.dispose();lookup.dispose();
      return {rgb,mask,uv};
    },angle);
    for(const [kind,url] of Object.entries(sets)){
      const file=name+'-'+kind+'.png',bytes=Buffer.from(url.split(',')[1],'base64');
      await fs.writeFile(path.join(target,file),bytes);files[file]=sha(bytes);
    }
  }
  const rendererSourceSha256=sha(await fs.readFile(new URL('../preview/viewer.js',import.meta.url)));
  await fs.writeFile(path.join(target,'manifest.json'),JSON.stringify({artifactSha256:sha(glb),previewSha256:sha(html),referenceSha256:sha(await fs.readFile(ref)),captureSha256:sha(await fs.readFile(new URL(import.meta.url))),rendererSourceSha256,viewport:[480,416],pixelsPerReferencePixel:2,referenceRowAtTop:49,viewCenterY:153,views,files},null,2)+'\n');
}finally{await browser.close();}
