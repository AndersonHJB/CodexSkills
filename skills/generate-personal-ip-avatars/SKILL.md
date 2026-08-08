---
name: generate-personal-ip-avatars
description: "Design a gender-adaptive personal-IP cartoon collection from one user-provided portrait for people with no art or design background. Supports a quick classic set of 8 images or a blind-box collection with one immutable classic set, eight randomly drawn color themes, and any user-requested color themes appended on top; every theme contains eight distinct hairstyles, actions, outfits, and signature accessories. Use for personal IP, cartoon identity, avatar series, character packs, randomized multi-palette exploration, or expansion of an existing approved 8-image set."
---

# Generate Personal IP Avatars

Create a coherent, recognizable character system from one portrait without making it photorealistic. Offer three modes:

- **Quick mode:** one classic series of eight separate square images.
- **Blind-box full mode:** the classic eight plus eight randomly drawn color-theme series of eight images each, for 72 images by default.
- **Expansion mode:** when an approved classic eight already exists, treat it as immutable and generate only the 64 random-theme additions by default. Never overwrite or silently revise the approved eight.

If the user names preferred colors or palettes, append one eight-image series per requested theme after the eight random themes. Do not replace, reduce, or bias the random eight. The total becomes `72 + 8 × requested-theme-count` in full mode.

## Required input

Require exactly one clear user reference photo showing the face. Accept additional photos when offered, but do not require them.

If the photo exists only as a local path, inspect it with `view_image` before generation. Also inspect both bundled style assets before the first generation call:

- `assets/style-reference.png`: original visual-language reference
- `assets/series-anchor.png`: approved adaptation used only as a medium and composition anchor

Resolve asset paths relative to this `SKILL.md`.

## Workflow

1. Extract a short identity DNA description from the user photo:
   - face and jaw shape
   - hair length, texture, fringe, and side treatment
   - brows, eye shape, nose, and mouth
   - apparent age range and visible presentation cues, without asserting gender identity
   - build, posture, and any real signature clothing or accessory
2. Separate identity, visual style, and palette:
   - Take identity only from the user photo.
   - Take crayon texture, naive proportions, white cutout silhouette, simple facial construction, and doodle density from the bundled assets.
   - Treat the bundled yellow/cobalt palette as the classic baseline only. It is not evidence of the user's favorite color or permanent brand palette.
3. Infer presentation and accessory guardrails from visible evidence, not stereotypes. Do not claim certainty about gender, require disclosure, or let a bundled reference determine presentation.
4. Route styling adaptively:
   - Preserve or thoughtfully vary a source-supported signature accessory or presentation cue.
   - Describe masculine-leaning, feminine-leaning, androgynous, nonbinary, or ambiguous presentation only through visible drawing cues.
   - If evidence is ambiguous, write `presentation-neutral` and use neutral accessories such as glasses, cap, notebook, headphones, watch, camera, mug, or crossbody bag.
   - Never transfer a bow, tie, ribbon, curls, glasses, jewelry, facial hair, or other identity-specific trait from a bundled style asset unless visible in the user's photo or explicitly requested.
   - Preserve source hair length and texture. A cap, pose, or concept must not silently shorten long hair or lengthen short hair.
5. Choose the mode from the request:
   - Use quick mode only when the user explicitly asks for eight images or one compact set.
   - Use blind-box full mode for a complete pack, multiple themes, broad color exploration, or an unspecified request to batch-design a reusable IP collection.
   - Use expansion mode when the user supplies or identifies an existing approved eight-image set.
