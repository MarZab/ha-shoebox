# Architecture

## Modules

| Module | Holds | Imports Home Assistant |
|--------|-------|------------------------|
| `media.py` | Paths kept below the media folder, listing, patterns, rotation order, file operations | no |
| `imaging.py` | EXIF orientation, XMP crop, preparing a picture at a size | no |
| `cache.py` | Prepared pictures on disk | no |
| `upload.py` | Upload names and placement | no |
| `errors.py` | Errors of the modules above, each with a translation key | no |
| `runtime.py` | `Shoebox`, the entry's runtime: media folder, cache, rotations, the executor bridge | yes |
| `rotations.py` | Rotation state, kept in Home Assistant storage | yes |
| `__init__.py` | Setup, unload, removal | yes |
| `config_flow.py` | Config flow, options, the rotation subentry flow | yes |
| `services.py` | The file actions | yes |
| `entity.py`, `image.py`, `button.py` | Rotation devices, image entities, Next buttons | yes |
| `views.py` | HTTP: panel pictures, uploads, device pictures, media source pictures | yes |
| `websocket.py` | The panel's commands | yes |
| `panel.py` | Serving and registering the sidebar panel | yes |
| `media_source.py` | Rotations in the media browser | yes |
| `diagnostics.py` | Diagnostics | yes |
| `frontend/` | The panel: plain ES modules, no build step | |

The modules that do not import Home Assistant hold the file and picture logic. They are tested directly and fast, and stay that way.

## Data flow

### A rotation moves on

1. Pressing **Next** (`button.py`) calls `Rotations.async_advance` with the rotation's patterns.
2. It lists the media folder (`media.walk`, in the executor), takes the pictures of the first matching pattern (`media.first_match`) and the one after the current picture (`media.advance`).
3. The new state is saved to storage (with a short delay) and sent on the rotation's dispatcher signal.
4. The image entity writes its state; its `image_last_updated` is the time of the step, so dashboards fetch the new picture.

Turning or cropping a file calls `Rotations.async_file_changed`: rotations showing that file update the same way.

### A picture is shown

Every picture goes through `Shoebox.picture(path, width, height, fit)`:

1. The path is resolved below the media folder (`media.resolve_file`).
2. A semaphore lets two pictures be prepared at a time; more requests wait.
3. `VariantCache.get` returns the stored picture or makes it with `imaging.render` (crop, orientation, scale, baseline JPEG) and stores it.

Who asks: the image entity (1280 × 1280, contain), the panel's render view (thumbnails, viewer, editor), the device view (any size) and the media source view (1920 × 1080 and thumbnails).

### The panel

The panel talks over the WebSocket (`websocket.py`: browse, folders, info, edit, rotations) and the file actions. Its `<img>` elements cannot send the Authorization header, so picture URLs point at the render view and are signed for the user's connection (`async_sign_path`, one hour). Uploads go to the upload view as multipart and stream to a hidden temporary file.

## Storage

| What | Where |
|------|-------|
| Options | the config entry |
| Rotations: title and patterns | config subentries |
| Rotation state: file, position, count, pattern, last step | `.storage/shoebox.rotations`, keyed by subentry id, versioned |
| Prepared pictures | `.cache/shoebox/`, one JPEG per key |

The cache key is a SHA-256 of a version number, the file's real path, size and modification time, the width, height and fit, and an extra marker (`nocrop` for the editor's uncropped base). Any change to the file gives a new key; old pictures age out. Bump `cache.VERSION` when `render` output changes.

## Design choices

**A media organizer first, with extras by use.** Home Assistant's media browser uploads and deletes; Shoebox adds what it lacks (folders, move, rename, safe uploads, thumbnails, rotate and crop). Rotations, device pictures and the media source build on that. They have no switches: nothing runs until a rotation is added. The only setting besides the cache is *Show in sidebar*, because per-user hiding cannot remove the panel for everyone.

**Configured in the UI only.** Integrations with a config flow do not take YAML; `cv.config_entry_only_config_schema` turns a leftover `shoebox:` into a repair.

**Rotations are config subentries.** They get Settings' own add, change and delete dialogs and a stable identity (the subentry id), so renaming keeps the entity, its area and customizations, and names are free text. The add flow previews what the patterns select.

**A device per rotation with an image and a Next button, and no rotation actions.** That is how core integrations expose things: entities usable from dashboards, automations, scenes and voice. Advancing is a button, not an action or an interval setting; Home Assistant's guidance is that user-chosen schedules belong in automations. Configuration has no actions because it lives in subentries.

**Edits are metadata.** EXIF orientation and the Adobe XMP crop keep the picture data untouched and the edits reversible, and other apps understand them. The cost: only JPEG can be edited, and most viewers ignore the crop.

**Devices get a stable URL with a token.** Devices such as ESPHome need a URL that does not change, their own size and baseline JPEG; they authenticate with a long-lived token in a header, the standard for Home Assistant's API. The device and media source views accept any user, so a device can use a user without admin rights; they serve only pictures of rotations, which every user can see through the image entity anyway.

**Sized for hundreds of pictures.** Listing walks the media folder on demand, with no index or watcher. That keeps the code small; revisit if real use passes a few thousand files.

**Media players get their own view.** Home Assistant signs media source URLs for its content user, who is not an admin, so the admin-only render view cannot serve them.

**Home Assistant 2026.10 or newer.** Setup and unload return a bool, which 2026.10 requires and later versions accept from custom integrations.

## Open questions

- **Other media folders.** Home Assistant allows several `media_dirs`; Shoebox uses the local one only.
- **Recoverable delete.** Deletes are final, with a confirmation in the panel; a hidden trash could make them recoverable.
