---
name: wechat-article-pipeline
description: Create and publish Chinese WeChat/微信公众号 article packages. Use when asked to rewrite an article, design click-rate-oriented WeChat titles and summaries, inspect referenced images, generate new tutorial illustrations or WeChat article covers, upload article images to the AndersonHJB/PicGoImage GitHub image repository, replace Markdown image paths with GitHub raw URLs, archive the article under BornforthisData/公众号文章, or generate a copy-ready WeChat HTML layout.
---

# WeChat Article Pipeline

## Default Paths

- Article archive root: `/Users/huangjiabao/GitHub/Github_Repo/BornforthisData/公众号文章`
- Image host repo: `git@github.com:AndersonHJB/PicGoImage.git`
- Image host raw prefix: `https://raw.githubusercontent.com/AndersonHJB/PicGoImage/main`
- Temporary PicGoImage clone: `/tmp/PicGoImage-codex`

## Workflow

1. Read the source article and referenced assets.
   - Use `rg` to list image links in Markdown.
   - Use `view_image` for every relevant local image before rewriting or replacing it.
   - If the user references a PDF/DOCX发行资料, extract text with local tools where possible and visually inspect important images.

2. Rewrite or assemble the article.
   - Produce a new Markdown file in a dedicated working folder.
   - Preserve factual book/product information exactly: title, author, publisher, ISBN, price, and dates.
   - If source materials conflict, call out the mismatch and use the artifact that matches the requested subject.
   - For WeChat publishing, the `title:` and `summary:` must be written for吸金、爆款、有点击率. Use strong pain points, concrete outcomes, curiosity gaps, urgency, or benefit framing so readers have a clear reason to click.
   - Keep the title and summary truthful and backed by the article. Avoid unsupported numbers, false scarcity, fake guarantees, and claims not present in the content. Store them in frontmatter as `title:` and `summary:`.

3. Create or process illustrations and cover assets.
   - Use the `imagegen` skill for new bitmap cover/tutorial images.
   - For every WeChat publishing package, generate or prepare a dedicated 2.35:1 cover by default unless the user explicitly asks to skip cover creation or provides an already final cover.
   - For diagrams with Chinese labels, prefer deterministic SVG or HTML/CSS rendered to PNG so text is readable.
   - Save final article images locally under `images/`; keep SVG sources only when useful for future edits.

4. Generate a WeChat article cover.
   - For WeChat publishing, do not merely reuse the first inline article image as the cover unless the user explicitly asks for that or the source already contains a purpose-made cover.
   - Use the `imagegen` skill in built-in tool mode by default to generate the complete 2.35:1 cover in one pass, including the background illustration, title, subtitle, and footer/brand line inside the generated image.
   - Design the prompt from the article content. Include the exact cover text, visual theme, composition, typography guidance, safe margins, and constraints; explicitly forbid extra words, logos, watermarks, and garbled text.
   - Keep cover design diverse. Do not reuse a fixed title-on-right, 3D-dashboard, or single house style. Choose the art direction from the article's emotional hook and reader pain point, such as high-click tech thumbnail, editorial infographic, product strategy poster, split chaos-to-order collage, architectural blueprint, comic-style scenario, or clean premium magazine cover.
   - For important publishing packages, create or at least explicitly consider 2-3 distinct art-direction prompts before choosing the final cover. The variants should differ in layout, visual metaphor, typography hierarchy, and color rhythm, not just small color changes.
   - If the user provides a cover reference image, treat it as art-direction guidance, not as a rigid template to copy. Extract useful traits such as information density, contrast, headline hierarchy, metaphor, and click appeal.
   - Keep cover text concise enough for image generation. Prefer a short hook-style title plus one subtitle over forcing a long article title into the image.
   - Inspect the generated cover visually for text accuracy, readability, composition, and clipping. If text is wrong, iterate with a shorter or clearer prompt and regenerate the full cover with `imagegen`; do not split the cover into a generated background plus local text overlay by default.
   - Save the selected generated cover under `images/`, resize to `1280x544` if needed without editing or replacing text, upload it to PicGoImage, and store the raw URL in Markdown frontmatter as `cover: <url>`.
   - Use the local deterministic overlay script only when the user explicitly approves a fallback that separates background generation from local text rendering.

5. Upload images to PicGoImage.
   - Prefer sparse clone:
     ```bash
     rm -rf /tmp/PicGoImage-codex
     git clone --depth 1 --filter=blob:none --sparse git@github.com:AndersonHJB/PicGoImage.git /tmp/PicGoImage-codex
     ```
   - Use a stable path such as `YYYY/MMDD/<article-slug>/`.
   - Copy only final publishable image files, usually PNG/JPG/WebP.
   - Commit and push:
     ```bash
     git -C /tmp/PicGoImage-codex add --sparse YYYY/MMDD/<article-slug>
     git -C /tmp/PicGoImage-codex commit -m "Add <article topic> images"
     git -C /tmp/PicGoImage-codex push origin main
     ```
   - Verify each raw URL with `curl -L -s -o /dev/null -w '%{http_code}' <url>`.

6. Replace Markdown image links.
   - Replace local links like `images/foo.png` with raw links:
     `https://raw.githubusercontent.com/AndersonHJB/PicGoImage/main/YYYY/MMDD/<article-slug>/foo.png`
   - Keep local `images/` files in the article folder as editable backup unless the user asks to remove them.

7. Archive the article.
   - If the user asks for 公众号文章, create:
     `BornforthisData/公众号文章/<year>年/<MM-DD-topic-slug>/`
   - Move the Markdown file and local `images/` directory there.
   - Use a readable Chinese/English folder name; avoid spaces when a short hyphenated slug is clearer.

8. Generate a WeChat copy-ready HTML.
   - Use the bundled script:
     ```bash
     python /Users/huangjiabao/.codex/skills/wechat-article-pipeline/scripts/generate_wechat_html.py \
       --input <article.md> \
       --output <article-dir>/公众号排版-可复制版.html
     ```
   - The output includes a `复制公众号排版` button that copies an inline-styled HTML fragment.
   - Tell the user to open the HTML in a browser, click the button, and paste into the WeChat editor.

## Quality Gates

- All Markdown image links intended for publication must be remote `https://raw.githubusercontent.com/...` links.
- WeChat publishing Markdown should include a remote raw `cover:` URL unless the user explicitly skipped cover creation.
- Every remote image URL must return HTTP `200`.
- The WeChat HTML must parse as HTML and contain the expected images, tables, and code blocks.
- If `gh` is unavailable, use SSH `git@github.com:...` remotes; verify `ssh -T git@github.com` before pushing.
- Do not commit unrelated changes in BornforthisData or PicGoImage.
