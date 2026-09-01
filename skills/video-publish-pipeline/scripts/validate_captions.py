#!/usr/bin/env python3
"""Validate an opening-identity gate and aligned bilingual SRT deliverables."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path


TIMECODE = re.compile(
    r"^(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})\s+-->\s+"
    r"(\d{2,}):(\d{2}):(\d{2})[,.](\d{3})(?:\s+.*)?$"
)
HAN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
LATIN = re.compile(r"[A-Za-z]")


@dataclass(frozen=True)
class Cue:
    index: int
    start_ms: int
    end_ms: int
    text: str


def to_ms(parts: tuple[str, str, str, str]) -> int:
    hours, minutes, seconds, millis = map(int, parts)
    if minutes >= 60 or seconds >= 60 or millis >= 1000:
        raise ValueError(f"invalid SRT timecode component: {hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text)


def parse_srt(path: Path) -> list[Cue]:
    raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").strip()
    if not raw:
        return []
    cues: list[Cue] = []
    for block_number, block in enumerate(re.split(r"\n\s*\n", raw), start=1):
        lines = [line.rstrip() for line in block.splitlines()]
        if len(lines) < 3:
            raise ValueError(f"{path}: malformed block {block_number}")
        try:
            index = int(lines[0].strip())
        except ValueError as exc:
            raise ValueError(f"{path}: invalid cue index in block {block_number}") from exc
        match = TIMECODE.match(lines[1].strip())
        if not match:
            raise ValueError(f"{path}: invalid timecode in cue {index}")
        start_ms = to_ms(match.groups()[:4])
        end_ms = to_ms(match.groups()[4:])
        cues.append(Cue(index, start_ms, end_ms, "\n".join(lines[2:]).strip()))
    return cues


def issue(kind: str, code: str, message: str, cue: int | None = None) -> dict[str, object]:
    value: dict[str, object] = {"severity": kind, "code": code, "message": message}
    if cue is not None:
        value["cue"] = cue
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zh", required=True, type=Path)
    parser.add_argument("--en", required=True, type=Path)
    parser.add_argument("--bilingual", required=True, type=Path)
    parser.add_argument("--identity-manifest", required=True, type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--time-tolerance-ms", type=int, default=0)
    parser.add_argument("--min-duration", type=float, default=1.0)
    parser.add_argument("--max-duration", type=float, default=4.6)
    parser.add_argument("--max-zh-cps", type=float, default=10.0)
    parser.add_argument("--max-en-cps", type=float, default=18.0)
    args = parser.parse_args()

    caption_inputs = (args.zh.resolve(), args.en.resolve(), args.bilingual.resolve())
    if len(set(caption_inputs)) != 3:
        parser.error("--zh, --en, and --bilingual must be three distinct files")
    existing_inputs = (args.zh, args.en, args.bilingual)
    if all(path.exists() for path in existing_inputs):
        for index, left in enumerate(existing_inputs):
            for right in existing_inputs[index + 1:]:
                if left.samefile(right):
                    parser.error("--zh, --en, and --bilingual must not be hard links to the same file")
    if args.json_out is not None:
        same_target = args.json_out.resolve() in caption_inputs
        same_inode = args.json_out.exists() and any(path.exists() and args.json_out.samefile(path) for path in existing_inputs)
        if same_target or same_inode:
            parser.error("--json-out must not overwrite a caption input")

    issues: list[dict[str, object]] = []
    identity_manifest: dict[str, object] | None = None
    if not args.identity_manifest.is_file():
        issues.append(issue("error", "identity_manifest_missing", f"identity manifest not found: {args.identity_manifest}"))
    else:
        try:
            loaded_manifest = json.loads(args.identity_manifest.read_text(encoding="utf-8"))
            if not isinstance(loaded_manifest, dict):
                raise ValueError("identity manifest root must be an object")
            identity_manifest = loaded_manifest
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            issues.append(issue("error", "identity_manifest_parse", f"{args.identity_manifest}: {exc}"))

    parsed: dict[str, list[Cue]] = {}
    for label, path in (("zh", args.zh), ("en", args.en), ("bilingual", args.bilingual)):
        if not path.is_file():
            issues.append(issue("error", "missing_file", f"{label} file not found: {path}"))
            parsed[label] = []
            continue
        try:
            parsed[label] = parse_srt(path)
        except (OSError, UnicodeError, ValueError) as exc:
            issues.append(issue("error", "parse_error", str(exc)))
            parsed[label] = []

    zh, en, bi = parsed["zh"], parsed["en"], parsed["bilingual"]
    counts = {"zh": len(zh), "en": len(en), "bilingual": len(bi)}
    if not zh or not en or not bi:
        issues.append(issue("error", "empty_track", f"caption tracks must be non-empty: {counts}"))
    if len(set(counts.values())) != 1:
        issues.append(issue("error", "cue_count", f"cue counts differ: {counts}"))

    identity_summary: dict[str, object] = {
        "path": str(args.identity_manifest.resolve()),
        "status": None,
    }
    if identity_manifest is not None:
        status = identity_manifest.get("opening_identity_status")
        identity_summary["status"] = status
        if status not in {"confirmed", "not_present"}:
            issues.append(issue("error", "identity_status", "opening_identity_status must be confirmed or not_present"))
        elif status == "confirmed":
            required_fields = (
                "approved_chinese",
                "approved_english_or_romanized",
                "confirmation_source",
                "cue_id",
                "approved_zh_subtitle",
                "approved_en_subtitle",
            )
            missing_fields = [name for name in required_fields if identity_manifest.get(name) in (None, "")]
            for name in missing_fields:
                issues.append(issue("error", "identity_field", f"confirmed identity is missing {name}"))

            cue_id = identity_manifest.get("cue_id")
            approved_zh = identity_manifest.get("approved_zh_subtitle")
            approved_en = identity_manifest.get("approved_en_subtitle")
            identity_summary.update({
                "cue_id": cue_id,
                "approved_chinese": identity_manifest.get("approved_chinese"),
                "approved_english_or_romanized": identity_manifest.get("approved_english_or_romanized"),
                "confirmation_source": identity_manifest.get("confirmation_source"),
                "approved_zh_subtitle": approved_zh,
                "approved_en_subtitle": approved_en,
            })
            if not isinstance(cue_id, int) or cue_id < 1:
                issues.append(issue("error", "identity_cue_id", "confirmed identity cue_id must be a positive integer"))
            elif cue_id > min(len(zh), len(en), len(bi)):
                issues.append(issue("error", "identity_cue_missing", f"identity cue {cue_id} is absent from one or more tracks", cue_id))
            elif isinstance(approved_zh, str) and isinstance(approved_en, str):
                zh_cue = zh[cue_id - 1]
                en_cue = en[cue_id - 1]
                bi_cue = bi[cue_id - 1]
                if zh_cue.index != cue_id or zh_cue.text.strip() != approved_zh.strip():
                    issues.append(issue("error", "identity_zh_mismatch", "Chinese identity cue does not match the approved manifest text", cue_id))
                if en_cue.index != cue_id or en_cue.text.strip() != approved_en.strip():
                    issues.append(issue("error", "identity_en_mismatch", "English identity cue does not match the approved manifest text", cue_id))
                expected_bilingual = f"{approved_zh.strip()}\n{approved_en.strip()}"
                if bi_cue.index != cue_id or bi_cue.text.strip() != expected_bilingual:
                    issues.append(issue("error", "identity_bilingual_mismatch", "Bilingual identity cue does not exactly match the approved manifest text", cue_id))

    zh_text = " ".join(cue.text for cue in zh)
    en_text = " ".join(cue.text for cue in en)
    zh_han = len(HAN.findall(zh_text))
    zh_latin = len(LATIN.findall(zh_text))
    en_han = len(HAN.findall(en_text))
    en_latin = len(LATIN.findall(en_text))
    zh_ratio = zh_han / max(zh_han + zh_latin, 1)
    en_han_ratio = en_han / max(en_han + en_latin, 1)
    if zh and (zh_han == 0 or zh_ratio < 0.25):
        issues.append(issue("error", "zh_language", f"Chinese track does not look Chinese-dominant (Han ratio {zh_ratio:.3f})"))
    if en and (en_latin == 0 or en_han_ratio > 0.25):
        issues.append(issue("error", "en_language", f"English track does not look English-dominant (Han ratio {en_han_ratio:.3f})"))

    for label, cues in parsed.items():
        previous_end = -1
        for position, cue in enumerate(cues, start=1):
            if cue.index != position:
                issues.append(issue("error", "cue_index", f"{label} expected index {position}, got {cue.index}", cue.index))
            if cue.end_ms <= cue.start_ms:
                issues.append(issue("error", "duration", f"{label} cue has non-positive duration", cue.index))
            if cue.start_ms < previous_end:
                issues.append(issue("error", "overlap", f"{label} cue overlaps the prior cue", cue.index))
            if not normalize(cue.text):
                issues.append(issue("error", "empty_text", f"{label} cue is empty", cue.index))
            previous_end = max(previous_end, cue.end_ms)

    for position, (zh_cue, en_cue, bi_cue) in enumerate(zip(zh, en, bi), start=1):
        identity = (zh_cue.index, zh_cue.start_ms, zh_cue.end_ms)
        for label, cue in (("en", en_cue), ("bilingual", bi_cue)):
            if cue.index != identity[0] or abs(cue.start_ms - identity[1]) > args.time_tolerance_ms or abs(cue.end_ms - identity[2]) > args.time_tolerance_ms:
                issues.append(issue("error", "alignment", f"{label} timing/id differs from Chinese", position))
        normalized_zh = normalize(zh_cue.text)
        normalized_en = normalize(en_cue.text)
        normalized_bi = normalize(bi_cue.text)
        zh_position = normalized_bi.find(normalized_zh)
        en_position = normalized_bi.find(normalized_en)
        if zh_position < 0 or en_position < 0:
            issues.append(issue("error", "bilingual_content", "bilingual cue does not contain both source cue texts", position))
        elif normalized_zh != normalized_en and zh_position > en_position:
            issues.append(issue("error", "bilingual_order", "Chinese must appear before English in the bilingual cue", position))

        duration = max((zh_cue.end_ms - zh_cue.start_ms) / 1000.0, 0.001)
        if duration < args.min_duration or duration > args.max_duration:
            issues.append(issue("warning", "duration_review", f"cue duration {duration:.2f}s is outside {args.min_duration:.2f}-{args.max_duration:.2f}s", position))
        zh_cps = len(HAN.findall(zh_cue.text)) / duration
        if zh_cps > args.max_zh_cps:
            issues.append(issue("warning", "zh_reading_speed", f"Chinese reading speed is {zh_cps:.2f} chars/s", position))
        en_chars = len(re.sub(r"\s+", "", en_cue.text))
        en_cps = en_chars / duration
        if en_cps > args.max_en_cps:
            issues.append(issue("warning", "en_reading_speed", f"English reading speed is {en_cps:.2f} chars/s", position))

    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    report = {
        "status": "pass" if not errors else "fail",
        "files": {"zh": str(args.zh.resolve()), "en": str(args.en.resolve()), "bilingual": str(args.bilingual.resolve())},
        "opening_identity": identity_summary,
        "cue_counts": counts,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "issues": issues,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
        print(f"{report['status']}: {args.json_out.resolve()} ({len(errors)} errors, {len(warnings)} warnings)")
    else:
        print(rendered, end="")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
