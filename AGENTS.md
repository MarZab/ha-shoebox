# Agent instructions

## What this project is

**Shoebox**, a Home Assistant custom integration distributed through HACS. It is a media organizer first: it fills the gaps of Home Assistant's media browser for the chosen media folders (My media and any `media_dirs`) with folders, move, rename, safe uploads, thumbnails, and rotate and crop. Extras build on it: rotations (pictures that change, each a device with an image and a Next button), a sized picture URL for devices such as ESPHome, and a media source.

The shipped product is `custom_components/shoebox/`. Everything else is developer tooling.

## Read first

| Doc | For |
|-----|-----|
| [docs/architecture.md](docs/architecture.md) | Modules, data flow, storage, and the reasons behind the design. Read before changing behaviour. |
| [docs/development.md](docs/development.md) | Setup, tasks, the Docker Home Assistant, checking the panel |
| [docs/testing.md](docs/testing.md) | Test layout and fixtures |
| [docs/security.md](docs/security.md) | Path confinement, who may do what |
| [docs/release.md](docs/release.md) | Versions and releases |
| [docs/README.md](docs/README.md) | User documentation index |

## Commands

```bash
mise run setup        # dev dependencies
mise run check        # lint, types, tests: what CI runs
mise run test         # pytest (extra args after --)
mise run format       # ruff fix + format
mise run hassfest     # Home Assistant's manifest, translation and service checks
mise run dev:up       # Home Assistant in Docker at http://localhost:8123
mise run dev:restart  # pick up integration edits
mise run dev:token    # access token for scripted checks (onboards as dev/dev)
mise run dev:panel    # the panel in a headless browser, with screenshots
mise run release      # the version; see docs/release.md
```

## Home Assistant conventions

Follow what core integrations do. When unsure, look at a current core integration of the same shape, the [developer docs](https://developers.home-assistant.io) and the [integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/); keep `quality_scale.yaml` current.

- **Manifest**: `domain` and `name` first, then keys alphabetical. Keep `requirements` minimal; Pillow comes with Home Assistant.
- **Config entries**: typed `ShoeboxConfigEntry`, state on `entry.runtime_data`. `async_setup_entry` and `async_unload_entry` return a bool: Home Assistant 2026.10 requires it. Find the loaded entry with `hass.config_entries.async_loaded_entries`. One update listener reloads the entry on option and subentry changes.
- **No YAML**: `cv.config_entry_only_config_schema`.
- **Actions**: registered in `async_setup`, admin-only. Schema in `services.yaml`, names and descriptions in the translations, icons in `icons.json`.
- **Errors**: the modules without Home Assistant raise `errors.ShoeboxError` subclasses with a key from `errors.MESSAGES`; `Shoebox.run` turns them into `ServiceValidationError` with that translation key. Every key is in `translations/en.json` and `sl.json`.
- **Entities**: `has_entity_name`, a device per rotation (`DeviceEntryType.SERVICE`), unique ids from the subentry id, translation keys.
- **I/O**: nothing blocking in the event loop; file and picture work runs in the executor through `Shoebox.run`.
- **HTTP views**: `requires_auth = True`; admin-only views use `require_admin`. Picture URLs for `<img>` are signed with `async_sign_path`.
- **Frontend**: `panel_custom` and static paths; Home Assistant's `ha-*` elements and theme variables; every visible text through `frontend/i18n.js` in English and Slovenian.
- **Logging**: `_LOGGER = logging.getLogger(__name__)`, no f-strings in log calls; INFO only for user actions such as uploads.

## Python

- Python 3.14. Modern syntax (`type X = …`, `X | None`, `@override`).
- Every signature typed; `mypy --strict` passes. A `# type: ignore[code]` needs the code and a reason.
- `ruff format` is canonical; `ruff check` is clean.
- Docstrings only where they add something the name doesn't. Comments explain *why*.
- One concept per module.

## Tests

Testing policy:

- Test behaviour at public boundaries (actions, views, WebSocket commands, entities, flows, and the exported functions of the modules without Home Assistant), not internals.
- No tests for: trivial getters/setters, type-only code, constants, simple pass-through wrappers, framework behaviour (what Home Assistant itself guarantees).
- Prefer one table-driven test (`pytest.mark.parametrize`) over N near-identical tests.
- Max ~3-5 new test cases per feature unless the human asks for more. Happy path + the edge cases that actually bite.
- Extend existing test files; don't create new ones per function.
- Don't mock what you own. Mock only external I/O (network, clock); files are real, on `tmp_path`.
- Never add tests just to raise coverage.
- If unsure whether a test is worth it, leave it out and mention it in the summary.

Also: no network and no sleeping; a bug fix starts with a failing test. The panel has no unit tests: `mise run dev:panel` and the checklist in docs/development.md.

## Backlog

Work is tracked with the `backlog` CLI in `backlog/`; edit tasks through the CLI.

```bash
backlog task list --plain
backlog task <id> --plain
backlog task edit <id> -s "In Progress" -a @agent
backlog task edit <id> --check-ac 1 --notes "…"
backlog task edit <id> -s Done
backlog task create "Title" -d "…" --ac "…" -l <label> -m <milestone>
```

- One task at a time; one commit per task.
- Done means every acceptance criterion checked and `mise run check` passing.
- Something new turns up: create a task instead of widening the current one.
- A design choice goes in docs/architecture.md with its reason. A change users can see updates README.md or docs/ in the same task.

## Hard rules

1. **Everything stays in the chosen media folders.** Outside paths start with a folder's name (`local/…`) and go through `Library`, which uses `media.resolve` per folder.
2. **Never overwrite a user file by accident.** Uploads claim a free name; edits replace atomically.
3. **The cache deletes only its own files.**
4. **Admin-only stays admin-only**: actions, panel, WebSocket commands, render and upload views. The device and media source views serve only rotation pictures.
5. **Modules without Home Assistant stay without it.**
6. **Version**: `manifest.json` is the single source; release tags `vX.Y.Z` match it.

## Ask the human before

- Adding a runtime requirement to `manifest.json`.
- Changing an action's name, fields or response, the storage format, the cache key, or a URL devices use.
- Removing a feature or an option.
