"""Merge the Lanugo atlas into the verified English v2.0 Rev 1 data track."""
import argparse
import hashlib
from pathlib import Path
import shutil
import struct

import build_track as lanugo

ENGLISH_SHA1 = "325585c11548538e323e8896c3fb8b1cc5d65521"

def bcd(number):
    return ((number // 10) << 4) | (number % 10)

def build(english, atlas, output, walk_atlas=None):
    with english.open("rb") as source:
        if hashlib.file_digest(source, "sha1").hexdigest() != ENGLISH_SHA1:
            raise ValueError("Expected the verified English v2.0 raw data track.")
        source.seek(0, 2)
        first_lba, remainder = divmod(source.tell(), lanugo.SECTOR_SIZE)
        if remainder:
            raise ValueError("Incomplete raw data sector.")
        payload = lanugo.payload(atlas, walk_atlas)
        sectors = [
            lanugo.read_sector(source, lba)
            for lba in range(lanugo.EXE_LBA, lanugo.EXE_LBA + 761856 // 2048)
        ]
        executable = b"".join(sector[24:2072] for sector in sectors)
        edited = lanugo.edit_executable(executable, first_lba, walking=walk_atlas is not None)
        updates = {}
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
    build(**vars(parser.parse_args()))
