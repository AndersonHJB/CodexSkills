---
name: video-publish-pipeline
description: Process one supplied video into a verified five-platform publishing package with the user's approved centered bilingual captions, top-left chapter cards, bottom-segment progress preset, source-fidelity export, and content-derived 16:9/3:4/4:3 covers in the fixed warm-paper editorial collage system. Use for full editing, packaging, final delivery, “same style as before,” or $video-publish-pipeline. Do not use for one isolated subtitle, cover, export, or copywriting task.
---

# Video Publish Pipeline

## Goal

Turn one source video into a complete, verified delivery package. Preserve the source as evidence, use the approved video-packaging preset, create content-specific covers in the approved house visual system, and make every subtitle, chapter, cover claim, and platform claim traceable to the actual video.

This is an orchestration skill. Reuse specialized skills for editing, image generation, and platform research; keep this skill responsible for phase order, shared facts, acceptance gates, file layout, and final handoff.

## Load the references progressively

1. Read [workflow.md](references/workflow.md) at intake and keep its phase gates active throughout the run.
2. Read [packaging-profile.md](references/packaging-profile.md) before transcription, chaptering, layout, or rendering.
3. Read [approved-edit-preset.md](references/approved-edit-preset.md) before building or changing the composition. Treat its 4K values and scaling rules as the default style contract.
4. Read [covers.md](references/covers.md) when resolving the cover mode and evidence.
5. Read [approved-cover-preset.md](references/approved-cover-preset.md) before producing a `house-creative` cover.
6. Read [publishing.md](references/publishing.md) only when starting the five-platform publishing package.
7. Read [qa-and-delivery.md](references/qa-and-delivery.md) before preview approval, final render, and handoff.

## Route specialized work

- For the default local video-editing path, read and follow `hyperframes` first. Obey its current routing decision and load the selected workflow plus required domain skills. Speech-led/talking-head footage with designed overlays will commonly route to `talking-head-recut`; screen tutorials or mixed footage will commonly route to `general-video`. Whichever route applies must implement the approved preset rather than inventing another overlay style.
- Use `imagegen` for one coordinated `house-creative` cover system expressed as three independent ratio-specific compositions. Make one generation call per ratio from inspected source evidence and the approved cover preset; do not replace this with a CSS-only cover workflow or crop one master into every ratio. Preserve an existing cover only when the user explicitly asks to keep that source asset unchanged; ratio derivatives may use only the authorized content-safe adaptation described in `covers.md`.
- Use `video-platform-publishing` for current market-reference research and platform-native copy. When invoking it, explicitly override its normal cover matrix: deliver only 16:9, 3:4, and 4:3 PNG files unless the user requests more. Market research may refine hook density and proof hierarchy but must not replace the approved house visual system.
- Use ChatCut only when the user explicitly requests an editable ChatCut project or supplies an existing ChatCut project. In that case, follow the ChatCut import, transcription, graphics, verification, and export skills. Never run the HyperFrames and ChatCut editing paths in parallel for the same final master.
- Announce each specialized skill when it starts affecting the work, as required by the host skill rules.

## Input contract

- Prefer the exact video path named by the user. If no path is named and exactly one plausible video is attached or present in scope, use it. Ask one concise question only when multiple plausible source videos remain.
- Treat the source as read-only. Never replace, rename, move, trim, or delete it unless explicitly requested.
- If the user supplies no creative direction, use [approved-edit-preset.md](references/approved-edit-preset.md). Do not invent a different overlay style or ask for optional style choices.
- Resolve `cover_mode` during intake: `house-creative` by default; `preserve-asset` only when the user explicitly says to keep or reuse a specific cover unchanged; `preserve-frame` only when the user explicitly requests a source-frame cover. A nearby or same-series cover is a style reference, not an automatic pixel-preservation anchor.
- Interpret “保持之前效果”, “风格和之前一致”, “按原本样式做”, and “和之前一样” as `house-creative`: keep the fixed design DNA while deriving wording, proof, screenshots, and layout from the current video. Interpret “这张原图不变”, “沿用这个封面文件”, and “不要重做封面” as `preserve-asset`.
- The approved cover preset wins by default. A user-named different style reference overrides it for that run. If an explicitly preserved asset contains wording or a visual claim that conflicts with the current video's fact matrix, stop before production and ask whether to keep the asset despite the mismatch or switch to `house-creative`; do not silently alter or publish it.
- Detect private or sensitive content for awareness and review, but do not add a mask, blur, crop, redaction, or replacement unless the user explicitly requests it.
- User instructions override every default in this skill, including ratios, platforms, language order, and output format.

