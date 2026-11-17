---
id: TASK-49
title: Docs and translations match the current design
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:03:00Z'
labels:
  - docs
milestone: m-5
dependencies: []
priority: high
type: docs
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review: services.yaml examples and field descriptions use prefixed paths; move's "to" is described correctly; the rotation step text mentions shuffle; use-cases.md describes the current editor; the README/panel screenshot is retaken; architecture.md lists the current state fields and views; displays.md says the image entity token rotates; security.md says what the media view shows non-admins; README explains adding a custom HACS repository for the first release; smaller stale wording listed in the review.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No example or description uses unprefixed paths or describes removed behaviour
- [x] #2 The README and panel screenshots show the current panel
- [x] #3 displays.md and security.md are accurate about tokens and what non-admins can see
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
services.yaml examples and both translations' field texts use local/... paths; move 'to' described as a folder or a media folder itself; rotation step mentions shuffle. Docstrings (runtime, views, diagnostics, rotations) and the panel comment updated. architecture.md: download view, order, state fields, what the media view shows. security.md: media view shows every selected picture to all users. displays.md: entity_picture token rotates every 5 minutes; image_proxy and the device URL. README: custom repository step, display id 'frame' as in displays.md. use-cases: current editor, New folder inside My media. panel.md ⋮ menu items; troubleshooting 400/401/404; testing.md file names; development.md frontend pin. New panel screenshot.
<!-- SECTION:NOTES:END -->
