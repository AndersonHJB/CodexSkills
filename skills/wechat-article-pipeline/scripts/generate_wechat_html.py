#!/usr/bin/env python3
"""Generate a copy-ready WeChat article HTML from Markdown."""

from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CSS = r"""
:root {
  --ink: #243238;
  --muted: #657579;
  --teal: #0f8b8d;
  --teal-soft: #e9f5f4;
  --gold: #f5a63b;
  --gold-soft: #fff4df;
  --line: #ded8cd;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 28px 16px 80px;
  background: #ece8dd;
  color: var(--ink);
  font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", Arial, sans-serif;
}
.toolbar {
  position: sticky;
  top: 0;
  z-index: 9;
  max-width: 780px;
  margin: 0 auto 18px;
  padding: 12px;
  border: 1px solid rgba(36, 50, 56, 0.12);
  border-radius: 12px;
  background: rgba(255,255,255,0.92);
  box-shadow: 0 12px 28px rgba(36,50,56,0.08);
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
}
.toolbar span { color: #5d6b70; font-size: 14px; line-height: 1.5; }
.toolbar button {
  border: 0;
  border-radius: 8px;
  padding: 10px 16px;
  color: #fff;
  background: var(--teal);
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
}
.wechat-shell {
  max-width: 780px;
  margin: 0 auto;
  padding: 24px 0;
  background: #fff;
  box-shadow: 0 16px 42px rgba(36,50,56,0.10);
}
#wechat-article {
  max-width: 677px;
  margin: 0 auto;
  padding: 0 18px 42px;
  background: #fff;
  color: var(--ink);
  font-size: 16px;
  line-height: 1.95;
  letter-spacing: 0;
  overflow-wrap: break-word;
  word-break: normal;
}
#wechat-article h1 {
  margin: 12px 0 24px;
  padding: 0 0 16px;
  color: var(--ink);
  font-size: 26px;
  font-weight: 800;
  line-height: 1.38;
  text-align: left;
  border-bottom: 4px solid var(--teal);
}
#wechat-article h2 {
  margin: 34px 0 18px;
  padding: 10px 14px;
  border-left: 6px solid var(--teal);
  border-radius: 0 8px 8px 0;
  background: var(--teal-soft);
  color: var(--ink);
  font-size: 21px;
  font-weight: 800;
  line-height: 1.55;
}
#wechat-article h3 {
  margin: 28px 0 12px;
  color: var(--teal);
  font-size: 18px;
  font-weight: 800;
  line-height: 1.6;
}
#wechat-article p {
  margin: 14px 0;
  color: var(--ink);
  font-size: 16px;
  line-height: 1.95;
  text-align: justify;
}
#wechat-article p:has(img) { text-align: center; margin: 24px 0; }
#wechat-article img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 10px 26px rgba(36,50,56,0.12);
}
#wechat-article hr {
  height: 1px;
  margin: 28px 0;
  border: 0;
  background: linear-gradient(90deg, transparent, var(--line), transparent);
}
#wechat-article blockquote {
  margin: 20px 0;
  padding: 14px 16px;
  border-left: 5px solid var(--gold);
  border-radius: 0 8px 8px 0;
  background: var(--gold-soft);
  color: #5d4b2b;
}
#wechat-article blockquote p {
  margin: 0;
  color: #5d4b2b;
  font-size: 15px;
  line-height: 1.85;
  text-align: left;
}
#wechat-article ul, #wechat-article ol {
  margin: 14px 0;
  padding-left: 1.35em;
  color: var(--ink);
}
#wechat-article li {
  margin: 7px 0;
  color: var(--ink);
  font-size: 16px;
  line-height: 1.85;
}
#wechat-article table {
  width: 100%;
  margin: 22px 0;
  border-collapse: collapse;
  border: 1px solid var(--line);
  font-size: 14px;
  line-height: 1.65;
}
#wechat-article th {
  padding: 10px 8px;
  border: 1px solid var(--line);
  background: var(--teal);
  color: #fff;
  font-weight: 700;
  text-align: left;
}
#wechat-article td {
  padding: 10px 8px;
  border: 1px solid var(--line);
  color: var(--ink);
  vertical-align: top;
  background: #fff;
}
#wechat-article tr:nth-child(even) td { background: #f8fbfb; }
#wechat-article code {
  padding: 2px 6px;
  border-radius: 5px;
  background: #f1f4f4;
  color: #0d6670;
  font-family: Menlo, Consolas, Monaco, "SFMono-Regular", monospace;
  font-size: 0.92em;
  white-space: normal;
}
#wechat-article pre {
  margin: 18px 0;
  padding: 14px 16px;
  border-radius: 8px;
  background: #17242b;
  color: #eaf2f1;
  overflow-x: auto;
  line-height: 1.7;
}
#wechat-article pre code {
  padding: 0;
  background: transparent;
  color: #eaf2f1;
  font-size: 13px;
  white-space: pre;
}
#wechat-article a {
  color: #0b78c5;
  text-decoration: none;
  border-bottom: 1px solid rgba(11,120,197,0.35);
}
.copied { color: var(--teal); font-weight: 700; }
@media (max-width: 720px) {
  body { padding: 12px 8px 48px; }
  .toolbar { position: static; flex-direction: column; align-items: stretch; }
  .toolbar button { width: 100%; }
  .wechat-shell { box-shadow: none; }
  #wechat-article { padding: 0 14px 36px; }
  #wechat-article h1 { font-size: 24px; }
  #wechat-article h2 { font-size: 20px; }
}
"""


