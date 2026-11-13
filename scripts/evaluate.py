"""Evaluate a selected detector; test is for a frozen experiment only."""
import argparse
import hashlib
import json
from pathlib import Path
from ultralytics import YOLO


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--weights',type=Path,required=True)
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--split',choices=['val','test'],default='val')
    parser.add_argument('--device',default='mps')
    parser.add_argument('--imgsz',type=int,default=320)
    args=parser.parse_args()
    if not args.weights.is_file() or not args.data.is_file():
        parser.error('Local weights and dataset configuration are required')
    model=YOLO(str(args.weights))
    metrics=model.val(data=str(args.data.resolve()),split=args.split,device=args.device,
                      imgsz=args.imgsz,batch=4,workers=0,plots=True,
                      project=str(Path('runs/waste_evaluation').resolve()),name=args.split)
    report=dict(split=args.split,weights=str(args.weights.resolve()),
                weights_sha256=hashlib.sha256(args.weights.read_bytes()).hexdigest(),
                data=str(args.data.resolve()),metrics=metrics.results_dict,
                note='Public TACO evaluation only; not C920 or Korean sorting validation.')
    (Path(metrics.save_dir)/'summary.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    main()
