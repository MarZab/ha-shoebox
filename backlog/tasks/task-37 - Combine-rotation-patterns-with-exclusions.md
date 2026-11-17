---
id: TASK-37
title: Combine rotation patterns, with exclusions
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T11:58:00Z'
updated_date: '2026-11-17T12:01:00Z'
labels:
  - integration
milestone: m-3
dependencies: []
priority: medium
type: feature
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A rotation shows every picture any of its patterns selects, minus pictures selected by a pattern starting with "!", such as !**/private/**. This replaces the fallbacks (the first pattern with pictures), and with them the pattern-in-use attribute.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Pictures of all patterns are combined, without duplicates; ! patterns exclude
- [x] #2 Invalid patterns, also after !, are refused in the rotation flow
- [x] #3 The pattern-in-use attribute is gone from the entity, diagnostics, panel and preview; stored state from before still loads
- [x] #4 Docs describe combining and excluding
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
media.select_pictures replaces first_match: pictures of all patterns, sorted, once each, minus those of ! patterns; each pattern is compiled once. media.check_pattern validates patterns also after !. The pattern-in-use attribute is gone from the image entity, diagnostics, the panel and the preview; stored state with old fields still loads (unknown fields are ignored). Checked in the Docker HA: state stored before loaded; */Family/** with !**/Kids art/** previewed 4 pictures across both folders and the rotation only showed those.
<!-- SECTION:NOTES:END -->
