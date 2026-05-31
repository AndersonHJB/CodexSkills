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

3. Create or process illustrations.
   - Use the `imagegen` skill for new bitmap cover/tutorial images.
   - For diagrams with Chinese labels, prefer deterministic SVG or HTML/CSS rendered to PNG so text is readable.
   - Save final article images locally under `images/`; keep SVG sources only when useful for future edits.

4. Generate a WeChat article cover when requested.
   - Prefer direct OpenAI `imagegen` generation of the full 2.35:1 cover first. Include the exact Chinese title, subtitle, footer/brand line, visual theme, composition, and constraints in the prompt; explicitly forbid extra words, logos, watermarks, and garbled text.
   - Inspect the generated cover visually. If the title/subtitle/footer are accurate and readable, save it as the final cover, resize to `1280x544` if needed, upload it to PicGoImage, and store the raw URL in Markdown frontmatter as `cover: <url>`.
   - If image generation produces incorrect Chinese text, fall back to a no-text `imagegen` background and overlay exact Chinese text locally:
     ```bash
     uv run --with pillow python /Users/huangjiabao/.codex/skills/wechat-article-pipeline/scripts/generate_wechat_cover.py \
       --background <background.png> \
       --output <article-dir>/images/wechat-cover.png \
       --title "文章主标题" \
       --subtitle "文章副标题" \
       --tag "工程实践" \
       --footer "AI悦创 · 公众号文章"
     ```
   - Keep the deterministic overlay script as the fallback when exact typography matters more than imagegen's integrated layout.

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
- Every remote image URL must return HTTP `200`.
- The WeChat HTML must parse as HTML and contain the expected images, tables, and code blocks.
- If `gh` is unavailable, use SSH `git@github.com:...` remotes; verify `ssh -T git@github.com` before pushing.
- Do not commit unrelated changes in BornforthisData or PicGoImage.
