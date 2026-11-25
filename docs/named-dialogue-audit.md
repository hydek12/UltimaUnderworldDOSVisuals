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

The lighting option uses the PlayStation depth-light table for the two tested room banks. The DOS shade-map and monochrome checks are still open.
