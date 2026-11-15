"""Create lightweight posters and register this collection without replacing others.
Run after generate.py: uv run --with pillow python models/singapore-fish/register.py
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw
HERE=Path(__file__).resolve().parent
repo=HERE.parent.parent
specs=json.loads((HERE/'species.json').read_text())
assets=[]
sheet=Image.new('RGB',(1500,2100),'#10202c');draw=ImageDraw.Draw(sheet)
for i,(slug,cn,en,priority,kind,color,pattern,length) in enumerate(specs,1):
 p=HERE/slug;im=Image.open(p/'previews/hero.png');im.resize((400,300)).save(p/'previews/thumbnail.webp',quality=85)
 thumb=im.copy();thumb.thumbnail((250,187));x=((i-1)%6)*250;y=((i-1)//6)*210;sheet.paste(thumb,(x,y));draw.text((x+5,y+188),f'{i:03} {slug}',fill='white')
 base=f'models/singapore-fish/{slug}'
 assets.append({'id':'fish-'+slug,'name':en.split(' / ')[0],'category':'Fish','browseCategory':'Nature','description':f'FISH-{i:03} · {priority}. {en}. Stylized Blender fish study with editable body, fins and markings. Looping skeletal swim animation with tail and fin motion; common names follow the supplied brief.','tags':[f'FISH-{i:03}',cn,en,priority,'Singapore','Malaysia',kind,color],'file':base+'/exports/model.glb','thumbnail':base+'/previews/thumbnail.webp','metadata':base+'/metadata/model.json','license':"Original geometry and materials; reuse in the owner's projects is authorized. Public redistribution terms have not been specified."})
sheet.save(HERE/'contact-sheet.jpg',quality=90)
catpath=repo/'models/catalog.json';catalog=json.loads(catpath.read_text());cid='singapore-fish'
collection={'id':cid,'name':'Singapore & Malaysia Fish Collection','description':'60 stylized fish studies: seafood market, freshwater, reef and ornamental fish. Common names are supplied aliases; not a taxonomic identification guide.','assets':assets}
# Keep approved deployment derivatives authoritative when rebuilding baseline posters.
import importlib.util
spec=importlib.util.spec_from_file_location('fish_release_register',repo/'models/fish-realism-release/register.py')
release=importlib.util.module_from_spec(spec);spec.loader.exec_module(release)
release.apply(collection)
old=next((c for c in catalog['collections'] if c['id']==cid),None)
if old:catalog['collections'][catalog['collections'].index(old)]=collection
else:catalog['collections'].append(collection)
catpath.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
print('Registered',len(assets),'fish')
