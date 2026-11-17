# Shoebox

Shoebox: media manager and picture organizer for Home Assistant. Organize, upload, rotate and crop the photos in your media folder, and show them as rotating pictures on dashboards, notifications and displays.

![The Shoebox panel](docs/images/panel.png)

Home Assistant's media browser can upload and delete files. Shoebox adds what it doesn't have: folders, moving and renaming, uploads that never overwrite, thumbnails, and rotate and crop that keep the picture's quality. On top of that, a *rotation* turns a set of pictures into an image that changes, for dashboards, phones and small displays.

## What you can do

- **Organize the photos in My media from your phone**: create folders, rename, move and delete. [How](docs/use-cases.md#organize-from-your-phone)
- **Upload from your phone straight into the right folder.** An existing file is never overwritten. [How](docs/use-cases.md#upload-from-your-phone)
- **Fix sideways photos and crop them** without re-encoding: the turn and the crop are stored in the photo's own metadata. [How](docs/use-cases.md#fix-sideways-photos-and-crop)
- **Run a slideshow on a dashboard**, on a tablet, TV or browser. [How](docs/use-cases.md#slideshow-on-a-dashboard)
- **Build a digital photo frame** with an ESPHome e-ink or LCD display. [How](docs/use-cases.md#esphome-photo-frame)
- **Show different pictures by time of day or season**, switched by automations. [How](docs/use-cases.md#pictures-by-time-of-day-or-season)
- **Send a photo of the day** in a notification. [How](docs/use-cases.md#photo-of-the-day)
- **Put the kids' artwork on the wall**, uploaded from the phone. [How](docs/use-cases.md#kids-artwork-wall)

## Install

1. In HACS, search for **Shoebox** (or "media manager", "photo") and download it. Restart Home Assistant.
2. Go to **Settings → Devices & services → Add integration** and add **Shoebox Media Manager**. It asks no questions.
3. Open **Shoebox** in the sidebar.

Shoebox works on Home Assistant's local media folder (**My media**, `/media`). Removing the integration leaves your files as they are. More in [configuration](docs/configuration.md).

## Quick start: a slideshow on a dashboard

1. Go to **Settings → Devices & services → Shoebox Media Manager → Add rotation**. Name it *Living room* and give it a pattern such as `Family/**` (every picture below the `Family` folder). The next step shows how many pictures it selects.
2. Add a picture entity card to a dashboard:

   ```yaml
   type: picture-entity
   entity: image.living_room
   show_name: false
   show_state: false
   ```

3. Move to the next picture every 10 minutes with an automation:

   ```yaml
   alias: Next living room picture
   triggers:
     - trigger: time_pattern
       minutes: /10
   actions:
     - action: button.press
       target:
         entity_id: button.living_room_next
   ```

## Quick start: an ESPHome display

Every rotation has a fixed URL that serves its current picture at the size a device asks for, as a baseline JPEG small displays can decode. Create a [long-lived access token](docs/displays.md#a-user-for-devices) for a user without admin rights, then:

```yaml
http_request:

online_image:
  - id: photo
    url: http://homeassistant.local:8123/api/shoebox/image/image.living_room?width=800&height=480&fit=cover
    format: JPEG
    type: RGB565
    update_interval: never
    request_headers:
      Authorization: !secret shoebox_authorization  # "Bearer <long-lived token>"
    on_download_finished:
      - component.update: my_display

api:
  actions:
    - action: show_next_photo
      then:
        - component.update: photo
```

Draw it with `it.image(0, 0, id(photo));` and refresh it from Home Assistant whenever the rotation moves on:

```yaml
alias: Photo frame follows the living room
triggers:
  - trigger: state
    entity_id: image.living_room
actions:
  - action: esphome.photo_frame_show_next_photo
```

The whole setup is in [displays](docs/displays.md#esphome).

## Actions and entities

| | What it does | Reference |
|---|---|---|
| `shoebox.list` | Lists files and folders that match a pattern | [actions](docs/actions.md#list) |
| `shoebox.create_folder` | Creates a folder | [actions](docs/actions.md#create_folder) |
| `shoebox.move` | Moves a file or folder into another folder | [actions](docs/actions.md#move) |
| `shoebox.rename` | Renames a file or folder | [actions](docs/actions.md#rename) |
| `shoebox.delete` | Deletes a file or folder | [actions](docs/actions.md#delete) |
| `shoebox.rotate` | Turns a JPEG picture | [actions](docs/actions.md#rotate) |
| `shoebox.crop` | Crops a JPEG picture | [actions](docs/actions.md#crop) |
| `image.<rotation>` | The rotation's current picture | [entities](docs/entities.md#image) |
| `button.<rotation>_next` | Moves the rotation to its next picture | [entities](docs/entities.md#next-button) |

The actions are for administrators. Paths are relative to the media folder, such as `Family/beach.jpg`.

## Limits

- Rotate and crop work on JPEG files. Other formats (PNG, HEIC, ...) are shown and served, but not edited.
- Shoebox works on the local media folder, not on network shares added as other media folders.
- The panel is for administrators.
- It is made for a household media folder: hundreds of pictures, not a photo library.

## Documentation

[docs/](docs/README.md) has the details: rotations and patterns, every action, the entities, editing, displays, the panel, the cache and troubleshooting.

---

Keywords: media manager, picture organizer, photo organizer, photo frame, slideshow, file manager, Home Assistant.
