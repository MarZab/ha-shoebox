---
id: TASK-4
title: Repository metadata
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T09:50:00Z'
labels:
  - docs
  - release
milestone: m-0
dependencies: []
priority: medium
type: docs
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
hacs.json, CHANGELOG.md, and the GitHub repository ha-shoebox. Display names carry the words people search for: "Shoebox Media Manager" in manifest.json and hacs.json, "Shoebox" for the entry, sidebar and panel.

Description: "Shoebox: media manager and picture organizer for Home Assistant. Organize, upload, rotate and crop the photos in your media folder, and show them as rotating pictures on dashboards, notifications and displays."

Topics: home-assistant, homeassistant, hacs, hacs-integration, home-assistant-integration, home-assistant-custom-component, media-manager, picture-organizer, photo-organizer, photo-manager, file-manager, media-browser, photos, slideshow, photo-frame, digital-photo-frame, picture-frame, esphome, e-ink, image-resize
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 hacs.json is valid for hacs/action, named Shoebox Media Manager, with the minimum HA version
- [x] #2 CHANGELOG.md exists
- [ ] #3 The GitHub repository has the description and the 20 topics
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
hacs.json and CHANGELOG.md added. Open: create the GitHub repository ha-shoebox and set its description and topics (needs the owner's go-ahead).
<!-- SECTION:NOTES:END -->
