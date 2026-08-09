# Feature switches and character coverage

Read this file completely at the beginning of every personal-IP task.

## Default configuration

All features default to enabled. This complete default applies whenever the user does not deliberately provide a `功能开关` block or an unambiguous enable/disable instruction. Accept this YAML-like block:

```yaml
功能开关:
  经典主题组: 开
  随机主题组: 开
  浅色主题组: 开
  行业全身IP组: 开
  机构品牌主题组: 开
  基础动作设计: 开
  正面全身照: 开
  八角度角色照: 开
  全面情绪包: 开
  分组拼图: 开
  全部图片拼图: 开
随机主题数量: 8
浅色主题数量: 2
行业全身数量: 8
机构品牌主题数量: 0
喜欢的主题色: []
机构或高校VI资料: []
```

Map these labels to canonical keys:

| User-facing switch | Canonical key | Default | Originals per series |
|---|---|---:|---:|
| 经典主题组 | `classic_series` | on | creates one series |
| 随机主题组 | `random_theme_series` | on | creates `random_theme_count` series |
| 浅色主题组 | `light_theme_series` | on | creates `light_theme_count` new light series |
| 行业全身IP组 | `industry_full_body_pack` | on | creates `industry_count` standalone originals |
| 机构品牌主题组 | `brand_theme_series` | on | data-dependent; creates `brand_theme_count` complete series |
| 基础动作设计 | `base_designs` | on | 8 |
| 正面全身照 | `front_full_body` | on | 1 |
| 八角度角色照 | `angle_views` | on | 8 |
| 全面情绪包 | `emotion_pack` | on | 24 |
| 分组拼图 | `series_collages` | on | overview only |
| 全部图片拼图 | `all_images_collage` | on | overview only |

Every item in `喜欢的主题色` creates one appended series. A deliberately grouped phrase such as `蓝粉撞色` is one theme; separately listed colors are separate themes. User themes are additions and never replace the random themes.

`机构品牌主题组` is enabled but data-dependent. With no named brand, institution, official VI URL, or supplied manual, resolve `brand_theme_count=0`; never apply a specific organization's identity to every user. When the user supplies one official VI system and does not choose a count, resolve `brand_theme_count=8`. Each brand series receives all enabled per-series modules.

Apply this resolution order:

1. If there is no explicit feature-control intent, enable every switch with `random_theme_count=8`, `light_theme_count=2`, `industry_count=8`, and data-dependent `brand_theme_count`. Do not infer disabled modules from a short request or from modules the user did not mention.
2. A `功能开关` block activates control mode. Apply stated values and preserve `on` for every omitted key.
3. An unambiguous natural-language command such as “关闭情绪包” or “只要全身和角度” also activates control mode. In a “只要” request, disable unmentioned image-generation modules while keeping QA enabled; keep collage switches on unless explicitly disabled.
4. Statements about style, quantity, color preference, or desired output are not feature-control intent unless they explicitly enable, disable, include-only, or exclude a module.

At least one complete series with one per-series image module, or the standalone industry full-body pack, must remain enabled. `FEATURES.json` must contain the fully resolved canonical configuration.

## Count formula

Let:

- `S = classic_series + random_theme_count + light_theme_count + user_theme_count + brand_theme_count`, counting only enabled series
- `P = 8×base_designs + 1×front_full_body + 8×angle_views + 24×emotion_pack`
- `I = industry_count` when `industry_full_body_pack` is on, otherwise `0`

Then `delivered originals = S × P + I`.

Default without a brand/institution input: `S=11`, `P=41`, `I=8`, total `459`. One supplied official VI system defaults to eight added complete series: `19×41+8=787`. Each ordinary preferred-color theme adds 41 when all modules are on.

Run the deterministic count calculator before generation:

```bash
python3 scripts/calculate_feature_plan.py \
  --classic on \
  --random-count 8 \
  --light-count 2 \
  --user-theme-count 0 \
  --brand-theme-count 0 \
  --industry-full-body-pack on \
  --industry-count 8 \
  --base-designs on \
  --front-full-body on \
  --angle-views on \
  --emotion-pack on
```

Add `--existing-original-count N` for expansion of a frozen collection. `--existing-classic` remains available for the older classic-eight workflow.

## Eight angle views

Generate eight separate square, neutral head-to-toe turnaround images per series. Keep camera height, body scale, stance, hairstyle, outfit, palette, proportions, and expression fixed. Change only viewpoint:

