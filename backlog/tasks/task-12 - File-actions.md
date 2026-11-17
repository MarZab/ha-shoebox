---
id: TASK-12
title: File actions
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T13:10:00Z'
labels:
  - integration
milestone: m-2
dependencies:
  - TASK-11
priority: high
type: task
ordinal: 12000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Admin-only domain actions for files: list, create_folder, move, rename, delete, rotate, crop. They act on files, so they are domain actions; rotations have no actions.

- services.yaml holds the schema; names and descriptions of every action and field in translations/en.json
- icons.json for every action
- ServiceValidationError and HomeAssistantError with translation_domain and translation_key; errors of the HA-free modules are mapped in one place (Shoebox.run)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Registered actions are exactly these seven
- [x] #2 Every action and field has a translated name and description
- [x] #3 icons.json covers every action
- [x] #4 Raised exceptions carry translation keys
- [x] #5 Each action tested: happy path and one refusal, response shapes asserted; admin-only through async_register_admin_service, with a non-admin refusal tested
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Errors of the HA-free modules carry a key and placeholders (errors.py MESSAGES); Shoebox.run turns them into ServiceValidationError with translation keys, OSError into HomeAssistantError(file_error). en.json exceptions are generated from MESSAGES and a test keeps them equal; another keeps services.yaml, icons.json, translations and SERVICES in step. hassfest rejects placeholders in single quotes and '-90' as an option key: messages use double quotes, and the rotate selector offers 90, 180 and 270 (labelled 90 degrees counterclockwise). Fixed: crop_shown accepted an inverted box by sorting its corners; it now refuses it. Verified in the Docker HA: list returns the sample pictures; a '..' path is refused with the translated message.
<!-- SECTION:NOTES:END -->
