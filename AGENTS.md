# Agent instructions

## What this project is

**Shoebox**, a Home Assistant custom integration distributed through HACS. It is a media organiser first: it fills the gaps of HA's media browser for the local media folder (`/media`, "My media") with folders, move, rename, safe uploads, thumbnails, and rotate and crop. Small extras build on it: rotations, a sized image URL for devices, and a media source. Extras are opt-in by use; nothing runs until a rotation is added.

- **Rotations**: config subentries of the one Shoebox entry, added and changed in Settings. Each has a name plus glob/regex patterns over paths below `/media`, and steps to the next image in path order. Each rotation has its own device with an `image` entity and a "Next" `button` entity.
- **Actions**: admin-only file actions: list media, and create, move, rename, delete, rotate and crop files. Rotations advance with `button.press`.
- **Consumers**: HA's own (picture cards, notifications, the media browser), plus devices such as ESPHome displays. Devices fetch `/api/shoebox/image/<entity_id>?width=&height=&fit=` with a long-lived token. Sized for hundreds of items, not a photo library.
- **Edits are metadata**: rotation is the EXIF Orientation tag and crop is the Adobe XMP crop (`crs:CropLeft/…`). JPEG pixel data is never re-encoded.
- **Variant cache** under `/config/.cache/shoebox`, size-limited with LRU eviction. The options flow holds only the cache size, clearing the cache, and Show in sidebar (on by default).
- **Sidebar panel** (admin only) for browsing, uploading and editing files, and an overview of rotations that links to Settings.

Design choices and their reasons are in `docs/architecture.md`. Read it before changing behaviour.

The shipped product is `custom_components/shoebox/`. Everything else in the repo is developer tooling.

## Layout

