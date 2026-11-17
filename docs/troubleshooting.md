# Troubleshooting

## Shoebox does not start: "The media folder … is missing or no longer configured"

A media folder chosen for Shoebox does not exist, or was removed from `media_dirs` in `configuration.yaml`. Create the folder or add it back, and Shoebox retries on its own; or choose other folders in the [options](configuration.md#options). My media (`local`) is `/media` on Home Assistant OS and in the container.

## A rotation shows nothing

- Before its first **Next**, a rotation has no picture: press its Next button once.
- Its patterns may select no pictures. The rotation's `count` attribute is 0; check the patterns with the preview in **Settings → Devices & services → Shoebox Media Manager → the rotation's gear**. See [patterns](rotations.md#patterns).
- Only pictures count, by their extension. A video or a file without a picture extension is never shown.

## A picture shows sideways or uncropped elsewhere

Shoebox stores turns and crops in the picture's metadata. Most apps honor the turn; only Shoebox and Adobe's apps show the crop. See [editing](editing.md).

## A picture is refused as too large

Pictures are prepared at the size shown, but a PNG, HEIC or other non-JPEG must first be decoded in full. Above 50 megapixels Shoebox refuses that, because a small file can claim a huge picture and take gigabytes of memory. Large JPEGs are decoded at a reduced size and are not affected. The file itself can still be downloaded, moved and renamed.

## Turning or cropping is refused

Only JPEG pictures can be edited. HEIC (iPhone), PNG and other formats are shown, but their metadata cannot be changed in place.

## An action is refused: "… is not a media folder Shoebox uses" or "'..' is not allowed"

Paths start with the name of a media folder: `local` is My media, so a picture there is `local/Family/beach.jpg`. Shoebox never touches anything outside the media folders chosen in its [options](configuration.md#options).

## A device gets 401 or 404

- **401**: the `Authorization: Bearer <token>` header is missing or the token was deleted. See [a user for devices](displays.md#a-user-for-devices).
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
