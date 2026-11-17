# Testing

```bash
mise run test                 # everything
mise run test -- tests/ha     # Home Assistant tests only
mise run check                # with lint, types and coverage
```

## Layout

| Path | Tests |
|------|-------|
| `tests/test_media.py`, `test_library.py`, `test_imaging.py`, `test_cache.py`, `test_upload.py` | The modules that do not import Home Assistant, directly, on `tmp_path` |
| `tests/test_definitions.py` | `services.yaml`, `icons.json`, translations, error messages and panel texts agree; English and Slovenian match |
| `tests/test_docs.py` | Every relative link and heading anchor in the docs resolves |
| `tests/test_release.py` | Release version arithmetic and checks |
| `tests/ha/` | The integration in Home Assistant, with `pytest-homeassistant-custom-component` |

`tests/ha/` covers setup and removal, the config, options and rotation flows, several media folders (`test_folders.py`), every action, the entities, the views, the WebSocket commands, the media source and diagnostics.

## Fixtures

| | Gives |
|---|---|
| `media_root` | an empty media folder on `tmp_path` |
| `tree("a/", "b/c.jpg", "d.txt")` | lays out folders, quadrant pictures and text files below it |
| `tests/images.py` | `write_image` (quadrant pictures with EXIF orientation and XMP crop), `colour_at` (which quadrant colour is at a point) |
| `tests/ha/conftest.py` | each test's own config and media folder; `entry`, `loaded`, `with_rotation` (an entry with the rotation *Evening*), `rotation_id` |

Quadrant pictures are red, green, blue and white in their four corners, so a test reads orientation and crop back by colour instead of comparing pixels. Pictures are generated in memory; there are no binary test files.

## Writing tests

- One behaviour per test, named after the behaviour; parametrize instead of copying.
- Most coverage comes from the modules without Home Assistant. Home Assistant tests check the wiring: one happy path and one refusal per action, view or command.
- No network and no sleeping.
- A bug fix starts with a test that fails.
- The panel's JavaScript has no unit tests; check it with `mise run dev:panel` and the [checklist](development.md#checking-the-panel).
