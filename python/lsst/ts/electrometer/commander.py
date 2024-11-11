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
        self.timeout: int = 5
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

    async def send_command(self, msg, has_reply, timeout=None) -> None | str:
        if self.connected:
            if timeout is None:
                timeout = self.timeout
            else:
                timeout = timeout
            async with self.lock:
                self.log.debug(f"sending command {msg}")
                await self.client.write_str(msg)
                if self.brand == "Keysight":
                    async with asyncio.timeout(timeout):
                        echo = await self.client.read_str()
                        self.log.debug(f"echo is {echo}")
                if has_reply:
                    async with asyncio.timeout(timeout):
                        try:
                            reply = b""
                            byte = b""
                            while not reply.endswith(self.client.terminator):
                                byte = await self.client.read(1024)
                                reply += byte
                            reply = reply.rstrip(self.client.terminator).decode(
                                self.client.encoding
                            )
                            # reply = await self.client.read_str()
                            self.log.debug(f"reply is {reply[:100]}")
                        except asyncio.IncompleteReadError as e:
                            self.log.exception(f"{e.partial=}")
                        except asyncio.LimitOverrunError as loe:
                            self.log.exception(f"{loe.consumed=}")
                    return reply
        else:
            raise RuntimeError("Client is not connected.")

    def configure(self, config):
        self.hostname = config.hostname
        self.port = config.port
        self.timeout = config.timeout
