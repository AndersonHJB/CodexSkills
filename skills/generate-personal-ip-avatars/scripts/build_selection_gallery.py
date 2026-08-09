#!/usr/bin/env python3
"""Build an offline image-selection HTML gallery from delivered IP originals."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}
CATEGORY_LABELS = {
    "designs": "动作设计",
    "full-body": "正面全身",
    "angles": "八角度",
    "emotions": "情绪头像",
    "industry": "行业全身",
}


def is_original(path: Path) -> bool:
    lowered = "/".join(part.lower() for part in path.parts)
    return (
        path.suffix.lower() in IMAGE_SUFFIXES
        and "overview" not in lowered
        and "preview" not in lowered
        and "_discarded" not in lowered
        and not path.name.startswith("00-")
    )


def classify(path: Path) -> str:
    normalized = "/".join(path.parts).lower()
    if "industry-full-body" in normalized:
        return "industry"
    if "/04-emotions/" in f"/{normalized}/":
        return "emotions"
    if "/03-angle-views/" in f"/{normalized}/":
        return "angles"
    if "/02-front-full-body/" in f"/{normalized}/":
        return "full-body"
    return "designs"


def series_name(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
        if len(relative.parts) > 1:
            return relative.parts[0]
    except ValueError:
        pass
    return path.parent.name


def read_sha_paths(manifest: Path, workspace_root: Path) -> list[Path]:
    paths: list[Path] = []
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        parts = raw.strip().split(maxsplit=1)
        if len(parts) != 2:
            continue
        candidate = Path(parts[1].lstrip("*"))
        if not candidate.is_absolute():
            candidate = workspace_root / candidate
        if candidate.is_file() and is_original(candidate):
            paths.append(candidate.resolve())
    return paths


def collect_images(root: Path, manifests: list[Path], workspace_root: Path) -> list[Path]:
    found = {p.resolve() for p in root.rglob("*") if p.is_file() and is_original(p)}
    for manifest in manifests:
        found.update(read_sha_paths(manifest, workspace_root))
    return sorted(found, key=lambda p: str(p).lower())


def make_records(images: list[Path], root: Path, output: Path) -> list[dict[str, object]]:
    records = []
    for index, image in enumerate(images, start=1):
        category = classify(image)
        series = series_name(image, root)
        records.append(
            {
                "id": f"ip-{index:04d}",
                "index": index,
                "src": Path(os.path.relpath(image, output.parent)).as_posix(),
                "name": image.stem.replace("-", " ").replace("_", " "),
                "filename": image.name,
                "series": series,
                "category": category,
                "categoryLabel": CATEGORY_LABELS[category],
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Delivered-image output root")
    parser.add_argument("--output", type=Path, required=True, help="HTML output path")
    parser.add_argument("--template", type=Path, help="Gallery template override")
    parser.add_argument("--workspace-root", type=Path, default=Path.cwd())
    parser.add_argument("--sha-manifest", type=Path, action="append", default=[])
    parser.add_argument("--title", default="我的 IP 角色选择画廊")
    parser.add_argument("--expected-count", type=int)
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    workspace_root = args.workspace_root.resolve()
    template = args.template or Path(__file__).resolve().parents[1] / "assets" / "selection-gallery-template.html"
    manifests = [m.resolve() for m in args.sha_manifest]
    images = collect_images(root, manifests, workspace_root)
    if args.expected_count is not None and len(images) != args.expected_count:
        parser.error(f"expected {args.expected_count} originals, found {len(images)}")
    if not images:
        parser.error("no original images found")

    records = make_records(images, root, output)
    payload = {
        "title": args.title,
        "total": len(records),
        "seriesCount": len({record["series"] for record in records}),
        "images": records,
    }
    html = template.read_text(encoding="utf-8")
    html = html.replace("__GALLERY_TITLE__", args.title)
    html = html.replace("__GALLERY_DATA__", json.dumps(payload, ensure_ascii=False).replace("</", "<\\/"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    print(json.dumps({"output": str(output), "originals": len(records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
