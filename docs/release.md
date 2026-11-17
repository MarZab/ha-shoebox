# Release

Shoebox is released through HACS: a release is a Git tag and a GitHub release.

## Versions

- The version is in `custom_components/shoebox/manifest.json` and nowhere else.
- [Semantic versioning](https://semver.org/). Pre-releases use Home Assistant's style: `1.3.0b1` for betas, `1.3.0rc1` for release candidates.
- Order: `1.2.0 < 1.3.0b1 < 1.3.0b2 < 1.3.0rc1 < 1.3.0`.

## Releasing

1. Add a `## X.Y.Z` section to `CHANGELOG.md` and commit it.

   The first release is the version already in `manifest.json` (0.1.0): `mise run release -- 0.1.0` tags it without a version commit. A version without a tag can always be released as it is.
2. Release:

   ```bash
   mise run release                     # the current version
   mise run release -- minor --dry-run  # the plan, without changing anything
   mise run release -- minor            # bump, commit, tag, push
   ```

   The argument is `patch`, `minor`, `major`, `beta`, `rc`, `final`, or a version such as `1.4.0`. From a stable version, `beta` and `rc` start the next minor version.

   The task shows its plan, warns when the changelog has no section for the version, refuses a dirty working tree, an existing tag, an older version or an `origin` it cannot reach, and asks before changing anything (`--yes` skips the question). It commits `Release vX.Y.Z`, creates the annotated tag `vX.Y.Z` and pushes the branch and the tag in one atomic push. If the push fails, the commit and the tag are undone, so the release can simply be run again.

3. GitHub Actions does the rest:
   - `release.yaml` checks that the tag matches `manifest.json` and creates the GitHub release: a full release for `vX.Y.Z`, a pre-release for `a`, `b` and `rc` tags.
   - `validate.yaml` runs hassfest and HACS validation on every push and nightly.

HACS offers pre-releases only to users who enable beta versions for the repository. A bad release is fixed with the next version; tags are never moved or deleted.

## HACS default catalog

To be listed in HACS without adding a custom repository, the repository needs: passing hassfest and HACS validation, a full GitHub release, the MIT license, the brand icon (`custom_components/shoebox/brand/`), a description, topics and issues enabled. Then a pull request to [hacs/default](https://github.com/hacs/default).
