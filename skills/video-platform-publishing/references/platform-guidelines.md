# Platform Guidelines

Use these as practical defaults. If the user asks for exact current limits, monetization policy, ad policy, or upload specs, verify with current official documentation.

## Cover Ratio Matrix

Use these as production defaults. Export PNG for quality and JPG for upload compatibility unless the user asks otherwise.

| Platform | Primary cover ratio | Recommended export | Notes |
| --- | --- | --- | --- |
| 微信视频号 | 3:4 and 9:16 | 1080x1440, 1080x1920 | 3:4 is useful for feed-card presentation; 9:16 is useful when the app picks from vertical video frames. Keep key text in the center safe area. |
| 抖音 | 3:4 and 9:16 | 1080x1440, 1080x1920 | Feed cover must read on mobile. Avoid dense body text; 1 big hook plus 1 proof cue. |
| 哔哩哔哩 | 16:9 | 1920x1080 or 1280x720 | Tutorial and tech videos benefit from large title text plus UI proof/screenshot. |
| YouTube | 16:9 | 1280x720 minimum; 1920x1080 optional master | Thumbnail text should be very short. Make the first two title/description lines searchable. |
| 小红书 | 3:4, optional 4:3 or 1:1 | 1080x1440, 1440x1080, 1080x1080 | 3:4 usually gives more information-feed presence. Use note-like hooks and save-worthy framing. |

If the user asks for "all platform covers", generate at least:

- `16:9` for YouTube and 哔哩哔哩.
- `3:4` for 小红书, 微信视频号, and 抖音 feed covers.
- `9:16` for 抖音、微信视频号 vertical cover/frame needs.
- `4:3` as an alternate for 小红书 or cross-platform image posts when requested.

## Cover File Naming

Use filenames that make the target obvious:

- `cover-youtube-16x9-1280x720.png`
- `cover-bilibili-16x9-1920x1080.png`
- `cover-douyin-3x4-1080x1440.png`
- `cover-douyin-9x16-1080x1920.png`
- `cover-wechat-channels-3x4-1080x1440.png`
- `cover-xiaohongshu-3x4-1080x1440.png`
- `cover-xiaohongshu-4x3-1440x1080.png`

## Cover Composition Defaults

- Text: 4-12 Chinese characters for short-video platforms; 2-5 English words or 4-10 Chinese characters for YouTube/B站 thumbnails.
- Hierarchy: one oversized hook, one proof cue, optional small platform/tool badge.
- Proof: use an actual frame, UI screenshot, result screen, face frame, or object from the video.
- Contrast: dark translucent treatment over light screen captures; avoid low-contrast text over busy UI.
- Safe area: keep essential text away from bottom controls, avatar overlays, and platform UI crop zones.
- Variants: produce one high-curiosity option and one safer/searchable option when time allows.

## Cross-Platform Strategy

Create one core positioning sentence first:

`给[人群]看的[问题]解决/避坑内容，核心看点是[具体收益或发现]，证据是[视频里的演示/账单/对比/实测]。`

Then adapt:

- 微信视频号: trust, practical value, social sharing.
- 抖音: fast hook, curiosity, direct payoff.
- 哔哩哔哩: searchable tutorial title, clearer context, more complete intro.
- YouTube: search intent, durable title, first two description lines matter.
- 小红书: note-style experience, useful checklist, strong cover promise.

## 微信视频号

Best for acquaintances, public-domain traffic, and practical sharing.

Output:

- 标题: 14-28 Chinese characters, direct and useful.
- 封面: usually 3:4 or 9:16; 6-12 Chinese characters, readable on mobile.
- 正文: 80-180 Chinese characters, explain why worth watching and what to discuss.
- 话题: 3-6 hashtags, broader and less noisy than Douyin.
- 置顶评论: Ask for experiences, questions, or whether viewers want the next tutorial.

Tone:

