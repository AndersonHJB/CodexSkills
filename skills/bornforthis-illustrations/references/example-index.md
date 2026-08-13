# 内置参考图索引

## 使用规则

`assets/examples/` 是 Bornforthis 正文配图的低频视觉校准集。需要判断输出是否达到目标效果时，按当前问题选择最多 1–2 张查看，不要一次加载全部，也不要把它们默认传入 `image_gen`。

只校准这些维度：

- 16:9 纯白背景与留白密度。
- 蜡笔或马克笔斜线填充、深海军蓝晃动描边。
- Bornforthis 的固定身份在不同动作和服装下保持一致。
- 角色亲自承担核心动作。
- 单一概念、简短中文标注、温暖且略荒诞的绘本感。

不要照抄样例的主题、构图、主物件、服装、动作或标注。生成新图时仍只把 `assets/references/bornforthis-ref-1.png` 和 `assets/references/bornforthis-ref-2.png` 作为必传身份参考。

## 样例清单

| 文件 | 结构覆盖 | 主要校准点 | 当次可变造型 |
|---|---|---|---|
| `assets/examples/01-two-breakpoints.png` | 断点 / 修补 | 一条简单结构中突出两个故障点，角色亲手修复 | 以成图为准，不是固定服装 |
| `assets/examples/02-sort-by-purpose.png` | 分流 / 分拣 | 少量彩色块、三向分流、角色主动操作 | 以成图为准，不是固定服装 |
| `assets/examples/03-data-compression.png` | 输入 → 处理 → 输出 | 手压机、松散输入到紧凑输出、大留白 | 珊瑚红围裙工作装 |
| `assets/examples/04-causal-chain.png` | 因果结构 | 单条链、局部断裂、角色修复关键连接 | 绿色维修工装 |
| `assets/examples/05-abstract-to-concrete.png` | 概念转化 | 从抽象线形中拉出具体物件、动作清楚 | 浅青衬衫与珊瑚围裙 |
| `assets/examples/06-comparison.png` | 对比 | 两个不同对象、手工测量、结构克制 | 绿色工作服与红领巾 |
| `assets/examples/07-process-steps.png` | 三步流程 | 同一角色的三个连续状态、服装保持一致 | 青绿色外衫与珊瑚长裤 |
| `assets/examples/08-core-anchor.png` | 核心锚点 | 中心动作、外围拉力、同心结构但非 UI | 黄色工装背心与珊瑚衬衫 |
| `assets/examples/09-note-recirculation.png` | 概念隐喻 / 回流 | 怪机器、清晰因果动作、少量多色短标注 | 珊瑚工作衫与深蓝工装裤 |
| `assets/examples/10-information-well.png` | 信息提取 / 检索 | 从低科技信息井主动捞取有效内容 | 以成图为准，不是固定服装 |
| `assets/examples/11-idea-press.png` | 创意加工 | 松散想法经过手动装置变成可用形态 | 以成图为准，不是固定服装 |
| `assets/examples/12-content-fermentation.png` | 内容发酵 | 原始碎片在透明容器中发生状态转化 | 以成图为准，不是固定服装 |
| `assets/examples/13-system-bearing.png` | 系统承重 | 角色亲手加固关键支点，承接上层重量 | 以成图为准，不是固定服装 |
| `assets/examples/14-trust-bridge.png` | 信任建立 | 逐块搭建并补上最后的连接，使鸿沟可跨越 | 紫色工作衫、黄色背带与深蓝长裤 |

## 选择建议

- 身份或换装漂移：查看两张身份锚点，再查看与当前姿势接近的一张样例。
- 画面太像 PPT：查看 `03`、`05` 或 `09` 的自然场景组织。
- 流程不清：查看 `03` 或 `07` 的动作递进，只校准信息密度。
- 角色太装饰：查看 `04`、`06`、`08`、`13` 或 `14` 中角色如何直接操作核心结构。
- 纹理、描边或留白漂移：任选一张主体大小接近的样例即可。

样例数量不代表默认配图数量，也不允许据此复刻同一构图。
