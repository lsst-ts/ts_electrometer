"""Sphinx configuration file for TSSW package"""

from documenteer.sphinxconfig.stackconf import build_package_configs
import lsst.ts.electrometer


_g = globals()
_g.update(build_package_configs(
    project_name='ts_electrometer2',
    version=lsst.ts.electrometer.version.__version__
))

intersphinx_mapping["ts_xml"] = ("https://ts-xml.lsst.io", None)
intersphinx_mapping["pyserial"] = ("https://pyserial.readthedocs.io/en/latest", None)
intersphinx_mapping["ts_salobj"] = ("https://ts-salobj.lsst.io", None)
