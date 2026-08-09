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
    parser.add_argument("--brand-theme-count", type=int, default=0)
    parser.add_argument("--industry-full-body-pack", choices=("on", "off"), default="on")
    parser.add_argument("--industry-count", type=int, default=8)
    parser.add_argument("--base-designs", choices=("on", "off"), default="on")
    parser.add_argument("--front-full-body", choices=("on", "off"), default="on")
    parser.add_argument("--angle-views", choices=("on", "off"), default="on")
    parser.add_argument("--emotion-pack", choices=("on", "off"), default="on")
    parser.add_argument("--existing-classic", action="store_true")
    parser.add_argument("--existing-original-count", type=int, default=0)
    args = parser.parse_args()

    if any(value < 0 for value in (
        args.random_count,
        args.light_count,
        args.user_theme_count,
        args.brand_theme_count,
        args.industry_count,
        args.existing_original_count,
    )):
        parser.error("theme counts cannot be negative")

    series_count = (
        enabled(args.classic)
        + args.random_count
        + args.light_count
        + args.user_theme_count
        + args.brand_theme_count
    )
    per_series = (
        8 * enabled(args.base_designs)
        + enabled(args.front_full_body)
        + 8 * enabled(args.angle_views)
        + 24 * enabled(args.emotion_pack)
    )
    industry_originals = args.industry_count * enabled(args.industry_full_body_pack)
    if series_count == 0 and industry_originals == 0:
        parser.error("at least one series or the industry full-body pack must be enabled")
    if series_count > 0 and per_series == 0 and industry_originals == 0:
        parser.error("at least one image-generation module must be enabled")
    delivered = series_count * per_series + industry_originals
    existing_count = args.existing_original_count
    if existing_count == 0 and args.existing_classic and args.classic == "on" and args.base_designs == "on":
        existing_count = 8
    if existing_count > delivered:
        parser.error("existing original count cannot exceed delivered originals")

    result = {
        "series_count": series_count,
        "series_counts": {
            "classic": enabled(args.classic),
            "random": args.random_count,
            "light": args.light_count,
            "user_appended": args.user_theme_count,
            "brand_or_institution": args.brand_theme_count,
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
        "standalone_module_counts": {
            "industry_full_body_pack": industry_originals,
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
