#!/usr/bin/env python3
"""Draw auditable blind-box palette seeds using only the Python standard library."""

from __future__ import annotations

import argparse
import colorsys
import json
import random
import secrets


MOODS = ["清醒", "松弛", "冒险", "温柔", "未来", "复古", "活力", "静谧", "俏皮", "沉稳", "梦游", "自然"]
SETTINGS = ["晨雾", "午夜街区", "海风", "山野", "工作室", "宇宙站", "旧书房", "运动场", "甜品铺", "雨后", "音乐节", "远行"]
HARMONIES = ["analogous", "complementary", "split-complementary", "triadic"]


def hex_color(hue: float, saturation: float, lightness: float) -> str:
    red, green, blue = colorsys.hls_to_rgb((hue % 360) / 360, lightness, saturation)
    return f"#{round(red * 255):02X}{round(green * 255):02X}{round(blue * 255):02X}"


def draw_palette(rng: random.Random, hue: float, harmony: str) -> dict[str, str]:
    offsets = {
        "analogous": ([28, 48], [150, 185]),
        "complementary": ([165, 195], [145, 215]),
        "split-complementary": ([145, 215], [165, 230]),
        "triadic": ([110, 130], [225, 250]),
    }
    base_offsets, accent_offsets = offsets[harmony]
    dark = rng.random() < 0.3
    if dark:
        background = hex_color(hue, rng.uniform(0.38, 0.68), rng.uniform(0.14, 0.25))
        line = hex_color(hue + 165 + rng.uniform(-18, 18), rng.uniform(0.35, 0.65), rng.uniform(0.78, 0.9))
    else:
        background = hex_color(hue, rng.uniform(0.42, 0.72), rng.uniform(0.72, 0.88))
        line = hex_color(hue + 170 + rng.uniform(-20, 20), rng.uniform(0.45, 0.78), rng.uniform(0.16, 0.3))
    base = hex_color(hue + rng.choice(base_offsets), rng.uniform(0.45, 0.78), rng.uniform(0.42, 0.64))
    accent = hex_color(hue + rng.choice(accent_offsets), rng.uniform(0.68, 0.92), rng.uniform(0.5, 0.68))
    return {"background": background, "line": line, "base": base, "accent": accent}


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw random personal-IP theme seeds.")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--user-theme", action="append", default=[])
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.count < 0:
        parser.error("--count cannot be negative")

    seed = args.seed if args.seed is not None else secrets.randbits(64)
    rng = random.Random(seed)
    offset = rng.uniform(0, 360)
    hues = [] if args.count == 0 else [
        (offset + index * 360 / args.count + rng.uniform(-12, 12)) % 360
        for index in range(args.count)
    ]
    rng.shuffle(hues)
    names: set[str] = set()
    random_themes = []
    for index, hue in enumerate(hues, start=1):
        while True:
            name = f"{rng.choice(MOODS)}·{rng.choice(SETTINGS)}"
            if name not in names:
                names.add(name)
                break
        harmony = rng.choice(HARMONIES)
        random_themes.append({
            "index": index,
            "source": "blind-box-random",
            "name_seed": name,
            "hue_anchor": round(hue, 1),
            "harmony": harmony,
            "palette": draw_palette(rng, hue, harmony),
        })

    user_themes = [
        {"index": args.count + index, "source": "user-appended", "request": value}
        for index, value in enumerate(args.user_theme, start=1)
    ]
    print(json.dumps({
        "seed": seed,
        "random_theme_count": len(random_themes),
        "user_theme_count": len(user_themes),
        "random_themes": random_themes,
        "user_themes": user_themes,
        "total_expansion_themes": len(random_themes) + len(user_themes),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
