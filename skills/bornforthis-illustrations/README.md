# Bornforthis 正文配图 Skill

为中文文章、博客、帖子、Notion 文档、工作流和方法论生成 Bornforthis 个人 IP 风格的 16:9 正文插图。

![Bornforthis 示例总览](assets/examples/00-overview.png)

## 视觉识别

- IP 名称：**Bornforthis**
- 一词识别点：**黄腮红**
- 辅助识别链：**蓝碎发 + 白脸 + 黄腮红**
- 背景：纯白 `#FFFFFF`
- 气质：**可爱但有品质 · 手绘蜡笔感 · 有温度 · 不像 AI · 一看就是 Bornforthis 的**

耳机、蓝色夹克、相机、相机包和笔记本都是情境元素，不是永久服装或固定配件。

## 色彩系统

三个品牌色彼此保持约 60/30/10 的视觉层级：

- `#2B7FD8` 蓝：主色、角色头发、主轮廓、主结构、标题和链接。
- `#F4D758` 黄：黄腮红、强调、装饰和高亮。
- `#E84A5F` 红：CTA、标签、警示和转折。

这不是封闭色板。可以根据真实物体和信息语义加入绿色、青色、紫色、棕色、灰色、橙色、自然肤色等内容辅助色。辅助色必须有意义，不能形成无意义彩虹，也不能取代品牌蓝成为系列主识别。

## 字体角色

- 汇文明朝体：中文标题。
- Fraunces：英文装饰。
- Caveat：手写与注释。
- Fira Code：代码与终端。

图片模型无法保证直接调用本地字体。需要精确字体时，请提供合法字体文件，并使用“无字底图 + 后期确定性排字”。

## 使用

```text
使用 $bornforthis-illustrations，分析这篇中文文章的认知锚点，并生成 6 张 Bornforthis 风格的 16:9 正文配图。
```

也可以只要求配图策略：

```text
使用 $bornforthis-illustrations，为这篇文章提供 shot list，先不要生成图片。
```

## 目录

```text
bornforthis-illustrations/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── references/
│   ├── bornforthis-ip.md
│   ├── style-dna.md
│   ├── prompt-template.md
│   ├── composition-patterns.md
│   └── qa-checklist.md
└── assets/
    ├── references/
    │   ├── face-anchor.png
    │   └── fullbody-anchor.png
    └── examples/
        ├── 00-overview.png
        └── 01–14 示例图
```

## 安装

```bash
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo AndersonHJB/CodexSkills \
  --path skills/bornforthis-illustrations \
  --ref main
```

安装后在下一次对话中即可使用 `$bornforthis-illustrations`。

## 设计原则

- 一张图只解释一个核心结构。
- Bornforthis 必须亲自执行核心动作。
- 默认白底、大留白、短标签。
- 品牌三色控制身份与主线，内容辅助色解释真实物体和状态。
- 示例只校准角色、笔触、留白和色彩层级，不作为构图模板复刻。
