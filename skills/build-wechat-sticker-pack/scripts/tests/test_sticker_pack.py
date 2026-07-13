from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw


SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))
import sticker_pack as sp  # noqa: E402


TEXTS = [
    "早安啦",
    "你好呀",
    "回头见",
    "晚安哦",
    "谢谢你",
    "对不起",
    "可以的",
    "真不错",
    "哈哈哈",
    "哇哦",
    "什么情况",
    "呜呜呜",
    "生气了",
    "好困呀",
    "开饭啦",
    "等一下",
    "记得哦",
    "加油呀",
    "可爱吗",
    "够酷吗",
]

MEANINGS = [
    "早安",
    "你好",
    "再见",
    "晚安",
    "感谢",
    "抱歉",
    "同意",
    "夸奖",
    "开心",
    "惊讶",
    "疑惑",
    "难过",
    "生气",
    "困了",
    "吃饭",
    "稍等",
    "提醒",
    "加油",
    "卖萌",
    "耍酷",
]


def make_spec() -> dict:
    stickers = []
    framings = ["close_up", "bust", "half_body", "full_body"]
    categories = ["greeting", "social", "reaction", "emotion"]
    for index in range(20):
        item_id = f"{index + 1:02d}"
        stickers.append(
            {
                "id": item_id,
                "intent_key": f"intent.{item_id}",
                "category": categories[index % len(categories)],
                "exact_text": TEXTS[index],
                "meaning_word": MEANINGS[index],
                "emotion": f"emotion-{item_id}",
                "pose_action": f"pose-{item_id}",
                "prop": f"prop-{item_id}" if index < 5 else None,
                "framing": framings[index % len(framings)],
                "text_zone": "bottom",
                "line_break": None,
                "art_prompt": f"Generate text-free sticker art for {item_id}.",
            }
        )
    return {
        "schema_version": 1,
        "platform_spec": "wechat-open-platform-test",
        "rules_status": "official-current",
        "rules_checked_at": "2026-07-13",
        "pack": {
            "slug": "test-pack",
            "name": "测试表情",
            "introduction": "用于验证全流程脚本的测试表情包。",
            "copyright": "黄家宝",
            "type": "静态表情",
            "category": "卡通表情/其他",
            "character": ["人物角色", "女人"],
            "styles": ["日常", "软萌可爱"],
            "theme": "万能通用",
            "download_region": "全球",
            "listing_region": "中国大陆",
            "price": "免费",
            "ai_generated": True,
            "rights_confirmed": True,
            "portrait_use_confirmed": True,
        },
        "character_bible": {"hair": "dark"},
        "style_bible": {"medium": "2d"},
        "avoid": ["logo", "watermark", "multi-panel layout"],
        "anchor_prompt": "Generate one text-free Q-version character anchor.",
        "render": {
            "background": "#FFFFFF",
            "master_size": 512,
            "font_path": None,
            "default_text": {
                "position": "bottom",
                "box": [12, 166, 228, 234],
                "max_lines": 2,
                "min_font_size": 20,
                "max_font_size": 42,
                "fill": "#3A2416",
                "stroke_fill": "#FFD979",
                "stroke_width": 2,
            },
        },
        "stickers": stickers,
        "assets": {
            "banner_prompt": "banner",
            "cover_prompt": "cover",
            "icon_prompt": "icon",
        },
        "manual_review": {key: True for key in sp.MANUAL_REVIEW_KEYS},
    }


