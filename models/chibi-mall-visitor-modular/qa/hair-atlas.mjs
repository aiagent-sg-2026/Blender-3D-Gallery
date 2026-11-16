// Two different pieces of hair cannot write different tangent normals to the
// same texel. Boundary contact between neighboring UV triangles is expected.
function componentReader(doc,bin,index,width){
  const a=doc.accessors[index],view=doc.bufferViews[a.bufferView];
  const types={5121:[1,'readUInt8',255],5123:[2,'readUInt16LE',65535],
    5125:[4,'readUInt32LE',4294967295],5126:[4,'readFloatLE',1]};
  const [bytes,read,limit]=types[a.componentType];
  const start=(view.byteOffset||0)+(a.byteOffset||0),stride=view.byteStride||bytes*width;
  return (i,k=0)=>bin[read](start+i*stride+k*bytes)/(a.normalized?limit:1);
}

const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);

function intersectionArea(first,second){
  let polygon=first;
  const orientation=Math.sign(cross(...second));
  for(let edge=0;edge<3&&polygon.length;edge++){
    const a=second[edge],b=second[(edge+1)%3],output=[];
    let prev=polygon.at(-1),previous=orientation*cross(a,b,prev);
    for(const pt of polygon){
      const value=orientation*cross(a,b,pt);
      if((value>0)!==(previous>0)){
        const t=previous/(previous-value);
        output.push([prev[0]+t*(pt[0]-prev[0]),prev[1]+t*(pt[1]-prev[1])]);
      }
      if(value>=0)output.push(pt);
      prev=pt;previous=value;
    }
    polygon=output;
  }
  let area=0;
  for(let i=1;i+1<polygon.length;i++)area+=cross(polygon[0],polygon[i],polygon[i+1]);
  return Math.abs(area)/2;
}

export function inspectHairAtlas(doc,bin){
  const triangles=[],cells=new Map();
  let inBounds=true,overlapPairs=0,maxOverlapPx2=0,occupiedArea=0;
  for(const node of doc.nodes.filter(n=>n.extras?.partSlot==='Hair')){
    for(const part of doc.meshes[node.mesh].primitives){
      const index=componentReader(doc,bin,part.indices,1);
      const uv=componentReader(doc,bin,part.attributes.TEXCOORD_0,2);
      for(let i=0;i<doc.accessors[part.indices].count;i+=3){
        const tri=[0,1,2].map(k=>[uv(index(i+k))*1024-512,uv(index(i+k),1)*1024]);
        if(tri.some(pt=>pt.some(v=>!Number.isFinite(v)||v<0||v>512))){inBounds=false;continue;}
        const area=Math.abs(cross(...tri))/2,id=triangles.length;
        triangles.push(tri);occupiedArea+=area;
        if(area<1e-8)continue;
        const bounds=[0,1].map(k=>tri.map(p=>Math.floor(p[k]/16)));
        const candidates=new Set();
        for(let x=Math.min(...bounds[0]);x<=Math.max(...bounds[0]);x++){
          for(let y=Math.min(...bounds[1]);y<=Math.max(...bounds[1]);y++){
            const key=x+33*y,cell=cells.get(key)||[];
            for(const j of cell)candidates.add(j);
            cell.push(id);cells.set(key,cell);
          }
        }
        for(const j of candidates){
          const overlap=intersectionArea(tri,triangles[j]);
          if(overlap>1e-5){overlapPairs++;maxOverlapPx2=Math.max(maxOverlapPx2,overlap);}
        }
      }
    }
  }
  return {triangles:triangles.length,inBounds,overlapPairs,maxOverlapPx2,
    coverageFraction:occupiedArea/512**2,pass:triangles.length>0&&inBounds&&overlapPairs===0};
}
