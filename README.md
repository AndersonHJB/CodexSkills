# CodexSkills

这是个人维护的 Codex Skills 仓库，用来沉淀可复用的 Codex 工作流。

公开仓库地址：

```text
https://github.com/AndersonHJB/CodexSkills
```

## Skills 列表

- `wechat-article-pipeline`：微信公众号文章流水线，支持文章重写、吸金标题与摘要、教程插图、公众号封面、图片上传 PicGoImage、Markdown 图片链接替换、文章归档、公众号可复制 HTML 排版。

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

## 单独安装一个 Skill

以 `wechat-article-pipeline` 为例：

```bash
mkdir -p ~/.codex/skills/wechat-article-pipeline
rsync -a skills/wechat-article-pipeline/ ~/.codex/skills/wechat-article-pipeline/
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
```

也可以检查 Skill 文件是否存在：

```bash
test -f ~/.codex/skills/wechat-article-pipeline/SKILL.md && echo "installed"
```

在 Codex 中新建会话后，如果任务匹配 Skill 的描述，Codex 会自动使用对应 Skill。

## 卸载一个 Skill

```bash
rm -rf ~/.codex/skills/wechat-article-pipeline
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
