# Rotations

A rotation is a set of pictures shown one at a time. Each rotation has a name and one or more patterns; the patterns choose pictures by their path, such as `local/Family/beach.jpg`. Pressing the rotation's **Next** button moves it to the next picture.

## Adding, changing and deleting

All in **Settings → Devices & services → Shoebox Media Manager**:

- **Add rotation** asks for a name and patterns. The next step shows how many pictures the patterns select and the first few, before anything is saved.
- The gear next to a rotation changes its name or patterns. Renaming keeps its entities, areas and customizations.
- The rotation's menu (⋮) deletes it, with its device and entities. Pictures stay.

Each rotation becomes a device with two entities: an [image](entities.md#image) and a [Next button](entities.md#next-button). Their entity IDs come from the name: a rotation named *Living room* has `image.living_room` and `button.living_room_next`.

## Patterns

Patterns match paths, which start with the name of the media folder: `local/Family/2024 Summer/beach.jpg` is in My media.

| Pattern | Selects |
|---------|---------|
| `local/Family/*` | pictures directly in `Family` |
| `local/Family/**` | pictures in `Family` and every folder below it |
| `*/Family/**` | pictures below a `Family` folder in every media folder |
| `**/beach*.jpg` | `beach…jpg` files anywhere |
| `local/Family/202?/*` | pictures in `local/Family/2020` … `local/Family/2029` |
| `local/Wallpapers/[a-m]*` | pictures in `Wallpapers` starting with a to m |
| `local/Wallpapers/[!a-m]*` | the other pictures in `Wallpapers` |
| `re:summer` | paths that contain `summer` (a regular expression) |
| `re:^local/Phone/IMG_\d+\.jpe?g$` | a regular expression matched against the whole path |

- A glob (`*`, `**`, `?`, `[...]`) must match the whole path. `*` and `?` stay within one folder; `**` crosses folders; `**/` also matches no folder at all. A leading `/` is ignored.
- `re:` followed by a [regular expression](https://docs.python.org/3/library/re.html) matches anywhere in the path; use `^` and `$` to match the whole path.
- Matching is case-sensitive.

Only pictures count: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif`, `.avif`, `.gif`, `.bmp`, `.tif` and `.tiff`. Hidden files and folders (names starting with `.`) and symbolic links are skipped.

### Fallbacks

A rotation can have several patterns. The first pattern that selects any picture is used, and the others are ignored. That makes fallbacks:

```text
local/Seasons/Winter/**
local/Wallpapers/**
```

shows winter pictures while there are any, and wallpapers otherwise. The rotation's `pattern` attribute tells which one is in use.

## Order

Pictures are shown in path order: sorted by their full path, so `local/Family/2023/…` comes before `local/Family/2024/…`. After the last picture the rotation starts again at the first.

The rotation remembers its current picture, also across restarts. When files change:

- New pictures join in their place in the order.
- If the current picture is deleted, moved or renamed, the rotation continues with the picture that sorts after it, so it does not start over.
- If the patterns select nothing, the rotation shows no picture until they do.
