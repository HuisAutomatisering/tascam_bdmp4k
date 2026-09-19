"""Async TCP protocol client for the Tascam BD-MP4K.

The BD-MP4K protocol specification requires that the TCP connection is held
open continuously and that only one client connects at a time. This client
keeps a single connection with a background listener task, so unsolicited
status notifications from the player are received and dispatched in real
time (push) while commands and status requests share the same connection.

Protocol notes (RS-232C/Ethernet spec v1.01):
- Commands are ASCII, start with ``!7`` and end with CR (0x0D).
- The device replies ``ack`` (optionally followed by ``+`` and an answer
  such as ``!7SET0011230``) or ``nack``.
- The interval between commands must be at least 30 ms.
- The device pushes status notifications on state changes; the controller
  must reply with ``ack``.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import logging
import re
import time

_LOGGER = logging.getLogger(__name__)

START = "!7"
CR = "\r"
ACK = "ack"
NACK = "nack"

COMMAND_INTERVAL = 0.03  # 30 ms minimum between commands (spec 4.3.6)
RESPONSE_TIMEOUT = 1.0
CONNECT_TIMEOUT = 5.0
FLUSH_TIMEOUT = 0.05  # flush a partial buffer after 50 ms of silence
RETRY_DELAY = 0.5  # pause before retrying a failed command
RETRY_ATTEMPTS = 2  # initial attempt plus one retry

_MESSAGE_RE = re.compile(r"(!7[A-Z0-9]{3}[^!\r\n]*|ack|nack)")


class TascamError(Exception):
    """Base error for Tascam protocol failures."""


class TascamConnectionError(TascamError):
    """Raised when the device cannot be reached."""


class TascamNackError(TascamError):
    """Raised when the device replies with NACK."""


class _Pending:
    """An in-flight command awaiting its reply."""

    def __init__(self, is_request: bool) -> None:
        """Initialize the pending command."""
        self.is_request = is_request
        self.acked = False
        loop = asyncio.get_running_loop()
        self.future: asyncio.Future[str | None] = loop.create_future()


class TascamClient:
    """Maintain a single persistent, push-capable connection."""

    def __init__(self, host: str, port: int) -> None:
        """Initialize the client."""
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._listen_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()
        self._last_command = 0.0
        self._pending: _Pending | None = None
        self._notification_callback: Callable[[str], None] | None = None

    @property
    def connected(self) -> bool:
        """Return True if the connection is open."""
        return self._writer is not None and not self._writer.is_closing()

    def set_notification_callback(
        self,
        callback: Callable[[str], None] | None,
    ) -> None:
        """Register a callback for unsolicited status notifications."""
        self._notification_callback = callback

    async def async_connect(self) -> None:
        """Open the TCP connection and start the listener task."""
        if self.connected:
            return
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port),
                timeout=CONNECT_TIMEOUT,
            )
        except (OSError, TimeoutError) as err:
            self._reader = None
            self._writer = None
            raise TascamConnectionError(
                f"Cannot connect to {self._host}:{self._port}: {err}",
            ) from err
        loop = asyncio.get_running_loop()
        self._listen_task = loop.create_task(self._listen())
        _LOGGER.debug("Connected to %s:%s", self._host, self._port)

    async def async_disconnect(self) -> None:
        """Close the TCP connection and stop the listener task."""
        if (
            self._listen_task is not None
            and self._listen_task is not asyncio.current_task()
        ):
            self._listen_task.cancel()
        self._listen_task = None
        writer = self._writer
        self._reader = None
        self._writer = None
        if writer is not None:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError as err:
                # The socket was already gone; nothing left to close.
                _LOGGER.debug("Error while closing connection: %s", err)
        self._fail_pending(TascamConnectionError("Disconnected"))

    async def async_send(self, command: str) -> str | None:
        """Send a command and return the answer message, if any.

        Returns the ``!7XXX...`` answer for status requests, or None for
        plain control commands that are only acknowledged. A connection
        failure is retried once after a short delay before raising, since
        the player briefly refuses connections around power state changes.
        """
        last_error: TascamConnectionError | None = None
        for attempt in range(RETRY_ATTEMPTS):
            try:
                return await self._async_send_once(command)
            except TascamConnectionError as err:
                last_error = err
                if attempt + 1 >= RETRY_ATTEMPTS:
                    break
                _LOGGER.debug("Retrying %s after failure: %s", command, err)
                await self.async_disconnect()
                await asyncio.sleep(RETRY_DELAY)
        raise TascamConnectionError(str(last_error))

    async def _async_send_once(self, command: str) -> str | None:
        """Send a command once over the shared connection."""
        async with self._lock:
            await self.async_connect()
            await self._respect_interval()
            writer = self._writer
            if writer is None:
                raise TascamConnectionError("Connection lost before sending")
            pending = _Pending(is_request=command.startswith(f"{START}?"))
            self._pending = pending
            try:
                writer.write(f"{command}{CR}".encode("ascii"))
                await writer.drain()
                self._last_command = time.monotonic()
                return await asyncio.wait_for(
                    pending.future,
                    RESPONSE_TIMEOUT,
                )
            except (OSError, TimeoutError) as err:
                await self.async_disconnect()
                raise TascamConnectionError(
                    f"No reply to {command}: {err}",
                ) from err
            finally:
                self._pending = None

    async def _respect_interval(self) -> None:
        """Enforce the 30 ms minimum interval between commands."""
        elapsed = time.monotonic() - self._last_command
        if elapsed < COMMAND_INTERVAL:
            await asyncio.sleep(COMMAND_INTERVAL - elapsed)

    async def _listen(self) -> None:
        """Continuously read the socket and dispatch incoming tokens."""
        reader = self._reader
        if reader is None:
            return
        buffer = ""
        try:
            while True:
                try:
                    if buffer:
                        chunk = await asyncio.wait_for(
                            reader.read(256),
                            timeout=FLUSH_TIMEOUT,
                        )
                    else:
                        chunk = await reader.read(256)
                except TimeoutError:
                    # No more data: the partial tail is a complete token.
                    self._dispatch_buffer(buffer, final=True)
                    buffer = ""
                    continue
                if not chunk:
                    raise TascamConnectionError("Connection closed by device")
                buffer += chunk.decode("ascii", errors="replace")
                buffer = self._dispatch_buffer(buffer, final=False)
        except asyncio.CancelledError:
            raise
        except (TascamError, OSError) as err:
            _LOGGER.debug("Listener stopped: %s", err)
            self._fail_pending(TascamConnectionError(str(err)))
            self._listen_task = None
            writer = self._writer
            self._reader = None
            self._writer = None
            if writer is not None:
                writer.close()

    def _dispatch_buffer(self, buffer: str, final: bool) -> str:
        """Dispatch complete tokens and return the unconsumed tail."""
        tail = ""
        matches = _MESSAGE_RE.findall(buffer)
        if not final and matches:
            last = matches[-1]
            if buffer.endswith(last) and last.startswith(START):
                # Possibly incomplete; hold it until more data or a flush.
                tail = last
                matches = matches[:-1]
        for token in matches:
            self._dispatch(token.strip("\r\n+ "))
        if not final and not matches and not tail:
            # Possibly a partial 'ack'/'nack' or start character.
            tail = buffer[-8:]
        return tail

    def _dispatch(self, token: str) -> None:
        """Route one token to the pending command or the callback."""
        if not token:
            return
        pending = self._pending
        if token == NACK:
            if pending is not None and not pending.future.done():
                pending.future.set_exception(
                    TascamNackError("Device replied NACK"),
                )
            return
        if token == ACK:
            if pending is None or pending.future.done():
                return
            if pending.is_request:
                pending.acked = True
            else:
                pending.future.set_result(None)
            return
        if token.startswith(START):
            if (
                pending is not None
                and pending.is_request
                and pending.acked
                and not pending.future.done()
            ):
                pending.future.set_result(token)
                return
            # Unsolicited status notification: acknowledge it (spec 4.4.3).
            if self._writer is not None:
                self._writer.write(f"{ACK}{CR}".encode("ascii"))
            _LOGGER.debug("Notification: %s", token)
            if self._notification_callback is not None:
                self._notification_callback(token)

    def _fail_pending(self, err: TascamError) -> None:
        """Fail the in-flight command, if there is one."""
        if self._pending is not None and not self._pending.future.done():
            self._pending.future.set_exception(err)
