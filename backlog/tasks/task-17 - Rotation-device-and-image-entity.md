---
id: TASK-17
title: Rotation device and image entity
status: To Do
assignee: []
created_date: '2026-11-17T09:40:00Z'
labels:
  - integration
milestone: m-3
dependencies:
  - TASK-16
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
One device per rotation subentry (DeviceEntryType.SERVICE, named after the subentry title) with an image entity: has_entity_name, name None, unique_id = subentry id, added with config_subentry_id.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Device and entity created per subentry; renaming the subentry renames the device and keeps the entity id
- [ ] #2 Deleting the subentry removes device and entity
- [ ] #3 The image is the current picture fitted inside the entity size; attributes describe the rotation
- [ ] #4 image_last_updated changes when the rotation advances and when its current file is edited
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
