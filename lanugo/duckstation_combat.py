#!/usr/bin/env python3
"""Inspect nearby actors and stage defeats in a disposable UW PSX session."""

import argparse
from dataclasses import dataclass
from math import hypot
import socket
from struct import unpack_from
from threading import Timer


FRAME = 0x80061CC8
DAMAGE = 0x8002DC78
POSITION = 0x801D9700
ACTOR_TABLE = 0x800C9E14
PLAYER = 0x800C9F90
TILE = 256
RECORD = 28
ATTITUDE_CHECK = 0x80025F2C
TYPES = {
    72: "Giant rat",
    81: "Mongbat",
    82: "Bloodworm",
    91: "Headless",
    114: "Earth golem",
    120: "Fire elemental",
}


class Remote:
    """DuckStation's acknowledged GDB remote protocol on localhost."""

    def __init__(self, port):
        self.socket = socket.create_connection(("127.0.0.1", port), timeout=5)
        self.stream = self.socket.makefile("rb")

    def close(self):
        self.stream.close()
        self.socket.close()

    def command(self, command):
        body = command.encode("ascii")
        self.socket.sendall(b"$" + body + f"#{sum(body) & 255:02x}".encode())
        while (byte := self.stream.read(1)) != b"$":
            if not byte:
                raise RuntimeError("DuckStation closed the debugger connection")
        reply = bytearray()
        while (byte := self.stream.read(1)) != b"#":
            if not byte:
                raise RuntimeError("Incomplete debugger reply")
            reply += byte
        if int(self.stream.read(2), 16) != sum(reply) & 255:
            raise RuntimeError("Invalid debugger checksum")
        self.socket.sendall(b"+")
        return reply.decode("ascii")

    def read(self, address, count):
        data = bytes.fromhex(self.command(f"m{address:x},{count:x}"))
        if len(data) != count:
            raise RuntimeError(f"Incomplete RAM read at {address:#x}")
        return data

    def register(self, index):
        return int.from_bytes(bytes.fromhex(self.command(f"p{index:x}")), "little")

    def set_register(self, index, value):
        self.expect_ok(f"P{index:x}={value.to_bytes(4, 'little').hex()}")

    def expect_ok(self, command):
        if self.command(command) != "OK":
            raise RuntimeError(f"DuckStation rejected {command}")

    def run_to(self, address):
        self.expect_ok(f"Z0,{address:x},4")
        timer = Timer(2, self.socket.sendall, args=(b"\x03",))
        timer.start()
        try:
            if self.command("c") != "S05" or self.register(37) != address:
                raise RuntimeError("Game loop breakpoint did not fire. Close game menus and retry.")
        finally:
            timer.cancel()
            self.expect_ok(f"z0,{address:x},4")


@dataclass(frozen=True)
class Actor:
    index: int
    address: int
    kind: int
    health: int
    x: int
    y: int
    distance: float
    disposition: str

    @property
    def can_damage(self):
        return self.disposition == "Attacking player"


def disposition(goal_word, attitude_word, player_index):
    attitude = attitude_word >> 14
    if attitude == 3:
        return "Friendly"
    if attitude == 2:
        return "Neutral"
    if attitude != 0:
        return "Upset, non-hostile"
    goal = goal_word & 15
    target = (goal_word >> 4) & 255
    if goal == 5 and target == player_index:
        return "Attacking player"
    return "Hostile, attack unconfirmed"


def guest_word(remote, address):
    return int.from_bytes(remote.read(address, 4), "little")


def check_build(remote):
    signatures = {
        ATTITUDE_CHECK: "0e004294000000008213020008004014",
        FRAME: "1a33010c212000027d5d010c",
        DAMAGE: "d8ffbd271000b0af218080001400b1af2188c000",
    }
    for address, signature in signatures.items():
        expected = bytes.fromhex(signature)
        if remote.read(address, len(expected)) != expected:
            raise RuntimeError("Unsupported executable or game not yet loaded into gameplay")


