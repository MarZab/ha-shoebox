---
id: TASK-48
title: Panel races and robustness
status: Done
assignee: []
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:01:00Z'
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
- [x] #1 Fast navigation and fast previous/next always show the latest request's result
- [x] #2 Double-clicking Save sends one edit
- [x] #3 A language change keeps dialogs and uploads
- [x] #4 Thumbnails are not downloaded again on every listing and keep working after an hour
- [x] #5 No console warnings or errors; panel check passes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Folder and info loads carry a sequence number; stale answers are dropped. Edit is off while a picture loads; Save shows loading and a busy flag blocks a second save or turn. Language change rebuilds only the top bar (dialogs, uploads, drop overlay are siblings). Drop at the top level is ignored. Malformed folder URLs fall back to the top level. size=s; the broken CSS fragment and the unused code rule are gone. Thumbnail URLs carry the file's mtime and are signed once per user for 30 min (bounded LRU); the panel lists again after 25 min. Drop overlay and viewer show folder names. Plural item count via Intl.PluralRules (Slovenian one/two/few/other). Network and HTTP errors translated. Non-UTF-8 text decoded as windows-1250 (sl) or 1252. Empty files say so. Verified with the review's Playwright scripts and dev:panel.
<!-- SECTION:NOTES:END -->
