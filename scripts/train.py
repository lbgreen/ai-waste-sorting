"""Fine-tune a detector on manually reviewed YOLO-format local data."""
import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--weights', type=Path, default=Path('weights/yolo26n.pt'))
    parser.add_argument('--device', default='mps')
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch', type=int, default=4)
    parser.add_argument('--imgsz', type=int, default=640)
    parser.add_argument('--name', default='detector')
    parser.add_argument('--small-portions', action='store_true', help='Disable augmentation that combines scenes or adds objects')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if not args.data.is_file() or not args.weights.is_file():
        parser.error('Local dataset YAML and model weights must exist; see docs/07_training.md.')
    if args.epochs < 1 or args.batch < 1:
        parser.error('epochs and batch must be positive')
    import yaml
    import hashlib
    import math
    data = yaml.safe_load(args.data.read_text())
    if 'download' in data:
        parser.error('Use a local dataset without a download directive')
    root = Path(data.get('path', '.'))
    if not root.is_absolute():
        root = (args.data.resolve().parent / root).resolve()
    names = data.get('names', [])
    if not names:
        parser.error('Dataset requires class names')
    seen = {}
    for split in ('train', 'val', 'test'):
        # Explicit layout prevents silently interpreting unlabelled captures as negatives.
        if data.get(split) != f'images/{split}':
            parser.error(f'Require {split}: images/{split}')
        images = [p for p in (root / 'images' / split).rglob('*')
                  if p.suffix.lower() in ('.jpg', '.jpeg', '.png')]
        if not images:
            parser.error(f'No images in {root}/images/{split}')
        objects = 0
        for image in images:
            digest = hashlib.sha256(image.read_bytes()).hexdigest()
            if digest in seen and seen[digest] != split:
                parser.error(f'Duplicate image across splits: {image}')
            seen[digest] = split
            label = root / 'labels' / split / image.relative_to(root / 'images' / split).with_suffix('.txt')
            if not label.is_file():
                parser.error(f'Missing reviewed label: {label}; empty scenes need an empty label file')
            for line in label.read_text().splitlines():
                try:
                    cls, x, y, w, h = map(float, line.split())
                    assert all(math.isfinite(v) for v in (cls, x, y, w, h))
                    assert cls.is_integer() and 0 <= cls < len(names)
                    assert 0 < w <= 1 and 0 < h <= 1
                    assert w/2-1e-8 <= x <= 1-w/2+1e-8 and h/2-1e-8 <= y <= 1-h/2+1e-8
                except (ValueError, AssertionError):
                    parser.error(f'Invalid YOLO bounding box in {label}: {line}')
                objects += 1
        if not objects:
            parser.error(f'{split} has no annotated objects')
        print(f'{split}: {len(images)} images, {objects} boxes')
    if args.check_only:
        print('Basic checks passed. Physical-object/session separation needs manual review.')
        return
    from ultralytics import YOLO
    output = Path('runs/waste_training').resolve()
    output.mkdir(parents=True, exist_ok=True)
    resolved_text = yaml.safe_dump({**data, 'path': str(root)})
    resolved = output / ('dataset_' + hashlib.sha256(resolved_text.encode()).hexdigest()[:12] + '.yaml')
    resolved.write_text(resolved_text)
    model = YOLO(str(args.weights))
    augmentation = dict(mosaic=0.0,mixup=0.0,cutmix=0.0,copy_paste=0.0) if args.small_portions else {}
    model.train(data=str(resolved.resolve()), device=args.device, epochs=args.epochs,
                batch=args.batch, imgsz=args.imgsz, workers=0, cache=False, amp=False,
                seed=42, patience=10, project=str(output), name=args.name, exist_ok=False,
                **augmentation)
    print('Training finished. Review validation results before evaluating the held-out test set.')
    print('Best checkpoint:', model.trainer.best)


if __name__ == '__main__':
    main()
