---
id: TASK-32
title: HACS default catalog
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-17T09:40:00Z'
updated_date: '2026-11-17T17:49:00Z'
labels:
  - release
milestone: m-6
dependencies:
  - TASK-31
priority: low
type: task
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Submit Shoebox to the HACS default catalog.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Every hacs/default inclusion check passes
- [ ] #2 Submission pull request opened
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Prepared on 2026-11-17 against hacs/default master: the inclusion checks (brands, core domain conflict, manifest, hacs-validation, hacs.json name, archived, releases, owner, OSI license, repository description/issues/topics, lint jq and sorted) all hold for MarZab/ha-shoebox at v0.2.1. Entry "MarZab/ha-shoebox" goes into the integration file after "Martreides/ha-grimmory" (sorted by str.casefold); a local copy with it passes is_sorted and JSON parsing. Links for the PR template: release https://github.com/MarZab/ha-shoebox/releases/tag/v0.2.1, HACS action https://github.com/MarZab/ha-shoebox/actions/runs/44139536716/job/134238215958, hassfest https://github.com/MarZab/ha-shoebox/actions/runs/44139536716/job/134238216624. The PR is opened by the owner (AC 2).
<!-- SECTION:NOTES:END -->
