"""Add DOS creature sprites to the verified English v2.0 Rev 1 data track."""
import argparse
import hashlib
from pathlib import Path
import shutil
import struct

import build_track as lanugo
import spell_effects

ENGLISH_SHA1 = "325585c11548538e323e8896c3fb8b1cc5d65521"

def bcd(number):
    return ((number // 10) << 4) | (number % 10)

def build(english, atlas, output, walk_atlas=None, goblin_variants=None,
          dos_light_preview=None, lower_floor_goblins=False, lizardmen=None, lizardman_combat=False, level_eight_rats=None,
          level_six_wizards=None, level_six_spiders=False, level_six_casting=False, level_six_combat=False,
          dos_spell_effects=None, expanded_level_six=False, academy_bank=None, academy_runtime=False):
    if (academy_bank or academy_runtime) and (not expanded_level_six or level_six_wizards is None):
        raise ValueError("An Academy bank requires the expanded Level 6 atlas.")
    if academy_bank and academy_runtime:
        raise ValueError("Choose a single Academy bank or runtime switching.")
    if expanded_level_six and not level_six_combat:
        raise ValueError("The expanded Level 6 atlas requires the wizard combat preview.")
    if level_six_combat and not level_six_casting:
        raise ValueError("Wizard combat extends the casting preview.")
    if level_six_casting and not level_six_spiders:
        raise ValueError("The casting preview requires the combined Level 6 payload.")
    if level_six_spiders and level_six_wizards is None:
        raise ValueError("Level 6 spiders share the Level 6 wizard payload.")
    if lizardman_combat and lizardmen is None:
        raise ValueError("Lizardman combat requires --lizardmen.")
    with english.open("rb") as source:
        if hashlib.file_digest(source, "sha1").hexdigest() != ENGLISH_SHA1:
            raise ValueError("Expected the verified English v2.0 raw data track.")
        source.seek(0, 2)
        first_lba, remainder = divmod(source.tell(), lanugo.SECTOR_SIZE)
        if remainder:
            raise ValueError("Incomplete raw data sector.")
        lower_payload_lba = None
        lizard_payload_lba = None
        rat_payload_lba = None
        wizard_payload_lba = None
        creature_atlases = (lizardmen, level_eight_rats, level_six_wizards)
        if lower_floor_goblins or any(atlases is not None for atlases in creature_atlases):
            if walk_atlas is None or goblin_variants is None:
                raise ValueError("Floor-specific atlases require both --walk-atlas and --goblin-variants.")
            payload = lanugo.variant_payload(atlas, walk_atlas, goblin_variants, dos_light_preview, floor_aware=True)
            if lower_floor_goblins:
                lower_payload_lba = first_lba + len(payload) // 2048
                payload += lanugo.lower_floor_payload(goblin_variants)
            if lizardmen is not None:
                lizard_payload_lba = first_lba + len(payload) // 2048
                payload += lanugo.lizard_payload(lizardmen, lizardman_combat)
            if level_eight_rats is not None:
                rat_payload_lba = first_lba + len(payload) // 2048
                payload += lanugo.rat_payload(level_eight_rats)
            if level_six_wizards is not None:
                wizard_payload_lba = first_lba + len(payload) // 2048
                banks = (None, *lanugo.academy_banks.BANK_FAMILIES) if academy_runtime else (academy_bank,)
                bank_size = 0x12800
                for bank_id, bank in enumerate(banks):
                    bank_sections = None
                    if academy_runtime:
                        byte_offset = (wizard_payload_lba - lanugo.AVATAR_LBA) * 2048
                        bank_sections = lanugo.academy_banks.sections(byte_offset, bank_size, bank_id)
                    bank_payload = lanugo.creature_payload(
                        level_six_wizards, lanugo.creature_atlas.LEVEL_SIX_WIZARD_TYPES,
                        lanugo.creature_atlas.TEXTURE_PAGES[:1],
                        extra_type=lanugo.creature_atlas.LEVEL_SIX_SPIDER_TYPE if level_six_spiders else None,
                        casting=level_six_casting, combat=level_six_combat, expanded_level_six=expanded_level_six,
                        academy_bank=bank, academy_sections=bank_sections,
                    )
                    if academy_runtime and len(bank_payload) != bank_size:
                        raise ValueError("The runtime Academy banks must have the same disc stride.")
                    payload += bank_payload
        else:
            payload = lanugo.payload(atlas, walk_atlas, goblin_variants, dos_light_preview)
        if expanded_level_six:
            image = bytearray(payload)
            restore = lanugo.menu_return(lanugo.VARIANT_UPLOAD_RAM, True, dialogue=True)
            if len(restore) > 0x80:
                raise ValueError("The dialogue return hook overlaps the VRAM guard.")
            restore_lbas = [first_lba, lower_payload_lba, lizard_payload_lba, rat_payload_lba, wizard_payload_lba]
            if academy_runtime:
                restore_lbas.extend(wizard_payload_lba + i * (bank_size // 2048) for i in range(1, len(banks)))
            for lba in restore_lbas:
                if lba is not None:
                    start = (lba - first_lba) * 2048 + 0xe00
                    image[start:start + len(restore)] = restore
            payload = image
        sectors = [
            lanugo.read_sector(source, lba)
            for lba in range(lanugo.EXE_LBA, lanugo.EXE_LBA + 761856 // 2048)
        ]
        executable = b"".join(sector[24:2072] for sector in sectors)
        edited = lanugo.edit_executable(
            executable, first_lba, walking=walk_atlas is not None, wide=goblin_variants is not None,
            lower_payload_lba=lower_payload_lba, lizard_payload_lba=lizard_payload_lba, rat_payload_lba=rat_payload_lba,
            wizard_payload_lba=wizard_payload_lba, expanded_level_six=expanded_level_six,
            academy_runtime=academy_runtime,
        )
        updates = {}
        if dos_spell_effects is not None:
            edited = spell_effects.apply(source, edited, updates, dos_spell_effects)
        for index, original in enumerate(sectors):
            start = index * 2048
            data = edited[start:start + 2048]
            if data != original[24:2072]:
                if lanugo.form1_sector(original, original[24:2072]) != original:
                    raise ValueError("Original executable sector failed integrity check.")
                updates[lanugo.EXE_LBA + index] = lanugo.form1_sector(original, data)
        volume = lanugo.read_sector(source, 16)
        descriptor = bytearray(volume[24:2072])
        if descriptor[:7] != b"\x01CD001\x01" or struct.unpack_from("<I", descriptor, 80)[0] != first_lba:
            raise ValueError("Unexpected ISO volume descriptor.")
        if lanugo.form1_sector(volume, descriptor) != volume:
            raise ValueError("Original volume descriptor failed integrity check.")
        descriptor[40:72] = b"ULTIMA UNDERWORLD ENGLISH PATCH".ljust(32)
        count = len(payload) // 2048
        struct.pack_into("<I", descriptor, 80, first_lba + count)
        struct.pack_into(">I", descriptor, 84, first_lba + count)
        updates[16] = lanugo.form1_sector(volume, descriptor)
        template = bytearray(volume)
        template[16:24] = bytes(8)
        for index in range(count):
            lba = first_lba + index
            minute, rest = divmod(lba + 150, 4500)
            second, frame = divmod(rest, 75)
            template[12:15] = bytes(map(bcd, (minute, second, frame)))
            start = index * 2048
            updates[lba] = lanugo.form1_sector(template, payload[start:start + 2048])
        with output.open("xb") as target:
            source.seek(0)
            shutil.copyfileobj(source, target, 1024 * 1024)
            for lba, sector in updates.items():
                lanugo.write_sector(target, lba, sector)
        print(f"Modified LBAs {sorted(updates)}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("english", type=Path)
    parser.add_argument("atlas", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--walk-atlas", type=Path)
    parser.add_argument("--goblin-variants", type=Path)
    parser.add_argument("--dos-light-preview", type=Path, metavar="DOS_ROOT")
    parser.add_argument("--lower-floor-goblins", action="store_true")
    parser.add_argument("--lizardmen", type=Path, metavar="EXPORTED_ATLASES")
    parser.add_argument("--lizardman-combat", action="store_true")
    parser.add_argument("--level-eight-rats", type=Path, metavar="EXPORTED_ATLASES")
    parser.add_argument("--level-six-wizards", type=Path, metavar="EXPORTED_ATLASES")
    parser.add_argument("--level-six-spiders", action="store_true")
    parser.add_argument("--level-six-casting", action="store_true")
    parser.add_argument("--level-six-combat", action="store_true")
    parser.add_argument("--dos-spell-effects", type=Path, metavar="EXPORTED_EFFECTS")
    parser.add_argument("--expanded-level-six", action="store_true")
    parser.add_argument("--academy-bank", choices=lanugo.LEVEL_SIX_ACADEMY)
    parser.add_argument("--academy-runtime", action="store_true")
    build(**vars(parser.parse_args()))
