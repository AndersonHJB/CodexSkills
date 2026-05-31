#!/usr/bin/env python3
"""Compose a WeChat cover image from a no-text background and exact title text."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:
    raise SystemExit(
        "Pillow is required. Run with: uv run --with pillow python generate_wechat_cover.py ..."
    ) from exc


DEFAULT_CN_FONT = "/System/Library/Fonts/STHeiti Medium.ttc"
DEFAULT_CN_LIGHT_FONT = "/System/Library/Fonts/STHeiti Light.ttc"
DEFAULT_EN_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def cover_crop(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    new_size = (int(image.width * scale + 0.5), int(image.height * scale + 0.5))
    image = image.resize(new_size, Image.Resampling.LANCZOS)
    left = (image.width - width) // 2
    top = (image.height - height) // 2
    return image.crop((left, top, left + width, top + height))


def rounded_layer(size: tuple[int, int], xy, radius: int, fill, outline=None, width: int = 1) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    return layer


def compose(
    background: Path,
    output: Path,
    title: str,
    subtitle: str,
    tag: str,
    footer: str,
    chips: list[str],
    width: int,
    height: int,
    cn_font: str,
    cn_light_font: str,
    en_font: str,
) -> None:
    img = Image.open(background).convert("RGB")
    img = cover_crop(img, width, height).convert("RGBA")

    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(width):
        t = x / (width - 1)
        alpha = int(20 + max(0, (t - 0.40) / 0.60) * 185)
        draw.line([(x, 0), (x, height)], fill=(5, 14, 20, alpha))
    for y in range(height):
        t = y / (height - 1)
        alpha = int(max(0, (t - 0.58) / 0.42) * 80)
        if alpha:
            draw.line([(0, y), (width, y)], fill=(5, 14, 20, alpha))
    img = Image.alpha_composite(img, overlay)

    panel_x = int(width * 0.54)
    panel_y = int(height * 0.15)
    panel_w = int(width * 0.39)
    panel_h = int(height * 0.64)
    panel = rounded_layer(
        (width, height),
        (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h),
        30,
        (5, 17, 25, 170),
        (68, 123, 128, 54),
        2,
    ).filter(ImageFilter.GaussianBlur(0.2))
    img = Image.alpha_composite(img, panel)

    draw = ImageDraw.Draw(img)
    title_x = panel_x + 32
    badge_w = max(116, len(tag) * 22 + 28)
    badge = rounded_layer((width, height), (title_x, panel_y + 34, title_x + badge_w, panel_y + 68), 17, (15, 139, 141, 235))
    img = Image.alpha_composite(img, badge)
    draw = ImageDraw.Draw(img)
    draw.text((title_x + badge_w / 2, panel_y + 51), tag, anchor="mm", font=load_font(cn_font, 18), fill=(234, 255, 251, 255))

    # Split title into at most two lines. ASCII-heavy first line uses EN font.
    title_lines = title.split("|") if "|" in title else [title]
    y = panel_y + 104
    for idx, line in enumerate(title_lines[:2]):
        ascii_ratio = sum(ch.isascii() for ch in line) / max(1, len(line))
        font_path = en_font if ascii_ratio > 0.55 else cn_font
        size = 56 if idx == 0 else 62
        fill = (255, 255, 255, 255) if idx == 0 else (255, 197, 102, 255)
        draw.text((title_x, y), line, font=load_font(font_path, size), fill=fill)
        y += 70

    draw.rounded_rectangle((title_x, y + 4, title_x + int(panel_w * 0.82), y + 8), radius=2, fill=(246, 162, 58, 255))
    draw.text((title_x, y + 56), subtitle, font=load_font(cn_font, 30), fill=(216, 244, 241, 255))

    chip_y = y + 96
    chip_x = title_x
    chip_colors = [(15, 139, 141), (246, 162, 58), (38, 54, 66)]
    for idx, chip in enumerate(chips[:3]):
        chip_w = max(110, len(chip) * 23 + 28)
        color = chip_colors[idx % len(chip_colors)]
        chip_layer = rounded_layer((width, height), (chip_x, chip_y, chip_x + chip_w, chip_y + 38), 19, (*color, 235))
        img = Image.alpha_composite(img, chip_layer)
        draw = ImageDraw.Draw(img)
        fill = (19, 32, 39, 255) if color == (246, 162, 58) else (255, 255, 255, 255)
        draw.text((chip_x + chip_w / 2, chip_y + 19), chip, anchor="mm", font=load_font(cn_font, 20), fill=fill)
        chip_x += chip_w + 16

    draw.text((34, height - 34), footer, font=load_font(cn_light_font, 21), fill=(184, 205, 210, 255))
    output.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output, quality=95)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--background", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--title", required=True, help="Use | to force a line break, e.g. 'Claude Code|记忆系统实战'")
    parser.add_argument("--subtitle", required=True)
    parser.add_argument("--tag", default="公众号文章")
    parser.add_argument("--footer", default="AI悦创 · 公众号文章")
    parser.add_argument("--chips", default="", help="Comma-separated chips, e.g. 项目记忆,规则目录,自动记忆")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=544)
    parser.add_argument("--cn-font", default=DEFAULT_CN_FONT)
    parser.add_argument("--cn-light-font", default=DEFAULT_CN_LIGHT_FONT)
    parser.add_argument("--en-font", default=DEFAULT_EN_FONT)
    args = parser.parse_args()

    chips = [part.strip() for part in args.chips.split(",") if part.strip()]
    compose(
        args.background.expanduser().resolve(),
        args.output.expanduser().resolve(),
        args.title,
        args.subtitle,
        args.tag,
        args.footer,
        chips,
        args.width,
        args.height,
        args.cn_font,
        args.cn_light_font,
        args.en_font,
    )
    print(args.output.expanduser().resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
