# Editing

Shoebox turns and crops JPEG pictures without re-encoding them: the turn and the crop are written into the picture's own metadata, the way cameras and photo editors do. The picture data stays exactly as it was, so nothing is lost, and every edit can be changed or undone.

Edit in the [panel](panel.md) (open a picture, then turn or crop it) or with the [rotate](actions.md#rotate) and [crop](actions.md#crop) actions.

## Turning

A turn sets the picture's **EXIF orientation**, the tag phones write when they are held sideways. Browsers, phones, Home Assistant's dashboards and almost every photo viewer honor it, so a turned picture shows upright everywhere.

## Cropping

A crop is stored as the **Adobe XMP crop** (`crs:CropLeft`, `crs:CropTop`, `crs:CropRight`, `crs:CropBottom`), as Lightroom and Camera Raw write it. The crop is kept relative to the picture before orientation, so turning a cropped picture keeps the same part.

Shoebox applies the crop everywhere it shows a picture: the panel, rotations, the media browser and device URLs. Other apps differ:

| Shows the crop | Shows the whole picture |
|----------------|-------------------------|
| Shoebox, Adobe Lightroom and Camera Raw | Home Assistant's own media browser ("My media"), phones' galleries, most viewers |

Removing the crop (**Reset** in the panel, or `clear: true`) brings back the whole picture.

## Formats

| Format | Shown | Turned and cropped |
|--------|-------|--------------------|
| JPEG | yes | yes |
| JPEG with further images (MPO: iPhone photos with an HDR gain map or depth map) | yes | yes; the further images are kept and stay readable |
| PNG, WebP, GIF, BMP, TIFF, AVIF | yes | no |
| HEIC and HEIF (iPhone photos) | yes | no |

Pictures in other formats show with their own orientation, but turning or cropping them is refused: their metadata cannot be changed without rewriting the file.
