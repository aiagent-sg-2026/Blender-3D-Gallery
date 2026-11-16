/** Runs inside Chromium against Three.js geometry after skin and morph evaluation. */
export function inspectRuntime(){
  return v.measure(()=>{
  const {THREE,model,meshes,bones,clips,presets,contracts}=v;
  const expectedClips='idle walk run talk browse sit wave pick_up inspect point nod cheer'.split(' ');
  const expectedFaces='default happy wink surprised thinking excited'.split(' ');
  const group=s=>meshes.filter(m=>m.userData.partSlot===s);
  const byName=n=>model.getObjectByName(n) || bones.find(b=>b.userData.name===n||b.name===n.replaceAll('.',''));
  const point=(m,i)=>m.getVertexPosition(i,new THREE.Vector3()).applyMatrix4(m.matrixWorld);
  function points(objects){return objects.flatMap(o=>Array.from({length:o.geometry.attributes.position.count},(_,i)=>point(o,i)));}
  const axis=(p,k)=>p.map(q=>q[k]);
  const range=nums=>[Math.min(...nums),Math.max(...nums)];
  const extent=(p,k)=>range(axis(p,k));
  const dist=(a,b)=>a.distanceTo(b);
  const pick=n=>byName(n).getWorldPosition(new THREE.Vector3());
  const values=o=>o.morphTargetInfluences??[];
  v.slot('Hair',true);v.slot('Watch',true);v.slot('Backpack',true);v.grey(false);v.face('default');v.motion('');
  const rest=points(meshes);const [ground,top]=extent(rest,'y');
  const face=byName('Face'),eyes=byName('Iris_and_sclera'),tee=byName('Crewneck_shirt'),hand=byName('Hand_R');
  const facePts=points([face]),eyePts=points([eyes]);
  const eyeHeight=arr=>{const [a,b]=extent(arr,'y');return b-a;};
  const openHeight=eyeHeight(eyePts.filter(p=>p.x>0));
  const candidates=points([tee]).filter(q=>q.y<.475&&Math.abs(q.x)<.045&&q.z>.06);
  const landmark={eye:extent(eyePts,'y').reduce((a,b)=>a+b)/2,chin:Math.min(...axis(facePts,'y')),
    hem:Math.min(...axis(candidates,'y'))};
  const landmarkPx={};
  for(const [k,row] of Object.entries({eye:173,chin:228,hem:349})){
    landmarkPx[k]=Math.abs(505-451*(landmark[k]-ground)/(top-ground)-row);
  }
  const denim=byName('Straight_denim'),restDenim=points([denim]);
  const handRest=points([hand]);const refTip=new THREE.Vector3(-.205,.382,.056);
  const tipIndex=handRest.reduce((best,q,i)=>dist(q,refTip)<dist(handRest[best],refTip)?i:best,0);
  const faceGeometry=face.geometry;
  const signatures={},blinks={};
  for(const name of expectedFaces){
    v.face(name);
    signatures[name]=meshes.flatMap(values).map(n=>Math.round(n*100)).join(',');
    const p=points([eyes]);
    blinks[name]=[eyeHeight(p.filter(q=>q.x>0)),eyeHeight(p.filter(q=>q.x<0))];
  }
  v.face('thinking');
  const tip=point(hand,tipIndex);const fv=points([face]);let chinDistance=10;
  const indices=faceGeometry.index.array;const tri=new THREE.Triangle(),closest=new THREE.Vector3();
  for(let i=0;i<indices.length;i+=3){
    const [a,b,c]=[fv[indices[i]],fv[indices[i+1]],fv[indices[i+2]]];
    if(Math.max(a.y,b.y,c.y)>.895||Math.max(a.z,b.z,c.z)<.05)continue;
    chinDistance=Math.min(chinDistance,dist(tri.set(a,b,c).closestPointToPoint(tip,closest),tip));
  }
  v.face('default');
  const poses={},seams={},accessoryStates={};
  for(const name of expectedClips){
    const clip=clips.get(name);
    if(!clip)continue;
    const perClip=[];
    for(const t of [0,.21,.43,.64,.83,1]){
      v.sample(name,t*contracts[name].frames);
      perClip.push([...bones.flatMap(b=>b.quaternion.toArray()),...meshes.flatMap(values)]);
    }
    poses[name]={seconds:clip.duration,tracks:clip.tracks.length,
      delta:Math.max(...perClip.slice(1).map(s=>Math.max(...s.map((x,i)=>Math.abs(x-perClip[0][i])))))};
    if(contracts[name].loop){
      let diff=0;
      for(const track of clip.tracks){
        const size=track.getValueSize(),seq=track.values;
        const q=seq.slice(0,size),end=seq.slice(-size);
        let d=Math.max(...q.map((a,i)=>Math.abs(a-end[i])));
        if(track.name.endsWith('.quaternion'))d=Math.min(d,Math.max(...q.map((a,i)=>Math.abs(a+end[i]))));
        diff=Math.max(diff,d);
      }
      seams[name]=diff;
    }
  }
  for(const bag of [true,false]){
    for(const watch of [true,false]){
      v.slot('Backpack',bag);v.slot('Watch',watch);
      const checked=[];
      for(const name of expectedClips){
        v.sample(name,contracts[name].reviewFrame);
        checked.push(group('Backpack').every(o=>o.visible===bag)&&group('Watch').every(o=>o.visible===watch)
          &&group('Shirt').every(o=>o.visible)&&bones.every(b=>b.matrixWorld.elements.every(Number.isFinite)));
      }
      accessoryStates['pack-'+bag+'_watch-'+watch]=checked.filter(Boolean).length;
    }
  }
  v.slot('Backpack',true);v.slot('Watch',true);
  const gait={};
  for(const name of ['walk','run']){
    const {frames,fps,stanceFraction,speedMps}=contracts[name];
    let maxPlantError=0,maxSlide=0,minShoe=10;
    for(const side of ['L','R']){
      let first=null;
      for(let i=0;i<=frames;i++){
        const phase=(i/frames+(side==='R'?.5:0))%1;
        v.sample(name,i);
        const foot=pick('foot.'+side);
        const min=Math.min(...axis(points([byName('Sneaker_'+side)]),'y'));
        minShoe=Math.min(minShoe,min);
        if(phase<stanceFraction && (i===0||phase>.001)){
          maxPlantError=Math.max(maxPlantError,Math.abs(min));
          const world=foot.z+i/fps*speedMps;
          if(first===null)first=world;else maxSlide=Math.max(maxSlide,Math.abs(world-first));
        }else first=null;
      }
    }
    gait[name]={maxPlantErrorM:maxPlantError,maxSlideM:maxSlide,lowestShoeM:minShoe};
  }
  v.sample('pick_up',contracts.pick_up.contactFrame);
  const contact=pick('Socket_Palm_R'),target=new THREE.Vector3(...contracts.pick_up.target);
  const gripContactError=dist(contact,target);
  const halfProduct=new THREE.Vector3(...contracts.pick_up.testProductSizeM).multiplyScalar(.5);
  const fingers=points([hand]).map(p=>p.sub(target));
  const deepestPickupVertexM=Math.max(0,...fingers.map(p=>
    Math.min(...['x','y','z'].map(a=>halfProduct[a]-Math.abs(p[a])))));
  function intersectsProduct(triangle){
    let polygon=triangle;
    for(const axis of ['x','y','z'])for(const sign of [-1,1]){
      if(!polygon.length)return false;
      const clipped=[];
      let prev=polygon.at(-1),previous=halfProduct[axis]-1e-7-sign*prev[axis];
      for(const pt of polygon){
        const value=halfProduct[axis]-1e-7-sign*pt[axis];
        if((value>=0)!==(previous>=0))clipped.push(prev.clone().lerp(pt,previous/(previous-value)));
        if(value>=0)clipped.push(pt);
        prev=pt;previous=value;
      }
      polygon=clipped;
    }
    return polygon.length>=3;
  }
  const handIndices=hand.geometry.index.array;
  function intersectingFaces(pos){
    let count=0;
    for(let i=0;i<handIndices.length;i+=3){
      if(intersectsProduct([pos[handIndices[i]],pos[handIndices[i+1]],pos[handIndices[i+2]]]))count++;
    }
    return count;
  }
  const penetratingPickupTriangles=intersectingFaces(fingers);
  function faceGap(restPad,axis,sign){
    const insideFace=p=>['x','y','z'].every(a=>a===axis||Math.abs(p[a])<=halfProduct[a]+.001);
    const pad=fingers.filter((p,i)=>restPad(handRest[i])&&insideFace(p));
    return pad.length?Math.min(...pad.map(p=>Math.abs(sign*p[axis]-halfProduct[axis]))):null;
  }
  // Tests three anatomically distinct contact patches against three actual
  // box faces. The socket can be perfectly aligned even on the wrist.
  const pickupPadGapM={
    thumb:faceGap(p=>p.y<.412&&p.x>-.19,'x',1),
    index:faceGap(p=>p.y<.396&&p.z>.047&&p.x<-.19,'z',1),
    lowerFingers:faceGap(p=>p.y<.383&&p.x<-.215,'y',-1)
  };
  const productAtContact=new THREE.Matrix4().makeTranslation(...contracts.pick_up.target);
  const palmSocket=byName(contracts.pick_up.contactSocket);
  const socketToProduct=palmSocket.matrixWorld.clone().invert().multiply(productAtContact);
  const pickupSweep={stepFrames:.5,samples:0,intersectingSamples:0,maxIntersectingFaces:0};
  for(let frame=0;frame<=contracts.pick_up.frames;frame+=pickupSweep.stepFrames){
    v.sample('pick_up',frame);
    const box=frame>contracts.pick_up.contactFrame?palmSocket.matrixWorld.clone().multiply(socketToProduct):productAtContact;
    const local=box.clone().invert(),count=intersectingFaces(points([hand]).map(p=>p.applyMatrix4(local)));
    pickupSweep.samples++;
    if(count)pickupSweep.intersectingSamples++;
    pickupSweep.maxIntersectingFaces=Math.max(pickupSweep.maxIntersectingFaces,count);
  }
  v.sample('sit',contracts.sit.frames);
  const sitPelvis=pick('pelvis').y;
  const seat=contracts.sit;
  const seatPoints=points([denim]).filter((p,i)=>restDenim[i].y>.31&&Math.abs(p.x)<.17&&Math.abs(p.z-seat.seatCenterZ)<seat.seatDepthM/2);
  const seatGap=Math.min(...axis(seatPoints,'y'))-seat.seatHeightM;
  v.face('wink');v.sample('wave',contracts.wave.reviewFrame);
  const combined=eyes.morphTargetInfluences[eyes.morphTargetDictionary.blink_L]>.99 &&
     Math.abs(byName('upperarm.L').quaternion.angleTo(new THREE.Quaternion()))>.1;
  v.face('default');v.sample('talk',11);
  const talkMouth=face.morphTargetInfluences[face.morphTargetDictionary.open];
  v.sample('point',contracts.point.reviewFrame);
  const pointKey=hand.morphTargetInfluences[hand.morphTargetDictionary.point_R];
  v.motion('');v.face('default');v.view();v.draw();
  const matches=(iterable,expected)=>[...iterable].sort().join('|')===[...expected].sort().join('|');
  const scalpRays=[];
  const ray=new THREE.Raycaster();
  for(const y of [1.14,1.175,1.205,1.23,1.25])for(const x of [-.077,-.033,0,.041,.075]){
    ray.set(new THREE.Vector3(x,y,-1),new THREE.Vector3(0,0,1));
    const hit=ray.intersectObjects(meshes,false)[0];scalpRays.push(hit?.object.userData.partSlot);
  }
  const checks={rearHair:scalpRays.every(s=>s==='Hair'),clips:matches(clips.keys(),expectedClips),faces:matches(Object.keys(presets),expectedFaces),
    height:Math.abs(top-ground-1.30)<=.01,ground:Math.abs(ground)<=.002,landmarks:Object.values(landmarkPx).every(x=>x<=9),
    skin:bones.length===20&&meshes.every(m=>m.isSkinnedMesh),sockets:['Socket_Palm_R','Socket_Palm_L','Socket_Wrist_L','Socket_Back'].every(n=>!!byName(n)),
    expressions:new Set(Object.values(signatures)).size===6,
    eyelids:blinks.wink[0]<.27*openHeight&&blinks.wink[1]>.92*openHeight&&blinks.happy.every(x=>x<.28*openHeight),
    motion:expectedClips.every(n=>poses[n]?.delta>.01),loops:Object.keys(seams).length===5&&Object.values(seams).every(x=>x<.0015),
    modular:Object.values(accessoryStates).every(x=>x===12),contacts:Object.values(gait).every(g=>g.maxPlantErrorM<.004&&g.maxSlideM<.008&&g.lowestShoeM>-.004),
    pickup:gripContactError<.009&&pickupSweep.intersectingSamples===0&&penetratingPickupTriangles===0&&deepestPickupVertexM<1e-7&&Object.values(pickupPadGapM).every(d=>d!==null&&d<.004),
    chin:chinDistance<.015,sit:sitPelvis<.27&&sitPelvis>.18&&seatGap>-.004&&seatGap<.008,
    combined,talk:talkMouth>.10,point:pointKey>.75};
  return {checks,rearScalpHairHits:scalpRays.filter(x=>x==='Hair').length,heightM:top-ground,soleM:ground,landmarkM:landmark,landmarkOffsetPx:landmarkPx,poses,seamDelta:seams,
    eyeHeightsM:blinks,accessoryStates,gait,pickupErrorM:gripContactError,pickupPalm:contact.toArray(),pickupPadGapM,deepestPickupVertexM,penetratingPickupTriangles,pickupSweep,chinErrorM:chinDistance,
    chinTip:tip.toArray(),seatedPelvisM:sitPelvis,seatContactGapM:seatGap,talkMouth,pointKey,drawCalls: v.renderer.info.render.calls};
  });
}

