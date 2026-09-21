# Style locks（4 类 · 已确认）

每个 style_lock = style_ref + style_prompt_lock + style_negative_lock。  
仅在生成角色标准正面图时使用对应 `style_refs/<id>/style-ref.webp`，用它传递材质、线条与渲染方式；不得复制参考图中的角色形态、五官、服装、配色、道具或构图。角色标准正面图通过后，下游生成优先使用 Pack 的 `character-reference-board.png`，不要继续混入 style ref。  
备注：搪胶身上叠手绘纹 ≠ 独立画风。

---

## 1 · 治愈绘本手绘（impasto / gouache grain）

目录：`style_refs/01-impasto-gouache/`

**style_prompt_lock**
```
thick gouache / acrylic illustration on fine canvas grain, soft painterly layered paint,
visible paper/canvas tooth, matte hand-painted look (NOT waxy crayon sticks, NOT fine pencil hatching),
bold soft dark outlines, large simple eyes, gentle blush, limited warm palette,
flat-ish color with soft paint texture, chibi-friendly proportions, plain light background,
content-illustration ready, cozy modern character art
```

**style_negative_lock**
```
chunky wax crayon sticks, broken crayon edges, fine colored-pencil cross-hatching,
3D vinyl toy, glossy plastic, photorealistic, oil-slick anime cel, complex scenery,
nine-grid, collage, watermark, UI text, midjourney label, flocked plush fur
```

---

## 2 · 极简符号卡通（flat symbol mascot）

目录：`style_refs/02-flat-symbol/`

**style_prompt_lock**
```
ultra-minimal flat mascot, solid color blocks only, almost no gradients,
logo-like silhouette, thick simple shapes, tiny facial dots, one accent prop carrier,
high contrast, plain white background, sticker-ready graphic character,
readable at thumbnail size
```

**style_negative_lock**
```
painterly texture, crayon, canvas grain, 3D render, soft vinyl highlights, fabric weave,
complex clothing folds, photorealistic, busy background, nine-grid, watermark, flocked plush
```

---

## 3 · 盲盒潮玩公仔（matte soft vinyl）

目录：`style_refs/03-matte-vinyl/`

**style_prompt_lock**
```
matte soft-vinyl designer toy / blind-box figure, smooth rounded plastic shell,
subtle soft specular only, collectible designer-toy finish, chibi oversized head,
minimal cute face, soft studio lighting, plain seamless backdrop,
product-showcase clarity, toy-like limbs, clean color blocks
```

**style_negative_lock**
```
canvas grain, gouache strokes, crayon scribble all-over, 2D flat logo only,
photorealistic skin pores, wet glossy chrome, cyberpunk neon pile,
complex outdoor scenery, watermark, midjourney label, nine-grid, flocked plush fur
```

备注：果冻透鞋/布料织纹可选，不写进默认。

---

## 4 · 日常扁平漫画（flat comic content actor）

目录：`style_refs/04-flat-comic/`

**style_prompt_lock**
```
flat modern comic illustration, clean limited palette, soft slight grain OK but mostly flat fills,
simple oval/bean eyes, readable streetwear silhouette, content-actor pose language,
light soft shading only, plain white/light background, editorial illustration character,
consistent clip/motif friendly
```

**style_negative_lock**
```
3D vinyl toy, heavy gouache canvas, thick wax crayon, photorealistic, hyper-detail pores,
busy full environment, nine-grid, watermark, midjourney label, flocked plush
```
