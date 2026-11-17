# Actions

Shoebox's actions work on files and folders below the media folder. They are for administrators: a call from a user without admin rights is refused.

Paths are relative to the media folder, such as `Family/beach.jpg`. Absolute paths below the media folder (`/media/Family/beach.jpg`) work too. Anything outside the media folder, `..`, and symbolic links are refused.

Every action can return a response; use `response_variable` in a script or automation. Refusals stop the script with a message in your language, for example *"Family/beach.jpg" does not exist.*

## list

Lists the files and folders that match a pattern. It only returns a response.

| Field | Default | |
|-------|---------|---|
| `pattern` | `**` | A [pattern](rotations.md#patterns) over paths below the media folder |
| `type` | `all` | `all`, `image` (pictures), `file` (other files) or `folder` |

```yaml
action: shoebox.list
data:
  pattern: "Family/**"
  type: image
response_variable: found
```

```yaml
count: 2
items:
  - path: Family/2024 Summer/beach.jpg
    type: image
    size: 482113
    modified: 1763371200.5
  - path: Family/Kids art/drawing.png
    type: image
    size: 91240
    modified: 1763371260.0
```

`size` is in bytes; `modified` is a Unix timestamp. Items are sorted by path.

## create_folder

Creates a folder, with any missing parent folders. Creating a folder that exists does nothing.

```yaml
action: shoebox.create_folder
data:
  path: Family/2025 Summer
```

```yaml
path: Family/2025 Summer
```

## move

Moves a file or folder into another folder. Nothing is overwritten: if the target exists, the move is refused.

| Field | |
|-------|---|
| `path` | The file or folder to move |
| `to` | The folder to move into; empty for the media folder itself |

```yaml
action: shoebox.move
data:
  path: Phone/IMG_0001.jpg
  to: Family/2025 Summer
```

```yaml
path: Family/2025 Summer/IMG_0001.jpg
```

## rename

Renames a file or folder where it is. Nothing is overwritten.

```yaml
action: shoebox.rename
data:
  path: Family/2025 Summer/IMG_0001.jpg
  name: beach.jpg
```

```yaml
path: Family/2025 Summer/beach.jpg
```

## delete

Deletes a file, or a folder with everything in it. **This cannot be undone.**

```yaml
action: shoebox.delete
data:
  path: Phone/IMG_0002.jpg
```

```yaml
deleted: Phone/IMG_0002.jpg
```

## rotate

Turns a JPEG picture by changing its EXIF orientation. The picture data is not re-encoded. See [editing](editing.md).

| Field | |
|-------|---|
| `path` | A JPEG picture |
| `by` | How far to turn the picture as shown, clockwise: `90`, `180`, `270` (or `-90`) |
| `orientation` | Instead of `by`: set the EXIF orientation, 1 to 8 |

```yaml
action: shoebox.rotate
data:
  path: Family/2025 Summer/beach.jpg
  by: 90
```

```yaml
path: Family/2025 Summer/beach.jpg
orientation: 6
```

## crop

Crops a JPEG picture by storing the crop in its XMP data, as photo editors do. The picture data is not changed. See [editing](editing.md).

| Field | |
|-------|---|
| `path` | A JPEG picture |
| `left`, `top`, `right`, `bottom` | The crop as fractions of the picture as shown (0 to 1); all four are needed |
| `clear` | `true` removes the crop instead |

```yaml
action: shoebox.crop
data:
  path: Family/2025 Summer/beach.jpg
  left: 0.1
  top: 0
  right: 0.9
  bottom: 1
```

```yaml
path: Family/2025 Summer/beach.jpg
crop: [0.1, 0, 0.9, 1]
```

The returned `crop` is stored relative to the picture before its orientation is applied, as photo editors store it; for an upright picture it equals what you gave. `crop` is empty after `clear: true`.

When the turned or cropped picture is the current picture of a rotation, the rotation's image updates.
