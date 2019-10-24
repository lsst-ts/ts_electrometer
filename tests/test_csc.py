import logging
import unittest
import asyncio

import numpy as np

from lsst.ts import salobj

from lsst.ts import electrometer
import sys

SEED = 3480

np.random.seed(SEED)

BASE_TIMEOUT = 20

index_gen = salobj.index_generator()

logger = logging.getLogger(__name__)
logger.level = logging.DEBUG


class Harness:
    def __init__(self, index, config_dir, initial_simulation_mode):
        salobj.test_utils.set_random_lsst_dds_domain()
        self.csc = electrometer.csc.ElectrometerCsc(
            index=index, config_dir=config_dir, initial_simulation_mode=initial_simulation_mode)
        self.remote = salobj.Remote(self.csc.domain, "Environment", index)

    async def __aenter__(self):
        await self.csc.start_task
        await self.remote.start_task
        return self

    async def __aexit__(self, *args):
        await self.csc.close()

    
class TestElectrometerCSC(unittest.TestCase):

    def test_standard_state_transitions(self):
        async def doit():
            commands = ("start", "enable", "disable", "exitControl", "standby")
            index = next(index_gen)
            self.assertGreater(index, 0)

            async with Harness(index, None, 1) as harness:
                current_state = await harness.remote.evt_summaryState.next(flush=False, timeout=BASE_TIMEOUT)

                self.assertEqual(harness.csc.summary_state, salobj.State.STANDBY)
                self.assertEqual(current_state.summaryState, salobj.State.STANDBY)

                setting_versions = await harness.remote.evt_settingsVersions.next(flush=False, timeout=BASE_TIMEOUT)

                self.assertIsNotNone(setting_versions)

                for bad_command in commands:
                    if bad_command in ("start", "exitControl"):
                        continue
                    with self.subTest(bad_command=bad_command):
                        cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                        with self.assertRaises(salobj.AckError):
                            id_ack = await cmd_attr.start(timeout=BASE_TIMEOUT)

                cmd_attr = getattr(harness.remote, f"cmd_start")
                harness.remote.evt_summaryState.flush()
                id_ack = await cmd_attr.start(timeout=120)
                state = await harness.remote.evt_summaryState.next(flush=False, timeout=BASE_TIMEOUT)

                self.assertEqual(id_ack.ack, salobj.SalRetCode.CMD_COMPLETE)
                self.assertEqual(id_ack.error, 0)
                self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)
                self.assertEqual(state.summaryState, salobj.State.DISABLED)

                for bad_command in commands:
                    if bad_command in ("enable", "standby"):
                        continue
                    with self.subTest(bad_command=bad_command):
                        cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                        with self.assertRaises(salobj.AckError):
                            id_ack = await cmd_attr.start(timeout=BASE_TIMEOUT)

                cmd_attr = getattr(harness.remote, f"cmd_enable")
                harness.remote.evt_summaryState.flush()
                id_ack = await cmd_attr.start(timeout=BASE_TIMEOUT)
                state = await harness.remote.evt_summaryState.next(flush=False,
                                                                   timeout=BASE_TIMEOUT)
                self.assertEqual(id_ack.ack, salobj.SalRetCode.CMD_COMPLETE)
                self.assertEqual(id_ack.error, 0)
                self.assertEqual(harness.csc.summary_state, salobj.State.ENABLED)
                self.assertEqual(state.summaryState, salobj.State.ENABLED)

                for bad_command in commands:
                    if bad_command == "disable":
                        continue  # valid command in ENABLE state
                    with self.subTest(bad_command=bad_command):
                        cmd_attr = getattr(harness.remote, f"cmd_{bad_command}")
                        with self.assertRaises(salobj.AckError):
                            id_ack = await cmd_attr.start(timeout=BASE_TIMEOUT)

                # send disable; new state is DISABLED
                cmd_attr = getattr(harness.remote, f"cmd_disable")
                # this CMD may take some time to complete
                id_ack = await cmd_attr.start(timeout=30.)
                self.assertEqual(id_ack.ack, salobj.SalRetCode.CMD_COMPLETE)
                self.assertEqual(id_ack.error, 0)
                self.assertEqual(harness.csc.summary_state, salobj.State.DISABLED)

        asyncio.get_event_loop().run_until_complete(doit())


if __name__ == '__main__':

    stream_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stream_handler)

    unittest.main()
