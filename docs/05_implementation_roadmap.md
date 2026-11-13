# Phase 2 roadmap and executive summary

Current team handoff: [DEVELOPMENT_STATUS.md](../DEVELOPMENT_STATUS.md). The text below preserves the original research plan. A webcam prototype and two experimental training runs now exist; neither trained detector is approved for automatic sorting.

Prepared **2026-11-09**. This is a plan; **Phase 2 has not started**. The project directory was empty when inspected, with no existing application, Git metadata or applicable AGENTS.md discovered. Only the requested research documents and CSV are introduced.

## Executive summary

1. **Best practical starting approach:** object recognition followed by a separate Korean disposal-rule engine, with explicit confirmed-conflict blocking and a separately labeled uncertainty fallback. It exposes why a decision is made and can accommodate local rule changes without retraining the vision model.
2. **Architecture choice:** multi-object detection, per-instance Korean rules, and a batch agreement/uncertainty gate. Different object types may be sorted together when every supported final destination agrees. A whole-image classifier cannot establish this.
3. **First pretrained model:** YOLO26n detection (`yolo26n.pt`), fine-tuned on local instance annotations; compare YOLO11n. Neither is a proven project winner. Use YOLO26n-seg as the overlap/separation alternative; B0/MobileNetV3 are optional crop classifiers. [Model evidence](02_model_comparison.md).
4. **Data:** local Logitech images are essential. Use TrashNet and RealWaste selectively for auxiliary recognition; Korean AI Hub data is promising but access/terms must be verified. TACO boxes/masks are now a priority auxiliary detection source. Do not map public material labels directly to disposal outputs. [Dataset review](03_datasets.md).
5. **Hardest Korean cases:** paper cups versus cartons, clean versus soiled food packaging, multilayer/coated products, transparent drink PET versus other plastic, container glass versus ceramics/heat-resistant glass, and dedicated streams. Current guidance allows clean paper noodle cups in the paper stream subject to locality; a blanket “all coated-looking cups are general” is wrong. [Official item entry](https://www.wasteguide.or.kr/front/dischargeMethod/dictionaryView.do?niIdx=406).
6. **Minimize errors:** constrain presentation, verify preparation/site acceptance, calibrate on local data, distinguish detection warnings from classification fallback, require temporal consistency, latch one event per complete presentation, and evaluate held-out physical objects at matched coverage. Unknown classification uses UNSURE/general in usable scenes without a confirmed conflict; known unsupported items remain excluded.
7. **First Phase 2 work:** confirm site and machine specifications, approve an item whitelist and rules, capture a small pilot dataset and camera sequences, then compare YOLO26n and YOLO11n on multi-object scenes offline. Build the live preview only after validating this loop. No Arduino control is part of that first prototype.

**Primary recommendation:** YOLO26n detection + per-instance rules + complete-batch uncertainty/agreement gate. **Fallback alternative:** YOLO26n-seg when boxes cannot reliably separate touching objects. No model authorizes unresolved occlusion. The first implementation must support same-category batches and block confirmed mixed batches and emit general with UNSURE for usable classification-uncertain batches, not merely demonstrate single-object classification. See [ranked shortlist](02_model_comparison.md).

## Work packages and exit criteria

Indicative schedule for a small student team: 4–6 weeks, highly dependent on access, labeling and hardware. Effort ranges are estimates, not promises.

| Stage | Work | Concrete output / exit criterion | Estimate |
|---|---|---|---|
| 0. Scope and disposal review | Identify campus/building, municipality, collector and accepted mixed streams; inspect actual computer/camera; choose 12–16 object classes | Versioned locality profile, source list and whitelist; unsupported classes explicit; no ambiguous rule can issue command | 1–2 days |
| 1. Camera pilot | Validate OpenCV capture, focus, field of view, lighting, whole-tray ROI, empty/multiple/hand scenes | Pilot recordings and capture manifest; no assumption that requested resolution/FPS was honored | 1–2 days |
| 2. Ground truth and collection | Pilot 5–10 distinct objects per class; review labels; expand toward 30–50/class | Instance boxes, scene labels and object/session-grouped dataset; two-person rule adjudication; locked test manifest | 3–7 days plus ongoing collection |
| 3. Recognition benchmark | Fine-tune YOLO26n/YOLO11n on scene boxes; compare masks if instance separation fails | Reproducible configs, model cards, per-class recall, complete-scene recall, mixed-batch errors and CPU latency | 3–5 days |
| 4. Decision layer | Declarative rules, prerequisite checks, per-instance calibration, scene completeness, category agreement and rejection | Table-driven rule cases; confirmed-conflict priority; UNSURE/general for uncertain classifications; no command for detection failures or explicit rule blockers | 2–3 days |
| 5. Preview and event loop | Integrate capture, tracking, complete-batch stability, fresh final recheck, one-event latch and explanations | Local UI showing each box/label/confidence/stream plus batch status/reason; logged replayable events; no serial/servo code | 2–4 days |
| 6. Independent trial | Freeze model/rules/thresholds; unseen-object and challenge sessions | Accuracy/F1, confusion matrices, risk-coverage, unknown acceptance, latency and confidence intervals | 2–4 days |
| 7. Targeted improvement | Add difficult multi-item examples; test segmentation or crop classifier when observed errors justify it | New model/version and fresh locked evaluation; documented decision to proceed or narrow scope | 3–7 days |

The first pilot's role is to reveal camera/ontology mistakes, not to claim final accuracy. Do not begin expensive training or acquire full archives until the needed subset, license and compute budget are known. Any subsequent download requires the authorization requested in the original task.

## Proposed software boundaries

These paths are a future design; they are **not created now**.

| Module / artifact | Responsibility |
|---|---|
| `capture/` | OpenCV backend, timestamps, frame health, ROI and image collection |
| `vision/` | Detector, instance coordinates, optional masks/crop classifier, track association and confidence outputs |
| `rules/` | Versioned YAML/JSON profiles, official stream mapping, prerequisites, source URLs |
| `decision/` | Scene completeness, per-item unknown checks, batch agreement, final recheck and event latch |
| `ui/` | Live frame, object, confidence, official stream, destination or rejection reason |
| `data/manifest` | Object/session/source IDs, annotations, licenses and immutable split assignment |
| `training/` | Fine-tuning configs, seeds, model versions and dataset provenance |
| `evaluation/` | Independent metrics, calibration, risk-coverage, replay and hardware benchmarks |
| `interfaces/` | Pure decision-event contract; future hardware adapter stays absent until separately scoped |

Use a pinned Ultralytics/PyTorch detector after license review, OpenCV capture and a configuration-driven rule layer. TorchVision is optional for per-object crop experiments. Evaluate ONNX Runtime only after establishing a correct PyTorch baseline; conversion is an optimization step with its own prediction-parity check. Keep dependencies pinned and weights identified by checksum. No paid cloud API is needed for runtime.

## Required tests in the implementation phase

- Rule cases for every supported item, contamination exception, jurisdiction override and missing property; battery/carton/food tests must never produce a command under the initial profile.
- Group-split and duplicate checks; each physical object and its derived frames appears in one partition only.
- Model preprocessing parity and export parity if applicable; invalid class names or missing model files fail closed.
- Sequence tests for same-category batches, all mixed-category pairs, known-plus-unknown items, obscuration, lost tracks, same-count replacements, one event per presentation, no re-arm while occupied, camera disconnect and stale frames.
- Independent real-camera evaluation per [protocol](04_system_architecture.md). These tests are not claimed to have run in Phase 1.

## Information still required before deployment decisions

| Missing input | Why it matters | Interim assumption |
|---|---|---|
| Exact campus/building and collection contract | Household municipal advice may not match an institution's arrangements | Suwon and Gwanak are examples only; no site profile activated |
| CPU model, RAM, OS, optional GPU/VRAM | Determines local inference/export and training budget | Compact CPU-capable model; all FPS unvalidated |
| Logitech model, mounting distance, resolution and focus/exposure behavior | Small marks, transparency and motion blur may be unresolvable | Fixed camera with diffuse lighting; verify in pilot |
| Item dimensions and allowed preparation | Defines cropping, supported vocabulary and whether hidden residue can be excluded | Prepared, fully exposed batch; initial 1–5-item validation envelope |
| Operator availability and target throughput | Determines acceptable rejection and temporal delay | Supervised university demonstration |
| Dedicated PET/carton/glass handling and later manual separation | Three bins are not a full Korean collection system | Dedicated streams unsupported unless a specific compatible profile is approved |
| Dataset access eligibility and redistribution intent | AI Hub restrictions and model/dataset licenses affect choices | No account use, large downloads or redistribution performed |

## Risk register

| Risk | Mitigation / decision |
|---|---|
| Model sees familiar shape but wrong material | Mark/OCR or verified product evidence; otherwise manual review |
| Surface looks clean but interior is dirty | Preparation protocol, multi-view inspection or operator confirmation; do not infer absence |
| Dataset leakage inflates accuracy | Group splits, cross-source deduplication, later-session test |
| Official sources differ or change | Store jurisdiction/date/source and review conflicts before enabling rule |
| Three compartments mix separately collected streams | Narrow accepted items, keep separate collection outside system, or explicitly document downstream sorting |
| Unknown objects receive confident predictions | Held-out unknown-family tests, rejection thresholds, whitelist and supervised operation |
| Newer model looks faster only in vendor benchmark | Batch-1 end-to-end measurement on actual computer |
| Model upgrade silently changes behavior | Freeze checkpoints/preprocessing/rules and rerun the independent protocol |

Phase 1 ends with these research deliverables. No camera application, training job, Arduino communication or flap movement is initiated.

## Revised decision-layer acceptance criteria

Implement configurable candidate/recognition/category thresholds and temporal settings; log their version. Use the [current architecture truth table](04_system_architecture.md): confirmed conflict first, usable-scene classification fallback second, confident agreement third. Verify all seven requested examples, plus paper+unknown, empty view, threshold crossings, unsupported objects and occlusion warnings. Both READY and UNSURE require stable observations, fresh final recheck and one-event latching. UNSURE remains a status, never a fourth command; outgoing vocabulary stays paper/recycling/general. Show individual confidence and name every uncertain object. No Arduino/servo code is added by this documentation change.

## Prototype implementation checkpoint — 2026-11-11

A first supervised prototype now exists under `waste_sorter/`; earlier “not implemented” statements describe the research-phase snapshot. See the repository README for setup and current limitations. Implemented: OpenCV preview/record capture, optional local YOLO detection adapter, configurable category policy, temporal gate and console-only events. Tests cover policy and gating. Still outstanding: trained waste weights, validated site/condition rules, calibrated confidence, robust tracking/occlusion/completeness, real webcam evaluation and runtime profiling. Camera-only mode is not a waste classifier. No Arduino interface exists.
