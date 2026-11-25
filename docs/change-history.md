# Historical change log

The 89 commits below were reachable from `main` when the pull request workflow was adopted. The entries use the original commit subjects in oldest-first order. GitHub had no historical PRs at that point. These commits document prior work and preserve its diffs. Historical review and testing evidence is recorded where available in the linked commits and project documentation.

Use [the pull request workflow](pull-request-workflow.md) for new changes. The [NPC backlog](npc-conversion-backlog.md), [dialogue and gameplay audit](named-dialogue-audit.md), and [local build and verification notes](local-patch-builder.md) give additional evidence for earlier milestones.

## Rev 1 tooling, facing, movement, and light

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-23 | [`b6a9955`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b6a9955c583c6e48d97b401f4cff5a6d79f79271) | Add Ultima Underworld Rev 1 visual patch tooling |
| 2026-11-23 | [`0ef8fbb`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/0ef8fbb8b90bc11e6f33a7b2490627f99679e07c) | Match Lanugo idle facing to DOS camera yaw |
| 2026-11-23 | [`d596356`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/d596356bb7994e55949099918d44f5035b869d22) | Animate Lanugo with the complete DOS idle cycle |
| 2026-11-23 | [`e8a657b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/e8a657b3dcd55946c3a5594cef138223070d1987) | Export Lanugo directional walking atlas |
| 2026-11-23 | [`e6804d6`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/e6804d67be1b938e610585082f1ea202e810b188) | Render and verify Lanugo DOS walking sprites |
| 2026-11-23 | [`cedce76`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/cedce76b95fdebd00226980e0a529ef45e429190) | Cover Level 1 green goblins and guard atlas uploads |
| 2026-11-23 | [`0bf55e9`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/0bf55e9a57ea3e1943630eefc3190bbb134e3ae9) | Render all four Level 1 green goblin palettes |
| 2026-11-23 | [`406d853`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/406d853be3ad0a396b9f9be5a836345de53a9d11) | Export original DOS lighting rows for sprite comparisons |
| 2026-11-23 | [`147a469`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/147a46978f3b07ae12f28d7cfb700ca511480cdf) | Resolve the full PSX creature roster and DOS sprite shade |
| 2026-11-23 | [`21d13ee`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/21d13ee245f8e3df0f1c39b993e613c718c44641) | Build a separate DOS distance-lighting preview |
| 2026-11-23 | [`d44c22b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/d44c22b048a64172446d14c57de77f0990662780) | Record remaining artwork and native lighting work |

## Creature inventory and local build recipe

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-24 | [`7f4575f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/7f4575f9e84d060ba3adfaa5b117e2e32b53c637) | Add DOS goblin sprites for deeper floors |
| 2026-11-24 | [`80a830d`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/80a830db038b8a9b1e3581f98c1f2dabed666e1f) | Convert DOS lizardmen and Level 8 rats |
| 2026-11-24 | [`0cdd44e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/0cdd44ea0d127830cb4bb261841a619395e32bf5) | Document NPC renderer changes with gameplay screenshots |
| 2026-11-24 | [`1196dff`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/1196dff6755c09c0c380b8d52ad552317d4e98cc) | Publish PlayStation NPC conversion backlog |
| 2026-11-24 | [`ff656e3`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/ff656e3c8bb75e5affb7647dd2794f40a07d497c) | Record cumulative NPC atlas reload results |
| 2026-11-24 | [`1293e0a`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/1293e0a225ba34ade7ad5091f2a87249888dc59a) | Build the English DOS preview from local game inputs |
| 2026-11-24 | [`93f931c`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/93f931c1c459fa49a7ee30c972eafe7a54ee7bb9) | Accept local translation deltas and document source-only releases |

