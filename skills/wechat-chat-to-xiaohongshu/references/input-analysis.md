# Input Analysis and Privacy

Use this reference while turning raw screenshots into a verified source record.

## 1. Establish File Order

Start with the natural filename order from `manifest.json`, then correct it by visual evidence.

Prefer these signals, in order:

1. Visible date separators and message timestamps.
2. A message repeated at the bottom of one screenshot and the top of the next.
3. Question-and-answer continuity.
4. Sequential image numbers or capture timestamps.
5. Filesystem timestamps only as a last resort.

Treat web pages, course outlines, payment receipts, booking pages, and schedules as supporting inserts. Place each insert after the message that introduces it, not merely by filename.

Record manual corrections in the evidence ledger rather than renaming source files.

## 2. Use OCR as an Index

`ocr.tsv` contains normalized Vision coordinates and recognized text. Use it to search and group content, not as authoritative transcription.

Correct OCR by inspecting the original when text includes:

- Names, dates, prices, URLs, course names, or technical terms.
- `0/O`, `1/l/I`, punctuation, mathematical notation, or mixed Chinese and English.
- Tiny gray text, reply previews, document thumbnails, or cropped message bubbles.
- Traditional/simplified substitutions that change meaning.

Ignore status-bar text, battery percentages, input-bar labels, duplicated headers, and unrelated app chrome unless they establish chronology.

## 3. Attribute Speakers

Build a simple speaker map before summarizing:

```text
right-side bubbles = owner/service provider (visually confirmed)
left-side bubbles  = client/student (visually confirmed)
```

Do not assume green always means the owner. Exported images, forwarded screenshots, Android themes, and mirrored images can reverse normal conventions. Confirm with self-reference, replies, and the visible conversation flow.

When a statement's speaker remains uncertain, paraphrase neutrally (`沟通中提到...`) or omit it.

## 4. Classify Evidence

Classify each useful item before planning slides:

| Type | Meaning | Publishing rule |
|---|---|---|
| Direct statement | Clearly visible participant message | Quote briefly or paraphrase faithfully |
| Attachment | Document, screenshot, schedule, or link sent in chat | Describe only what is visibly supported |
| Transaction | Payment or order record | Proves the transaction only |
| Editorial inference | Reasonable interpretation of several messages | Label as an interpretation or advice |
| Unknown | Cropped, ambiguous, or OCR-only content | Do not publish as fact |

Do not convert polite acknowledgements such as `好的`, `明白`, or an emoji into testimonials or satisfaction claims.

## 5. Evidence Ledger Template

Create `_work/evidence-ledger.md` with this shape:

```markdown
# Evidence Ledger

## Conversation order
1. `IMG_0001.PNG` -> opens with the learner's goal
2. `IMG_0002.PNG` -> confirms current foundation

## Verified facts
- [source filename + visible region] Fact.

## Speaker map
- Right: ... (confidence: high/medium/low)
- Left: ... (confidence: high/medium/low)

## Editorial themes
- Theme and the screenshots that support it.

## Ambiguities to omit
- Unclear phrase or unsupported outcome.

## Redaction map
- `IMG_0001.PNG`: header name; left avatar; private URL.
```

Keep quotes short. The ledger is an internal audit artifact, not publishing copy.

## 6. Strict Privacy Defaults

Redact these unless the user explicitly establishes that they are public and should remain:

- Contact names, nicknames, avatars, WeChat IDs, profile pages, and personal QR codes.
- Phone numbers, email addresses, street addresses, private booking links, and meeting links.
- Transaction IDs, order numbers, bank details, invoices, and payment QR codes.
- Student numbers, school portals, private timetables, account tokens, and document share links.
- Faces or names of minors and third parties.
- Location, health, family, immigration, or employment details that are not required for the post.

Keep a public creator/brand name only when it is the user's intended publishing identity. Redact the other participant by default.

Add every visible sensitive string to `privacy.blocked_terms`. Include OCR variants when a name could be recognized in more than one way.

## 7. Redaction Method

Use normalized source coordinates `[x, y, width, height]`, with `(0, 0)` at the top-left.

- `solid`: strongest option for names, account IDs, QR codes, and tiny text.
- `pixelate`: suitable for avatars and faces when visual context is useful.
- `blur`: suitable for broad low-detail regions, but increase radius until the text cannot be recovered by eye.

Apply redaction before cropping or resizing. Expand each rectangle slightly beyond the visible glyphs or avatar edge.

Never rely on a crop alone when sensitive text sits close to the crop boundary. Mark `privacy_reviewed: true` only after viewing the rendered slide at full size.

## 8. Relevance Filtering

Exclude screenshots that are:

- Exact or near duplicates.
- Pure acknowledgements with no narrative value.
- Administrative details that add privacy risk but no reader value.
- Superseded by a clearer screenshot of the same exchange.
- Unrelated to the chosen post angle.

Preserve omitted files in the source folder. The final carousel is an editorial selection, not a complete chat archive.
