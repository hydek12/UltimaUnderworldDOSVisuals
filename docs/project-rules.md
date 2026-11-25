# Project rules

These rules come from the Ultima Underworld PSX project thread in Slack. Use the [pull request workflow](pull-request-workflow.md) for changes to `main`. Post verification and milestone updates in the [project thread](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795464039475459).

## Baseline and distribution

- Build the combined patch from clean Japanese Rev 1 raw Mode 2/2352 Track 1, serial SLPS-00742 and SHA-1 `937ae8cf9a65526f2622c39d34205941f22c10cb`. Preserve the original archive, CUE, and three audio tracks, including pregaps and track layout. Use the existing English Batocera image as a comparison reference.
- Supply the DOS installation and separately obtained upstream English translation locally. Publish the source, patch recipe, command-line builder, and guide. Keep original game files, extracted game assets, translation payloads, generated xdelta files, and BIN/CUE and CHD images out of GitHub release packages. Use curated, captioned gameplay screenshots in the documentation gallery and for selected Slack updates.
- Keep the application, player-facing UI, and DuckStation title in English. Include **English Patch** in the preview title. Keep the work folder outside iCloud-backed locations where possible.

## Verification and cleanup

- Verify each affected original encounter before marking it complete. Check the actor or effect identity, DOS asset, supported facings and actions, palette, and applicable interactions. Include matched DOS and PSX captures when comparing visuals and record native fallbacks and dormant exceptions. Distinguish normal gameplay and original encounter behavior from debugger staging and controlled replays.
- Preserve native identity, collision, dialogue, AI, and combat timing when changing visuals. Check scale, hotspots, transparency, occlusion, VRAM, and frame timing as applicable. For named NPCs, exercise dialogue, quest branches, trade, and sprite restoration after leaving dialogue and inventory.
- Test disc changes on a separate local candidate. Fresh-boot its CHD, round-trip the xdelta from clean Rev 1, and compare all four extracted tracks with their expected bytes. Verify original audio, English UI and dialogue, music, combat, and save/load where applicable. Verify the installed image by readback when deploying to Batocera.
- Keep the latest verified test image as the active preview. Clean up superseded test CHDs and temporary BIN/CUE copies while preserving the original source media. Close DOSBox and DuckStation after testing and confirm DuckStation's exit dialog.

## Progress and milestones

- Continue the batch through its acceptance checks within any requested time limit. Post one-percentage-point progress as verified checklist gates pass, with evidence, limitations, what remains, and the relevant PR or source commit. Add one or two sentences of context to selected before-and-after captures.
- The original roadmap grouped integration at five-percentage-point milestones. Current work uses the newer PR workflow for verified changes, and the five-point gates remain the criteria for declaring project milestones. Keep measured subproject coverage distinct from the overall roadmap estimate. Advance a milestone after its acceptance criteria pass.

| Gate | Acceptance criteria |
| --- | --- |
| 65% | Verify wizard projectile and impact rendering, integrate matched DOS effects, cold-boot a new CHD, and round-trip the clean Rev 1 delta. |
| 70% | Verify eligible Level 6 and named NPCs, including supported facings, poses, palettes, dormant activation, dialogue, trade, Murgo's handoff to Dr. Owl, and Warren in a progressed save. Check sprite restoration after dialogue and inventory on a cumulative CHD. |
| 75% | Verify recurring creature and humanoid families on Levels 1–4, shared rooms, bank boundaries, stairs, revisits, and save/load. |
| 80% | Verify recurring families on Levels 5–9, special models, and dormant activations. Record a disposition for all 657 PSX records, including the reason for each native fallback. |
| 85% | Verify applicable stance, attack, casting, retreat, impact, and death poses across families. Compare palettes, lighting, scale, hotspots, transparency, and occlusion. Verify native fallbacks and preserve native gameplay. |
| 90% | Compare matched DOS and PSX environments, implement feasible visual changes, and capture matched views. Verify English menus, HUD, inventory, prompts, and preview title. |
| 95% | Reproduce the release candidate from clean local inputs, cold-boot a fresh four-track CHD, and verify the delta and original audio. Play named quest handoffs through the ending, including save/load and floor transitions. |
| 100% | Publish the source recipe, CLI builder, guide, and curated gallery. Reproduce the build from the published instructions, close the verification and audit checklist, and record the release commit in Slack. |

## Slack references

- [Project scope and implementation plan](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795464039475459)
- [Standing release rules](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795533869607129)
- [Test image cleanup](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795534468022919)
- [Milestone criteria](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795538332017449)
- [Updated working rules](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795545315949759)
- [Project roadmap and update cadence](https://hydeksworkspace.slack.com/archives/C0CL4CBU2TE/p1795549834220249)
