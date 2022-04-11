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

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.reader = None
        self.writer = None
        self.reply_terminator = b"\n"
        self.command_terminator = "\r"
        self.lock = asyncio.Lock()
        self.host = tcpip.LOCAL_HOST
        self.port = 9999
        self.timeout = 2
        self.connected = False

    async def connect(self):
        """Connect to the electrometer"""
        self.reader, self.writer = await asyncio.open_connection(
            host=self.host, port=int(self.port)
        )
        self.connected = True

    async def disconnect(self):
        """Disconnect from the electrometer."""
        self.reader = None
        if self.writer is not None:
            await tcpip.close_stream_writer(self.writer)
            self.writer = None
        self.connected = False

    async def send_command(self, msg, has_reply=False):
        """Send a command to the electrometer and read reply if has one.

        Parameters
        ----------
        msg
        has_reply

        Returns
        -------
        reply
        """
        msg = msg + self.command_terminator
        msg = msg.encode("ascii")
        if self.writer is not None:
            self.log.debug(f'Commanding using: {msg}')
            self.writer.write(msg)
            await self.writer.drain()
            if has_reply:
                reply = await asyncio.wait_for(
                    self.reader.readuntil(self.reply_terminator), timeout=self.timeout
                )
                self.log.debug(f"reply={reply}")
                reply = reply.decode().strip()
                return reply
            return None
        else:
            raise RuntimeError("CSC not connected.")
