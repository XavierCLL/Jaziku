#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2011-2012 IDEAM
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

#==============================================================================
# GLOBAL VARIABLES

# name program
PROG_NAME = "jaziku"

# version
VERSION = "0.2"

# compilation date
COMPILE_DATE = "12/03/2012"

# valid null value for variables dependent and independent (inside files input)
VALID_NULL = [99999, -99999]

# accuracy of number decimal places, only for print result
ACCURACY = 3

# types of internal variable independent
internal_var_I_types = ["ONI", "SOI", "MEI", "OLR", "W200", "SST", "ARH", "NAO", "QBO"]

# namefiles of internal variable independent
internal_var_I_files = {"ONI": "ONI_1950_2011_CPC.txt",
                        "SOI": "SOI_1951_2011_CPC_NOAA.txt",
                        "MEI": "MEI_1950_2011_ESRL_NOAA.txt",
                        "OLR": "OLR_1974_2011_CPC_NCEP_NOAA.txt",
                        "W200": "W200_1979_2011_CPC_NCEP_NOAA.txt",
                        "SST": "SST_1950_2011_CPC_NCEP_NOAA.txt",
                        #"ARH": "????",
                        "NAO": "NAO_1950_2011_CPC_NCEP_NOAA.txt",
                        "QBO": "QBO_1950_2011_ESRL_NOAA.txt"}

# urls where get the internal files for independent variable
internal_var_I_urls = {"ONI": "http://goo.gl/bppGe",
                        "SOI": "http://goo.gl/nhF4D",
                        "MEI": "http://goo.gl/KWEwZ",
                        "OLR": "http://goo.gl/goMpA",
                        "W200": "http://goo.gl/aliLh",
                        "SST": "http://goo.gl/WcYSg",
                        #"ARH": "????",
                        "NAO": "http://goo.gl/1uDjY",
                        "QBO": "http://goo.gl/UO6PX"}

# maps files for climate:
maps_files_climate = {'5days':None, '10days':None, '15days':None, 'trimester':None}
# maps files for forecasting:
maps_files_forecasting = {'5days':None, '10days':None, '15days':None, 'trimester':None}


# phenomenon based on arguments or not, start with default value
phenomenon_below = _('var_I_below')
phenomenon_normal = _('var_I_normal')
phenomenon_above = _('var_I_above')



# directory to save all results, this can be absolute or relative path
# import Jaziku_utils.input_arg as input_arg
# args = input_arg.arguments.parse_args()
# DIR_RESULTS = args.file_D.split('.')[0] + args.file_I.split('.')[0]
