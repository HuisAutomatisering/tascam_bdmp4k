# Changelog

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
