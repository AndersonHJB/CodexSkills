#!/usr/bin/env python3
"""Calculate series and image counts for the personal-IP feature switches."""

from __future__ import annotations

import argparse
import json


def enabled(value: str) -> int:
    return 1 if value == "on" else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Calculate a personal-IP generation plan.")
    parser.add_argument("--classic", choices=("on", "off"), default="on")
    parser.add_argument("--random-count", type=int, default=8)
    parser.add_argument("--light-count", type=int, default=2)
    parser.add_argument("--user-theme-count", type=int, default=0)
    parser.add_argument("--base-designs", choices=("on", "off"), default="on")
    parser.add_argument("--front-full-body", choices=("on", "off"), default="on")
    parser.add_argument("--angle-views", choices=("on", "off"), default="on")
    parser.add_argument("--emotion-pack", choices=("on", "off"), default="on")
    parser.add_argument("--existing-classic", action="store_true")
    args = parser.parse_args()

    if args.random_count < 0 or args.light_count < 0 or args.user_theme_count < 0:
        parser.error("theme counts cannot be negative")

    series_count = enabled(args.classic) + args.random_count + args.light_count + args.user_theme_count
    per_series = (
        8 * enabled(args.base_designs)
        + enabled(args.front_full_body)
        + 8 * enabled(args.angle_views)
        + 24 * enabled(args.emotion_pack)
    )
    if series_count == 0:
        parser.error("at least one series must be enabled")
    if per_series == 0:
        parser.error("at least one image-generation module must be enabled")

    delivered = series_count * per_series
    existing_count = 0
    if args.existing_classic and args.classic == "on" and args.base_designs == "on":
        existing_count = 8

    result = {
        "series_count": series_count,
        "series_counts": {
            "classic": enabled(args.classic),
            "random": args.random_count,
            "light": args.light_count,
            "user_appended": args.user_theme_count,
        },
        "per_series_originals": per_series,
        "delivered_originals": delivered,
        "existing_immutable_originals": existing_count,
        "new_generation_count": delivered - existing_count,
        "module_counts_per_series": {
            "base_designs": 8 * enabled(args.base_designs),
            "front_full_body": enabled(args.front_full_body),
            "angle_views": 8 * enabled(args.angle_views),
            "emotion_pack": 24 * enabled(args.emotion_pack),
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
