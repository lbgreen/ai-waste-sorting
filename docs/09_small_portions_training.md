# Small-portion detector experiment — 12 November 2026

The intended use is a small portion of waste per presentation, not a heap. This experiment selects scenes with **one to three annotated objects**. The choice of three is an initial configurable operating assumption.

## Selection

The script `scripts/prepare_small_portions.py` keeps existing source partitions and all annotations in each retained image. It rejects an entire image if it contains more than three marked instances, or if any two boxes overlap by more than 15% of the smaller box's area. This measure also rejects nested boxes that a low IoU could miss. The overlap threshold is a configurable heuristic, not a proven occlusion limit. No minimum object-area filter is applied in the final selection, since that would remove many small-object examples. A stricter preliminary area-filtered subset was inspected but not trained.

| Partition | Images | Boxes | One-item / two-item / three-item images |
|---|---:|---:|---|
| Train | 434 | 649 | 269 / 115 / 50 |
| Validation | 68 | 103 | 39 / 23 / 6 |
| Previously used public test | 150 | 248 | 74 / 54 / 22 |

Of the 1,033 prepared source images, 252 are excluded for object count and 129 for overlap. Annotation counts do not guarantee the true count: source annotations can miss objects, and a single marked object could be a composite. Twelve deterministic training samples were visually inspected in a contact sheet at `runs/small_portions_review/samples.jpg`. They still show outdoor backgrounds and some very small objects. This is not a complete manual audit or a match to the bin's camera view.

## Recognition taxonomy and policy

The original 60 classes are grouped into ten recognition classes: plastic bottle, glass bottle, metal can, cardboard, paper, film/wrapper, cup, plastic container, cigarette, and `needs_review`. The complete mapping and per-class counts are retained in `docs/small_portions_selection.json`. Original per-instance class IDs and boxes remain in the dataset manifest. No instance is silently discarded or relabelled as background.

`needs_review` includes all source classes outside the nine named groups, including batteries and beverage cartons. It is a broad supervised catch-all, **not a calibrated unknown-object detector and not a fourth sorting command**. In the separate demo configuration it blocks commands. The other broad recognition classes do not establish material/preparation or Korean recyclability: for example, `cup` includes multiple materials. The disposal mapping stays empty and `site_verified` stays false.

`config/small_portions_demo.json` is a separate experimental profile with a three-object capacity and `needs_review` rejection. It does not replace the active demo profile. Confident category conflicts must still block sorting; a small portion may contain mixed waste. Do not use unknown or uncertain-general fallback as a training label.

## Training and evaluation

The run starts from the original pretrained YOLO26n weights, with 20 planned epochs, 416 px input, batch 4, seed 42 and Apple MPS. Mosaic, MixUp, CutMix and copy-paste are all disabled so training does not combine several scenes into a more crowded image. Other normal augmentations may move or crop objects, but do not add instances.

```bash
.venv/bin/python scripts/prepare_small_portions.py --output datasets/taco_small_batches
.venv/bin/python scripts/train.py --data datasets/taco_small_batches/dataset.yaml --check-only
.venv/bin/python scripts/train.py --data datasets/taco_small_batches/dataset.yaml --epochs 20 --imgsz 416 --name small_portions --small-portions
```

Selection is based on validation only. The prior public test has already been viewed and is not evaluated again as a new independent test. C920 holdout scenes are still required. Validation contains no cup examples and only one example each for paper, metal can and plastic container, so aggregate metrics cannot demonstrate reliable coverage. Because both taxonomy and selected scenes changed, metrics are not directly comparable to the original 60-class baseline.

No empty-tray or hand-only training examples were added. False detections on empty scenes, hidden-object counts, mixed-category decisions and stable webcam behavior still need dedicated evaluation. Preparation refuses to overwrite an existing output directory; choose a new output path when rebuilding a dataset.

## Completed result

All 20 epochs completed. The selected checkpoint is from epoch 18 (best validation mAP@50–95). Its recorded validation mAP@50 is **19.29%**, mAP@50–95 is **15.37%**, and aggregate recall at the evaluator's operating point is **15.82%**. These are not sorting accuracy figures. Many objects are still missed; the model is **not approved for automatic sorting**. The operating point is not the app's configured 0.8 confidence threshold. No claim of improvement over the old differently defined task is made.

- Local checkpoint: `weights/small_portions_yolo26n.pt`.
- Training artifacts: `runs/waste_training/small_portions/`.
- Metrics, model hash and selection: `docs/small_portions_metrics.json`.
- Separate experimental profile: `config/small_portions_demo.json`.

The live app was not restarted and its active defaults were not changed. A future supervised visual evaluation must pass the matching profile explicitly:

```bash
.venv/bin/python -m waste_sorter --camera 0 --weights weights/small_portions_yolo26n.pt --config config/small_portions_demo.json
```

This command is for observation only; the checkpoint has no calibrated disposal model or verified Korean mappings. The three-object profile blocks scenes that it can identify as overloaded; missed or hidden instances can still defeat that check. Arduino/servo control remains absent.
