#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2013 IDEAM
#
# This file is part of Jaziku.
#
# Jaziku is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Jaziku is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Jaziku.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
from jaziku import env

setup(
    name=env.globals_vars.PROG_NAME,
    version=env.globals_vars.VERSION,
    license="GNU General Public License (GPL) v3",
    description="Jaziku is statistical inference software for the teleconnections analysis.",
    long_description=open('README.rst').read(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Atmospheric Science'],
    author="Xavier Corredor Llano, Ines Sánchez Rodriguez",
    author_email="xcorredorl(a)ideam.gov.co, icsanchez(a)ideam.gov.co",
    url="http://hg.ideam.gov.co:8000/meteorologia/jaziku",
    platforms="platform-independent",
    install_requires=["scipy", "argparse", "python-dateutil", "matplotlib", "numpy", "Pillow", "clint"],
    scripts=["bin/jaziku", "bin/sisdhim2jaziku", "bin/normalize_format"],
    packages=find_packages(),
    include_package_data=True,
)