## Academy sprite banks and dialogue

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-24 | [`e63350c`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/e63350c06a1c8569927f9323116f90f4ee482071) | Add optional DOS wizard sprites on Level 6 |
| 2026-11-24 | [`4ee4d79`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/4ee4d790f50a5d63ad2e1a1085dcc719866947d6) | Document the matched Level 6 wizard screenshots |
| 2026-11-24 | [`8468bc1`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/8468bc1668e8734de375b61658f1481c33737d6d) | Add DOS spiders to the Level 6 preview |
| 2026-11-24 | [`ea2602e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/ea2602e5cf59fbe5ae03a45574ed5b31ac28d2e9) | Document the Level 6 spider comparison |
| 2026-11-24 | [`eda8acf`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/eda8acfd2b00fa32df0f3fd746fbd867162c404f) | Render Level 6 wizard casting with DOS sprites |
| 2026-11-24 | [`94aa5e1`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/94aa5e1214d671f1277a9568ba27c86871e7e8f0) | Document the wizard casting comparison |
| 2026-11-24 | [`50a272f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/50a272f9ca7b0d72ac29bf82657f27640d684bf0) | Add DOS combat poses for Level 6 wizards |
| 2026-11-24 | [`d908939`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/d908939aab855d93f279a8e20621dbd4256d4929) | Document the Level 6 DOS wizard melee pose |
| 2026-11-24 | [`50d44c4`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/50d44c44aa9098139b5277dae161a9f192baa366) | Export DOS wizard projectile and impact frames |
| 2026-11-24 | [`c82d0ba`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/c82d0ba26f4512d8f7d017dcaeae298b4a549f67) | Use DOS graphics for shared wizard spell effects |
| 2026-11-24 | [`155947b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/155947b8f9393703f709e11a8d7d91b56d07357d) | Expand Level 6 DOS sprite coverage for grubs, slugs, and bats |
| 2026-11-24 | [`c37504f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/c37504f4de85f26e9eddcf71e0e974a227aa13ac) | Keep expanded NPC poses clear of floor-loader RAM |
| 2026-11-24 | [`fc6fd86`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/fc6fd8628692f77952de36ec8f7f181057efc936) | Restore DOS NPC textures when dialogue closes |
| 2026-11-24 | [`bea7198`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/bea7198cb9060627d460b07d83a49b920d324d7d) | Share stable inventory and dialogue return hooks |
| 2026-11-24 | [`6082b4a`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/6082b4a51b2a97583b8f1fff614eb5b5a3e48d85) | Add locally built Academy sprite previews |
| 2026-11-24 | [`74ba8e7`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/74ba8e77ef6f6e4fcad0fed3645c4103bd438e51) | Switch Level 6 DOS sprite banks between frames |
| 2026-11-24 | [`346de2e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/346de2e46a98a3a6d699c24b773ff336be400e57) | Add imp, skeleton, ghoul, and headless NPC banks |
| 2026-11-24 | [`bd865dc`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/bd865dc4ab08eaf7281e107a49fa79c6ebba81b3) | Add DOS combat poses for Level 6 creatures |

## Named NPCs and floor coverage

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-24 | [`95918b2`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/95918b278dc325d157187f0a59967626ecd7f10f) | Audit named DOS dialogue identities across PSX revisions |
| 2026-11-24 | [`7a3ea15`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/7a3ea15e78fccfeaeec120fa4be1faacd6bbf253) | Add runtime DOS banks for Level 1 dialogue NPCs |
| 2026-11-24 | [`4b13747`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/4b13747020b9c3e87e78c9d71ed33e2f01c88342) | Expand named NPC floor-bank addressing |
| 2026-11-24 | [`cf34d1e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/cf34d1e5f1af5dd26dccd201031336ee3c4e0027) | Record Academy dialogue checks on the extended floor build |
| 2026-11-24 | [`06b19cd`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/06b19cd9eb71ef05f4d67ca4eee01946fb0e0bf0) | Add DOS sprite banks for Level 2 named NPCs |
| 2026-11-24 | [`9a284ad`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/9a284ad5483ca74e9d004edf4a507760cca59913) | Add shared DOS sprite banks for Level 3 encounters |
| 2026-11-24 | [`45a3fae`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/45a3fae9ac78166ca19d2cb709378087229e6222) | Add Level 4 DOS sprite banks and one-percent gates |
| 2026-11-24 | [`b9450f5`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b9450f56367b8fecd3de7bfa6d0489562df1f9ea) | Verify the 70 percent named NPC and quest milestone |
| 2026-11-24 | [`6593cc4`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/6593cc46bf3e78f619c83a121cd22fd1d7f202ac) | Convert and verify recurring creatures on Levels 1–4 |
| 2026-11-24 | [`e2d58bf`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/e2d58bf93708f13de987972fcceeb9ed97aaec90) | Add and verify late-floor creature and hazard banks |
| 2026-11-24 | [`08fb7ff`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/08fb7ffef5ce51d77f1aaa84aa43d9faeb7f9475) | Ship the verified local xdelta and CHD recipe |

