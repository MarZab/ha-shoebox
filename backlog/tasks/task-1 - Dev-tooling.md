---
id: TASK-1
title: Dev tooling
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:46:00Z'
labels:
  - tooling
milestone: m-0
dependencies: []
priority: high
type: chore
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tooling for developing the integration; nothing here ships to users.

- pyproject.toml (`[tool.uv] package = false`, dev dependency group), ruff.toml, mypy strict, pytest (asyncio auto), .python-version
- mise.toml with tasks as scripts in tools/tasks/: setup, check, test, lint, format, type, clean
- Home Assistant pinned to the newest version pytest-homeassistant-custom-component supports, so tests need no compatibility shims
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `mise run setup` installs everything into .venv
- [x] #2 `mise run check` runs ruff, ruff format --check, mypy and pytest, and passes
- [x] #3 The HA version is pinned in one place
- [x] #4 Coverage is reported for custom_components/shoebox
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Home Assistant 2026.10.4 comes from pytest-homeassistant-custom-component 0.13.375, pinned in pyproject.toml; uv.lock records the rest. mypy covers custom_components/shoebox.
<!-- SECTION:NOTES:END -->
