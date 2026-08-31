# Workflow and phase gates

## A. Intake and source baseline

1. Resolve the exact source video and its output root.
2. Preserve the source byte-for-byte and compute SHA-256.
3. Probe width, height, display orientation, sample/display aspect ratio, frame rate, duration, video codec/profile, pixel format, color primaries, transfer, matrix, audio codec, sample rate, channels, and stream durations.
4. Fully decode the source. Stop if it is corrupt or its audio/video durations are not usable.
5. Detect existing burned-in captions, multiple languages, sensitive UI, QR codes, account names, and private notifications for placement and review. Detection does not authorize masking, blurring, cropping, or redaction.
6. Extract representative frames: opening, ending, each major visual change, desktop/UI operation, phone operation, person, and result/proof screens.
7. Resolve `cover_mode` plus the cover evidence and style anchors using `covers.md`. Default a new full-pipeline video to `house-creative`.

Gate: the source is uniquely identified, fully decodable, protected from overwrite, the cover mode and evidence/style anchors are recorded, and the final composition is configured to read the original media rather than a review proxy.

## B. Fact matrix

Before writing any outward-facing text, record:

- subject, version, audience, and one-sentence promise;
- actual steps and results shown;
- differences between devices, platforms, editions, or plans;
- output formats and prerequisites;
- limitations, unsupported cases, uncertainty, and safety or rights boundaries;
- real visual proof available for covers;
- disclosures required for AI-generated, marketing, sponsored, reposted, or opinion content.

Every important subtitle repair, chapter title, cover claim, title, and description must agree with this matrix and be traceable to transcript or frame evidence.

Gate: no invented feature, result, discount, credential, link, or capability remains.

## C. Transcript, chapters, and bilingual captions

1. Prefer an existing timed transcript when it is reliable; otherwise run the best available ASR on the original audio.
2. Repair Chinese semantics and names before translation. Listen again around low-confidence words, brands, versions, product terms, and code/English terms.
3. Segment by meaning and visual action. Do not let a cue cross a scene, chapter, or speaker change.
4. Lock the Chinese timing, then write concise natural English against the same cue IDs and times.
5. Export three artifacts: Chinese SRT, English SRT, and bilingual SRT.
6. Run `scripts/validate_captions.py` and repair all hard failures. Review reading-speed warnings manually.

Gate: equal cue identity and timing across languages, no overlap or empty cue, no broken terminology, and no caption that hides a critical action.

## D. Composition and review render

1. Create chapters from content, not from a fixed count or duration template.
2. Build the exact default visual system described in `approved-edit-preset.md`: centered low bilingual captions, short-lived extreme-top-left chapter cards, and a duration-weighted segmented progress rail tight to the bottom edge.
3. Keep the approved anchors stable. Prefer narrowing or rewrapping a caption before moving it; do not move the chapter card to the center or bottom. Record any necessary exception caused by a genuine critical-content collision.
4. Generate review frames before the full render. Include opening, every chapter boundary, the first frame after each layout switch, dense captions, phone/desktop scenes, last two seconds, and final frame.
5. Inspect those frames at full size and at likely phone-feed size.

Gate: progress is visibly bottom-aligned, subtitles match the approved low centered position, chapter cards remain compact and top-left, key controls and faces remain clear, every glyph renders, and the final progress state reaches 100%. Follow the active editing skill's preview-approval requirement before final render; a preview-only request never authorizes a master render.

## E. Source-fidelity master and verification

1. Render from the original source at the original display resolution, frame rate, orientation, and color intent.
2. Preserve the source audio stream when technically possible; otherwise use high-quality audio encoding without changing sample rate or channels.
3. Run `scripts/media_qa.py` on the source and master only, with `--full --fail-on-unexpected-black`, and save the provisional result as `video-qa.json`. Omit the fail flag only for an intentional new black transition and document that exception.
4. Compare fine UI text and other high-frequency detail against the source at 100% scale in regions without overlays.
5. Review unexpected black frames against the source rather than treating every intentional black scene as a failure.

Gate: no decode error, no unexplained duration drift beyond roughly one source frame, no unintended black/frozen tail, and no material clarity or color regression.

## F. Covers, platform package, and handoff

1. Produce covers only after `cover_mode`, the fact matrix, and usable source frames are ready. In `house-creative`, use the approved cover preset and current evidence; in preservation modes, change only what the user authorized.
2. Generate platform copy only after final filenames and chapter timestamps are stable.
3. Re-run `scripts/media_qa.py --full --fail-on-unexpected-black` with the same unchanged master, all three covers, and the publishing Markdown. Save this whole-package result as `qa-report.json`.
4. Verify all final files, write the delivery report, and keep failed variants outside the final delivery locations.
5. Return absolute clickable file paths and show the three cover images inline.

Gate: the final package contains the master video, three SRTs, three exact-size covers, five-platform Markdown, QA report, and retained editable project.
