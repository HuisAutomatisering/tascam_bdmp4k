# Contributing

Issues and pull requests are welcome. This is a hobby project, so
responses may take a while.

## Reporting problems

Include the integration version, your Home Assistant version, and debug
logs. Enable debug logging by adding this to `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.tascam_bdmp4k: debug
```

The protocol layer logs every command, reply and pushed notification at
debug level, which is usually enough to diagnose an issue.

## Code style

The code follows Home Assistant conventions and is checked with
[Ruff](https://docs.astral.sh/ruff/) (configuration in
`pyproject.toml`), plus `hassfest` and HACS validation. All three run
automatically on every push and pull request.

```bash
ruff check custom_components
ruff format custom_components
```

## Protocol documentation

The TEAC "BD-MP4K RS-232C/ETHERNET Protocol Specification" v1.01 is the
authoritative source. It is copyrighted by TEAC Corporation and is
therefore not included in this repository; it is available from
TEAC/Tascam support.

## Adding commands

Commands and status requests live in `const.py`, mapped exactly as the
specification names them. Entity behaviour lives in `media_player.py`,
`sensor.py` and `button.py`; the connection itself is handled entirely
in `protocol.py` and should not be duplicated elsewhere — the player
accepts only one client at a time.
