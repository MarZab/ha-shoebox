# Changelog

All notable changes to Shoebox are listed here. Versions follow [Semantic Versioning](https://semver.org/); pre-releases use Home Assistant's style (`1.0.0b1`, `1.0.0rc1`).

## Unreleased

- **Preview** in the picture viewer and a picture's menu: every device URL option on one picture, with a live preview and the parameters to copy.
- The device URL can prepare pictures for e-paper and other limited displays: palettes (black and white, greys, 6 and 7 colour e-paper, or your own colours), dithering, PNG or BMP, and contrast, saturation and brightness.

## 0.2.1

- iPhone photos saved as JPEG with an HDR gain map or depth map (MPO) can be turned and cropped; the extra images in them are kept.

## 0.2.0

- With only one media folder chosen, the panel opens it directly, as Home Assistant's media browser does.
- Reloading Shoebox (after changing options or rotations) no longer breaks an open panel.
- Release notes on GitHub, which HACS shows when updating, come from this changelog.

## 0.1.0

The first release.

- Media folder management: folders, upload, move, rename, delete, rotate and crop.
- Works on one or more of Home Assistant's media folders, chosen at setup; paths start with the folder's name, such as `local/Family/beach.jpg`.
- Text files open read-only in the panel; any file can be downloaded.
- Rotations: rotating pictures from the media folder, with an image entity and a Next button per rotation.
- A rotation shows the pictures of all its patterns; patterns starting with `!` leave pictures out.
- Rotations can shuffle: every picture once per round, in random order.
- A sized picture URL per rotation for devices such as ESPHome displays. ESPHome opens it with the image entity's own access token, without a long-lived token.
- Rotations in Home Assistant's media browser, for media players and Chromecast.
- Diagnostics, and English and Slovenian translations of the integration and the panel.
