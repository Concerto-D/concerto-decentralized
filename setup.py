#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="concerto",
    version="0.1.2",
    description="Preliminary implementation in Python 3 of the Concerto reconfiguration model.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Maverick Chardet, Hélène Coullon, Christian Perez",
    author_email="maverick.chardet@inria.fr, helene.coullon@imt-atlantique.fr, christian.perez@inria.fr",
    maintainer="Maverick Chardet",
    maintainer_email="maverick.chardet@inria.fr",
    license="GPL3",
    url="https://mad.readthedocs.io",
    packages=find_packages(),
    platforms=["POSIX"],
    classifier=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ],
    python_requires='>=3.6'
)
