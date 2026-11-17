---
id: TASK-65
title: Edit iPhone MPO pictures
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T17:28:00Z'
updated_date: '2026-11-17T17:31:00Z'
labels:
  - integration
milestone: m-4
dependencies: []
priority: high
type: bug
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
iPhone photos are often MPO: a JPEG with further images (HDR gain map, depth) appended, located by offsets in an APP2 MPF segment, relative to its own header. Pillow reports them as MPO, so Shoebox refused to edit them and skipped reduced decoding. Treat MPO as JPEG; when an edit changes the length of metadata segments after the MPF header, move the MPF offsets with them.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 MPO pictures can be turned and cropped; info reports them editable
- [x] #2 After turning and cropping, the appended images still read correctly, also when XMP comes after the MPF segment
- [x] #3 Thumbnails of MPO pictures use reduced decoding like JPEG
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
MPO is edited as JPEG (JPEG_FORMATS): info editable, reduced decoding and the pixel check. _jpeg_join takes the segments as they were; when the bytes after the APP2 MPF segment change length, the MP entry offsets of the further images (relative to the MPF header) move by the same amount. Test: Pillow MPOs with XMP after the MPF segment and without XMP, turned and cropped; the second frame still reads (fails without the correction: 'not a JPEG file'). The user's IMG_4546.jpeg (iPhone, HDR gain map 2856x2142): turned and cropped, image data byte for byte, gain map decodes; Edit enabled in the dev HA panel.
<!-- SECTION:NOTES:END -->
