---
name: video-platform-publishing
description: Generate platform-ready publishing packages for videos across 微信视频号, 抖音, 哔哩哔哩, YouTube, and 小红书. Use when Codex needs to research comparable high-performing videos or cover styles, create or adapt platform-specific covers/thumbnails, titles, descriptions, hashtags/search tags, cover text, pinned comments, CTAs, publishing checklists, or batch output files from a video, transcript, outline, topic, source folder, or existing draft.
---

# Video Platform Publishing

## Core Workflow

1. Gather source context from the video, transcript, outline, existing title, cover, or user notes. If a video file is available, inspect duration and existing transcript or subtitles before writing.
2. Identify the video promise in one sentence: audience, problem, outcome, proof point, and risk or caveat.
3. Run a market reference pass unless the user explicitly says not to search: inspect comparable videos and covers for the same niche/topic, summarize reusable patterns, and avoid copying any one reference.
4. Generate separate assets for each requested platform. Default platforms: 微信视频号、抖音、哔哩哔哩、YouTube、小红书.
5. Make each platform version native to that platform instead of copying one generic description everywhere.
6. Provide ready-to-paste output, including cover files or cover specs, titles, body copy, hashtags/tags, cover copy, pinned comment, and optional A/B variants.

Read `references/platform-guidelines.md` whenever producing platform-specific copy, tags, cover ratios, or publishing checklists.

Read `references/market-cover-research.md` whenever designing covers/thumbnails or when the user asks to reference market examples.

## Source Handling

When source material exists:

- Prefer the transcript over filename guesses.
- Extract 3-5 concrete content points before writing copy.
- Use the creator's actual proof, numbers, tools, timestamps, and warnings.
- Do not invent claims, links, coupons, discounts, results, or credentials.

When only a topic exists:

- State assumptions briefly.
- Generate copy that is safe to publish without claiming firsthand results.
- Ask for missing details only if they affect truthfulness or compliance.

## Cover Asset Workflow

When the user asks for covers or thumbnails:

1. Extract usable visual proof from the source: product UI, face frame, charts, before/after, invoice, code, result screen, or key object.
2. Produce platform-ratio covers using the platform matrix in `references/platform-guidelines.md`. At minimum for the default platforms, create 16:9, 3:4, and 9:16 variants when visual assets are requested.
3. Keep cover text short and large. Design for phone-feed legibility first, then desktop.
4. Save editable source files when practical, plus PNG and JPG exports. Use filenames that include platform and ratio.
5. Create a contact sheet preview so the user can compare all variants quickly.
6. Mention any visual QA performed, including exported dimensions and visible overlap/cropping issues fixed.

If a local HyperFrames project or design system exists, reuse its visual identity and assets. Otherwise, create a small local HTML/CSS cover board and render it with available browser/screenshot tooling, or use the most appropriate image/design tooling available in the current environment.

## Output Defaults

For each platform, include:

- `标题`: one recommended title plus 2-3 alternatives when useful.
- `封面`: target ratio, exported file path when generated, and short high-contrast cover text.
- `正文/简介`: platform-native copy.
- `标签/话题`: hashtags or search tags in the platform's native format.
- `置顶评论`: comment that invites discussion, clarifies caveats, or points to resources.
- `发布提醒`: 1-3 platform-specific notes when relevant.

For YouTube, separate `hashtags` from `tags` because they are used differently.

## Quality Rules

- Lead with a concrete hook, not a vague theme.
- Use the same factual core across platforms, but vary tone and structure.
- Keep Chinese short-video copy direct, useful, and searchable.
- Avoid spammy tag piles; prioritize relevant tags over volume.
- Avoid encouraging policy violations, fraud, evasion, piracy, or unsafe actions. Reframe risky content as mechanism explanation, risk warning, or compliance-aware teardown.
- If exact current platform limits, ad rules, or upload specs matter, verify with up-to-date official sources before asserting them.
- Do not copy a competitor thumbnail layout exactly. Use references to identify category conventions, then create an original cover matched to the user's video.

## Delivery Format

Default to concise Chinese Markdown:

```markdown
## 平台名

标题：
...

封面：
...

正文/简介：
...

标签/话题：
...

置顶评论：
...
```

When the user asks for batch production, place all outputs in a local Markdown file next to the source video and provide the path. When covers are generated, place them in a `covers/` or `publishing/` folder next to the source video and include a contact sheet preview.
