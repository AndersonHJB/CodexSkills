# Offline selection gallery

Read this reference when `selection_gallery` is enabled.

## Behavior

- Build one offline HTML page after all originals and collages pass QA.
- Include every delivered original exactly once. Never include overview images, previews, discarded variants, style references, or the HTML page itself.
- Use `scripts/build_selection_gallery.py`; do not hand-author hundreds of image tags.
- Keep image paths relative to the HTML file so the output folder can be moved as a unit.
- For expansion sets whose frozen originals live outside the output root, pass their SHA manifest with `--sha-manifest` and the common project directory with `--workspace-root`.
- Pass `--expected-count` using the resolved delivered-original count. A mismatch must fail instead of silently producing an incomplete gallery.

## Required interaction

The page must provide search, category and series filters, responsive density, lazy-loaded thumbnails, full-image modal preview, previous/next navigation, shortlist, reject, persistent local selection, reset, and JSON export. It must work when opened directly with `file://`; no application server or build step is required.

## Design and license

The bundled template adapts the App scene from `esther-design-system` by ESTHER不二. Preserve the visible attribution and hidden signature, the CC BY-NC-SA 4.0 notice, and non-commercial-use statement. Do not remove the attribution when customizing the gallery. Keep the warm paper background, blue/yellow/red hierarchy, serif headings, sans-serif body, responsive layout, reduced-motion support, and non-generic editorial character.

## Command

```bash
python3 scripts/build_selection_gallery.py \
  --root /absolute/output-root \
  --output /absolute/output-root/00-selection-gallery.html \
  --expected-count 459
```

Add `--sha-manifest /absolute/BASELINE-SHA256.txt --workspace-root /absolute/project` in expansion mode.

## QA

- Parse the embedded JSON and verify its image count equals the resolved original count.
- Confirm every referenced file exists relative to the HTML page.
- Confirm no overview/preview path appears.
- Open the file in a browser at desktop and mobile widths.
- Exercise search, one category filter, one series filter, shortlist, reject, modal navigation, reload persistence, reset, and exported JSON.
