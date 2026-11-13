"""Prepare the reviewed TACO release for a public-domain-shift baseline.
Images stay local. Image-specific rights remain unresolved; do not redistribute.
"""
import hashlib
import io
import json
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
import yaml
from PIL import Image


def main():
    source = Path('datasets/taco_source/annotations.json')
    if not source.exists():
        source.parent.mkdir(parents=True,exist_ok=True)
        response = requests.get('https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json',timeout=30)
        response.raise_for_status()
        # Validate before keeping a source file.
        response.json()
        source.write_bytes(response.content)
    data = json.loads(source.read_text())
    root = Path('datasets/taco_yolo').resolve()
    annotations = defaultdict(list)
    for a in data['annotations']:
        annotations[a['image_id']].append(a)
    # Whole source batches stay together to reduce nearby-scene leakage.
    batches = sorted({i['file_name'].split('/')[0] for i in data['images']},
                     key=lambda x: hashlib.sha256(('42'+x).encode()).hexdigest())
    n = len(batches)
    split_by_batch = {b: 'test' if j < max(1,n//5) else 'val' if j < max(2,2*n//5) else 'train'
                      for j,b in enumerate(batches)}
    for split in ('train','val','test'):
        for kind in ('images','labels'):
            (root/kind/split).mkdir(parents=True,exist_ok=True)
    def fetch(info):
        split = split_by_batch[info['file_name'].split('/')[0]]
        name = str(info['id'])
        target = root/'images'/split/(name+'.jpg')
        url = info.get('flickr_640_url')
        if not url or not url.startswith('https://'):
            # This first baseline is deliberately limited to the lightweight release.
            # Original-only images can be many MB each; record their exclusion.
            return {'source_image_id': info['id'], 'error': 'No 640px URL; original-only image excluded from baseline'}
        if not target.exists():
            response = requests.get(url,timeout=(5,10))
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            image.load()
            target.with_suffix('.part').write_bytes(response.content)
            target.with_suffix('.part').replace(target)
        with Image.open(target) as image:
            image.verify()
        labels = []
        for a in annotations[info['id']]:
            x,y,w,h = a['bbox']
            iw,ih = info['width'],info['height']
            x1,y1 = max(0,x),max(0,y)
            x2,y2 = min(iw,x+w),min(ih,y+h)
            if x2<=x1 or y2<=y1:
                raise ValueError(f'Invalid source box: {a}')
            labels.append(f"{a['category_id']} {(x1+x2)/2/iw:.10f} {(y1+y2)/2/ih:.10f} {(x2-x1)/iw:.10f} {(y2-y1)/ih:.10f}")
        (root/'labels'/split/(name+'.txt')).write_text('\n'.join(labels)+'\n')
        return dict(source_image_id=info['id'],source_file=info['file_name'],url=url,
                    split=split,license=info.get('license'),sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    def checked_fetch(info):
        try:
            return fetch(info)
        except (requests.RequestException, OSError) as error:
            return {'source_image_id': info['id'], 'error': str(error)}
    manifest=[]
    failures=[]
    with ThreadPoolExecutor(max_workers=16) as pool:
        for row in pool.map(checked_fetch,data['images']):
            if 'error' in row:
                failures.append(row)
                continue
            manifest.append(row)
            if len(manifest)%100==0:
                print(f'Downloaded and checked {len(manifest)}/{len(data["images"])}',flush=True)
    unique = []
    seen = set()
    for row in sorted(manifest, key=lambda r: ({'test':0,'val':1,'train':2}[r['split']],r['source_image_id'])):
        if row['sha256'] in seen:
            failures.append({'source_image_id':row['source_image_id'],'error':'Exact duplicate excluded'})
            for kind,ext in (('images','.jpg'),('labels','.txt')):
                (root/kind/row['split']/(str(row['source_image_id'])+ext)).unlink()
        else:
            unique.append(row)
            seen.add(row['sha256'])
    manifest = unique
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2))
    (root/'download_failures.json').write_text(json.dumps(failures,indent=2))
    (root/'dataset.yaml').write_text(yaml.safe_dump(dict(path=str(root),train='images/train',val='images/val',test='images/test',names={c['id']:c['name'] for c in data['categories']})))
    (root/'provenance.json').write_text(json.dumps(dict(source='https://github.com/pedropro/TACO',annotation_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),split_by_batch=split_by_batch,counts=dict(Counter(r['split'] for r in manifest)),note='All 60 source classes preserved. No disposal labels. Batch grouping does not prove physical-object independence. Image licenses unresolved; no redistribution.'),indent=2))
    print('Prepared',root,flush=True)


if __name__=='__main__':
    main()
