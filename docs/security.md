# Security

Shoebox reads and changes files on the Home Assistant host. These are the rules that keep that safe, and where they are enforced.

## Everything stays in the chosen media folders

Every path from outside (actions, WebSocket commands, views, uploads) starts with the name of a media folder. `Library.locate` refuses names of folders Shoebox was not given and the top level itself, then `media.resolve` keeps the rest below that folder:

- `..` is refused outright, and so is a NUL byte.
- An absolute path must lie below one of the chosen media folders.
- A path that is itself a symbolic link is refused, since deleting or moving it would act on its target.
- Symbolic links in the folders on the way are followed, and the real result must still be below that media folder.

A media folder itself cannot be created, renamed, moved or deleted. Listings skip hidden names and symbolic links. Home Assistant's own security filter answers some suspicious URLs (such as `../` in a query) with 400 before Shoebox sees them.

## Nothing is overwritten by accident

- Uploads stream into a hidden temporary file in the target folder, then take the first free name (`photo.jpg`, `photo-1.jpg`, ...). The name is claimed with `O_CREAT | O_EXCL`, so two uploads never get the same name and an existing file is never replaced.
- Move and rename refuse an existing target.
- Turning and cropping rewrite the file through a temporary file and an atomic replace, keeping its permissions; a crash leaves the old file.

Delete is final; the panel asks first.

## Who may do what

| | Who |
|---|---|
| File actions (`shoebox.list`, `move`, `delete`, ...) | administrators (`async_register_admin_service`) |
| Panel and its WebSocket commands | administrators |
| Render view (panel pictures) | administrators, also through signed URLs |
| Upload view | administrators |
| Download view (original files) | administrators, also through signed URLs |
| Device view (`/api/shoebox/image/<entity_id>`) | any logged-in user or long-lived token |
| Media source view (`/api/shoebox/media/...`) | any logged-in user, also through URLs Home Assistant signs for media players |

The device and media source views serve only pictures of rotations, prepared: never other files, and never the original file. Every user can see rotations through their image entities anyway.

## URLs and tokens

- The panel's picture URLs are signed for the user's connection and expire after an hour.
- Devices use a long-lived access token in the `Authorization` header. A token carries all of its user's rights, so the docs recommend a user without admin rights for devices; deleting the token locks the device out.

## Uploads

Only files the browser declares as pictures, video or audio are accepted, up to 200 MB. File names are reduced to their last part, without control characters or leading dots.

## Pictures from elsewhere

A picture in a media folder may come from anywhere: an upload, a network share, a phone backup. Preparing one is bounded: pictures above 50 megapixels (after JPEG's reduced decoding) are refused before they are decoded, metadata is read only from the start of a JPEG, XMP above 256 KB is ignored, and the crop is parsed without patterns that backtrack. The media view checks the one picture asked for against the rotation instead of walking the folders.

## The cache

The cache folder holds only files Shoebox made. Eviction and clearing remove only names that match its own pattern (64 hex digits and `.jpg`, or its temporary files).

## Logs and diagnostics

Logs name the user and path of uploads at INFO. Diagnostics contain no file names.
