---
id: TASK-59
title: 'Device URL: accept the image entity''s access token'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-17T14:59:00Z'
updated_date: '2026-11-17T15:11:00Z'
labels:
  - integration
  - security
dependencies: []
priority: high
type: feature
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Why
Devices such as ESPHome displays fetch a rotation's picture from `/api/shoebox/image/<entity_id>?width=&height=&fit=`, which today needs a long-lived access token (a "Displays" user, a token created by hand, stored on the device or its build machine). Home Assistant already gives every image entity a short-lived key: its `entity_picture` attribute is `/api/image_proxy/<entity_id>?token=<token>`, and the token rotates every 5 minutes. HA's own image proxy accepts that token instead of a login. A device can read the attribute over the ESPHome API (`homeassistant` text sensor with `attribute: entity_picture`). But the image proxy only serves the entity's own size (fitted inside 1280 x 1280), not the device's size or `fit: cover`.

If Shoebox's device URL accepted the same token, a device would get its exact size without any long-lived token, user or secret.

## How (homeassistant/components/image/__init__.py, ImageView._authenticate_request; the same in 2026.10.4 and 2026.11.1)
- `DeviceImageView`: `requires_auth = False`, and authenticate the way HA's `ImageView` does: `request[KEY_AUTHENTICATED] or request.query.get("token") in image_entity.access_tokens`, where `image_entity` is the rotation's image entity, found through the image component (as `ImageView` does, not only the registry entry).
- The token opens only that entity: a token of another image entity is refused.
- Unknown entity: 404 when authenticated, 401 otherwise (as HA does, so the URL does not tell whether an entity exists).
- A failed request that carried an `Authorization` header: 401, so HA's ban middleware counts it as a wrong login. A request with only an expired or wrong `token`: 403, not counted as a login attempt (as HA's ImageView does for expired signed or query-token URLs).
- Never log the token (the request URL holds it): no URL in Shoebox's log lines for this view.
- Width, height, fit, ETag and If-None-Match are unchanged.

Changes how a URL devices use is authenticated: agreed by the user (this ticket is theirs).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GET /api/shoebox/image/image.<rotation>?token=<current entity token>&width=640&height=800&fit=cover returns the prepared picture without an Authorization header
- [x] #2 The previous token also works until HA drops it (HA keeps the last two); an older or made-up token is refused, and so is a token that belongs to a different image entity
- [x] #3 Bearer tokens and logged-in users keep working as before
- [x] #4 Refusals follow HA's ImageView: unknown entity 404 when authenticated, 401 otherwise; a failed request with an Authorization header 401 (counted by the ban middleware), without one 403 (not counted)
- [x] #5 The token never appears in Shoebox's logs
- [x] #6 Tests cover the cases above (unit, and against a real HA where the repo runs those)
- [x] #7 docs/displays.md and docs/security.md: the token first for devices that talk to HA (ESPHome), the long-lived token as the fallback for devices that cannot read entity attributes. ESPHome example: a homeassistant text sensor with attribute: entity_picture, take the token= value, set_url on the online_image with ?token=…&width=…&height=…&fit=cover, then update; and a note to keep the homeassistant and online_image loggers at level INFO so the token is not written to the device log
<!-- AC:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [ ] #1 `mise run check` passes
- [ ] #2 New or changed behaviour is covered by tests
- [ ] #3 README and AGENTS.md match the change
<!-- DOD:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
DeviceImageView: requires_auth False, authenticated as ImageView (2026.10.4 and 2026.11.1 alike): the entity from the image component, ours by its registry entry; logged in, or ?token= in its access_tokens. Unknown or not ours: 404 logged in, else 401. Refused with an Authorization header 401 (ban counting), without 403. No logging in the view. Tests: token with size and fit, previous token after one rotation, refused after two, made-up, missing, another rotation's token, wrong Bearer, unknown entity; no Shoebox log line holds the token; Bearer tests unchanged except no-credentials is now 403 as in HA. Dev HA (2026.10.4): token 200 at 640x800, made-up 403, none 403, Bearer 200, unknown 401. HA's ban middleware logs the URL of a 401 (unknown entity with a token), as for its image proxy: documented in security.md. Docs: displays.md token first with a full ESPHome config (homeassistant text sensors for entity_picture and the state, set_url + update, logger INFO for homeassistant, text_sensor, online_image, http_request), long-lived variant kept; quick-start, use-cases, security, architecture, troubleshooting (403). The ESPHome config passes esphome config 2026.10.2; not compiled or run on hardware.
<!-- SECTION:NOTES:END -->
