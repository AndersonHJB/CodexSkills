#!/usr/bin/env python3
"""Deterministic intake, rendering, validation, and packaging for WeChat sticker packs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
import zipfile
from datetime import date
from pathlib import Path
from typing import Any, Iterable

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps, __version__ as PILLOW_VERSION
except ImportError as exc:  # pragma: no cover - environment error
    raise SystemExit(
        "Pillow is required. Load the Codex workspace dependencies or install Pillow in the active Python environment."
    ) from exc


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = SKILL_DIR / "assets" / "creator-profile.json"
EXPECTED_IDS = [f"{i:02d}" for i in range(1, 21)]
HAN_RE = re.compile(r"^[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]+$")
MEANING_RE = re.compile(r"^[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]{1,4}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MANUAL_REVIEW_KEYS = [
    "banner_has_no_text_or_numbers",
    "source_art_has_no_gibberish",
    "character_consistent",
    "text_visually_correct",
    "publication_assets_visually_clean",
    "rights_reviewed",
]
RULES_STATUS_VALUES = {"official-current", "changed-unsupported", "snapshot-unverified"}
ALLOWED_FRAMINGS = {"close_up", "bust", "half_body", "full_body"}
ASSET_PROMPT_KEYS = {"banner_prompt", "cover_prompt", "icon_prompt"}
BUILTIN_GENERATED_KINDS = {"anchor", "sticker", "banner", "cover-chroma", "icon-chroma"}
LOCAL_DERIVED_KINDS = {"cover", "icon"}
FULL_ARCHIVE_PRIVACY_WARNING = (
    "Full archive preserves original reference bytes and may retain EXIF/GPS metadata; "
    "share only the submission archive unless archival disclosure is intended."
)
RESAMPLE = getattr(Image, "Resampling", Image).LANCZOS


class PackError(RuntimeError):
    pass


def canonical_json_bytes(data: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2)
    else:
        text = json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return (text + "\n").encode("utf-8")


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temp_path, mode)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def write_json(path: Path, data: Any, *, pretty: bool = True) -> None:
    atomic_write(path, canonical_json_bytes(data, pretty=pretty))


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PackError(f"Cannot read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise PackError(f"JSON root must be an object: {path}")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_regular_input(path: Path) -> Path:
    path = path.expanduser()
    if not path.exists():
        raise PackError(f"Input does not exist: {path}")
    if path.is_symlink() or not path.is_file():
        raise PackError(f"Input must be a regular non-symlink file: {path}")
    return path.resolve()


def inspect_image_file(path: Path, *, min_side: int = 1, max_pixels: int = 64_000_000) -> dict[str, Any]:
    try:
        with Image.open(path) as image:
            width, height = image.size
            if width < min_side or height < min_side:
                raise PackError(f"Image is smaller than {min_side}px on one side: {path}")
            if width * height > max_pixels:
                raise PackError(f"Image exceeds the {max_pixels:,}-pixel safety limit: {path}")
            image.load()
            return {
                "format": image.format,
                "width": width,
                "height": height,
                "mode": image.mode,
                "exif_orientation": image.getexif().get(274),
            }
    except PackError:
        raise
    except Exception as exc:
        raise PackError(f"Unreadable or truncated image: {path}: {exc}") from exc


def safe_relative_path(root: Path, relative: str) -> Path:
    candidate_relative = Path(relative)
    if candidate_relative.is_absolute() or ".." in candidate_relative.parts:
        raise PackError(f"Unsafe relative path in state: {relative!r}")
    root_resolved = root.resolve()
    candidate = (root / candidate_relative).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise PackError(f"Path escapes run directory: {relative!r}") from exc
    return candidate


def copy_bytes_preserving_content(src: Path, dst: Path, *, read_only: bool = True) -> dict[str, Any]:
    src = ensure_regular_input(src)
    if dst.exists():
        raise PackError(f"Refusing to overwrite existing file: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    source_hash = sha256_file(src)
    source_size = src.stat().st_size
    fd, temp_name = tempfile.mkstemp(prefix=f".{dst.name}.", dir=str(dst.parent))
    temp_path = Path(temp_name)
    try:
        with src.open("rb") as source, os.fdopen(fd, "wb") as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)
            target.flush()
            os.fsync(target.fileno())
        if temp_path.stat().st_size != source_size or sha256_file(temp_path) != source_hash:
            raise PackError(f"Copy verification failed: {src}")
        os.chmod(temp_path, 0o444 if read_only else 0o644)
        os.replace(temp_path, dst)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return {"sha256": source_hash, "size": source_size}


def codepoint_count(value: str) -> int:
    return len(value)


def normalized_surface(text: str) -> str:
    value = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in value if not ch.isspace() and not unicodedata.category(ch).startswith("P"))


def normalized_stem(text: str) -> str:
    surface = normalized_surface(text)
    collapsed = re.sub(r"(.)\1+", r"\1", surface)
    return re.sub(r"[呀啊哦啦呢嘛哇诶耶吧哈]+$", "", collapsed) or collapsed


def visible_text_length(text: str) -> int:
    return sum(1 for ch in text if not ch.isspace())


def validate_visible_text(text: str) -> str | None:
    if "\n" in text or "\r" in text:
        return "exact_text must not contain line breaks; use line_break"
    for ch in text:
        category = unicodedata.category(ch)
        if category in {"Cc", "Cf", "Cs"}:
            return f"exact_text contains forbidden invisible/control character U+{ord(ch):04X}"
    length = visible_text_length(text)
    if not (1 <= length <= 12):
        return "exact_text must contain 1-12 visible glyphs"
    punctuation_count = sum(1 for ch in text if unicodedata.category(ch).startswith("P"))
    if punctuation_count > 3:
        return "exact_text must contain at most three punctuation glyphs"
    if re.search(r"https?://|www\.|[@#]", text, flags=re.IGNORECASE):
        return "exact_text must not contain URLs, account markers, or hashtags"
    if re.search(r"\d{1,4}[-/.年]\d{1,2}", text):
        return "exact_text must not contain dates"
    if any(unicodedata.category(ch) == "So" for ch in text):
        return "exact_text must not contain emoji or other-symbol glyphs"
    return None


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if spec.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if not isinstance(spec.get("platform_spec"), str) or not spec.get("platform_spec", "").strip():
        errors.append("platform_spec is required")
    rules_status = spec.get("rules_status")
    if rules_status not in RULES_STATUS_VALUES:
        errors.append("rules_status must be official-current, changed-unsupported, or snapshot-unverified")
    checked = spec.get("rules_checked_at")
    if not isinstance(checked, str):
        errors.append("rules_checked_at must be a real YYYY-MM-DD date")
    else:
        try:
            parsed = date.fromisoformat(checked)
            if parsed > date.today():
                errors.append("rules_checked_at must not be in the future")
        except ValueError:
            errors.append("rules_checked_at must be a real YYYY-MM-DD date")
    if rules_status == "changed-unsupported":
        details = spec.get("rules_change_details")
        if not isinstance(details, list) or not details or not all(
            isinstance(value, str) and value.strip() for value in details
        ):
            errors.append("rules_change_details must record every unsupported official change")

    pack = spec.get("pack")
    if not isinstance(pack, dict):
        return errors + ["pack must be an object"]

    slug = pack.get("slug", "")
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        errors.append("pack.slug must use lowercase ASCII letters, digits, and hyphens")

    name = pack.get("name", "")
    if not isinstance(name, str) or not (1 <= len(name) <= 8) or not HAN_RE.fullmatch(name):
        errors.append("pack.name must contain 1-8 Han characters only")

    introduction = pack.get("introduction", "")
    if not isinstance(introduction, str) or not (1 <= codepoint_count(introduction) <= 80):
        errors.append("pack.introduction must contain 1-80 characters")

    copyright_value = pack.get("copyright", "")
    if (
        not isinstance(copyright_value, str)
        or not (1 <= codepoint_count(copyright_value) <= 10)
        or any(ch.isspace() for ch in copyright_value)
    ):
        errors.append("pack.copyright must contain 1-10 non-space characters")

    if pack.get("ai_generated") is not True:
        errors.append("pack.ai_generated must be true")
    if not isinstance(pack.get("rights_confirmed"), bool):
        errors.append("pack.rights_confirmed must be boolean")
    if not isinstance(pack.get("portrait_use_confirmed"), bool):
        errors.append("pack.portrait_use_confirmed must be boolean")
    required_pack_strings = {
        "type": {"静态表情"},
        "category": {"卡通表情/其他", "真人拍摄表情", "截图表情"},
        "theme": None,
        "download_region": {"全球", "中国大陆"},
        "listing_region": {"中国大陆"},
        "price": {"免费", "10微信豆", "10 微信豆"},
    }
    for field, allowed in required_pack_strings.items():
        value = pack.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"pack.{field} is required")
        elif allowed is not None and value not in allowed:
            errors.append(f"pack.{field} has an unsupported value")
    character = pack.get("character")
    if not isinstance(character, list) or len(character) != 2 or not all(
        isinstance(value, str) and value.strip() for value in character
    ):
        errors.append("pack.character must contain exactly two non-empty selection labels")
    styles = pack.get("styles")
    if not isinstance(styles, list) or not (1 <= len(styles) <= 2) or not all(
        isinstance(value, str) and value.strip() for value in styles
    ):
        errors.append("pack.styles must contain one or two non-empty labels")

    for bible_name in ("character_bible", "style_bible"):
        value = spec.get(bible_name)
        if not isinstance(value, dict) or not value:
            errors.append(f"{bible_name} must be a non-empty object")
    avoid = spec.get("avoid")
    if not isinstance(avoid, list) or not avoid or not all(
        isinstance(value, str) and value.strip() for value in avoid
    ):
        errors.append("avoid must be a non-empty string list")
    if not isinstance(spec.get("anchor_prompt"), str) or not spec.get("anchor_prompt", "").strip():
        errors.append("anchor_prompt is required")
    assets = spec.get("assets")
    if not isinstance(assets, dict):
        errors.append("assets must be an object")
    else:
        for key in ASSET_PROMPT_KEYS:
            if not isinstance(assets.get(key), str) or not assets.get(key, "").strip():
                errors.append(f"assets.{key} is required")

    render = spec.get("render")
    if not isinstance(render, dict):
        errors.append("render must be an object")
    else:
        background = render.get("background")
        if not isinstance(background, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", background):
            errors.append("render.background must be a six-digit hex color")
        master_size = render.get("master_size")
        if not isinstance(master_size, int) or isinstance(master_size, bool) or not (480 <= master_size <= 4096):
            errors.append("render.master_size must be an integer from 480 to 4096")
        default_text = render.get("default_text")
        if not isinstance(default_text, dict):
            errors.append("render.default_text must be an object")
        else:
            for key, minimum, maximum in (
                ("min_font_size", 8, 120),
                ("max_font_size", 8, 160),
                ("max_lines", 1, 2),
                ("stroke_width", 0, 12),
            ):
                value = default_text.get(key)
                if not isinstance(value, int) or isinstance(value, bool) or not (minimum <= value <= maximum):
                    errors.append(f"render.default_text.{key} must be an integer from {minimum} to {maximum}")
            if isinstance(default_text.get("min_font_size"), int) and isinstance(
                default_text.get("max_font_size"), int
            ) and default_text["min_font_size"] > default_text["max_font_size"]:
                errors.append("render.default_text.min_font_size must not exceed max_font_size")
            for key in ("fill", "stroke_fill"):
                if not isinstance(default_text.get(key), str) or not re.fullmatch(
                    r"#[0-9A-Fa-f]{6}", default_text.get(key, "")
                ):
                    errors.append(f"render.default_text.{key} must be a six-digit hex color")

    stickers = spec.get("stickers")
    if not isinstance(stickers, list) or len(stickers) != 20:
        return errors + ["stickers must contain exactly 20 items"]

    ids: list[str] = []
    texts: list[str] = []
    surfaces: list[str] = []
    stems: list[str] = []
    meanings: list[str] = []
    intents: list[str] = []
    combinations: list[tuple[str, str, str, str]] = []
    framings: list[str] = []
    categories: list[str] = []
    prop_count = 0
    final_particles: dict[str, int] = {}
    for index, item in enumerate(stickers, 1):
        prefix = f"stickers[{index - 1}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix} must be an object")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str):
            errors.append(f"{prefix}.id must be a string")
        else:
            ids.append(item_id)
        text = item.get("exact_text")
        if not isinstance(text, str):
            errors.append(f"{prefix}.exact_text must be a string")
        else:
            text_error = validate_visible_text(text)
            if text_error:
                errors.append(f"{prefix}.{text_error}")
            else:
                texts.append(text)
                surfaces.append(normalized_surface(text))
                stems.append(normalized_stem(text))
                normalized = normalized_surface(text)
                if normalized and normalized[-1] in "呀啊哦啦呢嘛哇诶耶吧哈":
                    final_particles[normalized[-1]] = final_particles.get(normalized[-1], 0) + 1
        meaning = item.get("meaning_word")
        if not isinstance(meaning, str) or not MEANING_RE.fullmatch(meaning):
            errors.append(f"{prefix}.meaning_word must contain 1-4 Han characters")
        else:
            meanings.append(meaning)
        intent = item.get("intent_key")
        if not isinstance(intent, str) or not intent.strip():
            errors.append(f"{prefix}.intent_key is required")
        else:
            intents.append(intent)
        category = item.get("category")
        if not isinstance(category, str) or not category.strip():
            errors.append(f"{prefix}.category is required")
            category_value = ""
        else:
            category_value = category.strip()
            categories.append(category_value)
        emotion = item.get("emotion")
        if not isinstance(emotion, str) or not emotion.strip():
            errors.append(f"{prefix}.emotion is required")
            emotion_value = ""
        else:
            emotion_value = emotion.strip()
        pose = item.get("pose_action")
        if not isinstance(pose, str) or not pose.strip():
            errors.append(f"{prefix}.pose_action is required")
            pose_value = ""
        else:
            pose_value = pose.strip()
        prop = item.get("prop")
        if prop is not None and (not isinstance(prop, str) or not prop.strip()):
            errors.append(f"{prefix}.prop must be null or a non-empty string")
            prop_value = ""
        else:
            prop_value = "" if prop is None else prop.strip()
            if prop_value:
                prop_count += 1
        framing = item.get("framing")
        if framing not in ALLOWED_FRAMINGS:
            errors.append(f"{prefix}.framing must be one of {sorted(ALLOWED_FRAMINGS)}")
            framing_value = ""
        else:
            framing_value = framing
            framings.append(framing)
        if item.get("text_zone") not in {"top", "bottom"}:
            errors.append(f"{prefix}.text_zone must be top or bottom")
        if not isinstance(item.get("art_prompt"), str) or not item.get("art_prompt", "").strip():
            errors.append(f"{prefix}.art_prompt is required")
        line_break = item.get("line_break")
        if line_break is not None:
            if isinstance(line_break, list):
                lines = [str(value) for value in line_break]
            elif isinstance(line_break, str):
                lines = line_break.split("\n")
            else:
                lines = []
                errors.append(f"{prefix}.line_break must be null, a string, or a string list")
            if lines and (len(lines) > 2 or "".join(lines) != str(text)):
                errors.append(f"{prefix}.line_break must use at most two lines and reconstruct exact_text")
        combinations.append((emotion_value, pose_value, prop_value, framing_value))

    if ids != EXPECTED_IDS:
        errors.append("sticker IDs must be ordered exactly 01 through 20")
    for label, values in [
        ("exact_text", texts),
        ("normalized exact_text", surfaces),
        ("normalized text stem", stems),
        ("meaning_word", meanings),
        ("intent_key", intents),
    ]:
        if len(values) != len(set(values)):
            errors.append(f"{label} values must be unique")
    if len(combinations) != len(set(combinations)):
        errors.append("emotion + pose_action + prop + framing combinations must be unique")
    if len(set(framings)) < 3:
        errors.append("the plan must use at least three framing types")
    if len(set(categories)) < 3:
        errors.append("the plan must use at least three communication categories")
    if not (4 <= prop_count <= 7):
        errors.append("the plan must use props in 4-7 stickers")
    for particle, count in sorted(final_particles.items()):
        if count > 3:
            errors.append(f"sentence-final particle {particle!r} is used more than three times")

    manual = spec.get("manual_review")
    if not isinstance(manual, dict):
        errors.append("manual_review must be an object")
    else:
        for key in MANUAL_REVIEW_KEYS:
            if not isinstance(manual.get(key), bool):
                errors.append(f"manual_review.{key} must be boolean")
    return errors


def merge_profile_defaults(spec: dict[str, Any], profile: dict[str, Any]) -> dict[str, Any]:
    spec = json.loads(json.dumps(spec, ensure_ascii=False))
    pack = spec.setdefault("pack", {})
    mappings = {
        "copyright": "copyright_holder",
        "download_region": "default_download_region",
        "price": "default_price",
        "category": "default_category",
        "styles": "default_styles",
        "theme": "default_theme",
    }
    for pack_key, profile_key in mappings.items():
        if not pack.get(pack_key) and profile.get(profile_key) is not None:
            pack[pack_key] = profile[profile_key]
    pack["ai_generated"] = True
    return spec


def run_paths(run_dir: Path) -> dict[str, Path]:
    return {
        "run": run_dir,
        "originals": run_dir / "00-reference-originals",
        "plan": run_dir / "01-plan",
        "source": run_dir / "02-source-assets",
        "raw_stickers": run_dir / "02-source-assets" / "generated-raw" / "stickers",
        "raw_assets": run_dir / "02-source-assets" / "generated-raw" / "assets",
        "masters": run_dir / "02-source-assets" / "generated-masters",
        "provenance": run_dir / "02-source-assets" / "provenance",
        "submission": run_dir / "03-submission",
        "submission_stickers": run_dir / "03-submission" / "stickers",
        "submission_assets": run_dir / "03-submission" / "assets",
        "metadata": run_dir / "03-submission" / "metadata",
        "qa": run_dir / "03-submission" / "qa",
        "preview": run_dir / "04-preview",
        "archives": run_dir / "archives",
        "state": run_dir / "state.json",
        "spec": run_dir / "01-plan" / "pack.json",
    }


def initialize_run(args: argparse.Namespace) -> None:
    run_dir = args.run_dir.expanduser().resolve()
    if run_dir.exists():
        raise PackError(f"Run directory already exists: {run_dir}")
    spec_source = ensure_regular_input(args.spec)
    profile_source = ensure_regular_input(args.profile or DEFAULT_PROFILE)
    references = [ensure_regular_input(path) for path in args.reference]
    if not references:
        raise PackError("At least one --reference is required")
    for reference in references:
        try:
            reference.relative_to(run_dir)
            raise PackError("Reference files must not be inside the new run directory")
        except ValueError:
            pass

    spec = merge_profile_defaults(load_json(spec_source), load_json(profile_source))
    errors = validate_spec(spec)
    if errors:
        raise PackError("Invalid pack spec:\n- " + "\n- ".join(errors))

    run_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{run_dir.name}.init-", dir=str(run_dir.parent)))
    paths = run_paths(temp_dir)
    try:
        for key, path in paths.items():
            if key not in {"run", "state", "spec"}:
                path.mkdir(parents=True, exist_ok=True)
        originals: list[dict[str, Any]] = []
        hash_lines: list[str] = []
        for index, reference in enumerate(references, 1):
            destination = paths["originals"] / f"{index:02d}" / reference.name
            receipt = copy_bytes_preserving_content(reference, destination)
            image_info = inspect_image_file(destination, min_side=32)
            originals.append(
                {
                    "display_name": reference.name,
                    "archive_path": destination.relative_to(temp_dir).as_posix(),
                    **receipt,
                    **image_info,
                }
            )
            hash_lines.append(f"{receipt['sha256']}  {destination.relative_to(temp_dir).as_posix()}")

        write_json(paths["spec"], spec)
        write_json(paths["plan"] / "creator-profile.json", load_json(profile_source))
        atomic_write(paths["originals"] / "SHA256SUMS.txt", ("\n".join(hash_lines) + "\n").encode("utf-8"))
        write_json(
            paths["state"],
            {
                "schema_version": 1,
                "originals": originals,
                "imports": {},
                "events": [],
                "local_source_paths": [str(path) for path in references],
            },
        )
        os.replace(temp_dir, run_dir)
    except Exception:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise
    print(run_dir)


def load_run(run_dir: Path) -> tuple[dict[str, Path], dict[str, Any], dict[str, Any]]:
    run_dir = run_dir.expanduser()
    if run_dir.is_symlink():
        raise PackError(f"Run directory must not be a symlink: {run_dir}")
    run_dir = run_dir.resolve()
    paths = run_paths(run_dir)
    if not run_dir.is_dir() or not paths["spec"].is_file() or not paths["state"].is_file():
        raise PackError(f"Not a valid run directory: {run_dir}")
    for top in (
        "00-reference-originals",
        "01-plan",
        "02-source-assets",
        "03-submission",
        "04-preview",
        "archives",
    ):
        top_path = run_dir / top
        if top_path.exists() and (top_path.is_symlink() or not top_path.is_dir()):
            raise PackError(f"Run top-level path must be a real directory: {top_path}")
        if top_path.exists():
            try:
                top_path.resolve().relative_to(run_dir)
            except ValueError as exc:
                raise PackError(f"Run top-level path escapes run directory: {top_path}") from exc
    for key, path in paths.items():
        if key in {"run", "state", "spec"}:
            continue
        if path.exists() and path.is_symlink():
            raise PackError(f"Run subdirectory must not be a symlink: {path}")
    for path in run_dir.rglob("*"):
        if path.is_symlink():
            raise PackError(f"Run directory must not contain symlinks: {path}")
    return paths, load_json(paths["spec"]), load_json(paths["state"])


def require_generation_supported(spec: dict[str, Any]) -> None:
    if spec.get("rules_status") == "changed-unsupported":
        raise PackError("Official platform requirements changed; update this skill before generating assets")


def expected_prompt(spec: dict[str, Any], kind: str, slot: str | None) -> str | None:
    if kind == "anchor":
        return spec["anchor_prompt"]
    if kind == "sticker":
        matches = [item for item in spec["stickers"] if item.get("id") == slot]
        if len(matches) != 1:
            raise PackError(f"Cannot resolve frozen prompt for sticker {slot}")
        return matches[0]["art_prompt"]
    if kind == "banner":
        return spec["assets"]["banner_prompt"]
    if kind == "cover-chroma":
        return spec["assets"]["cover_prompt"]
    if kind == "icon-chroma":
        return spec["assets"]["icon_prompt"]
    return None


def expected_reference_hashes(
    paths: dict[str, Path], state: dict[str, Any], kind: str
) -> list[str]:
    original_hashes = [
        record.get("sha256")
        for record in state.get("originals", [])
        if isinstance(record, dict) and isinstance(record.get("sha256"), str)
    ]
    imports = state.get("imports", {})
    if kind == "anchor":
        return original_hashes
    if kind in {"sticker", "banner", "cover-chroma", "icon-chroma"}:
        anchor = imports.get("anchor")
        if not isinstance(anchor, dict) or not isinstance(anchor.get("sha256"), str):
            raise PackError(f"Import the character anchor before {kind}")
        return original_hashes + [anchor["sha256"]]
    if kind == "cover":
        chroma = imports.get("cover-chroma")
        if not isinstance(chroma, dict) or not isinstance(chroma.get("sha256"), str):
            raise PackError("Import cover-chroma before the locally derived cover")
        return [chroma["sha256"]]
    if kind == "icon":
        chroma = imports.get("icon-chroma")
        if not isinstance(chroma, dict) or not isinstance(chroma.get("sha256"), str):
            raise PackError("Import icon-chroma before the locally derived icon")
        return [chroma["sha256"]]
    return []


def invalidate_manual_review(spec: dict[str, Any], keys: Iterable[str]) -> None:
    manual = spec.setdefault("manual_review", {})
    for key in keys:
        manual[key] = False


def invalidate_contact_sheet(paths: dict[str, Path]) -> None:
    for name in ("contact-sheet.png", "contact-sheet.json"):
        path = paths["preview"] / name
        if path.exists() and path.is_file() and not path.is_symlink():
            path.unlink()


def generation_ledger_data(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "assurance": "workflow-recorded; generator labels are asserted by the executing agent",
        "originals": [
            {
                "archive_path": record.get("archive_path"),
                "sha256": record.get("sha256"),
                "size": record.get("size"),
            }
            for record in state.get("originals", [])
            if isinstance(record, dict)
        ],
        "imports": state.get("imports", {}),
        "events": state.get("events", []),
    }


def write_generation_ledger(paths: dict[str, Path], state: dict[str, Any]) -> None:
    write_json(paths["provenance"] / "generation-ledger.json", generation_ledger_data(state))


def find_one(directory: Path, stem: str) -> Path:
    matches = [path for path in directory.glob(f"{stem}.*") if path.is_file() and not path.name.startswith(".")]
    if len(matches) != 1:
        raise PackError(f"Expected exactly one imported source for {stem} in {directory}; found {len(matches)}")
    return matches[0]


def import_art(args: argparse.Namespace) -> None:
    paths, spec, state = load_run(args.run_dir)
    require_generation_supported(spec)
    source = ensure_regular_input(args.source)
    source_info = inspect_image_file(source, min_side=32)
    kind = args.kind
    slot = args.slot
    expected_generator = "builtin-imagegen" if kind in BUILTIN_GENERATED_KINDS else "local-chroma-removal"
    if args.generator != expected_generator:
        raise PackError(f"{kind} must use --generator {expected_generator}")
    chroma_key = getattr(args, "chroma_key", None)
    edge_contract = getattr(args, "edge_contract", None)
    if kind in LOCAL_DERIVED_KINDS:
        if not isinstance(chroma_key, str) or not re.fullmatch(r"#[0-9A-Fa-f]{6}", chroma_key):
            raise PackError(f"--chroma-key is required for locally derived {kind}")
        if not isinstance(edge_contract, int) or isinstance(edge_contract, bool) or not (0 <= edge_contract <= 3):
            raise PackError("--edge-contract must be an integer from 0 to 3")
        chroma_key = chroma_key.lower()
    elif chroma_key is not None or edge_contract is not None:
        raise PackError("Chroma-removal parameters are allowed only for locally derived cover/icon")
    if kind == "sticker":
        if slot not in EXPECTED_IDS:
            raise PackError("--slot must be 01 through 20 for sticker art")
        destination_dir = paths["raw_stickers"]
        stem = slot
        import_key = f"sticker:{slot}"
    elif kind == "anchor":
        if slot:
            raise PackError("--slot is not allowed for anchor")
        destination_dir = paths["run"] / "02-source-assets"
        stem = "character-anchor"
        import_key = "anchor"
    elif kind in {"banner", "cover", "icon", "cover-chroma", "icon-chroma"}:
        if slot:
            raise PackError(f"--slot is not allowed for {kind}")
        destination_dir = paths["raw_assets"]
        stem = kind
        import_key = kind
    else:
        raise PackError(f"Unsupported art kind: {kind}")

    frozen_prompt = expected_prompt(spec, kind, slot)
    prompt_relative: str | None = None
    prompt_hash: str | None = None
    if frozen_prompt is not None:
        if args.prompt_file is None:
            raise PackError(f"--prompt-file is required for {kind}")
        prompt_source = ensure_regular_input(args.prompt_file)
        try:
            supplied_prompt = prompt_source.read_text(encoding="utf-8").strip()
        except UnicodeDecodeError as exc:
            raise PackError(f"Prompt file must be UTF-8 text: {prompt_source}") from exc
        if supplied_prompt != frozen_prompt.strip():
            raise PackError(f"Prompt file does not match the frozen pack prompt for {import_key}")
        prompt_destination = paths["plan"] / "prompts" / f"{import_key.replace(':', '-')}.txt"
        atomic_write(prompt_destination, (supplied_prompt + "\n").encode("utf-8"))
        prompt_relative = prompt_destination.relative_to(paths["run"]).as_posix()
        prompt_hash = sha256_file(prompt_destination)
    elif args.prompt_file is not None:
        raise PackError(f"--prompt-file is not allowed for locally derived {kind}")

    reference_hashes = expected_reference_hashes(paths, state, kind)

    extension = source.suffix.lower() or ".png"
    destination = destination_dir / f"{stem}{extension}"
    existing = [path for path in destination_dir.glob(f"{stem}.*") if path.is_file()]
    source_hash = sha256_file(source)
    if existing:
        identical = len(existing) == 1 and sha256_file(existing[0]) == source_hash
        if not identical and not args.replace_slot:
            raise PackError(f"Art slot already contains different content: {import_key}")
        if not identical:
            versions = paths["run"] / "02-source-assets" / "versions"
            versions.mkdir(parents=True, exist_ok=True)
            for old in existing:
                old.chmod(0o644)
                archived = versions / f"{stem}-{sha256_file(old)[:12]}{old.suffix.lower()}"
                if not archived.exists():
                    os.replace(old, archived)
                else:
                    old.unlink()
        else:
            destination = existing[0]

    if destination.exists():
        receipt = {"sha256": sha256_file(destination), "size": destination.stat().st_size}
    else:
        receipt = copy_bytes_preserving_content(source, destination)
    events = state.setdefault("events", [])
    if not isinstance(events, list):
        raise PackError("state.events must be an array")
    event = {
        "event_index": len(events) + 1,
        "import_key": import_key,
        "kind": kind,
        "slot": slot,
        "generator": args.generator,
        "prompt_path": prompt_relative,
        "prompt_sha256": prompt_hash,
        "source_sha256": receipt["sha256"],
        "reference_sha256": reference_hashes,
        "chroma_key": chroma_key,
        "edge_contract": edge_contract,
    }
    events.append(event)
    state.setdefault("imports", {})[import_key] = {
        "archive_path": destination.relative_to(paths["run"]).as_posix(),
        "event_index": event["event_index"],
        "generator": args.generator,
        "prompt_path": prompt_relative,
        "prompt_sha256": prompt_hash,
        "reference_sha256": reference_hashes,
        "chroma_key": chroma_key,
        "edge_contract": edge_contract,
        **receipt,
        **source_info,
    }
    if kind in {"anchor", "sticker"}:
        invalidate_manual_review(
            spec,
            ["source_art_has_no_gibberish", "character_consistent", "text_visually_correct"],
        )
        invalidate_contact_sheet(paths)
    elif kind == "banner":
        invalidate_manual_review(spec, ["banner_has_no_text_or_numbers", "publication_assets_visually_clean"])
    else:
        invalidate_manual_review(spec, ["publication_assets_visually_clean"])
    write_json(paths["state"], state)
    write_generation_ledger(paths, state)
    write_json(paths["spec"], spec)
    print(destination)


def find_font(spec: dict[str, Any]) -> Path:
    configured = spec.get("render", {}).get("font_path")
    candidates: list[Path] = []
    if configured:
        configured_path = Path(configured).expanduser()
        candidates.append(configured_path if configured_path.is_absolute() else SKILL_DIR / configured_path)
    env_font = os.environ.get("STICKER_FONT")
    if env_font:
        candidates.append(Path(env_font).expanduser())
    candidates.extend(
        [
            Path("/System/Library/Fonts/Hiragino Sans GB.ttc"),
            Path("/System/Library/Fonts/STHeiti Medium.ttc"),
            Path("/System/Library/Fonts/Supplemental/Songti.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
            Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
            Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
            Path("C:/Windows/Fonts/msyhbd.ttc"),
            Path("C:/Windows/Fonts/msyh.ttc"),
        ]
    )
    for candidate in candidates:
        if candidate.is_file():
            try:
                font = ImageFont.truetype(str(candidate), 32)
                fingerprints = {glyph_fingerprint(font, ch) for ch in "汉字表情早安"}
                missing = glyph_fingerprint(font, "\u0378")
                if len(fingerprints) >= 4 and missing not in fingerprints:
                    return candidate
            except OSError:
                continue
    raise PackError("No usable CJK font found. Set render.font_path or STICKER_FONT.")


def glyph_fingerprint(font: ImageFont.FreeTypeFont, character: str) -> tuple[tuple[int, int], bytes]:
    mask = font.getmask(character, mode="L")
    return mask.size, bytes(mask)


def ensure_font_support(font_path: Path, text: str) -> None:
    font = ImageFont.truetype(str(font_path), 48)
    missing = glyph_fingerprint(font, "\u0378")
    for character in sorted(set(text)):
        if character.isspace():
            continue
        if glyph_fingerprint(font, character) == missing:
            raise PackError(f"Selected font lacks glyph U+{ord(character):04X}: {font_path}")


def image_to_square_rgb(image: Image.Image, size: int, background: str) -> Image.Image:
    image = ImageOps.exif_transpose(image)
    if image.mode == "RGBA":
        base = Image.new("RGBA", image.size, background)
        base.alpha_composite(image)
        image = base.convert("RGB")
    else:
        image = image.convert("RGB")
    return ImageOps.fit(image, (size, size), method=RESAMPLE, centering=(0.5, 0.5))


def layout_box_for(item: dict[str, Any], render: dict[str, Any]) -> list[int]:
    default = render.get("default_text", {})
    if isinstance(item.get("text_layout"), dict) and isinstance(item["text_layout"].get("box"), list):
        box = item["text_layout"]["box"]
    else:
        position = item.get("text_zone", default.get("position", "bottom"))
        box = [12, 8, 228, 74] if position == "top" else [12, 166, 228, 234]
    if len(box) != 4 or not all(isinstance(value, int) for value in box):
        raise PackError(f"Invalid text box for sticker {item.get('id')}")
    if not (0 <= box[0] < box[2] <= 240 and 0 <= box[1] < box[3] <= 240):
        raise PackError(f"Text box is outside 240x240 canvas for sticker {item.get('id')}")
    return box


def line_candidates(text: str, explicit: Any, max_lines: int) -> list[list[str]]:
    if explicit:
        if isinstance(explicit, list):
            lines = [str(value) for value in explicit]
        else:
            lines = str(explicit).split("\n")
        if "".join(lines) != text.replace("\n", ""):
            raise PackError("Explicit line_break does not reconstruct exact_text")
        return [lines]
    raw = text.replace("\n", "")
    candidates = [[raw]]
    if max_lines >= 2:
        for split in range(1, len(raw)):
            candidates.append([raw[:split], raw[split:]])
    candidates.sort(key=lambda lines: (len(lines), max(len(line) for line in lines), abs(len(lines[0]) - len(lines[-1]))))
    return candidates


def fit_text_layout(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: Path,
    box: tuple[int, int, int, int],
    min_size: int,
    max_size: int,
    max_lines: int,
    stroke_width: int,
    explicit_break: Any,
) -> tuple[ImageFont.FreeTypeFont, list[str], tuple[int, int, int, int], int]:
    candidates = line_candidates(text, explicit_break, max_lines)
    box_width = box[2] - box[0]
    box_height = box[3] - box[1]
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(str(font_path), size)
        spacing = max(1, size // 12)
        for lines in candidates:
            if len(lines) > max_lines:
                continue
            joined = "\n".join(lines)
            bbox = draw.multiline_textbbox(
                (0, 0),
                joined,
                font=font,
                spacing=spacing,
                align="center",
                stroke_width=stroke_width,
            )
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width <= box_width and height <= box_height:
                return font, lines, bbox, spacing
    raise PackError(f"Exact text cannot fit legibly in its box: {text!r}")


def render_input_sha256(spec: dict[str, Any], item: dict[str, Any]) -> str:
    payload = {
        "render": spec.get("render"),
        "item": {
            key: item.get(key)
            for key in ("id", "exact_text", "text_zone", "line_break", "text_layout")
        },
    }
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def render_stickers(args: argparse.Namespace) -> None:
    paths, spec, state = load_run(args.run_dir)
    require_generation_supported(spec)
    errors = validate_spec(spec)
    if errors:
        raise PackError("Invalid pack spec:\n- " + "\n- ".join(errors))
    font_path = find_font(spec)
    ensure_font_support(font_path, "".join(item["exact_text"] for item in spec["stickers"]))
    font_hash = sha256_file(font_path)
    render = spec.get("render", {})
    master_size = int(render.get("master_size", 1024))
    if master_size < 480 or master_size > 4096:
        raise PackError("render.master_size must be between 480 and 4096")
    background = str(render.get("background", "#FFFFFF"))
    default_text = render.get("default_text", {})
    base_min = int(default_text.get("min_font_size", 20))
    base_max = int(default_text.get("max_font_size", 42))
    base_stroke = int(default_text.get("stroke_width", 2))
    max_lines = int(default_text.get("max_lines", 2))
    fill = str(default_text.get("fill", "#3A2416"))
    stroke_fill = str(default_text.get("stroke_fill", "#FFD979"))
    scale = master_size / 240.0

    paths["masters"].mkdir(parents=True, exist_ok=True)
    paths["submission_stickers"].mkdir(parents=True, exist_ok=True)
    receipt_dir = paths["provenance"] / "render"
    receipt_dir.mkdir(parents=True, exist_ok=True)

    for item in spec["stickers"]:
        item_id = item["id"]
        source = find_one(paths["raw_stickers"], item_id)
        with Image.open(source) as raw:
            master = image_to_square_rgb(raw, master_size, background)
        draw = ImageDraw.Draw(master)
        base_box = layout_box_for(item, render)
        box = tuple(int(round(value * scale)) for value in base_box)
        stroke_width = max(1, int(round(base_stroke * scale)))
        font, lines, bbox, spacing = fit_text_layout(
            draw,
            item["exact_text"].replace("\n", ""),
            font_path,
            box,
            max(1, int(round(base_min * scale))),
            max(2, int(round(base_max * scale))),
            max_lines,
            stroke_width,
            item.get("line_break"),
        )
        joined = "\n".join(lines)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        x = box[0] + (box[2] - box[0] - width) / 2 - bbox[0]
        y = box[1] + (box[3] - box[1] - height) / 2 - bbox[1]
        draw.multiline_text(
            (x, y),
            joined,
            font=font,
            fill=fill,
            spacing=spacing,
            align="center",
            stroke_width=stroke_width,
            stroke_fill=stroke_fill,
        )
        master_path = paths["masters"] / f"{item_id}.png"
        master.save(master_path, format="PNG", compress_level=9, optimize=False)

        final = master.resize((240, 240), RESAMPLE)
        final_path = paths["submission_stickers"] / f"{item_id}.png"
        final.save(final_path, format="PNG", compress_level=9, optimize=False)
        if final_path.stat().st_size >= 500_000:
            raise PackError(f"Rendered sticker exceeds 500 KB: {final_path}")

        receipt = {
            "id": item_id,
            "exact_text": item["exact_text"],
            "unicode_codepoints": [f"U+{ord(ch):04X}" for ch in item["exact_text"]],
            "lines": lines,
            "font_name": font_path.name,
            "font_sha256": font_hash,
            "font_size_master": font.size,
            "master_size": master_size,
            "text_box_240": base_box,
            "raw_sha256": sha256_file(source),
            "master_sha256": sha256_file(master_path),
            "final_sha256": sha256_file(final_path),
            "text_render_mode": "deterministic-overlay",
            "render_input_sha256": render_input_sha256(spec, item),
        }
        write_json(receipt_dir / f"{item_id}.json", receipt)
    invalidate_manual_review(
        spec,
        ["source_art_has_no_gibberish", "character_consistent", "text_visually_correct"],
    )
    invalidate_contact_sheet(paths)
    write_json(paths["spec"], spec)
    print(paths["submission_stickers"])


def contain_rgba(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = ImageOps.exif_transpose(image).convert("RGBA")
    contained = ImageOps.contain(image, size, method=RESAMPLE)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - contained.width) // 2, (size[1] - contained.height) // 2)
    canvas.alpha_composite(contained, offset)
    return canvas


def save_banner(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        image = ImageOps.exif_transpose(image).convert("RGB")
        final = ImageOps.fit(image, (750, 400), method=RESAMPLE, centering=(0.5, 0.5))
    for quality in (88, 84, 80, 76, 72, 68):
        buffer = io.BytesIO()
        final.save(buffer, format="JPEG", quality=quality, optimize=True, progressive=False)
        if len(buffer.getvalue()) < 500_000:
            atomic_write(destination, buffer.getvalue())
            return
    raise PackError("Banner cannot be compressed below 500 KB")


def save_alpha_asset(source: Path, destination: Path, size: tuple[int, int], limit: int) -> None:
    with Image.open(source) as image:
        if image.mode not in {"RGBA", "LA"} and "transparency" not in image.info:
            raise PackError(f"Transparent source required for {destination.name}: {source}")
        final = contain_rgba(image, size)
    alpha = final.getchannel("A")
    extrema = alpha.getextrema()
    if extrema[0] != 0 or extrema[1] != 255:
        raise PackError(f"Asset must contain both transparent and opaque pixels: {source}")
    buffer = io.BytesIO()
    final.save(buffer, format="PNG", compress_level=9, optimize=False)
    if len(buffer.getvalue()) >= limit:
        raise PackError(f"Asset exceeds size limit after resizing: {destination.name}")
    atomic_write(destination, buffer.getvalue())


def public_pack_metadata(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": spec["schema_version"],
        "platform_spec": spec["platform_spec"],
        "rules_status": spec["rules_status"],
        "rules_checked_at": spec.get("rules_checked_at"),
        "pack": {
            key: value
            for key, value in spec["pack"].items()
            if key
            in {
                "slug",
                "name",
                "introduction",
                "copyright",
                "type",
                "category",
                "character",
                "styles",
                "theme",
                "download_region",
                "listing_region",
                "price",
                "ai_generated",
            }
        },
        "stickers": [
            {
                "id": item["id"],
                "exact_text": item["exact_text"],
                "meaning_word": item["meaning_word"],
                "intent_key": item["intent_key"],
            }
            for item in spec["stickers"]
        ],
    }


def meaning_words_bytes(spec: dict[str, Any]) -> bytes:
    csv_buffer = io.StringIO(newline="")
    writer = csv.writer(csv_buffer)
    writer.writerow(["顺序", "文件", "图中文字", "含义词", "沟通意图"])
    for item in spec["stickers"]:
        writer.writerow(
            [
                item["id"],
                f"stickers/{item['id']}.png",
                item["exact_text"],
                item["meaning_word"],
                item["intent_key"],
            ]
        )
    return b"\xef\xbb\xbf" + csv_buffer.getvalue().encode("utf-8")


def fill_information_bytes(spec: dict[str, Any]) -> bytes:
    pack = spec["pack"]
    selections = [
        ("名称", pack["name"]),
        ("介绍", pack["introduction"]),
        ("版权", pack["copyright"]),
        ("上传表情类型", pack.get("type", "静态表情")),
        ("类型", pack.get("category", "卡通表情/其他")),
        ("角色/内容", " → ".join(pack.get("character", []))),
        ("表情风格", "、".join(pack.get("styles", []))),
        ("表情主题", pack.get("theme", "万能通用")),
        ("下载地区", pack.get("download_region", "全球")),
        ("上架地区", pack.get("listing_region", "中国大陆")),
        ("价格", pack.get("price", "免费")),
        ("赞赏", "关闭"),
    ]
    copy_text = ["微信表情专辑直接填写", ""]
    copy_text.extend(f"{label}：{value}" for label, value in selections)
    copy_text.extend(["", "逐张含义词："])
    copy_text.extend(f"{item['id']} {item['meaning_word']}" for item in spec["stickers"])
    return ("\n".join(copy_text) + "\n").encode("utf-8")


def rights_declaration(spec: dict[str, Any]) -> dict[str, Any]:
    pack = spec["pack"]
    return {
        "ai_generated": True,
        "reference_use": "User-supplied reference images were used as visual identity references.",
        "generation": "Q-version sticker art and publication art were generated with built-in image generation.",
        "local_processing": "Exact Chinese typography, resizing, transparency processing, validation, and packaging were performed locally.",
        "platform_action": "Select AI-generated or AI-assisted if the platform exposes that option.",
        "copyright": pack["copyright"],
        "rights_confirmed": pack["rights_confirmed"],
        "portrait_use_confirmed": pack["portrait_use_confirmed"],
    }


def generation_prompts_data(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "anchor": spec["anchor_prompt"],
        "stickers": [{"id": item["id"], "prompt": item["art_prompt"]} for item in spec["stickers"]],
        "assets": spec.get("assets", {}),
    }


def write_submission_metadata(paths: dict[str, Path], spec: dict[str, Any]) -> None:
    paths["metadata"].mkdir(parents=True, exist_ok=True)
    write_json(paths["metadata"] / "pack.json", public_pack_metadata(spec))
    atomic_write(paths["metadata"] / "meaning_words.csv", meaning_words_bytes(spec))
    atomic_write(paths["metadata"] / "填写信息.txt", fill_information_bytes(spec))

    write_json(paths["plan"] / "generation-prompts.json", generation_prompts_data(spec))
    write_json(paths["metadata"] / "rights-ai-declaration.json", rights_declaration(spec))


def prepare_assets(args: argparse.Namespace) -> None:
    paths, spec, state = load_run(args.run_dir)
    require_generation_supported(spec)
    paths["submission_assets"].mkdir(parents=True, exist_ok=True)
    banner = find_one(paths["raw_assets"], "banner")
    cover = find_one(paths["raw_assets"], "cover")
    icon = find_one(paths["raw_assets"], "icon")
    save_banner(banner, paths["submission_assets"] / "banner_750x400.jpg")
    save_alpha_asset(cover, paths["submission_assets"] / "cover_240x240.png", (240, 240), 500_000)
    save_alpha_asset(icon, paths["submission_assets"] / "icon_50x50.png", (50, 50), 100_000)
    write_submission_metadata(paths, spec)
    asset_receipts = paths["provenance"] / "assets"
    asset_receipts.mkdir(parents=True, exist_ok=True)
    for name, source, output in (
        ("banner", banner, paths["submission_assets"] / "banner_750x400.jpg"),
        ("cover", cover, paths["submission_assets"] / "cover_240x240.png"),
        ("icon", icon, paths["submission_assets"] / "icon_50x50.png"),
    ):
        write_json(
            asset_receipts / f"{name}.json",
            {
                "asset": name,
                "source_sha256": sha256_file(source),
                "output_sha256": sha256_file(output),
            },
        )
    invalidate_manual_review(
        spec,
        ["banner_has_no_text_or_numbers", "publication_assets_visually_clean"],
    )
    write_json(paths["spec"], spec)
    print(paths["submission_assets"])


def contact_sheet(args: argparse.Namespace) -> None:
    paths, spec, state = load_run(args.run_dir)
    files = [paths["submission_stickers"] / f"{item_id}.png" for item_id in EXPECTED_IDS]
    missing = [path.name for path in files if not path.is_file()]
    if missing:
        raise PackError("Cannot create contact sheet; missing: " + ", ".join(missing))
    columns, rows, cell, gap = 5, 4, 240, 12
    canvas = Image.new(
        "RGB",
        (columns * cell + (columns + 1) * gap, rows * cell + (rows + 1) * gap),
        "#E8E8E8",
    )
    for index, path in enumerate(files):
        with Image.open(path) as image:
            image = image.convert("RGB")
            x = gap + (index % columns) * (cell + gap)
            y = gap + (index // columns) * (cell + gap)
            canvas.paste(image, (x, y))
    paths["preview"].mkdir(parents=True, exist_ok=True)
    destination = paths["preview"] / "contact-sheet.png"
    canvas.save(destination, format="PNG", compress_level=9, optimize=False)
    receipt = {
        "contact_sheet_sha256": sha256_file(destination),
        "stickers": [
            {"id": item_id, "sha256": sha256_file(paths["submission_stickers"] / f"{item_id}.png")}
            for item_id in EXPECTED_IDS
        ],
    }
    write_json(paths["preview"] / "contact-sheet.json", receipt)
    invalidate_manual_review(
        spec,
        ["source_art_has_no_gibberish", "character_consistent", "text_visually_correct"],
    )
    write_json(paths["spec"], spec)
    print(destination)


def flattened_pixels(image: Image.Image) -> list[Any]:
    getter = getattr(image, "get_flattened_data", None)
    return list(getter() if getter else image.getdata())


def dhash(image: Image.Image) -> int:
    grayscale = image.convert("L").resize((9, 8), RESAMPLE)
    pixels = flattened_pixels(grayscale)
    value = 0
    for row in range(8):
        for col in range(8):
            value <<= 1
            if pixels[row * 9 + col] > pixels[row * 9 + col + 1]:
                value |= 1
    return value


def alpha_metrics(image: Image.Image) -> dict[str, Any]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    extrema = alpha.getextrema()
    corners = [
        alpha.getpixel((0, 0)),
        alpha.getpixel((rgba.width - 1, 0)),
        alpha.getpixel((0, rgba.height - 1)),
        alpha.getpixel((rgba.width - 1, rgba.height - 1)),
    ]
    return {"alpha_extrema": extrema, "alpha_corners": corners, "bbox": alpha.getbbox()}


def white_ratio(image: Image.Image) -> float:
    rgb = image.convert("RGB").resize((150, 80), RESAMPLE)
    pixels = flattened_pixels(rgb)
    whites = sum(1 for r, g, b in pixels if r > 242 and g > 242 and b > 242)
    return whites / len(pixels)


def verify_originals(paths: dict[str, Path], state: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    records = state.get("originals")
    if not isinstance(records, list) or not records:
        return ["state.originals must contain at least one preserved reference record"]
    expected_files = {"SHA256SUMS.txt"}
    checksum_lines: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            errors.append("Original record must be an object")
            continue
        relative = record.get("archive_path")
        if not isinstance(relative, str):
            errors.append("Original record missing archive_path")
            continue
        try:
            original_relative = Path(relative).relative_to("00-reference-originals").as_posix()
        except ValueError:
            errors.append(f"Original archive_path is outside 00-reference-originals: {relative}")
            continue
        expected_files.add(original_relative)
        checksum_lines.append(f"{record.get('sha256')}  {relative}")
        try:
            path = safe_relative_path(paths["run"], relative)
        except PackError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file():
            errors.append(f"Archived original missing: {relative}")
        elif path.stat().st_size != record.get("size") or sha256_file(path) != record.get("sha256"):
            errors.append(f"Archived original changed: {relative}")
        elif path.name != record.get("display_name"):
            errors.append(f"Archived original filename changed: {relative}")
    actual_files: set[str] = set()
    if paths["originals"].is_dir() and not paths["originals"].is_symlink():
        for path in paths["originals"].rglob("*"):
            if path.is_symlink():
                errors.append(f"Original archive contains a symlink: {path}")
            elif path.is_file():
                actual_files.add(path.relative_to(paths["originals"]).as_posix())
    if actual_files != expected_files:
        errors.append(
            "Original archive tree differs from recorded files: "
            f"missing={sorted(expected_files - actual_files)}, extra={sorted(actual_files - expected_files)}"
        )
    checksum_path = paths["originals"] / "SHA256SUMS.txt"
    expected_checksum = ("\n".join(checksum_lines) + "\n").encode("utf-8")
    if not checksum_path.is_file() or checksum_path.read_bytes() != expected_checksum:
        errors.append("Original SHA256SUMS.txt is missing or stale")
    return errors


def forbidden_derived_metadata(image: Image.Image) -> list[str]:
    forbidden: list[str] = []
    if image.getexif():
        forbidden.append("EXIF")
    allowed_structural = {"jfif", "jfif_version", "jfif_unit", "jfif_density"}
    for key in image.info:
        if key.lower() not in allowed_structural:
            forbidden.append(key)
    return sorted(set(forbidden))


def verify_source_provenance(
    paths: dict[str, Path], spec: dict[str, Any], state: dict[str, Any]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    warnings.append(FULL_ARCHIVE_PRIVACY_WARNING)
    imports = state.get("imports")
    if not isinstance(imports, dict):
        return ["state.imports must be an object"], warnings
    events = state.get("events")
    if not isinstance(events, list):
        return ["state.events must be an array"], warnings
    for index, event in enumerate(events, 1):
        if not isinstance(event, dict) or event.get("event_index") != index:
            errors.append(f"Import event sequence is invalid at index {index}")
    ledger_path = paths["provenance"] / "generation-ledger.json"
    if not ledger_path.is_file() or ledger_path.is_symlink():
        errors.append("Generation provenance ledger is missing or unsafe")
    else:
        try:
            if load_json(ledger_path) != generation_ledger_data(state):
                errors.append("Generation provenance ledger is stale")
        except PackError as exc:
            errors.append(str(exc))

    required_keys = (
        ["anchor", "banner", "cover", "icon", "cover-chroma", "icon-chroma"]
        + [f"sticker:{item_id}" for item_id in EXPECTED_IDS]
    )
    for key in required_keys:
        record = imports.get(key)
        if not isinstance(record, dict):
            errors.append(f"Missing import provenance: {key}")
            continue
        relative = record.get("archive_path")
        if not isinstance(relative, str):
            errors.append(f"Import provenance lacks archive_path: {key}")
            continue
        try:
            path = safe_relative_path(paths["run"], relative)
        except PackError as exc:
            errors.append(str(exc))
            continue
        if not path.is_file() or path.is_symlink():
            errors.append(f"Imported source missing or unsafe: {key}")
            continue
        if path.stat().st_size != record.get("size") or sha256_file(path) != record.get("sha256"):
            errors.append(f"Imported source changed after registration: {key}")
        kind = "sticker" if key.startswith("sticker:") else key
        slot = key.split(":", 1)[1] if key.startswith("sticker:") else None
        expected_generator = "builtin-imagegen" if kind in BUILTIN_GENERATED_KINDS else "local-chroma-removal"
        if record.get("generator") != expected_generator:
            errors.append(f"Wrong or missing generator provenance for {key}")
        if kind in LOCAL_DERIVED_KINDS:
            if not isinstance(record.get("chroma_key"), str) or not re.fullmatch(
                r"#[0-9a-f]{6}", record.get("chroma_key", "")
            ):
                errors.append(f"Missing chroma-key provenance for {key}")
            if not isinstance(record.get("edge_contract"), int) or not (0 <= record.get("edge_contract") <= 3):
                errors.append(f"Missing edge-contract provenance for {key}")
        event_index = record.get("event_index")
        if not isinstance(event_index, int) or not (1 <= event_index <= len(events)):
            errors.append(f"Missing latest event provenance for {key}")
        else:
            event = events[event_index - 1]
            expected_event = {
                "import_key": key,
                "kind": kind,
                "slot": slot,
                "generator": expected_generator,
                "source_sha256": record.get("sha256"),
                "chroma_key": record.get("chroma_key"),
                "edge_contract": record.get("edge_contract"),
            }
            for field, expected_value in expected_event.items():
                if not isinstance(event, dict) or event.get(field) != expected_value:
                    errors.append(f"Import event mismatch for {key}: {field}")
        try:
            references = expected_reference_hashes(paths, state, kind)
        except PackError as exc:
            errors.append(str(exc))
            references = []
        if record.get("reference_sha256") != references:
            errors.append(f"Reference provenance is stale for {key}")
        if isinstance(event_index, int) and 1 <= event_index <= len(events):
            event = events[event_index - 1]
            if not isinstance(event, dict) or event.get("reference_sha256") != references:
                errors.append(f"Import event reference hashes are stale for {key}")
        frozen_prompt = expected_prompt(spec, kind, slot)
        prompt_relative = record.get("prompt_path")
        if frozen_prompt is None:
            if prompt_relative is not None or record.get("prompt_sha256") is not None:
                errors.append(f"Locally derived asset must not claim a generation prompt: {key}")
        elif not isinstance(prompt_relative, str):
            errors.append(f"Missing frozen prompt provenance for {key}")
        else:
            try:
                prompt_path = safe_relative_path(paths["run"], prompt_relative)
            except PackError as exc:
                errors.append(str(exc))
                continue
            expected_bytes = (frozen_prompt.strip() + "\n").encode("utf-8")
            if not prompt_path.is_file() or prompt_path.is_symlink():
                errors.append(f"Frozen prompt file missing or unsafe for {key}")
            elif prompt_path.read_bytes() != expected_bytes:
                errors.append(f"Frozen prompt file is stale for {key}")
            elif record.get("prompt_sha256") != sha256_file(prompt_path):
                errors.append(f"Frozen prompt hash mismatch for {key}")
        if isinstance(event_index, int) and 1 <= event_index <= len(events):
            event = events[event_index - 1]
            if not isinstance(event, dict) or event.get("prompt_path") != record.get("prompt_path"):
                errors.append(f"Import event prompt path mismatch for {key}")
            if not isinstance(event, dict) or event.get("prompt_sha256") != record.get("prompt_sha256"):
                errors.append(f"Import event prompt hash mismatch for {key}")

    raw_hashes: dict[str, str] = {}
    for item_id in EXPECTED_IDS:
        try:
            raw = find_one(paths["raw_stickers"], item_id)
            info = inspect_image_file(raw, min_side=480)
        except PackError as exc:
            errors.append(str(exc))
            continue
        digest = sha256_file(raw)
        if digest in raw_hashes:
            errors.append(f"Duplicate high-resolution raw artwork: {raw_hashes[digest]} and {item_id}")
        raw_hashes[digest] = item_id

    try:
        anchor = find_one(paths["run"] / "02-source-assets", "character-anchor")
        inspect_image_file(anchor, min_side=480)
    except PackError as exc:
        errors.append(str(exc))

    for stem in ("banner", "cover", "icon", "cover-chroma", "icon-chroma"):
        try:
            source = find_one(paths["raw_assets"], stem)
            inspect_image_file(source, min_side=240 if stem in {"cover", "icon"} else 480)
        except PackError as exc:
            errors.append(str(exc))

    master_names = sorted(path.name for path in paths["masters"].glob("*.png"))
    expected_names = [f"{item_id}.png" for item_id in EXPECTED_IDS]
    if master_names != expected_names:
        errors.append("High-resolution masters must be exactly 01.png through 20.png")
    receipt_dir = paths["provenance"] / "render"
    receipt_names = sorted(path.name for path in receipt_dir.glob("*.json"))
    expected_receipts = [f"{item_id}.json" for item_id in EXPECTED_IDS]
    if receipt_names != expected_receipts:
        errors.append("Render receipts must be exactly 01.json through 20.json")

    items = {item["id"]: item for item in spec.get("stickers", []) if isinstance(item, dict)}
    master_size = int(spec.get("render", {}).get("master_size", 1024))
    current_font_hash: str | None = None
    try:
        current_font_hash = sha256_file(find_font(spec))
    except PackError as exc:
        errors.append(str(exc))
    for item_id in EXPECTED_IDS:
        master = paths["masters"] / f"{item_id}.png"
        final = paths["submission_stickers"] / f"{item_id}.png"
        receipt_path = receipt_dir / f"{item_id}.json"
        raw: Path | None = None
        try:
            raw = find_one(paths["raw_stickers"], item_id)
        except PackError:
            pass
        if master.is_file():
            try:
                with Image.open(master) as image:
                    image.load()
                    if image.format != "PNG" or image.size != (master_size, master_size):
                        errors.append(f"Master {item_id}.png must be {master_size}x{master_size} PNG")
                    metadata = forbidden_derived_metadata(image)
                    if metadata:
                        errors.append(f"Master {item_id}.png contains metadata: {', '.join(metadata)}")
            except Exception as exc:
                errors.append(f"Master {item_id}.png is unreadable: {exc}")
        if not receipt_path.is_file():
            continue
        try:
            receipt = load_json(receipt_path)
        except PackError as exc:
            errors.append(str(exc))
            continue
        item = items.get(item_id)
        if not item:
            errors.append(f"Spec item missing for receipt {item_id}")
            continue
        if receipt.get("exact_text") != item.get("exact_text"):
            errors.append(f"Receipt text is stale for {item_id}")
        if receipt.get("unicode_codepoints") != [f"U+{ord(ch):04X}" for ch in item.get("exact_text", "")]:
            errors.append(f"Receipt code points are stale for {item_id}")
        if receipt.get("render_input_sha256") != render_input_sha256(spec, item):
            errors.append(f"Receipt render configuration is stale for {item_id}")
        if current_font_hash is not None and receipt.get("font_sha256") != current_font_hash:
            errors.append(f"Receipt font is stale for {item_id}")
        if "".join(receipt.get("lines", [])) != item.get("exact_text"):
            errors.append(f"Receipt line layout does not reconstruct exact text for {item_id}")
        comparisons = [
            ("raw_sha256", raw),
            ("master_sha256", master),
            ("final_sha256", final),
        ]
        for field, file_path in comparisons:
            if file_path is None or not file_path.is_file():
                errors.append(f"Receipt target missing for {item_id}: {field}")
            elif receipt.get(field) != sha256_file(file_path):
                errors.append(f"Receipt hash mismatch for {item_id}: {field}")

    contact_sheet_path = paths["preview"] / "contact-sheet.png"
    contact_receipt_path = paths["preview"] / "contact-sheet.json"
    if not contact_sheet_path.is_file():
        errors.append("Review contact sheet is missing")
    if not contact_receipt_path.is_file():
        errors.append("Review contact sheet receipt is missing")
    else:
        try:
            contact_receipt = load_json(contact_receipt_path)
            if not contact_sheet_path.is_file() or contact_receipt.get("contact_sheet_sha256") != sha256_file(contact_sheet_path):
                errors.append("Review contact sheet receipt is stale")
            expected_contact = [
                {
                    "id": item_id,
                    "sha256": sha256_file(paths["submission_stickers"] / f"{item_id}.png"),
                }
                for item_id in EXPECTED_IDS
                if (paths["submission_stickers"] / f"{item_id}.png").is_file()
            ]
            if contact_receipt.get("stickers") != expected_contact or len(expected_contact) != 20:
                errors.append("Review contact sheet does not match all current final stickers")
        except PackError as exc:
            errors.append(str(exc))
    prompts_path = paths["plan"] / "generation-prompts.json"
    if not prompts_path.is_file():
        errors.append("Plan generation-prompts.json is missing")
    else:
        try:
            if load_json(prompts_path) != generation_prompts_data(spec):
                errors.append("Plan generation-prompts.json is stale")
        except PackError as exc:
            errors.append(str(exc))
    asset_receipt_dir = paths["provenance"] / "assets"
    for name, source_stem, output_name in (
        ("banner", "banner", "banner_750x400.jpg"),
        ("cover", "cover", "cover_240x240.png"),
        ("icon", "icon", "icon_50x50.png"),
    ):
        receipt_path = asset_receipt_dir / f"{name}.json"
        output_path = paths["submission_assets"] / output_name
        try:
            source_path = find_one(paths["raw_assets"], source_stem)
        except PackError as exc:
            errors.append(str(exc))
            continue
        if not receipt_path.is_file():
            errors.append(f"Publication asset receipt is missing: {name}")
            continue
        try:
            receipt = load_json(receipt_path)
        except PackError as exc:
            errors.append(str(exc))
            continue
        if receipt.get("source_sha256") != sha256_file(source_path):
            errors.append(f"Publication asset source receipt is stale: {name}")
        if not output_path.is_file() or receipt.get("output_sha256") != sha256_file(output_path):
            errors.append(f"Publication asset output receipt is stale: {name}")
    return errors, warnings


def validate_run(run_dir: Path, *, strict: bool, write_report: bool = True) -> dict[str, Any]:
    paths, spec, state = load_run(run_dir)
    errors = validate_spec(spec)
    if errors:
        report = {
            "schema_version": 1,
            "status": "draft/not-ready",
            "strict": strict,
            "checks": {
                "sticker_count": 0,
                "expected_sticker_count": 20,
                "original_count": len(state.get("originals", [])) if isinstance(state.get("originals"), list) else 0,
                "rules_status": spec.get("rules_status"),
                "python": sys.version.split()[0],
                "pillow": PILLOW_VERSION,
            },
            "integrity_errors": list(errors),
            "readiness_blockers": [],
            "errors": list(errors),
            "warnings": [FULL_ARCHIVE_PRIVACY_WARNING],
        }
        if write_report:
            paths["qa"].mkdir(parents=True, exist_ok=True)
            write_json(paths["qa"] / "qa-report.json", report)
            lines = [
                "Status: draft/not-ready",
                f"Errors: {len(errors)}",
                "",
                "FULL ARCHIVE PRIVACY",
                f"- {FULL_ARCHIVE_PRIVACY_WARNING}",
                "",
                "ERRORS",
                *[f"- {item}" for item in errors],
            ]
            atomic_write(paths["qa"] / "qa-report.txt", ("\n".join(lines) + "\n").encode("utf-8"))
        return report
    warnings: list[str] = []
    errors.extend(verify_originals(paths, state))
    provenance_errors, provenance_warnings = verify_source_provenance(paths, spec, state)
    errors.extend(provenance_errors)
    warnings.extend(provenance_warnings)

    sticker_files = sorted(path.name for path in paths["submission_stickers"].glob("*.png"))
    expected_names = [f"{item_id}.png" for item_id in EXPECTED_IDS]
    if sticker_files != expected_names:
        errors.append("Submission stickers must be exactly 01.png through 20.png")
    hashes: list[str] = []
    hashes_seen: set[str] = set()
    dhashes: list[tuple[str, int]] = []
    for name in expected_names:
        path = paths["submission_stickers"] / name
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                image.load()
                if image.format != "PNG" or image.size != (240, 240):
                    errors.append(f"{name} must be 240x240 PNG")
                if image.mode not in {"RGB", "RGBA"}:
                    errors.append(f"{name} must be RGB or RGBA")
                metadata = forbidden_derived_metadata(image)
                if metadata:
                    errors.append(f"{name} contains forbidden metadata: {', '.join(metadata)}")
                dhashes.append((name, dhash(image)))
        except Exception as exc:
            errors.append(f"{name} is unreadable: {exc}")
            continue
        if path.stat().st_size >= 500_000:
            errors.append(f"{name} must be below 500 KB")
        digest = sha256_file(path)
        hashes.append(digest)
        if digest in hashes_seen:
            errors.append(f"Duplicate final sticker bytes detected: {name}")
        hashes_seen.add(digest)

    for index, (name_a, hash_a) in enumerate(dhashes):
        for name_b, hash_b in dhashes[index + 1 :]:
            distance = (hash_a ^ hash_b).bit_count()
            if distance <= 2:
                warnings.append(f"Visually similar stickers require review: {name_a} and {name_b} (dHash {distance})")

    asset_specs = {
        "banner_750x400.jpg": ((750, 400), 500_000, False, "JPEG"),
        "cover_240x240.png": ((240, 240), 500_000, True, "PNG"),
        "icon_50x50.png": ((50, 50), 100_000, True, "PNG"),
    }
    for name, (size, limit, needs_alpha, expected_format) in asset_specs.items():
        path = paths["submission_assets"] / name
        if not path.is_file():
            errors.append(f"Missing publication asset: {name}")
            continue
        if path.stat().st_size >= limit:
            errors.append(f"{name} exceeds {limit} bytes")
        try:
            with Image.open(path) as image:
                image.load()
                if image.size != size:
                    errors.append(f"{name} must be {size[0]}x{size[1]}")
                if image.format != expected_format:
                    errors.append(f"{name} must be encoded as {expected_format}")
                metadata = forbidden_derived_metadata(image)
                if metadata:
                    errors.append(f"{name} contains forbidden metadata: {', '.join(metadata)}")
                if needs_alpha:
                    metrics = alpha_metrics(image)
                    if metrics["alpha_extrema"][0] != 0 or metrics["alpha_extrema"][1] != 255:
                        errors.append(f"{name} must contain transparent and opaque pixels")
                    if any(value != 0 for value in metrics["alpha_corners"]):
                        errors.append(f"{name} must have transparent corners")
                else:
                    if image.mode in {"RGBA", "LA"}:
                        errors.append(f"{name} must not have an alpha channel")
                    ratio = white_ratio(image)
                    if ratio > 0.65:
                        errors.append(f"{name} has too much white background ({ratio:.1%})")
        except Exception as exc:
            errors.append(f"{name} is unreadable: {exc}")

    required_metadata = [
        "pack.json",
        "meaning_words.csv",
        "填写信息.txt",
        "rights-ai-declaration.json",
    ]
    for name in required_metadata:
        if not (paths["metadata"] / name).is_file():
            errors.append(f"Missing metadata file: {name}")
    public_metadata_path = paths["metadata"] / "pack.json"
    if public_metadata_path.is_file():
        try:
            if load_json(public_metadata_path) != public_pack_metadata(spec):
                errors.append("Submission metadata pack.json is stale or contains extra private fields")
        except PackError as exc:
            errors.append(str(exc))
    exact_metadata = {
        "meaning_words.csv": meaning_words_bytes(spec),
        "填写信息.txt": fill_information_bytes(spec),
        "rights-ai-declaration.json": canonical_json_bytes(rights_declaration(spec), pretty=True),
    }
    for name, expected_bytes in exact_metadata.items():
        path = paths["metadata"] / name
        if path.is_file() and path.read_bytes() != expected_bytes:
            errors.append(f"Submission metadata is stale or modified: {name}")

    allowed_submission = {
        *(f"stickers/{item_id}.png" for item_id in EXPECTED_IDS),
        "assets/banner_750x400.jpg",
        "assets/cover_240x240.png",
        "assets/icon_50x50.png",
        "metadata/pack.json",
        "metadata/meaning_words.csv",
        "metadata/填写信息.txt",
        "metadata/rights-ai-declaration.json",
        "qa/qa-report.json",
        "qa/qa-report.txt",
        "qa/SHA256SUMS.txt",
    }
    for path in (paths["run"] / "03-submission").rglob("*"):
        if path.is_symlink():
            errors.append(f"Submission contains a symlink: {path.relative_to(paths['run']).as_posix()}")
        elif path.is_file():
            relative = path.relative_to(paths["run"] / "03-submission").as_posix()
            if relative not in allowed_submission:
                errors.append(f"Unexpected file in submission tree: {relative}")

    manual = spec.get("manual_review", {})
    readiness_blockers: list[str] = []
    pending_manual = [key for key in MANUAL_REVIEW_KEYS if manual.get(key) is not True]
    if pending_manual:
        readiness_blockers.append("Manual review pending: " + ", ".join(pending_manual))
    if spec["pack"].get("rights_confirmed") is not True:
        readiness_blockers.append("Rights are not confirmed")
    if spec["pack"].get("portrait_use_confirmed") is not True:
        readiness_blockers.append("Portrait use is not confirmed")
    if spec.get("rules_status") != "official-current":
        readiness_blockers.append(
            f"Official platform rules are not supported for submission: {spec.get('rules_status')}"
        )

    integrity_errors = list(errors)
    if strict:
        errors.extend(readiness_blockers)
    else:
        warnings.extend(readiness_blockers)

    status = "ready-to-submit" if not integrity_errors and not readiness_blockers else "draft/not-ready"
    report = {
        "schema_version": 1,
        "status": status,
        "strict": strict,
        "checks": {
            "sticker_count": len(sticker_files),
            "expected_sticker_count": 20,
            "publication_assets": sorted(asset_specs),
            "original_count": len(state.get("originals", [])),
            "rules_status": spec.get("rules_status"),
            "python": sys.version.split()[0],
            "pillow": PILLOW_VERSION,
        },
        "integrity_errors": integrity_errors,
        "readiness_blockers": readiness_blockers,
        "errors": errors,
        "warnings": sorted(set(warnings)),
    }
    if write_report:
        paths["qa"].mkdir(parents=True, exist_ok=True)
        write_json(paths["qa"] / "qa-report.json", report)
        lines = [
            f"Status: {status}",
            f"Stickers: {len(sticker_files)}/20",
            f"Original references: {len(state.get('originals', []))}",
            f"Errors: {len(errors)}",
            f"Warnings: {len(report['warnings'])}",
            "",
            "FULL ARCHIVE PRIVACY",
            f"- {FULL_ARCHIVE_PRIVACY_WARNING}",
        ]
        if errors:
            lines.extend(["", "ERRORS"] + [f"- {item}" for item in errors])
        if report["warnings"]:
            lines.extend(["", "WARNINGS"] + [f"- {item}" for item in report["warnings"]])
        atomic_write(paths["qa"] / "qa-report.txt", ("\n".join(lines) + "\n").encode("utf-8"))
        hash_lines: list[str] = []
        for path in sorted((paths["run"] / "03-submission").rglob("*")):
            if path.is_file() and path.parent != paths["qa"]:
                hash_lines.append(f"{sha256_file(path)}  {path.relative_to(paths['run'] / '03-submission').as_posix()}")
        atomic_write(paths["qa"] / "SHA256SUMS.txt", ("\n".join(hash_lines) + "\n").encode("utf-8"))
    return report


def validate_command(args: argparse.Namespace) -> None:
    report = validate_run(args.run_dir, strict=args.strict, write_report=True)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errors"]:
        manual_only = all(error.startswith("Manual review pending:") for error in report["errors"])
        raise SystemExit(4 if manual_only else 3)


def deterministic_zip(destination: Path, entries: Iterable[tuple[str, bytes | Path]]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=str(destination.parent))
    os.close(fd)
    temp_path = Path(temp_name)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_STORED, allowZip64=True) as archive:
            for arcname, data in sorted(entries, key=lambda item: item[0].encode("utf-8")):
                info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                info.compress_type = zipfile.ZIP_STORED
                info.extra = b""
                info.comment = b""
                if isinstance(data, Path):
                    source = ensure_regular_input(data)
                    with source.open("rb") as input_handle, archive.open(info, "w") as output_handle:
                        shutil.copyfileobj(input_handle, output_handle, length=1024 * 1024)
                else:
                    archive.writestr(info, data)
        with temp_path.open("rb") as handle:
            os.fsync(handle.fileno())
        with zipfile.ZipFile(temp_path, "r") as archive:
            bad = archive.testzip()
            if bad:
                raise PackError(f"ZIP integrity failure: {bad}")
        os.replace(temp_path, destination)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def file_entries(root: Path, prefix: str = "", *, include_hidden: bool = False) -> list[tuple[str, bytes]]:
    if root.is_symlink() or not root.is_dir():
        raise PackError(f"Archive root must be a real directory: {root}")
    root_resolved = root.resolve()
    entries: list[tuple[str, bytes]] = []
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root)
        if not include_hidden and any(part.startswith(".") for part in relative_path.parts):
            continue
        if path.is_symlink():
            raise PackError(f"Archive source contains a symlink: {path}")
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(root_resolved)
        except ValueError as exc:
            raise PackError(f"Archive source escapes its root: {path}") from exc
        relative = relative_path.as_posix()
        entries.append((f"{prefix}{relative}", path.read_bytes()))
    return entries


def file_path_entries(
    root: Path, prefix: str = "", *, include_hidden: bool = False
) -> list[tuple[str, Path]]:
    if root.is_symlink() or not root.is_dir():
        raise PackError(f"Archive root must be a real directory: {root}")
    root_resolved = root.resolve()
    entries: list[tuple[str, Path]] = []
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root)
        if not include_hidden and any(part.startswith(".") for part in relative_path.parts):
            continue
        if path.is_symlink():
            raise PackError(f"Archive source contains a symlink: {path}")
        if not path.is_file():
            continue
        try:
            path.resolve().relative_to(root_resolved)
        except ValueError as exc:
            raise PackError(f"Archive source escapes its root: {path}") from exc
        entries.append((f"{prefix}{relative_path.as_posix()}", path))
    return entries


def submission_file_entries(paths: dict[str, Path]) -> list[tuple[str, bytes]]:
    relatives = [
        *(f"stickers/{item_id}.png" for item_id in EXPECTED_IDS),
        "assets/banner_750x400.jpg",
        "assets/cover_240x240.png",
        "assets/icon_50x50.png",
        "metadata/pack.json",
        "metadata/meaning_words.csv",
        "metadata/填写信息.txt",
        "metadata/rights-ai-declaration.json",
        "qa/qa-report.json",
        "qa/qa-report.txt",
        "qa/SHA256SUMS.txt",
    ]
    root = paths["run"] / "03-submission"
    entries: list[tuple[str, bytes]] = []
    for relative in relatives:
        path = safe_relative_path(root, relative)
        if not path.is_file() or path.is_symlink():
            raise PackError(f"Required submission file is missing or unsafe: {relative}")
        entries.append((f"submission/{relative}", path.read_bytes()))
    return entries


def build_export_manifest(paths: dict[str, Path]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    for top in ["00-reference-originals", "01-plan", "02-source-assets", "03-submission", "04-preview"]:
        root = paths["run"] / top
        if not root.exists():
            continue
        if root.is_symlink() or not root.is_dir():
            raise PackError(f"Manifest root must be a real directory: {root}")
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            if top != "00-reference-originals" and any(part.startswith(".") for part in relative.parts):
                continue
            if path.is_symlink():
                raise PackError(f"Manifest source contains a symlink: {path}")
            if path.is_file():
                files.append(
                    {
                        "path": path.relative_to(paths["run"]).as_posix(),
                        "size": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
    return {"schema_version": 1, "files": files}


def quarantine_submission_archive(paths: dict[str, Path], slug: str) -> Path | None:
    submission_zip = paths["archives"] / f"{slug}-submission.zip"
    if not submission_zip.exists():
        return None
    if submission_zip.is_symlink() or not submission_zip.is_file():
        raise PackError(f"Unsafe stale submission archive: {submission_zip}")
    stale_dir = paths["archives"] / "stale"
    if stale_dir.exists() and (stale_dir.is_symlink() or not stale_dir.is_dir()):
        raise PackError(f"Unsafe stale archive directory: {stale_dir}")
    stale_dir.mkdir(parents=True, exist_ok=True)
    stale = stale_dir / f"{slug}-submission-{sha256_file(submission_zip)[:12]}.zip"
    if stale.exists() and sha256_file(stale) != sha256_file(submission_zip):
        raise PackError(f"Stale archive destination collision: {stale}")
    if stale.exists():
        submission_zip.unlink()
    else:
        os.replace(submission_zip, stale)
    return stale


def package_command(args: argparse.Namespace) -> None:
    paths, spec, state = load_run(args.run_dir)
    report = validate_run(args.run_dir, strict=not args.full_only, write_report=True)
    slug = spec.get("pack", {}).get("slug")
    if not isinstance(slug, str) or not SLUG_RE.fullmatch(slug):
        raise PackError("Cannot package a run without a valid pack.slug")
    if report.get("integrity_errors") or (not args.full_only and report.get("readiness_blockers")):
        quarantine_submission_archive(paths, slug)
        failures = report.get("integrity_errors", []) + report.get("readiness_blockers", [])
        raise PackError("Validation failed; package was not created:\n- " + "\n- ".join(failures))

    export_manifest = build_export_manifest(paths)
    write_json(paths["run"] / "run-manifest.json", export_manifest)
    root_hashes = [
        f"{item['sha256']}  {item['path']}" for item in export_manifest["files"]
    ]
    atomic_write(paths["run"] / "SHA256SUMS.txt", ("\n".join(root_hashes) + "\n").encode("utf-8"))

    submission_zip = paths["archives"] / f"{slug}-submission.zip"
    full_zip = paths["archives"] / (
        f"{slug}-draft-full-archive.zip" if args.full_only else f"{slug}-full-archive.zip"
    )
    if args.full_only:
        quarantine_submission_archive(paths, slug)
    if not args.full_only:
        deterministic_zip(submission_zip, submission_file_entries(paths))

    full_entries: list[tuple[str, bytes | Path]] = []
    for top in [
        "00-reference-originals",
        "01-plan",
        "02-source-assets",
        "03-submission",
        "04-preview",
    ]:
        root = paths["run"] / top
        if root.exists():
            full_entries.extend(
                file_path_entries(root, f"{top}/", include_hidden=(top == "00-reference-originals"))
            )
    full_entries.append(("run-manifest.json", (paths["run"] / "run-manifest.json").read_bytes()))
    full_entries.append(("SHA256SUMS.txt", (paths["run"] / "SHA256SUMS.txt").read_bytes()))
    deterministic_zip(full_zip, full_entries)
    if not args.full_only:
        print(submission_zip)
    print(full_zip)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Initialize a run and preserve reference images")
    init.add_argument("--run-dir", type=Path, required=True)
    init.add_argument("--spec", type=Path, required=True)
    init.add_argument("--profile", type=Path)
    init.add_argument("--reference", type=Path, action="append", required=True)
    init.set_defaults(func=initialize_run)

    importer = subparsers.add_parser("import-art", help="Register generated artwork without modifying it")
    importer.add_argument("--run-dir", type=Path, required=True)
    importer.add_argument(
        "--kind",
        choices=["anchor", "sticker", "banner", "cover", "icon", "cover-chroma", "icon-chroma"],
        required=True,
    )
    importer.add_argument("--slot")
    importer.add_argument("--source", type=Path, required=True)
    importer.add_argument(
        "--generator",
        choices=["builtin-imagegen", "local-chroma-removal"],
        required=True,
    )
    importer.add_argument(
        "--prompt-file",
        type=Path,
        help="UTF-8 file containing the exact frozen prompt; required for built-in generation",
    )
    importer.add_argument(
        "--chroma-key",
        help="Exact #RRGGBB key used by local cover/icon background removal",
    )
    importer.add_argument(
        "--edge-contract",
        type=int,
        help="Edge contraction used by local chroma removal (0-3)",
    )
    importer.add_argument("--replace-slot", action="store_true")
    importer.set_defaults(func=import_art)

    render = subparsers.add_parser("render-stickers", help="Compose exact text and 240x240 sticker PNGs")
    render.add_argument("--run-dir", type=Path, required=True)
    render.set_defaults(func=render_stickers)

    prepare = subparsers.add_parser("prepare-assets", help="Build banner, cover, icon, and metadata")
    prepare.add_argument("--run-dir", type=Path, required=True)
    prepare.set_defaults(func=prepare_assets)

    sheet = subparsers.add_parser("contact-sheet", help="Create a review-only contact sheet")
    sheet.add_argument("--run-dir", type=Path, required=True)
    sheet.set_defaults(func=contact_sheet)

    validate = subparsers.add_parser("validate", help="Validate the complete run")
    validate.add_argument("--run-dir", type=Path, required=True)
    validate.add_argument("--strict", action="store_true")
    validate.set_defaults(func=validate_command)

    package = subparsers.add_parser("package", help="Create deterministic submission and full archives")
    package.add_argument("--run-dir", type=Path, required=True)
    package.add_argument(
        "--full-only",
        action="store_true",
        help="Create only a draft full archive even when strict submission gates are not ready",
    )
    package.set_defaults(func=package_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except PackError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
