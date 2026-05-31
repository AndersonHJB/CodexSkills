# CodexSkills

Personal Codex Skills repository.

## Structure

- `skills/wechat-article-pipeline/`: WeChat article rewrite, image upload, cover generation, archive, and copy-ready HTML workflow.

## Add Or Update A Skill

```bash
rsync -a --delete ~/.codex/skills/<skill-name>/ skills/<skill-name>/
git add skills/<skill-name>
git commit -m "Update <skill-name> skill"
git push
```

## Restore A Skill Locally

```bash
mkdir -p ~/.codex/skills/<skill-name>
rsync -a skills/<skill-name>/ ~/.codex/skills/<skill-name>/
```
