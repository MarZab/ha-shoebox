# Shoebox documentation

Shoebox manages the pictures in Home Assistant's media folder and shows them as rotating pictures. Start with the [README](../README.md) for installation, then the [quick start](quick-start.md).

## Using Shoebox

| Page | What you learn |
|------|----------------|
| [Quick start](quick-start.md) | A rotation on a dashboard, with screenshots, and an ESPHome display |
| [Use cases](use-cases.md) | Step-by-step recipes: organizing, uploading, slideshows, photo frames, notifications |
| [Configuration](configuration.md) | Adding Shoebox, its options, and removing it |
| [Rotations](rotations.md) | How rotations pick pictures: patterns, exclusions, order |
| [Entities](entities.md) | The image and Next button of each rotation |
| [Actions](actions.md) | Every action, its fields and its response |
| [Displays](displays.md) | Dashboards, notifications, the media browser and devices such as ESPHome |
| [Editing](editing.md) | How rotate and crop are stored, and which apps show them |
| [Panel](panel.md) | The Shoebox sidebar panel |
| [Cache](cache.md) | Prepared pictures: where they live and how big the cache gets |
| [Troubleshooting](troubleshooting.md) | Common problems and where to look |

## Actions and entities

| | What it does | Reference |
|---|---|---|
| `shoebox.list` | Lists files and folders that match a pattern | [actions](actions.md#list) |
| `shoebox.create_folder` | Creates a folder | [actions](actions.md#create_folder) |
| `shoebox.move` | Moves a file or folder into another folder | [actions](actions.md#move) |
| `shoebox.rename` | Renames a file or folder | [actions](actions.md#rename) |
| `shoebox.delete` | Deletes a file or folder | [actions](actions.md#delete) |
| `shoebox.rotate` | Turns a JPEG picture | [actions](actions.md#rotate) |
| `shoebox.crop` | Crops a JPEG picture | [actions](actions.md#crop) |
| `image.<rotation>` | The rotation's current picture | [entities](entities.md#image) |
| `button.<rotation>_next` | Moves the rotation to its next picture | [entities](entities.md#next-button) |

The actions are for administrators. Paths start with the name of a media folder: `local` is My media, so a picture there is `local/Family/beach.jpg`.

## Working on Shoebox

| Page | What you learn |
|------|----------------|
| [Development](development.md) | Tools, tasks, the local Home Assistant, checking the panel |
| [Architecture](architecture.md) | Modules, data flow, storage and the reasons behind the design |
| [Security](security.md) | What is kept inside the media folders, and who may do what |
| [Testing](testing.md) | How the tests are laid out, and the fixtures |
| [Release](release.md) | Versions and releases through HACS |
