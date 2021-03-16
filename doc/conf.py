"""Sphinx configuration file for TSSW package"""

from documenteer.conf.pipelinespkg import *

project = "ts_electrometer"
html_theme_options["logotext"] = project
html_title = project
html_short_title = project

intersphinx_mapping["ts_xml"] = ("https://ts-xml.lsst.io", None)
intersphinx_mapping["pyserial"] = ("https://pyserial.readthedocs.io/en/latest", None)
intersphinx_mapping["ts_salobj"] = ("https://ts-salobj.lsst.io", None)
