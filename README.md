# CodexSkills

这是个人维护的 Codex Skills 仓库，用来沉淀可复用的 Codex 工作流。

公开仓库地址：

```text
https://github.com/AndersonHJB/CodexSkills
```

## Skills 列表

- `wechat-article-pipeline`：微信公众号文章流水线，支持文章重写、吸金标题与摘要、教程插图、公众号封面、图片上传 PicGoImage、Markdown 图片链接替换、文章归档、公众号可复制 HTML 排版。
- `xiaohongshu-post-imagegen`：小红书帖子图生成工作流，支持按主题生成多张轮播插图、图片内中文文案、整帖统一发布文案、标题备选、互动引导和标签组合。

## 目录结构

```text
CodexSkills/
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/
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
```

也可以检查 Skill 文件是否存在：

```bash
test -f ~/.codex/skills/wechat-article-pipeline/SKILL.md && echo "installed"
test -f ~/.codex/skills/xiaohongshu-post-imagegen/SKILL.md && echo "installed"
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