6. For the classic series, read `references/prompt-set.md` completely. Substitute the identity DNA and presentation guardrails into its common prompt and eight concepts.
7. For blind-box full or expansion mode, read `references/theme-expansion.md` completely. Run `scripts/draw_theme_seed.py` once to draw eight random theme seeds. If the user supplied preferred colors, pass each as `--user-theme`; they are appended after the random eight. Record the returned seed and plan in `PROMPTS.md` before generation.
8. Resolve every random seed into a distinct four-role palette and plan the full action/prop matrix. The default matrix contains 64 expansion cells; add eight cells per user theme.
9. Use the built-in image-generation tool. Pass the user photo plus both bundled style assets as references. Issue one independent call per concept; never request a grid as a substitute for separate assets.
10. Generate in batches of four when parallel calls are supported. Keep the user informed between batches.
11. Validate every image against the checklist below. Regenerate only failed concepts with a targeted correction.
12. Save non-destructively:
    - Quick mode: `output/personal-ip-avatars/` or the next versioned sibling.
    - Blind-box full mode: `00-classic/` followed by eight random theme directories, then any user-theme directories.
    - Expansion mode: preserve the existing classic directory and write the `64 + 8N` additions to a new sibling directory.
13. Create one `00-overview.png` per eight-image series with `scripts/make_contact_sheet.sh`. Create a series-level overview with `scripts/make_series_overview.sh` when there are exactly nine series.
14. Always create `00-all-images-overview.png` directly from every original in the delivered collection, in reading order, with `scripts/make_all_images_overview.sh`. In expansion mode this includes the immutable classic eight plus all additions. Exclude contact sheets and other overview files from its inputs. This final collage is mandatory even when ImageMagick requires a reduced thumbnail size.
15. Save resolved identity, style lock, random seed, palette draw, user-appended themes, and all concept prompts as `PROMPTS.md`. Save counts and validation results as `QA.md`.

## Validation checklist

Check all of the following before delivery:

- Quick mode has exactly 8 separate square images. Blind-box full mode has `72 + 8N`, where `N` is the number of requested themes. Expansion mode has `64 + 8N` new images plus an explicit reference to the unchanged classic 8.
- The person remains plausibly recognizable through at least four extracted identity traits.
- Every image stays in the same handmade crayon/cut-paper visual language, even when the palette changes.
- The classic series keeps its approved palette and concepts unchanged during expansion.
- The eight blind-box palettes come from the recorded random draw and are distinguishable from the classic palette and from one another. They are coordinated color systems, not superficial hue filters.
- User-requested themes appear after the random eight and do not replace them.
- Each palette defines background, line, base, and accent roles with readable contrast.
- Within every series, all eight images differ in hairstyle treatment, action, signature accessory, and clothing detail—not merely color.
- Across all expansion images, core props and actions do not repeat unless the user requests repetition.
- No image drifts into photorealism, realistic skin rendering, gradients, 3D, or polished vector art.
- Hands have plausible finger counts and the requested gesture is readable.
- No identity, accessory, hairstyle, or gender-presentation cue leaked from a bundled style asset.
- No text, logo, watermark, or unrelated extra character appears.
- Files are square raster images, uniquely hashed, and grouped correctly.
- `00-all-images-overview.png` contains every delivered original exactly once and no overview recursively contains itself.

## Output handoff

Show `00-all-images-overview.png` inline. Report the absolute output directories, mode, random seed, random themes, appended user themes, counts, `PROMPTS.md`, `QA.md`, and whether the built-in image-generation tool was used. Briefly name the series and their eight concepts in reading order. In expansion mode, explicitly confirm that the original eight were not modified.

## Contact sheets

Create each eight-image sheet:

```bash
bash scripts/make_contact_sheet.sh \
  --out <series-directory>/00-overview.png \
  <image-01> <image-02> <image-03> <image-04> \
  <image-05> <image-06> <image-07> <image-08>
```

Create the complete nine-series overview:

```bash
bash scripts/make_series_overview.sh \
  --out <collection-directory>/00-complete-9-series-overview.png \
  <classic-overview> <theme-01-overview> <theme-02-overview> \
  <theme-03-overview> <theme-04-overview> <theme-05-overview> \
  <theme-06-overview> <theme-07-overview> <theme-08-overview>
```

These overview scripts require ImageMagick and never modify source images.

Create the mandatory collage from all original images:

```bash
bash scripts/make_all_images_overview.sh \
  --out <collection-directory>/00-all-images-overview.png \
  <all-original-images-in-reading-order>
```
