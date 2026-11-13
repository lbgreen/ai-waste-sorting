# Project collaboration instructions

These preferences were explicitly requested by the project owner:

- Keep `lbgreen/ai-waste-sorting` PUBLIC. This supersedes the earlier private-repository preference. Do not change visibility unless asked.
- After meaningful changes, update `DEVELOPMENT_STATUS.md` with the current implementation, actual validation results, known limitations, artifact locations and concrete next steps so teammates can continue.
- Run checks appropriate to the changes, commit the project changes and push to the current intended GitHub branch. The owner has requested this routinely; ask for tool/sandbox approval only when technically required. Do not claim a push succeeded without verification.
- Do not force-push or overwrite teammates' work. Inspect remote changes before integrating or pushing.
- Keep credentials, datasets, camera captures, virtual environments, training output directories and model binaries out of Git. Document how teammates can reproduce or obtain local-only artifacts.
- The system targets small waste portions (initial training envelope: 1–3 objects). Preserve mixed-waste blocking, separate UNSURE/general fallback, empty-scene/no-command behavior and Korean disposal rules. No Arduino/servo control until separately requested.
- Record training metrics honestly. Recognition metrics are not sorting accuracy, and experimental models must not silently replace the live model.
