---
id: TASK-10
title: Typing and lint
status: Done
assignee: []
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:59:00Z'
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
- [x] #1 mypy --strict passes for custom_components/shoebox
- [x] #2 ruff check and ruff format --check pass
- [x] #3 Every callable is typed
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Met for every module so far; mise run check (mypy --strict, ruff) gates each commit, so new modules stay to the same standard.
<!-- SECTION:NOTES:END -->
