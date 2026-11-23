#!/bin/bash
set -euo pipefail

if [[ $# != 4 ]]; then
    echo "Usage: $0 UNDERWORLD_VISUALS DOS_ARCHIVE PSX_AVATAR OUTPUT_DIRECTORY" >&2
    exit 2
fi

tool=$1
archive=$2
avatar=$3
output=$4
seven_zip=${SEVEN_ZIP:-/Applications/7zz}
script_dir=$(cd -- "$(dirname -- "$0")" && pwd)

if [[ ! -x "$tool" || ! -r "$archive" || ! -r "$avatar" || ! -x "$seven_zip" ]]; then
    echo "Provide the built tool, DOS 7z archive, extracted PSX AVATAR file, and an executable 7zz (SEVEN_ZIP)." >&2
    exit 2
fi

temporary=$(mktemp -d)
trap 'rm -rf -- "$temporary"' EXIT
"$seven_zip" x -y "-o$temporary" "$archive" 'ultimaunderworld/uu/CRIT/*' 'ultimaunderworld/uu/DATA/PALS.DAT' >/dev/null
dos_root="$temporary/ultimaunderworld/uu"

mkdir -p -- "$output"
run=$(mktemp -d "$output/comparison.XXXXXX")
mkdir -- "$run/frames" "$run/captures"
"$tool" inspect-psx "$avatar" > "$run/psx-archive.csv"

{
    printf 'actor_id,idle_slot,file,frame_details\n'
    for slot in {32..39}; do
        file="frames/goblin-slot-$slot.png"
        details=$("$tool" export-dos "$dos_root" 70 "$slot" 0 "$run/$file")
        printf '70,%s,%s,"%s"\n' "$slot" "$file" "$details"
    done
    for actor in 96 111 112; do
        file="frames/troll-$actor.png"
        details=$("$tool" export-dos "$dos_root" "$actor" 36 0 "$run/$file")
        printf '%s,36,%s,"%s"\n' "$actor" "$file" "$details"
    done
} > "$run/dos-frames.csv"

cp -- "$script_dir/Compare.html" "$run/Compare.html"
printf '%s\n' "$run"