1. `01-front` — direct front, 0°
2. `02-front-left-three-quarter` — character turns 45° toward screen left
3. `03-left-profile` — character's left profile, 90°
4. `04-back-left-three-quarter` — 135°, back of hair and left shoulder visible
5. `05-back` — direct back, 180°, no face visible
6. `06-back-right-three-quarter` — 225°, back of hair and right shoulder visible
7. `07-right-profile` — character's right profile, 270°
8. `08-front-right-three-quarter` — 315°

Do not mirror a finished image as a substitute. Preserve asymmetrical hair, clothing, and accessories correctly around the body. Keep the full hairstyle, hands, legs, and shoes inside every frame; use a neutral stance without a large prop so the silhouette remains readable from all directions.

## Front-facing full-body image

Generate one polished hero-style square image named `01-front-full-body.png` per series. It is distinct from the technical neutral front image in the angle module:

- centered, direct front, head-to-toe, entire shoes visible
- relaxed natural or signature stance with arms separated enough to read the torso silhouette
- five readable fingers when visible
- same canonical hairstyle, face, outfit, palette, and visual proportions as the series
- simple sparse doodles that do not cover the silhouette
- no crop at hair, elbows, hands, knees, or feet

## Comprehensive 24-emotion pack

“Every character” means the canonical IP character in every enabled theme series. Do not multiply the emotion pack by each of the eight action-design images.

Generate 24 separate square head-and-shoulders images per series, named and ordered exactly as follows:

1. `01-neutral` — neutral attentive face
2. `02-calm` — peaceful, relaxed
3. `03-happy` — warm smile
4. `04-laughing` — open joyful laugh
5. `05-excited` — sparkling energetic delight
6. `06-proud` — confident satisfaction
7. `07-grateful` — touched and appreciative
8. `08-relieved` — tension released
9. `09-curious` — inquisitive interest
10. `10-focused` — concentrated attention
11. `11-determined` — firm resolve
12. `12-surprised` — sudden wide-eyed surprise
13. `13-confused` — puzzled uncertainty
14. `14-shy` — bashful reserve
15. `15-embarrassed` — awkward flushed discomfort
16. `16-worried` — anxious concern
17. `17-afraid` — readable fear without horror
18. `18-sad` — downcast sadness
19. `19-crying` — visible tears, still gentle and non-graphic
20. `20-angry` — controlled anger
21. `21-annoyed` — irritated impatience
22. `22-disgusted` — mild aversion, non-grotesque
23. `23-tired` — sleepy exhaustion
24. `24-bored` — low-energy disinterest

Expression must come primarily from brows, eye openness/direction, mouth shape, cheek marks, and small doodle accents. Keep face geometry, hair, outfit, crop, palette, line quality, and background fixed. Small hands may appear only when essential; props must not distract from the face.

## Output structure

Use a numbered folder per enabled series:

```text
00-classic/
  01-designs/                 # 8 originals when enabled
  02-front-full-body/         # 1 original when enabled
  03-angle-views/             # 8 originals when enabled
  04-emotions/                # 24 originals when enabled
  00-series-overview.png      # when enabled
01-<random-theme>/
...
09-<user-theme>/
industry-full-body/
20-<brand-or-institution-theme>/
00-all-images-overview.png    # every delivered original exactly once
FEATURES.json
PROMPTS.md
QA.md
```

In expansion mode, keep existing classic files in place and create `00-classic-extensions/` for new full-body, angle, or emotion originals. Include the unchanged classic originals in the all-images collage only when `classic_series` and `all_images_collage` are enabled.

## Shared prompt locks

For angle and emotion calls, explicitly state:

```text
This is the same canonical character and same theme as the approved series anchor. Preserve face geometry, age range, hairstyle length and silhouette, outfit construction, accessory placement, palette hex roles, crayon pressure, white cutout edge, crop rules, and body proportions. Change only the requested viewpoint or emotion. One square deliverable image, never a grid or model sheet. No text or labels inside the image.
```

For each angle call, also add:

```text
Technical full-body turnaround view at <ANGLE>. Keep the entire head-to-toe body and shoes inside the square, with the same neutral stance, camera height, body scale, and outfit construction as the other views. No large prop. Do not mirror another finished view.
```

For the front full-body call, add:

```text
Polished direct front-facing head-to-toe hero view. Entire hairstyle, hands, legs, and shoes are inside the square. Relaxed natural or signature stance, no perspective distortion, no seated pose, and no large prop blocking the body.
```
