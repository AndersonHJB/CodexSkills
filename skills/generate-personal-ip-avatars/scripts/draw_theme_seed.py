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
LIGHT_MOODS = ["轻盈", "清甜", "柔和", "晴朗", "奶油", "空气感", "春日", "微光"]
LIGHT_SETTINGS = ["云朵", "汽水", "花园", "晨光", "海盐", "纸鸢", "柠檬糖", "薄荷窗"]


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


def draw_light_palette(rng: random.Random, hue: float, harmony: str) -> dict[str, str]:
    """Draw a genuinely light palette while retaining readable line contrast."""
    offsets = {
        "analogous": (rng.choice([24, 42]), rng.choice([145, 185])),
        "complementary": (rng.choice([165, 195]), rng.choice([150, 210])),
        "split-complementary": (rng.choice([145, 215]), rng.choice([165, 225])),
        "triadic": (rng.choice([110, 130]), rng.choice([225, 250])),
    }
    base_offset, accent_offset = offsets[harmony]
    return {
        "background": hex_color(hue, rng.uniform(0.22, 0.45), rng.uniform(0.88, 0.95)),
        "line": hex_color(hue + 170 + rng.uniform(-16, 16), rng.uniform(0.38, 0.62), rng.uniform(0.24, 0.36)),
        "base": hex_color(hue + base_offset, rng.uniform(0.28, 0.52), rng.uniform(0.72, 0.84)),
        "accent": hex_color(hue + accent_offset, rng.uniform(0.48, 0.72), rng.uniform(0.64, 0.76)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Draw random personal-IP theme seeds.")
    parser.add_argument("--count", type=int, default=8)
    parser.add_argument("--light-count", type=int, default=2)
    parser.add_argument("--user-theme", action="append", default=[])
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    if args.count < 0 or args.light_count < 0:
        parser.error("theme counts cannot be negative")

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

    light_offset = rng.uniform(0, 360)
    light_hues = [] if args.light_count == 0 else [
        (light_offset + index * 360 / args.light_count + rng.uniform(-16, 16)) % 360
        for index in range(args.light_count)
    ]
    rng.shuffle(light_hues)
    light_themes = []
    for index, hue in enumerate(light_hues, start=1):
        while True:
            name = f"{rng.choice(LIGHT_MOODS)}·{rng.choice(LIGHT_SETTINGS)}"
            if name not in names:
                names.add(name)
                break
        harmony = rng.choice(HARMONIES)
        light_themes.append({
            "index": args.count + index,
            "source": "blind-box-light",
            "name_seed": name,
            "hue_anchor": round(hue, 1),
            "harmony": harmony,
            "value_direction": "light",
            "palette": draw_light_palette(rng, hue, harmony),
        })

    user_themes = [
        {"index": args.count + args.light_count + index, "source": "user-appended", "request": value}
        for index, value in enumerate(args.user_theme, start=1)
    ]
    print(json.dumps({
        "seed": seed,
        "random_theme_count": len(random_themes),
        "light_theme_count": len(light_themes),
        "user_theme_count": len(user_themes),
        "random_themes": random_themes,
        "light_themes": light_themes,
        "user_themes": user_themes,
        "total_expansion_themes": len(random_themes) + len(light_themes) + len(user_themes),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
