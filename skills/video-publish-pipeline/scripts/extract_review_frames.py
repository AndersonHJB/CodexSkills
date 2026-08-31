#!/usr/bin/env python3
"""Extract deterministic review frames from a video with ffmpeg."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def media_info(video: Path) -> tuple[float, float | None]:
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,avg_frame_rate,r_frame_rate",
        "-of", "json", str(video),
    ])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffprobe failed")
    data = json.loads(result.stdout)
    total = float(data.get("format", {}).get("duration"))
    video_stream = next((item for item in data.get("streams", []) if item.get("codec_type") == "video"), None)
    fps = None
    if video_stream:
        for key in ("avg_frame_rate", "r_frame_rate"):
            raw = video_stream.get(key)
            try:
                candidate = float(Fraction(raw)) if raw not in (None, "", "0/0") else None
            except (TypeError, ValueError, ZeroDivisionError):
                candidate = None
            if candidate and candidate > 0:
                fps = candidate
                break
    return total, fps


def parse_times(raw_values: list[str]) -> list[float]:
    values: list[float] = []
    for raw in raw_values:
        for token in raw.split(","):
            token = token.strip()
            if token:
                values.append(float(token))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--times", action="append", default=[], help="Seconds, comma separated; repeatable")
    parser.add_argument("--count", type=int, default=8, help="Even samples when --times is omitted")
    parser.add_argument("--prefix", default="review")
    parser.add_argument("--format", choices=("png", "jpg"), default="jpg")
    args = parser.parse_args()

    if not args.video.is_file():
        parser.error(f"video not found: {args.video}")
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        parser.error("ffmpeg and ffprobe are required")
    if Path(args.prefix).name != args.prefix:
        parser.error("--prefix must be a filename prefix, not a path")

    try:
        total, fps = media_info(args.video)
        times = parse_times(args.times)
    except (RuntimeError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    if total <= 0.001:
        parser.error(f"video duration is not usable: {total}")
    if not times:
        if args.count < 2:
            parser.error("--count must be at least 2")
        pad = min(0.5, total * 0.01)
        usable = max(0.0, total - 2 * pad)
        times = [pad + usable * index / (args.count - 1) for index in range(args.count)]

    times = sorted({max(0.0, min(total, value)) for value in times})
    args.out_dir.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, object]] = []
    frame_interval = 1.0 / fps if fps else 0.04
    final_window = max(frame_interval * 2.0, 0.10)

    for index, requested_timestamp in enumerate(times, start=1):
        final_frame = requested_timestamp >= total - final_window
        label_timestamp = total if final_frame else requested_timestamp
        suffix = args.format
        output = args.out_dir / f"{args.prefix}-{index:03d}-{label_timestamp:09.3f}s.{suffix}"
        if final_frame:
            lookback = min(total, max(1.0, frame_interval * 3.0))
            command = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-sseof", f"-{lookback:.6f}",
                "-i", str(args.video), "-vf", "reverse", "-frames:v", "1", "-y",
            ]
        else:
            command = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", f"{requested_timestamp:.6f}",
                "-i", str(args.video), "-frames:v", "1", "-y",
            ]
        if suffix == "jpg":
            command.extend(["-q:v", "2"])
        command.append(str(output))
        result = run(command)
        if result.returncode != 0 or not output.is_file():
            print(result.stderr.strip() or f"failed at {requested_timestamp:.3f}s", file=sys.stderr)
            return 1
        manifest.append({
            "requested_time_seconds": round(requested_timestamp, 6),
            "frame_time_hint_seconds": round(max(0.0, total - frame_interval), 6) if final_frame else round(requested_timestamp, 6),
            "mode": "final_frame" if final_frame else "timestamp",
            "path": str(output.resolve()),
        })

    manifest_path = args.out_dir / f"{args.prefix}-manifest.json"
    manifest_path.write_text(json.dumps({
        "video": str(args.video.resolve()),
        "duration_seconds": total,
        "fps": fps,
        "frames": manifest,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(manifest_path.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
