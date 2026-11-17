# Cache

Showing a picture at a size means decoding it, applying its [edits](editing.md), scaling it and encoding a JPEG. Shoebox keeps the results so the same picture at the same size is prepared only once.

## What is kept

One JPEG per picture, size and fit, in the `.cache/shoebox` folder of Home Assistant's configuration folder. Any change to a picture (a new version, a turn, a crop) produces a new prepared picture; the old one is no longer used and ages out.

The cache holds only derived data: clearing it loses nothing.

## Size

The [cache size option](configuration.md#options) (512 MB by default) limits it. When the cache grows past the limit, the pictures used least recently are removed.

Size **0** turns the cache off: nothing is stored, and pictures are prepared on every request. That costs CPU on every view, which a small host notices with thumbnails and large pictures.

## Backups

Home Assistant's backups leave out `.cache`, so the cache never makes backups bigger.

## Clearing

Turn on **Clear the cache** in the [options](configuration.md#options) and save. The options dialog shows how many pictures the cache holds and how much space they take. Removing the integration clears the cache too.

Only Shoebox's own files are removed; anything else in that folder is left alone.
