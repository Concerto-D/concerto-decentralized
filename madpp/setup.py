#!/usr/bin/env python
# encoding: utf-8
import sys
import os

from setuptools import setup, find_packages

if sys.version_info < (2, 6):
    sys.exit("requires python 2.6 and up")

here = os.path.dirname(__file__)
pks=find_packages()

setup(name = "mad",
      version = "0.2",
      description = "The implementation of the Madeus model in Python.",
      author = "Hélène Coullon, Christian Perez",
      author_email = "helene.coullon@imt-atlantique.fr, christian.perez@inria.fr",
      maintainer = "Helene Coullon",
      maintainer_email = "helene.coullon@imt-atlantique.fr",
      license = "GPL3",
      url = "https://mad.readthedocs.io",
      packages = pks,
      platforms = ["POSIX"],
      use_2to3 = False,
      zip_safe = False,
      long_description = open(os.path.join(here, "README.md"), "r").read()
)

