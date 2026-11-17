---
id: TASK-11
title: Setup, config flow and options
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-2
dependencies:
  - TASK-10
priority: high
type: task
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
- configured in the UI only: cv.config_entry_only_config_schema, no import step
- async_setup_entry and async_unload_entry return None and raise on failure
- unload saves rotation state and removes the panel; reload works
- config flow: single instance, one translated step
- options flow: cache size, clear cache with current usage shown, and Show in sidebar (on by default; off means no panel for anyone while actions, entities and the device URL keep working). Nothing else: the extras are opt-in by use, not by switches
- the loaded entry is found with hass.config_entries.async_loaded_entries
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Setup, unload and reload tested
- [ ] #2 Config flow: creates the entry; aborts when already configured
- [ ] #3 Options: saves the size, clears the cache when asked, evicts on change
- [ ] #4 A shoebox: key in configuration.yaml raises HA's repair issue
- [ ] #5 Show in sidebar defaults on; switching it removes or adds the panel without a restart
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
