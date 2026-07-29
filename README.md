# CodexSkills

这是个人维护的 Codex Skills 仓库，用来沉淀可复用的 Codex 工作流。

公开仓库地址：

```text
https://github.com/AndersonHJB/CodexSkills
```

## Skills 列表

- `wechat-article-pipeline`：微信公众号文章流水线，支持文章重写、吸金标题与摘要、教程插图、公众号封面、图片上传 PicGoImage、Markdown 图片链接替换、文章归档、公众号可复制 HTML 排版。
- `xiaohongshu-post-imagegen`：小红书帖子图生成工作流，支持按主题生成多张轮播插图、图片内中文文案、整帖统一发布文案、标题备选、互动引导和标签组合。
- `wechat-chat-to-xiaohongshu`：微信聊天截图转小红书工作流，支持截图排序、OCR、证据核对、严格匿名化、1080×1440 轮播排版、标题正文标签和隐私质检。
- `build-wechat-sticker-pack`：从一张或多张参考图片，全流程生成 20 张独立 Q 版微信表情、发布横幅/封面/聊天图标、填写文案、含义词、QA 报告、原图归档及双压缩包。
- `cola-voice-delivery`：使用 ListenHub 将文本或播客转成晓曼与 Cola 两种中文女生声，按输入长度动态分段，交付每个片段和两种音声的完整拼接 MP3。

## 微信聊天截图转小红书 Skill

`wechat-chat-to-xiaohongshu` 适合把私教沟通、客户咨询、课程规划等微信聊天截图整理成可发布的小红书帖子。默认保留真实截图作为证据主体，不让图片模型重绘聊天文字。

主要能力：

- 自动盘点截图并结合时间、文件名和对话连续性重建顺序；
- 使用 macOS Vision OCR 建立可检索文本，同时要求逐图核对；
- 建立证据台账，区分双方表述、已核实事实、编辑推断和不可发布内容；
- 默认隐藏昵称、头像、账号、电话、链接、二维码、交易与排课信息；
- 确定性生成 1080×1440 轮播图、总览图、标题、统一正文、标签和图片顺序；
- 最终 OCR 扫描隐私屏蔽词，并生成可审计的质检报告；
- 保持原始素材目录和文件字节不变。

安装后，给出包含原始微信截图的文件夹路径并发送：

```text
使用 $wechat-chat-to-xiaohongshu，把这个微信聊天截图文件夹做成可发布的小红书帖子：
/绝对路径/聊天截图文件夹

请自动完成聊天排序、OCR、隐私脱敏、轮播设计与生成，并提供标题、整帖文案、标签、图片顺序和质检报告。
```

只有 Finder 文件列表截图无法读取聊天内容，需要提供实际截图文件或文件夹路径。

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

## Cola 双音声长文朗读 Skill

`cola-voice-delivery` 适合把一份文本、文本文件或播客内容直接生成两套中文朗读音频。调用 Skill 并提供内容即可，Skill 会自行读取、转写（播客音频时）、动态分段、生成、下载、拼接和核查，不要求手动拆分或合并。

固定使用两个 ListenHub 音色：

- 晓曼：`chat-girl-105-cn`
- Cola：`chatb812x-500306f5`

它会根据文本长度和章节边界动态决定片段数量，不假设固定 11 段。每个音色都会交付：

- 全部有序 MP3 片段；
- 一个独立命名的完整拼接 MP3；
- 生成状态、下载结果、音频时长和文件大小核查。

简单调用：

```text
使用 $cola-voice-delivery，把这个文本生成完整音频：
/绝对路径/播客稿.txt

请交付晓曼和 Cola 两个音声的全部片段，以及各自的完整拼接音频。
```

也可以直接附带文本内容。长文本会按章节或自然段动态拆分；如果 ListenHub 的输入接口要求 HTML，Skill 会准备 HTML 备用输入，失败时回退到逐段直接文本生成。

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

安装微信聊天截图转小红书 Skill 时，把 Skill 名称换成：

```text
wechat-chat-to-xiaohongshu
```

安装微信表情包 Skill 时，把上面的 `wechat-article-pipeline` 替换为 `build-wechat-sticker-pack` 即可。

安装 Cola 双音声长文朗读 Skill 时，把上面的 Skill 名称替换为：

```text
cola-voice-delivery
```

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

安装 `wechat-chat-to-xiaohongshu`：

```bash
mkdir -p ~/.codex/skills/wechat-chat-to-xiaohongshu
rsync -a skills/wechat-chat-to-xiaohongshu/ ~/.codex/skills/wechat-chat-to-xiaohongshu/
```

安装微信表情包 Skill：

```bash
mkdir -p ~/.codex/skills/build-wechat-sticker-pack
rsync -a skills/build-wechat-sticker-pack/ ~/.codex/skills/build-wechat-sticker-pack/
```

安装 Cola 双音声长文朗读 Skill：

```bash
mkdir -p ~/.codex/skills/cola-voice-delivery
rsync -a skills/cola-voice-delivery/ ~/.codex/skills/cola-voice-delivery/
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
ls ~/.codex/skills/wechat-chat-to-xiaohongshu
ls ~/.codex/skills/build-wechat-sticker-pack
```

也可以检查 Skill 文件是否存在：

```bash
test -f ~/.codex/skills/wechat-article-pipeline/SKILL.md && echo "installed"
test -f ~/.codex/skills/xiaohongshu-post-imagegen/SKILL.md && echo "installed"
test -f ~/.codex/skills/wechat-chat-to-xiaohongshu/SKILL.md && echo "installed"
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

卸载 `wechat-chat-to-xiaohongshu`：

```bash
rm -rf ~/.codex/skills/wechat-chat-to-xiaohongshu
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
