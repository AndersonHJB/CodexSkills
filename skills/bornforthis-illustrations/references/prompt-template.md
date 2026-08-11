# Bornforthis 标准生图 Prompt

每张图片单独生成，并同时传入 `assets/references/face-anchor.png` 与 `assets/references/fullbody-anchor.png`。

## 变量

- `{主题}`：唯一核心概念。
- `{核心动作}`：Bornforthis 亲手执行的动作。
- `{主结构}`：一个路径、机器、桥、分流、闭环或其它单一隐喻。
- `{服装}`：随场景变化的成年创作者服装。
- `{配饰策略}`：无配饰，或本图必要的一件情境配饰。
- `{内容辅助色}`：按真实物体或信息语义加入的颜色及其用途。
- `{短标签}`：2–5 个短标签，或无文字。

## 模板

```text
Use case: infographic-diagram
Asset type: 16:9 horizontal illustration inside a premium Chinese article
Primary request: create one standalone illustration about “{主题}”.

INPUT IMAGES
- Image 1 is the Bornforthis face reference. Lock the compact square-round paper-white face, short upward blue fringe, straight blue brows, simple blue eyes, tiny yellow dot nose, two round yellow cheek patches and warm closed-mouth smile.
- Image 2 is the Bornforthis full-body reference. Lock adult proportions, natural gesture, irregular white sticker/cut-paper edge and hand-drawn wax-crayon finish.
- Do not inherit the yellow background, headphones, blue jacket, camera, camera bag or notebook from the references unless the current scene explicitly needs them.

IDENTITY LOCK — NEVER CHANGE
- Bornforthis is a friendly young adult male, around 4.5–5 heads tall, not a child or chibi mascot.
- Fixed traits: paper-white square-round face; short upward #2B7FD8 blue hair; blue brows and simple blue eyes; tiny #F4D758 yellow dot nose; two conspicuous round #F4D758 yellow cheek patches; gentle closed-mouth smile.
- One-word recognition anchor: “黄腮红”. Supporting chain: blue spiky fringe + white face + yellow cheeks.
- Preserve the irregular white sticker/cut-paper margin. Never let clothing or props obscure the face.

SCENE
- Core action: {核心动作}.
- Main structure: {主结构}.
- Clothing: {服装}. Clothing is contextual and must not become a permanent blue-jacket uniform.
- Accessory policy: {配饰策略}. Use no accessory by default.
- Bornforthis must physically perform the central action, not stand in a corner.

STYLE DNA
- Pure clean #FFFFFF white background, generous whitespace, no yellow full background and no environmental scene.
- 2D hand-drawn wax crayon plus colored pencil: visible paper grain inside strokes, broken hatching, uneven pressure, tiny white gaps and imperfect edges.
- Cute but premium, warm, human-made, unmistakably Bornforthis, never slick AI vector art.
- Brand-blue main outlines; flat paper-sticker/cutout feeling without cast shadows.

COLOR SYSTEM — OPEN PALETTE
- Brand identity colors: blue #2B7FD8, yellow #F4D758 and red #E84A5F.
- Among the three brand colors, target the visual hierarchy blue 60% / yellow 30% / red 10%. This is not a ban on other colors and not a rigid pixel histogram. Exclude the white background.
- Use blue for hair, main outlines, main structure and title/link semantics; yellow for cheeks, highlights and emphasis; red for CTA, warnings, labels and turning points.
- Add context colors when semantically or materially justified: {内容辅助色}.
- Render context colors with the same warm crayon texture. Keep them connected to actual content; avoid arbitrary rainbow clutter, neon colors or a competing dominant palette.

COMPOSITION AND TEXT
- Use one visual metaphor, a clear reading order, character height around 38%–58% and ample white safe margins.
- Short labels: {短标签}.
- Use Huiwen Mincho character for required Chinese titles, Fraunces for English decoration, Caveat for handwritten Latin annotations with matching loose handwritten Chinese notes, and Fira Code for code or terminal text.
- If exact text cannot be rendered, leave clean blank label tabs instead of gibberish. Do not create long text.

FORBIDDEN
- no Xiaohei, black blob mascot, black silhouette or substitute protagonist
- no permanent headphones, permanent blue jacket, forced camera, camera bag or notebook
- no yellow full background and no rule restricting the scene to only three colors
- no meaningless rainbow, neon palette or auxiliary color overpowering brand blue
- no black primary outlines, photorealism, 3D, plastic toy, glossy vector, anime, chibi or baby proportions
- no giant shiny eyes, skin-tone face fill, beard, random hat, glasses, jewelry, logo, watermark or signature
- no gradients, heavy shadows, complex background, dense infographic, long text or gibberish

OUTPUT
- one finished 16:9 illustration, pure white background, visibly handmade and suitable for a premium Bornforthis article.
```

## 精确字体流程

当字体文件级准确性是硬要求时，把 `{短标签}` 改成“无文字，为后期文字保留空白标签位”。生成底图后再用真实的汇文明朝体、Fraunces、Caveat 和 Fira Code 进行确定性排版。

## 局部编辑模板

只移除错误标题：

```text
Edit the provided image. Remove only the text “{要删除的文字}” and its underline or label container. Fill that area with clean #FFFFFF white background. Preserve Bornforthis identity, all other labels, composition, open-palette color roles, crayon texture, aspect ratio and image quality. Do not add new text or objects.
```

修复角色身份：

```text
Edit only the Bornforthis character to restore the fixed identity from the two reference images: short upward #2B7FD8 blue hair, paper-white square-round face, tiny yellow dot nose and two round yellow cheek patches. Preserve the scene, action, clothing choice, contextual accessories, content colors, labels and composition exactly.
```
