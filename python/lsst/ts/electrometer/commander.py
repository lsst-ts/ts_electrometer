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

import asyncio
import logging
import typing

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

    def __init__(self, log: None | logging.Logger = None) -> None:
        # Create a logger if none were passed during the instantiation of
        # the class
        self.log: None | logging.Logger = None
        if log is None:
            self.log = logging.getLogger(type(self).__name__)
        else:
            self.log = log.getChild(type(self).__name__)

        self.reader: None = None
        self.writer: None = None
        self.reply_terminator: bytes = b"\r"
        self.command_terminator: str = "\r"
        self.lock: asyncio.Lock = asyncio.Lock()
        self.host: str = tcpip.LOCAL_HOST
        self.port: int = 9999
        self.timeout: int = 2
        self.long_timeout: int = 30
        self.connected: bool = False

    async def connect(self) -> None:
        """Connect to the electrometer"""
        async with self.lock:
            try:
                connect_task = asyncio.open_connection(
                    host=self.host, port=int(self.port)
                )
                self.reader, self.writer = await asyncio.wait_for(
                    connect_task, timeout=self.long_timeout
                )
            except Exception as e:
                raise RuntimeError(
                    f"Failed to connect. {self.host=} {self.port=}: {e!r}"
                )
            self.connected = True

    async def disconnect(self) -> None:
        """Disconnect from the electrometer."""
        async with self.lock:
            if self.writer is None:
                return
            try:
                await tcpip.close_stream_writer(self.writer)
            except Exception:
                self.log.exception("Disconnect failed, continuing")
            finally:
                self.writer = None
                self.reader = None
                self.connected = False

    async def send_command(
        self, msg: str, has_reply: bool = False, timeout: typing.Optional[int] = None
    ) -> str:
        """Send a command to the electrometer and read reply if has one.

        Parameters
        ----------
        msg : `str`
            The message to send.
        has_reply : `bool`
            Does the command expect a reply.

        Returns
        -------
        reply
        """

        async with self.lock:
            msg = msg + self.command_terminator
            msg = msg.encode("ascii")
            if self.writer is not None:
                self.log.debug(f"Commanding using: {msg}")
                self.writer.write(msg)
                await self.writer.drain()
                if has_reply:
                    reply = await asyncio.wait_for(
                        self.reader.readuntil(self.reply_terminator),
                        timeout=self.timeout if timeout is None else timeout,
                    )
                    self.log.debug(f"reply={reply}")
                    reply = reply.decode().strip()
                    return reply
                return None
            else:
                raise RuntimeError("CSC not connected.")
