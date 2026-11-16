import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {rolldown} from 'rolldown';

// Bake the local preview into one file so double-click works offline, including textures.
const here=path.dirname(fileURLToPath(import.meta.url));
const [glb,out]=process.argv.slice(2);
const bundle=await rolldown({input:path.join(here,'viewer.js')});
const {output}=await bundle.generate({format:'iife',minify:true});
await bundle.close();
const script=output.find(o=>o.type==='chunk').code.replace(/<\/script/gi,'<\\/script');
const file=await fs.readFile(glb);
const license=await fs.readFile(path.resolve(here,'../../../node_modules/three/LICENSE'),'utf8');
const html=(await fs.readFile(path.join(here,'index.html'),'utf8'))
  .replace('</head>',()=>'<script type="text/plain" id="three-license">'+license+'</script></head>')
  .replace(/<script type="importmap">.*?<\/script>/s,'')
  .replace('<script type="module" src="./viewer.js"></script>',()=>'<script type="application/octet-stream" id="asset">'+file.toString('base64')+'</script><script>'+script+'</script>');
await fs.writeFile(out,html);

