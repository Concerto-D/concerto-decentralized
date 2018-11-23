#!/usr/bin/env python
# encoding: utf-8
import sys
import os

from setuptools import setup, find_packages

if sys.version_info < (3, 6):
    sys.exit("requires python 3.6 and up")

here = os.path.dirname(__file__)
pks=find_packages()

setup(name = "madpp",
      version = "0.1",
      description = "The implementation of the Madeus++ model in Python.",
      author = "Maverick Chardet, Hélène Coullon, Christian Perez",
      author_email = "maverick.chardet@inria.fr, helene.coullon@imt-atlantique.fr, christian.perez@inria.fr",
      maintainer = "Maverick Chardet",
      maintainer_email = "maverick.chardet@inria.fr",
      license = "GPL3",
      url = "https://mad.readthedocs.io",
      packages = pks,
      platforms = ["POSIX"],
      use_2to3 = False,
      zip_safe = False,
      long_description = open(os.path.join(here, "README.md"), "r").read()
)

