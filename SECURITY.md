# Security Policy

## Supported versions

Only the latest released version of this integration receives security
updates. Please update to the newest release before reporting an issue.

| Version | Supported |
| ------- | --------- |
| 2.2.x   | Yes       |
| < 2.2   | No        |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Report privately through GitHub:
[Security → Report a vulnerability](https://github.com/HuisAutomatisering/tascam_bdmp4k/security/advisories/new).

You can expect an acknowledgement within 14 days. Because this is a
hobby project maintained in spare time, fixes are made on a best-effort
basis; credit is given in the release notes unless you prefer otherwise.

## Security model

Understanding what this integration does helps to judge impact:

- It speaks the Tascam BD-MP4K control protocol over **plain TCP on port
  9030** on the local network. The protocol has **no authentication and
  no encryption** — this is a property of the device, not of this
  integration. Anyone with network access to the player can control it.
- **Keep the player on a trusted or isolated (V)LAN.** Never expose port
  9030 to the internet.
- The integration stores only the host, port and optional MAC address in
  the Home Assistant config entry. No credentials are involved.
- Wake-on-LAN sends a UDP broadcast magic packet on the local network
  when the optional MAC address is configured.
- The integration has **no runtime Python dependencies** and makes no
  outbound internet connections.

## Scope

In scope: vulnerabilities in this integration's code, such as
injection through device responses, unsafe handling of config entry
data, or denial of service triggered by malformed protocol messages.

Out of scope: the lack of authentication in the Tascam control protocol
itself, and issues in Home Assistant core or HACS (report those to
their own projects).
