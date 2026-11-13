# AI Waste Sorting — supervised camera prototype

Python prototype for a MacBook Air M3 and Logitech C920. **No Arduino/servo control.**

**Team handoff:** read [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md) for the current implementation, training results, local-only artifacts and next steps. The GitHub repository stays public; update the handoff and push verified changes after each meaningful work session.

For the next lecture: [Round 1 analysis and discussion points](docs/training_round_1/README.md).

## Start camera preview

Run from this repository directory:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m waste_sorter --camera 0
```

Try `--camera 1` or `--camera 2` if the internal camera is selected. Allow camera access for the launching application under macOS System Settings → Privacy & Security → Camera. Quit other applications using the C920 if capture fails.

- `B`: calibrate the **empty** marked tray, after removing all objects/hands.
- `S`: save the current original image and prediction metadata under `captures/` (ignored by Git).
- `Q`: quit.

Camera-only mode collects images and displays foreground regions; it **does not classify waste or emit sorting decisions for occupied scenes**.

## Enable object detection

The locally downloaded demonstration model can be started with:

```bash
.venv/bin/python -m waste_sorter --camera 0 --weights weights/yolo26n.pt
```

Live boxes show each object's name, confidence and disposal uncertainty directly in the image. Recognition starts immediately; empty-tray calibration with `B` is needed for sorting decisions. The top image banner shows the overall decision status. Per-object fallback labels do not authorize a command while the overall scene is blocked or still stabilizing. The model file is ignored by Git and must be supplied separately on other machines.

Use an existing trusted local Ultralytics detection checkpoint:

```bash
.venv/bin/python -m waste_sorter --camera 1 --weights weights/best.pt
```

No weights or datasets are automatically downloaded. A generic COCO YOLO checkpoint detects some everyday objects, but lacks waste classes such as cardboard and cannot establish Korean recyclability. It is only a demonstration baseline. A trained waste detector and reviewed site rules are still required. CPU is the default; `--device mps` is an optional locally tested alternative.

`config/demo.json` has no approved disposal mappings (`site_verified: false`, empty `rules`). Identified objects without a reliable disposal mapping produce `UNSURE/general` in a complete stable scene, not a fabricated confident material classification. The demo policy must not be connected to actuators. Configure exact model class names as keys in `rules` only after reviewing material, preparation and site requirements; `site_verified` is an operator declaration, not automatic legal verification. Visual condition/preparation inference and product lookup are not implemented.

## Decision behavior

- Two different confident mapped categories: `ERROR_MIXED_WASTE`, no command.
- Otherwise uncertain classification in a usable scene: `UNSURE`, `general`.
- Confident shared category: `READY`, shared `paper`, `recycling` or `general`.
- Empty, unresolved detection, occlusion or known unsupported item: no command.

Console JSON events contain a single `command` string and separate status/warning fields. They are demo events only, not serial output. Every successful event requires consecutive stable frames plus a fresh extra recheck, then latches until the tray is empty. Disconnects disarm the gate.

Thresholds and temporal settings are configurable. The initial numbers are unvalidated starting settings. UI scores are model confidence scores, **not calibrated legal-disposal probabilities**. Foreground/background subtraction and bounding-box overlap are conservative heuristics: shadows, lighting changes, transparent items, hidden objects and same-count replacements can defeat them. There is no validated instance tracker or reliable occlusion detector yet. Spread objects out; do not stack or nest items. Recalibrating an occupied tray corrupts the empty baseline.

## Tests

For local data collection, annotation and Apple MPS fine-tuning, see [training instructions](docs/07_training.md). A first public TACO baseline has been trained and tested; its detection quality is insufficient for deployment. See [the experiment report](docs/08_training_results.md). The live model remains unchanged.

The follow-up [small-portion experiment](docs/09_small_portions_training.md) selects one to three annotated objects per scene and disables augmentation that combines scenes. It uses a separate experimental configuration and does not replace the live model.

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Tests cover decision priorities and temporal gating, not real-camera accuracy. The research design in `docs/` describes additional requirements that this prototype does not yet fully implement. Images saved by the preview are unlabelled ground truth; predictions must not become automatic training labels.

Model integration follows the [Ultralytics prediction API](https://docs.ultralytics.com/modes/predict/). Ultralytics has AGPL-3.0/Enterprise terms; review the selected software and model licenses before distribution. `requirements-lock-macos.txt` records the installed Python 3.12/macOS Apple Silicon dependency versions. Use `pip install -r requirements-lock-macos.txt` to reproduce those versions; hardware/runtime behavior still needs local validation.
