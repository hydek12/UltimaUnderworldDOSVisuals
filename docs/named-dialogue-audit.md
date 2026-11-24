# Named NPC identity and dialogue audit

The audit matches clean Japanese Rev 1 PSX creature records to locally installed DOS data. It reads the DOS displayed name, checks for a DOS conversation script, and records the matching DOS type, level, tile, palette, and directional animation counts. The optional English v2.0 comparison independently parses that version's relocated object table and checks the corresponding 28-byte records.

Generate the inventory with `audit-npcs.py --dialogue-inventory` as shown in the [repo instructions](../README.md). The CSV is a local QA artifact. The source repo tracks the audit parser and verification notes.

## Completed identity checks

- The PSX inventory has 90 records with a personal dialogue ID in the DOS name-table range. All 90 mobile records matched byte for byte in English v2.0 after accounting for the object table's relocation by 1 MiB.
- Of the 82 initially linked records, 80 have both a DOS displayed name and a DOS conversation archive entry. Those 80 records represent 72 conversation IDs. There are 72 exact actor matches, seven spawn-tile matches, and one conversation-ID match that needs an in-game identity check. Eight other records are initially unlinked.
- Hewstone on Level 2 was the initially linked conversation-ID-only match. The runtime check below confirms his identity. The dormant Level 3 bandit and Garamon records still need activation checks. The linked type 102 record with ID 110 has an exact actor match but no DOS displayed name or script.
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

## Level 1 preview verification

