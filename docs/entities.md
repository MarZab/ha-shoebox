# Entities

Every [rotation](rotations.md) is a device with two entities. A rotation named *Living room* has:

| Entity | ID |
|--------|----|
| [Image](#image) | `image.living_room` |
| [Next button](#next-button) | `button.living_room_next` |

## Image

The rotation's current picture, prepared to fit inside 1280 × 1280 pixels with the [edits](editing.md) applied.

Its state is the time the picture last changed: when the rotation moved on, or when its current picture was turned or cropped. Dashboards fetch the new picture when the state changes.

Attributes:

| Attribute | Example | Meaning |
|-----------|---------|---------|
| `patterns` | `["local/Family/**"]` | The rotation's patterns |
| `pattern` | `local/Family/**` | The pattern in use (see [fallbacks](rotations.md#fallbacks)); empty when nothing matches |
| `file` | `local/Family/2024 Summer/beach.jpg` | The current picture |
| `position` | `2` | Its place in the order, from 1; 0 before the first Next |
| `count` | `48` | How many pictures the rotation selects |

The state is `unknown` until Next is pressed the first time.

Use it with a picture entity or picture glance card, in [notifications](displays.md#notifications), or from devices through its [URL](displays.md#devices).

## Next button

Pressing it moves the rotation to its next picture. Press it from a dashboard, or with the `button.press` action in automations and scripts:

```yaml
action: button.press
target:
  entity_id: button.living_room_next
```

There is no timer of its own: an automation decides when the rotation moves on, for example every 10 minutes, at sunrise, or when someone comes home. See [use cases](use-cases.md).
