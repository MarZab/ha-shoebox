---
id: TASK-1
title: Dev tooling
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
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
- [ ] #1 `mise run setup` installs everything into .venv
- [ ] #2 `mise run check` runs ruff, ruff format --check, mypy and pytest, and passes
- [ ] #3 The HA version is pinned in one place
- [ ] #4 Coverage is reported for custom_components/shoebox
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
