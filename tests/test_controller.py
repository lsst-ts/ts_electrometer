import pathlib
import types
import unittest
import unittest.mock

import yaml

from lsst.ts.electrometer import controller

TEST_CONFIG = pathlib.Path(__file__).parents[1].joinpath("tests", "data", "config", "_init.yaml")


class ControllerTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_configure_does_not_require_csc(self):
        with open(TEST_CONFIG) as fp:
            config = yaml.safe_load(fp)

        instance = next(item for item in config["instances"] if item["sal_index"] == 103)
        ctrl = controller.KeithleyElectrometerController()
        ctrl.configure(types.SimpleNamespace(**instance))

        self.assertFalse(hasattr(ctrl, "csc"))
        self.assertEqual(ctrl.commander.brand, "Keithley")
        self.assertEqual(ctrl.commander.hostname, "localhost")
        self.assertEqual(ctrl.commander.port, 4002)
        self.assertEqual(ctrl.mode, "CURR")

    async def test_get_settings_returns_typed_snapshot(self):
        with open(TEST_CONFIG) as fp:
            config = yaml.safe_load(fp)

        instance = next(item for item in config["instances"] if item["sal_index"] == 103)
        ctrl = controller.KeithleyElectrometerController()
        ctrl.configure(types.SimpleNamespace(**instance))

        settings = ctrl.get_settings()

        self.assertEqual(settings.mode, "CURR")
        self.assertAlmostEqual(settings.range, 2.0e-08)
        self.assertAlmostEqual(settings.integration_time, 0.1)
        self.assertFalse(settings.filter_active)
        self.assertIsNone(settings.nplc)

    async def test_manual_scan_uses_before_and_during_phases(self):
        ctrl = controller.KeithleyElectrometerController()
        ctrl.before_scan = unittest.mock.AsyncMock()
        ctrl.during_scan = unittest.mock.AsyncMock()

        await ctrl.start_scan(group_id="GROUP1")

        ctrl.before_scan.assert_awaited_once_with(group_id="GROUP1", timed_scan=False)
        ctrl.during_scan.assert_awaited_once_with(timed_scan=False)

    async def test_timed_scan_uses_before_and_during_phases(self):
        ctrl = controller.KeithleyElectrometerController()
        ctrl.before_scan = unittest.mock.AsyncMock()
        ctrl.during_scan = unittest.mock.AsyncMock()

        await ctrl.start_scan_dt(scan_duration=1.5, group_id="GROUP2")

        ctrl.before_scan.assert_awaited_once_with(group_id="GROUP2", timed_scan=True)
        ctrl.during_scan.assert_awaited_once_with(timed_scan=True, scan_duration=1.5)

    async def test_stop_scan_uses_after_phase(self):
        ctrl = controller.KeithleyElectrometerController()
        expected = controller.ScanResult(
            data={"Signal": [1.0]},
            trace_elements=["Signal"],
            start_time=1.0,
            end_time=2.0,
            duration=1.0,
            group_id="GROUP3",
        )
        ctrl.after_scan = unittest.mock.AsyncMock(return_value=expected)

        result = await ctrl.stop_scan()

        ctrl.after_scan.assert_awaited_once_with()
        self.assertEqual(result, expected)

    async def test_keysight_overrides_timed_wait_hook(self):
        ctrl = controller.KeysightElectrometerController()
        ctrl.send_command = unittest.mock.AsyncMock()

        await ctrl.wait_for_scan_completion(0.0)

        self.assertEqual(
            [call.args[0] for call in ctrl.send_command.await_args_list],
            [ctrl.commands.acquire_data(), ctrl.commands.stop_taking_data()],
        )

    async def test_keithley_overrides_scan_storage_hook(self):
        ctrl = controller.KeithleyElectrometerController()
        ctrl.send_command = unittest.mock.AsyncMock()

        await ctrl.configure_scan_storage()

        self.assertEqual(
            [call.args[0] for call in ctrl.send_command.await_args_list],
            [ctrl.commands.clear_buffer(), ctrl.commands.set_buffer_size(50000)],
        )


if __name__ == "__main__":
    unittest.main()
