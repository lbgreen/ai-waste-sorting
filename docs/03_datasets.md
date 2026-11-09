# Dataset research and collection strategy

Research cutoff: **2026-11-09**. No image archives or model weights downloaded. Public metadata was inspected, including TACO's annotation JSON in memory. Counts below describe identified releases, not a filesystem audit of downloaded images. **None of these datasets supplies validated Korean legal disposal labels.**

## Recommended order

1. Build a local Logitech dataset with physically verified object identity, preparation status and a reviewed site-specific disposal label.
2. Use TrashNet and RealWaste as optional auxiliary material-recognition data. Compare ImageNet→local fine-tuning with ImageNet→public waste→local; intermediate waste training is an experiment, not an assured improvement.
3. Review a small authorized Korean AI Hub subset if an eligible team member can obtain access. Its products and scene diversity may help more than another generic web compilation.
4. Detection is now required: prioritize TACO and authorized AI Hub boxes/masks as auxiliary sources. Keep ZeroWaste for overlap/clutter stress research. TrashNet and RealWaste image labels alone cannot train or evaluate complete multi-object enumeration.

Links in each entry lead to the original download page or repository. Preserve licenses and source IDs when combining data.

## Core datasets

| Dataset / release | Size and labels | Resolution and annotation | Scene, balance and condition coverage | License / access | Fit |
|---|---|---|---|---|---|
| [TrashNet](https://github.com/garythung/trashnet), [author HF mirror](https://huggingface.co/datasets/garythung/trashnet) | 2,527; glass 501, paper 594, cardboard 403, plastic 482, metal 410, trash 137 | 512×384 resized release; one image-level class | White board; sunlight/room light; small trash class; no systematic clean/dirty labels | MIT repository/license; retain author attribution and mirror provenance | Good starter classification data; weak unknown/background coverage; material labels cannot directly select bins |
| [RealWaste, UCI](https://archive.ics.uci.edu/dataset/908/realwaste), donated 2023-10-17 | 4,752; cardboard 461, food organics 411, glass 420, metal 790, miscellaneous trash 495, paper 500, plastic 921, textile trash 318, vegetation 436 | 524×524; image-level material labels | Authentic landfill reception; realistic deformation/dirt; plastic is largest class; cleanliness severity not separately annotated | CC BY 4.0; direct archive, approximately 656.6 MB; original full resolution requires author contact | Useful domain diversity; landfill scene differs from chamber; food and textiles do not imply GENERAL |
| [TACO original benchmark](https://arxiv.org/abs/2003.06975), [toolkit/download](https://github.com/pedropro/TACO) | 1,500 images, 4,784 objects, 60 fine classes; hierarchical object/material labels including bottles, cans, cups, bags, cartons, paper and cigarette litter | COCO boxes/polygons; varied resolution, not a fixed classifier crop | Outdoor litter, roads/beaches/woods; strong long tail, occlusion; weathered items but no legal cleanliness labels | MIT toolkit is not a blanket image license; image permissions/provenance need audit; original annotation JSON has empty top-level `licenses` | Detection/segmentation; crops can supplement classification if parent-scene split is preserved |
| [ZeroWaste](https://ai.bu.edu/zerowaste/), [official repository/download DOI](https://github.com/dbash/zerowaste) | Common ZeroWaste-f release: 4,503 labeled images; cardboard, soft plastic, rigid plastic, metal | Instance/semantic segmentation; confirm exact resolution and split from chosen archive before use | Industrial conveyor, dense clutter and deformed waste; paper/background and material frequency differ from household setting; no preparation labels | Dataset CC BY-NC 4.0; code MIT; [download DOI](https://doi.org/10.5281/zenodo.4899926) | Specialized localization research; poor first choice for a single clean chamber item |

TrashNet metadata: [author README](https://github.com/garythung/trashnet), [license](https://github.com/garythung/trashnet/blob/master/LICENSE). RealWaste counts and terms: [UCI record](https://archive.ics.uci.edu/dataset/908/realwaste). TACO counts independently matched its [official annotation file](https://raw.githubusercontent.com/pedropro/TACO/master/data/annotations.json); image widths range 842–6,000 pixels in that metadata. The JSON is metadata, not the image archive. The author's repository explicitly distinguishes reviewed and unofficial annotations. ZeroWaste's dataset/code license distinction is explicit in its [README](https://github.com/dbash/zerowaste); the 4,503-image count is also tabulated by the [WACV 2026 StreetView-Waste authors](https://openaccess.thecvf.com/content/WACV2026/supplemental/Paulo_StreetView-Waste_A_Multi-Task_WACV_2026_supplemental.pdf). Exact ZeroWaste archive dimensions/class counts remain unverified here.

TACO categories are finer than the displayed examples: retain the full taxonomy rather than inventing a three-bin collapse. A Hugging Face repack documents mixed image rights and labels its annotations CC BY 4.0, but that does not cure missing rights metadata in the original archive. [Repack card](https://huggingface.co/datasets/pictograph/taco/blob/main/README.md). Use the original source chain and clarify missing permissions before redistribution.

## Korean dataset

[AI Hub: 생활 폐기물 이미지, dataset 140](https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=140) was built in 2020, opened 2021-06-25, with sample release recorded 2022-10-13. Its table distinguishes **150,000 records (건) and 750,000 images (장)**, evenly listed as 10,000 records/50,000 images per category. Do not call these 750,000 independent physical objects.

The 15 classes are furniture, scrap metal, wood, ceramics, film, foam, glass bottles, clothing, bicycles, electronics, paper, cans, PET bottles, plastic and fluorescent lamps. Schema: 1920×1080 resolution field, box/polygon coordinates, object count, damage, transparency and capture metadata. Indoor/outdoor/studio and day/night fields are documented; actual distribution and condition-label quality require sample inspection. No clean-versus-contaminated legal decision annotation is established.

The page limits applications to Korean nationals and requires approved access for API downloads. An open catalog listing is not an unrestricted license. Confirm current dataset terms and team eligibility before acquisition. It is promising for recognition/localization and unsupported-item examples, but still requires local Korean disposal adjudication. [Official metadata and access notice](https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=140).

## Additional publicly listed candidates

| Candidate | Size/categories | Annotation / resolution / conditions | Quality and license assessment | Recommendation |
|---|---|---|---|---|
| [Mostafa Mohamed, Garbage Classification](https://www.kaggle.com/datasets/mostafaabla/garbage-classification) | Author notebook says 15,150 images, 12 classes: paper, cardboard, biological, metal, plastic, three glass colors, clothes, shoes, batteries, trash | Classification folders; exact dimensions unverified; mixed web/other dataset sources; contamination labels not established | Other publications report 15,515, so count is unresolved without archive/version audit. Direct dataset page did not render readable metadata; license not independently verified | Optional only after deduplication and rights audit; do not treat as independent of TrashNet-derived compilations |
| [Garbage Dataset V2, pinned Kaggle version](https://www.kaggle.com/dsv/10182596) | 19,762; metal 1,020, glass 3,061, biological 997, paper 1,680, battery 944, trash 947, cardboard 1,825, shoes 1,977, clothes 5,327, plastic 1,984 | Class labels; dimensions not verified; mixed household/web imagery; no verified boxes or contamination severity | Card declares MIT; provenance of constituent images still requires review. Clothes are 5.6× batteries: not balanced despite card wording | Optional larger classification pool; battery labels useful for rejection, never GENERAL |
| [GlobalWasteData (GWD), February 2026 preprint](https://arxiv.org/abs/2602.07463) | Authors report 89,807 images, 14 main categories, 68 subclasses | Aggregation of prior datasets; harmonized labels; resolution and actual archive inventory unverified | Authors report filtering/deduplication; independent validation not performed. Underlying source licenses and an actionable download release were not verified | Discovery lead, not a ready dependency. Obtain manifest and download/license evidence before committing |
| [MJU-Waste original project](https://github.com/realwecan/mju-waste) | 2,475 RGB/depth pairs; single waste foreground class; 1,485/248/742 train/val/test | 640×480, pixel masks; PASCAL VOC and COCO instances; campus objects held by people in a lab | No material balance or cleanliness-label guarantee; repository [MIT license](https://raw.githubusercontent.com/realwecan/mju-waste/master/LICENSE); preserve archive terms | Optional foreground segmentation data; Logitech RGB lacks depth; paired modalities are not 4,950 independent objects |

The Mostafa count and reuse disclosure come from the [uploader's notebook input page](https://www.kaggle.com/code/mostafaabla/garbage-classification-keras-transfer-learning/input); inconsistent counts are intentionally not reconciled by guessing. GWD is a **preprint**, not proof that merging datasets improves this project's test accuracy. Kaggle download may require authentication/acceptance of terms; Hugging Face mirrors also require inspecting card, revision and original provenance. No accounts or terms were accepted during this phase.

MJU-Waste dimensions, paired-image counts and acquisition method are verified in its [author paper, Table 1 and section 4.1](https://arxiv.org/html/2007.04259v1). Its published image-level split is not evidence of physical-object independence; re-group if used for project validation.

## Why material labels are insufficient

These are proposed ontology rules, not automatic annotations:

| Source label | Safe use in recognition | Forbidden shortcut |
|---|---|---|
| paper / cardboard | Material supervision with unknown condition | All paper → PAPER |
| plastic | Broad material label; add object, resin/mark and preparation attributes locally | All plastic → RECYCLING |
| glass | Appearance supervision; distinguish container vs ceramic/heat-resistant glass locally | All glass → RECYCLING |
| trash | Retain source meaning only; manually inspect | “trash” is a universal Korean GENERAL class |
| biological / food organics | Out-of-scope/food-stream examples | Organic → GENERAL |
| battery / electronics | Unsupported recognition and rejection tests | Any of the three compartments |

Do not label a public image “clean” merely because residue is not visible. Keep missing attributes `unknown`; omit their loss or exclude them from condition training. Public material images can train the backbone without supplying a disposal target.

## Local collection plan — engineering recommendation

Start with **12–16 supported object classes**, plus explicit unsupported examples and empty/hand/multiple-item scenes. Candidate classes include office paper, cardboard, paper cup, paper noodle cup, carton, clear drink bottle, other plastic container, film wrapper, can, glass bottle, tissue and thermal receipt. Cartons and some others can be recognized yet remain unsupported for actuation.

Aim initially for **30–50 distinct physical objects per object class**, 8–12 deliberately varied views each: about **360–800 objects and 2,880–9,600 images**. These are planning ranges, not proven sample-complexity requirements. Use learning curves to decide expansion. Obtain different products/brands and condition examples, rather than many adjacent video frames of the same object. Reserve additional unknown families not used in training or threshold tuning.

Capture repeat sessions across at least three days with normal, dimmer and side-lit conditions; vary orientation, position, crushing and label attachment. Use safe, nonhazardous representatives for unsupported tests. Photograph clean/dirty pairs under supervision, preserving the same object ID across both conditions. A stain is not automatically unrecoverable contamination; annotate the actual preparation outcome independently of the image.

Required manifest: `image_id`, `physical_object_id`, `product_family_id`, `session_id`, `source_dataset`, `source_image_id`, `split`, `object_class`, `material`, `condition`, `preparation_verified`, `supported_stream`, `municipality_profile`, `rule_version`, `disposal_label`, `annotator`, `adjudication`, `license`, image hash, crop coordinates and capture settings. Unknown is a valid attribute value. Keep operational serial labels separate from research ontology.

Two people should label legal destination independently using the selected municipal/site profile; resolve disagreements and retain uncertainty. Photograph identifying marks separately for ground truth without giving test inference unavailable information. Avoid faces and personal shipping information in retained images.

## Combining datasets without leakage

Deduplicate by exact hash, perceptual similarity and manual review across **all** candidate datasets before splitting. Group by physical object, product family when feasible, source photograph and video/session; all derivatives, masks, crops, clean/dirty views and augmentations remain in one split. A Kaggle mirror of TrashNet is not an independent test set. Industrial consecutive frames can leak the same moving object.

Use local-only validation/calibration and an untouched local test. Public data belongs in training or a separately named domain-shift evaluation, not silently in the local test. Compare local-only fine-tuning against public-assisted fine-tuning with matched local labels and tuning budgets. Balance source sampling so landfill/web data does not overwhelm chamber data. Inspect per-class confusion and rejected cases before adding more data. Full split and test design is in [system architecture](04_system_architecture.md).

## Multi-object extension — revised collection and annotation plan

Retain the distinct physical-object targets above, but collect **scene annotations and short sequences**, not just isolated classification images. Start with 1–5 separated objects per tray; this is a proposed validated capacity, not a permanent product limit. Larger/overloaded or stacked presentations return `WARNING_DETECTION` with no command until evaluated. Add 600–1,000 deliberately arranged scenes across single items, homogeneous identical items, homogeneous different object types, mixed destinations, and known-plus-unknown/unsupported objects. Aim for 50–100 short enter/leave/occlude/replace sequences. These are planning quantities, not proven requirements; expand rare errors using learning curves.

Annotate every visible instance with box coordinates, object class, physical-object ID, track ID within sequence, material/condition evidence, official stream, supported destination or rejection reason, truncation, occlusion and visibility uncertainty. Draw visible masks for the overlap subset if comparing segmentation. Record ground-truth instance count and batch eligibility. Unidentifiable foreground must be annotated, never silently treated as background. If instance boundaries/count are resolved, unknown identity is classification uncertainty eligible for UNSURE/general; unresolved foreground extent/count is a blocking detection warning. A detached cap is a separate item; an attached cap is part of its bottle unless the annotation convention explicitly says otherwise.

Split **object pools before constructing scenes**. All scenes sharing a physical object, their source clips and derived crops must stay in one partition; otherwise grouping by scene alone leaks objects. Use disjoint products/sessions for final tests. Separate real occlusion sequences from synthetic copy-paste augmentation; synthetic scenes are training supplements, never evidence of webcam reliability. Keep true count and occlusion labels even when the detector misses an item.

Public boxes/polygons in [TACO](https://github.com/pedropro/TACO), [AI Hub](https://www.aihub.or.kr/aihubdata/data/view.do?dataSetSn=140) and [ZeroWaste](https://github.com/dbash/zerowaste) are relevant, but their classes still need ontology review. Public image-level datasets must not be assigned fabricated full-frame boxes for multi-object training. The same-category/mixed/uncertain **batch label is derived from adjudicated per-item rules and scene visibility**, not the dominant material or filename. Test all three destination pairs and the three-way mixture, plus different object classes with the same final destination.

## Labels for the revised fallback policy

Keep `ground_truth_disposal` separate from `policy_status`, `policy_destination` and `assignment_basis`. Add per-instance recognition score/source, threshold-profile version, uncertainty reason and batch uncertain IDs. A policy-generated general label must never overwrite an unknown or recyclable ground-truth label or become an automatic training target. Distinguish well-localized unknown objects from unresolved detection regions and known unsupported streams.

Include unknown alone, recycling+unknown, paper+unknown, confident-general+unknown and paper+recycling+unknown. Expected policy outcomes are UNSURE/general for the first four and ERROR_MIXED_WASTE/no command for the last, once scene/rule prerequisites pass. Include confidence-threshold crossings and stable fallback sequences in the temporal test set. Report policy correctness and actual disposal correctness independently.
