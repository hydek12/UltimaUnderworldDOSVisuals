#!/bin/bash
set -euo pipefail

translation_patch=0
if [[ ${1:-} == --english-patch ]]; then
    translation_patch=1
    shift
fi

if [[ $# != 5 ]]; then
    printf 'Usage: %s [--english-patch] DOS_ROOT JAPANESE_REV1_TRACK1.bin ENGLISH_INPUT UNDERWORLD_VISUALS OUTPUT.xdelta\n' "$0" >&2
    exit 2
fi

project=$(cd -- "$(dirname -- "$0")" && pwd)
dos_root=$1
japanese_track=$2
english_input=$3
english_track=$english_input
exporter=$4
output=$5

if [[ ! -d "$dos_root/CRIT" || ! -x "$exporter" || ! -f "$japanese_track" || ! -f "$english_input" ]]; then
    printf 'Select the extracted DOS folder containing CRIT, the clean Track 1 BIN, the English input, and the built UnderworldVisuals executable.\n' >&2
    exit 1
fi
if [[ -e "$output" || -L "$output" || ! -d "$(dirname -- "$output")" ]]; then
    printf 'Choose a new output file in an existing directory.\n' >&2
    exit 1
fi

umask 077
scratch=$(mktemp -d "${TMPDIR:-/tmp}/underworld-local.XXXXXX")
trap 'rm -rf -- "$scratch"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if (( translation_patch )); then
    japanese_sha1=$(shasum < "$japanese_track" | cut -d ' ' -f 1)
    if [[ "$japanese_sha1" != 937ae8cf9a65526f2622c39d34205941f22c10cb ]]; then
        printf 'The translation patch requires clean Japanese Rev 1 Track 1.\n' >&2
        exit 1
    fi
    english_track=$scratch/english.bin
    printf 'Applying the supplied translation patch locally…\n'
    env -u XDELTA "${XDELTA3:-xdelta3}" -d -s "$japanese_track" "$english_input" "$english_track"
fi

printf 'Exporting creature sprites from the selected DOS installation…\n'
"$exporter" export-lanugo-tim "$dos_root" "$scratch/idle"
"$exporter" export-lanugo-walk-tim "$dos_root" "$scratch/walk"
mkdir "$scratch/goblins" "$scratch/lizardmen" "$scratch/rats"
for actor in 76 77 78; do
    "$exporter" export-goblin-atlases "$dos_root" "$actor" "$scratch/goblins/type-$actor"
done
for actor in 85 88 89; do
    "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/lizardmen/type-$actor" --lizardman-combat
done
"$exporter" export-creature-atlases "$dos_root" 72 "$scratch/rats/type-72"

printf 'Building the English preview data track…\n'
PYTHONDONTWRITEBYTECODE=1 python3 "$project/lanugo/build_english.py" "$english_track" "$scratch/idle" "$scratch/preview.bin" \
    --walk-atlas "$scratch/walk" --goblin-variants "$scratch/goblins" --lower-floor-goblins \
    --lizardmen "$scratch/lizardmen" --lizardman-combat --level-eight-rats "$scratch/rats"

printf 'Encoding and verifying the local xdelta…\n'
"$project/build-rev1-patch.sh" --allow-expanded-track "$japanese_track" "$scratch/preview.bin" "$output"
