---
id: TASK-24
title: 'Panel: translations'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:34:00Z'
labels:
  - panel
milestone: m-4
dependencies:
  - TASK-23
priority: medium
type: task
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every visible string comes from i18n.js and follows the user language with English as fallback. Wording follows HA style: sentence case, HA terms.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 No visible text outside the string table
- [x] #2 Changing the user language changes the panel
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
21 texts no longer used were removed from both languages. Every visible text goes through i18n.js; English is sentence case. Tests keep the English and Slovenian keys and placeholders equal and fail when the panel uses a key i18n.js lacks. Verified in the Docker HA: selecting Slovenian switches the rotations view live (Upravljaj rotacije, 3 od 4).
<!-- SECTION:NOTES:END -->
