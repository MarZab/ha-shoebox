---
id: TASK-12
title: File actions
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 Registered actions are exactly these seven
- [ ] #2 Every action and field has a translated name and description
- [ ] #3 icons.json covers every action
- [ ] #4 Raised exceptions carry translation keys
- [ ] #5 Each action tested: happy path, one refusal, and a non-admin call refused; response shapes asserted
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
