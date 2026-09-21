---
name: blindbox-ip-skill-4styles
description: >-
  Create a reusable content-illustration character and simple IP Standard Pack for a person, creator account, or brand. Use for personal IP, account mascots, brand characters, blind-box or designer-toy characters, “把我变成一个角色”, “做一个账号形象”, or when someone needs consistent character images, values, turnaround views, and reusable prompts.
---
# 内容配图角色 IP Standard Pack

## 目标

把个人、自媒体账号或品牌的描述，变成一个能长期复用的内容配图角色。最终交付角色价值观、视觉 DNA、正面图、三视图、角色参考板、分层提示词和一致性测试图。

## 核心规则

- 面向不懂设计的人：优先让用户上传喜欢的图片或已有资产；少问术语，多给 2–3 个清晰选项。
- 无图、不会描述或回答“不知道”也能开始；只追问影响设计的硬缺口，每次最多 3 个问题。
- 用户确认角色 DNA 后再生图；用户审美确认与视觉规范验收分开。
- 角色标准正面图是唯一权威原件，后续视图不得重新仿画替代它。
- 三视图、系列图和表情包都使用同一角色标准正面图或角色参考板作为参考图。
- 每张图独立生成并独立验收；禁止九宫格生成后切图。
- 正式 Pack 使用相对路径，不绑定本机路径。

## 1. 快速收集信息

先这样问：

> 开始前你可以任选一种方式：上传 1–5 张喜欢或不喜欢的图片；贴 1–3 段代表内容；简单描述自己或品牌；或者直接说“不知道”，我来推荐。

四个入口可任选一个或混用：

1. **上传图片**：1–5 张喜欢或不喜欢的 IP、插画、玩具图片；每张只需标注“喜欢”“不喜欢”或“只喜欢配色/比例/质感”。
2. **提供已有内容**：粘贴 1–3 段代表性文章、帖子、账号简介或品牌介绍，让 Agent 提取价值观、语气与受众。
3. **简单描述**：说清自己或品牌是谁、做什么内容、希望给人什么感觉、角色用在哪里。
4. **完全不知道**：由 Agent 根据内容主题和受众直接推荐 2–3 个方向。

图片分两类处理：

- **灵感参考**：只提取形态、比例、五官、配色、材质、细节量和气质，不复制具体角色、服装、Logo、道具或独特构图。
- **自有资产**：本人照片、现有角色、Logo、产品图、品牌色可作为身份或品牌约束；先确认哪些元素必须保留。

读取图片后，先用一句话总结用户喜欢和排斥的视觉特征，让用户确认；不要要求用户自己说出设计术语。

同时从图片或描述中提取：身份、内容主题、受众、主要用途、性格矛盾、个人价值观、表达边界和品牌约束。信息不足时，只补问会改变角色形态、价值立场或使用方式的问题。

## 2. 给出角色方向

提供 2–3 个方向，每个方向只写：

- 角色形态与剪影；
- 性格与价值立场；
- 招牌识别点；
- 适合的内容；
- 一个主要风险。

用户选定方向后再建立 DNA。

## 3. 确认角色 DNA

```yaml
meta:
  name:
  mode: creator | brand
  audience:
  primary_uses: []

personality_values:
  one_line_core:
  soul_tension:
  core_values: []           # 最多 3 个
  core_belief:
  content_stance:
  behavior_patterns: []
  voice:
  boundaries: []

visual_dna:
  form: character | object
  silhouette:
  body_proportions:
  face_lock:
  signature_props: []       # 1–2 个
  accent_rule:
  palette:
    primary: {name: "", hex: ""}
    secondary: {name: "", hex: ""}
    accent: {name: "", hex: ""}
    outline: {name: "", hex: ""}
    background: {name: "", hex: ""}
  movable_parts: []
  forbidden_drift: []
  content_actor_notes:
```

价值观必须能指导角色如何表达内容，不能只写“温柔、自由、勇敢”等空词。

## 4. 确认画风

生成图片前必须让用户确认画风，不能根据参考图静默决定。

提供四张简短风格卡：

1. **治愈绘本手绘**：像独立绘本和手绘文创角色，温暖、有颜料与纸张质感；适合情绪和生活内容，细节较容易漂移。
2. **极简符号卡通**：可用 Miffy、LINE FRIENDS 的“少线条、少色块、高识别”逻辑帮助理解；适合头像、贴纸和轻品牌，复杂动作表现较弱。
3. **盲盒潮玩公仔**：可用泡泡玛特这一类设计师玩具的“大头比例、圆润造型、搪胶材质、商品展示感”帮助理解；适合品牌角色，三视图要求更高。
4. **日常扁平漫画**：可用 Snoopy、Moomin 漫画的“角色能持续做动作、进入日常场景”逻辑帮助理解；适合长期内容配图。

