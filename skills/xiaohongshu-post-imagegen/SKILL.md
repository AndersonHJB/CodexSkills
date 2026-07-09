---
name: xiaohongshu-post-imagegen
description: Generate Xiaohongshu carousel post images and publishing copy from a short Chinese topic. Use when the user asks to create 小红书帖子插图, 小红书轮播图, social media education/marketing images, multi-image posts with in-image Chinese copy, or wants to provide only a theme and receive generated images plus a unified whole-post caption, title options, per-slide notes, tags, and saved deliverables.
---

# Xiaohongshu Post Imagegen

## Overview

Turn a short topic into a ready-to-post Xiaohongshu carousel: multiple vertical images with Chinese copy rendered inside the images, title options, one unified whole-post caption that matches the image set, per-slide notes, and tags.

This skill is normally used together with the built-in `imagegen` skill/tool. If the task involves generating raster images, follow the imagegen skill rules and use built-in `image_gen` by default.

## Default Output

Unless the user specifies otherwise, create 4 portrait images:

1. Cover: brand/topic hook and core offer.
2. Content: what the reader can learn or gain.
3. Audience: who it is suitable for.
4. CTA: next step, private-message keyword, or action prompt.

Use a Xiaohongshu-friendly vertical layout. Prefer 3:4 portrait output. Keep in-image Chinese text short, large, and easy to read on mobile.

Always include one unified publishing copy package for the entire carousel, not only per-image notes.

## Workflow

1. Extract the topic, offer, audience, brand name, and CTA from the user request.
2. If the user only provides a topic, infer a practical 4-slide structure. Do not ask follow-up questions unless a required brand or compliance constraint is missing.
3. Draft exact in-image Chinese copy for each slide before image generation.
4. Generate each distinct slide with one separate built-in `image_gen` call. Do not use one generic prompt for all slides.
5. Inspect every generated image with `view_image` when possible. Check:
   - Chinese characters are correct and simplified.
   - No text is cropped, tiny, or unreadable.
   - No unwanted QR code, phone number, watermark, lorem ipsum, or random English appears.
   - The slide role matches the requested carousel structure.
6. If a slide has a visible text error, regenerate only that slide with a narrower prompt and a stronger verbatim-text constraint.
7. Save final images into the current workspace under `成品/<safe-topic-name>/`. Keep generated originals in place.
8. Create `小红书发布文案.md` in the same output folder with:
   - Image filenames.
   - In-image copy for each slide.
   - Per-slide caption notes.
   - Title options for the post.
   - One unified whole-post caption written for the full image set.
   - Image order and how each image supports the caption.
   - Comment/DM call to action.
   - Tags grouped by core topic, audience, scenario, and long-tail search.
9. Report final saved paths, the generation mode, and any caveats about image text quality.

## Unified Caption Rules

Read `references/copywriting.md` before writing the publishing copy. Apply those patterns without promising virality or fabricating outcomes.

The unified caption should:

- Start with a concrete pain point, result, or question that matches the cover.
- Explain why the carousel is worth saving or reading.
- Reference the image order naturally, such as "这 4 张图整理了...".
- Use short paragraphs and scan-friendly bullets.
- Include a soft CTA such as "想要路线，私信：AI学习".
- Avoid exaggerated claims such as guaranteed income, guaranteed admission, guaranteed job offers, or impossible learning timelines.

## Prompting Rules

Read `references/prompt-templates.md` for slide prompt templates when generating a carousel.

Use these constraints in every image prompt:

- Use case: `ads-marketing`.
- Asset type: `Xiaohongshu carousel post illustration`.
- Text must be rendered verbatim in Simplified Chinese.
- Include only the listed text; avoid extra text.
- Use clean bold Chinese sans-serif typography.
- Use a balanced palette such as warm white, coral red, teal green, charcoal black, and yellow accents.
- Avoid dominant purple/blue gradients, QR codes, phone numbers, watermarks, lorem ipsum, and random UI text.
- Keep text inside safe margins and readable on mobile.

For Chinese words that often drift, explicitly specify the exact character. Example: `对` must be simplified Chinese `对` (U+5BF9), not `対`.

## File Naming

Use stable filenames:

- `01-封面-长期招生.png`
- `02-课程内容.png`
- `03-适合人群.png`
- `04-私信转化.png`

Adapt the suffixes when the topic is not enrollment-related, but keep numeric prefixes.

If replacing a flawed generated image, move the flawed copy to `_备份/` instead of deleting it.
