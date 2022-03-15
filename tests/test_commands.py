import unittest

from lsst.ts.electrometer.commands_factory import ElectrometerCommandFactory


class TestElectrometerCommandFactory(unittest.TestCase):
    def setUp(self):
        self.commands = ElectrometerCommandFactory()

    def test_activate_filter(self):
        reply = self.commands.activate_filter(mode=1, filter_type=1, active=1)
        self.assertEqual(reply, ":sens:CURR:MED:stat 1;")

    def test_get_avg_filter_status(self):
        reply = self.commands.get_avg_filter_status(1)
        self.assertEqual(reply, ":sens:CURR:aver:type?;")

    def test_get_med_filter_status(self):
        reply = self.commands.get_med_filter_status(1)
        self.assertEqual(reply, ":sens:CURR:med:stat?;")

    def test_get_filter_status(self):
        reply = self.commands.get_filter_status(1, 1)
        self.assertEqual(reply, ":sens:CURR:MED:stat?;")

    def test_set_avg_filter_status(self):
        reply = self.commands.set_avg_filter_status(1, 1)
        self.assertEqual(reply, ":sens:CURR:aver:type NONE;")

    def test_med_filter_status(self):
        reply = self.commands.set_med_filter_status(1, 1)
        self.assertEqual(reply, ":sens:CURR:med:stat 1;")

    def test_always_read(self):
        reply = self.commands.always_read()
        self.assertEqual(reply, ":trac:feed:cont alw;:init;")

    def test_next_read(self):
        reply = self.commands.next_read()
        self.assertEqual(reply, ":trac:feed:cont next;:init;")

    def test_clear_buffer(self):
        reply = self.commands.clear_buffer()
        self.assertEqual(reply, ":trac:cle;")

    def test_clear_device(self):
        reply = self.commands.clear_device()
        self.assertEqual(reply, "^C")

    def test_get_last_error(self):
        reply = self.commands.get_last_error()
        self.assertEqual(reply, ":syst:err?;")

    def test_format_trac(self):
        reply = self.commands.format_trac()
        self.assertEqual(reply, ":trac:elem TST;")

    def test_get_buffer_quantity(self):
        reply = self.commands.get_buffer_quantity()
        self.assertEqual(reply, ":trac:poin:act?;")

    def test_get_hardware_info(self):
        reply = self.commands.get_hardware_info()
        self.assertEqual(reply, "*idn?")

    def test_get_measure(self):
        reply = self.commands.get_measure(1)
        self.assertEqual(reply, ":sens:data?;")

    def test_get_mode(self):
        reply = self.commands.get_mode()
        self.assertEqual(reply, ":sens:func?;")

    def test_enable_temperature_reading(self):
        reply = self.commands.enable_temperature_reading(False)
        self.assertEqual(reply, ":syst:tsc OFF;")

    def test_read_buffer(self):
        reply = self.commands.read_buffer()
        self.assertEqual(reply, ":trac:data?;")

    def test_reset_device(self):
        reply = self.commands.reset_device()
        self.assertEqual(reply, "*RST; :trac:cle;")

    def test_select_device_time(self):
        reply = self.commands.select_device_timer()
        self.assertEqual(reply, ":trig:sour tim;\n:trig:tim 0.001;")

    def test_set_buffer_size(self):
        reply = self.commands.set_buffer_size()
        self.assertEqual(reply, ":trac:cle;:trac:points 50000;:trig:count 50000;")

    def test_init_buffer(self):
        reply = self.commands.init_buffer()
        self.assertEqual(reply, ":init;")

    def test_integration_time(self):
        reply = self.commands.integration_time(1)
        self.assertEqual(reply, ":sens:CURR:aper 0.001000;")

    def test_set_mode(self):
        reply = self.commands.set_mode(2)
        self.assertEqual(reply, ":sens:func 'CHAR';")

    def test_set_range(self):
        reply = self.commands.set_range(auto=False, range_value=0.001, mode=1)
        self.assertEqual(reply, ":sens:CURR:rang:auto 0;\n:sens:CURR:rang 0.001;")

    def test_enable_sync(self):
        reply = self.commands.enable_sync(False)
        self.assertEqual(reply, ":syst:lsyn:stat OFF;")

    def test_stop_storing_buffer(self):
        reply = self.commands.stop_storing_buffer()
        self.assertEqual(reply, ":trac:feed:cont NEV;")

    def test_enable_all_instrument_errors(self):
        reply = self.commands.enable_all_instrument_errors()
        self.assertEqual(reply, ":stat:que:enab (-440:+958);")

    def test_enable_zero_check(self):
        reply = self.commands.enable_zero_check(True)
        self.assertEqual(reply, ":syst:zch ON;")

    def test_enable_zero_correction(self):
        reply = self.commands.enable_zero_correction(True)
        self.assertEqual(reply, ":syst:zcor ON;")

    def test_get_range(self):
        reply = self.commands.get_range(1)
        self.assertEqual(reply, ":sens:CURR:rang?;")

    def test_get_integration_time(self):
        reply = self.commands.get_integration_time(1)
        self.assertEqual(reply, ":sens:CURR:aper?;")

    def test_enable_display(self):
        reply = self.commands.enable_display(True)
        self.assertEqual(reply, ":disp:enab ON;")

    def test_set_timer(self):
        reply = self.commands.set_timer()
        self.assertEqual(reply, ":sens:curr:nplc 0.01;")
