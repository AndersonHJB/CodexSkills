#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  printf 'Usage: %s <parts-directory> <output.mp3>\n' "$0" >&2
  exit 2
fi

parts_dir=$1
output=$2
list_file=$(mktemp -t cola-mp3-list.XXXXXX)
trap 'rm -f "$list_file"' EXIT

find "$parts_dir" -maxdepth 1 -type f -name '*.mp3' | sort > "$list_file.raw"
trap 'rm -f "$list_file" "$list_file.raw"' EXIT

if [ ! -s "$list_file.raw" ]; then
  printf 'No MP3 parts found in %s\n' "$parts_dir" >&2
  exit 1
fi

while IFS= read -r file; do
  printf "file '%s'\n" "$file" >> "$list_file"
done < "$list_file.raw"

mkdir -p "$(dirname "$output")"
ffmpeg -y -f concat -safe 0 -i "$list_file" -c copy "$output"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 "$output"
