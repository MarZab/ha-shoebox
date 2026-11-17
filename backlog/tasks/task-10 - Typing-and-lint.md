---
id: TASK-10
title: Typing and lint
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-2
dependencies:
  - TASK-1
priority: high
type: task
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Every module passes mypy --strict and ruff. Docstrings and comments explain why, never what.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 mypy --strict passes for custom_components/shoebox
- [ ] #2 ruff check and ruff format --check pass
- [ ] #3 Every callable is typed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
