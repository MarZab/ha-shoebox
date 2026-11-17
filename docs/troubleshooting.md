# Troubleshooting

## Shoebox does not start

- **"The media folder … does not exist or cannot be reached"**: the folder is configured but not there, for example a network share that is not mounted yet. Shoebox retries on its own and starts once the folder is there.
- **"The media folder … is no longer in Home Assistant's media folders"**: the folder was removed from `media_dirs` in `configuration.yaml`. Shoebox does not retry, because only a change to the configuration brings it back. Add it back and restart Home Assistant, or choose other folders in the [options](configuration.md#options) and reload Shoebox.

My media (`local`) is `/media` on Home Assistant OS and in the container.

## A rotation shows nothing

- Before its first **Next**, a rotation has no picture: press its Next button once.
- Its patterns may select no pictures. The rotation's `count` attribute is 0; check the patterns with the preview in **Settings → Devices & services → Shoebox Media Manager → the rotation's gear**. See [patterns](rotations.md#patterns).
- Only pictures count, by their extension. A video or a file without a picture extension is never shown.
- Files and folders whose names are not valid UTF-8 (often from old Windows or camera software) are skipped everywhere, with a warning in the log naming them. Rename them, for example over Samba.

## A picture shows sideways or uncropped elsewhere

Shoebox stores turns and crops in the picture's metadata. Most apps honor the turn; only Shoebox and Adobe's apps show the crop. See [editing](editing.md).

## A picture is refused as too large

Pictures are prepared at the size shown, but a PNG, HEIC or other non-JPEG must first be decoded in full. Above 50 megapixels Shoebox refuses that, because a small file can claim a huge picture and take gigabytes of memory. Large JPEGs are decoded at a reduced size and are not affected. The file itself can still be downloaded, moved and renamed.

## Turning or cropping is refused

Only JPEG pictures can be edited. HEIC (iPhone), PNG and other formats are shown, but their metadata cannot be changed in place.

## An action is refused: "… is not a media folder Shoebox uses" or "'..' is not allowed"

Paths start with the name of a media folder: `local` is My media, so a picture there is `local/Family/beach.jpg`. Shoebox never touches anything outside the media folders chosen in its [options](configuration.md#options).

## A device gets 400, 401, 403 or 404

- **401**: the `Authorization: Bearer <token>` header is missing or the token was deleted. See [a user for devices](displays.md#a-user-for-devices).
- **403**: the `token` in the URL is not the image entity's current or previous one, or belongs to another rotation's entity. A device should read it from the entity's `entity_picture` each time it changes: see the [ESPHome example](displays.md#esphome).
- **404**: the entity ID is not a Shoebox rotation image, or the rotation has no picture yet.
- **400**: `width` or `height` is outside 1 to 4096, or `fit` is not `cover` or `contain`.

## The panel is missing

The panel is for administrators. It is also gone when **Show in sidebar** is off in the [options](configuration.md#options), or when you hid it in your own sidebar.

## Logs and diagnostics

Shoebox logs under `custom_components.shoebox`. For more detail, add to `configuration.yaml`:

```yaml
logger:
  logs:
    custom_components.shoebox: debug
```

**Settings → Devices & services → Shoebox Media Manager → ⋮ → Download diagnostics** gives the options, the cache's size and each rotation's patterns and position. It contains no file names; attach it to an issue.

Report problems at [github.com/MarZab/ha-shoebox/issues](https://github.com/MarZab/ha-shoebox/issues).
