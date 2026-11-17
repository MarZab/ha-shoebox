---
id: TASK-31
title: First release
status: Done
assignee: []
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T16:02:00Z'
labels:
  - release
milestone: m-6
dependencies:
  - TASK-4
  - TASK-5
  - TASK-25
  - TASK-26
  - TASK-27
  - TASK-28
  - TASK-30
priority: high
type: task
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Release 0.1.0, the version already in manifest.json: mise run release -- 0.1.0 tags it without a version commit and pushes branch and tag atomically. Then install it through HACS as a custom repository on a clean Docker HA. Needs the GitHub repository (TASK-4).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CHANGELOG has the version's entry
- [x] #2 The tag matches manifest.json and release.yaml creates the GitHub release
- [x] #3 Installed through HACS on a clean HA: integration, rotations, actions, entities, device URL and panel work
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
v0.1.0 tagged by the user with mise run release; release.yaml succeeded and published a full release. Installed on a clean HA 2026.10.4 from the v0.1.0 tag's custom_components/shoebox (what HACS downloads for a release; the HACS UI itself needs a GitHub login, not available here): integration loaded, rotation with preview, Next, shoebox.list, the device URL with the entity's token, and the panel. The release text is only GitHub's generated changelog link: TASK follow-up.
<!-- SECTION:NOTES:END -->
