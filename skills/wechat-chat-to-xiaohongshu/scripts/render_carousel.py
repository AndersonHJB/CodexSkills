#!/usr/bin/env python3
"""Render a privacy-reviewed screenshot storyboard into Xiaohongshu slides."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError as exc:  # pragma: no cover - environment guard
    raise SystemExit("Pillow is required. Run this script with the Codex workspace Python runtime.") from exc


BASE_SIZE = (1080, 1440)
DEFAULT_THEME = {
    "background": "#F7F3EA",
    "paper": "#FFFDF8",
    "ink": "#20231F",
    "muted": "#62675F",
    "accent": "#D9573F",
    "accent_2": "#4E6B45",
    "accent_3": "#D7A928",
    "line": "#D8D1C3",
}
REGULAR_FONT_CANDIDATES = [
    Path.home() / "Library/Fonts/PingFang-SC-Regular.ttf",
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path("/System/Library/Fonts/STHeiti Light.ttc"),
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
]
BOLD_FONT_CANDIDATES = [
    Path("/System/Library/Fonts/STHeiti Medium.ttc"),
    Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
    Path.home() / "Library/Fonts/PingFang-SC-Regular.ttf",
]
LAYOUTS = {"cover", "chat-left", "chat-right", "chat-full"}


class RenderError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("storyboard", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def color(value: str) -> str:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
        raise RenderError(f"Invalid color: {value}")
    return value


def resolve_path(value: str, base: Path) -> Path:
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (base / path).resolve()


class FontBook:
    def __init__(self, theme: dict[str, Any], plan_dir: Path):
        self.regular_path = self._resolve_font(theme.get("font_regular"), plan_dir, REGULAR_FONT_CANDIDATES)
        self.bold_path = self._resolve_font(theme.get("font_bold"), plan_dir, BOLD_FONT_CANDIDATES)

    @staticmethod
    def _resolve_font(value: str | None, base: Path, candidates: Sequence[Path]) -> Path:
        if value:
            path = resolve_path(value, base)
            if not path.exists():
                raise RenderError(f"Font does not exist: {path}")
            return path
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise RenderError("No Chinese font found. Set theme.font_regular and theme.font_bold.")

    def get(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(str(self.bold_path if bold else self.regular_path), size=size)


def text_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text or " ", font=font)
    return box[2] - box[0]


def line_height(font: ImageFont.ImageFont, multiplier: float = 1.18) -> int:
    box = font.getbbox("国Ag")
    return max(1, int((box[3] - box[1]) * multiplier))


def tokens_for_wrap(text: str) -> list[str]:
    return re.findall(r"[\u3400-\u9fff]|[A-Za-z0-9][A-Za-z0-9_./:+%-]*|\s+|.", text)


def wrap_line(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    if not text:
        return [""]
    lines: list[str] = []
    current = ""
    for token in tokens_for_wrap(text):
        if token.isspace() and not current:
            continue
        candidate = current + token
        if current and text_width(draw, candidate.rstrip(), font) > max_width:
            lines.append(current.rstrip())
            current = token.lstrip()
        else:
            current = candidate
    if current or not lines:
        lines.append(current.rstrip())
    return lines


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in str(text).splitlines() or [""]:
        lines.extend(wrap_line(draw, paragraph, font, max_width))
    return lines


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    fonts: FontBook,
    max_width: int,
    max_height: int,
    max_lines: int,
    start_size: int,
    min_size: int,
    bold: bool,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        font = fonts.get(size, bold=bold)
        lines = wrap_text(draw, text, font, max_width)
        height = line_height(font) * len(lines)
        if len(lines) <= max_lines and height <= max_height:
            return font, lines, line_height(font)
    raise RenderError(f"Text does not fit; shorten it: {text!r}")


def draw_fitted_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fonts: FontBook,
    fill: str,
    max_width: int,
    max_height: int,
    max_lines: int,
    start_size: int,
    min_size: int,
    bold: bool = False,
) -> int:
    font, lines, spacing = fit_text(
        draw, text, fonts, max_width, max_height, max_lines, start_size, min_size, bold
    )
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += spacing
    return y


def normalized_box(rect: Sequence[float], width: int, height: int) -> tuple[int, int, int, int]:
    if len(rect) != 4:
        raise RenderError(f"Expected [x, y, width, height], got: {rect}")
    x, y, w, h = [float(value) for value in rect]
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > 1.0001 or y + h > 1.0001:
        raise RenderError(f"Normalized rectangle is outside the image: {rect}")
    left = max(0, min(width - 1, round(x * width)))
    top = max(0, min(height - 1, round(y * height)))
    right = max(left + 1, min(width, round((x + w) * width)))
    bottom = max(top + 1, min(height, round((y + h) * height)))
    return left, top, right, bottom


def apply_redactions(image: Image.Image, redactions: list[dict[str, Any]], default_color: str) -> Image.Image:
    result = image.copy()
    for item in redactions:
        box = normalized_box(item.get("rect", []), result.width, result.height)
        mode = item.get("mode", "solid")
        if mode == "solid":
            ImageDraw.Draw(result).rectangle(box, fill=color(item.get("color", default_color)))
        elif mode == "blur":
            radius = max(8, int(item.get("radius", 22)))
            region = result.crop(box).filter(ImageFilter.GaussianBlur(radius=radius))
            result.paste(region, box[:2])
        elif mode == "pixelate":
            block = max(6, int(item.get("block_size", 18)))
            region = result.crop(box)
            small = region.resize((max(1, region.width // block), max(1, region.height // block)), Image.Resampling.BILINEAR)
            region = small.resize(region.size, Image.Resampling.NEAREST)
            result.paste(region, box[:2])
        else:
            raise RenderError(f"Unsupported redaction mode: {mode}")
    return result


def load_source(source: dict[str, Any], plan_dir: Path, strict_privacy: bool, theme: dict[str, Any]) -> Image.Image:
    if strict_privacy and source.get("privacy_reviewed") is not True:
        raise RenderError("privacy_reviewed must be true before rendering real chat material")
    path = resolve_path(str(source.get("path", "")), plan_dir)
    if not path.exists():
        raise RenderError(f"Source image does not exist: {path}")
    try:
        image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    except Exception as error:
        raise RenderError(f"Cannot open source image {path}: {error}") from error
    image = apply_redactions(image, source.get("redactions", []), theme["ink"])
    crop = normalized_box(source.get("crop", [0.0, 0.0, 1.0, 1.0]), image.width, image.height)
    return image.crop(crop)


def rounded_image(image: Image.Image, radius: int = 8) -> Image.Image:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width, image.height), radius=radius, fill=255)
    rounded = Image.new("RGB", image.size, "white")
    rounded.paste(image, (0, 0), mask)
    return rounded


def draw_source_panel(canvas: Image.Image, source: Image.Image, box: tuple[int, int, int, int], theme: dict[str, Any]) -> None:
    left, top, right, bottom = box
    max_size = (right - left, bottom - top)
    fitted = ImageOps.contain(source, max_size, method=Image.Resampling.LANCZOS)
    x = left + (max_size[0] - fitted.width) // 2
    y = top + (max_size[1] - fitted.height) // 2

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((x + 10, y + 14, x + fitted.width + 10, y + fitted.height + 14), radius=10, fill=(32, 35, 31, 42))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    canvas.paste(shadow, (0, 0), shadow)

    panel = rounded_image(fitted, radius=8)
    canvas.paste(panel, (x, y))
    ImageDraw.Draw(canvas).rounded_rectangle((x - 2, y - 2, x + fitted.width + 1, y + fitted.height + 1), radius=9, outline=theme["line"], width=3)


def draw_background(draw: ImageDraw.ImageDraw, theme: dict[str, Any], accent: str) -> None:
    draw.rectangle((0, 0, BASE_SIZE[0], BASE_SIZE[1]), fill=theme["background"])
    for y in range(348, 1260, 72):
        draw.line((48, y, 1032, y), fill="#EEE8DD", width=2)
    draw.rectangle((0, 0, 18, BASE_SIZE[1]), fill=accent)
    draw.line((48, 330, 1032, 330), fill=theme["line"], width=3)
    draw.line((48, 1323, 1032, 1323), fill=theme["line"], width=2)


def draw_badges(
    draw: ImageDraw.ImageDraw,
    badges: list[str],
    fonts: FontBook,
    x: int,
    y: int,
    max_width: int,
    theme: dict[str, Any],
    accent: str,
) -> int:
    font = fonts.get(25, bold=True)
    cursor_x, cursor_y = x, y
    row_height = 48
    for badge in badges[:4]:
        label = str(badge)
        width = text_width(draw, label, font) + 30
        if cursor_x + width > x + max_width and cursor_x > x:
            cursor_x = x
            cursor_y += row_height + 10
        draw.rounded_rectangle((cursor_x, cursor_y, cursor_x + width, cursor_y + row_height), radius=6, fill=theme["paper"], outline=accent, width=2)
        draw.text((cursor_x + 15, cursor_y + 9), label, font=font, fill=theme["ink"])
        cursor_x += width + 12
    return cursor_y + row_height


def draw_callouts(
    draw: ImageDraw.ImageDraw,
    callouts: list[dict[str, Any]],
    fonts: FontBook,
    box: tuple[int, int, int, int],
    theme: dict[str, Any],
    accent: str,
) -> None:
    if not callouts:
        return
    if len(callouts) > 4:
        raise RenderError("Use no more than four callouts on one slide")
    left, top, right, bottom = box
    width, height = right - left, bottom - top
    block_height = height // len(callouts)

    for index, item in enumerate(callouts):
        item_top = top + index * block_height
        item_bottom = top + (index + 1) * block_height
        if index:
            draw.line((left, item_top, right, item_top), fill=theme["line"], width=2)
        draw.rectangle((left, item_top + 20, left + 7, item_bottom - 20), fill=accent)
        title = str(item.get("title", "")).strip()
        body = str(item.get("body", "")).strip()
        y = item_top + 24
        if title:
            y = draw_fitted_text(
                draw,
                (left + 24, y),
                title,
                fonts,
                theme["ink"],
                width - 32,
                82,
                2,
                34,
                27,
                bold=True,
            ) + 10
        if body:
            available = max(48, item_bottom - y - 20)
            draw_fitted_text(
                draw,
                (left + 24, y),
                body,
                fonts,
                theme["muted"],
                width - 32,
                available,
                4,
                28,
                22,
            )


def draw_horizontal_callouts(
    draw: ImageDraw.ImageDraw,
    callouts: list[dict[str, Any]],
    fonts: FontBook,
    box: tuple[int, int, int, int],
    theme: dict[str, Any],
    accent: str,
) -> None:
    if not callouts:
        return
    if len(callouts) > 3:
        raise RenderError("chat-full supports at most three callouts")
    left, top, right, bottom = box
    gap = 26
    width = (right - left - gap * (len(callouts) - 1)) // len(callouts)
    for index, item in enumerate(callouts):
        x = left + index * (width + gap)
        draw.rectangle((x, top, x + width, top + 7), fill=accent)
        title = str(item.get("title", "")).strip()
        body = str(item.get("body", "")).strip()
        y = top + 22
        if title:
            y = draw_fitted_text(draw, (x, y), title, fonts, theme["ink"], width, 72, 2, 31, 25, bold=True) + 8
        if body:
            draw_fitted_text(draw, (x, y), body, fonts, theme["muted"], width, bottom - y, 3, 25, 21)


def draw_header(
    draw: ImageDraw.ImageDraw,
    slide: dict[str, Any],
    project: dict[str, Any],
    fonts: FontBook,
    theme: dict[str, Any],
    accent: str,
) -> int:
    eyebrow = str(slide.get("eyebrow") or project.get("series_label") or "真实沟通记录")
    eyebrow_font = fonts.get(25, bold=True)
    eyebrow_width = min(420, text_width(draw, eyebrow, eyebrow_font) + 32)
    draw.rectangle((64, 43, 64 + eyebrow_width, 87), fill=accent)
    draw.text((80, 50), eyebrow, font=eyebrow_font, fill=theme["paper"])

    title = str(slide.get("title", "")).strip()
    if not title:
        raise RenderError("Every slide needs a non-empty title")
    cover = slide.get("layout") == "cover"
    title_y = 103
    title_bottom = draw_fitted_text(
        draw,
        (64, title_y),
        title,
        fonts,
        theme["ink"],
        952,
        180 if cover else 156,
        2,
        86 if cover else 72,
        54 if cover else 48,
        bold=True,
    )
    subtitle = str(slide.get("subtitle", "")).strip()
    if subtitle:
        draw_fitted_text(draw, (66, title_bottom + 6), subtitle, fonts, theme["muted"], 940, 44, 1, 33, 25)
    return 350


def draw_takeaway(
    draw: ImageDraw.ImageDraw,
    takeaway: str,
    fonts: FontBook,
    theme: dict[str, Any],
    accent: str,
) -> None:
    if not takeaway:
        return
    draw.rectangle((64, 1275, 74, 1312), fill=accent)
    draw_fitted_text(draw, (90, 1273), takeaway, fonts, theme["ink"], 920, 42, 1, 27, 22, bold=True)


def draw_footer(
    draw: ImageDraw.ImageDraw,
    project: dict[str, Any],
    index: int,
    total: int,
    fonts: FontBook,
    theme: dict[str, Any],
) -> None:
    footer = str(project.get("footer", "")).strip()
    font = fonts.get(23)
    if footer:
        draw.text((64, 1353), footer, font=font, fill=theme["muted"])
    counter = f"{index:02d} / {total:02d}"
    width = text_width(draw, counter, font)
    draw.text((1016 - width, 1353), counter, font=font, fill=theme["muted"])


def render_slide(
    slide: dict[str, Any],
    index: int,
    total: int,
    project: dict[str, Any],
    privacy: dict[str, Any],
    theme: dict[str, Any],
    fonts: FontBook,
    plan_dir: Path,
) -> Image.Image:
    layout = slide.get("layout")
    if layout not in LAYOUTS:
        raise RenderError(f"Unsupported layout: {layout}")
    source_config = slide.get("source")
    if not isinstance(source_config, dict):
        raise RenderError("Every rendered slide needs a source object")
    source = load_source(source_config, plan_dir, bool(privacy.get("strict", True)), theme)

    accents = [theme["accent"], theme["accent_2"], theme["accent_3"]]
    accent = accents[(index - 1) % len(accents)]
    canvas = Image.new("RGB", BASE_SIZE, theme["background"])
    draw = ImageDraw.Draw(canvas)
    draw_background(draw, theme, accent)
    content_top = draw_header(draw, slide, project, fonts, theme, accent)
    callouts = slide.get("callouts", [])
    badges = slide.get("badges", [])

    if layout in {"cover", "chat-left"}:
        draw_source_panel(canvas, source, (64, content_top, 622, 1252), theme)
        badge_bottom = draw_badges(draw, badges, fonts, 660, content_top, 356, theme, accent) if badges else content_top
        callout_top = badge_bottom + 28 if badges else content_top
        draw_callouts(draw, callouts, fonts, (660, callout_top, 1016, 1252), theme, accent)
    elif layout == "chat-right":
        draw_source_panel(canvas, source, (458, content_top, 1016, 1252), theme)
        badge_bottom = draw_badges(draw, badges, fonts, 64, content_top, 356, theme, accent) if badges else content_top
        callout_top = badge_bottom + 28 if badges else content_top
        draw_callouts(draw, callouts, fonts, (64, callout_top, 420, 1252), theme, accent)
    else:
        source_bottom = 1080 if callouts else 1252
        draw_source_panel(canvas, source, (110, content_top, 970, source_bottom), theme)
        if callouts:
            draw_horizontal_callouts(draw, callouts, fonts, (64, 1104, 1016, 1252), theme, accent)

    draw_takeaway(draw, str(slide.get("takeaway", "")).strip(), fonts, theme, accent)
    draw_footer(draw, project, index, total, fonts, theme)
    return canvas


def validate_storyboard(plan: dict[str, Any]) -> None:
    if plan.get("schema_version") != 1:
        raise RenderError("storyboard.schema_version must be 1")
    if plan.get("canvas", list(BASE_SIZE)) != list(BASE_SIZE):
        raise RenderError("This renderer currently requires canvas [1080, 1440]")
    slides = plan.get("slides")
    if not isinstance(slides, list) or not slides:
        raise RenderError("storyboard.slides must be a non-empty array")
    seen: set[str] = set()
    for index, slide in enumerate(slides, start=1):
        filename = str(slide.get("filename", ""))
        if Path(filename).name != filename or not filename.lower().endswith(".png"):
            raise RenderError(f"Slide {index} has an unsafe or non-PNG filename: {filename}")
        if not re.match(rf"^{index:02d}[-_]", filename):
            raise RenderError(f"Slide {index} filename must start with {index:02d}- or {index:02d}_")
        if filename in seen:
            raise RenderError(f"Duplicate slide filename: {filename}")
        seen.add(filename)


def backup_or_write(path: Path, data: bytes, backup_root: Path) -> bool:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(data)
    if path.exists():
        old = path.read_bytes()
        if hashlib.sha256(old).digest() == hashlib.sha256(data).digest():
            temporary.unlink()
            return False
        backup_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(backup_root / path.name))
    temporary.replace(path)
    return True


def build_overview(slide_paths: list[Path], destination: Path) -> None:
    columns, thumb_width, thumb_height, gap, label_height = 4, 243, 324, 20, 42
    rows = (len(slide_paths) + columns - 1) // columns
    width = gap + columns * (thumb_width + gap)
    height = gap + rows * (thumb_height + label_height + gap)
    canvas = Image.new("RGB", (width, height), "#E9E5DD")
    draw = ImageDraw.Draw(canvas)
    font_path = next((path for path in REGULAR_FONT_CANDIDATES if path.exists()), None)
    font = ImageFont.truetype(str(font_path), 19) if font_path else ImageFont.load_default()
    for index, path in enumerate(slide_paths):
        row, column = divmod(index, columns)
        x = gap + column * (thumb_width + gap)
        y = gap + row * (thumb_height + label_height + gap)
        image = Image.open(path).convert("RGB").resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        canvas.paste(image, (x, y))
        label = path.name if len(path.name) <= 24 else path.name[:21] + "..."
        draw.text((x, y + thumb_height + 9), label, font=font, fill="#292B27")
    canvas.save(destination, quality=91, optimize=True)


def main() -> int:
    args = parse_args()
    storyboard_path = args.storyboard.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    if not storyboard_path.exists():
        print(f"Storyboard does not exist: {storyboard_path}", file=sys.stderr)
        return 2
    try:
        plan = json.loads(storyboard_path.read_text(encoding="utf-8"))
        validate_storyboard(plan)
        theme = dict(DEFAULT_THEME)
        theme.update(plan.get("theme", {}))
        for key in ("background", "paper", "ink", "muted", "accent", "accent_2", "accent_3", "line"):
            theme[key] = color(theme[key])
        fonts = FontBook(theme, storyboard_path.parent)
        project = plan.get("project", {})
        privacy = plan.get("privacy", {"strict": True})
        slides = plan["slides"]

        output_dir.mkdir(parents=True, exist_ok=True)
        backup_root = output_dir / "_备份" / datetime.now().strftime("%Y%m%d-%H%M%S")
        payloads: list[tuple[Path, bytes]] = []
        for index, slide in enumerate(slides, start=1):
            image = render_slide(slide, index, len(slides), project, privacy, theme, fonts, storyboard_path.parent)
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            destination = output_dir / slide["filename"]
            payloads.append((destination, buffer.getvalue()))
            print(f"Prepared {index:02d}/{len(slides):02d}: {destination.name}")

        # Render every slide successfully before changing the existing package.
        rendered_paths: list[Path] = []
        changed = 0
        for destination, data in payloads:
            changed += int(backup_or_write(destination, data, backup_root))
            rendered_paths.append(destination)

        build_overview(rendered_paths, output_dir / "轮播总览.jpg")
        if backup_root.exists() and not any(backup_root.iterdir()):
            backup_root.rmdir()
        print(f"Completed {len(rendered_paths)} slide(s); {changed} file(s) changed.")
        print(f"Overview: {output_dir / '轮播总览.jpg'}")
        return 0
    except (json.JSONDecodeError, RenderError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
