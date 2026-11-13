# Development status and team handoff

Updated: **13 November 2026** (Europe/Rome). Start here before continuing work.
Repository: [lbgreen/ai-waste-sorting](https://github.com/lbgreen/ai-waste-sorting), **public** by the owner's latest instruction.

## Current state

A supervised Python webcam prototype and two experimental waste-detector training runs exist. **There is no validated automatic sorting system yet.** Hardware target: MacBook Air M3 and Logitech C920. Camera capture worked, but camera index 0 was not conclusively identified as the C920; confirm the device before collecting evaluation images. No Arduino, serial output or servo control is implemented.

- `waste_sorter/__main__.py`: OpenCV preview, local YOLO integration, per-object boxes/name/confidence and status text, empty-tray calibration (`B`), image/metadata capture (`S`), quit (`Q`).
- `waste_sorter/decision.py`: category decision and temporal gate, extra fresh recheck, event latch until the tray clears. Commands are console demo events.
- `config/demo.json`: active default, no verified site profile or approved disposal mappings. Generic pretrained detection can be demonstrated, but it cannot establish Korean recyclability.
- `config/small_portions_demo.json`: separate experimental three-object profile; `needs_review` blocks commands. Not activated as the default.
- `scripts/prepare_taco.py`, `prepare_small_portions.py`, `train.py`, `evaluate.py`: public dataset preparation, small-scene selection, Apple MPS training and explicit evaluation.

Policy: confirmed conflicting confident destinations block sorting; otherwise usable uncertain classification produces `UNSURE` and `general`; confident shared categories produce `READY`. No waste, unresolved detection/occlusion, and recognized unsupported items produce no command. The three commands remain `paper`, `recycling`, `general`.

## Training results — completed 12 November

| Experiment | Data and setup | Result | Decision |
|---|---|---|---|
| Original TACO baseline | 687 train / 119 validation / 227 test images, 60 classes, 20 epochs, 320 px | Public test mAP@50 4.21%, mAP@50–95 2.96% | Not suitable for deployment |
| Small portions | 434 train / 68 validation / 150 previously used test images; 1–3 annotated objects, 10 recognition classes, 20 epochs, 416 px | Selected epoch 18: validation mAP@50 19.29%, mAP@50–95 15.37%, recall 15.82% at evaluator operating point | Many misses; not suitable for automatic sorting |

The tasks/label sets differ, so those metrics are **not a controlled before/after comparison**. Small-portion selection excludes 252 crowded images and 129 images with box overlap over 15% of the smaller box area. Mosaic, MixUp, CutMix and copy-paste are disabled. Counts are annotation counts, not proof that no unlabelled objects are present. Twelve training samples were visually inspected; outdoor backgrounds and very small objects remain.

The public test was already viewed in the first experiment and was not re-used as a new independent test for the second. Local C920 holdout scenes remain missing. Small-portion validation has no cup examples and very few examples for several other classes. `needs_review` retains all other source labels, including dedicated streams; it is not a fourth destination or a reliable unknown detector.

Detailed reports: [baseline](docs/08_training_results.md), [small portions](docs/09_small_portions_training.md), [machine-readable metrics](docs/small_portions_metrics.json).

## Checks and limitations

Six decision/temporal unit tests pass. Dataset preflight checks pass. All 652 small-portion images were checked for preserved source splits, 1–3 annotations, retained instances and the configured overlap limit. The separate profile was checked to reject `needs_review` without a command. Python compilation passes. These checks do not validate real-camera detection accuracy.

Known gaps: no calibrated confidence, robust instance tracking, proven occlusion/count completeness, condition/preparation inference, reviewed site mappings, or independent webcam evaluation. Background subtraction and box overlap are heuristics. No empty-tray/hand-only examples were added to training. No trained checkpoint has replaced the live default.

## Local-only artifacts and reproducibility

Git intentionally excludes `datasets/`, `weights/`, `runs/`, `captures/` and `.venv/`. **Cloning the repository does not include trained models or images.** No model release has been uploaded.

On the original training machine:

- `weights/yolo26n.pt`: generic pretrained detector.
- `weights/taco_yolo26n_baseline.pt`: first experimental model.
- `weights/small_portions_yolo26n.pt`: latest experimental model.
- `datasets/taco_small_batches/`: selected images, YOLO labels, source manifest and exclusion report.
- `runs/waste_training/small_portions/`: model checkpoints, configuration, curves and epoch CSV.
- `runs/small_portions_review/samples.jpg`: inspected contact sheet.

A teammate can obtain the experimental checkpoint from the training-machine owner through an agreed transfer, or reproduce training. Image-specific source rights are incomplete; excluded images and source provenance are recorded. Do not publish the image collection.

Fresh setup, from the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
# Explicitly fetch the generic pretrained checkpoint into weights/:
mkdir -p weights
.venv/bin/python -c 'import os; from ultralytics import YOLO; os.chdir("weights"); YOLO("yolo26n.pt")'
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/prepare_taco.py
.venv/bin/python scripts/prepare_small_portions.py --output datasets/taco_small_batches
.venv/bin/python scripts/train.py --data datasets/taco_small_batches/dataset.yaml --check-only
.venv/bin/python scripts/train.py --data datasets/taco_small_batches/dataset.yaml --epochs 20 --imgsz 416 --name small_portions --small-portions
```

Preparation refuses to overwrite an existing small-portion output; select a new directory for changed settings. Training prints the actual run/checkpoint path. `requirements-lock-macos.txt` records the earlier installed dependency snapshot; the broad requirements file permits newer compatible versions. Runtime/retraining results can differ with dependencies and hardware.

For supervised visual inspection only, if the named local model is available:

```bash
.venv/bin/python -m waste_sorter --camera 0 --weights weights/small_portions_yolo26n.pt --config config/small_portions_demo.json
```

Verify the camera index. Recognition overlays start immediately; clear the tray and press `B` before attempting demo decisions. Press `Q` to stop. The next session should not start the camera without an inspection/collection task.

## Next work, in priority order

1. **Verify the real setup.** Identify the C920 index, fix mounting/lighting and define the actual tray. Collect labelled, physically distinct 1-, 2- and 3-item scenes plus empty, hand-only, unknown and overlapping scenes. Record object/session IDs before splitting; do not label predictions as ground truth.
2. **Fix evaluation coverage.** Add local validation examples for every target class, especially paper, cans, cups and containers. Keep a fresh local object/session pool untouched for final testing. Include all mixed-category pairs and same-category multi-item portions.
3. **Improve recognition based on errors.** Inspect misses and per-class recall. Review the ten-class mapping against the actual whitelist; acquire additional suitable labelled public/local examples where coverage is weak. Keep all visible instances annotated and scene-combining augmentations disabled for small-portion experiments. Do not simply rerun the same weak experiment or repeatedly tune against the old public test.
4. **Review Korean disposal rules with the team.** Confirm campus/building, collector and preparation conditions. Keep `site_verified: false` until this is resolved; no blanket bottle/plastic/paper-to-bin shortcuts.
5. **Validate the integrated policy.** Measure complete-scene detection, false mixed-waste acceptance, unknown handling, empty-scene false detections, stable-frame behavior and latency on the C920. Only then consider a default-model change. Hardware actuation remains out of scope.

## Collaboration routine

After meaningful changes, update this handoff, run appropriate checks, commit and push. Keep the repository public. These preferences are also recorded in [AGENTS.md](AGENTS.md). If a push fails, report the failure rather than claiming synchronization. Use Git history as the authoritative record of pushed revisions.
