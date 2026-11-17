---
id: TASK-44
title: 'Panel: search in the current folder and its subfolders'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:36:00Z'
updated_date: '2026-11-17T14:05:00Z'
labels:
  - panel
milestone: m-4
dependencies: []
priority: medium
type: feature
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A Search item in the top bar's ⋮ menu toggles a search field, like Home Assistant's media browser. As there (local_source._search_media), the search covers the current folder and every folder below it: names containing the text, case-insensitive, hidden names skipped, folders and files, at most 100 results. At the top level it searches every chosen media folder. Results show where they are and open like any item. Searching runs on the server, in the executor, through the library.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Search in the ⋮ menu opens and closes a search field, like Home Assistant's media browser
- [x] #2 Results come from the current folder and all subfolders: case-insensitive name match, hidden names skipped, folders and files, at most 100
- [x] #3 Results show their folder and open, download and edit like other items; closing the search shows the folder again
- [x] #4 Navigating to another folder clears the search
- [x] #5 Texts in English and Slovenian; docs/panel.md describes it; the server search is tested
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Search in the ⋮ menu toggles a search bar under the top bar (highlighted while open), labelled 'Search <folder>' as in HA. shoebox/search (admin) walks lazily from the current folder, case-insensitive name match, hidden and non-UTF-8 names and links skipped as in walk, at most 100 and whether there were more; '' searches every media folder. Results show their folder, open/download/rename/move/delete like other items; actions re-run the search. Navigating clears it; clearing the field shows the folder. Tested at the WebSocket boundary (below a folder, every folder, limit).
<!-- SECTION:NOTES:END -->
