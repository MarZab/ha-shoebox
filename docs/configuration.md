# Configuration

Shoebox is set up in the UI. There is nothing to put in `configuration.yaml`; a `shoebox:` entry there only raises a repair asking to remove it.

## Adding Shoebox

1. Install Shoebox through HACS and restart Home Assistant.
2. Go to **Settings → Devices & services → Add integration** and choose **Shoebox Media Manager**.
3. Choose the media folders Shoebox works on. **My media** (`local`, which is `/media` on Home Assistant OS) is chosen already; more folders come from `media_dirs` in `configuration.yaml`:

   ```yaml
   homeassistant:
     media_dirs:
       local: /media
       nas: /mnt/photos
   ```

   Paths in Shoebox start with the folder's name: `local/Family/beach.jpg`, `nas/2024/beach.jpg`. Folders not chosen stay out of Shoebox's reach.

Shoebox can be added once. If a chosen folder does not exist or is no longer configured, setup waits and retries.

Rotations are added afterwards, from the same page: see [rotations](rotations.md).

## Options

**Settings → Devices & services → Shoebox Media Manager → Configure**:

| Option | Default | What it does |
|--------|---------|--------------|
| Media folders | My media | The media folders Shoebox works on; at least one. Removing a folder here only takes it out of Shoebox's reach: its files stay. Rotations whose patterns name it find no pictures there any more. |
| Cache size | 512 MB | How much space prepared pictures may take. When the cache grows past this, the pictures used least recently are removed. **0** turns the cache off: nothing is stored and pictures are prepared on every request. See [cache](cache.md). |
| Clear the cache | off | Removes every prepared picture when you save. They are made again when needed. The dialog shows how many pictures the cache holds now. |
| Show in sidebar | on | The Shoebox panel for administrators. Off removes it for everyone; actions, entities and device pictures keep working. To hide the panel only for yourself, edit your own sidebar instead. |

Changes apply when you save; no restart is needed.

## Removing Shoebox

1. Go to **Settings → Devices & services → Shoebox Media Manager**, open the menu (⋮) and choose **Delete**.
2. To remove the files as well, uninstall Shoebox in HACS and restart Home Assistant.

What stays and what goes:

| Stays | Goes |
|-------|------|
| Every file in the media folders, including turns and crops stored in your pictures | The rotations, their devices and entities |
| | Where each rotation was (its position) |
| | The cache of prepared pictures |

Automations, scripts and dashboards that use Shoebox entities or actions stop working; remove or change them.
