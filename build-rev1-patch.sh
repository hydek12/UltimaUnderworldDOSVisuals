#!/bin/bash
set -euo pipefail

expanded=0
if [[ ${1:-} == --allow-expanded-track ]]; then
    expanded=1
    shift
fi

if [[ $# != 3 ]]; then
    echo "Usage: $0 [--allow-expanded-track] JAPANESE_REV1_TRACK1.bin VISUAL_BUILD_TRACK1.bin OUTPUT.xdelta" >&2
    exit 2
fi

source_track=$1
visual_track=$2
output=$3
codec=${XDELTA3:-xdelta3}
japanese_sha1=937ae8cf9a65526f2622c39d34205941f22c10cb
batocera_english_sha1=325585c11548538e323e8896c3fb8b1cc5d65521

fail() {
    printf '%s\n' "$*" >&2
    exit 1
}

sha1() {
    shasum < "$1" | cut -d ' ' -f 1
}

[[ -f "$source_track" && -f "$visual_track" ]] || fail "Both raw Track 1 BIN files are required."
[[ ! -e "$output" && ! -L "$output" ]] || fail "Output already exists: $output"
actual_source=$(sha1 "$source_track")
[[ "$actual_source" == "$japanese_sha1" ]] ||
    fail "Expected the original Japanese Rev 1 Track 1 (SHA-1 $japanese_sha1); found $actual_source."

source_size=$(stat -f %z "$source_track")
visual_size=$(stat -f %z "$visual_track")
(( visual_size % 2352 == 0 )) || fail "Visual Track 1 must contain complete 2352-byte sectors."
if (( visual_size != source_size )); then
    (( expanded && visual_size > source_size )) ||
        fail "Use --allow-expanded-track for a larger data track built for a split-BIN CUE."
fi
actual_visual=$(sha1 "$visual_track")
[[ "$actual_visual" != "$japanese_sha1" && "$actual_visual" != "$batocera_english_sha1" ]] ||
    fail "The visual build matches an existing baseline. Provide a Track 1 with a tested visual edit."

command -v "$codec" >/dev/null || fail "Install xdelta3 or set XDELTA3 to its executable."
unset XDELTA
scratch=$(mktemp -d "$(dirname -- "$output")/.rev1-patch.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT

"$codec" -e -A -s "$source_track" "$visual_track" "$scratch/patch.xdelta"
"$codec" -d -s "$source_track" "$scratch/patch.xdelta" "$scratch/verified.bin"
cmp -s -- "$visual_track" "$scratch/verified.bin" ||
    fail "Round-trip verification failed. Patch was not published."
ln -- "$scratch/patch.xdelta" "$output"
printf 'Japanese Track 1 SHA-1: %s\nVisual Track 1 SHA-1: %s\nPatch: %s\n' "$actual_source" "$actual_visual" "$output"
