"""Package and verify Japanese Rev 1 split-track builds."""
import filecmp
import hashlib
from pathlib import Path
import re
import subprocess

JAPANESE_SHA1 = (
    "937ae8cf9a65526f2622c39d34205941f22c10cb",
    "f20f391b0c33e22621cd1c2a13d4171046da1219",
    "635416f6871854ead90c9a6cab2cc4afbe2e0615",
    "04786e51a431ac37910f7b2e3fc5294e44b3664f",
)
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


def package_chd(tracks, cue, data_track, scratch, chd, chdman):
    if data_track != scratch / "track-1.bin":
        (scratch / "track-1.bin").symlink_to(data_track.resolve())
    for index, track in enumerate(tracks[1:], 2):
        (scratch / f"track-{index}.bin").symlink_to(track)
    cue_path = scratch / "patched.cue"
    cue_path.write_text(cue, encoding="utf-8")
    subprocess.run([chdman, "createcd", "-i", cue_path, "-o", chd], check=True)
    subprocess.run([chdman, "verify", "-i", chd], check=True)
    subprocess.run([chdman, "extractcd", "-i", chd, "-o", scratch / "readback.cue",
                    "-ob", scratch / "readback-%t.bin", "-sb"], check=True)
    extracted, _ = read_cue(scratch / "readback.cue")
    for index, (track, copy) in enumerate(zip((data_track, *tracks[1:]), extracted, strict=True), 1):
        if not filecmp.cmp(track, copy, shallow=False):
            raise ValueError(f"CHD readback differs on track {index}.")
