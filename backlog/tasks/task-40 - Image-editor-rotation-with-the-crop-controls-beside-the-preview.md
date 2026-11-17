---
id: TASK-40
title: 'Image editor: rotation with the crop, controls beside the preview'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:13:00Z'
updated_date: '2026-11-17T12:15:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: task
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The image editor holds the turn and the crop together: rotate left/right turn the picture in the editor only, and Save writes the turn and the crop in one edit; Cancel discards both. Layout: the controls (rotate, aspect ratio, wrapping) take half the width with the preview to their right; the picture to crop is below.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Rotate left/right are in the editor; nothing is written until Save; Cancel discards the turn and the crop
- [x] #2 A crop box turns with the picture
- [x] #3 Controls take half the width, wrapping, with the preview to their right
- [x] #4 docs/panel.md and the editor screenshot match
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
shoebox-crop turns the picture in the browser (canvas, rotate(±90)), turns an existing crop box with it, and reports the turn; the panel saves rotate and crop in one shoebox/edit call, which already turns first and then crops as shown. Rotate left/right left the viewer's top bar (now Edit). Reset only clears the box in the editor. Original aspect is handled in the component, so it keeps the picture's shape after a turn. Layout: a controls slot (rotate, aspect ratio, wrapping) in the left half, preview on the right, picture below. Checked in the Docker HA: Cancel after turning and cropping left the file unchanged; Save wrote orientation 6 and a 16:9 crop of the turned picture.
<!-- SECTION:NOTES:END -->
