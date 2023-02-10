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
import re

from lsst.ts import tcpip


class MockServer(tcpip.OneClientServer):
    """Implements a mock server for the electrometer.

    Attributes
    ----------
    log : `logging.Logger`
        The log for the server.
    device : `MockKeithley`
        The mock device that handles commands that are parsed.
    read_loop_task : `asyncio.Future`
        The task that tracks the read loop.
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

    async def connect_callback(self, server):
        """Start the command loop when client is connected.

        Parameters
        ----------
        server : `MockServer`
            The server object.
        """
        self.read_loop_task.cancel()
        if server.connected:
            self.read_loop_task = asyncio.create_task(self.cmd_loop())


class MockKeithley:
    def __init__(self):
        """Mock a keithley electrometer.

        Attributes
        ----------
        log : `logging.Logger`
            The log.
        commands : `dict`
            Regular expressions that correspond to a given command.
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
                r"^:trac:elem (?P<parameter>CHAN|TST|ETEM|VSO), (?P<parameter2>CHAN|TST|ETEM|VSO);$"
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
            re.compile(r"^TST:TYPE RTC;$"): self.do_rtc_time,
            re.compile(
                r"^:sens:curr:nplc (?P<parameter>\d\.\d\d);$"
            ): self.do_change_nplc,
            re.compile(
                r"^:syst:lsyn:stat (?P<parameter>ON|OFF);$"
            ): self.do_change_nplc,
            re.compile(r"^:disp:enab (?P<parameter>ON|OFF);$"): self.do_change_nplc,
            re.compile(
                r"^:vsou:oper (?P<parameter>ON|OFF);$"
            ): self.do_toggle_voltage_source,
            re.compile(r"^:vsou:oper\?;$"): self.get_voltage_source_status,
            re.compile(r"^:sour:volt:lim:ampl 2;$"): self.set_voltage_limit,
            re.compile(r"^:sour:volt:lim:stat\?;$"): self.get_voltage_limit,
            re.compile(r"^:sour:volt:rang 1;$"): self.set_voltage_range,
            re.compile(r"^:sour:volt:rang\?;$"): self.get_voltage_range,
            re.compile(r"^:sour:volt:lev:imm:ampl 2;$"): self.set_voltage_level,
            re.compile(r"^:sour:volt:lev:imm:ampl\?;$"): self.get_voltage_level,
            re.compile(r"^:sens:CURR:dig 5;$"): self.set_resolution,
            re.compile(r"\*RST;$"): self.do_reset_device,
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
        return "+0.01DC 0.33\n+0.01DC 0.33\n+0.01DC 0.33\n+0.01DC 0.33\n"

    def do_read_sensor(self):
        """Read the sensor."""
        return "0"

    def do_get_avg_filter_status(self):
        """Get the status of the filter in average mode."""
        return "0"

    def do_get_med_filter_status(self):
        """Get the state of the filter in median mode."""
        return "1"

    def do_integration_time(self):
        """Set the integration time setting."""
        return ""

    def do_get_integration_time(self):
        """Get the integration time setting."""
        return "0.01"

    def do_get_range(self):
        """Get the range setting."""
        return "0.1"

    def do_rtc_time(self):
        """Switch to RTClock mode."""
        pass

    def do_change_nplc(self, nplc):
        """Change the number of programmable logic cycles

        Parameters
        ----------
        nplc : `int`
            The number of cycles.
        ."""
        pass

    def do_change_sync(self, sync):
        """Change the line synchronization setting.

        Parameters
        ----------
        sync : `bool`
            Turn on line synchronization.
        """
        pass

    def do_toggle_voltage_source(self, toggle):
        pass

    def get_voltage_source_status(self):
        return "ON"

    def set_voltage_limit(self):
        pass

    def get_voltage_limit(self):
        return "2"

    def get_voltage_range(self):
        return "1"

    def set_voltage_range(self):
        pass

    def get_voltage_level(self):
        return "2"

    def set_voltage_level(self):
        pass

    def set_resolution(self):
        pass

    def do_reset_device(self):
        pass
