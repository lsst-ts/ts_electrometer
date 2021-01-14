import logging
import queue
import re

import serial


class MockSerial(serial.Serial):
    """A mock serial object.

    Parameters
    ----------
    port
    baudrate
    bytesize
    parity
    stopbits
    timeout
    xonxoff
    rtscts
    write_timeout
    dsrdtr
    inter_byte_timeout
    exclusive

    Attributes
    ----------
    log
    device
    message_queue
    """

    def __init__(
        self,
        port,
        baudrate=19200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
        xonxoff=False,
        rtscts=False,
        write_timeout=None,
        dsrdtr=False,
        inter_byte_timeout=None,
        exclusive=None,
    ):
        super().__init__(port=port, baudrate=baudrate, timeout=timeout)
        self.log = logging.getLogger(__name__)

        self.device = MockKeithley()
        self.message_queue = queue.Queue()

        self.log.info("MockSerial created")

    def read_until(self, character):
        """Read until the following character is seen."""
        self.log.info("Reading from queue")
        msg = self.message_queue.get()
        self.log.info(msg.encode())
        return msg.encode() + b"\n"

    def write(self, data):
        """Write data to the serial port."""
        self.log.info(data)
        msg = self.device.parse_message(data)
        if msg is not None:
            self.log.debug(msg)
            self.message_queue.put(msg)
            self.log.info("Putting into queue")


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
            re.compile(r"^\*idn$"): self.do_get_hardware_info,
            re.compile(
                r"^:syst:zch (?P<parameter>ON|OFF);$"
            ): self.do_enable_zero_check,
            re.compile(
                r"^:sens:func (?P<parameter>'CURR'|'CHAR'|'VOLT'|'RES');$"
            ): self.do_set_mode,
            re.compile(r"^:sens:CURR|CHAR|VOLT|RES:rang:auto 0|1;$"): self.do_set_range,
            re.compile(
                r"^:syst:zcor (?P<parameter>ON|OFF);$"
            ): self.do_enable_zero_correction,
            re.compile(
                r"^:sens:CURR|CHAR|VOLT|RES:MED|AVG:stat 0|1;$"
            ): self.do_activate_filter,
            re.compile(r"^:syst:err\?;$"): self.do_get_last_error,
            re.compile(r"^:sens:func\?;$"): self.do_get_mode,
            re.compile(r"^:trac:cle;$"): self.do_clear_buffer,
            re.compile(
                r"^:trac:elem (?P<parameter>NONE|CHAN|TST|ETEM);$"
            ): self.do_format_trac,
            re.compile(r"^:trac:points 50000;$"): self.do_set_buffer_size,
            re.compile(r"^:trig:count 50000;$"): self.do_set_buffer_size,
            re.compile(r"^:trig:sour tim;$"): self.do_select_device_timer,
            re.compile(
                r"^:trig:tim (?P<parameter>\d\.\d\d\d);$"
            ): self.do_select_device_timer,
            re.compile(r"^:trac:feed:cont next;$"): self.do_next_read,
            re.compile(r"^:init;$"): self.do_init_buffer,
            re.compile(r"^:trac:feed:cont NEV;$"): self.do_stop_storing_buffer,
            re.compile(r"^:trac:data\?;$"): self.do_read_buffer,
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
        return "1 0 0 0\n0 0 0 0"
