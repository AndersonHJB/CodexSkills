---
name: generate-personal-ip-avatars
description: Batch-design eight distinct, gender-adaptive personal-IP cartoon portraits from one user-provided reference photo in a consistent handmade yellow-background, cobalt-crayon illustration system. Use when a user asks to turn any person's photo into a personal IP, cartoon identity, avatar series, character pack, or eight coordinated profile illustrations with varied hairstyles, poses, and signature accessories.
---

# Generate Personal IP Avatars

Create eight separate square raster illustrations from one portrait. Keep one coherent visual series while making the eight designs visibly different.

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
   - apparent age range and visual presentation cues, without asserting gender identity
   - build, posture, and any real signature clothing or accessory
2. Separate identity from style. Take identity only from the user photo. Take yellow background, cobalt crayon, white skin areas, cheek circles, white silhouette, and loose doodles only from the bundled assets.
3. Infer presentation and accessory guardrails from visible evidence, not stereotypes. Do not claim certainty about gender, do not require the user to disclose gender, and do not let either bundled reference determine the new character's gender presentation.
4. Route styling adaptively:
   - If the source clearly supports a signature accessory or presentation cue, preserve or thoughtfully vary it.
   - If the source appears masculine-leaning, feminine-leaning, androgynous, nonbinary, or ambiguous, describe only the visible cues needed for drawing and keep the wording respectful.
   - If evidence is ambiguous, write `presentation-neutral` and default to neutral accessories such as glasses, cap, notebook, headphones, watch, camera, mug, or crossbody bag.
   - Never transfer a bow, tie, ribbon, curls, glasses, jewelry, facial hair, or other identity-specific trait from a bundled style asset unless it is visible in the user's photo or explicitly requested.
   - Preserve source hair length and texture. A cap, pose, or concept must not silently shorten long hair or lengthen short hair.
5. Read `references/prompt-set.md` completely. Substitute the identity DNA and presentation guardrails into its common prompt and eight concepts.
6. Use the built-in image-generation tool. Pass the user photo plus both bundled assets as references. Issue one independent image-generation call per concept; do not request a grid as a substitute for eight assets.
7. Generate the concepts in two batches of four when parallel tool calls are supported. Keep the user informed between batches.
8. Validate every image against the checklist below. Regenerate only failed concepts with a targeted correction.
9. Save all eight images non-destructively in the current workspace. Prefer `output/personal-ip-avatars/`; if it exists, create the next versioned sibling such as `personal-ip-avatars-v2`.
10. Create `00-overview.png` with `scripts/make_contact_sheet.sh` when ImageMagick is available. If ImageMagick is unavailable, still deliver the eight originals.
11. Save the final resolved prompt set as `PROMPTS.md` beside the images.

## Validation checklist

Check all of the following before delivery:

- Exactly eight separate square images exist.
- The person remains plausibly recognizable through at least four extracted identity traits.
- Every image uses the same yellow/cobalt/red/white handmade crayon system.
- The eight images differ in hairstyle treatment, action, accessory, and clothing detail—not merely color.
- No image drifts into photorealism, realistic skin color, gradients, 3D, or polished vector art.
- Hands have plausible finger counts and the requested gesture is readable.
- No identity, accessory, hairstyle, or gender-presentation cue leaked from a bundled style asset; those choices come only from the user photo or explicit request.
- No text, logo, watermark, or unrelated extra character appears.

## Output handoff

Show the overview image inline. Report the absolute output directory, the eight original image paths, `PROMPTS.md`, and whether the built-in image-generation tool was used. Briefly name the eight concepts in reading order.

## Contact sheet

Run:

```bash
bash scripts/make_contact_sheet.sh \
  --out <output-directory>/00-overview.png \
  <image-01> <image-02> <image-03> <image-04> \
  <image-05> <image-06> <image-07> <image-08>
```

The script requires ImageMagick and never modifies the source images.
