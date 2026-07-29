# Cola Voice Delivery Skill

Reusable workflow for long Chinese ListenHub narration in two voices:

- `晓曼` / `Xiaoman`: `chat-girl-105-cn`
- `Cola`: `chatb812x-500306f5`

The skill delivers both the individual MP3 chunks and the voice-specific merged MP3. The number of chunks is decided from the input length; it is not fixed. See [SKILL.md](SKILL.md) for the full workflow.

## 安装

直接复制下面的命令，只安装这个 Skill，不影响其他已安装的 Skill：

```bash
repo_dir="${TMPDIR:-/tmp}/CodexSkills"
if [ -d "$repo_dir/.git" ]; then git -C "$repo_dir" pull --ff-only; else git clone https://github.com/AndersonHJB/CodexSkills.git "$repo_dir"; fi
mkdir -p "$HOME/.codex/skills/cola-voice-delivery"
rsync -a "$repo_dir/skills/cola-voice-delivery/" "$HOME/.codex/skills/cola-voice-delivery/"
test -f "$HOME/.codex/skills/cola-voice-delivery/SKILL.md" && echo "cola-voice-delivery installed"
```

完成后重启 Codex 或新建会话。

## 使用测试指令

把下面这段直接发给 Cola，并附上一个 `.txt`、`.md` 或其他文本文件：

```text
使用 $cola-voice-delivery，把我附带的文本生成完整中文朗读音频。

请使用两个音声：
1. 晓曼（chat-girl-105-cn）
2. Cola（chatb812x-500306f5）

请根据文本长度自动分段，不要假设固定段数。分别生成两个音声的全部 MP3 片段，并分别拼接成完整音频。最后交付：
- 晓曼的所有片段和完整音频
- Cola 的所有片段和完整音频

请核查每个片段、两个拼接文件的存在性、时长和文件大小，并为每个文件提供 MEDIA 路径。
```

也可以不附文件，直接把正文放在这条指令后面。播客音频则先转写成文字，再按同样流程生成。
