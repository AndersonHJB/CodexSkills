# Theme expansion: random palettes and enabled character modules

Read this file completely whenever random or user themes are enabled. Apply the resolved feature switches: each theme receives only the enabled modules. When `base_designs` is on, its eight concepts must be genuinely designed additions rather than recolors of one pose.

## Freeze the baseline

Before planning additions, record the classic eight paths and hashes. Never edit, overwrite, rename, recompress, or regenerate them during expansion. Exclude their core actions and props from the new concept matrix.

## Draw eight blind-box theme systems

Every person must receive a fresh blind-box draw. Do not reuse a fixed list of eight named themes, copy the previous user's themes, or make the draw deterministic from identity traits. Run:

```bash
python3 scripts/draw_theme_seed.py --count 8
```

If the user names preferred colors or palettes, append each request without changing the random count:

```bash
python3 scripts/draw_theme_seed.py --count 8 \
  --user-theme "用户主题一" \
  --user-theme "用户主题二"
```

Run it exactly once per collection. Record its numeric seed and complete JSON output in `PROMPTS.md` so the draw is auditable and reproducible. A rerun is allowed only after a technical failure before generation; reuse the recorded seed with `--seed` rather than opening a new blind box.

Resolve the draw into palettes using color harmony and the user's visible presentation only as an identity compatibility check. Do not assume the colors in the style reference are the user's personal colors. User themes are additional rows after the random eight; they never replace or recolor the random rows. Treat a deliberately grouped request such as “蓝粉渐变感” as one theme, and separately listed requests as separate themes.

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

The script's palette values are starting anchors. Refine contrast if needed while preserving the sampled hue family, mood, value direction, and harmony. Theme names should be freshly coined from the sampled mood and setting rather than selected from a fixed preset list.

## Build the action-design matrix when enabled

When `base_designs` is on, plan all action-design cells before generating. The default has 64 random-theme cells; append eight cells for every user-requested theme. Every row is one palette theme; every row contains eight different actions and eight different signature props. Across the entire matrix, avoid repeating the same core action-prop pair. When it is off, skip this matrix and create no design folders; the canonical series specification still drives any enabled full-body, angle, or emotion modules.

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

Use the module structure defined in `feature-switches.md`. For each random or user theme, create only enabled module folders:

```text
01-<random-theme>/
  01-designs/
  02-front-full-body/
  03-angle-views/
  04-emotions/
09-<user-theme>/
```

Omit disabled module folders. In expansion mode, keep approved classic files where they are and put classic-only additions in `00-classic-extensions/`.

Record in `PROMPTS.md`:

- identity DNA and presentation guardrails
- style lock
- mode and immutable baseline location
- random seed and raw blind-box JSON draw
- palette names, role colors, and rationale
- which themes were appended from the user's request
- the complete prompt plan for every enabled module

Record in `QA.md`:

- expected and actual counts
- square-dimension check
- unique-hash check
- classic baseline hashes before and after expansion
- any regenerated cells and targeted corrections
- angle-view and emotion coverage checks when enabled
- all-images collage count and input list
