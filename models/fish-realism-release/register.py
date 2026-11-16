"""Apply approved release overrides without changing other catalog assets."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[1]

def apply(collection):
 manifest=json.loads((HERE/'releases.json').read_text())
 for asset in collection['assets']:
  slug=asset['id'].removeprefix('fish-')
  if slug not in manifest['models']:continue
  item=manifest['models'][slug];base=f'models/fish-realism-release/{slug}'
  asset.update(file=base+'/model.glb',thumbnail=base+'/thumbnail.webp',metadata=base+'/metadata.json',license=item['license'])
  asset['description']=item['description']
 collection['description']='60 seafood, freshwater, reef and ornamental fish. Approved realistic upgrades retain swimming animation; individual entries identify provenance and limitations. Common names are supplied aliases, not a taxonomic guide.'
 return collection

if __name__=='__main__':
 path=REPO/'models/catalog.json';catalog=json.loads(path.read_text())
 for collection in catalog['collections']:
  if collection['id']=='singapore-fish':apply(collection)
 path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
