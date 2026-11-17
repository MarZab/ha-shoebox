---
id: TASK-50
title: 'Tests: fix the upload refusals, cover order and old state'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:04:00Z'
labels:
  - tests
milestone: m-5
dependencies: []
priority: medium
type: task
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
From the review: the upload type and missing-file refusal tests never reach those checks (folder ""). Add, within the testing policy: a rotation's order reaches Next (path vs shuffle via the button), and stored state with old fields still loads. Make the file-system error test independent of running as root.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Upload type and missing-part refusals are actually exercised
- [x] #2 Order through the Next button and old stored state are tested
- [x] #3 Tests pass as root and as a normal user
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Upload refusals use folder=local and assert the message, so type, file name, missing file part and non-multipart are each reached (views.py 226-228 now covered); '..' in the query is refused by HA's security filter first, left to the library tests. Order through the Next button: 20 pictures, path is sorted, shuffle is each once and not sorted (chance 1/20!). Old stored state with a 'pattern' key loads and continues. The file error test uses a folder inside a file (ENOTDIR), the same as root; it also checks the path is media-relative. image_proxy 500 assertion replaced with state unknown; media view refusals are exactly 404.
<!-- SECTION:NOTES:END -->
