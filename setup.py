from setuptools import setup, find_namespace_packages

setup(
    name="ts_electrometer",
    setup_requires=["setuptools_scm"],
    package_dir={"": "python"},
    packages=find_namespace_packages(where="python"),
    scripts=["bin/RunElectrometer.py"]
)
