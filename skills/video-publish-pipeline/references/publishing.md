# Five-platform publishing package

## Research first

Read and follow `video-platform-publishing`, including its platform-guideline and market-research references. Browse the web on every run because platform rules, labels, limits, and category conventions change. Prefer official platform sources for exact policy or specification claims, and use recent comparable content only to infer title, description, publishing, and cover-density patterns. In `house-creative`, those patterns may refine hook density but must not change the approved cover system. In preservation modes, do not restyle the delivered cover.

Record the research date and direct source links in the final Markdown. Clearly separate official requirements from inferred creative patterns. Search for three to five discoverable same-topic examples and three to five same-format examples across the target platforms; if a platform blocks public search, record that limitation and use accessible adjacent examples instead of pretending inaccessible posts were verified. Prefer recent examples, but retain an older example only when it demonstrates a durable pattern.

Before drafting, write a compact market-method section that records:

- the recurring search phrases users actually type;
- the hook families found in current examples, such as problem, outcome, proof, audience, checklist, comparison, or caveat;
- title structures worth testing without copying a single creator;
- high-signal description openings and platform-native CTA patterns;
- a small relevant tag cluster, excluding unrelated trending tags;
- which findings are direct observations and which are creative inferences.

Market examples are evidence for method, not a source to imitate line-for-line. Do not copy a competitor title, description, cover, or tag block.

## Shared factual core

Use the final transcript, fact matrix, final chapter timestamps, cover filenames, and verified master filename. Keep the same facts and caveats everywhere, but rewrite tone and structure for each platform.

Do not:

- invent results, links, download locations, coupons, sponsorships, credentials, or compatibility;
- use absolute claims such as “全网最强”, “永久可用”, “100%成功”, or “万能” without evidence;
- imply official affiliation or encourage piracy, unauthorized reposting, policy evasion, or traffic diversion;
- stuff irrelevant trending tags or promise a viral outcome.

## Markdown deliverable

For each of 微信视频号、哔哩哔哩、小红书、抖音、YouTube include:

- one recommended title;
- four or five A/B titles that test genuinely different angles: problem, outcome, proof, audience, search intent, or caveat;
- one short recommendation rationale naming the intended search phrase and click trigger;
- cover ratio, exact final file path, and short cover copy;
- ready-to-paste body/description;
- platform-native topics, hashtags, or backend search tags;
- a pinned/first comment when that surface currently exists;
- one to three publishing reminders, including disclosure or rights notes when relevant.

Also:

- Put real search language early in titles, with one main hook per title.
- Lead descriptions with the result, then steps, limitation, and responsible-use boundary.
- Adapt the same fact core to the platform instead of pasting one generic paragraph five times: Bilibili and YouTube should be search-rich and structured; Douyin should open with one tension or curiosity gap; 微信视频号 should prioritize trust and practical context; 小红书 should be saveable, scannable, and checklist-oriented.
- For Bilibili and YouTube, generate chapter lists from final verified timestamps.
- For YouTube, separate public hashtags from backend tags.
- Map each platform to an existing delivered cover rather than promising a missing file.
- In `house-creative`, report only the exact wording visible in the verified final cover; do not substitute an unrendered title variant.
- In `preserve-asset` or `preserve-frame` mode, report the unchanged cover wording actually present in the delivered image. If the image contains no cover wording, write `无新增封面文案`; do not invent replacement copy or propose a visual restyle inside the publishing Markdown.
- Add a short cross-platform fact-consistency checklist and a sources section.
- Label the output as a researched high-click-potential package, never as a guaranteed viral formula.

Write the result as `<stem>-五平台发布文案.md` next to the source. Run `scripts/validate_publishing.py <markdown> --json-out <project>/publishing-qa.json`, fix every hard failure, and preserve the report. Generate files only; uploading or publishing requires separate authorization.
