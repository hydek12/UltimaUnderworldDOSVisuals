"""Package a verified preview and replace the existing local Batocera game image."""

import argparse
import filecmp
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from disc_image import DISC_NAME, JAPANESE_SHA1, package_chd, read_cue, sha1


def deploy(args):
    share = args.share.resolve(strict=True)
    if not os.path.ismount(share):
        raise ValueError(f"Batocera share is not mounted: {share}")
    destination = share / "roms" / "psx" / DISC_NAME
    if not destination.is_file() or destination.is_symlink():
        raise ValueError(f"Expected the existing Batocera game image: {destination}")
    tracks, cue = read_cue(args.cue)
    if tracks[0] != args.source.resolve() or tuple(map(sha1, tracks)) != JAPANESE_SHA1:
        raise ValueError("The deployment CUE must refer to the clean Japanese Rev 1 build inputs.")

    with tempfile.TemporaryDirectory(prefix="underworld-preview-chd-") as directory:
        scratch = Path(directory)
        chd = scratch / DISC_NAME
        package_chd(tracks, cue, args.preview, scratch, chd, args.chdman)
        # Copy data bytes only. SMB can reject macOS extended attributes.
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".uw1-preview-", delete=False) as stage:
            staged = Path(stage.name)
            try:
                with chd.open("rb") as source:
                    shutil.copyfileobj(source, stage)
                stage.close()
                if not filecmp.cmp(chd, staged, shallow=False):
                    raise ValueError("Batocera staging copy differs from the verified CHD.")
                staged.replace(destination)
                if not filecmp.cmp(chd, destination, shallow=False):
                    raise ValueError("Installed Batocera image differs from the verified CHD.")
            finally:
                staged.unlink(missing_ok=True)
    print(f"Verified Batocera preview: {destination}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("share", type=Path)
    parser.add_argument("cue", type=Path)
    parser.add_argument("source", type=Path)
    parser.add_argument("preview", type=Path)
    parser.add_argument("chdman")
    try:
        deploy(parser.parse_args())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Batocera deployment failed. The local preview xdelta is available. {error}\n")


if __name__ == "__main__":
    main()
