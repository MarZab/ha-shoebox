---
id: TASK-14
title: Several media folders, prefixed paths
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T11:01:00Z'
labels:
  - integration
milestone: m-2
dependencies: []
priority: high
type: feature
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Shoebox works on the media folders chosen at setup, out of those Home Assistant knows (media_dirs; "local" is My media). Every path starts with its folder's name, as Home Assistant's own media IDs do: local/Family/beach.jpg, also when only one folder is chosen, so adding a folder later never changes existing paths, patterns or automations.

- config flow: choose folders (multi-select, local by default); options can change them
- library.py (no Home Assistant imports) maps prefixed paths onto the folders and reuses media.py per folder; moving between folders works
- the panel starts at the chosen folders
- folders not chosen stay out of reach
- setup retries when a chosen folder is missing
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Setup and options choose one or more folders; local by default
- [x] #2 Every path, pattern, response and listing is prefixed with its folder; absolute paths below a chosen folder still work
- [x] #3 Actions, panel, uploads, rotations, device URL and media source work across folders; move works between folders
- [x] #4 Folders that were not chosen, and the top level itself, are refused for changes
- [x] #5 Setup retries with a translated message when a chosen folder is missing or no longer configured
- [x] #6 Docs and examples use prefixed paths; architecture.md records the choice
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
library.py maps prefixed paths onto the chosen folders and reuses media.py per folder; media.move_resolved lets moves cross folders, and MediaError paths are re-prefixed. Config flow and options choose folders from hass.config.media_dirs (local by default, at least one); options store them. Setup retries naming a folder that is missing or no longer configured. The panel starts at the media folders, without upload, new folder or item menus there. Verified in the Docker HA with a second media_dirs folder (nas): both offered and listed, rotation preview and Next span both, move nas -> local and back.
<!-- SECTION:NOTES:END -->
