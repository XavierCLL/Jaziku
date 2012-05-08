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
VERSION = "0.3.0"

# compilation date
COMPILE_DATE = "07/05/2012"

# valid null value for variables dependent and independent (inside files input)
VALID_NULL = [99999, -99999]

# accuracy of number decimal places, only for print result
ACCURACY = 3

# types of internal variable independent
internal_var_I_types = ["ONI", "SOI", "MEI", "OLR", "W200", "SST", "ARH", "NAO", "QBO", "SSTA_CAR", "AREA_WHWP"]

# namefiles of internal variable independent
internal_var_I_files = {"ONI": "ONI_1950_2011_CPC.txt",
                        "SOI": "SOI_1951_2011_CPC_NOAA.txt",
                        "MEI": "MEI_1950_2011_ESRL_NOAA.txt",
                        "OLR": "OLR_1974_2011_CPC_NCEP_NOAA.txt",
                        "W200": "W200_1979_2011_CPC_NCEP_NOAA.txt",
                        "SST": "SST_1950_2011_CPC_NCEP_NOAA.txt",
                        #"ARH": "????",
                        "NAO": "NAO_1950_2011_CPC_NCEP_NOAA.txt",
                        "QBO": "QBO_1950_2011_ESRL_NOAA.txt",
                        "SSTA_CAR": "SSTA_CAR_1951_2010_ESRL_NOAA.txt",
                        "AREA_WHWP": "AREA_WHWP_1948_2011_ESRL_NOAA.txt"}

# urls where get the internal files for independent variable
internal_var_I_urls = {"ONI": "http://goo.gl/e7unc", # http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ensoyears.shtml
                        "SOI": "http://goo.gl/scbO7", # http://www.cpc.ncep.noaa.gov/data/indices/soi
                        "MEI": "http://goo.gl/dQsdb", # http://www.esrl.noaa.gov/psd/enso/mei/table.html
                        "OLR": "http://goo.gl/goMpA", # http://www.cpc.ncep.noaa.gov/data/indices/olr
                        "W200": "http://goo.gl/aliLh", # http://www.cpc.ncep.noaa.gov/data/indices/zwnd200
                        "SST": "http://goo.gl/WcYSg", # http://www.cpc.ncep.noaa.gov/data/indices/
                        #"ARH": "????",
                        "NAO": "http://goo.gl/1uDjY", # http://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/nao.shtml
                        "QBO": "http://goo.gl/UO6PX", # http://www.esrl.noaa.gov/psd/data/climateindices/list/
                        "SSTA_CAR": "http://goo.gl/BsAeN", # http://www.esrl.noaa.gov/psd/forecasts/sstlim/forcar.html
                        "AREA_WHWP":"http://goo.gl/mV4QI" # http://www.esrl.noaa.gov/psd/data/correlation/whwp.data 
                        }

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
