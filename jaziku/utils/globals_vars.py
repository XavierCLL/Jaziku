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

import math

from jaziku.i18n import i18n
_ = i18n.language.ugettext

#==============================================================================
# GLOBAL VARIABLES

PROG_NAME = "jaziku"

VERSION = "0.5.0"

COMPILE_DATE = "21/08/2012"

ROOT_DIR = None

# valid nulls
VALID_NULL = [99999, -99999]  # these are deprecate valid null but now used for maps files interpolation
# valid null value for variables dependent and independent (inside files input)
def is_valid_null(value):
    if math.isnan(value):
        return True
    else:
        try:
            if int(value) in VALID_NULL: # TODO: delete deprecated valid null
                return True
        except:
            return False
    return False

# accuracy of number decimal places, only for print result
ACCURACY = 5

# arguments
args = None

# runfile
run_file = None

# trimester text for print
trim_text = {-2: _('NDJ'), -1: _('DJF'), 0: _('JFM'), 1: _('FMA'), 2: _('MAM'),
             3: _('AMJ'), 4: _('MJJ'), 5: _('JJA'), 6: _('JAS'), 7: _('ASO'),
             8: _('SON'), 9: _('OND'), 10: _('NDJ'), 11: _('DJF')}

# month text for print
month_text = {-2: _('Nov'), -1: _('Dec'), 0: _('Jan'), 1: _('Feb'), 2: _('Mar'),
              3: _('Apr'), 4: _('May'), 5: _('Jun'), 6: _('Jul'), 7: _('Aug'),
              8: _('Sep'), 9: _('Oct'), 10: _('Nov'), 11: _('Dec')}

# Valid input types for dependent variable
types_var_D = ['PPT', 'NDPPT', 'TMIN', 'TMAX', 'TEMP', 'PATM', 'RH', 'RUNOFF']

# Units for types for dependent variable
units_of_types_var_D = {'PPT':'mm', 'NDPPT':'#', 'TMIN':'Celsius', 'TMAX':'Celsius', 'TEMP':'Celsius',
                        'PATM':'mb', 'RH':'%', 'RUNOFF':'m^3/s'}

# Valid input types for independent variable
types_var_I = ['ONI', 'SOI', 'MEI', 'OLR', 'W200', 'SST', 'ARH', 'QBO', 'NAO', 'SSTA_CAR', 'AREA_WHWP']

# Units for types for dependent variable
units_of_types_var_I = {'ONI':'anomaly', 'SOI':'standardized anomaly', 'MEI':'#', 'OLR':'W/m2', 'W200':'standardized anomaly',
                        'SST':'Celsius', 'ARH':'%', 'QBO':'Km/h', 'NAO':'anomaly', 'SSTA_CAR':'Celsius', 'AREA_WHWP':'scaled 10e6 km^2'}

# types of internal variable independent
internal_var_I_types = ["ONI", "SOI", "MEI", "OLR", "W200", "SST", "ARH", "NAO", "QBO", "SSTA_CAR", "AREA_WHWP"]

# namefiles of internal variable independent
internal_var_I_files = {"ONI": "ONI_1950_2011_CPC.txt",
                        "SOI": "SOI_1951_2011_CPC_NOAA.txt",
                        "MEI": "MEI_1950_2011_ESRL_NOAA.txt",
                        "OLR": "OLR_1974_2011_CPC_NCEP_NOAA.txt",
                        "W200": "W200_1979_2011_CPC_NCEP_NOAA.txt",
                        "SST": "SST_1950_2011_CPC_NCEP_NOAA.txt",
                        #"ARH": "????",  #TODO:
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
                        #"ARH": "????",  #TODO:
                        "NAO": "http://goo.gl/1uDjY", # http://www.cpc.ncep.noaa.gov/products/precip/CWlink/pna/nao.shtml
                        "QBO": "http://goo.gl/UO6PX", # http://www.esrl.noaa.gov/psd/data/climateindices/list/
                        "SSTA_CAR": "http://goo.gl/BsAeN", # http://www.esrl.noaa.gov/psd/forecasts/sstlim/forcar.html
                        "AREA_WHWP": "http://goo.gl/mV4QI"  # http://www.esrl.noaa.gov/psd/data/correlation/whwp.data 
                        }

# analysis_interval
options_analysis_interval = ["5days", "10days", "15days", "trimester"]
translate_analysis_interval = [_("5days"), _("10days"), _("15days"), _("trimester")]

# maps files for climate:
maps_files_climate = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for correlation:
maps_files_correlation = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for forecasting:
maps_files_forecasting = {'5days': {}, '10days': {}, '15days': {}, 'trimester': {}}

# phenomenon based on arguments or not, start with default value
phenomenon_below = None
phenomenon_normal = None
phenomenon_above = None

# configuration run reade and set from runfile
config_run = {'data_analysis': None,
              'climate_process': None,
              'forecasting_process': None,
              'process_period': None,
              'analog_year': None,
              'lags': None,
              'language': None,
              'type_var_D': None,
              'limit_var_D_below': None,
              'limit_var_D_above': None,
              'type_var_I': None,
              'limit_var_I_below': None,
              'limit_var_I_above': None,
              'consistent_data': None,
              'risk_analysis': None,
              'graphics': None,
              'phen_below_label': None,
              'phen_normal_label': None,
              'phen_above_label': None,
              'maps': None,
              'overlapping': None,
              "shape_boundary": None}

# globals variable for defined lags, lags = [ 0, 1 and/or 2 ]
lags = []

climate_dir = None

forecasting_dir = None

data_analysis_dir = None

# defined, after read runfile configuration, what run
maps = {'climate': False, 'forecasting': False, 'correlation': False}

# threshold_problem is global variable for detect problem with
# threshold of independent variable, if a problem is detected
# show message and print "nan" (this mean null value for
# division by zero) in contingency tabla percent in result
# table, jaziku continue but the graphics will not be created
# because "nan"  character could not be calculate.
threshold_problem = [False, False, False]