- Reliable, restrained, concrete.
- Avoid excessive slang or dense tag clusters.
- Use "避坑", "讲清楚", "实测", "新手先看" when accurate.

## 抖音

Best for fast discovery and curiosity-driven clicks.

Output:

- 标题: 12-24 Chinese characters; put the hook first.
- 封面: 3:4 and/or 9:16; 4-10 Chinese characters, high contrast and emotionally clear.
- 正文: 40-120 Chinese characters; first line should stand alone.
- 话题: 5-8 hashtags mixing topic, audience, and format.
- 置顶评论: Invite a simple reply or tease the next step.

Tone:

- Punchy and conversational.
- Prefer short lines and concrete stakes.
- Do not overpromise. If content is risky, frame as "别踩坑" or "机制讲清".

## 哔哩哔哩

Best for tutorials, technical breakdowns, and searchable evergreen videos.

Output:

- 标题: 28-60 Chinese characters; include tool/topic keywords.
- 封面: 16:9; 8-16 Chinese characters plus one proof cue if available.
- 简介: 150-350 Chinese characters; mention what viewers will learn and any caveats.
- 标签: 6-10 tags, no `#` needed if used as B站 tag fields.
- 置顶评论: Add resources, correction notes, or ask for the next episode.

Tone:

- More explanatory than Douyin.
- Use terms viewers search for, such as API, Gemini, Google Cloud, 教程, 避坑.
- If useful, include timestamps or a chapter list when transcript timing is available.

## YouTube

Best for search, recommendations, and long-tail tutorials.

Output:

- Title: 45-75 characters when in English; for Chinese audience, keep searchable and not too long.
- Thumbnail: 16:9; text 2-5 words or 4-10 Chinese characters.
- Description: Start with two strong lines summarizing the value. Then add bullets, links, chapters, and disclaimers.
- Hashtags: 2-4 in the description.
- Tags: 8-15 comma-separated search tags, usually without `#`.
- Pinned comment: Ask a focused question or provide a correction/resource thread.

Tone:

- Searchable, specific, durable.
- Title formulas: "X explained", "Don't do X before Y", "X tutorial / risk / setup".
- Avoid keyword stuffing and misleading thumbnails.

## 小红书

Best for save-worthy notes, checklists, experience posts, and practical discoveries.

Output:

- 标题: 14-28 Chinese characters; use note-like hooks.
- 封面: 3:4 primary; 4:3 or 1:1 alternate when requested; 6-14 Chinese characters, often "真相/避坑/教程/清单".
- 正文: 120-300 Chinese characters; use short paragraphs or numbered points.
- 话题: 6-12 hashtags, mix broad search and specific long-tail topics.
- 置顶评论: Ask viewers to comment a keyword or share their scenario.

Tone:

- Practical, personal, organized.
- Prefer "我踩过的坑", "新手先看", "一次讲清", "别只看..." when truthful.
- Avoid making the body read like an ad.

## Tag Construction

Use this mix:

- Topic tags: tool, product, platform, domain.
- Audience tags: 程序员, AI新手, 独立开发, 内容创作者.
- Intent tags: 教程, 避坑, 实测, 经验分享, 入门.
- Problem tags: 扣费, 账号, API, 费用机制, 配置.
- Brand/tool tags: Gemini, GoogleCloud, YouTube, B站, 小红书 as relevant.

Do not include irrelevant trending tags just for reach.

## Cover Copy Patterns

Use short, legible cover text:

- `[工具] + [数字] + [风险/收益]`
- `别乱[动作]`
- `[免费/额度]真相`
- `[新手]先看`
- `[账单/实测/对比]`
- `X 分钟讲清`

For sensitive or questionable tactics, prefer:

- `别踩坑`
- `费用机制`
- `风险提醒`
- `真相`
- `新手先看`

Avoid:

- Promising illegal or ToS-violating shortcuts.
- "100%可用", "稳赚", "无限白嫖", "包过" unless the source proves it and it is compliant.
