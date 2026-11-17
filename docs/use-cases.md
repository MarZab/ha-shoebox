# Use cases

Step-by-step recipes. Each assumes Shoebox is [installed and added](configuration.md#adding-shoebox).

## Organize from your phone

1. Open the Home Assistant app and tap **Shoebox** in the sidebar.
2. Tap folders to open them; tap the path at the top to go back.
3. **New folder** (top bar) creates a folder where you are.
4. The menu (⋮) of a picture or folder renames, moves or deletes it. Moving shows the folders to pick from, with a search box.

The same works from automations and scripts with the [actions](actions.md), for example to sort new phone pictures into a folder per month:

```yaml
alias: Sort phone pictures
sequence:
  - action: shoebox.list
    data:
      pattern: "local/Phone/*"
      type: image
    response_variable: found
  - action: shoebox.create_folder
    data:
      path: "local/Family/{{ now().strftime('%Y-%m') }}"
  - repeat:
      for_each: "{{ found['items'] | map(attribute='path') | list }}"
      sequence:
        - action: shoebox.move
          data:
            path: "{{ repeat.item }}"
            to: "local/Family/{{ now().strftime('%Y-%m') }}"
```

## Upload from your phone

1. In the Shoebox panel, open the folder the pictures belong in.
2. Tap **Upload** (top bar) and pick the pictures; several at once is fine.
3. The list at the bottom shows each upload. A picture with the name of an existing file is stored next to it as `name-1.jpg`; nothing is overwritten.

On a computer, drag the files onto the panel instead.

## Fix sideways photos and crop

1. In the Shoebox panel, tap the picture, then **Edit** (the pencil in its top bar).
2. Turn it with **Rotate left** or **Rotate right**.
3. Choose an **Aspect ratio**, such as *16:9* or *Free*, and draw the box. The preview shows the result. A display with an uncommon shape, such as 800 × 480 (5:3), crops with *Free*, or use `fit: cover` on the device URL and let it cut the overhang.
4. Tap **Save**: the turn and the crop are saved together. **Cancel** drops both; **Reset** removes the crop, saved with Save.

Only JPEG pictures can be edited; see [editing](editing.md) for how the turn and crop are stored.

## Slideshow on a dashboard

1. **Settings → Devices & services → Shoebox Media Manager → Add rotation**: name *Living room*, pattern `local/Family/**`.
2. Add a card to the dashboard on the tablet, TV or browser:

   ```yaml
   type: picture-entity
   entity: image.living_room
   show_name: false
   show_state: false
   ```

3. Move on every 10 minutes while the house is awake:

   ```yaml
   alias: Living room slideshow
   triggers:
     - trigger: time_pattern
       minutes: /10
   conditions:
     - condition: time
       after: "07:00:00"
       before: "23:00:00"
   actions:
     - action: button.press
       target:
         entity_id: button.living_room_next
   ```

## ESPHome photo frame

1. Add a rotation, for example *Living room*.
2. Create a user without admin rights for devices and a long-lived token for it: see [a user for devices](displays.md#a-user-for-devices).
3. Build the ESPHome device with `online_image` pointing at the rotation's URL, sized for the display: see the [ESPHome example](displays.md#esphome).
4. Add the automation from that example, so the frame downloads a new picture when the rotation moves on.
5. Move the rotation on as in the [slideshow](#slideshow-on-a-dashboard), or with its own schedule.

## Pictures by time of day or season

Make a rotation per mood and choose between them.

1. Put the pictures in folders, such as `local/Moods/Day` and `local/Moods/Night`, and add rotations *Day* (`local/Moods/Day/**`) and *Night* (`local/Moods/Night/**`).
2. Show the one that fits:

   ```yaml
   type: conditional
   conditions:
     - condition: state
       entity: sun.sun
       state: above_horizon
   card:
     type: picture-entity
     entity: image.day
     show_name: false
     show_state: false
   ```

   and a second conditional card with `state_not: above_horizon` showing `image.night`.

For seasons, keep a folder per season and change the rotation's patterns in **Settings** when the season turns, or keep the seasons in folders and let an automation move pictures into `local/Seasons/Now` with the [move action](actions.md#move).

## Photo of the day

1. Add a rotation *Photo of the day* with the patterns you like.
2. Each morning, move it on and send the picture to your phone:

   ```yaml
   alias: Photo of the day
   triggers:
     - trigger: time
       at: "07:30:00"
   actions:
     - action: button.press
       target:
         entity_id: button.photo_of_the_day_next
     - action: notify.mobile_app_my_phone
       data:
         message: "{{ state_attr('image.photo_of_the_day', 'file') }}"
         data:
           image: /api/image_proxy/image.photo_of_the_day
   ```

## Kids' artwork wall

1. In the Shoebox panel, open **My media** and create a folder `Kids art` with **New folder**.
2. Photograph new drawings with your phone and [upload](#upload-from-your-phone) them into that folder, cropping in the panel if needed.
3. Add a rotation *Artwork* with the pattern `local/Kids art/**` and put it on a wall tablet as in the [slideshow](#slideshow-on-a-dashboard), or on a [photo frame](#esphome-photo-frame).

New drawings join the rotation as soon as they are uploaded.
