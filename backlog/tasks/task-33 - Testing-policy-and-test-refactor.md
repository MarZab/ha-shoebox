---
id: TASK-33
title: Testing policy and test refactor
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T11:02:00Z'
updated_date: '2026-11-17T11:06:00Z'
labels:
  - tests
  - docs
milestone: m-5
dependencies: []
priority: medium
type: chore
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Adopt the testing policy in AGENTS.md (docs/testing.md points to it) and bring the existing tests in line: behaviour at public boundaries, table-driven, no tests of internals, constants, test helpers or Home Assistant itself, no mocks of our own code, no coverage-only tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AGENTS.md has the testing policy; docs/testing.md links to it
- [x] #2 Tests of internals, constants, test helpers and framework behaviour are gone
- [x] #3 Near-identical tests are table-driven; files are grouped by feature, not by function
- [x] #4 No test mocks code of this repository; coverage-only tests are gone
- [x] #5 Removed tests that might have been worth keeping are listed in the notes
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Policy in AGENTS.md (Tests), linked from docs/testing.md. Tests: 164 functions / 350 cases -> 105 / 289; coverage 98% -> 96%.

Removed: tests of a constant (test_const) and of the test helpers (test_images); coverage-only cache tests (failed write, files vanishing) and unusual EXIF values; Home Assistant behaviour (YAML repair issue, single config entry); duplicates (PNG info in the panel, cross-folder move and listing already covered at the library, button removal). Merged into tables: resolve, imaging refusals, file operation refusals, cache options, setup retries, admin-only checks, upload refusals; image and button tests are test_entities.py; the cross-folder rotation is in test_rotations.py. The file system error test uses a real read-only folder instead of patching media.delete.

Left out, possibly worth a test: the render cap (needs patching imaging.render), the 200 MB upload limit (needs a large body or patching the constant), the media source when Shoebox is not set up, the rotation preview with no matches, a failed cache write leaving no temporary file. Kept although not behaviour: test_definitions and test_docs, which keep translations, services.yaml and doc links in step.
<!-- SECTION:NOTES:END -->
