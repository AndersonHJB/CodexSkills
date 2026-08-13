# 生图提示词模板

每张图单独生成，不要拼图。每次新生成必须同时传入：

- `assets/references/bornforthis-ref-1.png`
- `assets/references/bornforthis-ref-2.png`

用以下模板替换变量。角色身份块必须位于提示词最前面。

```text
IP Character Bornforthis (HIGHEST PRIORITY — preserve the same identity in both reference images):
- A youthful adult male personal-IP character, not a child, with a compact roughly 3.5–4-head-tall illustrated body; keep the full-body reference's compact silhouette and do not elongate the limbs.
- Large rounded-square paper-white face: broad forehead, rounded cheeks, lower face tapering only slightly; never a pointed chin or realistic skin rendering.
- Thick saturated cobalt-blue short spiky hair, base around #1262D5 with darker #0D55B2 strokes; irregular upward tufts on top, much shorter faded sides, jagged natural front hairline; never long, curly, black, grey, or washed out.
- Two conspicuous outward-projecting semicircular ears, both visible, each with one simple C-shaped inner line.
- Two short cobalt-blue eyebrows; small cobalt-blue dot/oval eyes with one simple curved upper-eyelid stroke; no giant anime eyes and no realistic sclera-pupil construction.
- One tiny bright-yellow nose dot and two symmetrical flat, perfectly round golden-yellow cheek circles around #FCD40B; never pink or gradient blush.
- One short cobalt-blue single-line mouth, with a quiet, friendly, confident closed smile by default; no beard, glasses, realistic lips, or detailed nose.
- Keep these identity traits exact even when pose, expression, clothing, accessories, and props change.

Reference interpretation rule (CRITICAL):
The two attached images are identity references only. Do NOT copy their yellow background, white sticker border, headphones, yellow top, blue-yellow jacket, white T-shirt, beige baggy pants, sneakers, camera, bag, notebook, thumbs-up pose, or surrounding code/music/photo/book symbols. Clothing and accessories are NOT fixed character features. Redesign the outfit for this scene and add an accessory only when it conveys meaning.

Generate one standalone 16:9 horizontal Chinese article illustration.

Visual style (match the target style exactly):
- Pure clean white background.
- Warm crayon/marker texture fills; every colored area has visible natural diagonal hatching strokes, never flat solid fills.
- Thick dark-navy-blue outlines around 2–3px with a slightly wobbly hand-drawn line.
- Warm, clean, hand-colored picture-book feeling: charming but not childish, slightly absurd, never polished commercial art.
- Main subject occupies about 40%–60% of the canvas, with at least 35% empty white space.
- Use a restrained 4–5-color palette based on cobalt blue, dark navy, bright yellow, red/coral, orange, and paper white. Clothing colors vary with the scene.

Theme:
{正文配图主题}

Structure type:
{Workflow / 系统局部 / 前后对比 / 角色状态 / 概念隐喻 / 方法分层 / 地图路线 / 小漫画分镜}

Core idea:
{这张图只需要表达的一个核心意思}

Scene-specific wardrobe:
{根据动作设计的简单服装；无特殊语义时明确写“simple scene-appropriate outfit, no headphones or camera”}

Composition:
{Bornforthis 在哪里、正在做什么、主物件是什么、信息如何流动}

Suggested elements:
{元素1} / {元素2} / {元素3} / {可选元素4}

Chinese handwritten labels:
{标注词1} / {标注词2} / {标注词3} / {可选标注词4}

Constraints:
Bornforthis must perform the core conceptual action rather than decorate the scene. One concept per image. Keep the background simpler than the character if necessary. Use at most 5–8 short handwritten Chinese labels, each ideally 2–8 characters. Use blue for normal notes and red for warnings/key results; reserve orange mainly for paths and arrows. No top-left title, no structure-type label, no PPT or course-slide look, no formal flowchart, no grid-heavy layout, no gradients, no shadows, no paper texture, no yellow full-canvas background, no white sticker cutout, no 3D, no commercial vector style, no realistic UI. Invent a fresh metaphor for this article and do not replicate either reference composition.
```

## 关键注意

- **两张参考图缺一不可**：在一个 `image_gen` 调用的 `referenced_image_paths` 中同时传入两张，不要只传一张。
- **参考的是身份，不是造型**：耳机和所有服饰、配饰、道具均按当次主题决定。
- **人物描述必须最先出现**：角色身份优先级高于场景；背景可以简化，角色不能崩。
- **纹理是核心**：如果出现纯色平涂，重生成并强调 `visible crayon/marker diagonal hatching strokes in every color fill`。
- **白底是核心**：参考图的黄色背景不能进入最终图。

## 图像编辑提示

去掉左上角标题：

```text
Edit the provided image. Remove only the handwritten title "{要删除的文字}" and its underline from the top-left corner. Fill that area with the same clean pure-white background. Preserve everything else exactly: Bornforthis, clothing, objects, labels, paths, line work, crayon hatching, composition, aspect ratio, and image quality. Do not add any text or objects.
```

让角色承担核心动作：

```text
Regenerate the illustration with the same core meaning and sparse layout, but make Bornforthis perform the strange physical action that explains the concept instead of standing beside the diagram. Preserve his exact cobalt short-spiky hair, outward round ears, paper-white rounded-square face, yellow circular cheeks, minimal blue facial features, youthful-adult proportions, and the current scene-appropriate outfit. Keep the white background, textured crayon fills, navy wobbly outlines, and short Chinese labels.
```

修复身份漂移：编辑目标图时把目标图和两张固定身份参考图一并传入，并使用：

```text
Edit only Bornforthis to restore his canonical identity from the two identity references: cobalt-blue short spiky hair with short sides, both outward round ears visible, paper-white rounded-square face, two flat yellow circle cheeks, tiny yellow nose dot, small blue eyes and brows, and a simple blue single-line mouth. Preserve the target image's current scene-specific clothing, pose, props, background, composition, text, and crayon style. Do not copy clothing, accessories, yellow background, or poses from the identity references.
```
