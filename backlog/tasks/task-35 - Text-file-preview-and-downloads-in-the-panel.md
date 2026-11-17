---
id: TASK-35
title: Text file preview and downloads in the panel
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T11:36:00Z'
updated_date: '2026-11-17T11:44:00Z'
labels:
  - panel
  - integration
milestone: m-4
dependencies: []
priority: medium
type: feature
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Open text files read-only in the panel: plain text, logs and configs in a monospace box, Markdown formatted with Home Assistant's markdown element when it is available. Files over 256 KB show their start with a note. Binary files are refused with a message.

- WebSocket command shoebox/text (admin only) through the library, like every path
- the panel opens other files (not pictures, video or audio) in a text viewer
- English and Slovenian
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Text files open read-only in the panel; Markdown is formatted
- [x] #2 Files over 256 KB show their start and say that the rest is not shown
- [x] #3 Binary files and paths outside the chosen folders are refused with a message
- [x] #4 docs/panel.md describes it
- [x] #5 Any file can be downloaded from the panel, as the original file, by administrators
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 `mise run check` passes
- [x] #2 New or changed behaviour is covered by tests
- [x] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
One admin-only download view (/api/shoebox/download?path=) serves original files with web.FileResponse (streamed, Range support). The panel saves files through a URL signed with auth/sign_path, and reads the start of text files with hass.fetchWithAuth and a Range request (256 KB), as Home Assistant's frontend reads files; it decodes in the browser, refuses NUL bytes or invalid UTF-8 as not text, and drops a character cut at the end of the range. Home Assistant's own media view serves only pictures, video and audio, so it could not be reused. Checked in the Docker HA: Markdown formatted by ha-markdown, a 334 kB log shows its first 256 kB with a note, binary refused, empty file empty, download returns the original file.
<!-- SECTION:NOTES:END -->
