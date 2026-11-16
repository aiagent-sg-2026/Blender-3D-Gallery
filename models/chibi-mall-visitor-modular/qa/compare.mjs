/* Compare immutable, artifact-bound captures at the same camera settings. */
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';

const [beforeFolder,afterFolder,referenceFile]=process.argv.slice(2);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');

async function captures(folder){
  const manifest=JSON.parse(await fs.readFile(path.join(folder,'qa/captures.json'),'utf8'));
  if(hash(await fs.readFile(path.join(folder,'visitor.glb')))!==manifest.artifactSha256){
    throw Error('The capture manifest belongs to a different GLB');
  }
  const artifacts=new Set([manifest.artifactSha256]);
  for(const item of manifest.artifacts??[]){
    const resolved=path.resolve(folder,item.file),root=path.resolve(folder)+path.sep;
    if(!resolved.startsWith(root)||hash(await fs.readFile(resolved))!==item.sha256){
      throw Error('Capture artifact binding failed');
    }
    artifacts.add(item.sha256);
  }
  for(const item of manifest.captures){
    if(path.basename(item.file)!==item.file)throw Error('Expected a capture filename');
    const bytes=await fs.readFile(path.join(folder,'qa',item.file));
    if(hash(bytes)!==item.sha256||!artifacts.has(item.artifactSha256)){
      throw Error('Unbound capture '+item.file);
    }
  }
  const encoded={};
  for(const name of ['head','reference-overlay']){
    if(manifest.captures.find(item=>item.file===name+'.png')?.artifactSha256!==manifest.artifactSha256){
      throw Error('Comparison requires primary-artifact captures');
    }
    encoded[name]=(await fs.readFile(path.join(folder,'qa',name+'.png'))).toString('base64');
  }
  return {manifest,encoded};
}

const before=await captures(beforeFolder);
const after=await captures(afterFolder);
const reference=await fs.readFile(referenceFile);
const referenceSha256=hash(reference);
if(before.manifest.rendererSourceSha256!==after.manifest.rendererSourceSha256){
  throw Error('Recapture both artifacts with the same renderer before comparing');
}
if([before,after].some(c=>c.manifest.referenceSha256!==referenceSha256)){
  throw Error('Capture/reference mismatch');
}
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage();
  const images=await page.evaluate(async({before,after,reference})=>{
    async function decode(base64){
      const image=new Image();image.src='data:image/png;base64,'+base64;
      await image.decode();return image;
    }
    const oldHead=await decode(before.head),newHead=await decode(after.head);
    const oldBody=await decode(before['reference-overlay']),newBody=await decode(after['reference-overlay']);
    const sheet=await decode(reference);
    const pad=16,column=320,gap=20,width=pad*2+column*3+gap*2;
    function canvas(height,title){
      const image=document.createElement('canvas');image.width=width;image.height=height;
      const ctx=image.getContext('2d');ctx.fillStyle='#f6f4f8';ctx.fillRect(0,0,width,height);
      ctx.fillStyle='#282431';ctx.font='600 24px sans-serif';ctx.fillText(title,pad,34);
      ctx.font='18px sans-serif';
      ['Reference','Before','After'].forEach((label,i)=>ctx.fillText(label,pad+i*(column+gap),70));
      return {image,ctx};
    }
    const body=canvas(616,'Visitor · reference and revision');
    body.ctx.drawImage(newBody,5,12,320,505,pad,88,320,505);
    body.ctx.drawImage(oldBody,335,12,320,505,pad+column+gap,88,320,505);
    body.ctx.drawImage(newBody,335,12,320,505,pad+2*(column+gap),88,320,505);
    const heads=canvas(1130,'Head · identical front, quarter and back cameras');
    const scale=(305/.64)*(1.3/451);
    const referenceTop=505-1.044/(1.3/451)-305/(2*scale);
    const sourceWidth=315/scale,sourceBottom=505-.724/(1.3/451);
    const rows=[
      {title:'Front',sourceX:339,sourceY:67,referenceCenter:390},
      {title:'Quarter',sourceX:666,sourceY:67,referenceCenter:157},
      {title:'Back',sourceX:666,sourceY:420,referenceCenter:1082}
    ];
    rows.forEach((row,i)=>{
      const top=110+i*340;
      heads.ctx.font='16px sans-serif';heads.ctx.fillStyle='#443d4d';
      heads.ctx.fillText(row.title,pad,top-9);
      // Exclude the sheet's title banner, which is outside the character crop.
      heads.ctx.drawImage(sheet,row.referenceCenter-sourceWidth/2,48,sourceWidth,sourceBottom-48,
        pad+2.5,top+(48-referenceTop)*scale,315,(sourceBottom-48)*scale);
      heads.ctx.drawImage(oldHead,row.sourceX,row.sourceY,315,305,pad+column+gap+2.5,top,315,305);
      heads.ctx.drawImage(newHead,row.sourceX,row.sourceY,315,305,pad+2*(column+gap)+2.5,top,315,305);
    });
    return {body:body.image.toDataURL(),heads:heads.image.toDataURL()};
  },{before:before.encoded,after:after.encoded,reference:reference.toString('base64')});
  const outputs={};
  for(const [name,key] of [['before-after','body'],['before-after-head','heads']]){
    const bytes=Buffer.from(images[key].split(',')[1],'base64');
    await fs.writeFile(path.join(afterFolder,'qa',name+'.png'),bytes);
    outputs[name+'.png']=hash(bytes);
  }
  await fs.writeFile(path.join(afterFolder,'qa/before-after.json'),JSON.stringify({
    beforeSha256:before.manifest.artifactSha256,afterSha256:after.manifest.artifactSha256,
    referenceSha256,rendererSourceSha256:after.manifest.rendererSourceSha256,
    sourceCaptureManifests:{before:hash(await fs.readFile(path.join(beforeFolder,'qa/captures.json'))),
      after:hash(await fs.readFile(path.join(afterFolder,'qa/captures.json')))},outputs,
    referenceCamera:'Approximate orthographic registration. Original reference projection is unknown.',
    expressionNote:'The revision keeps the explicitly requested closed default smile. The reference quarter view has an open smile.',
    operations:'Crops, uniform scaling and labels only; candidate images retain their captured camera and pose.'
  },null,2)+'\n');
  console.log('Bound before/after images written');
}finally{await browser.close();}