| Path | Role |
|------|------|
| `custom_components/shoebox/` | The integration. **This is what HACS installs.** |
| `custom_components/shoebox/frontend/` | Panel: plain ES modules, no build step |
| `tests/` | pytest suite |
| `tools/tasks/` | mise task scripts (`mise tasks` lists them) |
| `docker/` | Local Home Assistant for manual testing |
| `README.md` | User entry point: install and quick starts |
| `docs/` | User reference (`docs/README.md` is the index) and developer docs (`development.md`, `architecture.md`, `security.md`, `testing.md`, `release.md`) |
| `backlog/` | Tasks and milestones ([Backlog.md](https://github.com/MrLesk/Backlog.md)) |

### Inside the integration

| Module | Holds | Imports HA |
|--------|-------|------------|
| `media.py` | Path confinement, listing, patterns, rotation order, file operations | no |
| `imaging.py` | EXIF orientation, XMP crop, rendering | no |
| `cache.py` | Variant cache on disk | no |
| `upload.py` | Upload naming and placement | no |
| `manager.py` | Runtime object: rotations store, cache, executor bridge | yes |
| `__init__.py` | Setup, services, variant view | yes |
| `config_flow.py` | Config and options flow | yes |
| `image.py` | Image platform: one entity per rotation | yes |
| `panel.py` | Panel registration, WebSocket commands, render and upload views | yes |

The modules marked "no" stay free of `homeassistant` imports so they can be unit-tested directly and fast.

## Commands

```bash
mise install          # Python + uv at the pinned versions
mise run setup        # uv sync
mise run check        # lint + types + tests (what CI runs)
mise run test         # pytest (extra args after --)
mise run format       # ruff fix + format
mise run dev:up       # Home Assistant in Docker at http://localhost:8123
mise run dev:restart  # pick up integration edits
mise run dev:logs     # tail HA logs
```

Without mise: `uv run pytest`, `uv run ruff check .`, `uv run mypy`.

## Home Assistant conventions

Follow what core integrations do. When unsure, look at a current core integration of the same shape and at the developer docs (developers.home-assistant.io), including the [integration quality scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) rules.

- **Manifest**: `domain` and `name` first, then keys alphabetical. `version` is required for custom integrations. Set `documentation` and `issue_tracker`. Keep `requirements` minimal; Pillow comes with HA.
- **Config entries**: typed `ConfigEntry[Shoebox]` alias, state on `entry.runtime_data`, never `hass.data` for entry state. `single_config_entry: true`. `async_setup_entry` and `async_unload_entry` return `None` and raise on failure (`async_unload_platforms_or_raise`). Find the loaded entry with `hass.config_entries.async_loaded_entries`.
- **No YAML**: configured in the UI only, with `cv.config_entry_only_config_schema`.
- **Services**: register in `async_setup`, not per entry. Describe them in `services.yaml`, with names and descriptions in `translations/en.json` and icons in `icons.json`. Admin actions use `async_register_admin_service`.
- **Errors**: raise `ServiceValidationError` for bad input and `HomeAssistantError` for failures, both with `translation_domain` + `translation_key`. The HA-free modules raise their own exceptions, which the manager translates at the boundary.
- **Entities**: `_attr_has_entity_name = True`, stable `unique_id`, a device for the service (`DeviceEntryType.SERVICE`), translated names.
- **I/O**: no blocking calls in the event loop. File and image work runs in the executor (`hass.async_add_executor_job`).
- **Validation**: use HA's schema helpers (`homeassistant.helpers.config_validation as cv`) and selectors, as core does for the current HA version.
- **HTTP views**: `requires_auth = True`; admin-only views use `homeassistant.components.http.require_admin`. URLs for `<img>` and devices are signed with `async_sign_path`. Don't import private constants from other integrations.
- **Frontend**: register with `panel_custom` and serve via `async_register_static_paths`. Use HA's theme variables and `ha-*` elements; no private HA APIs beyond what custom panels commonly rely on. Every visible string goes through the panel's translations.
- **Logging**: `_LOGGER = logging.getLogger(__name__)`. No f-strings in log calls. Never log at INFO in normal flow except for user-visible actions such as an upload.

## Python

- Python 3.14 and the HA version pinned in `pyproject.toml`. Modern syntax (`type X = …`, `X | None`, `@override`).
- Every signature is typed. `mypy --strict` must pass. A `# type: ignore[code]` needs the code and a short reason.
- `ruff format` is canonical; `ruff check` must be clean.
- Docstrings only where they add something the name doesn't. Comments explain *why*, never *what*.
- `from __future__ import annotations` in every module.
- Keep modules to one concept. Split before a file passes ~400 lines.

## Tests

- **Functions first**: the HA-free modules get direct, fast unit tests on `tmp_path` with small generated images. This is where most coverage comes from.
- **HA side** via `pytest-homeassistant-custom-component`: setup/unload, config and options flow, each service (happy path + refusal), image entity lifecycle, WebSocket commands, HTTP views.
- **Panel JS**: no unit tests. Check it manually in the Docker HA.
- Keep tests small and short: one behaviour per test, named after the behaviour. Parametrize instead of copying. Shared fixtures and helpers go in `conftest.py`.
- No network, no `time.sleep`. Use `freezegun` where time matters.
- A bug fix starts with a failing test.

## Backlog

Work is tracked with the `backlog` CLI. Task files live in `backlog/tasks/`; edit them through the CLI, not by hand.

```bash
backlog task list --plain                    # what's open
backlog task <id> --plain                    # read a task
backlog task edit <id> -s "In Progress" -a @agent
backlog task edit <id> --check-ac 1          # tick acceptance criteria as they pass
backlog task edit <id> --notes "…"           # what was done, follow-ups
backlog task edit <id> -s Done
backlog task create "Title" -d "…" --ac "…" -l <label> -m <milestone>
```

- Take one task at a time. Set it In Progress before starting.
- A task is Done when every acceptance criterion is checked and `mise run check` passes.
- Something new turns up: create a task for it instead of widening the current one.
- A design choice that changes behaviour goes in `docs/architecture.md`, with its reason.
- A change users can see updates `README.md` or the matching page in `docs/` in the same task.

## Hard rules

1. **Everything stays below the media root.** Every path goes through `media.resolve`. No `..` and no symlink escapes, in services, WebSocket commands and views alike.
2. **Never overwrite a user file by accident.** Uploads claim a free name, and edits replace atomically.
3. **The cache only ever deletes its own files** (names matching its pattern).
4. **Admin-only operations stay admin-only**: services, WebSocket commands, render and upload views, the panel.
5. **HA-free modules stay HA-free.**
6. **Version**: `manifest.json` `version` is the single source. Releases are tags `vX.Y.Z` that match it.

## Ask the human before

- Adding a runtime requirement to `manifest.json`.
- Changing a service's name, fields or response shape, the storage format, or the cache key (each one breaks existing users).
- Removing a feature or a configuration path.
