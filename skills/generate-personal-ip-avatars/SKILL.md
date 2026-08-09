---
name: generate-personal-ip-avatars
description: "Design a gender-adaptive personal-IP cartoon system from one portrait for users with no art background. Provides classic, random, guaranteed light-palette, industry full-body, and official brand or university VI theme modules plus action designs, front full-body characters, eight-angle turnarounds, 24-emotion packs, preferred colors, and collages. When the user gives no explicit feature-control instruction, every applicable feature defaults on. Use for personal IP, professional or industry avatars, campus-color characters, brand-guideline palettes, character sheets, expression packs, turnarounds, avatar blind boxes, or expansion of an approved set."
---

# Generate Personal IP Avatars

Build a recognizable, non-photorealistic IP character system from one portrait. If the user gives no explicit feature-control instruction, enable every module. Change switches only when the user deliberately supplies a `功能开关` block or an unambiguous enable/disable instruction.

With defaults, generate eleven complete series plus eight standalone industry full-body characters: one classic, eight unrestricted blind-box themes, and two guaranteed light-palette blind-box themes. Each complete series contains 41 originals:

- 8 action/accessory designs
- 1 front-facing full-body hero image
- 8 angle views
- 24 comprehensive emotions

Default without a brand or institution input: `11 × 41 + 8 industry full-body = 459` originals. Each ordinary preferred-color theme adds 41. When the user supplies an official brand or university VI source, append eight complete VI-derived series by default, adding 328 originals.

## Required reading and input

Read `references/feature-switches.md` completely at the start of every task. Read `references/prompt-set.md` whenever the classic series is enabled; use its eight concepts only when classic action designs are enabled. Read `references/theme-expansion.md` whenever random or user themes are enabled. Read `references/industry-brand-expansion.md` whenever industry full-body or brand/institution themes are enabled.

Require one clear user reference photo showing the face. Accept additional photos when offered. If a local path is supplied, inspect it with `view_image`. Inspect both bundled visual-language assets before generation:

- `assets/style-reference.png`
- `assets/series-anchor.png`

The user photo is the sole identity and presentation source. Bundled assets provide only the handmade crayon/cut-paper visual language.

## Workflow

1. Detect explicit feature-control intent. If neither a `功能开关` block nor an unambiguous enable/disable instruction appears, force the complete default configuration on. If control intent is explicit, resolve only the stated overrides and keep omitted switches on; never interpret mere omission, short wording, or missing module names as opt-out.
2. Run `scripts/calculate_feature_plan.py` with the resolved values. Tell the user the enabled modules and expected original-image count before generation, then continue without requiring confirmation unless the configuration is invalid.
3. Extract identity DNA: face and jaw shape, brows, eyes, nose, mouth, hair length/texture/fringe/sides, apparent age range, posture, build, visible presentation cues, and source-supported clothing/accessories. Never assert gender identity.
4. Separate identity, style, and palette. The bundled yellow/cobalt palette belongs only to the classic series; it is not the user's permanent palette or favorite color.
5. Apply presentation guardrails from visible evidence, not stereotypes. Never transfer bows, ties, ribbons, curls, glasses, jewelry, facial hair, or other identity traits from style assets unless visible in the user photo or explicitly requested. Preserve hair length and texture across every module and angle.
6. Establish enabled series:
   - classic series when `classic_series` is on
   - `random_theme_count` blind-box themes when `random_theme_series` is on
   - `light_theme_count` newly designed light-palette blind-box themes when `light_theme_series` is on
   - every user-requested theme appended after random themes
   - `brand_theme_count` complete series derived from a user-supplied official brand or institution VI source
7. If random, light, or user themes are enabled, run `scripts/draw_theme_seed.py` exactly once. Use `--count 0` or `--light-count 0` when its series type is off, and pass user themes through `--user-theme`. Record the seed and complete JSON draw in `PROMPTS.md`. On technical retry, reuse `--seed`.
8. Freeze one canonical character specification per series: identity traits, hairstyle, outfit silhouette, palette roles, facial construction, crayon texture, and white cutout silhouette. All modules in that series must use it.
9. When `industry_full_body_pack` is on, plan eight visibly different industry identities using `references/industry-brand-expansion.md`. These are standalone decorated front full-body originals and are not multiplied by theme series.
10. For brand or institution themes, verify colors and usage relationships against a primary official source. Record URLs, document title/date, Pantone/CMYK/RGB values, and any conversions or screen approximations. Use colors and abstract visual language by default; do not copy seals, logos, wordmarks, uniforms, or imply endorsement.
11. Generate enabled modules in this order:
   - `base_designs`: eight independent action/accessory designs
   - `front_full_body`: one centered head-to-toe front view
   - `angle_views`: eight independent neutral head-to-toe turnaround views using the exact angle list in `references/feature-switches.md`
   - `emotion_pack`: 24 independent head-and-shoulders expressions using the exact emotion list in that reference
12. Use one image-generation call per original image. Never use a grid as a substitute for deliverable originals. For consistency, pass the user photo, visual-language assets, and the closest approved same-series anchor to angle and emotion calls.
13. Generate in batches of four when supported. Validate each batch and regenerate only failed cells with targeted corrections.
14. Save non-destructively using the structure in `references/feature-switches.md`. When expanding an approved set, record its hashes and never overwrite, rename, recompress, or regenerate it.
15. If `series_collages` is on, create module and series overview images from originals only. If `all_images_collage` is on, create `00-all-images-overview.png` from every delivered original exactly once, including immutable originals and standalone industry images. Never include an overview as input to another original-level collage.
16. Save `FEATURES.json`, `PROMPTS.md`, and `QA.md`. Record resolved switches, counts, random seed, user themes, official VI sources, file inventory, dimensions, unique hashes, baseline hashes, and collage input counts.

## Validation

- Counts exactly match `scripts/calculate_feature_plan.py`.
- Each series preserves at least four recognizable identity traits and one canonical hairstyle/outfit system.
- The front full-body image is head-to-toe, centered, front-facing, unobstructed, and has readable hands and feet.
- All eight requested angles are present exactly once; left/right and front/back views are not mislabeled or mirrored duplicates.
- All 24 emotions are present exactly once and remain readable at avatar size without changing identity, hairstyle, outfit, or palette.
- Emotions change brows, eyes, mouth, cheeks, and restrained gesture marks—not face structure or costume.
- Random and light themes come from the recorded draw. Light themes keep high-value backgrounds and pastel clothing while retaining readable dark line contrast. User-requested themes append after them and never replace them.
- Every light series must be a newly designed character system with its own outfit silhouette, eight action-prop concepts, doodle vocabulary, and canonical anchor—not a recolor of an existing dark or random series.
- Industry full-body originals each show a different occupation through outfit construction, safe props, posture, and background decoration while preserving identity and avoiding stereotypes, protected insignia, or false credentials.
- Brand or institution series use verified official colors but remain eight newly designed systems, not eight recolors. Do not reproduce protected marks by default or imply affiliation, certification, employment, or endorsement.
- Every deliverable is a separate square raster image with no duplicate hash, text, logo, watermark, unrelated character, photorealism, gradients, 3D, or polished vector finish.
- Enabled collages contain the expected originals exactly once. Disabled modules produce no deliverable files or empty folders.

## Handoff

Show `00-all-images-overview.png` inline when enabled. Report the resolved switches, series count, originals per series, total delivered originals, newly generated count, random seed, appended themes, output path, `FEATURES.json`, `PROMPTS.md`, and `QA.md`. In expansion mode, explicitly confirm that existing originals were unchanged.
