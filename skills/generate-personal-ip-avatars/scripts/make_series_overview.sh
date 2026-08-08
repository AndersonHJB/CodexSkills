#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--out" || $# -ne 11 ]]; then
  echo "Usage: $0 --out OUTPUT.png CLASSIC.png THEME01.png ... THEME08.png" >&2
  exit 2
fi

output_path="$2"
shift 2

if ! command -v magick >/dev/null 2>&1; then
  echo "ImageMagick 'magick' is required." >&2
  exit 1
fi

for input_path in "$@"; do
  if [[ ! -f "$input_path" ]]; then
    echo "Missing overview: $input_path" >&2
    exit 1
  fi
done

mkdir -p "$(dirname "$output_path")"
magick montage "$@" \
  -thumbnail '1088x544>' \
  -tile 3x3 \
  -geometry '+16+16' \
  -background '#f2f2f2' \
  "$output_path"

echo "$output_path"