## Execute the full pipeline

1. Inspect and fully decode the source before expensive work. Record video, audio, orientation, frame rate, duration, pixel format, color metadata, and a source checksum.
2. Extract representative frames and create a fact matrix containing the audience, promise, steps, results, device/platform differences, limitations, and disclosure or rights issues.
3. Transcribe and repair the Chinese transcript, define semantic chapters, translate to concise English, and export Chinese, English, and bilingual SRT files.
4. Build the editable composition with the approved preset: centered Chinese-first bilingual captions, a compact short-lived chapter card at the extreme top-left, and a duration-weighted segmented progress system with its rail tight to the bottom edge.
5. Render review frames or a contact sheet before the full master. Correct occlusion, excessive caption height, progress-bar height, missing glyphs, and chapter transitions.
6. Render directly from the original media at source display resolution, frame rate, orientation, and color intent. Preserve the original audio when possible.
7. Run provisional structural, caption, full-decode, black-frame, boundary-frame, and visual-detail checks on the rendered master. Do not continue past a failed gate.
8. Record `cover_mode` and its evidence/style anchors. In the default `house-creative` mode, research current comparable cover patterns, then generate and verify independent 16:9, 3:4, and 4:3 covers with `imagegen` under the approved cover preset. In an explicitly requested preservation mode, adapt only as authorized.
9. Research current platform conventions and rules, then write one ready-to-paste Markdown publishing package for 微信视频号、哔哩哔哩、小红书、抖音、YouTube.
10. Re-run final whole-package QA with the finished covers and Markdown, produce the delivery report, and return clickable absolute paths for every final artifact plus inline previews of the three covers.

## Non-negotiable gates

- Do not overwrite the source or an earlier approved deliverable.
- Do not change story order, crop, color, music, or audio processing unless the user asks for it.
- Do not add privacy masks, blur, redaction, censor bars, or privacy-motivated crops unless the user explicitly asks for a specific concealment.
- Do not upscale a lower-resolution video master or silently downscale a higher-resolution video master. Required cover resizing to the declared 1920×1080, 1080×1440, and 1440×1080 outputs is an allowed cover-only operation.
- Keep captions horizontally centered and low. Keep the chapter card anchored at the extreme top-left and visible for at most 4.2 seconds per chapter. Keep the progress rail within the lowest 1% of the frame, with its playhead touching the bottom edge. Do not move the chapter title to the center or bottom by default.
- Keep Chinese visually primary and English secondary. Time-align both languages cue-for-cue.
- Reuse the approved video and cover visual tokens and behaviors, but derive chapter count, chapter text, cue timing, claims, cover wording, proof imagery, and platform copy from the current video. Never reuse topic-specific values from an earlier run.
- In `house-creative`, random style drift, mechanical cross-ratio crops, or reuse of an earlier video's topic text are hard failures. In preservation modes, unrequested changes to the selected cover asset are hard failures.
- Do not call a render successful until the file exists, fully decodes, matches required source properties, and passes representative-frame inspection.
- Do not promise that a title or cover will become viral. Provide researched, high-click-potential variants without guaranteed outcomes.
- Generate publishing files only. Do not upload or publish anywhere without separate authorization.

## Included utilities

- `scripts/extract_review_frames.py`: extract representative or explicit-timestamp review frames.
- `scripts/validate_captions.py`: validate Chinese, English, and bilingual SRT identity, timing, overlap, and reading speed.
- `scripts/media_qa.py`: compare source and final media, optionally run full decode plus source-aware black-frame checks, validate cover dimensions and publishing Markdown, and write a machine-readable QA report.

Run each utility with `--help` before first use. Treat utility success as necessary but not sufficient; the visual checks in [qa-and-delivery.md](references/qa-and-delivery.md) remain mandatory.
