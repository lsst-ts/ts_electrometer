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
RECONNECTION_DELAY = 1
NUMBER_OF_RETRIES = 10


class Commander:
    """Implement communication with the electrometer.

    Attributes
    ----------
    log : logging.Logger
        The log for this class.
    reader : asyncio.StreamReader
        The reader for the tcpip stream.
    writer : asyncio.StreamWriter
        The writer for the tcpip stream.
    reply_terminator : bytes
        The reply termination character.
    command_terminator : str
        The command termination character.
    lock : asyncio.Lock
        The lock for protecting reading and writing handling.
    host : str
        The hostname or ip address for the electrometer.
    port : int
        The port of the electrometer.
    timeout : int
        The amount of time to wait until a message is not received.
    connected : bool
        Whether the electrometer is connected or not.
    """

    def __init__(
        self, log: None | logging.Logger = None, brand: str | None = None
    ) -> None:
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
        self.timeout: int = 10
        self.long_timeout: int = 30
        self.brand: str | None = brand
        self.client: tcpip.Client = tcpip.Client(host="", port=None, log=log)

    @property
    def connected(self) -> bool:
        return self.client.connected

    async def connect(self) -> None:
        """Connect to the electrometer"""
        if self.brand == "Keysight":
            self.client = tcpip.Client(
                host=self.hostname,
                port=self.port,
                name=f"{self.brand} Client",
                log=self.log,
                encoding="latin_1",
                limit=LIMIT,
            )
        else:
            self.client = tcpip.Client(
                host=self.hostname,
                port=self.port,
                name=f"{self.brand} Client",
                log=self.log,
                terminator=b"\r",
                limit=LIMIT,
            )
        await self.client.start_task
        if self.brand == "Keysight":
            # ignore welcome message
            async with self.lock:
                try:
                    await self.client.read_str()
                except asyncio.IncompleteReadError as e:
                    self.log.exception(f"{e.partial=}")

    async def disconnect(self) -> None:
        """Disconnect from the electrometer."""
        await self.client.close()
        self.client = tcpip.Client(host="", port=None, log=self.log)

    async def send_command(
        self, msg: str, has_reply: bool, timeout: None | float = None
    ) -> None | str:
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
        if not timeout:
            timeout = self.timeout
        else:
            timeout = timeout
        async with self.lock:
            if not self.connected:
                await self.connect()
            await self.client.write_str(msg)
            if self.brand == "Keysight":
                async with asyncio.timeout(DEFAULT_TIMEOUT):
                    await self.client.read_str()
            if has_reply:
                async with asyncio.timeout(DEFAULT_TIMEOUT):
                    reply = b""
                    while not reply.endswith(self.client.terminator):
                        for _ in range(NUMBER_OF_RETRIES):
                            try:
                                byte = await self.client.read(1)
                                if byte:
                                    reply += byte
                                    break
                            except ConnectionError:
                                self.log.exception(
                                    f"Connection lost...Reconnecting in {RECONNECTION_DELAY} second(s)."
                                )
                                await self.disconnect()
                                await asyncio.sleep(RECONNECTION_DELAY)
                                await self.connect()
                                continue
                            except Exception:
                                self.log.exception(
                                    f"Getting reply failed... trying again in {RETRY_DELAY} second(s)."
                                )
                                await asyncio.sleep(RETRY_DELAY)
                reply = reply.rstrip(self.client.terminator).decode(
                    self.client.encoding
                )
                return reply
            else:
                return None

    def configure(self, config):
        self.hostname = config.hostname
        self.port = config.port
        self.timeout = config.timeout