## Combat, lighting, and release promotion

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-24 | [`86b724f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/86b724f15aa6daae14e7e7972284e00ad633c589) | Verify the 85 percent combat milestone |
| 2026-11-24 | [`5499f90`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/5499f90076bd9ae90565a8dc6ff826138ed760fc) | Verify native sprite lighting and the 90 percent milestone |
| 2026-11-24 | [`955ef9b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/955ef9bf43d5f13aa64337a7a68f61212b30c3b1) | Verify DOS shade maps and the 95 percent milestone |
| 2026-11-24 | [`a49ca5f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/a49ca5f3185a7e5f0af8c0926bbb6f1902c2b6ac) | Drive DOS goblin lighting from native torch and spell state |
| 2026-11-24 | [`534e03e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/534e03eb5ca1163557eb82341061ce805efd9957) | Cover the Level 1 imp, Level 3 goblin, and Level 5 Gazer |
| 2026-11-24 | [`6789309`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/678930951f3b53b440cbc9eb26a08a205e80b193) | Fill dormant creature sprite coverage and verify goblin rest trigger |
| 2026-11-25 | [`b564562`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b56456208d08ec32eab7e414d378db4274c89e8f) | Extend dedicated critter combat poses and verify the native goblin spawn |
| 2026-11-25 | [`2016c21`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/2016c21af3a72badf7f21c0e2c752090212d505a) | Select DOS combat poses per family in mixed room banks |
| 2026-11-25 | [`4ba8970`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/4ba8970ba6ad2963aa1d0c50cd5b1e2a838524fe) | Preserve Gazer combat draws in the Level 5 mixed bank |
| 2026-11-25 | [`d1d83a4`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/d1d83a4b37aa8d6235c32b684700fad847e74f0f) | Protect ordering in every mixed Gazer room |
| 2026-11-25 | [`1fe7362`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/1fe736224af349aa3ccc97315ba25b98d2cbfece) | Verify the Level 5 Gazer cast from native AI |
| 2026-11-25 | [`4ae4e74`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/4ae4e746169e79a2109803c346c24e2b951c1091) | Add DOS combat poses to remaining dedicated creature banks |
| 2026-11-25 | [`6c065c1`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/6c065c12fc204f6a1df7cd6691c289c33c5aa726) | Verify game-selected attacks in dedicated creature banks |
| 2026-11-25 | [`83f385c`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/83f385c8ddce363286114ad3e8c9a3506bcc2c5f) | Promote DOS combat and lighting to the local release |

