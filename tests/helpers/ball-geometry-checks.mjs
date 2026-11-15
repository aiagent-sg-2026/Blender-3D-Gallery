import assert from 'node:assert/strict';
import fs from 'node:fs';
import { Box3, Ray, Vector3 } from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

export async function loadBall(file, number, directory){
  const b=fs.readFileSync(`${directory}/${file}`);
  const gltf=await new GLTFLoader().parseAsync(b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),'');
  gltf.scene.updateMatrixWorld(true);
  const root=gltf.scene.getObjectByName(`ASSET_Ball_${String(number).padStart(2,'0')}`);assert.ok(root);
  const meshes=[];root.traverse(ob=>{if(ob.isMesh)meshes.push(ob);});
  const bodies=meshes.filter(ob=>ob.name.endsWith('resin'));assert.equal(bodies.length,1);
  return {gltf,root,meshes,body:bodies[0]};
}

export function assertSphere(body,roughness){
  const p=body.geometry.getAttribute('position'),n=body.geometry.getAttribute('normal'),radius=.05715/2;
  assert.equal(body.geometry.index.count/3,3968);
  for(let i=0;i<p.count;i++){
    const point=new Vector3().fromBufferAttribute(p,i),normal=new Vector3().fromBufferAttribute(n,i);
    assert.ok(Math.abs(point.length()-radius)<radius*1e-5,'Every vertex lies on the authored57.15mm sphere');
    assert.ok(Math.abs(normal.length()-1)<1e-5);
    // Half the authored64-longitude/32-latitude spacing bounds deviation.
    assert.ok(normal.dot(point.normalize())>Math.cos(Math.PI/64),'Smooth normals must follow the sphere');
  }
  assert.equal(body.material.metalness,0);assert.ok(Math.abs(body.material.roughness-roughness)<1e-6);
  assert.equal(body.material.opacity,1);assert.equal(body.material.transparent,false);
}

export function assertClothContact(gltf,body){
  const ball=new Box3().setFromObject(body);let cloth;
  gltf.scene.traverse(ob=>{if(ob.isMesh&&ob.name.includes('slate_and_green_cloth'))cloth=ob;});assert.ok(cloth);
  const center=ball.getCenter(new Vector3()),ray=new Ray(new Vector3(center.x,ball.max.y+1,center.z),new Vector3(0,-1,0)),p=cloth.geometry.getAttribute('position'),index=cloth.geometry.index,hits=[];
  for(let k=0;k<index.count;k+=3){const v=[0,1,2].map(j=>new Vector3().fromBufferAttribute(p,index.getX(k+j)).applyMatrix4(cloth.matrixWorld));const hit=ray.intersectTriangle(...v,false,new Vector3());if(hit)hits.push(hit.y);}
  assert.ok(hits.length,'A real cloth triangle supports the ball');const gap=ball.min.y-Math.max(...hits);
  assert.ok(Math.abs(gap)<1e-6,`Spherical bottom must be tangent to cloth, got ${gap}m`);
}

export function assertNumberMarks(meshes,number){
  const radius=.05715/2;
  const patches=meshes.filter(ob=>ob.name.includes('number_medallion')),glyphs=meshes.filter(ob=>ob.name.includes(`numeral_${number}`));
  assert.equal(patches.length,2);assert.equal(glyphs.length,2);
  for(const group of [patches,glyphs]){
    assert.equal(group.filter(ob=>ob.name.includes('opposite')).length,1);
    const sides=[];
    for(const ob of group){
      const glyph=group===glyphs,p=ob.geometry.getAttribute('position'),n=ob.geometry.getAttribute('normal'),index=ob.geometry.index;
      const expected=radius+(glyph ? .00009 : .00005),sign=Math.sign(p.getX(0));assert.ok(sign!==0);sides.push(sign);
      for(let i=0;i<p.count;i++){
        const point=new Vector3().fromBufferAttribute(p,i),normal=new Vector3().fromBufferAttribute(n,i);
        assert.ok(Math.abs(point.length()-expected)<radius*1e-5,'Marks follow the declared spherical layer');assert.equal(Math.sign(point.x),sign);
        assert.ok(Math.hypot(point.y,point.z)<=.0095+1e-7,'Mark stays within the medallion footprint');
        assert.ok(Math.abs(normal.length()-1)<1e-5&&normal.dot(point)>0,'Mark normals face outwards');
      }
      for(let k=0;k<index.count;k+=3){const v=[0,1,2].map(j=>new Vector3().fromBufferAttribute(p,index.getX(k+j)));const cross=v[1].clone().sub(v[0]).cross(v[2].clone().sub(v[0]));assert.ok(cross.lengthSq()>0&&cross.dot(v[0].clone().add(v[1]).add(v[2]))>0,'Decorative triangles have nondegenerate outward winding');}
      assert.equal(ob.material.opacity,1);assert.equal(ob.material.metalness,0);
    }
    assert.deepEqual(sides.sort(),[-1,1]);
  }
}
