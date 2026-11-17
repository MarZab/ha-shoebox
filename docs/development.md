# Development

The integration is `custom_components/shoebox/`; everything else is tooling for building, testing and releasing it.

## Setup

[mise](https://mise.jdx.dev) installs Python and uv at the pinned versions; [uv](https://docs.astral.sh/uv/) installs the dev dependencies.

```bash
mise install        # Python 3.14 and uv
mise run setup      # dev dependencies into .venv
mise run check      # lint, types and tests: what CI runs
```

Without mise: `uv sync`, then `uv run pytest`, `uv run ruff check .`, `uv run mypy`.

Home Assistant is pinned through `pytest-homeassistant-custom-component` in `pyproject.toml`: the tests and the Docker Home Assistant both use the version it brings. Raise both together by bumping that plugin, and bump `home-assistant-frontend` next to it to the version that Home Assistant release uses (the tests serve the panel with it).

## Tasks

Tasks are scripts in `tools/tasks/`; `mise tasks` lists them. Arguments after `--` go to the script.

| Task | Does |
|------|------|
| `check` | ruff, ruff format check, mypy strict, pytest with coverage |
| `test` | pytest (`mise run test -- -k rotation`) |
| `lint`, `format`, `type` | ruff check, ruff fix and format, mypy |
| `hassfest` | Home Assistant's own validation of the manifest, translations, services and icons, as CI runs it |
| `release` | the current version, or a release: see [release](release.md) |
| `clean` | removes caches and coverage files |
| `dev:up`, `dev:down`, `dev:restart`, `dev:logs`, `dev:pull` | the local Home Assistant |
| `dev:token` | an access token for scripted checks |
| `dev:panel` | the panel in a headless browser, with screenshots |

`hassfest` runs Home Assistant's validation of the latest stable release, as CI runs a current one: the manifest may use keys newer than the version the tests are pinned to, such as `categories`. It keeps that release's source and an environment with it in `.cache/hassfest/`; `HASSFEST_VERSION=2026.11.2 mise run hassfest` picks a release.

## Local Home Assistant

```bash
mise run dev:up       # http://localhost:8123
```

- Docker runs the official Home Assistant image at the pinned version, with the configuration in `docker/ha-config/`.
- The integration is mounted read-only; `mise run dev:restart` loads your changes.
- `docker/media/` is mounted as the media folder `local` (My media). `tools/scripts/sample_media.py` fills it on the first start: JPEGs with EXIF orientations (one sideways, one upside down), a PNG, a HEIC, a text file and nested folders. Every picture shows its name and an arrow to its top. Delete the folder to get fresh samples.
- `mise run dev:token` onboards a fresh Home Assistant with the owner **dev** / **dev** and prints an access token, for `curl` and scripts.

## Checking the panel

`mise run dev:panel` logs in as dev, opens the panel in light and dark themes and at phone width, fails on a missing Home Assistant element or a console error, and saves screenshots to `docker/screenshots/`. It needs Node.js with Playwright and Chromium.

After changing the panel, also walk these by hand (or with Playwright):

- [ ] Browse into a folder and back; thumbnails show turned pictures upright
- [ ] Upload several files by the picker and by dropping; a duplicate name becomes `name-1`; a non-media file is refused with a message
- [ ] New folder, rename, move (with the folder search), delete with confirmation
- [ ] Open a picture; previous and next
- [ ] Edit: turn and crop with each aspect ratio; Cancel leaves the file as it was; Save writes both; Reset
- [ ] Open a text file; download a file
- [ ] Grid, list and auto views, remembered after a reload; search from a folder and from the top level, open a result
- [ ] The menu (⋮) opens the integration's page in Settings
- [ ] Keyboard only: Tab to a folder and open it, open a picture, crop with the arrow keys, Escape back
- [ ] Light and dark theme; phone width with the sidebar menu button
- [ ] Your profile language set to Slovenian switches the panel

## Screenshots

The panel screenshot in the README shows real photos: `uv run python tools/scripts/screenshot_photos.py docker/media` downloads them (Unsplash photos through picsum.photos, free to use) into *Photos/Summer 2025*. Take the panel and editor screenshots at 960 × 760 with the sidebar docked (871 to 975 px keeps it docked with three thumbnails a row) and twice the pixel density, and save them as JPEG. The quick start's two screenshots show the add-rotation dialog filled in (*Living room*, `local/Photos/**`) and a dashboard with a picture entity card and a tile for its Next button.

## Repository

| Path | |
|------|---|
| `custom_components/shoebox/` | the integration (see [architecture](architecture.md)) |
| `tests/` | pytest (see [testing](testing.md)) |
| `docs/` | user and developer documentation |
| `docker/` | the local Home Assistant |
| `tools/tasks/` | mise tasks |
| `tools/scripts/` | sample media, screenshot photos, brand icon, dev token, panel check, release |
| `backlog/` | tasks and milestones ([Backlog.md](https://github.com/MrLesk/Backlog.md)) |
| `.github/workflows/` | CI, validation, releases |
