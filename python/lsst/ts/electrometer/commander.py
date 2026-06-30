# This file is part of ts_electrometer.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__all__ = ["Commander"]

import asyncio
import logging

from lsst.ts import tcpip

LIMIT = 2**16
DEFAULT_TIMEOUT = 240
RETRY_DELAY = 1
RECONNECTION_DELAY = 30
NUMBER_OF_RETRIES = 10


class Commander:
    """Implement communication with the electrometer.

    Parameters
    ----------
    log : `logging.Logger` or `None`, optional
        Logger for command and connection messages. If `None`, a logger named
        for this class is created.
    brand : `str` or `None`, optional
        Electrometer brand. Supported values are ``"Keithley"`` and
        ``"Keysight"``.

    Attributes
    ----------
    log : `logging.Logger`
        The log for this class.
    lock : `asyncio.Lock`
        Lock that serializes connection and command transactions.
    hostname : `str`
        The hostname or IP address for the electrometer.
    port : `int`
        The port of the electrometer.
    timeout : `int`
        Default command timeout, in seconds.
    long_timeout : `int`
        Longer timeout for operations that need it.
    brand : `str` or `None`
        Electrometer brand.
    client : `lsst.ts.tcpip.Client`
        TCP/IP client used to communicate with the electrometer.
    """

    def __init__(self, log: None | logging.Logger = None, brand: str | None = None) -> None:
        # Create a logger if none were passed during the instantiation of
        # the class
        self.log: None | logging.Logger = None
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.lock: asyncio.Lock = asyncio.Lock()
        self.hostname: str = tcpip.LOCAL_HOST
        self.port: int = 9999
        self.timeout: int = DEFAULT_TIMEOUT
        self.long_timeout: int = 30
        self.brand: str | None = brand
        self.client: tcpip.Client = tcpip.Client(host="", port=None, log=log)

    @property
    def connected(self) -> bool:
        """Whether the TCP/IP client is connected."""
        return self.client.connected

    async def connect(self) -> None:
        """Connect to the electrometer."""
        async with self.lock:
            await self._connect()

    async def disconnect(self) -> None:
        """Disconnect from the electrometer."""
        async with self.lock:
            await self._disconnect()

    async def _disconnect(self) -> None:
        """Disconnect without acquiring the transaction lock."""
        await self.client.close()
        self.client = tcpip.Client(host="", port=None, log=self.log)

    async def _connect(self) -> None:
        """Connect without acquiring the transaction lock.

        Raises
        ------
        RuntimeError
            If the brand is unsupported or a connection cannot be established
            after all retry attempts.
        """
        for _ in range(NUMBER_OF_RETRIES):
            match self.brand:
                case "Keysight":
                    self.client = tcpip.Client(
                        host=self.hostname,
                        port=self.port,
                        name=f"{self.brand} Client",
                        log=self.log,
                        encoding="latin_1",
                        limit=LIMIT,
                    )
                case "Keithley":
                    self.client = tcpip.Client(
                        host=self.hostname,
                        port=self.port,
                        name=f"{self.brand} Client",
                        log=self.log,
                        terminator=b"\r",
                        limit=LIMIT,
                    )
                case _:
                    raise RuntimeError(f"{self.brand=} is not supported.")
            try:
                await self.client.start_task
            except ConnectionRefusedError:
                self.log.exception("Connection refused. Closing client and trying again.")
                await self._disconnect()
                await asyncio.sleep(RECONNECTION_DELAY)
            else:
                break
        if not self.client.connected:
            raise RuntimeError("Not able to connect after retrying.")
        if self.brand == "Keysight":
            # ignore welcome message
            try:
                await self.client.read_str()
            except asyncio.IncompleteReadError as e:
                self.log.exception(f"{e.partial=}")

    async def _read_reply_chunked(self, timeout: float) -> bytes:
        """Read a terminator-delimited reply in chunks.

        Parameters
        ----------
        timeout : `float`
            Maximum time to wait for a complete reply, in seconds.

        Returns
        -------
        reply : `bytes`
            Reply bytes without the terminator.

        Raises
        ------
        ConnectionError
            If the connection closes before a complete reply is received.
        asyncio.TimeoutError
            If the reply is not complete before ``timeout`` expires.
        """
        reply = bytearray()
        terminator = self.client.terminator

        async with asyncio.timeout(timeout):
            while not reply.endswith(terminator):
                chunk = await self.client.read(4096)
                if not chunk:
                    raise ConnectionError("Connection closed while reading reply.")
                reply.extend(chunk)

        return bytes(reply).removesuffix(terminator)

    async def _discard_stale_reply(self, timeout: float = 0.1) -> None:
        """Discard one stale reply if it is immediately available.

        Parameters
        ----------
        timeout : `float`, optional
            Maximum time to wait for a stale reply, in seconds.
        """
        try:
            await self._read_reply_chunked(timeout)
        except (asyncio.TimeoutError, asyncio.IncompleteReadError, ConnectionError):
            pass

    async def _send_command_once(
        self, msg: str, has_reply: bool, timeout: float, discard_stale_reply: bool = False
    ) -> None | str:
        """Send one command transaction without retrying.

        Parameters
        ----------
        msg : `str`
            Command to send.
        has_reply : `bool`
            Whether a reply is expected.
        timeout : `float`
            Reply timeout, in seconds.
        discard_stale_reply : `bool`, optional
            Whether to drain one stale reply before sending the command.

        Returns
        -------
        reply : `str` or `None`
            Command reply if ``has_reply`` is true; otherwise `None`.
        """
        if not self.connected:
            await self._connect()

        if discard_stale_reply:
            await self._discard_stale_reply()

        await self.client.write_str(msg)
        # Ignore echo sent by Keysight. The mock Keysight echo is not
        # terminator-delimited, so keep the original read behavior here.
        if self.brand == "Keysight":
            async with asyncio.timeout(timeout):
                await self.client.read_str()

        if not has_reply:
            return None

        reply = await self._read_reply_chunked(timeout)
        return reply.decode(self.client.encoding)

    async def send_command(self, msg: str, has_reply: bool, timeout: None | float = None) -> None | str:
        """Send command to the device and receive reply if expected.

        Parameters
        ----------
        msg : str
            The command to be sent.
        has_reply : bool
            Does the command expect a reply?
        timeout : None | float, optional
            How long to wait before timing out reply, by default None.

        Returns
        -------
        None | str
            Return the reply if expected else return None.
        """
        timeout = self.timeout if timeout is None else timeout
        async with self.lock:
            last_exception = None
            discard_stale_reply = False
            for attempt in range(NUMBER_OF_RETRIES):
                try:
                    return await self._send_command_once(
                        msg=msg,
                        has_reply=has_reply,
                        timeout=timeout,
                        discard_stale_reply=discard_stale_reply,
                    )
                except (asyncio.TimeoutError, ConnectionError, asyncio.IncompleteReadError) as e:
                    last_exception = e
                    self.log.exception(
                        f"Command attempt {attempt + 1}/{NUMBER_OF_RETRIES} failed; "
                        f"reconnecting in {RECONNECTION_DELAY} second(s)."
                    )
                    await self._disconnect()
                    await asyncio.sleep(RECONNECTION_DELAY)
                    discard_stale_reply = True
                    if reply := getattr(e, "partial", b""):
                        self.log.debug(f"Discarding partial reply before retrying: {reply!r}")
            raise TimeoutError(
                f"Command failed after {NUMBER_OF_RETRIES} attempts: {msg}"
            ) from last_exception

    def configure(self, config):
        """Configure the network endpoint.

        Parameters
        ----------
        config : object
            Object with ``hostname``, ``port``, and ``timeout`` attributes.
        """
        self.hostname = config.hostname
        self.port = config.port
        self.timeout = config.timeout
