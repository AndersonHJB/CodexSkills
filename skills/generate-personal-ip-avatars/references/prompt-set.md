# Prompt set

Read this file completely before generating. Replace `<IDENTITY_DNA>` and `<PRESENTATION_GUARDRAILS>` in every prompt.

## Common prompt

```text
Use case: style-transfer
Asset type: square personal-IP cartoon series
Input images: Image 1 is the user's sole identity and presentation reference. Image 2 is the bundled original style reference. Image 3 is the bundled approved adaptation. Images 2 and 3 are strict anchors only for line quality, proportions, yellow background, cobalt crayon, white uncolored skin, cheek marks, white silhouette, and doodle density. They must not influence the new character's gender presentation, hairstyle, facial traits, clothing, or accessories.

Identity DNA from Image 1: <IDENTITY_DNA>

Series rules: create a 1:1 square, centered head-and-shoulders character on a saturated warm-yellow background. Use naive cobalt wax-crayon lines, uneven pencil pressure, flat white face and hands, simple eyes/nose/mouth, circular yellow cheek marks, an irregular white character silhouette, and sparse cobalt with tiny red doodles. Keep the same charming handmade imperfection as the bundled references. Preserve the user's age range, visible presentation cues, facial structure, hair length, texture, and recognizable silhouette. Do not state or invent a gender identity; translate visible evidence into drawing decisions.

Presentation guardrails derived only from Image 1 and the user's request: <PRESENTATION_GUARDRAILS>

No photorealism, realistic skin rendering, gradients, shadows, 3D, detailed anatomy, polished vector finish, text, logo, watermark, or unrelated character.
```

Append exactly one concept block below to the common prompt for each independent call.

## 1. Classic salute

```text
Hair: closest-to-source hairstyle, length, and texture with slightly more crayon texture and a readable silhouette.
Action: one hand makes a clean salute touching the forehead.
Signature accessory: preserve one source-supported signature accessory when available; otherwise use simple source-compatible glasses or no accessory. Do not introduce a tie, bow, ribbon, jewelry, or pendant solely from a bundled reference.
Clothing: mustard top with a simple neckline or collar adapted to the source presentation.
Face: thin round glasses, quiet smile, yellow cheeks.
Doodles: loops, question marks, and short hatching.
```

## 2. Notebook thinker

```text
Hair: plausible side-swept variation of the source hair.
Action: hold a small open red notebook while a cobalt pencil touches the chin; eyes look upward.
Signature accessory: red notebook and cobalt pencil; notebook contains no writing.
Clothing: mustard cardigan over white crewneck; no neck accessory.
Face: large round cobalt glasses, one eyebrow raised, yellow cheeks.
Doodles: thought loops, tiny question marks, and pencil hatching.
```

## 3. Cap hello

```text
Hair: preserve the source length and texture beneath and around a backward red baseball cap; long hair remains long and visible, while short hair remains short.
Action: open-hand wave beside the head with five simple fingers.
Signature accessory: backward red baseball cap with a short flat brim.
Clothing: loose cobalt sweatshirt; no tie or neck accessory.
Face: no glasses, friendly closed-mouth smile, yellow cheeks.
Doodles: cobalt zigzags, red circles, and energetic short strokes.
```

## 4. Headphone thumbs-up

```text
Hair: upward or higher-volume variation that remains plausible for the source.
Action: clear thumbs-up beside the shoulder.
Signature accessory: cobalt over-ear headphones around the neck with two circular earcups and a simple band.
Clothing: mustard T-shirt with white neckline; no tie.
Face: no glasses, confident crescent eyes, yellow cheeks.
Doodles: music-like curves, radiating strokes, and loose spirals without text.
```

## 5. Crossbody direction

```text
Hair: fringe-forward variation based on the source, using one memorable curved lock when plausible.
Action: point upward with one index finger; eyes follow the gesture.
Signature accessory: flat red crossbody strap and small cobalt rectangular pouch; no decorative loops.
Clothing: mustard sweatshirt with no neck accessory.
Face: no glasses, curious expression, yellow cheeks.
Doodles: arrows, circles, and upward motion strokes.
```

## 6. Watchful thinker

```text
Hair: neat structured or swept-back variation of the source hair.
Action: one hand under the chin; eyes glance sideways.
Signature accessory: simple red round wristwatch.
Clothing: mustard mock-neck or plain crewneck; nothing tied around the neck.
Face: thin rectangular cobalt glasses, thoughtful mouth, yellow cheeks.
Doodles: question marks, thought lines, and clock-like circles without numbers.
```

## 7. Camera gesture

```text
Hair: tousled near-source variation with separated cobalt pencil tufts or strands.
Action: one hand makes a V sign beside the temple; the other supports a compact camera.
Signature accessory: boxy cobalt camera with one red circular lens accent and no hanging strap.
Clothing: mustard utility vest over a white T-shirt; no neck accessory.
Face: no glasses, one gentle wink, yellow cheeks, friendly smile.
Doodles: frame corners, circles, and shutter-like radial strokes.
```

## 8. Coffee calm

```text
Hair: restrained neat version closest to the source silhouette.
Action: one arm crosses the chest while the other hand holds a small red mug near the shoulder.
Signature accessory: simple red cylindrical mug with a clear C-shaped handle and no decoration.
Clothing: cobalt cardigan over mustard T-shirt; no tie or neck accessory.
Face: small square cobalt glasses, relaxed smile, yellow cheeks.
Doodles: steam-like curves, calm horizontal hatching, and a few red dots.
```
