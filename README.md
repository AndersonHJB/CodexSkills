# CodexSkills

这是个人维护的 Codex Skills 仓库，用来沉淀可复用的 Codex 工作流。

公开仓库地址：

```text
https://github.com/AndersonHJB/CodexSkills
```

## Skills 列表

- `wechat-article-pipeline`：微信公众号文章流水线，支持文章重写、吸金标题与摘要、教程插图、公众号封面、图片上传 PicGoImage、Markdown 图片链接替换、文章归档、公众号可复制 HTML 排版。
- `xiaohongshu-post-imagegen`：小红书帖子图生成工作流，支持按主题生成多张轮播插图、图片内中文文案、整帖统一发布文案、标题备选、互动引导和标签组合。
- `build-wechat-sticker-pack`：从一张或多张参考图片，全流程生成 20 张独立 Q 版微信表情、发布横幅/封面/聊天图标、填写文案、含义词、QA 报告、原图归档及双压缩包。

## 微信表情包全流程 Skill

`build-wechat-sticker-pack` 适合希望“只提供参考图片，其余交给 Codex”的场景。每次固定生成 20 张独立表情，但文案、动作、表情与道具会结合当前人物和主题动态规划，不会机械复用一套内容。

主要能力：

- 原始参考图片逐字节保留，保留原文件名、扩展名、EXIF，并写入 SHA-256；
- 先生成无字角色锚点，再通过 20 次独立图片生成保持人物一致性；
- 图片生成阶段不直接生成中文，最终文字由本地确定性排版，降低错字风险；
- 输出 20 张 `240×240` 独立表情，以及微信发布所需横幅、透明封面和聊天图标；
- 自动生成名称、介绍、版权、20 个含义词、AI/版权声明和可直接填写的发布材料；
- 严格检查数量、尺寸、大小、透明度、重复图、文字、来源哈希、人工复核与版权门禁；
- 同时生成仅供上传的 submission ZIP，以及包含原图、源图、提示词、生成账本和 QA 的 full archive ZIP。

安装后，在新的 Codex 会话中上传参考图片并发送：

```text
使用 $build-wechat-sticker-pack，根据这张参考图片生成完整的20张微信表情及发布提交包。
```

首次使用前，请把 `~/.codex/skills/build-wechat-sticker-pack/assets/creator-profile.json` 中的 `copyright_holder` 改成真实提交者或版权方名称。公开模板不会预填他人的版权身份；设置一次后，后续自有素材通常只需提供参考图片。

也可以附加风格或主题要求：

```text
使用 $build-wechat-sticker-pack，根据这些参考图片制作一套校园日常主题的20张微信表情，整体软萌、白色背景，并生成完整发布材料。
```

正常完成后会得到：

```text
00-reference-originals/       原图无损归档与哈希
01-plan/                      20张内容计划、人物/风格设定、冻结提示词
02-source-assets/             角色锚点、20张高分源图、发布素材、生成账本
03-submission/                可提交表情、发布图片、填写材料、QA
04-preview/                   内部审阅总览图
archives/*-submission.zip     仅上传材料
archives/*-full-archive.zip   原图与完整生产资料
```

注意：full archive 会保留原始图片字节，因此可能保留 EXIF/GPS；公开提交或分享时优先使用 submission ZIP。真人、第三方图片、品牌角色或版权不明素材会触发授权确认，未确认时只生成明确标记的草稿存档，不生成可提交 ZIP。

## 目录结构

```text
CodexSkills/
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/
        ├── assets/
        ├── references/
        └── scripts/
```

每个 Skill 都放在 `skills/<skill-name>/` 目录下。安装到本机时，需要复制到：

```text
~/.codex/skills/<skill-name>/
```

## 准备工作

本机需要有 `git` 和 `rsync`。macOS 通常自带。

先克隆仓库：

```bash
git clone https://github.com/AndersonHJB/CodexSkills.git
cd CodexSkills
```

## 让 Codex 自动安装

如果你正在使用 Codex，也可以不手动敲命令，直接把下面的提示词发给 Codex，让它帮你安装。

### 让 Codex 单独安装一个 Skill

把这段发给 Codex：

```text
请帮我从 https://github.com/AndersonHJB/CodexSkills 安装 wechat-article-pipeline 这个 Codex Skill。
要求：
1. 克隆或更新这个仓库。
2. 将 skills/wechat-article-pipeline/ 复制到 ~/.codex/skills/wechat-article-pipeline/。
3. 如果本地已存在同名 Skill，请先告诉我会覆盖哪些文件，再执行覆盖。
4. 安装后检查 ~/.codex/skills/wechat-article-pipeline/SKILL.md 是否存在。
5. 最后告诉我是否需要重启 Codex 或新建会话。
```

安装小红书帖子图生成 Skill 时，把 Skill 名称换成：

