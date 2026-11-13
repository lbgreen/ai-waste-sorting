"""Select lightly overlapping scenes with 1–3 annotated items; preserve source splits."""
import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
import yaml

# Recognition labels only. All unmapped instances remain annotated as needs_review.
GROUPS = {
    'plastic_bottle': [4, 5],
    'glass_bottle': [6],
    'metal_can': [10, 12],
    'cardboard': [13, 14, 15, 17, 18, 19],
    'paper': [30, 32, 33, 34],
    'film_wrapper': list(range(36, 43)),
    'cup': list(range(20, 25)),
    'plastic_container': list(range(43, 48)),
    'cigarette': [59],
    'needs_review': [],
}


def overlap_fraction(a, b):
    _, x, y, w, h = a
    _, xx, yy, ww, hh = b
    intersection = max(0, min(x+w/2,xx+ww/2)-max(x-w/2,xx-ww/2)) * max(0,min(y+h/2,yy+hh/2)-max(y-h/2,yy-hh/2))
    return intersection / min(w*h, ww*hh)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path('datasets/taco_yolo'))
    parser.add_argument('--output', type=Path, default=Path('datasets/taco_small_portions'))
    parser.add_argument('--max-items', type=int, default=3)
    parser.add_argument('--max-overlap', type=float, default=.15)
    parser.add_argument('--min-box-area', type=float, default=0.0)
    args = parser.parse_args()
    if args.max_items < 1 or not 0 <= args.max_overlap <= 1 or not 0 <= args.min_box_area <= 1:
        parser.error('Invalid count/overlap/area settings')
    if args.output.exists():
        parser.error('Output already exists; choose a new directory to avoid stale data')
    root = args.output.resolve()
    manifest = json.loads((args.source/'manifest.json').read_text())
    names = list(GROUPS)
    mapping = {c: i for i, group in enumerate(GROUPS.values()) for c in group}
    fallback = names.index('needs_review')
    accepted, rejected = [], []
    counts = {s: Counter() for s in ('train','val','test')}
    for s in counts:
        for k in ('images','labels'):
            (root/k/s).mkdir(parents=True,exist_ok=True)
    for row in manifest:
        split, stem = row['split'], str(row['source_image_id'])
        label = args.source/'labels'/split/(stem+'.txt')
        original = [list(map(float,l.split())) for l in label.read_text().splitlines() if l.strip()]
        reason = None
        if not 1 <= len(original) <= args.max_items:
            reason = 'object_count'
        elif any(b[3]*b[4] < args.min_box_area for b in original):
            reason = 'tiny_object'
        elif any(overlap_fraction(a,b) > args.max_overlap for i,a in enumerate(original) for b in original[i+1:]):
            reason = 'overlap'
        if reason:
            rejected.append({**row, 'reason':reason, 'annotated_count':len(original)})
            continue
        converted=[]
        for c,x,y,w,h in original:
            target = mapping.get(int(c),fallback)
            converted.append(f'{target} {x:.10f} {y:.10f} {w:.10f} {h:.10f}')
            counts[split][names[target]]+=1
        shutil.copy2(args.source/'images'/split/(stem+'.jpg'),root/'images'/split/(stem+'.jpg'))
        (root/'labels'/split/(stem+'.txt')).write_text('\n'.join(converted)+'\n')
        accepted.append({**row,'annotated_count':len(original),'original_boxes':original})
    (root/'manifest.json').write_text(json.dumps(accepted,indent=2))
    (root/'excluded.json').write_text(json.dumps(rejected,indent=2))
    config = dict(path=str(root),train='images/train',val='images/val',test='images/test',names=dict(enumerate(names)))
    (root/'dataset.yaml').write_text(yaml.safe_dump(config))
    summary = dict(settings=dict(max_items=args.max_items,max_overlap=args.max_overlap,min_box_area=args.min_box_area),
                   images=dict(Counter(r['split'] for r in accepted)),boxes={s:dict(c) for s,c in counts.items()},
                   counts_per_scene={s:dict(Counter(r['annotated_count'] for r in accepted if r['split']==s)) for s in counts},
                   excluded=dict(Counter(r['reason'] for r in rejected)),class_groups=GROUPS,
                   note='Count/overlap heuristics do not prove complete annotation or absence of clutter. Source splits retained. Previously viewed public test is not a new holdout. needs_review is a recognition class, never a sorting command.')
    (root/'selection.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
