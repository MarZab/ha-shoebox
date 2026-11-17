---
id: TASK-56
title: 'Panel: breadcrumb icon sits low; dev HA badge'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T14:43:00Z'
updated_date: '2026-11-17T14:44:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: low
type: bug
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The folder icon before Media still looked lower than the text: ha-icon is inline-block, so its box had a line-height gap above the 18 px glyph and the glyph sat at the bottom. The dev Home Assistant showed a 'country not configured' repair badge on Settings in screenshots.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The icon's glyph is centred on the text
- [x] #2 The dev Home Assistant shows no repair badge
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Breadcrumb ha-icon is display:flex, so its box is the glyph; measured glyph 76.5-94.5 and text 76.0-95.0 (centres 85.5). docker/ha-config sets country: US.

configuration.yaml is gitignored, so tools/tasks/dev/_env writes a first one with country and My media when there is none.
<!-- SECTION:NOTES:END -->
