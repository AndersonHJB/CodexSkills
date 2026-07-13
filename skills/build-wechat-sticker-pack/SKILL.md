---
name: build-wechat-sticker-pack
description: "Turn one or more user-provided reference photos into a complete publishable WeChat sticker album: plan and generate exactly 20 separate identity-consistent Q-version stickers with varied Chinese reactions, preserve untouched originals and high-resolution generation sources, create current-spec WeChat banner/cover/chat-icon assets and submission metadata, validate every deliverable, and build upload-only plus full-archive packages. Use when the user wants to create, rebuild, package, or prepare a WeChat sticker pack from reference images."
---

# Build WeChat Sticker Pack

Create an end-to-end 20-sticker production run from reference image(s). Preserve originals, generate every sticker separately, prepare WeChat publishing assets, validate, and package.

## Required companion skill and tools

Before generating images, read and follow the installed `imagegen` skill completely. Use its built-in image generation path by default. Do not silently switch to CLI/API fallback.

Use:

- built-in `image_gen` for the character anchor, 20 independent sticker artworks, banner, cover, and icon;
- `view_image` for reference inspection and visual QA;
- `scripts/sticker_pack.py` for deterministic intake, text composition, validation, contact sheet, and packaging;
- official WeChat/Tencent sources to refresh time-sensitive publishing rules.

Resolve `<skill-dir>` to the directory containing this `SKILL.md`; do not assume the workspace working directory is the skill directory.

## Non-negotiable contract

- Produce exactly 20 final stickers, numbered `01.png` through `20.png`.
- Generate the 20 sticker artworks with 20 distinct built-in `image_gen` calls. Never use a collage, multi-panel image, contact sheet, one call with `n`, or duplicated artwork as a substitute.
- Generate a separate text-free character anchor first. The anchor does not count toward the 20.
- Preserve each supplied reference file byte-for-byte with its original filename, extension, EXIF, size, and SHA-256. Never overwrite, transcode, crop, or strip the archived copy.
- Preserve every accepted high-resolution generated raw artwork and every high-resolution final master. Keep rejected retry outputs under source `versions/` when they are useful for audit, but never substitute them for an accepted slot.
- Keep contact sheets only under preview/review; never place them in the submission package.
- Do not invent ownership, copyright, portrait consent, AI disclosure, or approval status.
- Mark the run `ready-to-submit` only when all 20 stickers, publication assets, metadata, manual review gates, and rights gates pass.

## Input contract and personal defaults

Require only one or more reference images for normal self-owned runs. Load `assets/creator-profile.json` for this user's reusable defaults.

If `copyright_holder` is blank, ask one onboarding question for the exact real submitter/copyright name, save it to the profile, and continue. Never substitute the repository maintainer's identity for another user.

Apply the saved copyright holder and publishing selections. Set the current run's rights and portrait booleans explicitly after inspecting the reference. For a privately supplied self-reference, treat invocation as the user's attestation only when there is no contrary information. If the image is a public figure, third-party work, downloaded artwork, visible branded IP, or a person whose consent is unclear, ask one concise rights question before declaring the package submission-ready.

If multiple images clearly show the same subject, combine them as identity references. If they show different primary subjects and the intended subject is unclear, ask one subject-selection question.

## Output layout

Create a new run directory under `output/wechat-sticker-pack/<slug>-<timestamp>/`:

```text
00-reference-originals/       untouched user inputs + hashes
01-plan/                      pack.json, plan CSV, character/style bible, prompts
02-source-assets/
  character-anchor.png
  generated-raw/stickers/     20 untouched imagegen outputs
  generated-raw/assets/       banner, cover, icon sources
  generated-masters/          20 high-resolution text-composed masters
03-submission/
  stickers/                   01.png ... 20.png
  assets/                     banner, transparent cover, transparent icon
  metadata/                   public copy, meanings, rights/AI declaration
  qa/                         QA JSON/TXT and hashes
04-preview/contact-sheet.png
archives/<slug>-submission.zip
archives/<slug>-full-archive.zip or <slug>-draft-full-archive.zip
state.json                    local-only state; exclude from archives
```

