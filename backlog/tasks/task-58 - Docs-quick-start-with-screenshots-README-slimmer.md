---
id: TASK-58
title: 'Docs: quick start with screenshots; README slimmer'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T14:58:00Z'
updated_date: '2026-11-17T14:58:00Z'
labels:
  - docs
milestone: m-5
dependencies: []
priority: medium
type: docs
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The README's quick starts and its actions and entities table move into docs/. A new docs/quick-start.md adds a rotation and puts it on a dashboard with two screenshots, and keeps the ESPHome start. The README shows the panel and the editor as two small thumbnails.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 docs/quick-start.md: adding a rotation and a dashboard card, with two screenshots; the ESPHome start
- [x] #2 The actions and entities table is in docs/README.md; the README links to both
- [x] #3 The README shows the panel and editor screenshots side by side, linking to the full pictures
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Found while taking the screenshots and fixed: the rotation step's patterns help was rendered as Markdown, so ** became bold; now code spans (en, sl). The editor's picture was 50vh tall and pushed itself under the dialog footer; it now gets the height left after the dialog's own parts (max(200px, 100vh - 440px)). Screenshots are JPEG at 2x; editor.png replaced by editor.jpg.
<!-- SECTION:NOTES:END -->
