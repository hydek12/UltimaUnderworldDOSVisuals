# Named NPC identity and dialogue audit

The audit matches clean Japanese Rev 1 PSX creature records to locally installed DOS data. It reads the DOS displayed name, checks for a DOS conversation script, and records the matching DOS type, level, tile, palette, and directional animation counts. The optional English v2.0 comparison independently parses that version's relocated object table and checks the corresponding 28-byte records.

Generate the inventory with `audit-npcs.py --dialogue-inventory` as shown in the [repo instructions](../README.md). The CSV is a local QA artifact. The source repo tracks the audit parser and verification notes.

## Completed identity checks

- The PSX inventory has 90 records with a personal dialogue ID in the DOS name-table range. All 90 mobile records matched byte for byte in English v2.0 after accounting for the object table's relocation by 1 MiB.
- Of the 82 initially linked records, 80 have both a DOS displayed name and a DOS conversation archive entry. Those 80 records represent 72 conversation IDs. There are 72 exact actor matches, seven spawn-tile matches, and one conversation-ID match that needs an in-game identity check. Eight other records are initially unlinked.
- Hewstone on Level 2 is the initially linked conversation-ID-only match. The dormant Level 3 bandit and Garamon records still need activation checks. The linked type 102 record with ID 110 has an exact actor match but no DOS displayed name or script.
- Warren's Level 6 record has an exact DOS counterpart and a displayed name. The local DOS archive has no script for his ID. The earlier DuckStation attempt produced the English no-response message. Quest-state behavior still needs checking before resolving his disposition.

| Level | Initially linked records with a DOS name and script |
| --- | ---: |
| 1 | 10 |
| 2 | 7 |
| 3 | 9 |
| 4 | 16 |
| 5 | 6 |
| 6 | 13 |
| 7 | 18 |
| 8 | 1 |

These totals include shared labels such as guards and bandits and records already covered by the sprite patch. They measure the identity audit. A quest or interaction passes only after gameplay verification.

## Remaining 70% checks

1. Start with the seven Level 1 actors whose art still uses the native renderer. Drog, Vernix, Ketchaval, and Retichall share the gray goblin animation family at two DOS palettes. Bragit, Gulik, and Hagbard use the fighter family. Eb, Jaacar, and Lanugo are the existing Level 1 controls.
2. Keep the existing green goblin art during Level 1 bank transitions. The full-resolution gray goblin variants fit two 4-bit pages together. The tested single-page fit required 13/16 texture resolution. The fighter has more than 16 converted colors and exceeded both tested 8-bit pages at full resolution. A dedicated layout or streamed frames are candidates for preserving the original art.
3. Confirm each named actor in its original PSX encounter. Check the English name and dialogue ID, the available quest and trade choices, behavior when leaving and returning, and sprite restoration after dialogue and inventory. Recheck the earlier Level 6 discussion captures for Gralwart, Dominus, and Louvnon on the same release candidate as the remaining quest actors.
4. Include dormant or ambiguous matches only when their activation and identity are verified. Record native fallback for unsupported poses and contexts.
5. Close 70% after the remaining named quest and dialogue checks pass. The 75% scope then covers recurring creature and humanoid families on Levels 1–4 and their floor transitions.

No new CHD was needed for the archive identity checks. The last boot-verified candidate remains the [Level 6 combat preview](level-six-combat-verification.md).