COPY_SCRIPT = r"""
const COPY_PROPS = [
  'display','box-sizing','max-width','min-width','height','margin-top','margin-right','margin-bottom','margin-left',
  'padding-top','padding-right','padding-bottom','padding-left','border-top','border-right','border-bottom','border-left',
  'border-radius','background','background-color','color','font-family','font-size','font-weight','font-style',
  'line-height','letter-spacing','text-align','text-decoration','vertical-align','white-space','overflow-wrap',
  'word-break','border-collapse','box-shadow'
];

function inlineComputedStyles(root) {
  const nodes = [root, ...root.querySelectorAll('*')];
  nodes.forEach((node) => {
    const cs = window.getComputedStyle(node);
    let styleText = '';
    COPY_PROPS.forEach((prop) => {
      const value = cs.getPropertyValue(prop);
      if (value && value !== 'normal' && value !== 'none') styleText += prop + ':' + value + ';';
    });
    if (node.tagName === 'IMG') {
      styleText += 'width:100%;max-width:100%;height:auto;display:block;margin-left:auto;margin-right:auto;';
    }
    node.setAttribute('style', styleText);
  });
}

async function copyWechatArticle() {
  const status = document.getElementById('copy-status');
  const source = document.getElementById('wechat-article');
  const clone = source.cloneNode(true);
  clone.querySelectorAll('script,style').forEach((el) => el.remove());
  clone.querySelectorAll('a[aria-hidden="true"][tabindex="-1"]').forEach((el) => el.remove());
  document.body.appendChild(clone);
  clone.style.position = 'fixed';
  clone.style.left = '-99999px';
  inlineComputedStyles(clone);
  const html = clone.innerHTML;
  clone.remove();

  try {
    if (navigator.clipboard && window.ClipboardItem) {
      await navigator.clipboard.write([
        new ClipboardItem({
          'text/html': new Blob([html], {type: 'text/html'}),
          'text/plain': new Blob([source.innerText], {type: 'text/plain'})
        })
      ]);
    } else {
      const box = document.createElement('div');
      box.contentEditable = 'true';
      box.style.position = 'fixed';
      box.style.left = '-99999px';
      box.innerHTML = html;
      document.body.appendChild(box);
      const range = document.createRange();
      range.selectNodeContents(box);
      const sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      document.execCommand('copy');
      sel.removeAllRanges();
      box.remove();
    }
    status.innerHTML = '<span class="copied">已复制。</span>现在可以粘贴到微信公众号编辑器正文区。';
  } catch (err) {
    status.textContent = '自动复制失败：请手动选中文章白色区域内容复制。';
    console.error(err);
  }
}
"""


def run_pandoc(input_path: Path) -> str:
    if not shutil.which("pandoc"):
        raise SystemExit("pandoc is required. Install pandoc or generate the HTML manually.")
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            [
                "pandoc",
                str(input_path),
                "-f",
                "markdown+yaml_metadata_block",
                "-t",
                "html",
                "--wrap=none",
                "-o",
                str(tmp_path),
            ],
            check=True,
        )
        return tmp_path.read_text(encoding="utf-8")
    finally:
        tmp_path.unlink(missing_ok=True)


def build_html(body: str, title: str) -> str:
    escaped_title = html.escape(title)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="toolbar">
    <span id="copy-status">点击右侧按钮复制排版内容，然后粘贴到微信公众号编辑器正文区。</span>
    <button type="button" onclick="copyWechatArticle()">复制公众号排版</button>
  </div>
  <main class="wechat-shell">
    <article id="wechat-article">
{body}
    </article>
  </main>
  <script>{COPY_SCRIPT}</script>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path, help="Markdown article path")
    parser.add_argument("--output", required=True, type=Path, help="Output HTML path")
    parser.add_argument("--title", default="公众号排版-可复制版", help="HTML document title")
    args = parser.parse_args()

    input_path = args.input.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"input not found: {input_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    body = run_pandoc(input_path)
    output_path.write_text(build_html(body, args.title), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
