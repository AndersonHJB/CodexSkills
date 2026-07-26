# Storyboard Schema

Author `_work/storyboard.json` as UTF-8 JSON. Paths may be absolute or relative to the storyboard file.

## Top-Level Fields

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | yes | Use `1` |
| `project` | yes | Project metadata and shared footer |
| `canvas` | no | `[width, height]`; defaults to `[1080, 1440]` |
| `theme` | no | Color and font overrides |
| `privacy` | yes | Strict mode and blocked OCR terms |
| `slides` | yes | Ordered slide definitions |

## Slide Fields

| Field | Required | Meaning |
|---|---:|---|
| `filename` | yes | Numeric PNG filename, e.g. `01-封面.png` |
| `layout` | yes | `cover`, `chat-left`, `chat-right`, or `chat-full` |
| `eyebrow` | no | Small series or section label |
| `title` | yes | Main headline, at most two lines |
| `subtitle` | no | One supporting sentence |
| `source` | normally | Source image, crop, redactions, and privacy review |
| `badges` | no | 1-4 compact cover/category labels |
| `callouts` | no | Explanatory blocks with `title` and optional `body` |
| `takeaway` | no | Footer conclusion above the shared footer |

## Source and Coordinates

Use normalized coordinates in `[x, y, width, height]` form. `(0, 0)` is the top-left of the original source image.

```json
{
  "path": "/absolute/path/to/IMG_0001.PNG",
  "crop": [0.0, 0.06, 1.0, 0.88],
  "privacy_reviewed": true,
  "redactions": [
    {"rect": [0.34, 0.025, 0.32, 0.045], "mode": "solid"},
    {"rect": [0.015, 0.12, 0.09, 0.07], "mode": "pixelate"}
  ]
}
```

Supported redaction modes are `solid`, `pixelate`, and `blur`. Optional redaction fields are `color`, `radius`, and `block_size`.

## Theme Fields

All theme fields are optional:

```json
{
  "background": "#F7F3EA",
  "paper": "#FFFDF8",
  "ink": "#20231F",
  "muted": "#62675F",
  "accent": "#D9573F",
  "accent_2": "#4E6B45",
  "accent_3": "#D7A928",
  "line": "#D8D1C3",
  "font_regular": "/path/to/font.ttf",
  "font_bold": "/path/to/font.ttf"
}
```

## Complete Example

Replace `__SOURCE_01__` and `__SOURCE_02__` before rendering.

```json
{
  "schema_version": 1,
  "project": {
    "name": "Python 科学计算沟通记录",
    "series_label": "真实沟通记录",
    "footer": "先看需求，再定学习路径"
  },
  "canvas": [1080, 1440],
  "privacy": {
    "strict": true,
    "blocked_terms": ["真实昵称", "private.example.com"]
  },
  "theme": {},
  "slides": [
    {
      "filename": "01-封面-科学计算.png",
      "layout": "cover",
      "eyebrow": "真实沟通记录",
      "title": "Python 科学计算\n一对一怎么规划？",
      "subtitle": "从基础确认，到 NumPy / SciPy 学习路径",
      "source": {
        "path": "__SOURCE_01__",
        "crop": [0.0, 0.02, 1.0, 0.92],
        "privacy_reviewed": true,
        "redactions": []
      },
      "badges": ["零基础", "科学计算", "学习规划"],
      "callouts": [
        {"title": "先确认目标", "body": "课程、作业和研究需求，路径并不相同。"}
      ],
      "takeaway": "真实记录已做匿名处理"
    },
    {
      "filename": "02-确认基础.png",
      "layout": "chat-left",
      "eyebrow": "需求诊断",
      "title": "基础没确认，路线很容易排错",
      "subtitle": "先问经历、目标和要用到的工具",
      "source": {
        "path": "__SOURCE_02__",
        "crop": [0.0, 0.06, 1.0, 0.86],
        "privacy_reviewed": true,
        "redactions": []
      },
      "callouts": [
        {"title": "当前基础", "body": "是否系统学过 Python？"},
        {"title": "使用场景", "body": "课程、作业、科研还是项目？"},
        {"title": "工具范围", "body": "确认 NumPy、SciPy、Matplotlib 等。"}
      ],
      "takeaway": "先诊断，再安排内容和节奏"
    },
    {
      "filename": "03-学习路径.png",
      "layout": "chat-right",
      "eyebrow": "课程规划",
      "title": "把大目标拆成可执行的三步",
      "subtitle": "基础、案例、工具环境逐步推进",
      "source": {
        "path": "__SOURCE_01__",
        "crop": [0.0, 0.18, 1.0, 0.72],
        "privacy_reviewed": true,
        "redactions": []
      },
      "callouts": [
        {"title": "Step 1", "body": "补 Python 基础与调试思维。"},
        {"title": "Step 2", "body": "进入科学计算库和典型案例。"},
        {"title": "Step 3", "body": "结合课程任务完成练习。"}
      ],
      "takeaway": "路线要能落到每次课和课后练习"
    }
  ]
}
```

## Authoring Checks

- Keep `filename` order identical to array order.
- Keep `privacy.strict` true for real conversations.
- Add a `source` to every screenshot-based slide.
- Mark `privacy_reviewed` true only after visual inspection.
- Use no more than four badges or four callouts on one slide.
- Shorten text when the renderer reports overflow.