## Workflow

### 1. Refresh platform rules

Read `references/wechat-publish-spec.md`. Browse the official WeChat Sticker Platform and current official resource code before each production run when internet access is available. If a supported requirement changed, record `changed-unsupported`, stop before generation, and update the skill and tests before resuming; never claim compatibility by changing only run metadata.

If current rules cannot be verified, continue only as a draft with the dated snapshot and record `rules_status: snapshot-unverified` plus the real check date. For a detected change, record `rules_change_details`; the script blocks generation until the skill is updated.

### 2. Inspect references and establish rights

Inspect every reference with `view_image`. Label roles explicitly: identity reference, optional outfit reference, optional style reference.

Build a character bible from visible, non-sensitive features only. Do not infer occupation, health, relationships, ethnicity, or personality from appearance.

Use the personal defaults from `assets/creator-profile.json` unless the current request overrides them. Follow `references/rights-and-ai.md`.

### 3. Plan exactly 20 stickers

Read `references/content-planning.md` before writing the plan. Create a frozen `pack.json` that matches `references/pack-schema.json` and contains:

- current album name, introduction, copyright, platform selections, and rights/AI fields;
- exactly 20 unique entries with IDs `01`–`20`;
- unique intent, exact text, meaning word, expression, pose/action, prop, framing, text zone, and art prompt;
- a character bible, style bible, shared avoid list, one anchor prompt, and publication-asset prompts.

Do not reuse the previous pack's fixed phrases automatically. Honor user-provided phrases first, then dynamically fill remaining communication roles.

Copy the profile template into the run plan and initialize the run:

```bash
python <skill-dir>/scripts/sticker_pack.py init \
  --run-dir <run-dir> \
  --spec <prepared-pack.json> \
  --reference <reference-image> [--reference <image> ...]
```

### 4. Generate and register a character anchor

Use the original reference(s) to generate one neutral, text-free Q-version character anchor. Preserve key visible identity features and one simplified outfit. Keep a plain production background and no props, words, logos, signature, border, or watermark.

Save the exact frozen anchor prompt as UTF-8 text, then register the generated file:

```bash
python <skill-dir>/scripts/sticker_pack.py import-art \
  --run-dir <run-dir> --kind anchor --source <anchor.png> \
  --generator builtin-imagegen --prompt-file <anchor-prompt.txt>
```

### 5. Generate 20 independent text-free sticker artworks

Read `references/prompt-templates.md`. For every frozen plan item:

1. Call built-in `image_gen` once with the original reference(s) plus the same character anchor.
2. Repeat the shared identity and style invariants.
3. Change only the planned expression, pose/action, prop, framing, and reserved text zone.
4. Generate one standalone square artwork with no words or text-like marks.
5. Inspect identity, action, crop, background, stray text, watermark, and one-image-only compliance.
6. Import the accepted raw image:

```bash
python <skill-dir>/scripts/sticker_pack.py import-art \
  --run-dir <run-dir> --kind sticker --slot <01..20> --source <generated.png> \
  --generator builtin-imagegen --prompt-file <slot-prompt.txt>
```

Retry policy:

- retry a tool failure once with the same prompt;
- perform one targeted prompt correction for identity drift, wrong action, crop, stray text, or multi-panel output;
- use reference(s) + anchor + best attempt for a third targeted attempt;
- stop after three failed attempts for one slot, finish safe remaining work, and mark the run draft/not-ready. Never fill the gap with a duplicate.

### 6. Compose exact text and publishing sticker files

Use the deterministic renderer instead of trusting generated Chinese lettering:

```bash
python <skill-dir>/scripts/sticker_pack.py render-stickers --run-dir <run-dir>
```

The renderer preserves raw imagegen files, creates high-resolution masters with exact planned text, produces 240×240 upload PNGs, removes derived EXIF, and writes a receipt containing text, code points, font, source hash, output hash, and layout.

If the renderer cannot fit the exact text legibly, revise only that plan item's text or layout before rendering; never silently truncate or shrink below the minimum.

### 7. Generate publication assets

Generate three distinct assets with separate built-in calls:

