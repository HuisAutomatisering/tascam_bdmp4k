# Tascam BD-MP4K — Home Assistant integration

[![hassfest](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/hassfest.yml/badge.svg)](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/hassfest.yml)
[![HACS validation](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/hacs.yml/badge.svg)](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/hacs.yml)
[![CodeQL](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/codeql.yml/badge.svg)](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/codeql.yml)
[![Ruff](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/ruff.yml/badge.svg)](https://github.com/HuisAutomatisering/tascam_bdmp4k/actions/workflows/ruff.yml)

[![HACS custom](https://img.shields.io/badge/HACS-custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Release](https://img.shields.io/github/v/release/HuisAutomatisering/tascam_bdmp4k?display_name=tag)](https://github.com/HuisAutomatisering/tascam_bdmp4k/releases)

Control a **Tascam BD-MP4K** professional Blu-ray player from Home
Assistant over its Ethernet control protocol (TCP port 9030).

## Features

- **Media player**: play, pause, stop, next/previous chapter, standby,
  power on via Wake-on-LAN (optional), media position and duration
  (derived from elapsed + remaining time).
- **Sensors**: disc status, playback status, elapsed time, remaining
  time, current chapter, current title. Times are numeric duration
  sensors, so they work in statistics and templates.
- **Buttons**: tray open/close, home, enter, return, top menu, popup
  menu, setup menu, display info, next subtitle, mute on/off, power off.
- **Real-time updates**: status changes pushed by the player (including
  ones triggered by its own remote control) appear instantly.
- **English and Dutch** translations.

## Installation

### HACS (recommended)

1. In HACS, open the three-dot menu → **Custom repositories**.
2. Add `https://github.com/HuisAutomatisering/tascam_bdmp4k`
   with category **Integration**.
3. Download **Tascam BD-MP4K** and restart Home Assistant.

### Manual

1. Copy `custom_components/tascam_bdmp4k` into your Home Assistant
   `config/custom_components/` directory.
2. Restart Home Assistant.

### Configuration

Go to **Settings → Devices & Services → Add Integration** and search for
**Tascam BD-MP4K**. Enter the IP address of the player; the port is
9030 and fixed by the device.

Optionally enter the player's **MAC address** to enable power on via
Wake-on-LAN. Enable network standby / Wake-on-LAN on the player itself
as well, otherwise the magic packet has no effect.

## How it works

The BD-MP4K protocol requires that the TCP connection is held open
continuously and allows **only one client** at a time. The integration
therefore maintains a single shared connection for all entities and
enforces the 30 ms minimum command interval from the specification.

Status notifications pushed by the player are processed in real time, so
play, pause and disc changes appear immediately. Polling (every 10
seconds) remains as a fallback and for elapsed and remaining time, which
the player does not push.

## Limitations

- **Power on over Ethernet is not supported by the protocol** — the
  specification prescribes Wake-on-LAN, which this integration uses.
- **Only one controller can be connected at a time.** Disconnect other
  control systems (Bitfocus Companion, Crestron, etc.) while using this
  integration.
- The player replies `nack` to status requests that do not apply to the
  current mode (for example remaining time while stopped). Those values
  show as *unknown*; this is normal.

## Troubleshooting

Enable debug logging to see every command, reply and notification:

```yaml
logger:
  default: info
  logs:
    custom_components.tascam_bdmp4k: debug
```

Entities going unavailable now and then usually means something else is
claiming the player's single client slot, or the player was powered off.

## Security

The control protocol has no authentication or encryption. Keep the
player on a trusted network and never expose port 9030 to the internet.
See [SECURITY.md](SECURITY.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Bug reports and pull requests
are welcome.

A standalone, Home Assistant independent Python client for the same
protocol is available as
[aiotascam](https://github.com/HuisAutomatisering/aiotascam), ready for
anyone who wants to build on it.

## License

MIT — see [LICENSE](LICENSE).

## Disclaimer

This integration is not affiliated with TEAC Corporation. Tascam, TEAC
and BD-MP4K are trademarks of their respective owners. See
[Brand/](Brand/) for how logos are handled.
