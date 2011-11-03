#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from jaziku.plugins import global_var

setup(name = global_var.PROG_NAME,
      version = global_var.VERSION,
      license = "GNU General Public License (GPL) v3",
      description = "Jaziku is a software for the implementation of composite analysis \
                     metodology between the major indices of climate variability and major \
                     meteorological variables in puntual scale.",
      long_description = """\
      
      """,
      author = "Ines Sánchez Rodriguez, Xavier Corredor Llano",
      author_email = "incsanchezro (a) gmail.com, xcorredorl (a) ideam.gov.co",
      url = "http://hg.ideam.gov.co/jaziku",
      platforms="platform-independent",
      packages = find_packages(),
      py_modules = ["jaziku"],
      scripts = [ "bin/jaziku" ],
      install_requires = ["scipy", "argparse", "python-dateutil", "matplotlib", "numpy", "PIL"]
      )
