#!/usr/bin/env python3
"""Verify a rendered master against its source and optional delivery assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Any


COVER_SPECS = {
    "16x9": (1920, 1080),
    "3x4": (1080, 1440),
    "4x3": (1440, 1080),
}
PLATFORMS = ("微信视频号", "哔哩哔哩", "小红书", "抖音", "YouTube")
BLACK_EVENT = re.compile(
    r"black_start:(?P<start>-?\d+(?:\.\d+)?)\s+black_end:(?P<end>-?\d+(?:\.\d+)?)\s+black_duration:(?P<duration>\d+(?:\.\d+)?)"
)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def probe(path: Path) -> dict[str, Any]:
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"ffprobe failed for {path}")
    return json.loads(result.stdout)


def stream(data: dict[str, Any], codec_type: str) -> dict[str, Any] | None:
    return next((item for item in data.get("streams", []) if item.get("codec_type") == codec_type), None)


def number(value: Any) -> float | None:
    if value in (None, "", "N/A", "0/0"):
        return None
    try:
        if isinstance(value, str) and "/" in value:
            return float(Fraction(value))
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def aspect_number(value: Any) -> float | None:
    if isinstance(value, str):
        value = value.replace(":", "/")
    return number(value)


def rotation(video: dict[str, Any] | None) -> int:
    if not video:
        return 0
    tags = video.get("tags", {})
    if "rotate" in tags:
        try:
            return int(float(tags["rotate"])) % 360
        except (TypeError, ValueError):
            pass
    for side_data in video.get("side_data_list", []):
        if "rotation" in side_data:
            try:
                return int(float(side_data["rotation"])) % 360
            except (TypeError, ValueError):
                pass
    return 0


def media_duration(data: dict[str, Any]) -> float | None:
    primary_video = stream(data, "video")
    video_duration = stream_duration(primary_video)
    if video_duration is not None:
        return video_duration
    container_duration = number(data.get("format", {}).get("duration"))
    if container_duration is not None:
        return container_duration
    candidates = [
        stream_duration(item)
        for item in data.get("streams", [])
        if item.get("codec_type") in ("video", "audio")
    ]
    present = [value for value in candidates if value is not None]
    return max(present) if present else None


def stream_duration(item: dict[str, Any] | None) -> float | None:
    if not item:
        return None
    direct = number(item.get("duration"))
    if direct is not None:
        return direct
    ticks = number(item.get("duration_ts"))
    time_base = number(item.get("time_base"))
    if ticks is not None and time_base is not None:
        return ticks * time_base
    return None


def display_geometry(video: dict[str, Any] | None) -> tuple[float | None, float | None, float | None]:
    if not video:
        return None, None, None
    width = number(video.get("width"))
    height = number(video.get("height"))
    if width is None or height is None or height == 0:
        return None, None, None
    sar = aspect_number(video.get("sample_aspect_ratio"))
    if sar is None or sar <= 0:
        sar = 1.0
    display_width = width * sar
    display_height = height
    if rotation(video) in (90, 270):
        display_width, display_height = display_height, display_width
    return display_width, display_height, display_width / display_height


def summary(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    video = stream(data, "video")
    audio = stream(data, "audio")
    format_data = data.get("format", {})
    display_width, display_height, display_aspect = display_geometry(video)
    avg_fps = number(video.get("avg_frame_rate")) if video else None
    nominal_fps = number(video.get("r_frame_rate")) if video else None
    effective_fps = avg_fps if avg_fps is not None else nominal_fps
    frame_rate_mode = None
    if avg_fps is not None and nominal_fps is not None:
        frame_rate_mode = "vfr" if not math.isclose(avg_fps, nominal_fps, rel_tol=0.0, abs_tol=0.001) else "cfr_or_unknown"
    return {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "duration_seconds": media_duration(data),
        "format": format_data.get("format_name"),
        "bit_rate": number(format_data.get("bit_rate")),
        "video_stream_count": sum(item.get("codec_type") == "video" for item in data.get("streams", [])),
        "audio_stream_count": sum(item.get("codec_type") == "audio" for item in data.get("streams", [])),
        "video": None if not video else {
            "codec": video.get("codec_name"),
            "profile": video.get("profile"),
            "width": video.get("width"),
            "height": video.get("height"),
            "rotation": rotation(video),
            "sample_aspect_ratio": video.get("sample_aspect_ratio"),
            "display_aspect_ratio": video.get("display_aspect_ratio"),
            "square_pixel_display_width": display_width,
            "square_pixel_display_height": display_height,
            "derived_display_aspect_ratio": display_aspect,
            "fps": effective_fps,
            "avg_fps": avg_fps,
            "nominal_fps": nominal_fps,
            "frame_rate_mode": frame_rate_mode,
            "start_time_seconds": number(video.get("start_time")),
            "duration_seconds": stream_duration(video),
            "pix_fmt": video.get("pix_fmt"),
            "color_range": video.get("color_range"),
            "color_space": video.get("color_space"),
            "color_transfer": video.get("color_transfer"),
            "color_primaries": video.get("color_primaries"),
            "field_order": video.get("field_order"),
        },
        "audio": None if not audio else {
            "codec": audio.get("codec_name"),
            "sample_rate": int(audio["sample_rate"]) if str(audio.get("sample_rate", "")).isdigit() else audio.get("sample_rate"),
            "channels": audio.get("channels"),
            "channel_layout": audio.get("channel_layout"),
            "start_time_seconds": number(audio.get("start_time")),
            "duration_seconds": stream_duration(audio),
        },
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_with_blackdetect(path: Path, black_min_duration: float) -> dict[str, Any]:
    command = [
        "ffmpeg", "-hide_banner", "-nostats", "-xerror", "-i", str(path),
        "-map", "0:v:0", "-map", "0:a?", "-vf", f"blackdetect=d={black_min_duration:.6f}:pix_th=0.10",
        "-f", "null", "-",
    ]
    result = run(command)
    events = [
        {key: float(value) for key, value in match.groupdict().items()}
        for match in BLACK_EVENT.finditer(result.stderr)
    ]
    return {
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "black_events": events,
        "error_tail": "\n".join(result.stderr.strip().splitlines()[-20:]) if result.returncode else "",
    }


def unexpected_black(source_events: list[dict[str, float]], output_events: list[dict[str, float]]) -> list[dict[str, float]]:
    unexpected: list[dict[str, float]] = []
    for output_event in output_events:
        matched = any(
            abs(output_event["start"] - source_event["start"]) <= 0.25
            and abs(output_event["duration"] - source_event["duration"]) <= 0.35
            for source_event in source_events
        )
        if not matched:
            unexpected.append(output_event)
    return unexpected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--cover-16x9", type=Path)
    parser.add_argument("--cover-3x4", type=Path)
    parser.add_argument("--cover-4x3", type=Path)
    parser.add_argument("--publishing-md", type=Path)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--full", action="store_true", help="Fully decode source and output and compare black intervals")
    parser.add_argument("--fail-on-unexpected-black", action="store_true")
    parser.add_argument("--black-min-duration", type=float, default=0.10)
    parser.add_argument("--duration-tolerance-frames", type=float, default=1.1)
    parser.add_argument("--fps-tolerance", type=float, default=0.01)
    parser.add_argument("--skip-hash", action="store_true")
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        parser.error("ffmpeg and ffprobe are required")
    if args.black_min_duration <= 0:
        parser.error("--black-min-duration must be positive")
    if args.fps_tolerance < 0:
        parser.error("--fps-tolerance cannot be negative")
    for label, path in (("source", args.source), ("output", args.output)):
        if not path.is_file():
            parser.error(f"{label} not found: {path}")
    if args.source.samefile(args.output):
        parser.error("source and output must be distinct files; never validate the source as its own render")
    protected_inputs = [
        args.source,
        args.output,
        args.cover_16x9,
        args.cover_3x4,
        args.cover_4x3,
        args.publishing_md,
    ]
    if args.json_out is not None:
        report_target = args.json_out.resolve()
        for protected in protected_inputs:
            if protected is None:
                continue
            same_target = report_target == protected.resolve()
            same_inode = args.json_out.exists() and protected.exists() and args.json_out.samefile(protected)
            if same_target or same_inode:
                parser.error(f"--json-out must not overwrite an input: {protected}")

    try:
        source_probe = probe(args.source)
        output_probe = probe(args.output)
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    source_summary = summary(args.source, source_probe)
    output_summary = summary(args.output, output_probe)
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, expected: Any, actual: Any, severity: str = "error") -> None:
        checks.append({
            "name": name,
            "status": "pass" if passed else ("warning" if severity == "warning" else "fail"),
            "expected": expected,
            "actual": actual,
        })

    sv = source_summary["video"]
    ov = output_summary["video"]
    sa = source_summary["audio"]
    oa = output_summary["audio"]
    add("source_video_stream", sv is not None, "present", "present" if sv else "missing")
    add("output_video_stream", ov is not None, "present", "present" if ov else "missing")
    add("video_stream_count", output_summary["video_stream_count"] == source_summary["video_stream_count"], source_summary["video_stream_count"], output_summary["video_stream_count"], severity="warning")
    add("audio_stream_count", output_summary["audio_stream_count"] == source_summary["audio_stream_count"], source_summary["audio_stream_count"], output_summary["audio_stream_count"])
    if sv and ov:
        for key in ("width", "height", "rotation"):
            add(f"video_coded_{key}", ov.get(key) == sv.get(key), sv.get(key), ov.get(key), severity="warning")
        source_sar = aspect_number(sv.get("sample_aspect_ratio")) or 1.0
        output_sar = aspect_number(ov.get("sample_aspect_ratio")) or 1.0
        add("video_coded_sample_aspect_ratio", math.isclose(source_sar, output_sar, rel_tol=0.0, abs_tol=0.000001), source_sar, output_sar, severity="warning")
        for key in ("pix_fmt", "field_order"):
            add(f"video_{key}", ov.get(key) == sv.get(key), sv.get(key), ov.get(key))
        geometry_keys = ("square_pixel_display_width", "square_pixel_display_height")
        geometry_ok = all(
            sv.get(key) is not None
            and ov.get(key) is not None
            and math.isclose(float(sv[key]), float(ov[key]), rel_tol=0.0, abs_tol=0.5)
            for key in geometry_keys
        )
        add(
            "video_display_geometry",
            geometry_ok,
            {key: sv.get(key) for key in geometry_keys},
            {key: ov.get(key) for key in geometry_keys},
        )
        source_dar = sv.get("derived_display_aspect_ratio")
        output_dar = ov.get("derived_display_aspect_ratio")
        dar_ok = source_dar is not None and output_dar is not None and math.isclose(source_dar, output_dar, rel_tol=0.0, abs_tol=0.001)
        add("video_display_aspect_ratio", dar_ok, source_dar, output_dar)
        source_fps = sv.get("fps")
        output_fps = ov.get("fps")
        fps_ok = source_fps is not None and output_fps is not None and math.isclose(source_fps, output_fps, rel_tol=0.0, abs_tol=args.fps_tolerance)
        add("video_fps", fps_ok, source_fps, output_fps, severity="warning" if sv.get("frame_rate_mode") == "vfr" else "error")
        add(
            "video_frame_rate_mode",
            sv.get("frame_rate_mode") == ov.get("frame_rate_mode"),
            sv.get("frame_rate_mode"),
            ov.get("frame_rate_mode"),
            severity="warning",
        )
        for key in ("color_range", "color_space", "color_transfer", "color_primaries"):
            expected = sv.get(key)
            actual = ov.get(key)
            add(f"video_{key}", expected in (None, "unknown") or actual == expected, expected, actual)
    else:
        source_fps = None

    add("audio_presence", (sa is None and oa is None) or (sa is not None and oa is not None), bool(sa), bool(oa))
    if sa and oa:
        add("audio_sample_rate", oa.get("sample_rate") == sa.get("sample_rate"), sa.get("sample_rate"), oa.get("sample_rate"), severity="warning")
        add("audio_channels", oa.get("channels") == sa.get("channels"), sa.get("channels"), oa.get("channels"))

    source_duration = source_summary["duration_seconds"]
    output_duration = output_summary["duration_seconds"]
    if source_duration is not None and output_duration is not None:
        tolerance = args.duration_tolerance_frames / source_fps if source_fps else 0.05
        add("duration", abs(output_duration - source_duration) <= tolerance, f"{source_duration:.6f} ± {tolerance:.6f}s", output_duration)
    else:
        add("duration", False, source_duration, output_duration)

    stream_tolerance = max(tolerance if source_duration is not None and output_duration is not None else 0.05, 0.10)
    if sv and ov:
        video_duration_available = sv.get("duration_seconds") is not None and ov.get("duration_seconds") is not None
        add(
            "video_stream_duration_available",
            video_duration_available,
            "source and output primary-video durations present",
            {"source": sv.get("duration_seconds"), "output": ov.get("duration_seconds")},
            severity="warning",
        )
    if sv and ov and sv.get("duration_seconds") is not None and ov.get("duration_seconds") is not None:
        add(
            "video_stream_duration",
            abs(ov["duration_seconds"] - sv["duration_seconds"]) <= stream_tolerance,
            f"{sv['duration_seconds']:.6f} ± {stream_tolerance:.6f}s",
            ov["duration_seconds"],
        )
    if sa and oa:
        audio_duration_available = sa.get("duration_seconds") is not None and oa.get("duration_seconds") is not None
        add(
            "audio_stream_duration_available",
            audio_duration_available,
            "source and output primary-audio durations present",
            {"source": sa.get("duration_seconds"), "output": oa.get("duration_seconds")},
            severity="warning",
        )
    if sa and oa and sa.get("duration_seconds") is not None and oa.get("duration_seconds") is not None:
        add(
            "audio_stream_duration",
            abs(oa["duration_seconds"] - sa["duration_seconds"]) <= stream_tolerance,
            f"{sa['duration_seconds']:.6f} ± {stream_tolerance:.6f}s",
            oa["duration_seconds"],
        )
        source_audio_tail = (sa.get("start_time_seconds") or 0.0) + sa["duration_seconds"]
        output_audio_tail = (oa.get("start_time_seconds") or 0.0) + oa["duration_seconds"]
        add(
            "audio_tail_time",
            abs(output_audio_tail - source_audio_tail) <= stream_tolerance,
            f"{source_audio_tail:.6f} ± {stream_tolerance:.6f}s",
            output_audio_tail,
        )

    source_bit_rate = source_summary.get("bit_rate")
    output_bit_rate = output_summary.get("bit_rate")
    if source_bit_rate and output_bit_rate and sv and ov and sv.get("codec") == ov.get("codec"):
        ratio = output_bit_rate / source_bit_rate
        add("same_codec_bitrate_review", ratio >= 0.60, ">= 60% of source or manual quality justification", round(ratio, 4), severity="warning")

    cover_args = {
        "16x9": args.cover_16x9,
        "3x4": args.cover_3x4,
        "4x3": args.cover_4x3,
    }
    cover_reports: dict[str, Any] = {}
    for label, path in cover_args.items():
        if path is None:
            continue
        if not path.is_file():
            add(f"cover_{label}", False, COVER_SPECS[label], "missing")
            continue
        try:
            image_probe = probe(path)
            image_stream = stream(image_probe, "video")
            actual_size = (image_stream.get("width"), image_stream.get("height")) if image_stream else None
            add(f"cover_{label}", actual_size == COVER_SPECS[label], COVER_SPECS[label], actual_size)
            cover_reports[label] = {"path": str(path.resolve()), "size": actual_size}
        except (RuntimeError, json.JSONDecodeError) as exc:
            add(f"cover_{label}", False, COVER_SPECS[label], str(exc))

    publishing_report: dict[str, Any] | None = None
    if args.publishing_md is not None:
        if not args.publishing_md.is_file():
            add("publishing_markdown", False, "existing UTF-8 Markdown with five platforms", "missing")
        else:
            try:
                markdown = args.publishing_md.read_text(encoding="utf-8")
                missing = [name for name in PLATFORMS if name not in markdown]
                add("publishing_markdown", not missing, "all five platform names", {"missing": missing})
                publishing_report = {"path": str(args.publishing_md.resolve()), "missing_platforms": missing}
            except UnicodeError as exc:
                add("publishing_markdown", False, "valid UTF-8", str(exc))

    decode_reports: dict[str, Any] = {}
    if args.full:
        decode_reports["source"] = decode_with_blackdetect(args.source, args.black_min_duration)
        decode_reports["output"] = decode_with_blackdetect(args.output, args.black_min_duration)
        add("source_full_decode", decode_reports["source"]["ok"], "success", decode_reports["source"]["returncode"])
        add("output_full_decode", decode_reports["output"]["ok"], "success", decode_reports["output"]["returncode"])
        unexpected = unexpected_black(
            decode_reports["source"]["black_events"],
            decode_reports["output"]["black_events"],
        )
        add(
            "unexpected_black_intervals",
            not unexpected,
            [],
            unexpected,
            severity="error" if args.fail_on_unexpected_black else "warning",
        )

    hashes = None if args.skip_hash else {
        "source_sha256": sha256(args.source),
        "output_sha256": sha256(args.output),
    }
    failures = [item for item in checks if item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warning"]
    report = {
        "status": "pass" if not failures else "fail",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "settings": {
            "full_decode": args.full,
            "black_min_duration_seconds": args.black_min_duration,
            "fail_on_unexpected_black": args.fail_on_unexpected_black,
            "duration_tolerance_frames": args.duration_tolerance_frames,
            "fps_tolerance": args.fps_tolerance,
        },
        "source": source_summary,
        "output": output_summary,
        "hashes": hashes,
        "covers": cover_reports,
        "publishing": publishing_report,
        "full_decode": decode_reports,
        "checks": checks,
        "failure_count": len(failures),
        "warning_count": len(warnings),
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
        print(f"{report['status']}: {args.json_out.resolve()} ({len(failures)} failures, {len(warnings)} warnings)")
    else:
        print(rendered, end="")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
