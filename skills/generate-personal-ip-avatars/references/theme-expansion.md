# Theme expansion: eight palettes × eight concepts

Read this file completely for full or expansion mode. The objective is 64 genuinely designed additions, not eight copies of the same character recolored eight times.

## Freeze the baseline

Before planning additions, record the classic eight paths and hashes. Never edit, overwrite, rename, recompress, or regenerate them during expansion. Exclude their core actions and props from the new concept matrix.

## Design eight theme systems

Discover palettes from the user's visible presentation, the emotional range useful for their IP, and color harmony. Do not assume the colors in the style reference are the user's personal colors. When the user gives no preference, choose a deliberately broad set of eight visual moods.

Each theme must define four roles:

1. `background`: dominant field color
2. `line`: high-contrast crayon or pencil color
3. `base`: clothing and large secondary shapes
4. `accent`: sparse focal color for the prop, cheeks, or doodles

Requirements:

- Keep enough line/background contrast for the face and silhouette to read at avatar size.
- Make neighboring themes different in hue family, value, temperature, or saturation—not only in name.
- Include tonal variety: light, dark, warm, cool, quiet, and energetic themes where appropriate.
- Use flat pigment-like color. Avoid gradients, glow effects, realistic light, metallic rendering, and polished vector fills.
- Keep the white cutout silhouette and handmade medium as the cross-theme visual glue.

If no stronger user-specific direction emerges, useful starting territories include forest mint, coral sunset, ocean cyan, lavender night, terracotta atelier, neon city, ink and crimson, and citrus sky. Adapt or replace these; they are not mandatory presets.

## Build the 8 × 8 concept matrix

Plan all 64 cells before generating. Every row is one palette theme; every row contains eight different actions and eight different signature props. Across the entire matrix, avoid repeating the same core action-prop pair.

For each cell specify:

- hairstyle treatment that remains plausible for the source
- one readable action or gesture
- one signature prop or accessory
- clothing silhouette/detail
- facial expression
- theme-compatible doodle vocabulary

Balance the complete matrix across work, creativity, outdoors, play, travel, rest, learning, food, sport, and technology. A color change alone never counts as a new design.

Apply the presentation guardrails to every cell. Do not introduce gender-coded accessories merely to increase variation. Preserve visible identity features across all themes.

## Common expansion prompt

Use this structure for every independent generation call:

```text
Use case: style-transfer and character-system expansion
Asset type: one square personal-IP cartoon illustration

Input references: Image 1 is the user's sole identity and presentation reference. Images 2 and 3 are strict visual-language anchors only: naive wax-crayon texture, simplified proportions, flat white face and hands, irregular white cutout silhouette, sparse hand-drawn doodles, and charming imperfection. They must not transfer a person, gender presentation, hairstyle, clothing, accessory, or permanent palette.

Identity DNA: <IDENTITY_DNA>
Presentation guardrails: <PRESENTATION_GUARDRAILS>
Style lock: <STYLE_LOCK>

Theme: <THEME_NAME>
Palette roles: background <BACKGROUND_HEX>; line <LINE_HEX>; base <BASE_HEX>; accent <ACCENT_HEX>. Use these as flat pigment-like colors with strong readable contrast. This palette is unique to this series.

Design cell:
- Hair: <HAIRSTYLE_TREATMENT>
- Action: <ACTION>
- Signature prop/accessory: <PROP>
- Clothing: <CLOTHING>
- Face: <EXPRESSION>
- Doodles: <DOODLES>

Create only this single character image, not a grid or contact sheet. Keep the person recognizable and the medium consistent with the references. Do not copy their yellow/cobalt palette unless this theme explicitly selects it. No photorealism, realistic skin, gradients, shadows, 3D, polished vector finish, text, logo, watermark, or unrelated character.
```

## Output structure

Use stable, sortable names:

```text
00-classic/01-...png ... 08-...png
01-<theme>/01-...png ... 08-...png
...
08-<theme>/01-...png ... 08-...png
```

In expansion mode, keep the approved classic directory where it is and begin the new sibling collection at `01-<theme>`.

Record in `PROMPTS.md`:

- identity DNA and presentation guardrails
- style lock
- mode and immutable baseline location
- palette names, role colors, and rationale
- the complete 64-cell concept matrix

Record in `QA.md`:

- expected and actual counts
- square-dimension check
- unique-hash check
- classic baseline hashes before and after expansion
- any regenerated cells and targeted corrections
