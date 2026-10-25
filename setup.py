# -*- coding: utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = "1.0.0"

with open("README.rst") as fh:
    long_description = fh.read()

with open("docs/changelog.rst") as fh:
    long_description += "\n\n"
    long_description += fh.read()

setup(
    name="senaite.dashboard",
    version=version,
    description="Configurable dashboards for SENAITE",
    long_description=long_description,
    classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="senaite lims dashboard",
    author="RIDING BYTES & NARALABS",
    author_email="senaite@senaite.com",
    url="https://github.com/senaite/senaite.dashboard",
    license="GPLv2",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    namespace_packages=["senaite"],
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7.*",
    install_requires=[
        "setuptools",
        "six",
        "plone.api",
        "plone.memoize",
        "senaite.core>=2.7.0",
        "senaite.jsonapi>=2.7.0",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
        ],
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
