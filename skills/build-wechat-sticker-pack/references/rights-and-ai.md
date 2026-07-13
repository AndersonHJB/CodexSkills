# Rights, Portrait Consent, and AI Disclosure

## Personal default

The bundled creator profile is a convenience for this user, not proof of ownership. Use its copyright value only for privately supplied, self-owned references when the user gives no contrary information.

## Rights gate

- Preserve the exact copyright name from the user/profile. Do not add “工作室”, “原创”, “©”, or other ownership claims.
- Treat a privately uploaded self-reference as authorized only under the profile's stated assumption.
- Ask before submission-ready packaging when the reference is a public figure, third-party artwork/photo, branded IP, downloaded media, another identifiable person, or the user mentions missing permission.
- When the subject is not the submitter, require real portrait consent or authorization.
- If rights are unresolved, allow draft generation and archival packaging but set `rights_confirmed: false`, block the upload-only archive, and report the exact gap.

## AI record

Always set `ai_generated: true` because built-in image generation creates the Q-version art. Generate a declaration recording:

- reference photos were used as visual identity references;
- Q-version illustrations and publication artwork were AI-generated;
- exact Chinese typography, resizing, transparency processing, validation, and packaging were performed locally;
- the user must select AI-generated/AI-assisted if the platform exposes that option.

Do not add visible AI disclosure text to assets that prohibit text. Use platform disclosure controls.

## Privacy

- Submission-only packages must exclude reference photos, EXIF, GPS, raw generation files, prompts, state, and absolute local paths.
- Full archives intentionally preserve original bytes and may preserve EXIF/GPS. Mention this in the full-archive QA.
- Derived submission images must strip EXIF and other metadata.
