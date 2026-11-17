---
id: TASK-48
title: Panel races and robustness
status: To Do
assignee: []
created_date: '2026-11-17T12:40:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: high
type: bug
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review.

- a stale folder listing or picture info response never replaces a newer one
- Save and the turn buttons cannot run twice at once
- changing the language keeps open dialogs and upload progress
- dropping files on the top level is not accepted
- a malformed folder URL falls back to the top level
- size="s" instead of the deprecated size="small"; the broken CSS fragment is gone
- thumbnail URLs are stable between listings and do not break after an hour
- the drop overlay and viewer show folder names, not IDs
- untranslated strings ("network error", HTTP status), "1 items"
- text files in legacy encodings (Windows-1250/1252) are shown
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fast navigation and fast previous/next always show the latest request's result
- [ ] #2 Double-clicking Save sends one edit
- [ ] #3 A language change keeps dialogs and uploads
- [ ] #4 Thumbnails are not downloaded again on every listing and keep working after an hour
- [ ] #5 No console warnings or errors; panel check passes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
