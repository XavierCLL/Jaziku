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

from math import isnan

#==============================================================================
# GLOBAL VARIABLES AND FUNCTIONS
#==============================================================================

#==============================================================================
# general

PROG_NAME = "jaziku"

VERSION = "0.6.0"

VERSION_DATE = "10/03/2013"

# absolute directory where is installed Jaziku in your system,
# this variable is set in jaziku.py
JAZIKU_DIR = None

# accuracy of number decimal places, only for print result
ACCURACY = 4

#==============================================================================
# arguments, inputs and outputs

# delimiter for inputs and outputs
INPUT_CSV_DELIMITER = ";"
OUTPUT_CSV_DELIMITER = ";"

# run arguments
ARGS = None

# absolute directory to save all result,
# this is absolute directory where is the runfile + filename of runfile,
# this variable is set in jaziku.py
WORK_DIR = None

#==============================================================================
# valid nulls

VALID_NULL = [99999, -99999]  # these are deprecate valid null but now used for maps files interpolation

def is_valid_null(value):
    """
    Check if value is a valid null value for variables dependent and independent (inside files input)

    return True if value is: 'nan', 'NaN', 'NAN', float('nan'), (deprecate: 99999, -99999)
    else return False
    """

    if value in ['nan', 'NaN', 'NAN']:
        return True
    else:
        try:
            if int(float(value)) in VALID_NULL: # TODO: delete deprecated valid null
                return True
            if isnan(value):
                return True
        except:
            return False
    return False

#==============================================================================
# analysis_interval
ALL_ANALYSIS_INTERVALS = ["5days", "10days", "15days", "trimester"]
NUM_DAYS_OF_ANALYSIS_INTERVAL = None
analysis_interval_i18n = None

STATE_OF_DATA = None

#==============================================================================
# generic labels

def generic_labels(key_label=False):
    from jaziku.env.config_run import settings
    if settings['class_category_analysis'] == 3:
        labels = {'below':_(u'below'),
                  'normal':_(u'normal'),
                  'above':_(u'above')}
    if settings['class_category_analysis'] == 7:
        labels = {'below3':_(u'strong below'),
                  'below2':_(u'moderate below'),
                  'below1':_(u'weak below'),
                  'normal':_(u'normal'),
                  'above1':_(u'weak above'),
                  'above2':_(u'moderate above'),
                  'above3':_(u'strong above')}
    if key_label is False:
        return labels

    if key_label in labels:
        return labels[key_label]

    return None

#==============================================================================
# maps #TODO: is now static fix it!

# maps files for climate:
maps_files_climate = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for correlation:
maps_files_correlation = {'5days': None, '10days': None, '15days': None, 'trimester': None}
# maps files for forecast:
maps_files_forecast = {'5days': {}, '10days': {}, '15days': {}, 'trimester': {}}

#==============================================================================
# graphics properties

def graphs_axis_properties(afs=15, ma='center'):
    axis_properties = {}
    axis_properties["fontsize"] = afs
    axis_properties["multialignment"] = ma
    return axis_properties

def graphs_title_properties(tfs=18, ma='center'):
    title_properties = {}
    title_properties["fontsize"] = tfs
    title_properties["multialignment"] = ma
    return title_properties


#==============================================================================
# settings to run, this si a global variable of 'settings' inside of settings_to_run
input_settings = {}

#==============================================================================
# globals variable for defined lags, lags = [ 0, 1 and/or 2 ]
ALL_LAGS = [0, 1, 2]

#==============================================================================
# globals directories

CLIMATE_DIR = None

FORECAST_DIR = None

DATA_ANALYSIS_DIR = None

#==============================================================================
# threshold_problem is global variable for detect problem with
# threshold of independent variable, if a problem is detected
# show message and print "nan" (this mean null value for
# division by zero) in contingency tabla percent in result
# table, jaziku continue but the graphics will not be created
# because "nan"  character could not be calculate.
threshold_problem = []

#==============================================================================
# this is the forecast_contingency_table for forecast process
# type = '3x3' '3x7' '7x7'

forecast_contingency_table = {'type': None}