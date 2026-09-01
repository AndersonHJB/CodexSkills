#!/usr/bin/env python3
"""Validate a researched five-platform publishing Markdown package."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PLATFORMS = ("微信视频号", "哔哩哔哩", "小红书", "抖音", "YouTube")
DATE = re.compile(r"\b20\d{2}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12]\d|3[01])\b")
URL = re.compile(r"https://[^\s)>`]+")
NUMBERED = re.compile(r"(?m)^\s*\d+\.\s+\S")
TIMESTAMP = re.compile(r"(?m)^\s*(\d{2}):(\d{2})(?::(\d{2}))?\s+\S")
ABSOLUTE_PNG = re.compile(r"`(/[^`\n]+\.png)`")
BANNED = re.compile(r"(?<!不)(?<!无)(?:保证爆款|必爆|100%成功|全网最强|永久可用|绝对成功|万能教程)", re.IGNORECASE)


def issue(severity: str, code: str, message: str, platform: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"severity": severity, "code": code, "message": message}
    if platform is not None:
        result["platform"] = platform
    return result


def section(markdown: str, platform: str) -> str | None:
    match = re.search(rf"(?m)^##\s+{re.escape(platform)}\s*$", markdown)
    if not match:
        return None
    next_heading = re.search(r"(?m)^##\s+", markdown[match.end():])
    end = len(markdown) if next_heading is None else match.end() + next_heading.start()
    return markdown[match.end():end]


def subsection(block: str, names: tuple[str, ...]) -> str | None:
    alternatives = "|".join(re.escape(name) for name in names)
    match = re.search(rf"(?mi)^###\s+(?:{alternatives})\s*$", block)
    if not match:
        return None
    next_heading = re.search(r"(?m)^###\s+", block[match.end():])
    end = len(block) if next_heading is None else match.end() + next_heading.start()
    return block[match.end():end].strip()


def timestamp_seconds(match: re.Match[str]) -> int:
    first, second, third = match.groups()
    if third is None:
        return int(first) * 60 + int(second)
    return int(first) * 3600 + int(second) * 60 + int(third)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--min-source-urls", type=int, default=5)
    args = parser.parse_args()

    if args.json_out is not None and args.json_out.resolve() == args.markdown.resolve():
        parser.error("--json-out must not overwrite the Markdown input")

    issues: list[dict[str, Any]] = []
    if not args.markdown.is_file():
        issues.append(issue("error", "file_missing", f"Markdown not found: {args.markdown}"))
        markdown = ""
    else:
        try:
            markdown = args.markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            issues.append(issue("error", "file_read", str(exc)))
            markdown = ""

    if markdown:
        if not DATE.search(markdown):
            issues.append(issue("error", "research_date", "missing YYYY-MM-DD research date"))
        if "## 市场方法提炼" not in markdown:
            issues.append(issue("error", "market_method", "missing ## 市场方法提炼"))
        if "## 跨平台事实一致性检查" not in markdown:
            issues.append(issue("error", "fact_checklist", "missing cross-platform fact checklist"))
        if "## 研究来源" not in markdown:
            issues.append(issue("error", "sources_heading", "missing ## 研究来源"))

        urls = sorted(set(URL.findall(markdown)))
        if len(urls) < args.min_source_urls:
            issues.append(issue("error", "source_urls", f"need at least {args.min_source_urls} direct HTTPS source URLs; found {len(urls)}"))

        banned = sorted(set(match.group(0) for match in BANNED.finditer(markdown)))
        if banned:
            issues.append(issue("error", "unsupported_promise", f"unsupported promise(s): {banned}"))

        for platform in PLATFORMS:
            block = section(markdown, platform)
            if block is None:
                issues.append(issue("error", "platform_section", "missing platform section", platform))
                continue

            required = {
                "recommended_title": ("推荐标题", "Recommended title"),
                "ab_titles": ("A/B 标题", "A/B titles"),
                "rationale": ("推荐理由", "Recommendation rationale"),
                "cover": ("封面", "Thumbnail"),
                "body": ("正文", "简介", "Description"),
                "comment": ("首条评论", "置顶评论", "Pinned comment"),
                "reminders": ("发布提醒", "Publishing reminders"),
            }
            if platform == "YouTube":
                required["public_hashtags"] = ("Public hashtags", "公开 Hashtags")
                required["backend_tags"] = ("Backend tags", "后台 Tags")
            else:
                required["tags"] = ("话题", "标签", "Topics", "Hashtags")

            for code, names in required.items():
                content = subsection(block, names)
                if not content:
                    issues.append(issue("error", code, f"missing or empty subsection: {' / '.join(names)}", platform))

            variants = subsection(block, ("A/B 标题", "A/B titles")) or ""
            variant_count = len(NUMBERED.findall(variants))
            if variant_count not in (4, 5):
                issues.append(issue("error", "ab_title_count", f"expected 4 or 5 numbered A/B titles; found {variant_count}", platform))

            cover = subsection(block, ("封面", "Thumbnail")) or ""
            paths = ABSOLUTE_PNG.findall(cover)
            if len(paths) != 1:
                issues.append(issue("error", "cover_path", f"expected exactly one backticked absolute PNG path; found {len(paths)}", platform))
            elif not Path(paths[0]).is_file():
                issues.append(issue("error", "cover_missing", f"mapped cover does not exist: {paths[0]}", platform))

            if platform in ("哔哩哔哩", "YouTube"):
                chapters = subsection(block, ("分段章节", "Chapters")) or ""
                matches = list(TIMESTAMP.finditer(chapters))
                seconds = [timestamp_seconds(match) for match in matches]
                valid = len(seconds) >= 3 and seconds[0] == 0 and seconds == sorted(set(seconds))
                if valid:
                    valid = all(later - earlier >= 10 for earlier, later in zip(seconds, seconds[1:]))
                if not valid:
                    issues.append(issue("error", "chapters", "need at least three ascending chapters starting at 00:00 and spaced by at least 10 seconds", platform))

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    report = {
        "status": "pass" if not errors else "fail",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "markdown": str(args.markdown.resolve()),
        "platforms": list(PLATFORMS),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
        print(f"{report['status']}: {args.json_out.resolve()} ({len(errors)} errors, {len(warnings)} warnings)")
    else:
        print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
