#!/bin/bash
set -euo pipefail

native_sprite_lighting=0
if [[ ${1:-} == --native-sprite-lighting ]]; then
    native_sprite_lighting=1
    shift
    set -- --slasher-combat "$@"
fi

slasher_combat=0
if [[ ${1:-} == --slasher-combat ]]; then
    slasher_combat=1
    shift
    set -- --late-dialogue "$@"
fi

academy_bank=
level_one_dialogue=0
level_two_dialogue=0
level_three_dialogue=0
level_four_dialogue=0
late_dialogue=0
expanded_preview=0
effects_preview=0
combat_preview=0
casting_preview=0
spider_preview=0
wizard_preview=0
if [[ ${1:-} == --level-six-wizards ]]; then
    wizard_preview=1
    shift
elif [[ ${1:-} == --level-six-spiders ]]; then
    wizard_preview=1
    spider_preview=1
    shift
elif [[ ${1:-} == --level-six-casting ]]; then
    wizard_preview=1
    spider_preview=1
    casting_preview=1
    shift
elif [[ ${1:-} == --level-six-combat || ${1:-} == --level-six-effects || ${1:-} == --level-six-expanded || ${1:-} == --academy-wizb || ${1:-} == --academy-wizc || ${1:-} == --academy-runtime || ${1:-} == --level-one-dialogue || ${1:-} == --level-two-dialogue || ${1:-} == --level-three-dialogue || ${1:-} == --level-four-dialogue || ${1:-} == --late-dialogue ]]; then
    if [[ $1 == --level-six-expanded || $1 == --academy-* || $1 == --level-one-dialogue || $1 == --level-two-dialogue || $1 == --level-three-dialogue || $1 == --level-four-dialogue || $1 == --late-dialogue ]]; then
        expanded_preview=1
    fi
    if [[ $1 == --level-one-dialogue || $1 == --level-two-dialogue || $1 == --level-three-dialogue || $1 == --level-four-dialogue || $1 == --late-dialogue ]]; then
        academy_bank=runtime
        level_one_dialogue=1
        if [[ $1 != --level-one-dialogue ]]; then level_two_dialogue=1; fi
        if [[ $1 == --level-three-dialogue || $1 == --level-four-dialogue || $1 == --late-dialogue ]]; then level_three_dialogue=1; fi
        if [[ $1 == --level-four-dialogue || $1 == --late-dialogue ]]; then level_four_dialogue=1; fi
        if [[ $1 == --late-dialogue ]]; then late_dialogue=1; fi
    elif [[ $1 == --academy-* ]]; then
        academy_bank=${1#--academy-}
    fi
    if [[ $1 != --level-six-combat ]]; then
        effects_preview=1
    fi
    wizard_preview=1
    spider_preview=1
    casting_preview=1
    combat_preview=1
    shift
fi

translation_patch=0
if [[ ${1:-} == --english-patch ]]; then
    translation_patch=1
    shift
fi

if [[ $# != 5 ]]; then
    printf 'Usage: %s [--level-six-wizards|--level-six-spiders|--level-six-casting|--level-six-combat|--level-six-effects|--level-six-expanded|--academy-wizb|--academy-wizc|--academy-runtime|--level-one-dialogue|--level-two-dialogue|--level-three-dialogue|--level-four-dialogue|--late-dialogue|--slasher-combat|--native-sprite-lighting] [--english-patch] DOS_ROOT JAPANESE_REV1_TRACK1.bin ENGLISH_INPUT UNDERWORLD_VISUALS OUTPUT.xdelta\n' "$0" >&2
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

wizard_args=()
if (( wizard_preview )); then
    mkdir "$scratch/wizards"
    for actor in 103 108 109; do
        "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
    done
    wizard_args=(--level-six-wizards "$scratch/wizards")
    if (( casting_preview )); then
        wizard_export=export-wizard-casting
        if (( combat_preview )); then
            wizard_export=export-wizard-combat
            wizard_args+=(--level-six-combat)
        fi
        for actor in 103 108 109; do
            "$exporter" "$wizard_export" "$dos_root" "$actor" "$scratch/wizards/type-$actor/combat"
        done
        wizard_args+=(--level-six-casting)
    fi
    if (( spider_preview )); then
        "$exporter" export-creature-atlases "$dos_root" 92 "$scratch/wizards/type-92"
        wizard_args+=(--level-six-spiders)
    fi
fi

if (( expanded_preview )); then
    case $academy_bank in
        wizb) directional_actors=(106 115) ;;
        wizc) directional_actors=(107) ;;
        runtime) directional_actors=(64 65 66 69 73 74 75 81 82 91 97 102 105 106 107 111 112 115 119 120) ;;
        *) directional_actors=(64 65 66 69 73 82) ;;
    esac
    for actor in "${directional_actors[@]}"; do
        "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
    done
    wizard_args+=(--expanded-level-six)
    if [[ $academy_bank == runtime ]]; then
        for actor in 74 75 81 91 105; do
            "$exporter" export-creature-combat "$dos_root" "$actor" "$scratch/wizards/type-$actor/combat"
        done
        wizard_args+=(--academy-runtime)
        if (( level_one_dialogue )); then
            for actor in 71 80 90; do
                "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
            done
            wizard_args+=(--level-one-dialogue)
            if (( level_two_dialogue )); then
                for actor in 84 86 98; do
                    "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
                done
                wizard_args+=(--level-two-dialogue)
                if (( level_three_dialogue )); then
                    for actor in 85 88 89 93 94 104; do
                        "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
                    done
                    wizard_args+=(--level-three-dialogue)
                    if (( level_four_dialogue )); then
                        for actor in 95 96; do
                            "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
                        done
                        wizard_args+=(--level-four-dialogue)
                        if (( late_dialogue )); then
                            for actor in 67 68 72 83 79 87 99 100 101 110 113 114 116 117 118 121 122 123 124 125 126; do
                                "$exporter" export-creature-atlases "$dos_root" "$actor" "$scratch/wizards/type-$actor"
                            done
                            if (( slasher_combat )); then
                                "$exporter" export-creature-combat "$dos_root" 124 "$scratch/wizards/type-124/combat"
                                wizard_args+=(--slasher-combat)
                            fi
                            if (( native_sprite_lighting )); then
                                wizard_args+=(--native-sprite-lighting)
                            fi
                            wizard_args+=(--late-dialogue)
                        fi
                    fi
                fi
            fi
        fi
    elif [[ -n $academy_bank ]]; then
        wizard_args+=(--academy-bank "$academy_bank")
    fi
fi

if (( effects_preview )); then
    "$exporter" export-dos-spell-effects "$dos_root" "$scratch/spell-effects"
    wizard_args+=(--dos-spell-effects "$scratch/spell-effects")
fi

printf 'Building the English preview data track…\n'
PYTHONDONTWRITEBYTECODE=1 python3 "$project/lanugo/build_english.py" "$english_track" "$scratch/idle" "$scratch/preview.bin" \
    --walk-atlas "$scratch/walk" --goblin-variants "$scratch/goblins" --lower-floor-goblins \
    --lizardmen "$scratch/lizardmen" --lizardman-combat --level-eight-rats "$scratch/rats" ${wizard_args[@]+"${wizard_args[@]}"}

printf 'Encoding and verifying the local xdelta…\n'
"$project/build-rev1-patch.sh" --allow-expanded-track "$japanese_track" "$scratch/preview.bin" "$output"
