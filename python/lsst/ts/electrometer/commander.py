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
        self.client = tcpip.Client(
            host=self.hostname,
            port=self.port,
            terminator=b"\r",
            name=f"{self.brand} Client",
            log=self.log,
        )
        await self.client.start_task

    async def disconnect(self) -> None:
        """Disconnect from the electrometer."""
        await self.client.close()
        self.client = tcpip.Client(host="", port=None, log=self.log)

    async def send_command(self, msg, has_reply, timeout) -> None | str:
        async with self.lock:
            await self.client.write_str(msg)
            if self.brand == "Keysight":
                async with asyncio.timeout(timeout):
                    await self.client.read_str()
            if has_reply:
                async with asyncio.timeout(timeout):
                    reply = await self.client.read_str()
                return reply

    def configure(self, config):
        self.hostname = config.hostname
        self.port = config.port
        self.timeout = config.timeout
