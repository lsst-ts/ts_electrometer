"""Sphinx configuration file for TSSW package"""

from documenteer.conf.pipelinespkg import *  # noqa

project = "ts_electrometer"
html_theme_options["logotext"] = project  # noqa
html_title = project
html_short_title = project

intersphinx_mapping["ts_xml"] = ("https://ts-xml.lsst.io", None)  # noqa
intersphinx_mapping["pyserial"] = (  # noqa
    "https://pyserial.readthedocs.io/en/latest",  # noqa
    None,  # noqa
)  # noqa
intersphinx_mapping["ts_salobj"] = ("https://ts-salobj.lsst.io", None)  # noqa
