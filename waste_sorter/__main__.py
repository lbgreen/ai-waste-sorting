import argparse
import json
import sys
import time
from pathlib import Path

from .decision import Item, Decision, Gate, assess, VALID


def main():
    parser = argparse.ArgumentParser(description='Supervised webcam sorting demo; no Arduino')
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--weights', type=Path, help='Existing local YOLO detection checkpoint; no automatic download')
    parser.add_argument('--config', type=Path, default=Path('config/demo.json'))
    parser.add_argument('--device', default='cpu', help='cpu or mps (benchmark before using)')
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if not 0 <= cfg['candidate_threshold'] <= cfg['classification_threshold'] <= 1:
        parser.error('Require 0 <= candidate_threshold <= classification_threshold <= 1')
    for key in ('stable_frames', 'stable_seconds', 'max_gap_seconds', 'empty_reset_seconds', 'max_objects'):
        if cfg[key] <= 0:
            parser.error(key + ' must be positive')
    if any(v not in VALID for v in cfg['rules'].values()):
        parser.error('Rule destinations must be paper, recycling or general')
    import cv2
    import numpy as np
    model = None
    if args.weights:
        if not args.weights.is_file():
            parser.error('Weights do not exist. No automatic downloads are performed.')
        from ultralytics import YOLO
        model = YOLO(str(args.weights))
        if model.task != 'detect':
            parser.error('Use a detection checkpoint, not a whole-image classifier')
    backend = cv2.CAP_AVFOUNDATION if sys.platform == 'darwin' else cv2.CAP_ANY
    cap = cv2.VideoCapture(args.camera, backend)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        raise SystemExit('Camera unavailable. Try --camera 1 or 2 and allow camera access in macOS settings.')
    print('Camera opened:', int(cap.get(3)), 'x', int(cap.get(4)), 'FPS:', cap.get(5), flush=True)
    print('B: calibrate EMPTY tray; S: save image; Q: quit. Commands are demo events only.', flush=True)
    gate = Gate(cfg)
    background = previous = None
    scene_revision = 0
    last_command = '-'
    sequence = 0
    session = time.strftime('%Y%m%d-%H%M%S')
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                gate.fault()
                raise RuntimeError('Camera read failed; disarmed. Restart and clear tray.')
            started = time.monotonic()
            h, w = frame.shape[:2]
            # Fixed central tray; objects must be entirely inside it.
            x0, y0, x1, y1 = int(w*.15), int(h*.12), int(w*.85), int(h*.88)
            crop = frame[y0:y1, x0:x1]
            gray = cv2.GaussianBlur(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY), (9,9), 0)
            motion = previous is not None and np.mean(cv2.absdiff(gray, previous)) / 255 > cfg['motion_threshold']
            previous = gray.copy()
            if motion:
                scene_revision += 1
            regions = []
            if background is not None:
                mask = (cv2.absdiff(gray, background) > cfg['foreground_pixel_threshold']).astype('uint8')*255
                mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7,7), np.uint8))
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                regions = [cv2.boundingRect(c) for c in contours
                           if cv2.contourArea(c) > gray.size*cfg['min_region_fraction']]
            items, boxes = [], []
            if model is not None:
                result = model.predict(crop, conf=cfg['candidate_threshold'], device=args.device,
                                       imgsz=640, max_det=cfg['max_objects']+1, verbose=False)[0]
                for box in result.boxes:
                    label = result.names[int(box.cls.item())]
                    score = float(box.conf.item())
                    coords = tuple(map(int, box.xyxy[0].tolist()))
                    destination = cfg['rules'].get(label) if cfg['site_verified'] else None
                    items.append(Item(label, score, destination, label in cfg['unsupported_labels']))
                    boxes.append(coords)
            # Conservative one foreground region per detection. This is a heuristic,
            # not proof that hidden or transparent objects are absent.
            complete = background is not None and not motion and len(regions) <= cfg['max_objects']
            matches = []
            for rx, ry, rw, rh in regions:
                hits = [i for i,(a,b,c,d) in enumerate(boxes)
                        if a <= rx+rw/2 <= c and b <= ry+rh/2 <= d]
                matches.append(hits)
            if model is not None:
                complete &= (len(regions) == len(boxes) and
                             all(len(m) == 1 for m in matches) and
                             len({m[0] for m in matches if m}) == len(boxes))
            for i,(a,b,c,d) in enumerate(boxes):
                if min(a,b) < 5 or c >= crop.shape[1]-5 or d >= crop.shape[0]-5:
                    complete = False
                if items[i].label in cfg['non_waste_labels']:
                    complete = False
                for aa,bb,cc,dd in boxes[i+1:]:
                    if min(c,cc)>max(a,aa) and min(d,dd)>max(b,bb):
                        complete = False
            # Camera-only mode: localized separated foreground is explicitly unknown.
            if model is None:
                boxes = [(x,y,x+ww,y+hh) for x,y,ww,hh in regions]
                items = [Item('Unknown object (no model)', 0.0) for _ in boxes]
                complete = False  # Preview/collection only; cannot establish individual objects.
            empty = background is not None and not regions and not boxes and not motion
            if empty:
                complete = True
            decision = assess(items, complete, empty, cfg['classification_threshold'])
            signature = (scene_revision, tuple(sorted((i.label if i.confidence >= cfg['classification_threshold'] else 'uncertain',
                         i.destination, tuple(v//24 for v in box)) for i,box in zip(items,boxes))))
            if time.monotonic()-started > cfg['max_gap_seconds']:
                decision = Decision('WARNING_DETECTION', reason='Inference too slow; stale observation')
            shown, command = gate.update(decision, signature, time.monotonic())
            if command:
                sequence += 1
                last_command = command
                print(json.dumps({'event_id': f'{session}-{sequence}', 'status': shown.status,
                                  'command': command, 'reason': shown.reason, 'demo_only': True}), flush=True)
            view = frame.copy()
            cv2.rectangle(view,(x0,y0),(x1,y1),(255,200,0),2)
            for index,(item,(a,b,c,d)) in enumerate(zip(items,boxes),1):
                unsure = item.destination is None or item.confidence < cfg['classification_threshold']
                color = (0,190,255) if unsure else (0,210,0)
                cv2.rectangle(view,(a+x0,b+y0),(c+x0,d+y0),color,2)
                disposition = ('UNSUPPORTED' if item.unsupported else
                               'UNSURE -> general (fallback)' if unsure else item.destination)
                labels = [f'{index}: {item.label} | confidence {item.confidence:.0%}', disposition]
                label_width = max(cv2.getTextSize(t,cv2.FONT_HERSHEY_SIMPLEX,.55,1)[0][0] for t in labels)+16
                left = max(0,min(a+x0,w-label_width))
                top = max(65,b+y0-54)
                cv2.rectangle(view,(left,top),(left+label_width,top+50),(20,20,20),-1)
                for row,text in enumerate(labels):
                    cv2.putText(view,text,(left+8,top+19+row*23),cv2.FONT_HERSHEY_SIMPLEX,.55,color,1,cv2.LINE_AA)
            cv2.rectangle(view,(0,0),(w,59),(20,20,20),-1)
            cv2.putText(view,f'LIVE | {shown.status} | sorting category: {shown.category or "-"}',
                        (12,24),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),1,cv2.LINE_AA)
            hint = shown.reason if background is not None else 'Recognition live. Clear tray and press B to enable sorting decisions.'
            cv2.putText(view,hint[:125],(12,47),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,190,255),1,cv2.LINE_AA)
            panel = np.zeros((165,w,3),np.uint8)
            lines = [f'DEMO | {shown.status} | category: {shown.category or "-"} | last event: {last_command}',
                     shown.reason[:130],
                     'Uncertain classification defaults to GENERAL.' if shown.status=='UNSURE' else 'No hardware connected. Foreground completeness is heuristic.',
                     'B: EMPTY tray calibration | S: save | Q: quit | '+('YOLO loaded' if model else 'CAMERA ONLY - no recognition model')]
            if background is None:
                lines[1] = 'Clear the marked tray, remove hands, then press B.'
            for n,line in enumerate(lines):
                cv2.putText(panel,line,(10,28+n*35),cv2.FONT_HERSHEY_SIMPLEX,.55,(240,240,240),1)
            cv2.imshow('Waste sorter - supervised prototype',np.vstack([view,panel]))
            key = cv2.waitKey(1) & 255
            if key == ord('q'):
                break
            if key == ord('b'):
                # Recalibration disarms until empty is observed, never directly re-arms.
                background = gray.copy()
                gate.fault()
            if key == ord('s'):
                folder = Path('captures') / session
                folder.mkdir(parents=True,exist_ok=True)
                name = str(time.time_ns())
                cv2.imwrite(str(folder/(name+'.jpg')),frame)
                (folder/(name+'.json')).write_text(json.dumps({'session_id':session,'status':shown.status,
                    'items':[vars(i) for i in items], 'boxes_roi':boxes, 'roi':[x0,y0,x1,y1],
                    'ground_truth':None},indent=2))
                print('Saved', folder/name, flush=True)
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
