---
name: wechat-chat-to-xiaohongshu
description: Turn a folder of WeChat/微信 chat screenshots into a privacy-safe, ready-to-publish Xiaohongshu/小红书 carousel package. Use when the user provides chat screenshots or a screenshot folder and asks to analyze the conversation, reconstruct its order, anonymize private information, design or generate carousel images, preserve real chat evidence, and deliver titles, one unified caption, hashtags, slide notes, a contact sheet, and QA results. Also use for 私教沟通记录, 客户案例, 咨询复盘, 成交过程, 学习规划, or other screenshot-based story posts. Do not use when the user only provides a topic with no chat screenshots; use xiaohongshu-post-imagegen instead.
---

# WeChat Chat to Xiaohongshu

## Goal

Convert raw WeChat screenshots into an accurate, anonymized Xiaohongshu story package while keeping the source folder unchanged. Preserve real screenshots as evidence; add editorial hierarchy around them instead of redrawing chat text with an image model.

## Default Deliverables

Create `成品/<safe-project-name>/` with:

```text
01-封面-<topic>.png
02-<slide-topic>.png
...
小红书发布文案.md
轮播总览.jpg
质检报告.md
_work/
  manifest.json
  ocr.tsv
  storyboard.json
```

Default to 6-14 slides, 1080 x 1440 pixels, based on the amount of useful material. Do not pad a weak story to reach a target count. Keep the final slide order numeric and contiguous.

## Required Workflow

### 1. Confirm Usable Inputs

Accept a folder path, attached screenshots, or both. If the user provides only a Finder/file-list screenshot, explain that it shows filenames but not conversation content and request the actual image files. Do not ask for brand, audience, or CTA details when they can be inferred safely.

Use strict privacy defaults unless the user explicitly requests a different policy:

- Hide non-public names, avatars, account IDs, phone numbers, email addresses, addresses, order or payment identifiers, QR codes, and private links.
- Keep prices, dates, schools, workplaces, schedules, or medical/family details only when editorially necessary and non-identifying.
- Never expose a student's or client's identity as social proof without explicit user direction.

### 2. Inventory, Sort, and OCR

Run the bundled preparation script with a Python 3 runtime that includes Pillow. In Codex desktop, call `codex_app__load_workspace_dependencies` first and use the reported Python executable when the system Python lacks Pillow.

```bash
python3 scripts/prepare_chat_folder.py \
  "/absolute/path/to/source-folder" \
  --work-dir "/absolute/path/to/成品/<project>/_work" \
  --ocr
```

Read `manifest.json`, inspect every generated contact sheet with `view_image`, and inspect ambiguous screenshots individually. Treat filename order and OCR as drafts. Reorder by visible timestamps, message continuity, repeated boundary messages, and referenced attachments.

Read `references/input-analysis.md` before interpreting the conversation or defining redactions. Do not infer the speaker from bubble color alone; verify bubble side and conversation context.

### 3. Build an Evidence Ledger

Before writing the post, record in `_work/evidence-ledger.md`:

- Verified facts stated in the screenshots.
- User/service-provider statements versus the other participant's statements.
- Editorially useful themes and turning points.
- Unclear OCR or ambiguous claims that must not be published as facts.
- Required redactions for each source image.

Paraphrase faithfully. Do not invent outcomes, satisfaction, enrollment, revenue, grades, results, or endorsements. A payment screenshot proves only the visible transaction, not satisfaction or future results.

### 4. Plan the Story

Read `references/story-and-copy.md` and `references/storyboard-schema.md`. Create `_work/storyboard.json` from the preparation script's draft.

Choose one clear narrative, such as:

- Need -> diagnosis -> plan -> next step.
- Initial question -> key objections -> response -> decision.
- Common mistake -> real conversation evidence -> practical checklist.
- Before-class uncertainty -> course design -> schedule and setup.

Use one screenshot only when it materially supports the slide's point. Crop to the relevant exchange without removing context that changes meaning. Keep each slide's headline useful even when read without the caption.

Set `privacy_reviewed: true` only after visually checking the source crop and every redaction rectangle. Add all names and sensitive strings to `privacy.blocked_terms` for OCR-based final QA.

### 5. Choose the Visual Mode

Use `screenshot-editorial` by default. Render original screenshots inside a designed editorial layout with the bundled renderer. This protects exact chat wording and produces repeatable output.

Use generated imagery only for a cover illustration, background asset, or fully illustrated post explicitly requested by the user. Follow the installed `xiaohongshu-post-imagegen` and built-in `imagegen` instructions in that case. Never ask an image model to recreate a real chat screenshot or render long verbatim chat text.

Read `references/design-system.md` before finalizing the storyboard. Keep a restrained multi-color palette, large Chinese typography, generous safe margins, and a legible screenshot scale.

### 6. Render

Run:

```bash
python3 scripts/render_carousel.py \
  "/absolute/path/to/成品/<project>/_work/storyboard.json" \
  --output-dir "/absolute/path/to/成品/<project>"
```

The renderer supports `cover`, `chat-left`, `chat-right`, and `chat-full` layouts plus crop and blur/pixelate/solid redaction rectangles. Fix the storyboard when rendering reports overflow; do not shrink body text below mobile-readable sizes merely to force content to fit.

### 7. Write the Publishing Package

Create `小红书发布文案.md` with:

1. Five title options, with one recommended title.
2. One unified caption for the full carousel.
3. A numbered slide-order guide matching exact filenames.
4. A conservative interaction or DM prompt when appropriate.
5. 8-15 relevant hashtags, including a recommended final tag line.
6. A privacy note when the post uses real conversation records.

Use Simplified Chinese unless the user requests another language. Keep the voice practical and human. Avoid virality promises, fake scarcity, guaranteed outcomes, and unsupported superlatives.

### 8. Inspect and Validate

Inspect every final image and `轮播总览.jpg` with `view_image`. Check text, crop, order, privacy, screenshot legibility, and visual consistency. Regenerate only the affected slides.

Then run:

```bash
python3 scripts/validate_package.py \
  "/absolute/path/to/成品/<project>/_work/storyboard.json" \
  --output-dir "/absolute/path/to/成品/<project>" \
  --copy "/absolute/path/to/成品/<project>/小红书发布文案.md" \
  --ocr
```

Do not report completion while validation has errors. Treat OCR privacy checks as a backstop, not a substitute for visual review.

## Revision Rules

- Keep the source folder untouched.
- Move replaced final slides to `成品/<project>/_备份/`; do not delete them.
- Preserve filenames for unaffected slides so publishing order remains stable.
- Update `storyboard.json`, publishing copy, overview image, and QA report together after a structural revision.
- Never publish raw OCR text as the final caption without checking it against the screenshots.

## Resource Routing

- Read `references/input-analysis.md` for ordering, OCR correction, speaker attribution, and privacy review.
- Read `references/story-and-copy.md` for slide selection, titles, captions, tags, and claim discipline.
- Read `references/design-system.md` for visual hierarchy, layout selection, typography, and QA.
- Read `references/storyboard-schema.md` while authoring or debugging `storyboard.json`.
