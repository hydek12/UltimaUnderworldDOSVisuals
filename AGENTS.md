# Repository instructions

- Put every change to `main` through a GitHub pull request. Work on a topic branch, push that branch, and open a PR against `main`. This applies to code, docs, fixes, and rollbacks.
- Use the PR template. Describe what changed and why, list measurable acceptance criteria, and record the checks actually run and their results. List any pending checks and distinguish emulator staging, normal controller input, build verification, and deployment where relevant.
- Update the affected project documentation in the same PR. Use a merge commit to preserve the PR as a discrete change that can be audited or reverted. Retain the GitHub PR and its verification evidence.
- Review and merge when authorized and the acceptance criteria are met. Follow GitHub's reviewer and merge permissions.
- Follow [the pull request workflow](docs/pull-request-workflow.md). For work that predates it, use [the historical commit log](docs/change-history.md).
- Follow the [project rules](docs/project-rules.md) for baselines, source-only releases, emulator verification, milestone criteria, and Slack reporting.

## Testing directions

- Preserve the original save and test from a disposable checkpoint or backed-up test memory card. When supplies run low, restock the test copy with native recovery items and verify that it reloads. Verify the equipped gear, consumables, and original quest items before continuing.
- Use in-game inventory containers, such as sacks, when available and compatible with the test. Use normal controller inputs to store and retrieve items. Before a quest handoff, verify the original quest item is accessible in the inventory slot the interaction uses.
- Use normal controller input for acceptance runs. Equip appropriate armor, heal as needed, and bypass enemies when the route allows. Before confirming or releasing an attack, aim the targeting reticle directly at the enemy if one is displayed. For attacks without a reticle, including charged sword strikes, center the enemy on screen before striking. Try a native damage spell when melee is ineffective.
- Use an in-game lighting item, such as a torch, when available and compatible with the test. Keep the required lighting conditions for darkness and comparison checks, and record which light source was active.
- Verify damage with enemy health before and after the action. A swing, a targeting reticle, or a visible projectile confirms input or casting. A health decrease attributable to the player confirms damage.
- Keep staging and verification distinct. Record any staged equipment, supplies, or position. Use read-only inspection during the run to confirm state. For route and quest checks, record each required transition and verify that the original item persists until the expected handoff or consumption.
- Save verified checkpoints separately, confirm the DuckStation exit dialog, and post verified results and pending checks in the GitHub PR and the `#projects` Slack thread.
