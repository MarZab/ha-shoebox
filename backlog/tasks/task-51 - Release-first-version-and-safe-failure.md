---
id: TASK-51
title: 'Release: first version and safe failure'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T12:40:00Z'
updated_date: '2026-11-17T13:05:00Z'
labels:
  - release
  - tooling
milestone: m-6
dependencies: []
priority: high
type: task
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The manifest is 0.1.0 with no tag, so the release task cannot release 0.1.0. It also tags before pushing, so a missing remote leaves a tag that blocks a retry. Decide the first version, make the task check the remote first (or push before tagging), and turn CHANGELOG "Unreleased" into the version section.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The first release can be made with mise run release
- [x] #2 A missing or failing remote leaves no commit or tag behind
- [x] #3 CHANGELOG has the first version's section
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
next_version accepts the current version while it has no tag (first release, hand-set versions). check_tree refuses an origin it cannot reach (ls-remote). publish() commits only if the version changes, tags, pushes branch and tag with --atomic, and on failure deletes the tag and resets to the previous HEAD; tested with a missing remote. The changelog check matches the whole heading line (0.2.0 no longer matches 0.2.0b1). CHANGELOG has ## 0.1.0 with media source, diagnostics and translations. docs/release.md and TASK-31 describe the first release.
<!-- SECTION:NOTES:END -->