知名 IP 只作为文字认知锚点，不把其名称写入生图提示词，也不要求复制其角色外形或画法。

如果提供视觉风格卡，四张卡必须使用同一个原创示例角色、相同姿势和相同配色，只改变画法与材质，让用户比较真正的风格差异。每张卡只展示：风格名称、原创示例图、适合内容、主要风险。

- 用户没有参考图：根据用途推荐 1 种，同时给 1 种备选。
- 用户上传了参考图：先说明图片更接近哪种风格，再推荐 1–2 种。
- 用户可以直接选编号，也可以回复“按你推荐的来”。

用户明确确认后，把 `style_id`、`material` 和对应 `style_lock` 写入 Visual DNA。未确认前不得生成角色标准正面图。

读取 `style_refs/STYLE-LOCKS.md`。参考图只用于传递材质、线条和渲染方式，不复制其中的角色、配色、服装、道具或构图。

## 5. 生成角色标准正面图

角色标准正面图要求：

- 正面、平视、中性站姿或中性悬浮姿；
- 完整显示身体、肢体/组件与招牌件；
- 浅色纯背景，无场景、文字和遮挡；
- 不用夸张动作隐藏身体比例。

用户确认喜欢且通过一致性检查后，将原图保存为 `character-front.png`。

## 6. 生成三视图与角色参考板

以角色标准正面图为参考，生成：

- 侧面；
- 背面；
- 面部近景；
- 招牌件局部；
- 标准色板。

正面直接使用角色标准正面图原件。所有视图保持相同的比例、脸、组件、招牌件、固有色与材质。

把通过验收的原图无损排成 `character-reference-board.png`。排版时不得重绘或改变角色标准正面图。后续跨 Agent 出图优先上传这张角色参考板。

## 7. 生成可复用提示词

不要把固定姿态、构图和背景写进角色锁。

```yaml
identity_lock: ""          # 身体、比例、脸、招牌件、固有色
style_lock: ""             # 材质、线条、渲染方式
values_tone: ""            # 内容需要时使用
pose_slot: ""              # 每张替换
environment_slot: ""       # 每张替换，可为空
composition_slot: ""       # 每张替换
output_spec: ""            # 比例、尺寸、背景要求
negative_lock: ""          # 永久禁止的身份与画风漂移
```

同时交付：

- `standard_front_prompt`；
- `scene_prompt_template`；
- 用户需要表情包时再交付 `sticker_prompt_template`。

场景提示词按以下顺序拼接：

```text
identity_lock + style_lock + values_tone
+ pose_slot + environment_slot + composition_slot
+ output_spec + negative_lock
```

## 8. 一致性验收

用角色参考板和 场景模板独立生成三张测试图：

1. 常用动作；
2. 大幅度动作；
3. 轻场景内容配图。

每张按 100 分检查：

| 项目 | 分值 |
|---|---:|
| 剪影与形态 | 20 |
| 身体比例与组件 | 15 |
| 脸规则 | 20 |
| 招牌件 | 15 |
| 固有色与强调色 | 10 |
| 材质与画风 | 10 |
| 角色气质 | 5 |
| 输出规格 | 5 |

正式图需达到 **90/100**。物种改变、肢体/组件数量错误、脸结构改变、招牌件消失或角色标准正面图被重画，直接判定失败。

未通过时只修正失败的 DNA、提示词或视图，不整套随机重做。

## 9. 交付 Standard Pack

```text
<ip-name>-standard-pack-v1/
├── IP-PACK.md
├── manifest.yaml
├── references/
│   ├── character-front.png
│   ├── view-side.png
│   ├── view-back.png
│   └── character-reference-board.png
├── prompts/
│   ├── prompt-locks.yaml
│   └── copy-paste-prompts.md
└── tests/
    ├── test-01-common-action.png
    ├── test-02-large-action.png
    ├── test-03-light-scene.png
    └── identity-qa.md
```

`manifest.yaml` 记录 Pack 版本、使用的 Agent/模型、参考图方式、正式资产相对路径和已知限制。只有三视图与三张测试图都通过后，状态才能写为 `locked`。

## 可选表情包

用户明确提出后才生成。每张表情独立生成并上传同一角色参考板；角色固有色和招牌件不得漂移。按目标平台检查透明背景、尺寸、安全留白和缩略图可读性，不强制凑满固定数量。

## 最终检查

- [ ] 价值观能指导角色表达内容
- [ ] DNA 含比例、脸、招牌件、HEX 色板和漂移禁区
- [ ] 用户已明确确认画风，Visual DNA 已写入 style 与 material
- [ ] 角色标准正面图是已确认的正面原件
- [ ] 三视图与角色参考板完成
- [ ] 分层提示词没有固定姿态冲突
- [ ] 三张测试图均达到 90 分
- [ ] Pack 只使用相对路径
- [ ] 品牌角色没有复制具体品牌或受保护角色特征
