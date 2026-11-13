# First public-data training experiment — 12 November 2026

**Completed, but rejected for deployment: detection quality is insufficient.** This is an experimental baseline, not a trained production sorting system.

## Data and experiment

Source: the [reviewed TACO annotations](https://github.com/pedropro/TACO). The annotation file and its SHA-256 are retained locally. The lightweight preparation excludes 466 original-only images and one exact duplicate from the 1,500 source records. Images remain local; source-specific rights metadata is incomplete and no blanket redistribution permission is claimed.

| Split | Images | Object boxes |
|---|---:|---:|
| Train | 687 | 2,178 |
| Validation | 119 | 432 |
| Test | 227 | 716 |

Whole source batches were assigned deterministically to partitions. Exact duplicates were removed, retaining held-out copies preferentially. Physical-object independence and near-duplicate absence are not established. Thumbnail aspect ratios were checked against source dimensions (none differed by more than 1%). All source instance boxes in retained images were preserved.

YOLO26n was fine-tuned from the local pretrained checkpoint for 20 epochs at 320 px, batch 4, seed 42, Apple MPS. The training loop and per-epoch validation took approximately 380 seconds; this excludes data acquisition, setup, final validation and separate test evaluation. A separate one-epoch pilot verified the pipeline first. The selected checkpoint was evaluated once on the public test split. No thresholds were tuned on that test set.

## Results

| Metric | Validation, selected epoch | Held-out public test |
|---|---:|---:|
| mAP@50 | 5.10% | 4.21% |
| mAP@50–95 | 2.82% | 2.96% |

These are detection metrics, not disposal accuracy or a percentage of correctly sorted items. The low values do not justify deployment. Validation covered 40 of the 60 source classes and test covered 41; aggregate metrics do not establish performance on absent classes. Two classes (`Carded blister pack`, `Plastified paper bag`) have no training instances; 35 classes have fewer than 20 training boxes. No C920 images, Korean disposal labels, temporal safety sequences or calibrated unknown-rejection evaluation were available for this experiment.

## Artifacts

- `weights/taco_yolo26n_baseline.pt`: copied best checkpoint, retained locally.
- `runs/waste_training/detector/`: configuration, curves, checkpoints and per-epoch CSV.
- `runs/waste_training/training.log`: complete training log.
- `runs/waste_evaluation/test/`: test plots and machine-readable metrics.
- `docs/training_baseline_metrics.json`: retained metrics and checkpoint hash.
- `datasets/taco_yolo/`: images, labels, source manifest, exclusions and split provenance.

Data and weights are ignored by Git. The existing live detector and disposal configuration were not changed. In particular, TACO class names must not be passed into the current policy without reviewing unsupported-class mappings and the Korean rules.

## Next experiment

Define a smaller recognition taxonomy aligned with the bin's target objects, retaining all annotated foreground and a separate category for other litter rather than dropping it into background. Preserve safety-relevant distinctions such as batteries, food and beverage cartons. Improve training coverage and compare learning curves at a higher input resolution. The public test results above are now known and must not be repeatedly used for model selection. Reserve new local C920 objects/sessions for final evaluation. Any revised model still needs condition/preparation evidence and the existing uncertain/mixed-waste policy before it can sort items.
