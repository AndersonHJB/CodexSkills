# Image Generation Prompt Templates

Use the installed imagegen skill's structured prompt style. Label reference roles explicitly.

## Character anchor

```text
Use case: stylized-concept
Asset type: internal text-free Q-version character anchor
Input images: Image 1..N are identity references only
Primary request: create one neutral, recognizable Q-version character design
Subject: preserve visible identity anchors from the references; simplify to one stable outfit
Style/medium: polished cute 2D digital sticker illustration; rounded dark linework; soft pastel fill; subtle flat shading
Composition: 1:1 square, front-facing half body, generous padding
Text: none
Constraints: no words, letters, numbers, watermark, logo, signature, border, collage, panel grid, props, or photographic background
```

## Sticker artwork

```text
Use case: stylized-concept
Asset type: text-free artwork for sticker <ID> of a 20-image set
Input images: original photo(s) are identity references; the anchor is the style/proportion reference
Primary request: same locked Q-version character performing <POSE_ACTION> with <EMOTION>
Prop: <PROP or none>
Composition: 1:1 square; <FRAMING>; keep the character fully inside frame; reserve a clean <TEXT_ZONE> area for later typography
Background: clean pure white #FFFFFF unless the user requested another production background
Text: none; render no words, letters, numbers, symbols, or text-like marks
Constraints: preserve face, hairstyle, glasses/accessories, outfit, palette, head/body ratio, line weight, shading, and outline; one standalone scene; no watermark, logo, signature, border, collage, or multi-panel layout
```

## Banner

```text
Use case: illustration-story
Asset type: WeChat sticker album detail banner, final crop 750×400
Input images: anchor is the identity/style reference; selected stickers are action references only
Primary request: a bright, colorful, story-rich horizontal scene about the same character's daily reactions
Composition: very wide 15:8; keep important content in the central 80% safe area
Background: opaque colorful scene, clearly nonwhite and nontransparent
Text: none
Constraints: no words, letters, numbers, clock numerals, logos, watermark, signature, speech bubble, collage, panel grid, duplicated character, or distortion
```

## Cover chroma master

Choose a flat key color absent from the character and outfit. Use `#00ff00` by default; use `#ff00ff` when the subject contains green. Freeze the chosen value as `<KEY_COLOR>` in both the prompt file and the chroma-removal command.

```text
Use case: background-extraction
Asset type: WeChat album cover master
Input images: anchor is the identity/style reference
Primary request: front-facing recognizable half/full-body character, simple friendly pose
Scene/backdrop: perfectly flat solid <KEY_COLOR> chroma-key background with no shadow, gradient, texture, reflection, floor plane, or lighting variation
Composition: 1:1 square; subject fills about 80–85%; modest even padding; no crop
Text: none
Constraints: do not use <KEY_COLOR> in the subject; no white sticker outline, halo, props, decoration, words, logo, watermark, border, or frame
```

## Chat icon chroma master

```text
Use case: background-extraction
Asset type: WeChat chat-list icon master
Input images: anchor is the identity/style reference
Primary request: highly recognizable straight-on head portrait with a simple expression
Scene/backdrop: perfectly flat solid <KEY_COLOR> chroma-key background
Composition: 1:1 square; head fills about 75–82%; small balanced padding; no hands or body pose
Text: none
Constraints: do not use <KEY_COLOR> in the subject; no white outline, jaggies, decoration, prop, word, logo, watermark, square frame, shadow, or background scene
```

## Inspection and correction

- Reject stray text, numbers, watermarks, logos, panels, cropped heads/hands, identity drift, or wrong action.
- Correct one issue at a time and repeat all invariants.
- For banner clocks, replace numerals with dots/tick marks.
- For cover/icon transparency, follow the imagegen chroma-key helper workflow and validate transparent corners, subject coverage, and key-color fringe.
