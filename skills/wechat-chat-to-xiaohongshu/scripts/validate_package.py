#!/usr/bin/env python3
"""Validate rendered Xiaohongshu slides, publishing copy, and privacy terms."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageStat
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("Pillow is required. Run this script with the Codex workspace Python runtime.") from exc


REQUIRED_COPY_HEADINGS = [
    "## 推荐标题",
    "## 备选标题",
    "## 整帖统一发布文案",
    "## 图片顺序说明",
    "## 互动引导",
    "## 标签组合",
    "## 推荐发布标签",
    "## 隐私说明",
]


@dataclass
class Finding:
    severity: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--copy", type=Path, help="Publishing Markdown file")
    parser.add_argument("--ocr", action="store_true", help="OCR final slides and scan for blocked terms")
    return parser.parse_args()


def add(findings: list[Finding], severity: str, message: str) -> None:
    findings.append(Finding(severity, message))


def visible_slide_text(slide: dict[str, Any]) -> str:
    parts = [
        str(slide.get("eyebrow", "")),
        str(slide.get("title", "")),
        str(slide.get("subtitle", "")),
        str(slide.get("takeaway", "")),
    ]
    parts.extend(str(value) for value in slide.get("badges", []))
    for callout in slide.get("callouts", []):
        parts.append(str(callout.get("title", "")))
        parts.append(str(callout.get("body", "")))
    return "\n".join(parts)


def scan_terms(text: str, blocked: list[str], allowed: list[str]) -> list[str]:
    lowered = text.casefold()
    allowed_lower = {term.casefold() for term in allowed}
    return [term for term in blocked if term.casefold() not in allowed_lower and term.casefold() in lowered]


def validate_storyboard(plan: dict[str, Any], findings: list[Finding]) -> list[dict[str, Any]]:
    if plan.get("schema_version") != 1:
        add(findings, "error", "storyboard.schema_version 必须为 1。")
    slides = plan.get("slides")
    if not isinstance(slides, list) or not slides:
        add(findings, "error", "storyboard.slides 不能为空。")
        return []
    privacy = plan.get("privacy", {})
    strict = privacy.get("strict", True)
    blocked = [str(term) for term in privacy.get("blocked_terms", []) if str(term).strip()]
    allowed = [str(term) for term in privacy.get("allowed_terms", []) if str(term).strip()]
    if strict and not blocked:
        add(findings, "warning", "严格隐私模式下 blocked_terms 为空；请确认素材确实没有可识别姓名或链接。")

    seen: set[str] = set()
    for index, slide in enumerate(slides, start=1):
        filename = str(slide.get("filename", ""))
        if not re.match(rf"^{index:02d}[-_].+\.png$", filename, re.IGNORECASE):
            add(findings, "error", f"第 {index} 张文件名未按顺序命名：{filename}")
        if filename in seen:
            add(findings, "error", f"轮播文件名重复：{filename}")
        seen.add(filename)
        if not str(slide.get("title", "")).strip():
            add(findings, "error", f"第 {index} 张缺少标题。")
        source = slide.get("source")
        if not isinstance(source, dict):
            add(findings, "error", f"第 {index} 张缺少 source。")
        elif strict and source.get("privacy_reviewed") is not True:
            add(findings, "error", f"第 {index} 张尚未确认隐私检查。")
        leaked = scan_terms(visible_slide_text(slide), blocked, allowed)
        if leaked:
            add(findings, "error", f"第 {index} 张编辑文案包含 blocked_terms：{', '.join(leaked)}")
    return slides


def validate_images(slides: list[dict[str, Any]], output_dir: Path, findings: list[Finding]) -> list[Path]:
    paths: list[Path] = []
    for index, slide in enumerate(slides, start=1):
        path = output_dir / str(slide.get("filename", ""))
        if not path.exists():
            add(findings, "error", f"缺少第 {index} 张成品图：{path.name}")
            continue
        paths.append(path)
        try:
            with Image.open(path) as image:
                if image.size != (1080, 1440):
                    add(findings, "error", f"{path.name} 尺寸为 {image.width}x{image.height}，应为 1080x1440。")
                if image.mode not in {"RGB", "RGBA"}:
                    add(findings, "warning", f"{path.name} 色彩模式为 {image.mode}，建议 RGB/RGBA。")
                stat = ImageStat.Stat(image.convert("L").resize((64, 64)))
                if stat.extrema[0][1] - stat.extrema[0][0] < 12 or stat.stddev[0] < 4:
                    add(findings, "error", f"{path.name} 可能为空白或对比度异常。")
        except Exception as error:
            add(findings, "error", f"无法读取 {path.name}：{error}")

    overview = output_dir / "轮播总览.jpg"
    if not overview.exists():
        add(findings, "error", "缺少轮播总览.jpg。")
    return paths


def section_text(markdown: str, heading: str) -> str:
    start = markdown.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    match = re.search(r"^##\s+", markdown[start:], flags=re.MULTILINE)
    end = start + match.start() if match else len(markdown)
    return markdown[start:end]


def validate_copy(
    copy_path: Path | None,
    slides: list[dict[str, Any]],
    privacy: dict[str, Any],
    findings: list[Finding],
) -> str:
    if copy_path is None:
        add(findings, "warning", "未提供小红书发布文案文件。")
        return ""
    if not copy_path.exists():
        add(findings, "error", f"发布文案不存在：{copy_path}")
        return ""
    markdown = copy_path.read_text(encoding="utf-8")
    for heading in REQUIRED_COPY_HEADINGS:
        if heading not in markdown:
            add(findings, "error", f"发布文案缺少章节：{heading}")

    alternatives = section_text(markdown, "## 备选标题")
    title_items = re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S+", alternatives, flags=re.MULTILINE)
    if len(title_items) < 4:
        add(findings, "warning", f"备选标题只有 {len(title_items)} 条；建议与推荐标题合计 5 条。")

    tag_section = section_text(markdown, "## 标签组合") + section_text(markdown, "## 推荐发布标签")
    hashtags = set(re.findall(r"#[^\s#，,。；;]+", tag_section))
    if not 8 <= len(hashtags) <= 15:
        add(findings, "warning", f"标签共 {len(hashtags)} 个；建议 8-15 个。")

    for slide in slides:
        filename = str(slide.get("filename", ""))
        if filename and filename not in markdown:
            add(findings, "error", f"图片顺序说明未引用文件名：{filename}")

    blocked = [str(term) for term in privacy.get("blocked_terms", [])]
    allowed = [str(term) for term in privacy.get("allowed_terms", [])]
    leaked = scan_terms(markdown, blocked, allowed)
    if leaked:
        add(findings, "error", f"发布文案包含 blocked_terms：{', '.join(leaked)}")
    return markdown


def run_final_ocr(paths: list[Path], destination: Path) -> tuple[str, str | None]:
    swift = shutil.which("swift")
    script = Path(__file__).with_name("macos_vision_ocr.swift")
    if not swift or not script.exists():
        return "", "Swift 或 OCR 脚本不可用，未执行最终 OCR。"
    result = subprocess.run([swift, str(script), *[str(path) for path in paths]], capture_output=True, text=True)
    if result.returncode != 0:
        return "", result.stderr.strip() or "最终 OCR 执行失败。"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(result.stdout, encoding="utf-8")
    texts: list[str] = []
    for line in result.stdout.splitlines()[1:]:
        fields = line.split("\t", 8)
        if len(fields) == 9:
            texts.append(fields[8])
    return "\n".join(texts), result.stderr.strip() or None


def validate_ocr_text(text: str, privacy: dict[str, Any], findings: list[Finding]) -> None:
    blocked = [str(term) for term in privacy.get("blocked_terms", [])]
    allowed = [str(term) for term in privacy.get("allowed_terms", [])]
    leaked = scan_terms(text, blocked, allowed)
    if leaked:
        add(findings, "error", f"最终图片 OCR 检出 blocked_terms：{', '.join(leaked)}")

    scrubbed = text
    for term in allowed:
        scrubbed = re.sub(re.escape(term), "", scrubbed, flags=re.IGNORECASE)
    if re.search(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)", scrubbed):
        add(findings, "warning", "最终图片 OCR 检出疑似手机号，请逐图核对。")
    if re.search(r"(?:https?://|www\.)\S+", scrubbed, flags=re.IGNORECASE):
        add(findings, "warning", "最终图片 OCR 检出网址，请确认是否为公开且必要的信息。")


def write_report(path: Path, findings: list[Finding], slide_count: int, ocr_ran: bool) -> None:
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    status = "通过" if not errors else "未通过"
    lines = [
        "# 小红书轮播质检报告",
        "",
        f"- 时间：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- 状态：{status}",
        f"- 图片数量：{slide_count}",
        f"- 最终图片 OCR：{'已执行' if ocr_ran else '未执行'}",
        f"- 错误：{len(errors)}",
        f"- 警告：{len(warnings)}",
        "",
        "## 错误",
        "",
    ]
    lines.extend(f"- {finding.message}" for finding in errors)
    if not errors:
        lines.append("- 无")
    lines.extend(["", "## 警告", ""])
    lines.extend(f"- {finding.message}" for finding in warnings)
    if not warnings:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## 人工复核",
            "",
            "- [ ] 已逐张查看最终 PNG。",
            "- [ ] 已查看轮播总览并确认叙事顺序。",
            "- [ ] 已确认头像、昵称、账号、链接、二维码和交易信息均不可识别。",
            "- [ ] 已确认标题、正文、标签与图片内容一致。",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    storyboard_path = args.storyboard.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    copy_path = args.copy.expanduser().resolve() if args.copy else None
    findings: list[Finding] = []
    if not storyboard_path.exists():
        print(f"Storyboard does not exist: {storyboard_path}", file=sys.stderr)
        return 2
    try:
        plan = json.loads(storyboard_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Invalid storyboard JSON: {error}", file=sys.stderr)
        return 2

    slides = validate_storyboard(plan, findings)
    paths = validate_images(slides, output_dir, findings)
    privacy = plan.get("privacy", {})
    validate_copy(copy_path, slides, privacy, findings)

    ocr_ran = False
    if args.ocr and paths:
        ocr_text, ocr_warning = run_final_ocr(paths, storyboard_path.parent / "final-ocr.tsv")
        if ocr_warning:
            add(findings, "warning", ocr_warning)
        if ocr_text:
            ocr_ran = True
            validate_ocr_text(ocr_text, privacy, findings)

    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "质检报告.md"
    write_report(report_path, findings, len(paths), ocr_ran)
    errors = [finding for finding in findings if finding.severity == "error"]
    warnings = [finding for finding in findings if finding.severity == "warning"]
    print(f"QA report: {report_path}")
    print(f"Errors: {len(errors)}; warnings: {len(warnings)}")
    for finding in findings:
        print(f"{finding.severity.upper()}: {finding.message}")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
