// Runtime adapters for the exported assembly; the original player stays unchanged.
export function prepareModules(T, R, physics, model, scene, mergeGeometries) {
  model.updateMatrixWorld(true);
  const roots = model.children.filter(o => o.userData.kind);
  const doors = roots.filter(o => o.userData.kind === 'door').sort((a,b)=>a.name.localeCompare(b.name));
  const ceilings = roots.filter(o => ['ceiling','collar'].includes(o.userData.kind));
  if (doors.length !== 2) throw Error('Expected two articulated doors');
  const pivots = [], moving = new Set(), doorColliders = [];
  for (const door of doors) {
    for (const side of ['Left','Right']) {
      let pivot;
      door.traverse(o => {if(o.name.startsWith('HINGE_'+side)) pivot=o;});
      if (!pivot) throw Error('Missing door hinge');
      pivots.push({pivot,sign:side==='Left'?-1:1});
      pivot.traverse(o=>{if(o.isMesh)moving.add(o);});
    }
  }
  function pose(object) {
    object.geometry.computeBoundingBox();
    const box=object.geometry.boundingBox,center=box.getCenter(new T.Vector3()).applyMatrix4(object.matrixWorld);
    const scale=new T.Vector3(),rotation=new T.Quaternion(),translation=new T.Vector3();
    object.matrixWorld.decompose(translation,rotation,scale);
    const half=box.getSize(new T.Vector3()).multiply(new T.Vector3(Math.abs(scale.x),Math.abs(scale.y),Math.abs(scale.z))).multiplyScalar(.5);
    return {center,rotation,half};
  }
  function collider(object) {
    const {center,rotation,half}=pose(object);
    return physics.createCollider(R.ColliderDesc.cuboid(half.x,half.y,half.z).setTranslation(center.x,center.y,center.z).setRotation(rotation));
  }
  function envelope(object) {
    const b=new T.Box3().setFromObject(object),c=b.getCenter(new T.Vector3()),h=b.getSize(new T.Vector3()).multiplyScalar(.5);
    physics.createCollider(R.ColliderDesc.cuboid(h.x,h.y,h.z).setTranslation(c.x,c.y,c.z));
  }
  for (const root of roots) {
    if (['ceiling','column','fascia210','fascia348'].includes(root.userData.kind)) envelope(root);
    else if (['door','partition','collar'].includes(root.userData.kind)) root.traverse(o=>{if(o.isMesh&&!moving.has(o))collider(o);});
  }
  let angle=0,player=null,transitionRejected=false;
  function apply(degrees) {
    for(const {pivot,sign} of pivots)pivot.rotation.y=sign*degrees*Math.PI/180;
    model.updateMatrixWorld(true);
  }
  function setDoors(degrees) {
    if (![0,90].includes(degrees)) throw Error('Door endpoints are 0 or 90 degrees');
    player?.clearInput();
    const previous=angle,step=degrees>=previous?1:-1;
    // No visual animation is claimed. Check the entire sampled sweep before an
    // instantaneous inspection-state change, including an occupied passage.
    if(player)for(let d=previous;;d+=step){
      apply(d);
      for(const object of moving){
        const {center,rotation,half}=pose(object);
        const hit=physics.intersectionWithShape(center,rotation,new R.Cuboid(half.x,half.y,half.z),undefined,undefined,undefined,undefined,c=>c.handle===player.capsule.handle);
        if(hit){apply(previous);transitionRejected=true;return false;}
      }
      if(d===degrees)break;
    }
    apply(degrees);
    for(const c of doorColliders)physics.removeCollider(c,true);
    doorColliders.length=0;
    for(const object of moving)doorColliders.push(collider(object));
    angle=degrees;transitionRejected=false;physics.step();
    return true;
  }
  setDoors(90);

  // Keep moving doors independent. Static glazing merges only within one
  // coplanar facade run; front/back visibility bands keep separate sorting layers.
  // Material opacity, sidedness and exported geometry remain unchanged.
  const groups=new Map(),batches=[];
  model.traverse(o=>{
    if(!o.isMesh||Array.isArray(o.material))return;
    let door=false,ceiling=false,partition=null;
    for(let p=o;p;p=p.parent){if(p.userData.kind==='door')door=true;if(['ceiling','collar'].includes(p.userData.kind))ceiling=true;if(p.userData.kind==='partition')partition=p;}
    if(door)return;
    if(o.material.transparent&&!partition)return;
    const layer=o.name.includes('_Front')?'front':o.name.includes('_Back')?'back':'pane';
    const run=partition?.name.replace(/_\d+$/,'');
    const key=o.material.uuid+ceiling+(o.material.transparent?run+layer:'');
    if(!groups.has(key))groups.set(key,{objects:[],ceiling});
    groups.get(key).objects.push(o);
  });
  for(const {objects,ceiling} of groups.values()){
    const geometries=objects.map(o=>{
      let g=o.geometry.clone().applyMatrix4(o.matrixWorld);
      if(g.index)g=g.toNonIndexed();
      for(const a of Object.keys(g.attributes))if(!['position','normal','uv'].includes(a))g.deleteAttribute(a);
      if(!g.attributes.normal)g.computeVertexNormals();
      if(!g.attributes.uv)g.setAttribute('uv',new T.BufferAttribute(new Float32Array(g.attributes.position.count*2),2));
      o.visible=false;return g;
    });
    const geometry=mergeGeometries(geometries);
    if(!geometry)throw Error('Static material batch failed');
    const mesh=new T.Mesh(geometry,objects[0].material);scene.add(mesh);batches.push({mesh,ceiling});
    for(const g of geometries)g.dispose();
  }
  return {
    bindPlayer(value){player=value;},setDoors,
    showCeilings(visible){for(const o of ceilings)o.visible=visible;for(const b of batches)if(b.ceiling)b.mesh.visible=visible;},
    get state(){return {angle,transitionRejected,doors:doors.length,staticBatches:batches.length,colliders:physics.colliders.len()};},
  };
}
