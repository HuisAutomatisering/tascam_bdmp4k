# Changelog

## 2.4.0

- Aligned with the Bronze tier of the Home Assistant integration quality scale; the status
  per rule is recorded in `quality_scale.yaml`
- Added tests for the config flow, setup, polling, push notifications, the entities and the
  protocol client, plus a Tests workflow and badge
- The config flow explains each field, re-fills the form after an error, ignores an empty
  MAC address, and reports unexpected errors instead of failing silently
- The HACS brands check is enabled again: the icon and logo come from the
  home-assistant/brands repository
- Fixed: a message split across two network reads could be lost, which caused a missed reply
  and a retry; a status notification running straight into a reply is now told apart too
- The media position now carries the time it was read from the player
- Closing the connection now waits for the reader task to stop
- Moved the Ruff configuration to `ruff.toml` (line length 100) and reformatted the code
- README: entity table, configuration fields, removal instructions and a quality scale section

## 2.3.1

- Added the My Home Assistant "Open in HACS" badge, so the repository can
  be added to HACS with one click
- Added a My Home Assistant link for starting the config flow
- Pinned the workflow status badges to the main branch

## 2.3.0

- Renamed entities so that Home Assistant's alphabetical ordering groups
  them logically: tray controls, menu controls, mute and the time
  sensors now sit together
- Added manual trigger (workflow_dispatch) to the CodeQL workflow

## 2.2.1

- Reformatted the integration code so it passes `ruff format --check`
- Pinned the Ruff version in CI and `pyproject.toml` so a future Ruff
  release cannot break the check unexpectedly
- Updated `actions/checkout` to v5

## 2.2.0

- Added hassfest, HACS, CodeQL and Ruff validation workflows
- Added `SECURITY.md` with a security policy and threat model
- Added Dependabot for monthly GitHub Actions updates
- Added issue template and contributing guide
- Added `Brand/` folder describing how logos are handled
- Added entity icons (`icons.json`) and translated sensor states in
  English and Dutch
- Removed runtime assertions and silent exception handling from the
  protocol layer; all failure paths are now logged
- Corrected `iot_class` to `local_push`

## 2.1.2

- Commands that fail to connect are retried once after a short delay
- Commands sent while the player is off are logged at debug level

## 2.1.1

- Fixed a tokenizer issue where an `ack` arriving in the same TCP read
  as a status notification could be swallowed

## 2.1.0

- Added power on via Wake-on-LAN (optional MAC address)
- Switched to push-based updates with a persistent listener task

## 2.0.3

- Fixed a crash on unknown disc/playback status codes
- Media player reports "off" instead of "unavailable" when powered off

## 2.0.2

- Reconnect and retry once before marking the device unavailable
- Status notifications are acknowledged as the specification requires

## 2.0.1

- Switched license from GPL-3.0 to MIT

## 2.0.0

- Complete rewrite around a single persistent connection and a
  DataUpdateCoordinator
