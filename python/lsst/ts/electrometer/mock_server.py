import asyncio
import logging
import re

from lsst.ts import tcpip


class MockServer(tcpip.OneClientServer):
    """Implements a mock server for the electrometer.

    Attributes
    ----------
    log
    device
    read_loop_task
    """

    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)
        self.device = MockKeithley()
        self.read_loop_task = asyncio.Future()
        super().__init__(
            name="Electrometer Mock Server",
            host=tcpip.LOCAL_HOST,
            port=9999,
            connect_callback=self.connect_callback,
            log=self.log,
        )

    async def cmd_loop(self):
        """Implement the command loop for the electrometer"""
        while self.connected:
            line = await self.reader.readuntil(b"\r")
            reply = self.device.parse_message(line)
            self.log.debug(f"reply={reply}")
            if reply is not None:
                reply = reply + "\r"
                reply = reply.encode("ascii")
                self.log.debug(f"writing reply={reply}")
                self.writer.write(reply)
                await self.writer.drain()

    def connect_callback(self, server):
        """Start the command loop when client is connected.

        Parameters
        ----------
        server
        """
        self.read_loop_task.cancel()
        if server.connected:
            self.read_loop_task = asyncio.create_task(self.cmd_loop())


class MockKeithley:
    def __init__(self):
        """Mock a keithley electrometer.

        Attributes
        ----------
        log
        commands
        """
        self.log = logging.getLogger(__name__)
        self.commands = {
            re.compile(r"^\*idn\?;$"): self.do_get_hardware_info,
            re.compile(
                r"^:sens:(CURR|CHAR|VOlT|RES):aper \d\.\d+;$"
            ): self.do_integration_time,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):aper\?;$"
            ): self.do_get_integration_time,
            re.compile(
                r"^:syst:zch (?P<parameter>ON|OFF);$"
            ): self.do_enable_zero_check,
            re.compile(
                r"^:sens:func (?P<parameter>'CURR'|'CHAR'|'VOLT'|'RES');$"
            ): self.do_set_mode,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):rang:auto (0|1);$"
            ): self.do_set_range,
            re.compile(r"^:sens:(CURR|CHAR|VOLT|RES):rang\?;$"): self.do_get_range,
            re.compile(
                r"^:syst:zcor (?P<parameter>ON|OFF);$"
            ): self.do_enable_zero_correction,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):(MED|AVER):stat (0|1);$"
            ): self.do_activate_filter,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):AVER:type\?;$"
            ): self.do_get_avg_filter_status,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):AVER:stat\?;$"
            ): self.do_get_avg_filter_status,
            re.compile(
                r"^:sens:(CURR|CHAR|VOLT|RES):MED:stat\?;$"
            ): self.do_get_med_filter_status,
            re.compile(r"^:syst:err\?;$"): self.do_get_last_error,
            re.compile(r"^:sens:func\?;$"): self.do_get_mode,
            re.compile(r"^:trac:cle;$"): self.do_clear_buffer,
            re.compile(
                r"^:trac:elem (?P<parameter>NONE|CHAN|TST|ETEM);$"
            ): self.do_format_trac,
            re.compile(r"^:trac:points 50000;$"): self.do_set_buffer_size,
            re.compile(r"^:trig:count 50000;$"): self.do_set_buffer_size,
            re.compile(r"^:trig:sour imm;$"): self.do_select_device_timer,
            re.compile(
                r"^:trig:tim (?P<parameter>\d\.\d\d\d);$"
            ): self.do_select_device_timer,
            re.compile(r"^:trac:feed:cont next;$"): self.do_next_read,
            re.compile(r"^:init;$"): self.do_init_buffer,
            re.compile(r"^:trac:feed:cont NEV;$"): self.do_stop_storing_buffer,
            re.compile(r"^:trac:data\?;$"): self.do_read_buffer,
            re.compile(r"^:sens:data\?;$"): self.do_read_sensor,
        }

    def parse_message(self, msg):
        """Parse and return the result of the message.

        Parameters
        ----------
        msg : `bytes`
            The message to parse.

        Returns
        -------
        reply : `bytes`
            The reply of the command parsed.

        Raises
        ------
        NotImplementedError
            Raised when command is not implemented.
        """
        try:
            msgs = msg.decode().split(";")
            for msg in msgs:
                msg = msg.rstrip("\r\n") + ";"
                self.log.info(repr(msg))
                for command, func in self.commands.items():
                    self.log.info(command)
                    matched_command = command.match(msg)
                    self.log.info(matched_command)
                    if matched_command:
                        try:
                            reply = func(matched_command.group("parameter"))
                            self.log.info(reply)
                            if reply != "":
                                return reply
                            return None
                        except IndexError:
                            reply = func()
                            self.log.info(reply)
                            if reply != "":
                                return reply
                            return None
                raise NotImplementedError(msg)
        except Exception as e:
            self.log.exception(e)
            raise e

    def do_get_hardware_info(self):
        """Return hardware information."""
        return "KEITHLEY INSTRUMENTS INC.,MODEL 6517B,4096271,A13/700X"

    def do_enable_zero_check(self, *args):
        """Enable zero check."""
        return ""

    def do_set_mode(self, *args):
        """Set the mode."""
        return ""

    def do_set_range(self, *args):
        """Set the range."""
        return ""

    def do_enable_zero_correction(self, *args):
        """Enable zero correction."""
        return ""

    def do_activate_filter(self, *args):
        """Activate filter(s)."""
        return ""

    def do_get_last_error(self):
        """Get the most recent error."""
        return "0, fine"

    def do_get_mode(self):
        """Get the current mode."""
        return "CURR:AMP"

    def do_clear_buffer(self):
        """Clear the buffer."""
        return ""

    def do_format_trac(self, *args):
        """Format the trac."""
        return ""

    def do_set_buffer_size(self):
        """Set the buffer size."""
        return ""

    def do_select_device_timer(self, *args):
        """Select the device timer."""
        return ""

    def do_next_read(self):
        """Read the next value."""
        return ""

    def do_init_buffer(self):
        """Initialize the buffer."""
        return ""

    def do_stop_storing_buffer(self):
        """Stop storing to the buffer."""
        return ""

    def do_read_buffer(self):
        """Read the values in the buffer."""
        return "1 0 0 c\n0 0 0 c"

    def do_read_sensor(self):
        return "0"

    def do_get_avg_filter_status(self):
        return "0"

    def do_get_med_filter_status(self):
        return "1"

    def do_integration_time(self):
        return ""

    def do_get_integration_time(self):
        return "0.01"

    def do_get_range(self):
        return "0.1"
