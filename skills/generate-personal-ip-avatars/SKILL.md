---
name: generate-personal-ip-avatars
description: "Design a gender-adaptive personal-IP cartoon system from one portrait for users with no art background. Provides independently switchable modules for classic and random color themes, eight action designs, a front-facing full-body character, eight-angle turnaround portraits, a comprehensive 24-emotion pack, user-requested color themes, per-series collages, and one all-images collage. All features default on. Use for personal IP, cartoon identity, character sheets, expression packs, turnarounds, avatar blind boxes, or expansion of an approved character set."
---

# Generate Personal IP Avatars

Build a recognizable, non-photorealistic IP character system from one portrait. All modules default on, but the user may enable or disable each module in the opening request.

With defaults, generate nine series: one classic plus eight blind-box random themes. Each series contains 41 originals:

- 8 action/accessory designs
- 1 front-facing full-body hero image
- 8 angle views
- 24 comprehensive emotions

Default total: `9 × 41 = 369` originals. Each user-requested color theme appends another 41 originals.

## Required reading and input

Read `references/feature-switches.md` completely at the start of every task. Read `references/prompt-set.md` whenever the classic series is enabled; use its eight concepts only when classic action designs are enabled. Read `references/theme-expansion.md` whenever random or user themes are enabled.

Require one clear user reference photo showing the face. Accept additional photos when offered. If a local path is supplied, inspect it with `view_image`. Inspect both bundled visual-language assets before generation:

- `assets/style-reference.png`
- `assets/series-anchor.png`

The user photo is the sole identity and presentation source. Bundled assets provide only the handmade crayon/cut-paper visual language.

## Workflow

1. Resolve feature switches from the first user message. Accept natural language or the copyable YAML-like block in `references/feature-switches.md`. Missing switches are `on`; do not interpret omission as opt-out.
2. Run `scripts/calculate_feature_plan.py` with the resolved values. Tell the user the enabled modules and expected original-image count before generation, then continue without requiring confirmation unless the configuration is invalid.
3. Extract identity DNA: face and jaw shape, brows, eyes, nose, mouth, hair length/texture/fringe/sides, apparent age range, posture, build, visible presentation cues, and source-supported clothing/accessories. Never assert gender identity.
4. Separate identity, style, and palette. The bundled yellow/cobalt palette belongs only to the classic series; it is not the user's permanent palette or favorite color.
5. Apply presentation guardrails from visible evidence, not stereotypes. Never transfer bows, ties, ribbons, curls, glasses, jewelry, facial hair, or other identity traits from style assets unless visible in the user photo or explicitly requested. Preserve hair length and texture across every module and angle.
6. Establish enabled series:
   - classic series when `classic_series` is on
   - `random_theme_count` blind-box themes when `random_theme_series` is on
   - every user-requested theme appended after random themes
7. If random or user themes are enabled, run `scripts/draw_theme_seed.py` exactly once. Use `--count 0` when random themes are off, and pass user themes through `--user-theme`. Record the seed and complete JSON draw in `PROMPTS.md`. On technical retry, reuse `--seed`.
8. Freeze one canonical character specification per series: identity traits, hairstyle, outfit silhouette, palette roles, facial construction, crayon texture, and white cutout silhouette. All modules in that series must use it.
9. Generate enabled modules in this order:
   - `base_designs`: eight independent action/accessory designs
   - `front_full_body`: one centered head-to-toe front view
   - `angle_views`: eight independent neutral head-to-toe turnaround views using the exact angle list in `references/feature-switches.md`
   - `emotion_pack`: 24 independent head-and-shoulders expressions using the exact emotion list in that reference
10. Use one image-generation call per original image. Never use a grid as a substitute for deliverable originals. For consistency, pass the user photo, visual-language assets, and the closest approved same-series anchor to angle and emotion calls.
11. Generate in batches of four when supported. Validate each batch and regenerate only failed cells with targeted corrections.
12. Save non-destructively using the structure in `references/feature-switches.md`. When expanding an approved classic set, record its hashes and never overwrite, rename, recompress, or regenerate it; write classic extensions to a sibling directory.
13. If `series_collages` is on, create module and series overview images from originals only. If `all_images_collage` is on, create `00-all-images-overview.png` from every delivered original exactly once, including immutable originals in expansion mode. Never include an overview as input to another original-level collage.
14. Save `FEATURES.json`, `PROMPTS.md`, and `QA.md`. Record resolved switches, counts, random seed, user themes, file inventory, dimensions, unique hashes, baseline hashes, and collage input counts.

## Validation

- Counts exactly match `scripts/calculate_feature_plan.py`.
- Each series preserves at least four recognizable identity traits and one canonical hairstyle/outfit system.
- The front full-body image is head-to-toe, centered, front-facing, unobstructed, and has readable hands and feet.
- All eight requested angles are present exactly once; left/right and front/back views are not mislabeled or mirrored duplicates.
- All 24 emotions are present exactly once and remain readable at avatar size without changing identity, hairstyle, outfit, or palette.
- Emotions change brows, eyes, mouth, cheeks, and restrained gesture marks—not face structure or costume.
- Random themes come from the recorded draw. User-requested themes append after them and never replace them.
- Every deliverable is a separate square raster image with no duplicate hash, text, logo, watermark, unrelated character, photorealism, gradients, 3D, or polished vector finish.
- Enabled collages contain the expected originals exactly once. Disabled modules produce no deliverable files or empty folders.

## Handoff

Show `00-all-images-overview.png` inline when enabled. Report the resolved switches, series count, originals per series, total delivered originals, newly generated count, random seed, appended themes, output path, `FEATURES.json`, `PROMPTS.md`, and `QA.md`. In expansion mode, explicitly confirm that existing originals were unchanged.
