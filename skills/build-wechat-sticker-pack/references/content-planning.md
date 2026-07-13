# Dynamic Content Planning for 20 Stickers

Read this reference before generating images. Freeze the completed plan before rendering so filenames, text, meanings, and metadata remain aligned.

## Analyze references

Create `character_bible` and `style_bible` from visible, non-sensitive features:

- primary subject count;
- face shape, hairstyle, glasses, accessories, and recognition anchors;
- one simplified outfit and dominant colors;
- Q-version head/body ratio, line style, palette, shading, and outline treatment.

Do not infer occupation, health, relationships, age, or personality from appearance. When multiple photos show the same subject, reconcile them into one design. Do not merge different identities unless the user requests a group pack.

Default to a soft, playful, everyday-chat voice when no theme is supplied.

## Fill exactly 20 intent roles

Use these as communication functions, not fixed phrases. Write new text, expressions, gestures, and props for the current subject.

Core roles:

1. `greeting.morning`
2. `greeting.hello`
3. `greeting.goodbye`
4. `greeting.goodnight`
5. `social.thanks`
6. `social.apology`
7. `response.agree`
8. `response.praise`
9. `emotion.joy`
10. `reaction.surprise`
11. `reaction.confusion`
12. `emotion.sad`
13. `emotion.angry`
14. `state.sleepy`
15. `action.eat-or-drink`
16. `control.wait-or-busy`
17. `control.reminder`
18. `support.encourage-or-comfort`

Choose two different adaptive roles that do not duplicate the core:

- positive bond: `celebration`, `affection`, `playful-cute`;
- practical/theme: `refusal`, `pleading`, `awkward`, `sneeze`, `cool`, `work-study`, `travel`, `seasonal`, `pet-specific`, or another theme-specific intent.

## Plan schema per item

```json
{
  "id": "01",
  "intent_key": "greeting.morning",
  "category": "greeting",
  "exact_text": "早呀开机啦",
  "meaning_word": "早安",
  "emotion": "bright and awake",
  "pose_action": "waves while stretching",
  "prop": null,
  "framing": "half_body",
  "text_zone": "top",
  "line_break": null,
  "art_prompt": "text-free item-specific art prompt"
}
```

Store the pack voice, theme, character/style bibles, and avoid list. Once generation begins, do not silently change exact text, meaning, intent order, or ID.

## Text rules

For `exact_text`:

- prefer 2–8 Han characters;
- allow at most 10 Han characters and 12 visible glyphs;
- use at most three punctuation glyphs;
- use one line up to six glyphs and plan two lines for longer text;
- avoid emoji, URLs, account names, brands, hashtags, dates, and decorative pseudo-text.

For `meaning_word`:

- use 1–4 Han characters only;
- use no punctuation, spaces, Latin letters, numerals, or emoji;
- describe communication intent, not the pose;
- keep all 20 unique.

Honor user-supplied phrases verbatim when safe and readable. Map them to the nearest roles and generate the remaining roles dynamically.

## Diversity checks

Normalize text with Unicode NFKC, remove spaces/punctuation, collapse repeated characters, and remove sentence-final particles. Reject:

- duplicate or near-duplicate text;
- duplicate intent or meaning;
- semantic paraphrases differing only by punctuation/particles;
- more than three phrases ending with the same particle;
- more than two uses of the same sentence template;
- identical emotion + primary gesture + prop + framing combinations.

Target about eight close/bust compositions, eight half-body compositions, and four full-body compositions. Use props in four to seven items. Reserve a clear text zone that does not overlap faces or gestures.

## Consistency

Generate one neutral text-free master before the 20. Use the original reference(s) plus the same master for every sticker. Never create a recursive chain where each sticker becomes the next sticker's reference.

Repeat the same shared identity/style prefix for all 20; vary only expression, pose/action, prop, framing, and text-zone reservation.

## Hard plan gate

Do not render until all conditions pass:

- exactly 20 items with IDs `01`–`20`;
- unique intent keys, exact texts, normalized stems, meanings, and filenames;
- each meaning is 1–4 Han characters;
- all entries have concrete expression/action and text zone;
- JSON order matches planned final file order.
