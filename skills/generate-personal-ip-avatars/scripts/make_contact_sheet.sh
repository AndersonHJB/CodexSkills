#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 --out OUTPUT.png IMAGE1 IMAGE2 ..." >&2
  exit 2
}

[[ "${1:-}" == "--out" ]] || usage
[[ -n "${2:-}" ]] || usage

output_path="$2"
shift 2
[[ "$#" -gt 0 ]] || usage

command -v magick >/dev/null 2>&1 || {
  echo "ImageMagick is required to create the contact sheet." >&2
  exit 127
}

for image_path in "$@"; do
  [[ -f "$image_path" ]] || {
    echo "Missing input image: $image_path" >&2
    exit 1
  }
done

mkdir -p "$(dirname "$output_path")"
magick montage "$@" \
  -thumbnail 512x512 \
  -tile 4x \
  -geometry 512x512+16+16 \
  -background '#f4efe6' \
  "$output_path"

echo "$(cd "$(dirname "$output_path")" && pwd)/$(basename "$output_path")"
