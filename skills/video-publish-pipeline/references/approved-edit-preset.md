# Approved edit preset

This is the default house preset for future `video-publish-pipeline` runs. It reproduces the user's approved final tutorial look while keeping all topic-specific text, timings, chapters, and claims derived from the current source.

## Scope and scaling

- The exact base canvas is 3840×2160 landscape. Preserve the source canvas; do not crop, stretch, upscale, or downscale merely to fit the preset.
- For another 16:9 landscape source, use `sx = output_width / 3840` and `sy = output_height / 2160`; these are equal for exact 16:9. Scale horizontal positions and widths with `sx`, and vertical positions, heights, fonts, radii, and shadows with `sy`. Round consistently, then recompute the alignment equalities below instead of rounding every dependent value independently.
- For materially non-16:9 footage, preserve the palette, type hierarchy, extreme-top-left chapter anchor, horizontally centered captions, and bottom-aligned progress behavior. Recompute widths from safe regions and require full-size review; never force a 16:9 crop.
- These tokens are defaults. A user instruction can override them. A genuine content collision may justify the narrowest possible exception, which must be documented.

After scaling, preserve these relationships:

- `caption_bottom = progress_band_height + structural_gap`; the 4K gap is `30px`, and the remaining gap below the 12px caption hard shadow is `18px`.
- `rail_center = rail_bottom + rail_height / 2` and `playhead_center = playhead_bottom + playhead_size / 2`; their difference must be at most 1px after rounding.
- `playhead_travel = canvas_width - 2 × progress_margin_x - playhead_size`.
- The rail's upper edge, `rail_bottom + rail_height`, remains within the lowest 1% of the frame.

For 1920×1080, the expected primary values are: caption bottom `71px`, progress band `56px`, structural gap `15px`, rail bottom/height `3/6px`, playhead `12px`, progress margin `80px`, chapter left/top `16/16px`, Chinese/English caption sizes `39/23px`, and chapter Chinese title `21px`.

## Visual system

| Role | Value |
| --- | --- |
| Primary blue | `#2B7FD8` |
| Deep blue | `#1E5BA8` |
| Warm yellow | `#F4D758` |
| Red accent | `#E84A5F` |
| Cream paper | `#FEFCF6` |
| Ink | `#1A1A2E` |
| Light / faint ink | `#4A4A5A` / `#8A8A9A` |
| Dark caption panel | `#151821`; shell background `rgba(26,26,46,0.94)` |
| Chinese display/body | Alibaba PuHuiTi 2.0 SemiBold, weight 600 |
| English caption | PingFang SC Regular, weight 400 |
| Latin index/time | Fraunces, weight 600 |

Do not replace this with neon, cyan, blue-purple gradients, glassmorphism, glow, monospace “tech” styling, generic Inter/Roboto/Arial styling, or Bilibili branding. The progress behavior may reference segmented player logic, but must not copy Bilibili marks or controls.

## Centered bilingual captions — 4K base

| Token | Value |
| --- | ---: |
| Clip width / height | `3000 × 340px` |
| Horizontal position | centered (`left: 420px` at 3840px) |
| Bottom | `142px` |
| Shell max width | `2700px` |
| Shell padding | `22px 40px 24px` |
| Radius | `12px` |
| Chinese | `78px`, weight 600, line-height `1.14` |
| English | `46px`, weight 400, line-height `1.24`, margin-top `8px`, yellow |
| Shadow | `12px 12px 0 rgba(244,215,88,.42)`, plus `0 28px 52px rgba(21,24,33,.24)` |
| Layer | `z-index: 7` |

- Center the container and both text lines. Chinese is first and visually primary; English is concise and cue-for-cue aligned.
- Keep Chinese to one or two lines. Do not use word-by-word animation; each cue is a stable card for its timed interval.
- Keep the caption at the preset bottom position. Prefer semantic shortening, rewrapping, or width reduction before raising or moving it sideways.

## Compact top-left chapter card — 4K base

| Token | Value |
| --- | ---: |
| Clip anchor | `left: 32px; top: 32px` |
| Clip size | `700 × 160px` |
| Card width | `min 580px; max 680px; width: fit-content` |
| Card height | `min-height: 140px` |
| Card padding / radius | `12px 24px 14px 18px`; `10px` |
| Grid | `78px minmax(0,1fr)`; gap `16px` |
| Index block | `78px` wide, min-height `104px`, deep blue, `58px` Fraunces |
| Chinese title | `42px` Alibaba PuHuiTi 2.0 SemiBold, one line |
| English line | `20px` italic Fraunces |
| Paper shadow | `8px 8px 0 rgba(244,215,88,.58)`, plus `0 14px 34px rgba(21,24,33,.20)` |
| Layer | `z-index: 8` |

- Show at each chapter boundary for `min(4.2 seconds, chapter duration)`, then remove it completely.
- Keep it at the extreme top-left. Do not center it, move it above the progress bar, or keep it visible for the whole chapter.
- Write short semantic chapter titles that fit one line. Shorten copy before enlarging the card.
- Use a deep-blue number block, cream paper, yellow underline/highlight, small red accent, and left-aligned copy.

## Segmented bottom progress — 4K base

| Token | Value |
| --- | ---: |
| Band | `left: 0; bottom: 0; width: 3840px; height: 112px` |
| Band background | `rgba(254,252,246,.965)` |
| Segment margins | `160px` left and right |
| Segment container | `top: 10px; bottom: 6px; gap: 12px` |
| Label height | `56px` |
| Index / title / time | `30px` Fraunces / `29px` Alibaba / `22px` Fraunces |
| Rail | `bottom: 0` inside the segment container, global bottom `6px`, height `12px` |
| Playhead | `24 × 24px`, `bottom: 0`, `3px` ink border, yellow fill, red shadow |
| Layer | `z-index: 9` |

- The band persists for the full program. Segment widths are proportional to exact chapter durations; chapter count remains content-derived.
- Completed, current, and future segments use distinct opacity/state. Each segment fills linearly through its own true duration.
- The playhead starts at the left segment margin and moves linearly by `canvas_width - 2 × margin - playhead_width`, reaching the final right edge on the final program frame.
- The rail and playhead centers must be co-linear. At the 4K base both centers are 12px above the bottom, while the playhead itself touches the bottom edge.
- Do not place another chapter title in the bottom band.

## Layering, privacy, and attribution

- Source video remains full-frame at layer 0. Captions, chapter, and progress use layers 7, 8, and 9 respectively; spacing must prevent overlap despite that order.
- At the 4K base, caption bottom `142px` and progress-band height `112px` leave 30px structural space. The 12px yellow caption shadow still leaves 18px before the band.
- Do not add privacy masks, blur, censor bars, redactions, or privacy-driven crops unless the user explicitly names what to conceal.
- Record the design attribution in the editable project and delivery report: adapted from ESTHER不二 / esthersjw `esther-design-system`, CC BY-NC-SA 4.0. Commercial use requires rights confirmation.

## Required visual proof

Before final render, inspect the opening, every chapter start and post-card frame, dense subtitles, every layout exception, the last two seconds, and the final frame. Confirm exact anchor behavior, no caption/progress collision, readable glyphs, rail within the bottom 1%, and 100% final progress. Repeat the same inspection on frames extracted from the encoded master.