## Context-sensitive controls and Batocera deployment

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-25 | [`b2c5b1c`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b2c5b1c666c284a3d0fe08a2c08dbbc7f29c443d) | Prototype context-sensitive Options button legend |
| 2026-11-25 | [`b1a710e`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b1a710e8d66c4fbdc34d6c45bd30dad043b07202) | Add context-sensitive controls to the inventory |
| 2026-11-25 | [`de78579`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/de7857945c03129a0c0dd842681ec25bd915df41) | Add context controls to rune and spell menus |
| 2026-11-25 | [`2b743dc`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/2b743dc8234d50c0379d37dbdeca311905dcf5ed) | Add context controls to dialogue screens |
| 2026-11-25 | [`44768be`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/44768bea74bdf1fa5fc72f9a71dcded2a20d8ec1) | Fit menu prompts around the PlayStation HUD and dialogue |
| 2026-11-25 | [`8ded130`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/8ded130edea2d0c834c1d717362e9886f2a11346) | Keep menu controls resident across a cold boot |
| 2026-11-25 | [`0653087`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/0653087506ff75ede7334663afbed5c73cfb9040) | Show contextual inventory button actions |
| 2026-11-25 | [`3beb992`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/3beb9927b0e8295a81a9d2ba2d646a20a008fdf0) | Use PSX button glyphs in compact menu legends |
| 2026-11-25 | [`8fdb826`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/8fdb826f300435aad9f864ee6c49705cbab26f51) | Center and standardize contextual button legends |
| 2026-11-25 | [`ee114b3`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/ee114b392050cabd3bcd1be9d6d4dd2740c0d08a) | Add a contextual legend to the automap |
| 2026-11-25 | [`44b5b3b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/44b5b3b2527665d21e1a2c97fb30531d0443ab13) | Deploy verified local previews to Batocera |
| 2026-11-25 | [`6f27b76`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/6f27b7647f79a69ea81602d45d9f39c915b1566a) | Right-align dialogue prompts in the footer |

## Creature coverage, combat poses, and native activation

| Date | Commit | Recorded change |
| --- | --- | --- |
| 2026-11-25 | [`2b95df5`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/2b95df527926ff1d889bdf383d12169d783d5cbf) | Fill Level 8 critter coverage at three bank boundaries |
| 2026-11-25 | [`cf0c85f`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/cf0c85f5e904639f7d8e0a01bb900b7d817add53) | Record live Level 8 boundary renderer checks |
| 2026-11-25 | [`72845c8`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/72845c8af78cab5fa0fe33978675a787f8320aba) | Add green goblin poses to the Level 7 troll bank |
| 2026-11-25 | [`c7cb5a0`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/c7cb5a06d071add4a035c1928051c0a5a6bafc3f) | Close the remaining Level 7 sprite coverage gaps |
| 2026-11-25 | [`bdb008d`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/bdb008d0e72a4b84f57f052b064d7b3693e7190f) | Close the remaining Level 8 sprite coverage gaps |
| 2026-11-25 | [`b8c8345`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b8c8345f16adf6503cf6f862cddd73f74d82d555) | Fill the Level 6 bat approach gaps |
| 2026-11-25 | [`f4895e7`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/f4895e7c0fe03d26a094013e1d2678a3b776ac32) | Close the remaining Level 6 sprite coverage gaps |
| 2026-11-25 | [`ece4abb`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/ece4abbd4ca7415a169fc380f8c4dc3b9c3bd178) | Close five Level 1 goblin gaps and document button legends |
| 2026-11-25 | [`905fb8d`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/905fb8d92f47dfead3f674014bb16fbf23de92cf) | Close the last Level 2 and Level 4 sprite coverage gaps |
| 2026-11-25 | [`9f6549b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/9f6549b12aef12a809226edb144dac3eb6dccc73) | Add DOS combat poses to dedicated fire elemental banks |
| 2026-11-25 | [`0c0e16b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/0c0e16b4461035edd1984effcfd2a855cd88875a) | Add dedicated spider combat and verify the Level 5 fire trap |
| 2026-11-25 | [`70b4d28`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/70b4d28cc3b8f68d9734f982dc4a03b51bdb3344) | Add DOS combat poses to the Academy default spider bank |
| 2026-11-25 | [`b523f74`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/b523f743d00ea46691dbe84a8bf1c6adac7ce0f8) | Document Level 6 dormant spider activation checks |
| 2026-11-25 | [`947282b`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/947282bd0e38bf919b8a78a49b50241b7a96afd7) | Verify Level 6 wandering spider spawns through rest |
| 2026-11-25 | [`3c30d87`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/3c30d87946f28281e85114c0d60bbf238d0f306f) | Verify Level 7 fire elemental activation by archive record |
| 2026-11-25 | [`890693c`](https://github.com/hydek12/UltimaUnderworldDOSVisuals/commit/890693c0d6f7b1823f69df762ec0d6214f0e164b) | Verify the remaining Level 7 fire elemental spawn |
