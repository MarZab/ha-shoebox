---
id: TASK-44
title: 'Panel: search in the current folder and its subfolders'
status: To Do
assignee: []
created_date: '2026-11-17T12:36:00Z'
updated_date: '2026-11-17T12:40:00Z'
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
- [ ] #1 Search in the ⋮ menu opens and closes a search field, like Home Assistant's media browser
- [ ] #2 Results come from the current folder and all subfolders: case-insensitive name match, hidden names skipped, folders and files, at most 100
- [ ] #3 Results show their folder and open, download and edit like other items; closing the search shows the folder again
- [ ] #4 Navigating to another folder clears the search
- [ ] #5 Texts in English and Slovenian; docs/panel.md describes it; the server search is tested
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->
