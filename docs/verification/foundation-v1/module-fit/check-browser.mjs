import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {chromium} from 'playwright';
import {serve,report} from '../qa-utils.mjs';

const here=path.dirname(new URL(import.meta.url).pathname);
const backend=process.env.FND_BROWSER_GPU||(process.platform==='darwin'?'metal':'swiftshader');
const server=await serve(path.resolve(here,'../../../..')),browser=await chromium.launch({headless:true,args:['--use-angle='+backend,...(backend==='swiftshader'?['--enable-unsafe-swiftshader']:[])]});
const rows=[],errors=[];let result;
const expectedHash=createHash('sha256').update(await fs.readFile(here+'/foundation-fitted.glb')).digest('hex');
async function drive(page,targets,tolerance=.12){
  return page.evaluate(({targets,tolerance})=>{
    const a=window.__whitebox,marks=[];
    for(const [x,z] of targets){
      let loops=0;
      while(Math.hypot(a.state.x-x,a.state.z-z)>tolerance&&loops++<180){
        const s=a.state,dx=x-s.x,dz=z-s.z,length=Math.hypot(dx,dz);
        const strength=Math.min(1,length/(2.65*.1));
        a.setInput({right:dx/length*strength,forward:-dz/length*strength,yaw:0});a.step(100);
      }
      a.setInput({right:0,forward:0});
      const s=a.state;marks.push({target:[x,z],x:s.x,y:s.y,z:s.z,zone:s.zone,camera:s.camera,drawCalls:s.drawCalls,error:Math.hypot(s.x-x,s.z-z)});
    }
    return marks;
  },{targets,tolerance});
}
try{
  for(const [width,height,touch] of [[1440,900,false],[768,1024,true],[390,844,true],[320,568,true],[667,375,true]]){
    const context=await browser.newContext({viewport:{width,height},hasTouch:touch,isMobile:touch,serviceWorkers:'block'});
    const page=await context.newPage();
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    await page.goto(server.url+'docs/verification/foundation-v1/module-fit/');
    await page.waitForFunction(()=>window.__whitebox?.ready||window.__whiteboxError,{},{timeout:60000});
    assert.equal(await page.evaluate(()=>window.__whiteboxError),undefined);
    assert.equal(await page.evaluate(()=>window.__whitebox.state.geometrySha256),expectedHash);
    const gpu=await page.evaluate(()=>{const g=document.querySelector('#scene').getContext('webgl2'),extension=g.getExtension('WEBGL_debug_renderer_info');return extension?g.getParameter(extension.UNMASKED_RENDERER_WEBGL):'unavailable';});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);
    await page.evaluate(()=>window.__whitebox.setInput({right:0,forward:0}));
    await page.screenshot({path:`${here}/screenshots/arrival-${width}.png`});
    const arrival=await page.evaluate(()=>window.__whitebox.state);
    assert.ok(arrival.modules.staticBatches>20&&arrival.modules.colliders>400);
    assert.ok(arrival.camera[2]-arrival.z>5);
    const walked=[];
    for(const target of [[0,13],[0,6],[0,0],[-6,0],[0,0],[6,0],[0,0],[0,6],[0,13],[0,18]]){
      const [mark]=await drive(page,[target]);walked.push(mark);
      assert.ok(mark.error<.14&&mark.zone!=='outside'&&Math.abs(mark.y)<.09,JSON.stringify(mark));
      assert.ok(mark.drawCalls<200,`Draw-call cap: ${mark.drawCalls}`);
      if([1440,390].includes(width)&&Math.abs(target[0])===6)await page.screenshot({path:`${here}/screenshots/store-${target[0]<0?'newmoon':'sample'}-${width}.png`});
    }
    const closed=[];
    for(const sign of [-1,1]){
      await page.evaluate(()=>window.__whitebox.reset());await drive(page,[[0,13],[0,0]]);
      assert.equal(await page.evaluate(()=>window.__whitebox.setDoors(0)),true);
      const state=await page.evaluate(sign=>{const a=window.__whitebox;a.setInput({right:sign,forward:0,yaw:0});a.step(2500);a.setInput({right:0,forward:0});return a.state;},sign);
      assert.ok(Math.abs(state.x)>1.8&&Math.abs(state.x)<2.12&&state.zone==='corridor');
      closed.push({side:sign,x:state.x,z:state.z});
      await page.evaluate(()=>window.__whitebox.reset());assert.equal(await page.evaluate(()=>window.__whitebox.setDoors(90)),true);
    }
    const offsets=[];
    if(width===1440){
      for(const sign of [-1,1])for(const offset of [.5,.7,1.3]){
        await page.evaluate(()=>window.__whitebox.reset());await drive(page,[[0,13],[0,0],[0,offset]],.005);
        const probe=await page.evaluate(({sign})=>{const a=window.__whitebox,start=a.state,path=[];a.setInput({right:sign,forward:0,yaw:0});for(let i=0;i<25;i++){a.step(100);const s=a.state;path.push({x:s.x,y:s.y,z:s.z});}a.setInput({right:0,forward:0});return {start,path,state:a.state};},{sign});
        const {state}=probe;
        if(offset===.5)assert.ok(Math.abs(state.x)>4);
        // Rapier legitimately slides a capsule around a leaf edge. A marginal
        // approach must either stop or be deflected towards the clear opening.
        if(offset===.7)assert.ok(Math.abs(state.x)<2.4||state.z<probe.start.z-.1,JSON.stringify(probe));
        if(offset===1.3)assert.ok(Math.abs(state.x)<2.4,'The adjacent fixed glazing must block entry');
        offsets.push({side:sign,requestedOffset:offset,startZ:probe.start.z,x:state.x,z:state.z,passed:Math.abs(state.x)>4,path:probe.path});
      }
    }
    await page.evaluate(()=>window.__whitebox.reset());await drive(page,[[0,13],[0,0],[2.4,0]]);
    assert.equal(await page.evaluate(()=>window.__whitebox.setDoors(0)),false,'Occupied door sweep must reject closing');
    const rejected=await page.evaluate(()=>window.__whitebox.state);
    assert.equal(rejected.modules.angle,90);assert.equal(rejected.modules.transitionRejected,true);
    if(width===1440)await page.screenshot({path:`${here}/screenshots/occupied-door.png`});
    await page.locator('#reset').click();
    const before=await page.evaluate(()=>window.__whitebox.state.z);
    if(touch){
      const cdp=await context.newCDPSession(page),r=await page.locator('#scene').boundingBox(),x=r.x+r.width*.3,y=r.y+r.height*.6;
      await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y,id:1}]});
      await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x,y:y-60,id:1}]});
      await page.waitForFunction(z=>window.__whitebox.state.z<z-.3,before);
      await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    }else{
      await page.locator('#scene').focus();await page.keyboard.down('w');await page.waitForFunction(z=>window.__whitebox.state.z<z-.4,before);await page.keyboard.up('w');
    }
    await page.evaluate(()=>window.__whitebox.setInput({right:0,forward:0}));
    await page.locator('#plan').click();
    const plan=await page.evaluate(()=>window.__whitebox.state);assert.equal(plan.view,'plan');assert.ok(plan.drawCalls<200,`Plan cap: ${plan.drawCalls}`);
    await page.screenshot({path:`${here}/screenshots/plan-${width}.png`});
    rows.push({viewport:{width,height},touchEmulated:touch,gpu,arrival,walked,closedDoors:closed,offsetPassageTests:offsets,occupiedSweepRejected:true,planDrawCalls:plan.drawCalls,overflow:false});
    console.log(`PASS ${width}px: real GLB, complete route, closed doors, occupied sweep, ${touch?'touch':'keyboard'} input, draw calls <200`);
    await context.close();
  }
  assert.deepEqual(errors,[]);
  result={status:'PASS',checkedAt:new Date().toISOString(),geometrySha256:expectedHash,browser:await browser.version(),backend,environment:'Pinned Three.js r170 / Rapier 0.21.0 and original v11 player, local HTTP, actual GPU strings recorded per viewport; touch is CDP emulation. Physical tests waived.',rows,errors};
}catch(error){result={status:'FAIL',rows,errors,error:error.message};throw error;}
finally{await report(here+'/reports/browser.json',result);await browser.close();await server.close();}
