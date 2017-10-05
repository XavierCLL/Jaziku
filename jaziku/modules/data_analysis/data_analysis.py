#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2017 Xavier Corredor Ll. - IDEAM
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

import os
from clint.textui import colored

from . import eda
from jaziku import env
from jaziku.utils import console


def main(stations_list):
    """
    In jaziku-Data Analysis, the outliers are reported, is made the assessing the homogeneity of
    the series and is made known to the user of statistical values that will allow discerning, in
    respect of their research objective, the use of a series or another, also directly obtaining the
    files folder of time series.
    """

    print(_("\n\n"
            "#################### DATA ANALYSIS PROCESS #####################\n"
            "# Data analysis module, here is verified linearity, outliers   #\n"
            "# are reported and the primary statistical time series.        #\n"
            "################################################################\n"))

    print(_("Saving the result for data analysis in:"))
    if env.globals_vars.arg_output:
        print("   " + colored.cyan(env.globals_vars.DATA_ANALYSIS_DIR))
    else:
        print("   " + colored.cyan(os.path.relpath(env.globals_vars.DATA_ANALYSIS_DIR,
                                                   os.path.abspath(os.path.dirname(env.globals_vars.arg_runfile)))))

    # -------------------------------------------------------------------------
    # Exploratory data analysis process

    eda.main(stations_list)
