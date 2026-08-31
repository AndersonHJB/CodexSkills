# Cover workflow

## Resolve the cover mode

Choose and record exactly one `cover_mode` before research or production:

1. `house-creative` — the default for a new full-pipeline video. Create new, content-derived covers in the fixed approved visual system. Existing covers may be style references, but do not copy their topic text or treat them as immutable pixels.
2. `preserve-asset` — use only when the user explicitly identifies a cover and asks to keep, reuse, or adapt that exact source image without redesign. Keep the source file immutable; required ratio outputs are derivatives.
3. `preserve-frame` — use only when the user explicitly asks for a video frame as the cover.

“保持之前效果”, “风格和之前一致”, “按原本样式做”, and “和之前一样” select `house-creative`. “这张原图不变”, “沿用这个封面文件”, and “不要重做封面” select `preserve-asset`. A matching file beside the video does not silently change the default.

Record the mode and:

- for `house-creative`: the current-video evidence frames, any inspected person/product references, and the approved cover preset;
- for `preserve-asset`: the exact absolute source asset path;
- for `preserve-frame`: the exact source-video timestamp.

Ask one concise question only when the user's wording explicitly requests preservation but several equally plausible assets remain.

The approved preset wins when “之前样式” is generic. If the user explicitly names a different style reference, that reference overrides the preset for the current run. If a preserved asset's wording or visual claim conflicts with the current fact matrix, stop before producing or publishing derivatives and ask whether to retain the mismatch or switch to `house-creative`; never silently rewrite the asset.

## House-creative research and evidence

1. Read [approved-cover-preset.md](approved-cover-preset.md) and keep its visual DNA and ratio templates fixed.
2. Browse current Bilibili and Xiaohongshu examples in the same topic/category and check current official platform guidance when exact rules matter. Treat trends as time-sensitive and use them only to refine hook length, proof density, contrast, and phone-feed readability; do not change the house style.
3. Extract and inspect 3–5 evidence-rich source frames: person, product/UI, device, before/after, result, chart, or key object.
4. Choose one accurate promise and one proof point from the fact matrix. A cover must not imply a feature or result the video does not support.
5. Detect private notifications, account data, QR codes, contact details, filenames, and sensitive UI for review, but do not blur, blank, mask, crop, or replace them unless the user explicitly requests concealment.

## House-creative imagegen production

- Read and follow `imagegen`. Use its built-in image generation path for all three ratio outputs within one coordinated cover system.
- Make one independent image-generation call per ratio using inspected source evidence and the ratio-specific composition in the approved cover preset. The result is one coordinated visual system, not three unrelated creative directions. Do not create one master and crop it into the other ratios.
- Generate the finished visual and typography with imagegen; do not substitute a CSS-only cover board. If imagegen cannot render exact Chinese, brand names, or critical UI reliably, retain the generated visual and repair only those narrow regions deterministically, then disclose the correction.
- Require exact approved cover copy verbatim. Keep one primary hook, one proof phrase, and at most one small badge. Roughly 4–8 Chinese characters is a useful main-hook default, not a fixed rule.
- Prefer real interface evidence plus a real person/device when present. Never invent a creator's face when the source has no person.
- Preserve face identity, hand anatomy, device geometry, recognizable UI, and every unmasked source detail the user did not ask to conceal. Avoid fake interface text, extra logos, watermarks, exaggerated expressions, and unsupported promises.
- Save raw generations and repaired variants in the editable project. Never leave the only copy under a generated-images cache.

## Explicit preservation modes

- Keep the selected artwork, wording, identity, palette, typography, key layout, and overall visual language. Do not introduce a new hook, badge, pose, generated background, logo, or unrelated concept.
- If the asset already matches a required size, preserve the derivative without visual changes. For other ratios, use content-safe crop, reframe, or padding, and never regenerate a retained face, UI, logo, or text.
- For `preserve-frame`, extract the exact recorded frame and add no new cover copy unless requested.
- Keep the source asset read-only and write collision-safe output names.

A content-safe adaptation deliberately protects every semantic region—title, face, proof, UI, badge, and disclosure—through ratio-specific crop selection, repositioning, or added non-semantic padding. A mechanical crop applies one automatic scale/crop recipe without protecting those regions or designing for the target ratio; it is forbidden.

## Required outputs

Produce three ratio-specific layouts and normalize the approved PNG files to:

| Ratio | Exact size | Default role |
| --- | ---: | --- |
| 16:9 | 1920×1080 | Bilibili / YouTube landscape thumbnail |
| 3:4 | 1080×1440 | Xiaohongshu portrait cover |
| 4:3 | 1440×1080 | WeChat Channels / adaptable landscape-card cover |

These three ratios override the default cover matrix in `video-platform-publishing`. Generate an additional ratio only when requested.

## Visual acceptance

Inspect every cover separately at full size and at approximately phone-thumbnail size. A compressed contact sheet is not a substitute for the three individual checks.

Hard failures include:

- wrong dimensions or a mechanical crop of one master into all ratios as defined above;
- departure from the approved visual DNA in `house-creative` mode;
- Chinese typo, missing glyph, unreadable type, or altered brand spelling;
- changed identity, malformed face/hand/device, invented product UI, or unintended watermark;
- unrequested blur, blanking, masking, privacy crop, or replacement of visible source information;
- unsafe crop around eyes, mouth, title, proof, or required disclosure;
- in `house-creative`, cover copy or a visual promise that contradicts the fact matrix; in preservation modes, an unresolved mismatch without the explicit recorded decision required above;
- low contrast or too many equal-weight elements at thumbnail size;
- in preservation modes, an unrequested change to the selected asset's wording, identity, palette, typography, key artwork, or overall style.

Save final PNG files in the source-side `封面/` directory. Keep originals and earlier approved deliverables read-only.