- detail banner: colorful opaque story scene, no text/numbers, no white or transparent background;
- album cover: recognizable front half/full body on a perfectly flat chroma-key background, no text or white outline;
- chat icon: front-facing head only on the same flat chroma key, no hands, text, decoration, white outline, or frame.

Choose a key color absent from the subject: `#00ff00` by default, or `#ff00ff` when the subject/outfit contains green. Freeze that choice in both asset prompts and the removal command.

Remove cover/icon chroma key with the helper required by the imagegen skill. Validate the alpha result; retry once with `--edge-contract 1` only if a fringe remains.

Import the untouched chroma outputs before removal, then import the accepted banner and already-transparent cover/icon:

```bash
python <skill-dir>/scripts/sticker_pack.py import-art --run-dir <run-dir> --kind cover-chroma --source <cover-chroma.png> --generator builtin-imagegen --prompt-file <cover-prompt.txt>
python <skill-dir>/scripts/sticker_pack.py import-art --run-dir <run-dir> --kind icon-chroma --source <icon-chroma.png> --generator builtin-imagegen --prompt-file <icon-prompt.txt>
python <skill-dir>/scripts/sticker_pack.py import-art --run-dir <run-dir> --kind banner --source <banner> --generator builtin-imagegen --prompt-file <banner-prompt.txt>
python <skill-dir>/scripts/sticker_pack.py import-art --run-dir <run-dir> --kind cover --source <cover-alpha.png> --generator local-chroma-removal --chroma-key <#RRGGBB> --edge-contract <0..3>
python <skill-dir>/scripts/sticker_pack.py import-art --run-dir <run-dir> --kind icon --source <icon-alpha.png> --generator local-chroma-removal --chroma-key <#RRGGBB> --edge-contract <0..3>
python <skill-dir>/scripts/sticker_pack.py prepare-assets --run-dir <run-dir>
```

### 8. Visual QA and manual gates

Create the internal contact sheet:

```bash
python <skill-dir>/scripts/sticker_pack.py contact-sheet --run-dir <run-dir>
```

Inspect the 20 final stickers individually and in the sheet. Verify character consistency, exact visible text, unique actions/silhouettes, legibility at 240×240, no watermark/logo/gibberish, and no accidental panels.

Inspect banner, cover, and icon at final size. Then set every applicable `manual_review` field in `01-plan/pack.json` to `true`. Do not confirm a field you did not actually review.

### 9. Validate and package

```bash
python <skill-dir>/scripts/sticker_pack.py validate --run-dir <run-dir> --strict
python <skill-dir>/scripts/sticker_pack.py package --run-dir <run-dir>
```

The upload-only archive must use the script's fixed allowlist and exclude originals, raw art, masters, prompts, contact sheets, state, extra files, and local absolute paths. The full archive must include byte-identical originals, sources, plans, frozen prompts, the sanitized generation ledger, submission files, QA, and provenance, but exclude local-only state and archive recursion. Warn that the full archive can retain original EXIF/GPS and should not be shared as the public upload package.

If rights or another submission gate remains unresolved, create only a clearly marked archival draft:

```bash
python <skill-dir>/scripts/sticker_pack.py package --run-dir <run-dir> --full-only
```

This produces `<slug>-draft-full-archive.zip` and quarantines any stale submission ZIP so it cannot be mistaken for a current ready package.

## Completion gate

Report success only when validation and archive integrity pass:

- `20/20 stickers passed`
- `publication assets passed`
- `original references preserved`
- `rights profile confirmed`
- `AI declaration prepared`
- `status: ready-to-submit`

Otherwise report `draft/not-ready` with the exact failed slot or gate. Always provide absolute paths to both archives, the submission directory, the copy/meaning file, and the QA report.

## Reference routing

- Read `references/content-planning.md` for every new pack.
- Read `references/prompt-templates.md` before image generation.
- Read `references/wechat-publish-spec.md` before platform asset planning or validation.
- Read `references/rights-and-ai.md` whenever a real person, third-party image, copyright, portrait right, or AI disclosure is involved.
- Use `references/pack-schema.json` when creating or repairing `pack.json`.