- DuckStation booted the English preview. The native encounter records for Drog, Vernix, Ketchaval, Retichall, Bragit, Gulik, and Hagbard each submitted the expected DOS palette in their own rooms. Representative records for both gray goblin palettes and the fighter each passed 64 instrumented render calls across idle and walk directions. Some encounters used a staged idle pose to verify the record and palette.
- Offline checks compared 128 gray goblin frame slots and 64 fighter frame slots with the DOS inputs. Both gray palettes retain full-resolution art. Fighter textures use 15/16 resolution and keep their original dimensions on screen. Level 1 retained the green goblin art and passed six live bank transitions. Native transitions followed Level 1 → 3 → 6 → 1, with active bank and palette checks on Levels 1 and 6.
- Vernix’s English conversation opened on the final preview. Inventory returned to the same conversation and farewell restored the sprites. Bragit’s English rescue choice and return to the fighter bank passed on the preceding preview. The final build changes the Level 1 bank map and renderer constants from that preview.
- The local xdelta decoded against clean Japanese Rev 1 Track 1 (SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`) to patched Track 1 (SHA-1 `6c2619accc59f4a6b8c89b4f5784655f00c34c43`). CHD verification passed and all four extracted tracks matched byte for byte. The CHD SHA-1 is `e7d886d55bf0522711394617380c3619308c443a`.

## Extended floor-bank preview verification

- DuckStation cold-booted the new CHD through the English menu and character creation into Level 1. The native floor loader passed Level 1 → 3 → 6 → 1 → 2, including the expected Level 6 bank and palette. A debugger-only override of the Level 6 table entry selected its second bank at sector offset 282 and reached the game’s disc-read routine with the expected address and resident length. The original table entry was restored before resuming. Older profile loaders compared byte for byte with the previous recipe.
- On Level 2 the linked type 84 actor at `0x80113d08` dispatched conversation 89. His English dialogue identified him as Hewstone. His mining and mine-monster branches opened, barter offered items and accepted appraisal, and farewell returned to the dungeon. A completed exchange, the mine-monster outcome, and the DOS dwarf sprite conversion remain open.
- Bragit’s type 90 encounter on Level 1 dispatched conversation 67. His English rescue response and follow-up pages displayed, and return to the dungeon restored the ready fighter bank.
- The Level 6 recheck reached Gralwart’s emerald instructions (ID 188), Dominus’s no-item identification response (ID 194), and Louvnon’s mantra research (ID 193). Louvnon returned to the ready bank. Warren (ID 207) still gave the English no-response message on a fresh character. Completing the associated puzzles, testing an item and payment with Dominus, and checking Warren in a progressed quest state remain open.
- The local xdelta decoded against the same clean Japanese Rev 1 Track 1 to SHA-1 `d3b370395327bdd630c3d9eade4d73662eb8dd43`. The CHD passed its internal SHA-1 verification and all four tracks matched after readback. The CHD logical SHA-1 is `d2ea85da96e0499cd6a0d18bc5e3b7824b47c353`.

## Level 2 named NPC preview verification

DuckStation cold-booted this CHD through the English menu to a fresh game. Native Level 2 encounters drew the six dwarves and Corby with their expected palettes. Both dwarf palettes were packed at full 8-bit resolution. Corby retained his DOS palette and screen geometry with 15/16 textures. Offline comparison checked 192 directional idle and walk slots across both banks and 182,208 texels. Live probes checked all 64 idle and walk slots on one actor per palette and on Corby. Six in-place switches covered the green goblin, dwarf, and fighter banks and matched resident code, frame tables, and ownership against disc. Native transitions exercised Level 2 → 1 → 3 → 6 → 2, including a return to the dwarf bank.

| Actor | PSX conversation ID | Palette from DOS | Encounter draw |
| --- | ---: | --- | --- |
| Shak | 2 | Dwarf 0 | Passed |
| Hewstone | 89 | Dwarf 0 | Passed |
| Goldthirst | 3 | Dwarf 1 | Passed |
| Steeltoe | 21 | Dwarf 0 | Passed |
| Corby | 1 | Fighter 1 | Passed |
| Brawnclan | 88 | Dwarf 0 | Passed after a closer camera setup |
| Ironwit | 90 | Dwarf 1 | Passed |

Brawnclan’s English dialogue confirmed his identity. His rescue and passage branches displayed, and farewell restored the ready dwarf bank. Hewstone’s opening dialogue also worked with the new bank.

The xdelta decoded from clean Japanese Rev 1 Track 1 to SHA-1 `1886fa383413e53d4dd1756975f5ced8526b187b`. Only the ISO descriptor and executable floor-table sector differ before the appended Level 2 banks. CHD SHA-1 `37e06dc0d910c55c1deded4c0d64bd130f597ad9` verified internally, and all four extracted tracks matched the split BINs.

## Level 3 named NPC preview verification

- DuckStation cold-booted the CHD into English gameplay and displayed the English Patch title. All four initially active bandits, Murgo, Zak, and Sseetharee produced the expected DOS palette packets at their native records. Offline checks compared 448 frame slots and 504,505 texels with the DOS exports. Live checks covered 256 idle and walk calls across the head bandit, Murgo, Sseetharee, and Zak. Six room-bank switches verified resident code, tables, and ownership without a floor load.
- A shared camera frame submitted both Murgo’s and Sseetharee’s DOS sprites with separate palettes. Murgo responded to the correct name and reached the lizard-language lesson and inventory prompt. The ready shared bank returned after the prompt closed. Sseetharee’s greeting and follow-up ran afterward. The complete rescue and Dr. Owl handoff still need a progressed quest run.
- A standard lizard bank control exercised 48 combat render calls, including eight fixed pose draws for the type 88 control. Within the shared room, lizard idle and walk use DOS art and fixed combat poses use native fallback. The dormant bandit still needs an activation check.
- The xdelta round-trip from clean Japanese Rev 1 produced Track 1 SHA-1 `59e4eaa757852bae0c9b1cac0aff28199e6c05b8`. CHD SHA-1 `48a93fcd1ab25df91cb07bf142e7e9dd3721fafd` verified internally, and all four extracted tracks matched the split BINs.

## Level 4 named NPC preview verification

DuckStation cold-booted the Level 4 preview with its English Patch title. All 16 initially linked named encounters submitted their expected DOS palette at their native records. The town bank uses both fighter families with 11/16 textures in shared sightlines. Separate fighter rooms use 15/16 textures, and the two troll palettes retain full resolution. Offline verification compared 768 idle and walk frame slots and 664,802 texels. Six in-place bank switches checked resident code, frame tables, and ownership across the standard lizard, town, fighter, and troll banks.

Representative live probes passed 576 idle and walking render calls across the new palettes and room layouts. Dorna Ironfist’s Order admission response displayed. His English name overlaps the greeting area and is tracked for the UI pass.

The xdelta decoded from clean Japanese Rev 1 to Track 1 SHA-1 `eab1814243f110e993076762d590ed86a4aaae24`. CHD SHA-1 `c2fd1893e27b1e6127f1c4fed33001efddc3f306` verified internally. All four extracted tracks matched the split BINs.

## Levels 5 and 8 local preview verification

- Judy, Anjor, all four named Level 5 ghouls, and Carasso submitted their expected DOS palette packets at the native encounters. Offline comparison covered 320 idle and walk slots and 281,348 texels. Carasso also passed 64 directional render calls, opened his English wizard-bones branch, and returned to the ready shared bank. Anjor’s English alchemy explanation opened. Judy’s live all-facing probe ended when the disposable character died, so only the offline full-slot comparison and a staged encounter draw are recorded for her.
- The latest preview cold-booted under its English Patch title. The xdelta round-trip from clean Japanese Rev 1 produced Track 1 SHA-1 `ebf725124a10e9c61bffd240cbd1acc4c48d19c6`. CHD SHA-1 `e133459a0eb84ecb661c59fa3c03c2cb1b2b261f` verified internally and all four extracted tracks matched the split BINs.

## Level 7 local preview verification

- The prison corridor uses two texture pages in a single room bank. Wizards retain full-resolution 4-bit art. Dwarves and fighters share an 8-bit page using 9/16 and 8/16 textures respectively. Cardon uses a separate 15/16 8-bit page.
- Offline comparison covered 704 directional idle and walk slots across the six custom banks. DuckStation submitted the expected DOS palette for all 12 initially active records assigned to those banks, including Tyball, Cardon, the four gray guards, Naruto, Kallistan, Gurstang, Smonden, the troll guard, and Fintor.
- Seven in-place room switches verified resident code, tables, and ownership against the disc. Cardon’s English conversation reached his no-port, prison directions, and guard advice branches. The ready Level 7 bank returned after dialogue. A follow-up live all-facing probe timed out, so directional coverage for these banks is the offline comparison. Prison actors drew with their own palettes in individual probes.
- The cumulative CHD cold-booted through the English title menu into Level 1. The xdelta applied to clean Japanese Rev 1 and decoded to Track 1 SHA-1 `84268556b9fc05f26bb076388961cfe3adb99892`. CHD SHA-1 `de0a7954fef78668d45817b0ca4654bdffecfd28` verified internally. All four extracted tracks matched byte for byte. The Level 5 and Level 8 bank sectors also matched the preceding preview.

## 70% cumulative DuckStation verification

- On Level 1, Hagbard and Bragit reached their English dialogue branches. Lanugo accepted a gift of 30 gold and handed over the stew recipe. The scroll was present in the live map after the handoff.
- On Level 2, the Gazer’s native death animation set quest bit 4. Goldthirst recognized the kill, remembered it on return, and accepted a large gold nugget through the original offer. The empty-handed response was also exercised.
- The original create-object trap at (35, 6) on Level 3 inserted a new bandit (ID 112, type 93) into the live tile chain. The spawned actor submitted its DOS sprite with CLUT `0x7e18` in bank 1 on the final CHD.
- On Level 5, using Garamon’s bones on the original grave ran his English conversation. The native handler set burial bits `0xc00` and updated the grave link. This scene uses a temporary dialogue actor. The serialized spectre records retained their original bytes.
- Sseetharee accepted six fish and opened the release branch. Murgo thanked the Avatar and reached the departure dialogue. After the Level 6 transition, Dr. Owl acknowledged the rescue and gave the Wine of Compassion directions.
- After the rescue, Warren displayed the English no-response message. His ID 207 is absent from the original 92-entry PSX conversation table. The runtime table matched clean Japanese Rev 1 byte for byte and the selector returned -1 before dispatch.
- On Level 7, the live tile chains already contained Dantes, Bolinard, Griffle, the imp, and both green guards. The serialized initialization byte alone did not identify whether these records were live. All six submitted their expected DOS palettes. Dantes, Bolinard, and Griffle opened their English prison dialogue.
- Both Level 7 shared views passed in bank 4. Naruto (4-bit, CLUT `0x7e18`) and Kallistan (8-bit, CLUT `0x7e98`) drew in the same frame. In a second view, Griffle (8-bit, CLUT `0x7ed8`) and Kallistan drew in the same frame.
- The final Level 7 room-map adjustment assigns (25, 55) to the default green goblin bank. Both green guards drew with CLUT `0x7f1b` on the final CHD. The four gray guards and the troll also drew with their expected bank and palette after the adjustment.

The debugger positioned the camera, staged input items in a disposable run, started the Gazer’s dying animation, and invoked the original trap and grave handlers. Gameplay code performed the transactions, spawned the bandit, and advanced the quest flags. Directional coverage for Level 7 is the 704 idle and walk slot comparison described above. The live probes cover encounter rendering, palette selection, and the cited shared views.

### Release verification

The cumulative CHD cold-booted in DuckStation through the English title menu and into a fresh Level 1 game. The builder decoded the local xdelta from clean Japanese Rev 1 Track 1 (SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`) and matched the built track (SHA-1 `f315e6d74f32a0c66c87e01096b1cbc39c04eae1`). The CHD verified with internal SHA-1 `9e45166475c0128c42d01a168bf6cae6c8d0c29b` and all four extracted tracks matched byte for byte. Generate the CHD and xdelta locally using the builder and the source files listed in the [local build guide](local-patch-builder.md).

## Milestone progress in one-percent increments

These percentages track the project checklist. They are estimates based on verified deliverables. Report progress in Slack when a one-point gate passes. Commit and push the verified batch at each completed five-point milestone.

| Progress | Status | Verification gate |
| --- | --- | --- |
| 65% | Verified | Matching DOS spell effects and the clean-disc xdelta round-trip |
| 66% | Verified | Level 6 runtime banks, encounter rendering, and supported combat poses |
| 67% | Verified | Level 1 named actors, room-bank switching, and representative dialogue |
| 68% | Verified | Wider floor addressing, Hewstone’s identity, and Level 2 named sprites |
| 69% | Verified | Level 3 and Level 4 encounter draws, shared rooms, and fresh-disc verification |
| 70% | Verified | Named encounters, dormant activation, quest and trade outcomes, shared views, and cumulative release verification |

## Next milestone

The 75% scope covers recurring creature and humanoid families on Levels 1–4 and their floor transitions.
