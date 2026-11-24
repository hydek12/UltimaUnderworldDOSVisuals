# Level 6 combat preview verification

The runtime recipe restores DOS idle and walking sprites for the eleven Level 6 actors in this batch. Each actor keeps its native AI, projection, hit testing, and action timing. Sprite selection uses the original actor type, the active room bank, and the action and facing the renderer receives.

| Actor family and PSX type | Original Level 6 map tiles | DOS combat poses |
| --- | --- | --- |
| Skeleton 74 | (23, 58), (22, 57) | Stance, three melee sequences, retreat, death |
| Imp 75 | (60, 36) | Stance, three melee sequences, retreat, death, casting |
| Imp 81 | (36, 52), (37, 50) | Stance, three melee sequences, retreat, death, casting |
| Headless 91 | (46, 60), (26, 55), (27, 53), (51, 48) | Stance, three melee sequences, retreat, death |
| Ghoul 105 | (44, 37), (41, 37) | Stance and retreat |

DuckStation emitted a DOS sprite packet for each of the eleven original actor records in the rooms above. The encounter test used the game's native floor and room entry and debugger-controlled camera angles. It kept each actor's identity and checked the draw packet against that actor's palette row. Captured actions included standing, walking, and a headless combat stance. The separate controlled combat pass checked 448 packets across all five actor types. It sampled the first and last phase of every enabled action in all eight directions and checked the fixed combat frames and directional standing fallback.

The ghouls' attack and death graphics stay native because the candidate preserves its existing idle and walking texture resolution. DOS supplies four imp casting frames. The fourth frame is held when the native phase exceeds the DOS sequence. Rear and side views use the directional standing poses except for supported deaths, which use the fixed DOS pose from all sides.

The locally built xdelta decodes from clean Japanese Rev 1 Track 1 SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb` to `3d7d656c0e40038774a04be1e6198daadae92e37`. CHD verification and byte comparison of all four extracted tracks passed. The offline comparison checked 444 frame slots from the affected banks, including 124 combat frames, against the local DOS assets and the expected PSX palette conversion and texture geometry.

The latest test CHD is the Level 6 Combat NPC Preview. Its SHA-1 is `6ae33cde5f196cc9043cf1a4e997f584e2d77710`. The emulator's local English title includes the words English Patch. The previous workspace test CHD and scratch raw data track were removed after the new image passed.

## Milestone gates

The 70% milestone remains open while named quest and dialogue NPCs outside the completed coverage still need sprite and interaction verification. Match PSX dialogue records to DOS identities, account for encounter state and quest flags, and record which conversations can complete with each bank active. Preserve native rendering for unsupported special models. Verify return from conversations and inventory while retaining the selected bank.

After 70% passes, the 75% scope is recurring creature and humanoid families on Levels 1 through 4. Its loader checks include entering and leaving supported floors, restoring atlases after menus, and retaining correct fallback graphics when moving between floors.
