---
id: TASK-38
title: 'Panel: settings menu instead of the rotations view'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:01:00Z'
updated_date: '2026-11-17T12:03:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: task
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the panel's rotations view. A menu (⋮) in the panel's top bar links to the integration's page in Settings, where rotations are added, changed and deleted, and the options live. The shoebox/rotations WebSocket command goes with the view.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The rotations view, its toggle and the shoebox/rotations command are gone
- [x] #2 A ⋮ menu in the top bar opens the integration's page in Settings
- [x] #3 Docs describe the menu
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The rotations view, its toggle, the shoebox/rotations command, its texts and styles are gone. A ⋮ menu in the top bar (ha-dropdown) has Rotations and settings, which opens /config/integrations/integration/shoebox. The panel only knows folders now. tools/scripts/panel_check.js screenshots the folder view only. Checked in the Docker HA: the menu opens the integration page; panel check passes in light, dark and phone.
<!-- SECTION:NOTES:END -->
