# QA and delivery contract

## Default file layout

Use the source video's parent as the delivery root unless the user chooses another location:

```text
<source.ext>                                  # untouched
videos/<stem>/                               # editable project and evidence
  transcripts/
    <stem>-中文.srt
    <stem>-English.srt
    <stem>-双语.srt
  frames/                                    # review frames/contact sheets
  work/                                      # drafts and rejected variants
  video-qa.json                              # provisional master-only full check
  qa-report.json
<stem>-居中双语字幕-左上章节-置底进度条-<source-resolution>.mp4 # verified master
封面/
  <stem>-封面-16x9-1920x1080.png
  <stem>-封面-3x4-1080x1440.png
  <stem>-封面-4x3-1440x1080.png
<stem>-五平台发布文案.md
<stem>-交付清单.md
```

Use `4K` only when the source is actually a 4K raster; otherwise use an honest label such as `1080P`, `1440P`, or the exact dimensions. If any target exists, write a collision-safe sibling such as `-v2`; do not overwrite an approved artifact.

## Automated checks

Run `scripts/validate_captions.py` on the three SRTs. After the master render, run `scripts/media_qa.py --full --fail-on-unexpected-black` with only source and master and save `video-qa.json`. After covers and Markdown exist, run it again with `--full --fail-on-unexpected-black`, all three covers, the publishing Markdown, and `qa-report.json`. The second run is the final whole-package gate. If an intentional new black transition exists, omit the fail flag only after visual confirmation and record the exception.

Required media checks:

- expected video and audio streams exist;
- output square-pixel display geometry, display aspect ratio, frame cadence, pixel format, color range/intent, and channel count agree with the source; coded geometry, rotation metadata, sample aspect ratio, or sample rate changes require a documented equivalent representation or high-quality conversion;
- duration drift is no more than approximately one source frame unless documented container/audio priming explains it;
- source and output fully decode without error;
- output-only black intervals are absent or explained by source evidence;
- SHA-256, file size, bitrate, codec/profile, and media parameters are recorded.

The script flags source-aware black intervals, but inspect every warning. Intentional source black frames are not defects; new output-only black frames are.

## Visual review frames

Inspect at full resolution:

- first second, including first visible progress state;
- 0.5–1.5 seconds after every chapter boundary, plus the 4.2-second card exit point within one source frame;
- first cue after every layout change;
- at least one dense Chinese/English cue;
- the longest one-line and two-line caption plus every progress-segment boundary;
- desktop/interface, phone/portrait, person, and proof/result scenes;
- last two seconds and final frame.

Verify:

- captions remain horizontally centered and at the approved low position; any exception is documented;
- the chapter card is at the extreme top-left, fits one line, and disappears after at most 4.2 seconds;
- the progress track is truly near the bottom edge and its playhead touches the bottom edge;
- captions, chapter label, and progress maintain clear spacing;
- face/mouth, pointer, buttons, code, and result UI remain readable;
- no clipped text, bad wrapping, missing glyph, animation half-state, or accidental proxy softness;
- source/output 100% crops retain fine UI detail outside overlay regions.
- the ending has no unexplained freeze, missing tail frame, or audible cutoff;
- the progress fill visibly reaches 100% on the final program frame.
- no privacy mask, blur, censor bar, redaction, or privacy-motivated crop appears unless explicitly requested.

Treat automated composition warnings as evidence to inspect, not warnings to bulk-ignore.

## Approved preset geometry checks

For 16:9 outputs, scale the 4K base values from `approved-edit-preset.md` and verify the resulting composition geometry before render:

- the caption container and both text lines are horizontally centered within 1px;
- `caption_bottom - progress_band_height` is at least the scaled 30px structural gap, and the scaled hard-shadow clearance is at least 18px;
- `rail_bottom + rail_height <= 1% × frame_height`;
- rail and playhead center lines differ by no more than 1px;
- progress labels, the label-to-rail gap, and the rail all fit inside the bottom band;
- the playhead starts at the left progress margin and reaches `frame_width - margin - playhead_width` on the final program frame;
- chapter cards fit inside the frame at the scaled extreme-top-left anchor and fully disappear after their exposure interval.

After encoding, extract a separate bottom-overlay contact sheet and repeat the checks on the master, not only the composition preview. Also inspect composition markup/styles and source-versus-output frames for any unrequested blur, mask, censor bar, redaction, or privacy-driven crop.

## Caption checks

- Chinese, English, and bilingual files have identical cue IDs and times.
- No overlap, negative duration, blank cue, cross-chapter cue, or unreviewed high reading speed remains.
- Chinese is visually primary; English is concise and secondary.
- Brand names, versions, technical terms, and numbers match the source.
- Caption boxes avoid real content in every layout mode.

## Cover and Markdown checks

- Cover dimensions are exactly 1920×1080, 1080×1440, and 1440×1080.
- Full-size and thumbnail checks pass for text, identity, hands, devices, UI truthfulness, contrast, and safe crops.
- The delivery report records `cover_mode`; for `house-creative`, it also records the approved preset and evidence/style references, while preservation modes record the exact source asset or timestamp.
- In `house-creative`, compare every ratio against `approved-cover-preset.md`; style drift, topic-text reuse, or a mechanical crop across ratios is a hard failure.
- In preservation modes, compare every delivered cover with the recorded anchor. Unrequested changes to wording, identity, palette, typography, key artwork, or overall visual style are hard failures.
- A preserved cover whose wording or visual claim conflicts with the current fact matrix requires an explicit recorded user decision before it can enter the final package.
- Unrequested privacy blur, blanking, masking, crop, or replacement is a hard failure in every cover mode.
- The Markdown contains all five platforms, stable final paths, accurate chapters, platform-native fields, current source links, and no unsupported claim.

## Final handoff

Do not report completion while a required artifact or hard gate is missing. The final response must be self-contained and include:

- clickable absolute paths to the master, three SRTs, three covers, publishing Markdown, QA report, delivery manifest, and editable project;
- inline previews of all three covers;
- a short measured summary of source versus output dimensions, frame rate, duration, audio, color, decode status, subtitle cue count, and cover dimensions;
- any intentional deviation or remaining non-blocking caveat.

Keep failed renders and rejected covers under the project `work/` area so they cannot be mistaken for final deliverables.
