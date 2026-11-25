#!/usr/bin/env python3
"""Build the English DOS-visual recipe and a verified split-track CHD locally."""

import argparse
import os
from pathlib import Path
import subprocess
import tempfile

from lanugo.disc_image import DISC_NAME, JAPANESE_SHA1, package_chd, read_cue, sha1


PATCHED_SHA1 = "e29e66fb895387c304b4c47c945e2876b24c87a9"


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
    env["UW_SKIP_BATOCERA"] = "1"
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
        chd = scratch / DISC_NAME
        package_chd(tracks, cue, data_track, scratch, chd, env.get("CHDMAN", "chdman"))

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
