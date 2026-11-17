---
id: TASK-55
title: Manifest categories
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T14:40:00Z'
updated_date: '2026-11-17T14:40:00Z'
labels:
  - release
milestone: m-6
dependencies: []
priority: medium
type: task
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
HACS validation warns when an integration's manifest has no categories (a key Home Assistant 2026.11 added). Shoebox: productivity_information.documents_photos and media_entertainment. The pinned Home Assistant (2026.10.4) does not know the key, so the hassfest task validates with the latest stable release, as CI does.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 manifest.json has the categories; HACS validation no longer warns
- [x] #2 mise run hassfest validates with the latest stable Home Assistant and passes
- [x] #3 Home Assistant 2026.10.4 still loads the integration
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
categories after name (domain and name first, then alphabetical). hassfest task: latest stable tag from git ls-remote (or HASSFEST_VERSION), a venv per version with that homeassistant release, and core's packages/hassfest installed (a separate package since 2026.11). Passes on 2026.11.2; tests and the Docker HA on 2026.10.4 load it.
<!-- SECTION:NOTES:END -->
