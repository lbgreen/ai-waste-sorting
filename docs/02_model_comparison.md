# Model comparison and recommendation

Research cutoff: **2026-11-09**. Phase 1 only: no training, weights, webcam experiments, or measured project accuracy. **Verified** means supported by the linked publication/documentation; **recommendation** means engineering judgment; **unvalidated** means a Phase 2 experiment is necessary. See [bibliography](06_references.md).

## Decision — revised for multiple objects

**Primary recommendation:** fine-tune **YOLO26n detection** on local multi-item scenes, apply Korean disposal rules **per instance**, then apply the revised policy: confirmed category conflict blocks; otherwise classification uncertainty in a usable scene produces UNSURE/general; fully confident agreement produces READY/shared category. Explicit scene-completeness, uncertainty, tracking and temporal gates are required. Start from `yolo26n.pt`, not a `-cls` checkpoint. Compare YOLO11n with matched labels, splits and runtime. Neither is a proven winner on this project.

**Fallback:** YOLO26n instance segmentation (`yolo26n-seg.pt`) plus the same rules/gates when box ambiguity or touching objects limits detection. Masks may improve separation but cannot recover invisible objects or prove a stack is homogeneous. Request users to spread obscured items out; refuse authorization while visibility is unresolved. YOLO11n remains a compatibility alternative within the detection approach. [Detection family](https://docs.ultralytics.com/models/yolo26), [instance segmentation](https://docs.ultralytics.com/tasks/segment/).

The earlier whole-image EfficientNet-B0 recommendation applied to a single-item setup and is superseded. Whole-image classification, including YOLO classification variants, cannot enumerate arbitrary individual objects. B0/MobileNetV3 can still classify **validated per-object crops** as optional second-stage experiments; they cannot replace scene detection or rescue missed objects. Three-bin agreement is checked after rules, not by requiring identical object classes.

## Ranked shortlist

| Rank | Approach | Why it fits | Main limitation / experiment |
|---|---|---|---|
| 1 | YOLO26n detector + per-instance rules + batch policy gate | Boxes, object labels and confidence for multiple items; lowest annotation complexity among the proposed multi-instance solutions | Measure complete-scene recall, small-object misses and mixed-batch false acceptance |
| 2 | YOLO26n-seg + per-instance rules + batch policy gate | Individual masks can help separate touching shapes and identify unexplained foreground | More annotation/runtime cost; hidden surfaces still require rejection |
| 3 | Detector + crop classifier (B0 or MobileNetV3) + rules | May improve confusing object/material labels after localization | Extra compute; overlapping crops can contain multiple objects; detector recall remains a bottleneck |

A frozen SigLIP 2 crop probe remains an optional research baseline. It is not a substitute for enumeration. All recommendations require local validation; no measured accuracy is asserted.

## Conventional classifiers

Verified publisher metadata below concern **ImageNet-1K**, not waste or this webcam. Different recipes and preprocessing prevent attributing all differences to architecture. File sizes are checkpoint MiB, not peak RAM. Values are rounded; local waste heads change parameter counts slightly.

| Model / weights | ImageNet top-1 | Parameters | Published operations | Checkpoint | Project interpretation |
|---|---:|---:|---:|---:|---|
| MobileNetV3-Large V2 | 75.274% | 5.48M | 0.217G | 21.1 MiB | First CPU-oriented challenger; low operation count does not guarantee lower latency on every backend |
| EfficientNet-B0 V1 | 77.692% | 5.29M | 0.386G | 20.5 MiB | Optional crop-classification candidate; not a whole-scene decision model |
| ResNet18 V1 | 69.758% | 11.69M | 1.814G | 44.7 MiB | Simple, mature sanity baseline; larger than compact candidates |
| ConvNeXt-Tiny V1 | 82.520% | 28.59M | 4.456G | 109.1 MiB | Test if small CNN errors remain after improving data; more compute and training memory |

Sources: [MobileNetV3 metadata](https://raw.githubusercontent.com/pytorch/vision/main/torchvision/models/mobilenetv3.py), [EfficientNet metadata](https://raw.githubusercontent.com/pytorch/vision/main/torchvision/models/efficientnet.py), [ResNet metadata](https://raw.githubusercontent.com/pytorch/vision/main/torchvision/models/resnet.py), [ConvNeXt metadata](https://github.com/pytorch/vision/blob/main/torchvision/models/convnext.py). Operations follow the publisher's counting convention.

ResNet50 and EfficientNetV2-S are reasonable larger controls if a GPU and training budget are available, but neither resolves hidden-material ambiguity. Avoid a broad model sweep before establishing clean labels and independent evaluation. Standard classifiers can fine-tune a replaced head first, then selected backbone layers. Do not train from scratch on a few thousand webcam images.

Modern lightweight transformers deserve consideration: **MobileViTv2** uses separable attention; its paper reports a roughly 3M-parameter variant at 75.6% ImageNet top-1. **FastViT-T8** has a released ImageNet checkpoint and reports 76.2% top-1 and 0.8 ms on an iPhone 12 Pro benchmark. Those mobile measurements do not predict desktop Python latency. Their conversion, reparameterization and checkpoint preprocessing deserve explicit verification before adoption. Neither paper establishes superiority on Korean waste. [MobileViTv2 paper](https://arxiv.org/abs/2206.02680), [FastViT official repository](https://github.com/apple-aiml-research/ml-fastvit).

## YOLO detection, classification and segmentation

Both YOLO11 and YOLO26 support detection, classification and instance segmentation. A `-cls` checkpoint is a whole-image classifier; choosing it does not add object localization. The current documentation recommends both families for stable workloads. YOLO26 is available by this cutoff, rather than merely a future proposal. [Supported models](https://docs.ultralytics.com/), [YOLO26 paper](https://arxiv.org/abs/2606.03748).

| Published configuration | Benchmark / score | CPU ONNX inference | T4 TensorRT inference | Parameters |
|---|---|---:|---:|---:|
| YOLO11n detection, 640 px | COCO mAP50–95 39.5 | 56.1 ms | 1.5 ms | 2.6M |
| YOLO26n detection, 640 px | COCO mAP50–95 40.9; end-to-end 40.1 | 38.9 ms | 1.7 ms | 2.4M fused |
| YOLO11n-cls, 224 px | ImageNet top-1 70.0% | 5.0 ms | 1.1 ms | 2.8M |

Sources: [YOLO11 official metadata](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo11.md), [YOLO26 official table](https://docs.ultralytics.com/models/yolo26). YOLO26 timing selects its NMS-free head; do not pair the larger non-end-to-end score with that runtime as a single operating point. Its fused parameter count differs from training checkpoint counts. The documentation's CPU comparison uses an Intel Xeon at 2.00 GHz; these are publisher measurements, not our hardware.

Derived throughput ceilings are approximately 17.8, 25.7 and 200 images/s respectively from `1000 / latency_ms`. They exclude capture, buffering, preprocessing, display and stable-decision delay; they are **not promised webcam FPS**. Detection mAP and classification accuracy have different denominators and cannot be ranked against one another. YOLO26 classification variants are available but no locally comparable accuracy/latency result exists.

Detection is now mandatory in the proposed architecture because multiple individual items must be resolved. Use segmentation only if boxes include substantial distracting material or overlapping objects defeat counting. Segmentation adds pixel labels and computation; masks cannot reveal a bottle's unseen interior. COCO class coverage omits many relevant waste types. A detector's failure to find a second object is not proof of a single item.

## Vision-language alternatives

| Candidate | Verified capability | Practical project use | Limitation |
|---|---|---|---|
| CLIP ViT-B/32 | Image/text embedding comparison; zero-shot labels; linear-probe example | Quick baseline with concrete object prompts | Candidate-relative similarity is not probability of correct disposal; prompt sensitivity |
| OpenCLIP | Open implementation and many pretrained checkpoints | Reproducible frozen-feature experiments | Checkpoint choice, training data and preprocessing substantially affect results |
| SigLIP / SigLIP 2 Base | Sigmoid image-text training; SigLIP 2 improves multilingual and dense representations | Test frozen image embeddings + local object-label probe; compare English/Korean prompts | Semantics still cannot infer invisible coatings or collector acceptance |
| MobileCLIP / smaller encoders | Potential efficiency-focused research alternative | Consider only if large encoder cost blocks a useful feature baseline | Verify exact weight license and desktop runtime before selection |

Sources: [CLIP implementation](https://github.com/openai/CLIP), [OpenCLIP](https://github.com/mlfoundations/open_clip), [SigLIP paper](https://arxiv.org/abs/2303.15343), [SigLIP 2 paper](https://arxiv.org/abs/2502.14786), [Google checkpoint](https://huggingface.co/google/siglip2-base-patch16-224), [MobileCLIP licensing](https://github.com/apple-aiml-research/ml-mobileclip/blob/main/LICENSE).

Recognizing familiar object names without training is plausible; reliable automatic Korean disposal without task-specific validation is not established. Compare prompts such as “a disposable paper cup” and “a clear plastic drinking cup,” not abstract destination labels alone. Cache text embeddings; only the image tower needs to run per frame for a fixed vocabulary. SigLIP 2 Base's vision tower is approximately 86M parameters, already much larger than B0; complete checkpoints also include a text tower. Measure peak resident memory, not just weight size. Few-shot means training or selecting from a few labeled examples per class; it does not eliminate the need for many independent test objects.

## Evidence from actual waste research

TrashNet's authors report approximately 75% test accuracy for their historical CNN with a 70/13/17 image split. This establishes a baseline on their six-category white-background task, not a ceiling for modern fine-tuning. [Original repository](https://github.com/garythung/trashnet).

A more relevant domain-shift comparison is the **2023 RealWaste paper, Table 4**: Inception V3 scored 49.69% when trained on pristine-object DiversionNet versus 89.19% with RealWaste training on the paper's landfill test; MobileNetV2 scored 27.65% versus 88.15%. These are within-study comparisons, not our measurements. They support collecting deployment-domain data and show that a compact model can be competitive; they do not establish MobileNetV3 or B0's expected accuracy. [Published paper](https://mdpi-res.com/d_attachment/information/information-14-00633/article_deploy/information-14-00633.pdf?version=1701065549).

The **2025 SwinConvNeXt paper** reports 98.97% on its Kaggle garbage-classification task. Its table also aggregates results from other publications, which should not be treated as one controlled head-to-head benchmark. The headline is insufficient to prefer a fused transformer/CNN for this chamber without matching splits, leakage checks, compute and Korean destination labels. [Author article](https://pmc.ncbi.nlm.nih.gov/articles/PMC11889143/).

TACO's original study reports 1,500 contextual litter images and 4,784 instances and studies detection/segmentation; ZeroWaste studies deformed objects in industrial clutter. These tasks support investigating localization when the scene requires it, but do not measure household disposal compliance. [TACO paper](https://arxiv.org/abs/2003.06975), [ZeroWaste paper](https://arxiv.org/abs/2106.02740).

The 2025 study *Robust and Label-Efficient Deep Waste Detection* reports poor class-name-only open-vocabulary performance on ZeroWaste and improvement through prompt optimization. This cautions against treating a generic zero-shot model as a finished sorter; it is not a direct test of our SigLIP probe. [Author preprint and code link](https://arxiv.org/abs/2508.18799).

No reviewed evidence establishes a controlled winner across B0, MobileNetV3, YOLO26 and SigLIP on the same Korean webcam objects and rules. Consequently, **waste accuracy, unknown-object acceptance, lighting robustness and visually similar-material performance remain unmeasured for every shortlisted model**. Published high percentages on random web-image splits must not be presented as expected bin accuracy.

## Deployment, training and robustness comparison

| Family | Data/annotation effort | CPU / GPU and memory expectation | Fine-tuning complexity | Robustness and unseen objects |
|---|---|---|---|---|
| Compact CNN | Image-level labels; local data essential | Most promising CPU starting point; optional GPU training/inference; tens of MiB weights plus runtime | Low–moderate | Needs varied products, lighting and rejected examples; closed-set confidence can be high on unknowns |
| ConvNeXt / larger CNN | Same labels; additional capacity must be justified | Higher RAM/compute; GPU helpful | Moderate | Potentially richer features, no guaranteed unseen-object improvement |
| MobileViTv2 / FastViT | Same labels; exact processor and export required | Potentially efficient; desktop kernel support matters | Moderate | Benchmark locally; transformer structure alone does not ensure robustness |
| YOLO detector | Boxes per instance; negatives and multiple-item scenes | Nano variants plausible on CPU; GPU optional; higher-resolution activations | Moderate | Better localization, but small/occluded items can disappear |
| Segmentation | Masks and instance identity | More annotation/runtime work | High relative to fixed crop | Helpful in clutter; transparent materials remain difficult |
| VLM frozen probe | Object labels; zero-shot baseline needs none | Larger encoders; GPU helpful, offline CPU possible but unbenchmarked | Low for probe; high for full fine-tuning | Semantic transfer helps unfamiliar appearances; open vocabulary is not a reliable unknown detector |

All can ingest NumPy camera frames through Python preprocessing and operate offline after dependencies and weights are obtained. None needs a Logitech-specific network architecture. OpenCV handles capture; test the actual webcam, OS backend, exposure and focus. GPU choices include CUDA where supported and platform-specific accelerators; do not assume the eventual machine matches this research workstation. [VideoCapture documentation](https://docs.opencv.org/4.x/d8/dfe/classcv_1_1VideoCapture.html).

For every candidate, use consistent whole-object crops, physical-object-separated data, moderate exposure/color augmentation, blur/glare challenge sets and realistic partial occlusion. Do not erase material cues with excessive color augmentation or crop away labels during evaluation. Lighting hardware and local examples may provide greater gains than moving to a larger model; this is a hypothesis to test.

## License and reproducibility decisions

- TorchVision code uses BSD-3-Clause; its documentation distinguishes model-weight/data terms from software licensing. Keep the exact weight identity and applicable notices. [License](https://github.com/pytorch/vision/blob/main/LICENSE), [model documentation](https://docs.pytorch.org/vision/stable/models.html).
- Ultralytics offers AGPL-3.0 and Enterprise licensing. A university project is not automatically exempt from applicable conditions. Record intended distribution and consult the actual terms before selecting it for a closed product. [YOLO26 documentation](https://docs.ultralytics.com/models/yolo26).
- CLIP and OpenCLIP implementations use MIT; OpenCLIP checkpoints need their own provenance review. The Google SigLIP 2 checkpoint is Apache-2.0. [CLIP](https://github.com/openai/CLIP), [OpenCLIP](https://github.com/mlfoundations/open_clip), [checkpoint](https://huggingface.co/google/siglip2-base-patch16-224).
- Apple model repositories can have separate code/model terms: inspect the selected checkpoint license rather than generalizing from another Apple model. [FastViT license](https://github.com/apple-aiml-research/ml-fastvit/blob/main/LICENSE).

## Controlled selection experiment

Compare YOLO26n and YOLO11n on identical multi-object scene splits, object ontology and tuning budgets. Run three seeds if practical. Compare full-scene recall and **batch false authorization at matched coverage**, alongside mAP. Add segmentation if touching-object misses dominate; test B0/MobileNetV3 on detected crops only if recognition errors dominate. Include detector errors in every end-to-end result; ground-truth crop accuracy is only an upper-bound diagnostic.

Measure batch-1 warm and cold inference, median/p95 end-to-end delay, CPU thread count, peak RAM, accelerator and export precision. Recheck calibration and sorting errors after ONNX conversion or quantization. Select the simplest model meeting the risk/coverage target in [evaluation protocol](04_system_architecture.md), not the model with the highest unrelated benchmark number.

## Updated uncertainty policy

Model choice remains detection-first. Configurable confidence thresholds determine the set of confident per-item destinations; conflict in that set blocks before classification fallback. An uncertain identity/category produces UNSURE/general only with a usable scene and no explicit rule blocker. Detection/count/occlusion failures are warnings with no command; known unsupported streams remain excluded. Compare **actual disposal errors including fallback**, not merely confidence or policy-conformance. No research benchmark cited above validates general as the correct disposal route for every unknown item. See [current policy and pseudocode](04_system_architecture.md).
