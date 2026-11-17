---
id: TASK-27
title: README
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T15:16:00Z'
labels:
  - docs
milestone: m-5
dependencies:
  - TASK-12
  - TASK-16
  - TASK-18
  - TASK-19
priority: high
type: docs
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The entry point users and HACS see. Short and task-oriented, in the words people search for; details live in docs/.

- first line: "Shoebox: media manager and picture organizer for Home Assistant. Organize, upload, rotate and crop the photos in your media folder, and show them as rotating pictures on dashboards, notifications and displays.", then a panel screenshot
- use cases, one or two lines each, linking to docs/use-cases.md:
  - organise the photos in My media from your phone: folders, rename, move, delete
  - upload from the phone straight into the right folder, never overwriting
  - fix sideways photos and crop them without losing quality
  - a slideshow on a dashboard (tablet, TV or browser)
  - a digital photo frame on an ESPHome e-ink or LCD display
  - different pictures by time of day or season, switched by automations
  - a photo of the day in a notification
  - a kids' artwork wall fed from the phone
- install through HACS (search "Shoebox", "media manager" or "photo") and add the integration
- quick starts: a picture entity card with Next pressed by a timed automation; an ESPHome display
- actions and entities in one table, linking to docs/
- limits: JPEG-only edits, the chosen media folders, admin-only panel
- a closing keywords line: media manager, picture organizer, photo organizer, photo frame, slideshow, file manager
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Install and both quick starts work as written on a clean Docker HA
- [x] #2 Every use case links to a working recipe
- [x] #3 Every action and entity links to its reference
- [x] #4 Renders correctly in HACS
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Clean HA 2026.10.4 on :8124 with custom_components/shoebox from GitHub main (what HACS installs before a release): added the integration with My media, the quick start's rotation (preview 6 pictures), Next, image entity and picture card source, the device URL with the entity's token at 640x800, and the panel. The ESPHome start was checked with esphome config only, not on hardware. HACS: its markdown rewriting (hacs/frontend src/tools/markdown.ts) turns Markdown links into GitHub URLs but leaves HTML alone, so the README's two thumbnails use absolute raw.githubusercontent.com URLs; rendered with HACS's rewriting and ha-markdown in the dev HA: both pictures load at 49%, links go to github.com blob pages.
<!-- SECTION:NOTES:END -->
