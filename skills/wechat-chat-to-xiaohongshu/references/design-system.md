# Screenshot Editorial Design System

## Canvas and Safe Area

- Render final slides at 1080 x 1440 pixels (3:4).
- Keep primary text at least 64 px from the left and right edges.
- Keep important content out of the bottom 72 px.
- Use stable header, content, and footer bands across the carousel.
- Keep screenshots large enough that key chat text remains readable on a phone.

## Visual Direction

Default to a quiet editorial notebook style suitable for real records:

- Warm paper background: `#F7F3EA`.
- Ink: `#20231F`.
- Muted text: `#62675F`.
- Coral accent: `#D9573F`.
- Leaf green: `#4E6B45`.
- Mustard accent: `#D7A928`.
- White/source panel: `#FFFDF8`.

Use the palette as a balanced system, not as a single-hue theme. Avoid blue-purple gradients, decorative blobs, heavy shadows, and marketing-dashboard UI.

## Typography

Prefer PingFang SC, Hiragino Sans GB, or STHeiti. Use a bold Chinese sans serif for headlines and a regular face for explanatory copy.

Recommended rendered sizes:

- Cover headline: 78-96 px.
- Content headline: 60-76 px.
- Subtitle: 30-36 px.
- Callout title: 30-36 px.
- Callout body: 25-30 px.
- Footer and page number: 22-26 px.

Never reduce body copy below 24 px. Shorten the copy or split the slide instead.

Use normal letter spacing. Keep headline line count to two when possible.

## Layout Selection

### `cover`

Use for the first slide. Lead with a literal topic or audience signal, not a mysterious slogan. Pair one strong source image or screenshot with 2-4 compact badges or callouts.

### `chat-left`

Place the screenshot on the left and analysis on the right. Use when the screenshot is the primary evidence and the annotations form a short checklist.

### `chat-right`

Mirror the structure to vary rhythm. Use when the callout should be read before the screenshot.

### `chat-full`

Center a single screenshot at the largest practical size. Use when the screenshot itself carries most of the meaning and only a short takeaway is needed.

Alternate left and right layouts deliberately. Do not switch layouts on every slide if it harms continuity.

## Screenshot Treatment

- Preserve the original screenshot aspect ratio unless a planned crop isolates the relevant exchange.
- Do not stretch screenshots.
- Crop redundant status bars or input areas only after privacy and context review.
- Use a thin neutral border and restrained shadow to separate dark-mode chats from the background.
- Keep the screenshot untouched except for crop, redaction, scaling, and modest tonal correction.
- Never repaint chat bubbles or replace chat text with generated text.

When one screenshot is too dense, crop to the key exchange and add the original filename to the evidence ledger. Avoid showing multiple tiny screenshots merely to prove completeness.

## Callouts

Use 1-4 callouts per slide. Separate them with rules or accent bars instead of stacking decorative cards. Each callout should explain interpretation, reader value, or a practical next step.

Do not add icons unless they convey a familiar concept and match the visual system. Avoid random stickers, fake handwriting, and decorative labels that compete with the evidence.

## Generated Assets

Use an image model only when a real source image cannot carry the cover or the user requests an illustrated style. Keep generated assets outside the chat screenshot. Composite them as a background or supporting visual, then verify that they contain no invented chat text, QR codes, watermarks, or random English.

## Carousel Rhythm

- Slide 1: strongest topic signal and readable hook.
- Slides 2-3: context and tension.
- Middle: method, evidence, and decisions.
- Final slide: reusable takeaway and optional CTA.

Keep a stable series label, headline position, page counter, and footer. Vary screenshot side, accent color, and callout density modestly.

## Visual QA

Inspect individual slides at full size and the overview sheet at a reduced size.

Check:

- Cover topic remains clear in the overview.
- No headline, callout, screenshot, or page number overlaps another element.
- Screenshot text is legible at typical phone scale.
- No slide is much denser or emptier than adjacent slides without intent.
- All redactions remain opaque after scaling.
- Every slide uses the same canvas, margins, typography family, and footer logic.
- No visible private names, avatars, IDs, links, QR codes, or payment details remain.
