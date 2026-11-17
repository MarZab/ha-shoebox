---
id: TASK-11
title: Setup, config flow and options
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T13:10:00Z'
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
- async_setup_entry and async_unload_entry return a bool (required by Home Assistant 2026.10)
- unload saves rotation state and removes the panel; reload works
- config flow: single instance, one translated step
- options flow: cache size, clear cache with current usage shown, and Show in sidebar (on by default; off means no panel for anyone while actions, entities and the device URL keep working). Later the media folders were added to the options too. The extras stay opt-in by use, not by switches
- the loaded entry is found with hass.config_entries.async_loaded_entries
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Setup, unload and reload tested
- [x] #2 Config flow: creates the entry; aborts when already configured
- [x] #3 Options: saves the size, clears the cache when asked, evicts on change
- [x] #4 A shoebox: key in configuration.yaml raises HA's repair issue
- [x] #5 Shoebox Media Manager can be added in the Docker HA
- [x] #6 Options store Show in sidebar, on by default
- [x] #7 Cache size 0 turns the cache off: nothing is stored and pictures are prepared on every request
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Home Assistant 2026.10 requires async_setup_entry and async_unload_entry to return a bool; later versions still accept it from custom integrations, so both return True. Options use OptionsFlowWithReload: setup evicts to the configured size, so a smaller size applies at once. VariantCache.get returns the picture bytes (with a key for ETags), so callers work the same whether the cache is on or off (size 0). Verified in the Docker HA: Shoebox added through the config flow API and loaded. tools/scripts/dev_token.py (mise run dev:token) onboards the dev HA as dev/dev and prints an access token.
<!-- SECTION:NOTES:END -->
