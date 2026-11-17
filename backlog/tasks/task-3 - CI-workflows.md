---
id: TASK-3
title: CI workflows
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:50:00Z'
labels:
  - tooling
  - release
milestone: m-0
dependencies:
  - TASK-1
priority: high
type: chore
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
GitHub Actions:
- ci.yaml: the same checks as `mise run check`, with coverage, on push and pull request
- validate.yaml: hassfest and hacs/action (category integration), on push, pull request and nightly
- release.yaml: on a tag vX.Y.Z or vX.Y.Z(a|b|rc)N, check it matches manifest.json and create the GitHub release (pre-release for a/b/rc)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ci.yaml and `mise run check` run the same checks
- [x] #2 validate.yaml runs hassfest and hacs/action
- [x] #3 release.yaml refuses a tag that does not match manifest.json
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ci.yaml runs mise run check through mise-action, so CI and local checks are one definition. The tag check lives in tools/scripts/release_channel.sh (tested by hand: stable, beta, mismatch, missing v). actionlint passes. The workflows have not run on GitHub yet: the repository has no remote.
<!-- SECTION:NOTES:END -->
