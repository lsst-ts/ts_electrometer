import asyncio
import logging
import socket
import unittest
import unittest.mock

from lsst.ts.electrometer import commander, mock_server


class CommanderIntegrationTestCase(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        if hasattr(self, "cmdr") and self.cmdr.connected:
            await self.cmdr.disconnect()
        if hasattr(self, "server") and self.server is not None:
            await self.server.close()

    async def test_connect_retries_until_server_is_available(self):
        self.server = None
        self.cmdr = commander.Commander(brand="Keithley", log=logging.getLogger(__file__))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((commander.tcpip.LOCAL_HOST, 0))
            _, port = sock.getsockname()

        self.cmdr.hostname = commander.tcpip.LOCAL_HOST
        self.cmdr.port = port

        async def start_server_later():
            await asyncio.sleep(0.05)
            self.server = mock_server.MockServer("Keithley")
            self.server.port = port
            await self.server.start_task

        start_task = asyncio.create_task(start_server_later())
        try:
            with unittest.mock.patch.object(commander, "RECONNECTION_DELAY", 0.01):
                await self.cmdr.connect()
        finally:
            await start_task

        self.assertTrue(self.cmdr.connected)

    async def test_send_command_recovers_after_server_drops_mid_reply(self):
        self.server = mock_server.MockServer("Keithley", disconnect_reply_after_bytes=1)
        await self.server.start_task

        self.cmdr = commander.Commander(brand="Keithley", log=logging.getLogger(__file__))
        self.cmdr.hostname = self.server.host
        self.cmdr.port = self.server.port

        with unittest.mock.patch.object(commander, "RECONNECTION_DELAY", 0.01):
            reply = await self.cmdr.send_command("*idn?;", has_reply=True, timeout=5)

        self.assertIn("KEITHLEY INSTRUMENTS INC.", reply)

    async def test_connect_raises_when_retries_are_exhausted(self):
        self.server = None
        self.cmdr = commander.Commander(brand="Keithley", log=logging.getLogger(__file__))

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((commander.tcpip.LOCAL_HOST, 0))
            _, port = sock.getsockname()

        self.cmdr.hostname = commander.tcpip.LOCAL_HOST
        self.cmdr.port = port

        with (
            unittest.mock.patch.object(commander, "RECONNECTION_DELAY", 0.01),
            unittest.mock.patch.object(commander, "NUMBER_OF_RETRIES", 2),
        ):
            with self.assertRaises(RuntimeError):
                await self.cmdr.connect()
