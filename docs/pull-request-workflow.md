# Pull request workflow

The merged pull requests against `main` are the cumulative change log. Each PR should describe a coherent change that can be reviewed and rolled back on its own.

1. Start a topic branch from current `main`, then commit and push the branch. Open a PR against `main` before integrating changes.
2. Fill in the PR template with the changes, observable acceptance criteria, verification evidence, and any deployment or rollback details. State what remains untested. Update the affected repository documentation in that PR.
3. Review the diff against the criteria. Record the tested patch profile and hashes when the disc or patch changes. For live gameplay, state how the test was staged, what normal input was used, and what the game did. Keep local game inputs, patched disc images, and saves out of GitHub.
4. Merge using **Create a merge commit** once the criteria pass or the project owner explicitly accepts a documented exception. A GitHub approval can be recorded by an eligible reviewer when needed. The PR author can record a self-review in the PR description.
5. For deployment, record the image or patch verified on the target and link back to the PR. A documentation-only PR can point to prior deployment evidence if the build inputs are identical.

## Audit and rollback

Use the PR's files, commits, and verification notes for the scope of an individual change. Use Git's first-parent history on `main` to see the order of integrated PRs. The [pre-PR commit index](change-history.md) covers the earlier history.

To roll back a merged PR, branch from current `main` and use GitHub's **Revert** action or `git revert -m 1 <merge-commit>`. Open a revert PR that links to the original, documents the behavior to restore, and records the verification. For history before this workflow, identify the specific commits and review dependencies before reverting them in a new PR. Preserve the published history.

If the rollback affects a deployed patch, rebuild the intended revision from its recorded inputs, verify the image or patch, and redeploy it. Reverting Git commits does not replace an installed Batocera image.

## Enforcement

The repository instructions and PR template apply to contributors and automation. GitHub rejected repository rulesets on the current private-repository plan, so adherence to this workflow requires following the repository instructions.