def nearby(remote, radius):
    x, y = unpack_from("<HH", remote.read(POSITION, 4))
    player = guest_word(remote, PLAYER)
    base = guest_word(remote, ACTOR_TABLE)
    if not 0x80000000 <= player < 0x801FFFF7 or not 0x80000000 <= base <= 0x80200000 - 256 * RECORD:
        raise RuntimeError("Actor table or player pointer is outside PlayStation RAM")
    player_index, remainder = divmod(player - base, RECORD)
    if remainder or not 0 < player_index < 256:
        raise RuntimeError("The player is not an identified actor in the current table")
    if not remote.read(player + 8, 1)[0]:
        raise RuntimeError("The avatar has no remaining vitality. Reload a live QA checkpoint.")
    actors = []
    for start in range(0, 256, 16):
        block = remote.read(base + start * RECORD, 16 * RECORD)
        for offset in range(0, len(block), RECORD):
            record = block[offset:offset + RECORD]
            address = base + start * RECORD + offset
            kind, local = unpack_from("<HH", record)
            kind &= 511
            health = record[8]
            if address == player or not 64 <= kind <= 127 or not health or record[27] != 1:
                continue
            region, = unpack_from("<H", record, 20)
            actor_x = (region >> 10) * TILE + (local >> 13) * 32 + 16
            actor_y = ((region >> 4) & 63) * TILE + ((local >> 10) & 7) * 32 + 16
            distance = hypot(actor_x - x, actor_y - y) / TILE
            if distance <= radius:
                goal, attitude = unpack_from("<HH", record, 12)
                actors.append(Actor(start + offset // RECORD, address, kind, health,
                                    actor_x, actor_y, distance, disposition(goal, attitude, player_index)))
    return x // TILE, y // TILE, sorted(actors, key=lambda actor: (actor.distance, actor.index))


def show_candidates(remote, radius):
    x, y, actors = nearby(remote, radius)
    print(f"Player tile ({x}, {y}). Active creature candidates within {radius:g} tiles:")
    print("Index  Type  Name              HP   Tile     Distance  Disposition")
    for actor in actors:
        name = TYPES.get(actor.kind, "Other creature")
        print(f"{actor.index:5}  {actor.kind:4}  {name:16}  {actor.health:3}  "
              f"({actor.x // TILE:2},{actor.y // TILE:2})  {actor.distance:7.2f}  {actor.disposition}")
    if not actors:
        print("No active living creatures found.")
    return {actor.index: actor for actor in actors}


def apply_damage(remote, expected, radius):
    if not expected.can_damage:
        raise RuntimeError("Damage blocked. The scan did not confirm that this actor is attacking the player.")
    if remote.read(0x800C9B78, 2) != b"\0\0":
        raise RuntimeError("Close the game menu before staging damage")
    remote.run_to(FRAME)
    _, _, actors = nearby(remote, radius)
    actor = next((actor for actor in actors if actor.index == expected.index), None)
    if actor is None or (actor.address, actor.kind) != (expected.address, expected.kind):
        raise RuntimeError("Selected actor changed or left the scan radius. Scan again.")
    if not actor.can_damage:
        raise RuntimeError("Damage blocked. The selected actor is no longer attacking the player.")
    saved = {index: remote.register(index) for index in (*range(1, 34), 37)}
    try:
        # Null attacker stages the defeat without giving the player kill credit.
        for index, value in ((4, actor.address), (5, actor.health), (6, 0), (31, FRAME + 8), (37, DAMAGE)):
            remote.set_register(index, value)
        remote.run_to(FRAME + 8)
        health = remote.read(actor.address + 8, 1)[0]
    finally:
        for index, value in saved.items():
            remote.set_register(index, value)
    print(f"Actor {actor.index}, type {actor.kind}: damage {actor.health}, HP {actor.health} -> {health}")
    if health != 0:
        raise RuntimeError("The native damage routine did not defeat the selected actor")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=2345)
    parser.add_argument("--radius", type=float, default=4, help="scan radius in tiles (default 4)")
    parser.add_argument("--interactive", action="store_true", help="scan, then accept damage INDEX, scan, or quit")
    parser.add_argument("--damage", type=int, metavar="INDEX", help="stage one defeat after scanning")
    args = parser.parse_args()
    if not 0 < args.radius <= 64 or not 1 <= args.port <= 65535:
        parser.error("radius must be greater than zero and at most 64, and port must be in 1–65535")
    if args.interactive and args.damage is not None:
        parser.error("choose either --interactive or --damage")

    remote = None
    try:
        remote = Remote(args.port)
        check_build(remote)
        candidates = show_candidates(remote, args.radius)
        if args.damage is not None:
            if args.damage not in candidates:
                raise RuntimeError("Index is not in the nearby candidate list")
            apply_damage(remote, candidates[args.damage], args.radius)
        while args.interactive:
            parts = input("QA combat [scan | damage INDEX | quit]> ").split()
            if parts == ["quit"]:
                break
            if parts == ["scan"]:
                candidates = show_candidates(remote, args.radius)
                continue
            if len(parts) != 2 or parts[0] != "damage" or not parts[1].isdecimal():
                print("Enter scan, damage INDEX, or quit.")
                continue
            index = int(parts[1])
            if index not in candidates:
                print("Index is not in the nearby candidate list. Run scan.")
                continue
            if not candidates[index].can_damage:
                print("Damage blocked. Only actors confirmed to be attacking the player are eligible.")
                continue
            apply_damage(remote, candidates[index], args.radius)
            candidates = show_candidates(remote, args.radius)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"{error}\n")
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        if remote is not None:
            remote.close()


if __name__ == "__main__":
    main()