```text
xiaohongshu-post-imagegen
```

安装微信表情包 Skill 时，把上面的 `wechat-article-pipeline` 替换为 `build-wechat-sticker-pack` 即可。

### 让 Codex 批量安装全部 Skills

把这段发给 Codex：

```text
请帮我从 https://github.com/AndersonHJB/CodexSkills 批量安装全部 Codex Skills。
要求：
1. 克隆或更新这个仓库。
2. 遍历仓库里的 skills/*/ 目录。
3. 将每个 Skill 分别复制到 ~/.codex/skills/<skill-name>/。
4. 如果本地已有同名 Skill，请先列出将被覆盖的 Skill 名称，再执行覆盖。
5. 安装后列出 ~/.codex/skills 下已经安装的 Skills。
6. 最后提醒我重启 Codex 或新建会话，让 Skills 生效。
```

如果你希望 Codex 直接覆盖本地同名 Skill，也可以在提示词里加一句：

```text
允许直接覆盖本地同名 Skill，不需要逐个确认。
```

## 单独安装一个 Skill

以 `wechat-article-pipeline` 为例：

```bash
mkdir -p ~/.codex/skills/wechat-article-pipeline
rsync -a skills/wechat-article-pipeline/ ~/.codex/skills/wechat-article-pipeline/
```

安装 `xiaohongshu-post-imagegen`：

```bash
mkdir -p ~/.codex/skills/xiaohongshu-post-imagegen
rsync -a skills/xiaohongshu-post-imagegen/ ~/.codex/skills/xiaohongshu-post-imagegen/
```

安装微信表情包 Skill：

```bash
mkdir -p ~/.codex/skills/build-wechat-sticker-pack
rsync -a skills/build-wechat-sticker-pack/ ~/.codex/skills/build-wechat-sticker-pack/
```

安装后，重启 Codex 或新建一个会话，让 Skill 列表重新加载。

## 批量安装全部 Skills

如果你想一次安装仓库里的全部 Skills：

```bash
mkdir -p ~/.codex/skills
for skill_dir in skills/*/; do
  skill_name="$(basename "$skill_dir")"
  mkdir -p "$HOME/.codex/skills/$skill_name"
  rsync -a "$skill_dir" "$HOME/.codex/skills/$skill_name/"
done
```

安装后，重启 Codex 或新建一个会话。

## 覆盖式更新已安装 Skills

如果你已经安装过，想用仓库版本覆盖本地版本：

```bash
git pull
rsync -a --delete skills/wechat-article-pipeline/ ~/.codex/skills/wechat-article-pipeline/
```

批量覆盖更新全部 Skills：

```bash
git pull
for skill_dir in skills/*/; do
  skill_name="$(basename "$skill_dir")"
  mkdir -p "$HOME/.codex/skills/$skill_name"
  rsync -a --delete "$skill_dir" "$HOME/.codex/skills/$skill_name/"
done
```

注意：`--delete` 会删除本地目标目录里仓库不存在的文件。如果你在本地改过 Skill，先备份或提交到自己的仓库。

## 验证安装结果

检查本地是否已经安装：

```bash
ls ~/.codex/skills
ls ~/.codex/skills/wechat-article-pipeline
ls ~/.codex/skills/xiaohongshu-post-imagegen
ls ~/.codex/skills/build-wechat-sticker-pack
```

也可以检查 Skill 文件是否存在：

```bash
test -f ~/.codex/skills/wechat-article-pipeline/SKILL.md && echo "installed"
test -f ~/.codex/skills/xiaohongshu-post-imagegen/SKILL.md && echo "installed"
test -f ~/.codex/skills/build-wechat-sticker-pack/SKILL.md && echo "installed"
```

在 Codex 中新建会话后，如果任务匹配 Skill 的描述，Codex 会自动使用对应 Skill。

## 卸载一个 Skill

```bash
rm -rf ~/.codex/skills/wechat-article-pipeline
```

卸载 `xiaohongshu-post-imagegen`：

```bash
rm -rf ~/.codex/skills/xiaohongshu-post-imagegen
```

卸载 `build-wechat-sticker-pack`：

```bash
rm -rf ~/.codex/skills/build-wechat-sticker-pack
```

卸载后重启 Codex 或新建会话。

## 维护者：新增或更新 Skill

从本机 Codex Skills 目录同步到仓库：

```bash
rsync -a --delete ~/.codex/skills/<skill-name>/ skills/<skill-name>/
git add skills/<skill-name>
git commit -m "Update <skill-name> skill"
git push
```

新增 Skill 时：

```bash
mkdir -p skills/<skill-name>
rsync -a ~/.codex/skills/<skill-name>/ skills/<skill-name>/
git add skills/<skill-name> README.md
git commit -m "Add <skill-name> skill"
git push
```
