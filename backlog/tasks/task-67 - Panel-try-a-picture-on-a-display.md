---
id: TASK-67
title: 'Panel: try a picture on a display'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T18:19:00Z'
updated_date: '2026-11-17T18:27:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: feature
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A demo page from a picture's ⋮ menu with knobs for every device URL option (size, fit, palette or own colours, dithering, format, contrast, saturation, brightness, presets for common displays), a live preview with file type and size, and the parameters to copy onto a rotation's device URL. The render view (admin, signed) accepts the same options.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Try on a display is in the ⋮ menu of pictures (tiles and viewer) and opens the page
- [x] #2 Every option has a knob; presets for common displays fill them; the preview follows within a moment, latest change wins
- [x] #3 The page shows the file type and size and the device URL parameters, with a copy button
- [x] #4 The render view accepts the display options, refusing bad values with 400
- [x] #5 English and Slovenian; docs/panel.md and docs/displays.md describe it
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
frontend/display.js: an ha-form (presets for 3 LCDs and 5 e-paper panels, width/height, fit, colours incl. own hex, dithering, format, contrast/saturation/brightness sliders), preview through a signed render URL fetched as a blob (type and size shown), 300 ms debounce with a sequence so the latest change wins; a knob changed by hand turns the preset into Own settings; the device URL parameters (defaults left out, commas readable) with copy (clipboard, else selects the text). Opened from the ⋮ menu of picture tiles and the viewer. The render view takes the look options and cache=0, which prepares without storing (VariantCache.get(store=False), Shoebox.picture(store=...)): asked for by the user so trials do not fill the cache; tested at the cache and the view. Dev HA: presets, hand changes, own colours, a bad colour shows the server's message; the cache size is unchanged after the trials.

Renamed to Preview at the user's request (Predogled in Slovenian; title 'Preview of <name>'), and the screen icon also sits next to Edit in the viewer's header; the menu entries stay.
<!-- SECTION:NOTES:END -->
