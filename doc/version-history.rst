.. _Version_History:

===============
Version History
===============

.. At the time of writing the Version history/release notes are not yet standardized amongst CSCs.
.. Until then, it is not expected that both a version history and a release_notes be maintained.
.. It is expected that each CSC link to whatever method of tracking is being used for that CSC until standardization occurs.
.. No new work should be required in order to complete this section.
.. Below is an example of a version history format.

.. towncrier release notes start

ts_electrometer v0.9.0 (2024-10-03)
===================================

Features
--------

- Added Keysight capabilities. (`DM-40055 <https://rubinobs.atlassian.net/DM-40055>`_)
- Implement the ts-tcpip.lsst.io library. (`DM-40055 <https://rubinobs.atlassian.net/DM-40055>`_)
- Updated config schema to handle Keysight and Keithley. (`DM-40055 <https://rubinobs.atlassian.net/DM-40055>`_)
- Add optional groupId to startScan and startScanDt (`DM-44757 <https://rubinobs.atlassian.net/DM-44757>`_)


Bugfixes
--------

- Fixed fits file name for the s3 bucket. (`DM-40055 <https://rubinobs.atlassian.net/DM-40055>`_)
- Add startScanDt ack_in_progress. (`DM-40055 <https://rubinobs.atlassian.net/DM-40055>`_)
- Update ts-conda-build 0.4. (`DM-43486 <https://rubinobs.atlassian.net/DM-43486>`_)
- Removed log message describing scan data redundantly. (`DM-45981 <https://rubinobs.atlassian.net/DM-45981>`_)


Improved Documentation
----------------------

- Add towncrier support. (`DM-43486 <https://rubinobs.atlassian.net/DM-43486>`_)


v0.8.3
======

* Support tpcip 2.0 by removing reader and writer attribute calls.

v0.8.2
======
* Add value call to enums that inherit from str.
* Remove scons files.
* Implement DevelopPipeline.
* Implement ts_precommit_conf.

v0.8.1
======
* Update pre-commit to black 23, isort 5.12 & check-yaml 4.4.

v0.8.0
======
* Make configurations correspond to a particular SAL Index.
* Remove baud_rate from schema.
* Correct s3 bucket names.
* Make fits file name the obsid when writing to disk.
* Fix parse_buffer assuming that temperature and voltage input will always be there even when temperature and vsource attached are false.
* Catch ValueError when get_intensity returns a saturated value.
* Make resolution return 5 values when running a scan.
* Add Error enum for fault error codes.
* Reset the controller when connecting to it to make integration time work correctly.
* Return early if ValueError is caught.

v0.7.0
======
* Remove cli module and move functions to csc module.
* Add OBSID to header using utils.ImageNameServiceClient.
* Modernize conda recipe.

v0.6.0
======
* Refactor fits files to match Vera C. Rubin Observatory format.

v0.5.0
======
* Add LFA support
* Add isort suport
* Add try-except to connect method
* Add try-except to revert detailed state if command failed
* Add voltage source command and event
* Add auto_range active at logic to set_range command

v0.4.0
======
* Fix not applying configuration to device
* Fix digitalFilterChange truthiness being incorrect
* Make events publish when getting values read from the controller
* Add a scan summary to the log
* Fix CHAR and RES modes not being set properly
* Add pyproject.toml
* Remove extensions from command and run_electrometer script

v0.3.0
======
* Fix integrationTime, digitalFilter and range not being updated
* Make package generic

v0.2.0
======
* Fix file writing

v0.1.0
======

* Initial CSC release
* Upgrade to black 20.8