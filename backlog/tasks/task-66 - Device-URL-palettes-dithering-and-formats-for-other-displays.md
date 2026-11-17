---
id: TASK-66
title: 'Device URL: palettes, dithering and formats for other displays'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T18:14:00Z'
updated_date: '2026-11-17T18:17:00Z'
labels:
  - integration
milestone: m-6
dependencies: []
priority: medium
type: feature
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
E-paper and small displays need fewer colours, dithering and other formats. Optional device URL parameters, Pillow only: colors (bw, gray4, gray16, spectra6, acep7, or hex colours for calibration), dither (floyd, none), format (jpeg, png, bmp; png by default with colors), contrast, saturation, brightness. Without them the URL is unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 colors reduces to the palette (named or hex list, 2 to 256), with Floyd-Steinberg dithering or none
- [x] #2 format png, bmp or jpeg with the right Content-Type; png by default with colors
- [x] #3 contrast, saturation and brightness (0 to 3) adjust before the palette
- [x] #4 Each combination is cached and has its own ETag; the URL without parameters is unchanged
- [x] #5 docs/displays.md: the parameters and an ESPHome e-paper example
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
imaging.Look (frozen) with parse_look: colors (named palettes or 2-256 hex), dither floyd/none, format jpeg/png/bmp (png default with colors), contrast/saturation/brightness 0-3 via ImageEnhance. Pillow quantize with a fixed palette; PNG with 1/2/4/8 bits by palette size; BMP 24-bit. Look.key joins the cache key (empty for the plain look, so existing keys stay). Device view parses it (400 on bad values) and answers with its MIME type. Tests: looks table (formats, palettes, saturation 0), refusals, cache key, device URL (PNG, ETag per look, 304). Dev HA: plain, bw png, gray4 bmp, spectra6 png, bad 400. ESPHome PNG BINARY snippet passes esphome config 2026.10.2. docs/displays.md with docs/images/display-looks.png.
<!-- SECTION:NOTES:END -->
