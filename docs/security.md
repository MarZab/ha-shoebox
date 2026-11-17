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
- Move and rename refuse an existing target. The target name is claimed first, with an empty file or folder created exclusively, and the move replaces only that; something arriving under the same name at the same moment is never replaced.
- Turning and cropping rewrite the file through a temporary file and an atomic replace, keeping its permissions; a crash leaves the old file. When one editor save turns and crops and the crop fails, the turn is taken back.
- Error messages name files by their path in the media folders, never by where they are on the host.

Delete is final; the panel asks first.

## Who may do what

| | Who |
|---|---|
| File actions (`shoebox.list`, `move`, `delete`, ...) | administrators (`async_register_admin_service`) |
| Panel and its WebSocket commands | administrators |
| Render view (panel pictures) | administrators, also through signed URLs |
| Upload view | administrators |
| Download view (original files) | administrators, also through signed URLs |
| Device view (`/api/shoebox/image/<entity_id>`) | any logged-in user or long-lived token, or the image entity's own access token (`?token=`), which opens only that rotation |
| Media source view (`/api/shoebox/media/...`) | any logged-in user, also through URLs Home Assistant signs for media players |

The device and media source views serve only pictures of rotations, prepared: never other files, and never the original file. The device view serves a rotation's current picture, which every user also sees through its image entity. The media source view serves **every picture a rotation's patterns select**, because the media browser lists them all: a rotation makes its pictures visible to every user. Folders no rotation selects stay admin-only.

## URLs and tokens

- The panel's picture URLs are signed for the user's connection and expire after an hour.
- Devices that talk to Home Assistant, such as ESPHome, use the image entity's own access token: the one in its `entity_picture` attribute, which Home Assistant changes every 5 minutes and keeps the last two of. The device view checks it exactly as Home Assistant's image proxy does, and it opens only that entity's picture, nothing else. Anyone who can read the entity's attributes can read the token; that is everyone who can see the entity anyway.
- Refusals follow Home Assistant's image view: a wrong or expired token gets `403` and does not count as a login attempt; a wrong `Authorization` header gets `401` and counts towards an IP ban; an unknown entity gets `401` unless the caller is logged in, so the URL does not reveal which entities exist.
- The token is in the URL, so Shoebox logs no URLs of the device view. Home Assistant itself logs the URL of a refused login (`401`), as it does for its image proxy; ESPHome logs it at debug level, which the documented configuration turns off.
- Other devices use a long-lived access token in the `Authorization` header. A token carries all of its user's rights, so the docs recommend a user without admin rights for devices; deleting the token locks the device out.

## Uploads

Only files the browser declares as pictures, video or audio are accepted, up to 200 MB. File names are reduced to their last part, without control characters or leading dots.

## Pictures from elsewhere

A picture in a media folder may come from anywhere: an upload, a network share, a phone backup. Preparing one is bounded: pictures above 50 megapixels (after JPEG's reduced decoding) are refused before they are decoded, metadata is read only from the start of a JPEG, XMP above 256 KB is ignored, and the crop is parsed without patterns that backtrack. The media view checks the one picture asked for against the rotation instead of walking the folders.

The device URL accepts any size from 1 to 4096, because displays need their exact size. Each size is prepared once and cached, so a logged-in user who asks for many different sizes keeps the preparing busy and pushes other pictures out of the cache. Give devices their own user and token, or the image entity's token, as for any Home Assistant API.

Rotation patterns are entered by admins. A `re:` expression that backtracks badly can still stall Home Assistant when the folders grow after it was saved; saving refuses patterns that already take more than a second.

## The cache

The cache folder holds only files Shoebox made. Eviction and clearing remove only names that match its own pattern (64 hex digits and `.jpg`, or its temporary files).

## Logs and diagnostics

Logs name the user and path of uploads at INFO. Diagnostics contain no file names.
