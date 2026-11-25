#!/usr/bin/env python3
"""Build the English DOS-visual recipe and a verified split-track CHD locally."""

import argparse
import filecmp
import hashlib
import os
from pathlib import Path
import re
import subprocess
import tempfile


JAPANESE_SHA1 = (
    "937ae8cf9a65526f2622c39d34205941f22c10cb",
    "f20f391b0c33e22621cd1c2a13d4171046da1219",
    "635416f6871854ead90c9a6cab2cc4afbe2e0615",
    "04786e51a431ac37910f7b2e3fc5294e44b3664f",
)
PATCHED_SHA1 = "78427bb7dea91c18fc2ca345865983a2ad6cc642"
DISC_NAME = "Ultima Underworld (English Patch - DOS Visuals).chd"
FILE_LINE = re.compile(r'FILE\s+"([^"]+)"\s+BINARY', re.IGNORECASE)


def sha1(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha1").hexdigest()


def read_cue(path):
    """Accept the supported Rev 1 split BIN layout and preserve its index lines."""
    tracks = []
    commands = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.upper().startswith("REM "):
            commands.append(line)
            continue
        match = FILE_LINE.fullmatch(stripped)
        if match:
            track = (path.parent / match[1]).resolve()
            tracks.append(track)
            commands.append(f'FILE "track-{len(tracks)}.bin" BINARY')
            continue
        commands.append(line)
    layout = [" ".join(line.upper().split()) for line in commands
              if line.strip() and not line.strip().upper().startswith("REM ")]
    expected = ['FILE "TRACK-1.BIN" BINARY', "TRACK 01 MODE2/2352", "INDEX 01 00:00:00"]
    for index in (2, 3, 4):
        expected.extend([f'FILE "TRACK-{index}.BIN" BINARY', f"TRACK {index:02} AUDIO",
                         "INDEX 00 00:00:00", "INDEX 01 00:03:00"])
    if layout != expected or len(set(tracks)) != 4:
        raise ValueError("Expected the Japanese Rev 1 split four-track CUE and its original indexes.")
    for track in tracks:
        if not track.is_file() or not track.stat().st_size or track.stat().st_size % 2352:
            raise ValueError(f"Expected a complete 2352-byte-sector BIN: {track}")
    return tracks, "\n".join(commands) + "\n"


def build(args):
    tracks, cue = read_cue(args.japanese_cue)
    for index, (track, expected) in enumerate(zip(tracks, JAPANESE_SHA1, strict=True), 1):
        if sha1(track) != expected:
            raise ValueError(f"Track {index} does not match clean Japanese Rev 1.")
    destination = args.output.resolve()
    if args.output.exists() or args.output.is_symlink():
        raise ValueError("Choose a new output directory.")
    builder = Path(__file__).resolve().with_name("build-local-preview.sh")
    env = os.environ.copy()
    env.pop("XDELTA", None)
    with tempfile.TemporaryDirectory(prefix=".underworld-release-", dir=destination.parent) as directory:
        scratch = Path(directory)
        patch = scratch / "english-dos-visuals.xdelta"
        options = ["--dos-shade-maps"]
        if args.english_patch:
            options.append("--english-patch")
        subprocess.run([builder, *options, args.dos_root.resolve(), tracks[0],
                        args.english_input.resolve(), args.exporter.resolve(), patch], env=env, check=True)

        data_track = scratch / "track-1.bin"
        subprocess.run([env.get("XDELTA3", "xdelta3"), "-d", "-s", tracks[0], patch, data_track],
                       env=env, check=True)
        patched_sha1 = sha1(data_track)
        if patched_sha1 != PATCHED_SHA1:
            raise ValueError(f"Patched Track 1 differs from the qualified recipe: {patched_sha1}")
        for index, track in enumerate(tracks[1:], 2):
            (scratch / f"track-{index}.bin").symlink_to(track)
        cue_path = scratch / "patched.cue"
        cue_path.write_text(cue, encoding="utf-8")
        chd = scratch / DISC_NAME
        chdman = env.get("CHDMAN", "chdman")
        subprocess.run([chdman, "createcd", "-i", cue_path, "-o", chd], check=True)
        subprocess.run([chdman, "verify", "-i", chd], check=True)
        subprocess.run([chdman, "extractcd", "-i", chd, "-o", scratch / "readback.cue",
                        "-ob", scratch / "readback-%t.bin", "-sb"], check=True)
        extracted, _ = read_cue(scratch / "readback.cue")
        for index, (track, copy) in enumerate(zip((data_track, *tracks[1:]), extracted, strict=True), 1):
            if not filecmp.cmp(track, copy, shallow=False):
                raise ValueError(f"CHD readback differs on track {index}.")

        destination.mkdir(mode=0o700)
        published = []
        try:
            for candidate in (patch, chd):
                target = destination / candidate.name
                os.link(candidate, target)
                published.append(target)
        except OSError:
            for target in published:
                target.unlink()
            destination.rmdir()
            raise
        print(f"Verified all four tracks and CUE indexes. Patched Track 1 SHA-1 {patched_sha1}")
        print(f"Local outputs: {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-patch", action="store_true",
                        help="Use the upstream English v2.0 xdelta instead of the translated Track 1 BIN.")
    parser.add_argument("dos_root", type=Path)
    parser.add_argument("japanese_cue", type=Path)
    parser.add_argument("english_input", type=Path)
    parser.add_argument("exporter", type=Path)
    parser.add_argument("output", type=Path, help="New directory for the verified CHD and xdelta.")
    try:
        build(parser.parse_args())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Build failed: {error}\n")


if __name__ == "__main__":
    main()
