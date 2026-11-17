---
id: TASK-30
title: Release task
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 Refuses a dirty tree, an existing tag or an older version
- [ ] #2 Version arithmetic tested for stable, beta, rc and final
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
