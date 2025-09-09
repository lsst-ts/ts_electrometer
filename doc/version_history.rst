v0.13.0 (2025-08-12)
====================

New Features
------------

- Switched from integration time to NPLC and set integration time to use auto functionality. (`DM-51029 <https://rubinobs.atlassian.net//browse/DM-51029>`_)
- Improved simulation mode to better match hardware. (`OBW-495 <https://rubinobs.atlassian.net//browse/OBW-495>`_)
- Added changeNPLC command to CSC. (`OSW-65 <https://rubinobs.atlassian.net//browse/OSW-65>`_)
- Added retry loop to commander. (`OSW-495 <https://rubinobs.atlassian.net//browse/OSW-495>`_)
- Added ack_in_progress to startScanDt for both before starting the scan and for reading the buffer. (`OSW-495 <https://rubinobs.atlassian.net//browse/OSW-495>`_)
- Improved retry loop by reconnecting if disconnected for whatever reason. (`OSW-559 <https://rubinobs.atlassian.net//browse/OSW-559>`_)
- Improved check_error by getting all potential non zero error codes. (`OSW-559 <https://rubinobs.atlassian.net//browse/OSW-559>`_)
- Added a delay between reconnection attempts to see if it improves issue with Keithley hardware. (`OSW-707 <https://rubinobs.atlassian.net//browse/OSW-707>`_)


Bug Fixes
---------

- Changed int_time to nplc when calling set_time in csc.py. (`DM-51305 <https://rubinobs.atlassian.net//browse/DM-51305>`_)
- Fixed the Keysight so that when it sets the timer it also sets the appropriate trigger wait time. (`DM-51723 <https://rubinobs.atlassian.net//browse/DM-51723>`_)
- Added get_timer to command factory so that setIntegrationTime does not throw exception. (`OSW-495 <https://rubinobs.atlassian.net//browse/OSW-495>`_)
- Added get_integration_time call to set_timer to get updated integration time. (`OSW-559 <https://rubinobs.atlassian.net//browse/OSW-559>`_)
