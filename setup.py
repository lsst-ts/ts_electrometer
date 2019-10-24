from setuptools import setup, find_namespace_packages

setup(
    name="ts_electrometer",
    version="0.1",
    package_dir={"": "python"},
    packages=find_namespace_packages(where="python")
)
