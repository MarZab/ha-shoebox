---
id: TASK-17
title: Rotation device and image entity
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T10:23:00Z'
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
- [x] #1 Device and entity created per subentry; renaming the subentry renames the device and keeps the entity id
- [x] #2 Deleting the subentry removes device and entity
- [x] #3 The image is the current picture fitted inside the entity size; attributes describe the rotation
- [x] #4 image_last_updated changes when the rotation advances and when its current file is edited
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
entity.py: RotationEntity (device per rotation subentry, dispatcher updates); image.py: RotationImage (name None, unique_id = subentry id, translation_key for the icon). Edits made through rotate, crop and the panel editor call Rotations.async_file_changed, so a rotation showing that file updates image_last_updated and dashboards fetch the new picture. Device lookups in tests use async_get_device_by_identifier (async_get_device is deprecated). Verified in the Docker HA: a rotation added through the subentry flow API creates image.living_room.
<!-- SECTION:NOTES:END -->
