# Displays

Every rotation can be shown on dashboards, in notifications, in the media browser and on devices outside Home Assistant.

## Dashboards

Use the rotation's [image entity](entities.md#image) with a picture entity card:

```yaml
type: picture-entity
entity: image.living_room
show_name: false
show_state: false
```

A picture glance card works the same way and can add the Next button:

```yaml
type: picture-glance
title: Living room
entity: image.living_room
entities:
  - entity: button.living_room_next
```

The card fetches the new picture whenever the rotation moves on or its picture is edited.

## Notifications

The Home Assistant Companion app can attach the current picture:

```yaml
action: notify.mobile_app_my_phone
data:
  message: Photo of the day
  data:
    image: /api/image_proxy/image.photo_of_the_day
```

## Media browser

Each rotation appears under **Media → Shoebox** as a folder of the pictures it selects. Pictures from there can be played on media players that show images, such as a Chromecast. They are served prepared (turned and cropped) at up to 1920 × 1080.

## Devices

Each rotation has a URL that always serves its current picture, prepared at the size the device asks for:

```text
http://<home assistant>:8123/api/shoebox/image/image.living_room?width=800&height=480&fit=cover
```

| Parameter | Default | |
|-----------|---------|---|
| `width`, `height` | 1280 | The size in pixels, 1 to 4096 |
| `fit` | `contain` | `cover`: exactly this size, the overhang cut evenly. `contain`: fitted inside, aspect kept |

- The picture is a baseline JPEG, which small displays can decode.
- The URL stays the same while the rotation moves on, across reloads and restarts.
- Each response has an `ETag`. A device that sends it back in `If-None-Match` gets `304 Not Modified` while the picture is unchanged.
- Before the rotation's first Next, the URL answers `404`.

### A user for devices

The URL needs an access token, sent as `Authorization: Bearer <token>`. A token carries all the rights of its user, so give devices their own user:

1. **Settings → People → Users → Add user**: name it *Displays*, and leave **Administrator** off.
2. Log in as that user once, open its profile, **Security → Long-lived access tokens → Create token**.
3. Put the token on the device. Delete the token in the same place to lock the device out.

### ESPHome

[ESPHome](https://esphome.io/)'s [online image](https://esphome.io/components/image/online_image/) downloads the picture and a display draws it. This photo frame downloads only when Home Assistant tells it the rotation moved on.

ESPHome configuration (`photo-frame.yaml`):

```yaml
esphome:
  name: photo-frame

http_request:

online_image:
  - id: photo
    url: http://homeassistant.local:8123/api/shoebox/image/image.living_room?width=800&height=480&fit=cover
    format: JPEG
    type: RGB565
    update_interval: never
    request_headers:
      Authorization: !secret shoebox_authorization
    on_download_finished:
      - component.update: frame

api:
  actions:
    - action: show_next_photo
      then:
        - component.update: photo

display:
  - platform: ...  # your display
    id: frame
    update_interval: never
    lambda: |-
      it.image(0, 0, id(photo));
```

`secrets.yaml`:

```yaml
shoebox_authorization: "Bearer <long-lived token of the Displays user>"
```

Home Assistant automation that refreshes the frame:

```yaml
alias: Photo frame follows the living room
triggers:
  - trigger: state
    entity_id: image.living_room
actions:
  - action: esphome.photo_frame_show_next_photo
```

Match `width` and `height` to the display. For e-paper, use `fit: cover` and the image `type` your display supports, such as `BINARY` or `GRAYSCALE`.

## URL lifetime

- The device URL does not expire; it works as long as its token does.
- The image entity's picture URL (`entity_picture`) carries an access token that Home Assistant changes every 5 minutes, so it is no good for devices. Home Assistant's `/api/image_proxy/<entity_id>` with an `Authorization` header does not change, but it is always the entity's size; the device URL takes yours.
- Thumbnails and pictures in the [panel](panel.md) use signed links that work for one hour; the panel asks for new ones before that.
