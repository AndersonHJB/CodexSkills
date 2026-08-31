# Packaging profile

These defaults separate the approved reusable visual preset from content-specific facts. Reuse the values and behavior in `approved-edit-preset.md`; derive chapter count, chapter text, cue timing, claims, and occupied regions from the current video.

## Preserve the program

- Default to information-layer packaging only: keep story order, source ranges, aspect ratio, and total duration unchanged.
- Do not crop, reframe, grade, denoise, add music, or alter gain unless requested or required to repair a demonstrated defect.
- Preview proxies may be smaller, but the final render must reference the original source.
- Overlay rendering requires video re-encoding. Use a visually transparent/high-quality encode rather than claiming bitstream identity.
- Keep source square-pixel display geometry, display aspect ratio, frame cadence, pixel depth, chroma fidelity, color range, and color metadata. Coded dimensions, rotation metadata, or sample aspect ratio may change only when the resulting display geometry is equivalent. Never apply an unapproved HDR-to-SDR conversion.
- If audio is untouched, prefer copying the original audio stream into the master. If the composition path requires re-encoding, preserve sample rate and channels and use a high-quality bitrate.

## Chinese-first bilingual captions

- Chinese is the first and visually dominant line. English is secondary, shorter, lighter, and about 55%–65% of the Chinese font size.
- Keep a cue semantically complete. Typical duration is 1.2–4.5 seconds; avoid more than two Chinese lines. English may condense rather than mirror every filler word.
- Use approximately 10 Chinese characters/second as a review threshold, not a blind deletion rule. Listen and split or shorten when comprehension suffers.
- Align Chinese, English, and bilingual cue IDs and timestamps exactly. Never allow overlaps, negative duration, blank translation, or cross-chapter cues.
- Use fonts proven to contain all Chinese and Latin glyphs. Validate names, versions, code terms, acronyms, punctuation, and numerals.
- Default to Alibaba PuHuiTi 2.0 SemiBold for Chinese and PingFang SC Regular for English. Use a fallback only after inspecting metric compatibility and every required glyph.

## Approved layout

- For 16:9 landscape, apply the 3840×2160 base values in `approved-edit-preset.md` and scale them linearly to the source display height. Do not substitute generic normalized values when the approved preset applies.
- Keep the caption block horizontally centered with both text lines centered. Keep its lower edge at the preset position; first shorten, rewrap, or narrow a cue before moving the whole block.
- Keep the chapter card at the extreme top-left. Shorten a long chapter title rather than growing the card across the frame or relocating it to the center/bottom.
- Keep the progress band at the frame bottom, the rail approximately 6/2160 of frame height above the bottom, and the playhead touching the bottom edge.
- For portrait, square, or materially non-16:9 footage, preserve the same palette, typography, top-left chapter anchor, centered bilingual-caption hierarchy, and bottom progress behavior. Recompute widths from the actual safe region without cropping the source, then require representative-frame review.

## Content-aware placement

1. Mark occupied regions for face/mouth, phone, active pointer, buttons, code, charts, and proof/result UI.
2. Keep the approved centered caption position unless a real critical-content collision is visible. Prefer shortening, narrowing, rewrapping, or reducing padding before moving it.
3. If an exception is unavoidable, change only at a stable visual transition and keep the exception consistent across the scene. Do not make subtitles jump cue by cue.
4. Keep the chapter card top-left; reduce exposure or scale before considering relocation, and record any relocation as a preset exception.
5. Check full-resolution readability and a phone-size preview.

## Chapters and progress

- Derive chapters from semantic tasks and visible operations. A 3–8 minute tutorial often yields 4–10 chapters, but content decides.
- Chapter ranges must cover the complete program without gaps or overlaps.
- Show the compact top-left chapter card for `min(4.2 seconds, chapter duration)` from each chapter boundary.
- Keep chapter graphics at the approved top-left anchor; do not create a centered or bottom chapter title.
- Do not add a separate persistent stage label. The segmented progress labels carry persistent chapter context.
- Calculate chapter ticks and progress from exact program time. The progress fill begins at the first frame and reaches 100% on the final frame.

## Source-fidelity export

- Match source display dimensions and frame cadence by default. Preserve variable-frame-rate timing when the pipeline supports it; if a stable CFR master is required, match the effective cadence, preserve duration/timestamps, and document the conversion. Do not turn 1080p into “4K,” and do not silently deliver a 4K source as 1080p.
- Preserve compatible pixel format and color tags. If the source is 10-bit or HDR, use a compatible pipeline and verify it explicitly.
- Preserve duration within about one source frame. Account for audio priming or container metadata before declaring a mismatch.
- Bitrate alone does not prove clarity. Inspect source and output crops at 100% scale, especially small UI text, hair, edges, and fine patterns outside overlay regions.
- Use a broadly compatible high-quality delivery codec unless the user specifies another. Record codec/profile, size, and bitrate in the QA report rather than hardcoding one encoder setting for every source.
