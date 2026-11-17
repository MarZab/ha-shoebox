# Rotations

A rotation is a set of pictures shown one at a time. Each rotation has a name and one or more patterns; the patterns choose pictures by their path, such as `local/Family/beach.jpg`. Pressing the rotation's **Next** button moves it to the next picture.

## Adding, changing and deleting

All in **Settings → Devices & services → Shoebox Media Manager**:

- **Add rotation** asks for a name, patterns and the [order](#order). The next step shows how many pictures the patterns select and the first few, before anything is saved.
- The gear next to a rotation changes its name, patterns or order. Renaming keeps its entities, areas and customizations.
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

- A glob (`*`, `**`, `?`, `[...]`) must match the whole path. `*` and `?` stay within one folder; `**` crosses folders; `**/` also matches no folder at all. A leading `/` is ignored. A pattern may have at most three `**`: each one multiplies the work of matching every path.
- `re:` followed by a [regular expression](https://docs.python.org/3/library/re.html) matches anywhere in the path; use `^` and `$` to match the whole path. Every walk matches every path against it, so keep it simple: an expression such as `(a+)+$` can take seconds per path. Saving a rotation refuses patterns that take more than a second to match the pictures as they are then.
- Matching is case-sensitive.

Only pictures count: `.jpg`, `.jpeg`, `.png`, `.webp`, `.heic`, `.heif`, `.avif`, `.gif`, `.bmp`, `.tif` and `.tiff`. Hidden files and folders (names starting with `.`) and symbolic links are skipped.

### Combining and excluding

A rotation shows the pictures of all its patterns together, each picture once. A pattern starting with `!` leaves pictures out:

```text
local/Family/**
nas/Holidays/**
!**/private/**
```

shows every picture below `Family` in My media and below `Holidays` on the NAS, except those in a `private` folder. Exclusions work with every kind of pattern, also `!re:…`.

## Order

Each rotation has an order, set when adding or changing it:

| Order | Next shows |
|-------|------------|
| **Path order** (default) | the picture after the current one, sorted by full path |
| **Shuffle** | a random picture not yet shown in this round |

### Path order

Pictures are shown sorted by their full path, so `local/Family/2023/…` comes before `local/Family/2024/…`. After the last picture the rotation starts again at the first.

### Shuffle

Shuffle works in rounds, as music players do: every picture is shown once per round, in random order, and the next round never starts with the picture that was just shown. The position counts the pictures shown in this round ("12 of 48").

### When files change

The rotation remembers its current picture, also across restarts.

- New pictures join in their place in path order; in shuffle they join the current round.
- If the current picture is deleted, moved or renamed, path order continues with the picture that sorts after it, so it does not start over; shuffle simply leaves it out.
- Changing the order keeps the current picture: switching to path order continues from it.
- If the patterns select nothing, the rotation shows no picture until they do.
