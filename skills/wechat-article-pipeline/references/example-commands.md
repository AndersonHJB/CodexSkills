# Example Commands

Use these patterns when the user asks for a full article publishing run.

## Find Markdown Images

```bash
rg -n '!\[[^]]*\]\([^)]+\)' article.md
```

## Verify Raw Image URLs

```bash
while read -r url; do
  code=$(curl -L -s -o /dev/null -w '%{http_code}' "$url")
  printf '%s %s\n' "$code" "$url"
done < urls.txt
```

## Generate WeChat HTML

```bash
python /Users/huangjiabao/.codex/skills/wechat-article-pipeline/scripts/generate_wechat_html.py \
  --input /path/to/article.md \
  --output /path/to/公众号排版-可复制版.html
```

## Suggested Article Folder Naming

```text
公众号文章/2026年/05-29-Claude-Code-记忆系统与-CLAUDE-md/
```
