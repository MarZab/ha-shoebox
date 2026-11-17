# Troubleshooting

## Shoebox does not start: "The media folder … does not exist"

Shoebox works on Home Assistant's local media folder (`/media` on Home Assistant OS and in the container). Create it, for example by uploading a file in **Media → My media**; Shoebox retries on its own.

## A rotation shows nothing

- Before its first **Next**, a rotation has no picture: press its Next button once.
- Its patterns may select no pictures. The rotation's `count` attribute is 0; check the patterns with the preview in **Settings → Devices & services → Shoebox Media Manager → the rotation's gear**. See [patterns](rotations.md#patterns).
- Only pictures count, by their extension. A video or a file without a picture extension is never shown.

## A picture shows sideways or uncropped elsewhere

Shoebox stores turns and crops in the picture's metadata. Most apps honor the turn; only Shoebox and Adobe's apps show the crop. See [editing](editing.md).

## Turning or cropping is refused

Only JPEG pictures can be edited. HEIC (iPhone), PNG and other formats are shown, but their metadata cannot be changed in place.

## An action is refused: "… is outside the media folder" or "'..' is not allowed"

Paths are relative to the media folder, such as `Family/beach.jpg`. Shoebox never touches anything outside it.

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