class StickerPackTests(unittest.TestCase):
    def test_spec_requires_exactly_twenty(self) -> None:
        spec = make_spec()
        spec["stickers"].pop()
        errors = sp.validate_spec(spec)
        self.assertTrue(any("exactly 20" in error for error in errors))

    def test_layout_rejects_unreadable_text(self) -> None:
        spec = make_spec()
        font_path = sp.find_font(spec)
        image = Image.new("RGB", (100, 100), "white")
        draw = ImageDraw.Draw(image)
        with self.assertRaises(sp.PackError):
            sp.fit_text_layout(
                draw,
                "这是一个无法装入极小文本框的超长句子",
                font_path,
                (0, 0, 8, 8),
                20,
                30,
                2,
                2,
                None,
            )

    def test_profile_never_autoconfirms_rights(self) -> None:
        spec = make_spec()
        del spec["pack"]["rights_confirmed"]
        del spec["pack"]["portrait_use_confirmed"]
        profile = sp.load_json(sp.DEFAULT_PROFILE)
        merged = sp.merge_profile_defaults(spec, profile)
        self.assertNotIn("rights_confirmed", merged["pack"])
        self.assertNotIn("portrait_use_confirmed", merged["pack"])
        errors = sp.validate_spec(merged)
        self.assertTrue(any("rights_confirmed" in error for error in errors))
        self.assertTrue(any("portrait_use_confirmed" in error for error in errors))

    def test_spec_rejects_invisible_text(self) -> None:
        spec = make_spec()
        spec["stickers"][0]["exact_text"] = "早\u200b安"
        errors = sp.validate_spec(spec)
        self.assertTrue(any("U+200B" in error for error in errors))

    def test_spec_rejects_excess_punctuation_and_missing_render(self) -> None:
        punctuated = make_spec()
        punctuated["stickers"][0]["exact_text"] = "哈！！！！"
        errors = sp.validate_spec(punctuated)
        self.assertTrue(any("at most three punctuation" in error for error in errors))

        malformed = make_spec()
        del malformed["render"]
        errors = sp.validate_spec(malformed)
        self.assertTrue(any("render must be an object" in error for error in errors))

    def test_changed_platform_rules_block_generation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            reference = root / "reference.png"
            Image.new("RGB", (320, 400), "#DDAA88").save(reference, format="PNG")
            spec = make_spec()
            spec["rules_status"] = "changed-unsupported"
            spec["rules_change_details"] = ["Sticker dimension changed in current official rules"]
            spec_path = root / "spec.json"
            spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            run_dir = root / "run"
            sp.initialize_run(
                argparse.Namespace(run_dir=run_dir, spec=spec_path, profile=None, reference=[reference])
            )
            anchor = root / "anchor.png"
            Image.new("RGB", (640, 640), "#EEEEEE").save(anchor, format="PNG")
            prompt = root / "anchor-prompt.txt"
            prompt.write_text(spec["anchor_prompt"] + "\n", encoding="utf-8")
            with self.assertRaises(sp.PackError):
                sp.import_art(
                    argparse.Namespace(
                        run_dir=run_dir,
                        kind="anchor",
                        slot=None,
                        source=anchor,
                        generator="builtin-imagegen",
                        prompt_file=prompt,
                        replace_slot=False,
                    )
                )

    def test_draft_full_archive_preserves_hidden_original_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            reference = root / ".portrait.png"
            Image.new("RGB", (320, 400), "#DDAA88").save(reference, format="PNG")
            original_bytes = reference.read_bytes()
            spec_path = root / "spec.json"
            spec_path.write_text(json.dumps(make_spec(), ensure_ascii=False), encoding="utf-8")
            run_dir = root / "run"
            sp.initialize_run(
                argparse.Namespace(run_dir=run_dir, spec=spec_path, profile=None, reference=[reference])
            )
            archive_path = root / "hidden-original.zip"
            entries = sp.file_entries(
                run_dir / "00-reference-originals",
                "00-reference-originals/",
                include_hidden=True,
            )
            sp.deterministic_zip(archive_path, entries)
            with zipfile.ZipFile(archive_path) as archive:
                archived = archive.read("00-reference-originals/01/.portrait.png")
            self.assertEqual(archived, original_bytes)

    def test_symlinked_source_root_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            reference = root / "reference.png"
            Image.new("RGB", (320, 400), "#DDAA88").save(reference, format="PNG")
            spec_path = root / "spec.json"
            spec_path.write_text(json.dumps(make_spec(), ensure_ascii=False), encoding="utf-8")
            run_dir = root / "run"
            sp.initialize_run(
                argparse.Namespace(run_dir=run_dir, spec=spec_path, profile=None, reference=[reference])
            )
            source = run_dir / "02-source-assets"
            backup = root / "source-backup"
            source.rename(backup)
            source.symlink_to(backup, target_is_directory=True)
            with self.assertRaises(sp.PackError):
                sp.load_run(run_dir)

    def test_full_pipeline_preserves_originals_and_builds_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            reference = root / "reference.png"
            reference_image = Image.new("RGB", (320, 400), "#DDAA88")
            reference_image.save(reference, format="PNG")
            reference_bytes = reference.read_bytes()
            reference_hash = hashlib.sha256(reference_bytes).hexdigest()

            spec_path = root / "spec.json"
            spec_path.write_text(json.dumps(make_spec(), ensure_ascii=False), encoding="utf-8")
            run_dir = root / "run"
            sp.initialize_run(
                argparse.Namespace(
                    run_dir=run_dir,
                    spec=spec_path,
                    profile=None,
                    reference=[reference],
                )
            )
            archived_reference = run_dir / "00-reference-originals" / "01" / "reference.png"
            self.assertEqual(archived_reference.read_bytes(), reference_bytes)
            self.assertEqual(sp.sha256_file(archived_reference), reference_hash)

            spec = make_spec()

            def prompt_file(name: str, content: str) -> Path:
                path = root / f"{name}.txt"
                path.write_text(content + "\n", encoding="utf-8")
                return path

            anchor = root / "anchor.png"
            Image.new("RGB", (640, 640), "#EEEEEE").save(anchor, format="PNG")
            sp.import_art(
                argparse.Namespace(
                    run_dir=run_dir,
                    kind="anchor",
                    slot=None,
                    source=anchor,
                    generator="builtin-imagegen",
                    prompt_file=prompt_file("anchor-prompt", spec["anchor_prompt"]),
                    replace_slot=False,
                )
            )

            for index, item_id in enumerate(sp.EXPECTED_IDS):
                art_path = root / f"art-{item_id}.png"
                color = ((40 + index * 9) % 220, (80 + index * 13) % 220, (120 + index * 17) % 220)
                art = Image.new("RGB", (640, 640), "white")
                draw = ImageDraw.Draw(art)
                draw.ellipse((160, 50, 480, 370), fill=color, outline="#332211", width=8)
                draw.rectangle((220, 320, 420, 480), fill=color, outline="#332211", width=8)
                art.save(art_path, format="PNG")
                sp.import_art(
                    argparse.Namespace(
                        run_dir=run_dir,
                        kind="sticker",
                        slot=item_id,
                        source=art_path,
                        generator="builtin-imagegen",
                        prompt_file=prompt_file(f"sticker-{item_id}-prompt", spec["stickers"][index]["art_prompt"]),
                        replace_slot=False,
                    )
                )

            banner = root / "banner.png"
            Image.new("RGB", (1500, 800), "#EE8866").save(banner, format="PNG")
            sp.import_art(
                argparse.Namespace(
                    run_dir=run_dir,
                    kind="banner",
                    slot=None,
                    source=banner,
                    generator="builtin-imagegen",
                    prompt_file=prompt_file("banner-prompt", spec["assets"]["banner_prompt"]),
                    replace_slot=False,
                )
            )

            for kind in ("cover", "icon"):
                chroma_path = root / f"{kind}-chroma.png"
                Image.new("RGB", (640, 640), "#00FF00").save(chroma_path, format="PNG")
                sp.import_art(
                    argparse.Namespace(
                        run_dir=run_dir,
                        kind=f"{kind}-chroma",
                        slot=None,
                        source=chroma_path,
                        generator="builtin-imagegen",
                        prompt_file=prompt_file(f"{kind}-prompt", spec["assets"][f"{kind}_prompt"]),
                        replace_slot=False,
                    )
                )
                path = root / f"{kind}.png"
                alpha = Image.new("RGBA", (640, 640), (0, 0, 0, 0))
                draw = ImageDraw.Draw(alpha)
                draw.ellipse((80, 40, 560, 600), fill=(120, 80, 60, 255))
                alpha.save(path, format="PNG")
                sp.import_art(
                    argparse.Namespace(
                        run_dir=run_dir,
                        kind=kind,
                        slot=None,
                        source=path,
                        generator="local-chroma-removal",
                        prompt_file=None,
                        chroma_key="#00ff00",
                        edge_contract=0,
                        replace_slot=False,
                    )
                )

            sp.render_stickers(argparse.Namespace(run_dir=run_dir))
            sp.prepare_assets(argparse.Namespace(run_dir=run_dir))
            sp.contact_sheet(argparse.Namespace(run_dir=run_dir))
            reviewed_spec = sp.load_json(run_dir / "01-plan" / "pack.json")
            reviewed_spec["manual_review"] = {key: True for key in sp.MANUAL_REVIEW_KEYS}
            sp.write_json(run_dir / "01-plan" / "pack.json", reviewed_spec)
            report = sp.validate_run(run_dir, strict=True, write_report=True)
            self.assertEqual(report["status"], "ready-to-submit")
            self.assertEqual(report["errors"], [])

            sp.package_command(argparse.Namespace(run_dir=run_dir, full_only=False))
            submission_zip = run_dir / "archives" / "test-pack-submission.zip"
            full_zip = run_dir / "archives" / "test-pack-full-archive.zip"
            self.assertTrue(submission_zip.is_file())
            self.assertTrue(full_zip.is_file())

            first_submission_hash = sp.sha256_file(submission_zip)
            first_full_hash = sp.sha256_file(full_zip)
            sp.package_command(argparse.Namespace(run_dir=run_dir, full_only=False))
            self.assertEqual(first_submission_hash, sp.sha256_file(submission_zip))
            self.assertEqual(first_full_hash, sp.sha256_file(full_zip))

            with zipfile.ZipFile(submission_zip) as archive:
                names = archive.namelist()
                self.assertIn("submission/stickers/01.png", names)
                self.assertFalse(any("reference" in name for name in names))
                self.assertFalse(any(name.startswith("00-reference-originals/") for name in names))
                self.assertFalse(any("prompt" in name for name in names))
            with zipfile.ZipFile(full_zip) as archive:
                names = archive.namelist()
                self.assertTrue(any(name.startswith("00-reference-originals/") for name in names))
                self.assertIn("03-submission/stickers/20.png", names)
                self.assertIn("02-source-assets/provenance/generation-ledger.json", names)
                self.assertNotIn("state.json", names)

            with Image.open(run_dir / "03-submission" / "assets" / "cover_240x240.png") as image:
                self.assertEqual(image.size, (240, 240))
                self.assertEqual(image.mode, "RGBA")
            with Image.open(run_dir / "03-submission" / "assets" / "icon_50x50.png") as image:
                self.assertEqual(image.size, (50, 50))
                self.assertEqual(image.mode, "RGBA")

            extra = run_dir / "03-submission" / ".env"
            extra.write_text("SECRET=not-for-upload", encoding="utf-8")
            extra_report = sp.validate_run(run_dir, strict=True, write_report=True)
            self.assertTrue(any("Unexpected file" in error for error in extra_report["errors"]))
            extra.unlink()

            current_spec = sp.load_json(run_dir / "01-plan" / "pack.json")
            current_spec["pack"]["rights_confirmed"] = False
            sp.write_json(run_dir / "01-plan" / "pack.json", current_spec)
            sp.prepare_assets(argparse.Namespace(run_dir=run_dir))
            draft_report = sp.validate_run(run_dir, strict=False, write_report=True)
            self.assertEqual(draft_report["status"], "draft/not-ready")
            self.assertEqual(draft_report["integrity_errors"], [])
            self.assertTrue(any("Rights are not confirmed" in item for item in draft_report["readiness_blockers"]))
            with self.assertRaises(sp.PackError):
                sp.package_command(argparse.Namespace(run_dir=run_dir, full_only=False))
            self.assertFalse(submission_zip.exists())
            sp.package_command(argparse.Namespace(run_dir=run_dir, full_only=True))
            self.assertFalse(submission_zip.exists())
            self.assertTrue(full_zip.exists())
            self.assertTrue((run_dir / "archives" / "test-pack-draft-full-archive.zip").is_file())
            self.assertEqual(len(list((run_dir / "archives" / "stale").glob("test-pack-submission-*.zip"))), 1)

            current_spec["pack"]["rights_confirmed"] = True
            current_spec["stickers"][0]["exact_text"] = "文字已改"
            sp.write_json(run_dir / "01-plan" / "pack.json", current_spec)
            stale_report = sp.validate_run(run_dir, strict=True, write_report=True)
            self.assertTrue(any("Receipt text is stale" in error for error in stale_report["errors"]))


if __name__ == "__main__":
    unittest.main()
