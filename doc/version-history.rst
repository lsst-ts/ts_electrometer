.. _Version_History:

===============
Version History
===============

.. At the time of writing the Version history/release notes are not yet standardized amongst CSCs.
.. Until then, it is not expected that both a version history and a release_notes be maintained.
.. It is expected that each CSC link to whatever method of tracking is being used for that CSC until standardization occurs.
.. No new work should be required in order to complete this section.
.. Below is an example of a version history format.

v0.5.0
======
* Add LFA support
* Add isort suport
* Add try-except to connect method
* Add try-except to revert detailed state if command failed

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