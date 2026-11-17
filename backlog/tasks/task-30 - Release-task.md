---
id: TASK-30
title: Release task
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:41:00Z'
labels:
  - release
  - tooling
milestone: m-6
dependencies:
  - TASK-3
priority: medium
type: chore
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
mise run release -- <version|patch|minor|major|beta|rc|final>: bumps manifest.json, commits, creates an annotated tag and pushes after confirmation. It shows the plan first; --dry-run only shows it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Refuses a dirty tree, an existing tag or an older version
- [x] #2 Version arithmetic tested for stable, beta, rc and final
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
tools/scripts/release.py and mise run release. Kinds patch, minor, major, beta, rc, final or an explicit newer version; pre-releases as 1.3.0b1 / 1.3.0rc1. Shows the plan (versions, commit, tag, push, GitHub channel, missing CHANGELOG section), refuses a dirty tree or an existing tag, asks before changing anything (--yes skips, --dry-run stops after the plan). Tests: version arithmetic and the tree checks on a temporary repository.
<!-- SECTION:NOTES:END -->
