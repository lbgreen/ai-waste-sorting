# Local detector training

Status: a first public TACO baseline has been trained and evaluated, but is unsuitable for deployment. No labelled local C920 data is available yet. See [results](08_training_results.md).

## First collection session

Use the C920 and the actual tray. Confirm the preview comes from the external camera before collecting; change `--camera` if needed. Start with cardboard, office paper, plastic bottles, metal cans, film wrappers and tissues. These are recognition labels, not automatic disposal mappings.

For an initial pipeline pilot, gather 10 distinct physical items per class and 5–10 deliberately different views per item. This is not enough to claim production accuracy; expand following the main dataset plan. Keep lighting, angles and product designs varied. Include empty scenes, hands and scenes with several separated objects. Do not label unrecognized waste as empty background.

The running preview saves an original image and prediction metadata when you press `S`. The files go to `captures/<session>/`. Predictions are annotation suggestions only: a human must check every visible object and its bounding box. Do not train directly on the saved predicted boxes. Record physical object IDs and session IDs alongside the image filenames; identify all items in multi-object scenes.

Split physical objects into train/validation/test pools BEFORE taking mixed-object scenes (initial suggestion: 60/20/20). Never mix pools within a scene. All views of the same physical item stay together. Prefer separate sessions for held-out evaluation. Exact image duplicate checks cannot detect near duplicates or repeated physical items.

## Reviewed data layout

Use `datasets/local_waste/images/{train,val,test}` and matching `labels/{train,val,test}` directories. Each image needs a same-stem `.txt` file containing one `class_id center_x center_y width height` line per object, with coordinates normalized to image dimensions. Only a reviewed empty image gets an empty label file. Preserve unknown, unsupported and occluded examples separately for challenge evaluation if outside the initial taxonomy.

Class IDs are in `config/waste_dataset.example.yaml`. Expand the taxonomy and reannotate consistently before adding other classes. The initial six classes do not cover every waste item.

```bash
.venv/bin/python scripts/train.py --data config/waste_dataset.example.yaml --check-only
# First verify the complete pipeline with one epoch:
.venv/bin/python scripts/train.py --data config/waste_dataset.example.yaml --epochs 1
# Then run the initial experiment:
.venv/bin/python scripts/train.py --data config/waste_dataset.example.yaml --epochs 50
```

Defaults use Apple MPS, batch 4, 640 px, no RAM cache and no data-loader subprocesses. Reduce batch size or use `--device cpu` if needed. Runtime and memory usage have not yet been benchmarked on real training data. Training creates a new run directory and prints the best checkpoint location; it does not replace the live model.

Review per-class validation precision/recall, missed objects and confusion before choosing thresholds. Keep the test set untouched until the model/configuration is selected; then evaluate it once using `YOLO(checkpoint).val(data=resolved_yaml, split='test')`. Also test live mixed, unknown and occluded scenes: detector mAP alone does not validate sorting safety. Only then run the live app with `--weights <best-checkpoint>`.

The Korean disposal rules and uncertainty logic remain separate. Recognizing a bottle does not establish its preparation or legal destination. No automatic update of `site_verified` or disposal mappings occurs.

Implementation references: [Ultralytics training](https://docs.ultralytics.com/modes/train/) and [YOLO detection annotations](https://docs.ultralytics.com/datasets/detect/).

## Public TACO baseline (12 November 2026)

`scripts/prepare_taco.py` downloads the 640 px image variants referenced by the original reviewed TACO annotation release and converts all 60 classes to YOLO boxes. Images without a thumbnail URL (466 of 1,500 source records) are explicitly excluded from this first lightweight baseline; unreachable files are recorded in `download_failures.json`. Normalized coordinates are calculated from the original dimensions; resizing preserves their relative geometry. All source instances in retained images remain annotated. Source batches stay together in deterministic train/validation/test partitions. This reduces some scene leakage but does not establish physical-object independence. Exact duplicates across partitions are rejected by the training preflight. Public validation/test performance measures the TACO domain only.

Source annotation metadata, source URLs, image hashes, original license fields and batch assignments are retained under `datasets/`. Image license fields may be missing; this local research preparation does not claim blanket image rights or authorize redistribution. Images and weights are excluded from Git. Source: [TACO original toolkit and reviewed data](https://github.com/pedropro/TACO).

```bash
.venv/bin/python scripts/prepare_taco.py
.venv/bin/python scripts/train.py --data datasets/taco_yolo/dataset.yaml --check-only
.venv/bin/python scripts/train.py --data datasets/taco_yolo/dataset.yaml --epochs 1 --imgsz 320
```

The first one-epoch, 320 px run is a pipeline and runtime test, not a final detector. Use its measured runtime and validation behavior to size the next experiment. No test-set tuning and no automatic deployment. TACO names differ from the live configuration: before deployment, explicitly review unsupported labels (e.g. `Battery`, `Drink carton`, `Food waste`) and disposal mappings. The live camera continues to use its existing checkpoint until this review and C920 evaluation are complete.

The initial 20-epoch public baseline and its separate test evaluation are now complete. See [the result report](08_training_results.md). Detection quality was insufficient, so the checkpoint was not deployed. Reproduce a selected model's evaluation with `scripts/evaluate.py --weights <checkpoint> --data <dataset.yaml> --split test`; keep test evaluation separate from model selection.
