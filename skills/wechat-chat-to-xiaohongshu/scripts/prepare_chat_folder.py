#!/usr/bin/env python3
"""Inventory a screenshot folder, build contact sheets, and optionally run OCR."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("Pillow is required. Run this script with the Codex workspace Python runtime.") from exc


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp", ".heic"}
GENERATED_DIR_NAMES = {
    "_xhs_generated",
    "_xhs_work",
    "_work",
    "_备份",
    "最终上传图片",
    "final-1080x1440",
    "output",
    "成品",
}
FONT_CANDIDATES = [
    Path.home() / "Library/Fonts/PingFang-SC-Regular.ttf",
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Folder containing source screenshots")
    parser.add_argument("--work-dir", type=Path, help="Destination for manifest, OCR, and contact sheets")
    parser.add_argument("--order", choices=("smart", "filename", "mtime", "exif"), default="smart")
    parser.add_argument("--order-file", type=Path, help="Text file listing filenames in explicit order")
    parser.add_argument("--ocr", action="store_true", help="Run bundled macOS Vision OCR")
    parser.add_argument("--include-generated", action="store_true", help="Include known generated/output folders")
    parser.add_argument("--contact-columns", type=int, default=4)
    parser.add_argument("--contact-rows", type=int, default=4)
    return parser.parse_args()


def natural_key(value: str) -> list[Any]:
    return [int(part) if part.isdigit() else part.casefold() for part in re.split(r"(\d+)", value)]


def discover_images(source: Path, include_generated: bool) -> list[Path]:
    if source.is_file():
        return [source] if source.suffix.casefold() in IMAGE_EXTENSIONS else []

    images: list[Path] = []
    for path in source.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        relative_parts = path.relative_to(source).parts[:-1]
        if not include_generated and any(part in GENERATED_DIR_NAMES for part in relative_parts):
            continue
        if path.suffix.casefold() in IMAGE_EXTENSIONS:
            images.append(path)
    return images


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def exif_datetime(image: Image.Image) -> str | None:
    try:
        exif = image.getexif()
    except Exception:
        return None
    raw = exif.get(36867) or exif.get(306)
    if not raw:
        return None
    value = str(raw)
    for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).isoformat(timespec="seconds")
        except ValueError:
            continue
    return value


def open_image(path: Path) -> Image.Image:
    try:
        image = Image.open(path)
        image.load()
        return ImageOps.exif_transpose(image).convert("RGB")
    except Exception as first_error:
        if path.suffix.casefold() != ".heic" or not shutil.which("sips"):
            raise first_error
        temp_dir = Path(os.environ.get("TMPDIR", "/tmp")) / "wechat-chat-to-xhs-heic"
        temp_dir.mkdir(parents=True, exist_ok=True)
        converted = temp_dir / f"{path.stem}-{sha256(path)[:8]}.png"
        result = subprocess.run(
            ["sips", "-s", "format", "png", str(path), "--out", str(converted)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"Cannot convert HEIC file: {path}") from first_error
        image = Image.open(converted)
        image.load()
        return ImageOps.exif_transpose(image).convert("RGB")


def inspect_image(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    image = open_image(path)
    width, height = image.size
    captured_at = exif_datetime(image)
    return {
        "filename": path.name,
        "relative_path": str(path.relative_to(root)) if path.is_relative_to(root) else path.name,
        "absolute_path": str(path.resolve()),
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 6),
        "orientation": "portrait" if height > width else "landscape" if width > height else "square",
        "captured_at": captured_at,
        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "bytes": stat.st_size,
        "sha256": sha256(path),
    }


def explicit_order(records: list[dict[str, Any]], order_file: Path) -> list[dict[str, Any]]:
    names = [line.strip() for line in order_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    rank = {name: index for index, name in enumerate(names)}
    return sorted(
        records,
        key=lambda item: (rank.get(item["relative_path"], rank.get(item["filename"], len(rank))), natural_key(item["relative_path"])),
    )


def sort_records(records: list[dict[str, Any]], mode: str, order_file: Path | None) -> list[dict[str, Any]]:
    if order_file:
        return explicit_order(records, order_file)
    if mode == "mtime":
        return sorted(records, key=lambda item: (item["modified_at"], natural_key(item["relative_path"])))
    if mode == "exif":
        return sorted(records, key=lambda item: (item["captured_at"] is None, item["captured_at"] or "", natural_key(item["relative_path"])))
    # Screenshot filenames are normally more reliable than mutable filesystem times.
    return sorted(records, key=lambda item: natural_key(item["relative_path"]))


def mark_duplicates(records: list[dict[str, Any]]) -> None:
    first_by_hash: dict[str, int] = {}
    for index, record in enumerate(records, start=1):
        record["index"] = index
        digest = record["sha256"]
        record["duplicate_of"] = first_by_hash.get(digest)
        first_by_hash.setdefault(digest, index)


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size)
            except OSError:
                continue
    return ImageFont.load_default()


def fit_thumbnail(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    thumb = ImageOps.contain(image, size, method=Image.Resampling.LANCZOS)
    panel = Image.new("RGB", size, "#F4F4F2")
    x = (size[0] - thumb.width) // 2
    y = (size[1] - thumb.height) // 2
    panel.paste(thumb, (x, y))
    return panel


def contact_sheet_pages(
    records: list[dict[str, Any]],
    work_dir: Path,
    columns: int,
    rows: int,
) -> list[str]:
    columns = max(1, columns)
    rows = max(1, rows)
    tile_width, image_height, label_height, gap = 360, 720, 54, 24
    page_capacity = columns * rows
    pages: list[str] = []
    font = load_font(22)

    for page_index, start in enumerate(range(0, len(records), page_capacity), start=1):
        subset = records[start : start + page_capacity]
        canvas_width = gap + columns * (tile_width + gap)
        canvas_height = gap + rows * (image_height + label_height + gap)
        canvas = Image.new("RGB", (canvas_width, canvas_height), "#E9E9E6")
        draw = ImageDraw.Draw(canvas)

        for local_index, record in enumerate(subset):
            row, column = divmod(local_index, columns)
            x = gap + column * (tile_width + gap)
            y = gap + row * (image_height + label_height + gap)
            try:
                source = open_image(Path(record["absolute_path"]))
                tile = fit_thumbnail(source, (tile_width, image_height))
            except Exception as error:
                tile = Image.new("RGB", (tile_width, image_height), "#F2D8D4")
                ImageDraw.Draw(tile).text((16, 16), f"Cannot open\n{error}", fill="#7B241C", font=font)
            canvas.paste(tile, (x, y))
            label = f"{record['index']:02d}  {record['filename']}"
            if record.get("duplicate_of"):
                label += f"  [dup {record['duplicate_of']:02d}]"
            draw.text((x, y + image_height + 10), label, fill="#222222", font=font)

        filename = "contact-sheet.jpg" if len(records) <= page_capacity else f"contact-sheet-{page_index:02d}.jpg"
        canvas.save(work_dir / filename, quality=90, optimize=True)
        pages.append(filename)
    return pages


def safe_slug(value: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff._-]+", "-", value).strip("-._")
    return cleaned or "wechat-chat"


def draft_storyboard(source_name: str, records: list[dict[str, Any]]) -> dict[str, Any]:
    slides: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        stem = safe_slug(Path(record["filename"]).stem)[:36]
        layout = "cover" if index == 1 else "chat-left" if index % 2 == 0 else "chat-right"
        slides.append(
            {
                "filename": f"{index:02d}-{stem}.png",
                "layout": layout,
                "eyebrow": "",
                "title": "",
                "subtitle": "",
                "source": {
                    "path": record["absolute_path"],
                    "crop": [0.0, 0.0, 1.0, 1.0],
                    "privacy_reviewed": False,
                    "redactions": [],
                },
                "badges": [],
                "callouts": [],
                "takeaway": "",
            }
        )
    return {
        "schema_version": 1,
        "project": {"name": source_name, "series_label": "真实沟通记录", "footer": ""},
        "canvas": [1080, 1440],
        "privacy": {"strict": True, "blocked_terms": []},
        "theme": {},
        "slides": slides,
    }


def run_ocr(records: list[dict[str, Any]], destination: Path) -> tuple[bool, str]:
    swift = shutil.which("swift")
    script = Path(__file__).with_name("macos_vision_ocr.swift")
    if not swift:
        return False, "Swift is unavailable; skipped macOS Vision OCR."
    if not script.exists():
        return False, f"OCR script is missing: {script}"
    command = [swift, str(script), *[record["absolute_path"] for record in records]]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return False, result.stderr.strip() or "Vision OCR failed."
    destination.write_text(result.stdout, encoding="utf-8")
    return True, result.stderr.strip()


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    if not source.exists():
        print(f"Source does not exist: {source}", file=sys.stderr)
        return 2

    root = source if source.is_dir() else source.parent
    work_dir = (args.work_dir or (root / "_xhs_work")).expanduser().resolve()
    work_dir.mkdir(parents=True, exist_ok=True)

    paths = discover_images(source, args.include_generated)
    if not paths:
        print(f"No supported images found in: {source}", file=sys.stderr)
        return 2

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in paths:
        try:
            records.append(inspect_image(path, root))
        except Exception as error:
            errors.append(f"{path}: {error}")

    records = sort_records(records, args.order, args.order_file)
    mark_duplicates(records)
    contact_sheets = contact_sheet_pages(records, work_dir, args.contact_columns, args.contact_rows)

    manifest = {
        "schema_version": 1,
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_root": str(root),
        "sort_mode": "explicit" if args.order_file else args.order,
        "contact_sheets": contact_sheets,
        "image_count": len(records),
        "errors": errors,
        "images": records,
    }
    (work_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (work_dir / "storyboard.draft.json").write_text(
        json.dumps(draft_storyboard(root.name, records), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    ocr_message = "OCR not requested."
    if args.ocr:
        ok, message = run_ocr(records, work_dir / "ocr.tsv")
        ocr_message = "OCR written to ocr.tsv." if ok else f"WARNING: {message}"

    print(f"Prepared {len(records)} image(s) in {work_dir}")
    print(f"Contact sheet(s): {', '.join(contact_sheets)}")
    print(ocr_message)
    for error in errors:
        print(f"WARNING: {error}", file=sys.stderr)
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
