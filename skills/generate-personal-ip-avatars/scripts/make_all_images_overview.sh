#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" != "--out" || $# -lt 4 ]]; then
  echo "Usage: $0 --out OUTPUT.png IMAGE1.png IMAGE2.png [...]" >&2
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
    echo "Missing original image: $input_path" >&2
    exit 1
  fi
  if [[ "$input_path" == "$output_path" ]]; then
    echo "Output must not be included as an input." >&2
    exit 1
  fi
done

mkdir -p "$(dirname "$output_path")"
image_count=$#
columns=8
thumbnail=320
if (( image_count > 200 )); then
  columns=16
  thumbnail=240
elif (( image_count > 100 )); then
  columns=12
  thumbnail=280
fi

magick montage "$@" \
  -thumbnail "${thumbnail}x${thumbnail}>" \
  -tile "${columns}x" \
  -geometry '+8+8' \
  -background '#f2f2f2' \
  "$output_path"

echo "$output_path"
