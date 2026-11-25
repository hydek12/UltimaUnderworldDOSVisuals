# Named NPC identity and dialogue audit

The audit matches clean Japanese Rev 1 PSX creature records to locally installed DOS data. It reads the DOS displayed name, checks for a DOS conversation script, and records the matching DOS type, level, tile, palette, and directional animation counts. The optional English v2.0 comparison independently parses that version's relocated object table and checks the corresponding 28-byte records.

Generate the inventory with `audit-npcs.py --dialogue-inventory` as shown in the [repo instructions](../README.md). The CSV is a local QA artifact. The source repo tracks the audit parser and verification notes.

## Completed identity checks

- The PSX inventory has 90 records with a personal dialogue ID in the DOS name-table range. All 90 mobile records matched byte for byte in English v2.0 after accounting for the object table's relocation by 1 MiB.
- Of the 82 initially linked records, 80 have both a DOS displayed name and a DOS conversation archive entry. Those 80 records represent 72 conversation IDs. There are 72 exact actor matches, seven spawn-tile matches, and one conversation-ID match that needs an in-game identity check. Eight other records are initially unlinked.
- Hewstone on Level 2 was the initially linked conversation-ID-only match. The runtime check below confirms his identity. The dormant Level 3 bandit and Garamon records still need activation checks. The linked type 102 record with ID 110 has an exact actor match but no DOS displayed name or script.
- Warren’s Level 6 record has an exact DOS counterpart and a displayed name. Both local originals lack a conversation for his ID. See the [follow-up proposal](#warren-dialogue-follow-up) for the progressed-save check and the scope of a potential addition.

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
- The Level 6 recheck reached Gralwart’s emerald instructions (ID 188), Dominus’s no-item identification response (ID 194), and Louvnon’s mantra research (ID 193). Louvnon returned to the ready bank. Warren (ID 207) gave the English no-response message on a fresh character. Completing the associated puzzles and testing an item and payment with Dominus remain open. Warren’s progressed-save result is recorded below.
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
| 71% | Verified | Levels 1–4 record and DOS palette inventory |
| 72% | Verified | Recurring room banks packed with eight idle and walk facings |
| 73% | Verified | Native encounter palette probes and directed floor transition matrix |
| 74% | Verified | Revised Level 4 mixed bank, disc readback, and reproducible xdelta |
| 75% | Verified | Final English CHD cold boot, directional render probes, and shared palette submission |
| 76% | Verified | Levels 5–9 record and DOS animation inventory |
| 77% | Verified | Late-floor bank layouts and byte-level facing and palette checks |
| 78% | Verified | Native dormant activation probes and Level 6 and 7 spawned palette checks |
| 79% | Verified | Level 8 directional draws and Level 9 special-model renderer checks |
| 80% | Verified | Cumulative English CHD boot and clean Japanese Rev 1 xdelta round-trip |
| 81% | Verified | Slasher combat frames, action mapping, and native render fallbacks |
| 82% | Verified | Level 4 mixed-bank draw and solid-wall occlusion control |
| 83% | Verified | Native torch toggle and matched environment lighting captures in the Level 4 mixed room |
| 84% | Verified | Level 4 partial wall cover, reversed depth order, and overlapping sprite bounds during native movement |
| 85% | Verified | Representative creature and humanoid combat rendering across all nine floors, native bandit strikes, and controller-driven grub damage |
| 86% | Verified | Native Level 3 bandit strike reduced player health from 35 to 30 |
| 87% | Verified | AI-driven rat walking packets followed native depth-based lighting |
| 88% | Verified | Level 3 bandit idle and walk lighting on the source-built preview |
| 89% | Verified | Live Level 4 creature lighting and seven native bandit combat fallbacks on the source-built preview |
| 90% | Verified | Preview bandit damage recheck, two-sector comparison, clean-disc delta and CHD readback, and default recipe hash regression |
| 91% | Verified | DOS normal and monochrome maps matched all 4,096 generated RGB555 entries |
| 92% | Verified | 168 normal shade-map packet selections across seven light levels and four palettes |
| 93% | Verified | 24 monochrome packet selections with matched sprite geometry and UVs |
| 94% | Verified | Native Level 1 room-bank restoration and full texture and palette VRAM comparison |
| 95% | Verified | Cumulative shade-map preview round-trip, four-track CHD readback, and default recipe hash regression |
| 100% | Verified | Native torch, Light and Night Vision drive the Level 1 DOS palettes in DuckStation. Preview and default recipe regression checks passed. |

## Levels 1–4 recurring creature preview

The cumulative build adds DOS idle and walking art for grubs, slugs, bats, rats, spiders, skeletons, lurkers, headless, imps, gazers, golems, ghosts, shadows, reapers, and wisps. The existing gray goblin, fighter, dwarf, troll, and wizard palettes cover additional rooms. The Level 4 mixed bank keeps bats, grubs, and rats available within the same room. Original fallback banks remain available for the green goblins and lizardmen.

The floor audit checked 221 initially linked and 36 other serialized records. The bank selected at the original spawn contains the actor’s entry for 220 initially linked records. Vernix uses the adjacent south view to preserve Lanugo’s bank. The noninitial records have 16 spawn assignments, five adjacent assignments, and 15 without a local assignment. These counts describe the parsed records and bank coverage. Activation of the other serialized records remains separate from the spawn audit.

The final disc’s 42 custom banks on Levels 1–4 matched 6,528 directional frame slots and 5,688,303 displayed texels against the local DOS exports. The comparison checked frame rectangles, hotspots, texture depth, palette indices, and colors. The new creature banks retain full-size textures. Original PlayStation combat and special actions remain available where no DOS pose is registered.

DuckStation exercised all 12 directed floor pairs on Levels 1–4. The loader selected a bank with the correct owner, disc offset, resident renderer, and palette registry after each entry. The final build changed 37 sectors within Level 4 bank 5. The banks used in the transition matrix matched the final disc byte for byte.

DuckStation confirmed DOS sprite packets at original encounters for 82 combinations of floor and actor type, including the fallback lizardman palette on Levels 3 and 4. Controlled staging checked 1,664 live idle and walk packets across 26 sets of eight facings with four animation phases each. The probes checked frame selection, UVs, texture page, and CLUT. Native action or projection changes interrupted the full live sweeps for the Gazer and the Level 4 grub. Their actual sprite packets and offline frame and palette data passed. With the camera at `(0x2380, 0x32c0, 0x2000)` and idle poses staged, the Level 4 grub (CLUT `0x7e98`) and rat (CLUT `0x7f18`) submitted separate packets in the same frame in bank 5.

### Local release

The final CHD cold-booted through the English title and character creation into fresh gameplay. The Xcode-built exporter reproduced the combined xdelta byte for byte. Decoding against clean Japanese Rev 1 Track 1 (SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`) yielded the patched data track (SHA-1 `11e712449846d8ecad84a148cbdc0f365bdc0e2c`). The CHD verified with internal SHA-1 `673809e6ec4fe18b921f65a3e6e01aad87adae2f`, and all four extracted tracks matched. Use `--late-dialogue` from the [local build guide](local-patch-builder.md) to reproduce it using your own source files.

## Levels 5–9 recurring creatures and special models

The source audit contains 400 records across these floors. The serialized initial marker is set for 329 and clear for 71. The marker describes initialization. Runtime tile chains and the original create-object traps identify which template records can become actors.

The new banks cover the recurring late-floor types and extend the Academy’s shared troll palette to type 96. The Slasher of Veils follows the Avatar across Level 9. A floor-wide bank holds the Slasher, bat skull, lightning, and eye. It uses 10/16 textures and preserves the DOS frame sizes, palettes, and anchors. The lightning and eye reuse their directional standing frames for movement because their DOS art has no walk slots. Unsupported actions retain native art.

A disc readback matched 5,248 frame slots and 5,892,063 sampled texels across 41 packs on Levels 5, 7, 8, and 9. The build uses the Xcode exporter and user-supplied DOS data. The final banks cover 328 initially marked records at their spawn cells, with the Level 5 Gazer drawing from an adjacent cell. Clean Japanese Rev 1 Track 1 decoded to `039e4a79a468c1dda7e8617b0eb463e867891ee7`. The CHD internal SHA-1 `cf4ce44c3b7a18043233558c31d08a8c249ce97b` verified and all four extracted tracks matched byte for byte.

DuckStation’s trap audit checked the runtime tile chains. It confirmed 24 distinct native create-object activations on Levels 5–8. The final image rechecked the Level 7 dormant troll at (52, 59), including its DOS palette submission after the trap created the actor. An Academy fire elemental created at (57, 56) also submitted its DOS palette. Both Level 9 zero-marker records were already linked when loaded. The debugger invoked original trap handlers in the disposable run. The remaining noninitial records include actors already on the map and events whose full in-game trigger sequence remains unverified.

The final CHD cold-booted to the English menu. In Level 9, the eye and lightning submitted their expected palettes at their native records. A staged idle test submitted the bat skull’s palette. The Slasher’s palette and quad passed using another actor’s captured native projection and the Slasher’s real frame table. The Slasher’s unstaged encounter draw remains unverified.

The live facing sweeps checked 256 idle and walk packets on Level 8 and 64 idle packets across the eight eye and lightning facings on Level 9. The Level 7 and 9 tested banks matched the final disc’s resident renderer, palette registry, and room grid in DuckStation.

## Level 9 Slasher renderer follow-up

The Slasher rendered at its own Level 9 encounter using its native idle action (`0x20`) and projected bounds. The previous ordering log overflowed at 128 entries. The Level 9 bank now saves each touched ordering-table bucket's original head once, so it can restore the table before submitting the DOS quad. The rebuilt CHD logged 69 buckets and submitted the Slasher's DOS palette (`0x7e18`) with no pose or projection override. The Slasher's native draw was replayed with eight facings, four animation phases, and both idle and walk, checking 64 GPU packets against the frame UVs and palette. The eye and lightning regression sweeps submitted another 64 idle packets across all eight facings. The local release rebuilt from the upstream translation and clean Japanese Rev 1, decoded Track 1 to `b824482c3b13b607aa039aba59effa4bd0cbac24`, and matched the boot-tested CHD byte for byte. Its CHD SHA-1 is `34a62d053a0db670b3db68b1db997a9aec8a2d13`.

The native create-object trap samples a roll from 0 through 62 before linking an actor. Its handler can return `2` on both a rejected roll and a successful spawn. The debugger audit retries the original handler and verifies the actor's membership in the destination tile chain. Of the 15 earlier misses, 13 created an actor in the requested tile. The Level 8 skeleton linked in the adjacent tile at (46, 7). The Level 7 fire elemental was already linked at (60, 43) on fresh entry and drew with its DOS palette in its native idle action. The create-handler checks start after dispatch. Ordinary gameplay trigger chains and the remaining special-action sprites still need encounter coverage.

## Level 9 Slasher combat preview

The opt-in preview’s disc readback matched 287 frame slots and 414,498 sampled texels across the Slasher, bat skull, lightning, and eye. The Slasher’s action table maps seven combat actions to 31 frames through 112 phase entries. A raw-sector comparison against cumulative release Track 1 found 17 changed sectors within the Level 9 bank, at LBAs 153562–153579. The preview’s xdelta decoded from clean Japanese Rev 1 Track 1 to SHA-1 `711e19c5623334a842f9c591d4ae1028d0ea97d6`. DuckStation cold-booted the preview CHD, and all four extracted tracks matched byte for byte.

A DuckStation replay used the Slasher’s own native projection at its Level 9 encounter. Controlled inputs covered 1,152 GPU packets across eight facings and all 16 tick values for the nine supported actions, including idle and walk. The checks covered frame selection, UVs, texture page, and CLUT. A separate replay enumerated all 55 unsupported action values and verified that the renderer preserved the captured ordering-table heads and GPU packet arena. At that encounter, the Slasher’s native idle action (`0x20`) submitted the expected DOS sprite with CLUT `0x7e18`; the test positioned the camera.

The combat sweep below covers representative creature and humanoid encounters across all nine floors. The Level 4 checks cover player damage, lighting, and occlusion in a mixed encounter.

## Level 4 mixed-encounter lighting and occlusion

The bat, grub, and rat bank loaded after a debugger-assisted floor entry from a disposable checkpoint. The test positioned the player and camera and let the original actor AI choose actions. The grub (type 82) and rat (type 72) submitted sprites in the same frame with palettes `0x7e98` and `0x7f18`. The trace captured native idle and walk transitions. Player-driven hits and damage through the mixed encounter remain unverified.

In the open view at `(0x2380, 0x32c0)`, the grub was visible against the dark floor. In the wall control at `(0x2380, 0x2f80)`, a solid tile at (35, 48) lay between the camera and the grub. The framebuffer showed the foreground wall with no creature sprite showing through. The renderer submitted both creature packets in that view, so packet presence alone does not establish visibility. This control covers one solid wall. Partial-cover and moving-overlap cases remain open.

Both creature packets used GPU command `0x2d`, which draws the texture in raw color. The palettes reached the GPU as expected, but the sprites did not receive per-polygon color modulation. Torch-on versus torch-off fidelity remains open.

### Native torch and controller combat follow-up

The disposable checkpoint started with empty inventory. The test added a native torch and dagger, then used the original inventory controls to ignite and extinguish the torch. The same equipped object changed from type 149 while lit to type 145 when extinguished. Both environment captures used camera coordinates `(0x2380, 0x32c0, 0x0200)` and heading `0x2000`. The torch illuminated the floor and right-hand wall. At framebuffer pixel (810, 900) the captured color changed from RGB (17, 11, 5) with the torch off to (56, 44, 21) with it on. This verifies the room lighting response. The two captures do not show a matched creature pose under both torch states.

In a separate unarmed run, the native controller switched battle mode and exercised R2 attacks while the grub and rat moved around the player. The health flask fell during the live encounter. The attempt did not establish a successful player hit or damage to either creature.

Two oblique wall-edge views produced screen-space intersections between the walking grub and idle rat quads in five captured frames. Their projected bounds overlapped by 24 and 6 pixels at the two positions, respectively. The rat occupied the nearer depth bucket in both views (489 versus 704, then 499 versus 728). Captures showed the rat in front of the visible portion of the grub. The capture verified this actor pair. The wall-edge views did not isolate a wall clipping only part of a single sprite, and a passing depth-swap test remains open.

### Matched torch pose and reversed depth controls

The matched torch check used the same two actor records, fixed idle action, facing, and phase after the original inventory toggled the equipped torch from item type 145 to 149. The grub and rat retained identical UV coordinates, texture pages, and palette selectors across the two draws. Both used the raw texture command `0x2d`. This confirms that these actor draws bypass per-polygon color modulation with the torch lit as well as unlit. The room lighting still responded to the native torch.

The reverse depth probe found four frames in which the grub's depth bucket was nearer than the rat's. The first such pair measured 175 for the grub and 205 for the rat, reversing the earlier 704 and 489 order. The two sprite rectangles did not overlap on-screen in those reversed frames. This establishes the ordering-table reversal and leaves the reversed-overlap framebuffer case open.

The native damage trace watched the creature health store while controller input attempted repeat attacks and charged melee. Neither run recorded a health decrease with the player identified as the source. An outgoing hit remains unverified.

A wall-edge height sweep captured the rat and grub at four camera heights from `0xc0` through `0x180`. At `0x140`, the walking grub's overlap with the nearer rat expanded from 20 to 32 pixels while the rat stayed in depth bucket 489. The inspected frames did not isolate partial foreground wall cover.

### Level 4 native lighting prototype

A separate local preview changes only raw Track 1 sector 150909, which contains the bat, grub, and rat bank's sprite renderer. The prototype reads the original PlayStation distance-light table at the sprite's ordering-table depth. It sends an opaque modulated texture command (`0x2c`) with equal RGB channels. For a neutral base color, each channel is the native table byte rounded down to even, matching the original polygon calculation. The existing frame, texture page, palette, and ordering-table paths still supply the sprite geometry.

DuckStation held the grub and rat at the same idle facing and phase at depth 256. Toggling the original inventory torch changed the native table value from 33 to 71 and the sprite RGB multiplier from 32 to 70 for both creatures. The matched UVs and CLUTs agreed. With the torch lit and native projected depths restored, a rat at depth 511 used multiplier 30 and the grub at depth 676 used multiplier 4. These checks compare the native game lighting response on one bank. DOS shade-map and monochrome behavior require separate validation.

The prototype CHD cold-booted in DuckStation. CHD verification passed and all four extracted tracks matched their inputs. The xdelta applied to clean Japanese Rev 1 Track 1 produced SHA-1 `5e4b2a2f9e40cca27cd6cb6d6e92df8fd47ca8e0` and matched the prototype track byte for byte.

### Staged depth reversal

In the local lighting preview, a debugger probe held the rat and grub idle, shifted their positions within their original tiles, and kept the camera fixed. Three frames per setup showed intersecting sprite bounds and opposite native depth orders. With the rat nearer, the grub and rat used buckets 233 and 150 and their bounds shared 637 pixels. With the grub nearer, they used buckets 133 and 249 and their bounds shared 672 pixels. The captures show the rat covering the grub in the first setup and both silhouettes visible in the second. The measured intersections include transparent texels, so the reverse capture leaves opaque-pixel overlap and overlap in motion open.

A second run brought the actors closer to the same depth and lowered the test camera. At buckets 188 and 193 (rat and grub), the rat covered part of the grub. At buckets 208 and 173, the framebuffer showed the grub crossing in front of the rat's body. Both setups produced three frames with intersecting sprite bounds. This closes visible occlusion in both depth orders for the staged pair. Player-dealt damage, partial wall cover, and overlap during ordinary actor movement remain open.

The next controller trial mapped native Triangle and Down to one test key in the disposable DuckStation profile. The player entered battle mode, charged the power gem, and visibly threw an unarmed punch. The fist shows that staging a dagger in inventory did not equip it for this attack. The camera ended up facing a wall during the trial, and the health-store trace captured no player-dealt health decrease. The test runner now rewrites the media path in its disposable save copy to use the selected local CHD.

### Partial cover at the Level 4 doorway

A foreground doorway wall hid the rat's body and tail while leaving its nose and front leg visible at camera coordinates `(0x20f8, 0x30fe, 0x0200)` and heading `0x2fae`. The open-side control at `(0x20f8, 0x3118, 0x0200)` showed the entire rat. The debugger kept the mixed creature bank active at the doorway in the disposable session. The wall geometry and renderer were unchanged. The rat submitted its native idle action in both views, and the partial cover capture also shows the grub.

### Overlap during native movement

With the camera at `(0x23f0, 0x2f80, 0x0140)` and heading `0x0600`, the rat stayed in walk action `0x2c` and moved from sub-tile coordinates (293, 405) to (294, 406) between sampled frames 1 and 4. The idle grub stayed at (294, 414). In both frames their projected sprite bounds intersected by 40 square pixels, with the rat in depth bucket 481 and the grub in bucket 723. The probe moved only the camera and left the original AI to drive both actors. This trace measures sprite bounds during movement. The staged depth reversal above supplies the visible overlap check.

### Player damage trace

Early trials missed the Level 4 grub or selected static object index 849 in the Level 3 encounter. Sseetharee began and ended that trial at 30 health.

A controller-driven melee strike on the Level 4 lighting preview selected the grub (type 82, object index 200). The native damage routine received the player at `0x801121e8` as the attacker and the grub at `0x801137ac` as the target. Reading the same health byte at routine entry and on return showed 10 becoming 0 in a single call. The debugger adjusted the player object's melee origin and facing in a disposable save. The native game selected the target, calculated damage, and updated health. The result verifies player-dealt damage in this Level 4 encounter.

## Cross-family combat rendering sweep

DuckStation replayed seven combat action values (`0x00`, `0x01`, `0x02`, `0x03`, `0x07`, `0x0c`, and `0x0d`) from captured native actor projections in the Slasher combat preview. The test staged the action byte and restored the saved draw state between replays. All 217 native fallbacks preserved the GPU packet arena and the captured ordering-table heads. The Level 6 wizard submitted a DOS packet with its assigned palette for each of its seven staged combat states. The capture for each of the 32 encounters also produced a control sprite with the expected palette.

| Level | Encounter records checked |
| --- | --- |
| 1 | Slug 65, bat 66, spider 68, gray goblin 71, skeleton 74, lurker 87, fighter 90 |
| 2 | Dwarf 84, headless 91, gazer 102, golem 114 |
| 3 | Imp 81, lizardman 85, bandit 93, ghost 97, wizard 106, shadow 117, reaper 118 |
| 4 | Troll 112, wisp 122 |
| 5 | Ghoul 99, female wizard 107 |
| 6 | Wizard 103, fire elemental 120 |
| 7 | Green goblin 78, Tyball 123 |
| 8 | Rat 72, fighter 104, golem 119 |
| 9 | Bat skull 79, lightning 125, eye 126 |

The gazer and Tyball reached the ordering-log overflow guard from some camera positions. A valid alternate view completed each palette control. The Slasher's 31-frame combat sweep is recorded above. The default release CHD, Slasher combat CHD, and local lighting prototype passed a fresh CHD integrity check.

For the humanoid gameplay check, the debugger assigned a Level 3 bandit (type 93) the attack goal for the player in a disposable save. The original AI drove movement, retreat, and swing actions `0x01`, `0x02`, and `0x03`. The native damage dispatcher received the bandit at `0x80113c98` as source and the player at `0x801121e8` as target on multiple attacks. The humanoid trace confirms attacker and target selection. The Level 4 grub trace supplies the measured health change.

## 90% native sprite lighting preview

- Reading the player actor's health byte at entry to and return from the native damage call confirmed a bandit hit from 35 to 30 HP on the Slasher preview and from 35 to 26 HP on the lighting preview. The disposable setup assigned the bandit its attack goal. The original AI selected the swing and the game resolved damage.
- With native movement on the Level 4 lighting prototype, a walking rat at depth 291 used RGB (26, 26, 26) from table entry 27. At depths 588 and 636 the native table and sprite multiplier were both zero.
- The source-built preview matched eight native idle and walking bandit samples to the depth-light table. The idle bandit used RGB (50, 50, 50) at depth 159 and (30, 30, 30) at depth 269. The two draws used the same DOS palette selector.
- Seven live samples across the rat, grub, and both bat types matched the native lighting table in their original Level 4 bank. The Level 3 bandit preserved its native draw and ordering-table heads in seven staged combat fallback cases, and its control sprite drew with the expected DOS palette.
- The preview differs from the Slasher combat build at raw Track 1 sectors 149991 and 150909. The clean Japanese Rev 1 xdelta round-trip produced Track 1 SHA-1 `0e2d7db3db07e11119d1803555b14952b6539d67`. CHD integrity passed, and all four extracted tracks matched their inputs byte for byte. A separate default recipe build reproduced Track 1 SHA-1 `b824482c3b13b607aa039aba59effa4bd0cbac24`.

The lighting option uses the PlayStation depth-light table for the two tested room banks. The cumulative DOS shade-map preview adds a separate Level 1 mode.

## 95% DOS shade-map and monochrome preview

- The DOS data comparison checked all 2,048 RGB555 entries from `LIGHT.DAT` and all 2,048 from `MONO.DAT`, including the transparent entries in each palette. All monochrome entries had equal red, green, and blue channels.
- DuckStation replayed a captured Level 1 green-goblin draw at six distance inputs for each of four palettes. All 168 normal and 24 monochrome CLUT selections matched the DOS distance calculation. The geometry, texture page, and UVs matched across the replayed lighting states.
- The cumulative Level 1 room stride is one sector larger in this preview to fit the streamed CLUT block. Its light selector at `0x801f7a00` has separate storage from the room-switch pointer. DuckStation loaded the preview bank after a Level 2 to Level 1 transition, switched from bank 0 to the gray-goblin bank, and returned to bank 0. Lanugo submitted the expected normal CLUT after the return. The restored GPU capture matched 90,112 texture bytes and all 8,192 shade-map palette bytes.
- The xdelta decoded against clean Japanese Rev 1 to Track 1 SHA-1 `19a1afea2fcfd96469b8383e9f36a2da7f03f1c5`. The CHD verified internally and all four extracted tracks matched their inputs byte for byte. A separate default recipe build reproduced `b824482c3b13b607aa039aba59effa4bd0cbac24`.

The checks cover debugger-selected lighting on green goblin idle and walk sprites in the Level 1 default bank. The native game still controls dungeon lighting, torches, and spells.

## 100% gameplay-driven DOS lighting

The opt-in `--dos-shade-maps` recipe reads the effective light level at `0x800c9674` in Japanese Rev 1. The native equipment and active spell updater resolves the level. The Level 1 bank 0 idle and walk renderer uses `SHADES.DAT` for distance shading and selects `MONO.DAT` at level 5. Other levels use `LIGHT.DAT`.

A disposable DuckStation Level 1 save reloaded through Level 2 to stream the rebuilt bank from disc. The debugger staged a fueled torch and invoked the game's inventory action, player spell dispatch, and timed-effect routine. The game changed the item and spell state, resolved the light level, and drew Lanugo. The spell timer was advanced through native calls. The normal controller and rune menus were outside this check.

| Gameplay transition | Effective level | Lanugo CLUT | Map |
| --- | --- | --- | --- |
| Darkness | 0 | `0x7a58` | Normal |
| Torch lit (item 145 to 149) | 2 | `0x7918` | Normal |
| Torch extinguished (item 149 to 145) | 0 | `0x7a58` | Normal |
| Light active | 3 | `0x7918` | Normal |
| Light expired | 0 | `0x7a58` | Normal |
| Night Vision active | 5 | `0x7c98` | Monochrome |
| Night Vision expired | 0 | `0x7a58` | Normal |

An independent controlled check matched the DOS shade calculation for all 192 combinations of four goblin palettes, eight levels, and six distances. This included 168 normal and 24 monochrome draws. The preview xdelta round-tripped against clean Japanese Rev 1 and all four tracks matched the CHD readback. The preview Track 1 SHA-1 was `4d0e5e33c53435989cd3b1f5ac2d1470e18925b0`. The default recipe reproduced `b824482c3b13b607aa039aba59effa4bd0cbac24`.

## Imp, green goblin, and Gazer spawn coverage

The cumulative recipe adds DOS idle and walking art for the Level 1 imp at (12, 20) and the Level 3 green goblin at (35, 62). On Level 5 the Gazer and nearby green goblins share a bank. The Gazer keeps its full-resolution DOS texture. The green goblin uses 13/16 texture resolution on Level 3 and 9/16 in the shared Level 5 bank. Both keep the original on-screen frame dimensions and anchors.

A disposable DuckStation checkpoint used the rebuilt executable's floor table to stream the new banks from disc. The debugger positioned the camera. The native game supplied the actor poses and projection.

| Actor | Live result |
| --- | --- |
| Level 1 imp (75) | Native floor loading linked slot 236 at (12, 20) despite its zero archive marker. Bank 8 submitted the DOS idle quad from the spawn tile with CLUT `0x7e18`. |
| Level 3 green goblin (78) | The debugger invoked the original create-object trap for template 183. The native handler linked slot 179 at (35, 62), and bank 14 submitted the DOS idle quad from that tile with CLUT `0x7e18`. The controller follow-up below verified which gameplay action dispatches the trap. |
| Level 5 Gazer (102) | Native floor loading linked slot 221 at (4, 43). From camera tile (3, 42), bank 10 submitted the DOS idle quad with CLUT `0x7e18`. This view previously selected the green-goblin-only bank. The shared bank registers DOS art for the three nearby green goblin spawn views. The goblin from (4, 42) also submitted a native walking quad with CLUT `0x7e58` from camera tile (5, 44). |

The spawn-bank comparison checked all actor records on the three changed floors at each spawn tile and one tile west. The three target records gained coverage at both positions and no other record lost coverage at those positions. The [local release builder](local-patch-builder.md) reproduced the gameplay CHD byte for byte. The xdelta decoded against clean Japanese Rev 1, and all four tracks and CUE indexes passed readback. The qualified Track 1 SHA-1 is `0cb2e8536ae8c9a8f6436c78d08d972c975e95a1`.

## Dormant creature spawn coverage

The Level 3 green goblin has a wandering-monster trap. In DuckStation, with a bedroll staged in the disposable character's backpack, the original R2 + Triangle shortcut opened the rest prompt. Confirming rest dispatched trap 536 for template 183 at (35, 62) from the native wandering-monster routine. The first controller trials verified dispatch. In the follow-up, the player rested at (5, 1) until the native roll of 57 cleared the threshold of 54. The tile chain changed from no goblin to a live type 78 actor in slot 179 at (35, 62). The debugger observed the call, roll, and tile chain during the rest trials. The earlier debugger-invoked trap test confirmed the DOS quad at the spawn tile.

The archive marks 107 of 657 creature records as noninitial. A native tile-chain and create-object audit found records that floor loading already links and records that a trap can create. At Level 7 (60, 43), two fire elemental records share the same archive identity and position. The original tile chain identifies slot 189 as already linked and the create-object trap points to slot 190. That location already has a DOS fire elemental bank.

The prior build lacked DOS art in at least one of two spawn views for 27 records. The revised grids register the appropriate idle and walking art at all 107 archive spawn tiles and one tile west, with no loss of existing actor coverage at those positions. The audit also checked the native create-object trap locations. One Level 3 headless is serialized at (49, 52) and spawns at (44, 55). Both areas now select a headless bank.

DuckStation captured a DOS idle or walking quad for each of the 27 corrected records. Native floor loading linked 11 of the tested actors. For the other 16, the debugger invoked the original create-object handlers and checked the live tile chains before the draw. The debugger positioned the camera. The game supplied each pose and projection.

| Floor | DOS sprite draws verified |
| --- | --- |
| 1 | Spider (14, 7) |
| 2 | Headless (9, 44), spider (43, 48), green goblins (32, 57) and (31, 58) |
| 3 | Bat (32, 3), skeleton (1, 8), bandit (3, 9), spiders (58, 12), (18, 34) and (44, 38), rat (42, 42), lurker (3, 59), headless (44, 55) and (45, 62) |
| 4 | Rats (35, 15) and (29, 54), grubs (28, 51), (30, 52) and (33, 55) |
| 6 | Grub (16, 55) |
| 7 | Imps (34, 35), (33, 36) and (35, 37) |
| 8 | Headless (21, 40), rats (28, 49) and (14, 58) |

The Level 3 mixed room uses 12/16 skeleton and spider textures alongside a 13/16 headless texture. The Level 8 mixed room uses a 13/16 headless texture with full-size ghost and rat textures. The shared banks retain the original frame dimensions and anchors. Native combat poses remain available for unsupported actions.

The release builder reproduced the tested CHD byte for byte. All four tracks and CUE indexes passed readback. Track 1 SHA-1 is `e3e2845b85d665a1240c5c89fab828b8703850b2`.

## Dedicated room combat preview

The cumulative `--slasher-combat` preview now gives imps (75 and 81), skeletons (74), and headless (91) full-resolution DOS combat textures in their dedicated room banks. These banks share the Academy renderer's fixed-pose path. Stance, three attacks, retreat, and death use the original DOS sequences. Imps also use their four-frame spell sequence. Existing view and timing rules still apply, including directional standing art for side and rear combat views and the death pose from all views.

DuckStation replayed seven action values from native actor projections in 15 dedicated room-bank encounters on Levels 1–5, 7, and 8. The Level 5 imp first spawned through the debugger-invoked original trap. The 105 action checks produced 95 DOS sprite packets and ten expected native fallbacks for skeleton and headless casting. The fallback checks preserved each captured GPU packet and ordering-table head. The fixed-pose path has one action and phase table per bank. The later mixed-room preview adds per-family pose lookup for actors that share a bank. The [dedicated ghoul, Gazer, and wizard audit](#dedicated-ghoul-gazer-and-wizard-banks) records the follow-up work.

The preview xdelta decoded against clean Japanese Rev 1 and all four CHD tracks passed readback. Track 1 matched `e55251f4d53020fcace419823e2466a04831dab8`. The default `--late-dialogue` build reproduced `e3e2845b85d665a1240c5c89fab828b8703850b2`.


### Mixed room combat and casting

The combat preview packs directional locomotion and available DOS stance, ready, melee, cast, hit, death, and special poses per actor type. It covers 37 actor types across 24 room layouts and 32 physical banks on Levels 1–5, 7, and 8. The runtime selects the active actor’s table and holds the final authored phase as needed. Fixed combat poses use the forward view, with directional standing frames for side and rear views. Death uses its fixed pose from all angles. Unavailable actions preserve native drawing, including the green goblin stance whose DOS source frame is truncated. The DOS green goblin slot 5 has no confirmed mapping to a native action.

DuckStation started from disposable checkpoints and loaded the candidate disc’s floor banks. The debugger captured native actor projections in live encounters and staged action values, facing, and animation phase at draw time. It compared the submitted texture page, palette, and UVs against the actor’s DOS frame records. Each native fallback preserved the captured packet and ordering-table state. This verified sprite selection under controlled inputs. A separate Level 4 check gave the rat and grub a player target through the debugger and left facing, action, and animation phase to the game. Both selected DOS stance and ready frames. The rat also selected a DOS hit reaction. With a player target assigned and the forward-facing view controlled at draw time, the Level 5 goblin and Gazer and the Level 7 wizard selected DOS melee frames. The wizard also selected a DOS hit reaction. A separate Level 7 test seeded the wizard's casting state. The game advanced all five DOS casting phases, dispatched the spell, and returned to stance. The Level 5 Gazer later passed the [AI-initiated cast check](#ai-initiated-gazer-cast).

| Level | Bank and actor type IDs | DOS packets | Native fallbacks |
| --- | --- | ---: | ---: |
| 1 | 3 (64, 65) | 90 | 30 |
| 2 | 3 (69, 82), 4 (68, 72, 83), 8 (102, 114) | 348 | 72 |
| 3 | 11 (102), 12 (97, 117) | 150 | 30 |
| 4 | 5 (72, 82), 11 (102) | 138 | 42 |
| 5 | 10 (78, 102) | 96 | 24 |
| 7 | 4 (108), 11 (102), 15 (114) | 156 | 24 |
| 8 | 7 (102), 11 (122), 15 (91) | 156 | 24 |
| Total | 23 actor encounters across 15 distinct types | 1,134 | 246 |

Gazers on Levels 2 and 5 could reach the ordering log's 128-entry limit when several native polygons shared a depth bucket. The four mixed room layouts containing Gazers now record the original head once per bucket. Both families passed the live-projection matrix on the rebuilt disc, including Gazer casting and the native green goblin stance. Gazer draws also passed on Levels 2–4, 7, and 8, covering all four affected room layouts on each floor where they occur. Those captures used 54 to 62 ordering entries.

The fixes changed six sectors of the combat preview's Track 1. The xdelta decoded byte for byte against clean Japanese Rev 1, and all four CHD tracks passed readback. Track 1 matched `2dbf1674c89160d7449d1d84c317270ea23d6605`. Both lighting previews passed their xdelta round-trips. The rebuilt shade-map CHD repeated the Level 1 lighting regression after a floor reload. A native torch changed effective light from 0 to 2 and back. Light selected normal shade level 3, Night Vision selected monochrome level 5, and both spell expiries restored level 0. The default `--late-dialogue` build reproduced `e3e2845b85d665a1240c5c89fab828b8703850b2`.


#### AI-initiated Gazer cast

The Level 5 Gazer (type 102) initiated a cast in mixed room bank 10 on combat preview Track 1 `2dbf1674c89160d7449d1d84c317270ea23d6605`. DuckStation entered the floor at tile (4, 45) from a disposable checkpoint. The probe stopped at the native AI instruction at `0x800330a8` and observed it change the Gazer's action from stance (`0x00`) to cast (`0x0d`). The debugger repositioned the camera after the AI selected the cast and selected the forward view for the draw checks. It left the Gazer's target, action, and animation phase under game control.

Each of the five phases submitted one DOS quad with the expected Gazer palette (`0x7e18`), texture page, and four UV corners. The compact atlas indices for phases 0–4 were 31, 24, 25, 24, and 13. DOS uses the same artwork at phases 1 and 3. The native spell dispatcher ran for that Gazer, and the Gazer returned to stance. This closes the remaining AI-initiated cast check for the mixed-room combat milestone.


### Warren dialogue follow-up

Warren is the Level 6 type-97 ghost at archived tile (4, 5), with identity 207. In the local DOS install, his personal name is present, `CNV.ARK` slot 207 has a zero offset, and `STRINGS.PAK` has no matching conversation block (`0x0ecf`). Clean Japanese Rev 1 has 92 unique conversation IDs in its native PSX table, including the Academy controls Gralwart (188), Louvnon (193), and Dominus (194). The table excludes 207. Earlier DuckStation checks showed the English no-response message on a fresh character and after the Murgo rescue and Dr. Owl handoff. The progressed-save trace returned `-1` at the conversation selector before dispatch, which explains why translation text alone cannot change the result.

A short, original, opt-in Warren interaction is feasible in principle. First prototype an identity-specific branch at the failed conversation lookup and establish how to enter and close the existing English dialogue UI safely. Keep the original actor record and native conversation table intact. Use a neutral line and ordinary dismiss input. Treat this as a new interaction. A restoration would require a verified original script and text from another legitimate source. This proposal adds no runtime code.

Acceptance criteria for an implementation PR:

- Confirm the branch matches only Warren’s original Level 6 record after native talk eligibility checks. With the preview flag disabled, reproduce the existing no-response behavior.
- Use normal controller input to open and close the dialogue on fresh and progressed saves. Check hostile and unavailable states, and confirm Warren returns to the expected DOS sprite and palette after dismissing the dialogue.
- Compare quest flags, inventory, and actor state before and after the interaction. Confirm no change to the Murgo rescue and Dr. Owl handoff. Verify nearby Academy conversations and the dialogue footer controls.
- Build from clean Japanese Rev 1. Verify the xdelta and all four CHD tracks, cold-boot in DuckStation, and record the build hash and evidence. Keep the proposal independent of the Warren combat-art change.

## Dedicated ghoul, Gazer, and wizard banks

The combat preview extends the compact action tables to the Level 4 wizard bank, the Level 5 Judy, Anjor, and ghoul banks, Level 7 Tyball, and the Level 8 ghoul bank. On Level 6 it adds the remaining actions to the Academy ghoul bank and adds combat and casting in both secondary wizard banks and the Gazer warren. The warren also keeps its Ghost family on DOS directional sprites and native combat poses. The secondary wizard banks and warren keep the primary wizard palette variants available.

The ghoul source supplies stance, ready, melee, hit, and death poses. Its cast action preserves the native renderer. The Gazer and wizard families also have DOS casting phases. The Academy preview reloads the resident renderer with each bank and restores the floor owner before uploading textures. Tyball and the Gazer warren record one ordering-table head per depth bucket, so repeated polygon submissions do not exhaust the log.


DuckStation captured live actor projections and replayed ten action values from front and rear views at native phases 0, 3, and 15. The probe compared each DOS packet's texture page, palette, and four UVs against the actor's frame record. Each expected native fallback preserved the packet and ordering heads. A separate control draw confirmed the actor's palette in the loaded bank.

| Level | Bank and actor type IDs | DOS packets | Native fallbacks |
| --- | --- | ---: | ---: |
| 4 | 13 (106) | 54 | 6 |
| 5 | 1 (107), 2 (99, 110), 3 (106) | 204 | 36 |
| 6 | 1 (106, 115), 2 (107), 3 (97, 102), 9 (105) | 276 | 84 |
| 7 | 1 (123) | 54 | 6 |
| 8 | 8 (110) | 48 | 12 |
| Total | 13 actor encounters across 10 banks | 636 | 144 |

The Academy switched back to the primary bank with the correct floor owner. Tyball's verified draw used 37 unique ordering buckets after the original per-polygon log exceeded 128 entries. The combat xdelta round-trip and all four CHD track readbacks passed. Track 1 matched `619b7b76837d008690679e3c9812a0510991154b`. Both lighting recipes passed their xdelta round-trips. The default `--late-dialogue` recipe reproduced `e3e2845b85d665a1240c5c89fab828b8703850b2`.

#### Game-selected dedicated combat actions

DuckStation ran the combat preview with Track 1 `619b7b76837d008690679e3c9812a0510991154b`. The probe entered the encounter from a disposable checkpoint and assigned the creature a player target. The game chose the action and advanced its phases. The debugger adjusted the camera or forward-view selection for packet capture. The probe compared the Gazer and wizard texture page, palette, and four UV corners against the dedicated DOS tables. The ghoul check compared its palette and four UV corners.

| Encounter | Native action | Result |
| --- | --- | --- |
| Level 6 bank 9, Academy ghoul (105) | Melee (`0x02`) | All five DOS phases matched. The same actor reached the native damage handler with the player as target. |
| Level 6 bank 3, Academy Gazer (102) | Cast (`0x0d`) | All five DOS phases matched. The native dispatcher ran and the Gazer returned to stance. |
| Level 4 bank 13, wizard (106) | Cast (`0x0d`) | All five DOS phases matched. The native dispatcher ran and the wizard returned to stance. |
| Level 7 bank 1, Tyball (123) | Cast (`0x0d`) | All five DOS phases matched. The native dispatcher ran and Tyball returned to stance. |

The Gazer cast after the probe entered the warren at tile (52, 52). Native AI selected the Gazer and Tyball casts at `0x800330a8` and the Level 4 wizard cast at `0x80032ec0`. The spell dispatcher confirmed the same actor in all three cases.

## Combat and lighting release

The local release builder now selects the cumulative `--dos-shade-maps` recipe. Its Track 1 SHA-1 is `78427bb7dea91c18fc2ca345865983a2ad6cc642`. It includes the mixed and dedicated combat banks, the Slasher poses, native sprite lighting, and gameplay-driven normal and monochrome DOS shades. The release builder verified the input CUE and the four clean tracks, decoded the resulting xdelta against Japanese Rev 1, and verified all four CHD readback tracks and indexes. The translated BIN and a locally generated translation-input delta produced byte-identical release xdelta and CHD files.

On the packaged CHD, the Level 2 to Level 1 reload selected the on-disc lighting bank. A lit torch selected effective light level 2 and extinguishing it restored level 0. Light selected normal level 3, Night Vision selected monochrome level 5, and both spell expiries restored darkness. The debugger invoked the native inventory and spell routines. In a separate encounter it assigned Tyball a player target. The game selected the cast, drew all five DOS phases, dispatched the spell, and returned to stance.
