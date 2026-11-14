import * as THREE from 'three';
export const cleanHeader = value => String(value).replace(/[\u0000-\u001f\u007f]/g, '').trim().slice(0,32);
export function createShelfParts(model, makeCanvas = () => document.createElement('canvas')) {
 const meshes=name=>{const found=[];model.getObjectByName(name)?.traverse(o=>{if(o.isMesh)found.push(o);});if(!found.length)throw new Error(`Missing shelf part: ${name}`);return found;};
 const shelves=[1,2,3].map(n=>meshes(`shelf_${n}`)),leds=['LED_1','LED_2','LED_3','LED_header','LED_base'].flatMap(meshes),header=meshes('brand_header_panel')[0],originals=new Map();
 for(const mesh of new Set([...shelves.flat(),...leds])){originals.set(mesh,mesh.material);const clones=[].concat(mesh.material).map(m=>m.clone());mesh.material=Array.isArray(mesh.material)?clones:clones[0];}
 let overlay=null,disposed=false;
 const restore=(mesh,on)=>[].concat(mesh.material).forEach((m,i)=>{const old=[].concat(originals.get(mesh))[i];m.emissive?.copy(old.emissive);m.emissiveIntensity=on?old.emissiveIntensity:0;});
 const clear=()=>{if(!overlay)return;model.remove(overlay);overlay.geometry.dispose();overlay.material.map.dispose();overlay.material.dispose();overlay=null;};
 return {
 select(row){if(!disposed)shelves.forEach((list,i)=>list.forEach(mesh=>{restore(mesh,true);if(i+1===row)[].concat(mesh.material).forEach(m=>{m.emissive?.setHex(0x8a6729);m.emissiveIntensity=.65;});}));},
 light(on){if(!disposed)leds.forEach(mesh=>restore(mesh,on));},
 title(value){if(disposed)return;clear();const text=cleanHeader(value);if(!text)return;const canvas=makeCanvas();canvas.width=1024;canvas.height=256;const ctx=canvas.getContext('2d');if(!ctx)throw new Error('Label canvas unavailable');ctx.fillStyle='#183a30';ctx.fillRect(0,0,1024,256);ctx.fillStyle='#ead5a3';ctx.textAlign='center';ctx.textBaseline='middle';let size=96;do{ctx.font=`600 ${size}px sans-serif`;size-=2;}while(ctx.measureText(text).width>950&&size>26);ctx.fillText(text,512,128);
 const texture=new THREE.CanvasTexture(canvas);texture.colorSpace=THREE.SRGBColorSpace;model.updateMatrixWorld(true);const box=new THREE.Box3().setFromObject(header),dim=box.getSize(new THREE.Vector3()),pos=box.getCenter(new THREE.Vector3());pos.z=box.max.z+.004;overlay=new THREE.Mesh(new THREE.PlaneGeometry(dim.x*.97,dim.y*.9),new THREE.MeshBasicMaterial({map:texture,toneMapped:false}));overlay.name='RUNTIME_ReplaceableHeader';overlay.position.copy(model.worldToLocal(pos));model.add(overlay);},
 dispose(){if(disposed)return;disposed=true;clear();for(const[mesh,original]of originals){[].concat(mesh.material).forEach(m=>m.dispose());mesh.material=original;}originals.clear();}
 };
}
