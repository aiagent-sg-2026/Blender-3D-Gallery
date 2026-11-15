import test from 'node:test';
import assert from 'node:assert/strict';
import { Vector3 } from 'three';
import { loadBall,assertSphere,assertClothContact } from './helpers/ball-geometry-checks.mjs';

const directory=process.env.BALL_01_QA_ASSET_DIR||'models/eight-ball-billiards/exports',radius=.05715/2;
for(const file of ['ball_01.glb','billiards-scene.glb']){
  test(`${file}: Ball01 preserves its full-size yellow resin body`,async()=>{
    const {body,meshes}=await loadBall(file,1,directory);assert.equal(meshes.length,5);assertSphere(body,.23);
    const color=body.material.color;for(const [key,value] of [['r',.92],['g',.56],['b',.012]])assert.ok(Math.abs(color[key]-value)<1e-6);
  });
  test(`${file}: Ball01 has outward, close-fitting number marks on both sides`,async()=>{
    const {meshes}=await loadBall(file,1,directory),patches=meshes.filter(ob=>ob.name.includes('number_medallion')),glyphs=meshes.filter(ob=>ob.name.includes('numeral_1'));
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
  });
}
test('assembled Ball01 is tangent to the actual flat cloth surface',async()=>{
  const {gltf,body}=await loadBall('billiards-scene.glb',1,directory);assertClothContact(gltf,body);
});
