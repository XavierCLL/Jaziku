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


#class Config(object):
#
#    def __init__(self, name):
#        self._name = name
#        self._value = None
#
#    def __str__(self):
#        return self._value
#
#    @property
#    def value(self):
#        return self._value
#
#    @value.setter
#    def value(self, value):
#        print "calling setter"
#        self._value = value


#==============================================================================
# settings and list_of_all_settings is global configuration settings (and are
# not particulars by station) for run Jaziku based on runfile and after reset
# and check in settings_to_run functions

# save all variable of configuration run settings
global settings
settings = {}

# all settings variables
list_of_all_settings = [

    ## MODULES

    # enable/disable data analysis process
    #   input: boolean (disable, enable)
    'data_analysis',

    # enable/disable climate process
    #   input: boolean (disable, enable)
    'climate_process',

    # enable/disable forecast process
    #   input: boolean (disable, enable)
    'forecast_process',

    ## GENERAL OPTIONS

    # analysis interval for process
    #   input/access: "5days", "10days", "15days" or "trimester"
    'analysis_interval',

    # defines how many categories to process
    #   input: int (3 or 7)
    'class_category_analysis',

    # start-end period to process
    #   input: maximum, yyyy-yyyy
    #   values: {'start': int, 'end': int}
    'process_period',

    # process with analog year
    #   input: yyyy
    'analog_year',

    # lags for process
    #   input: 0, 1 or 2 or combining of them
    'lags',

    # languages
    #   input: default, string (e.g 'es', 'en')
    'language',

    ## CHECK OPTIONS

    # check consistent data
    #   input: boolean (disable, enable)
    'consistent_data',

    # do or not risk analysis
    #   input: boolean (disable, enable)
    'risk_analysis',

    ## OUTPUT OPTIONS

    # do or not graphics
    #   input: boolean (disable, enable)
    'graphics',

    # defined, after read runfile configuration, what run
    #   input: ('climate', 'forecast', 'correlation') or combining of them
    #   access: {'climate': boolean, 'forecast': boolean, 'correlation': boolean}
    'maps',

    # labels for all categories for independent variable
    # the number of input labels depend of class_category_analysis, thus:
    # if is 3 categories should be 3 labels
    # if is 7 categories should be 7 labels
    #   input: string or 'default'
    #   access: {'below','normal','above'} or {'below3','below2','below1','normal','above1','above2','above3'}
    'var_I_category_labels',

    ## VAR D OPTIONS

    # type for dependence variable (jaziku used this only input, USE: env.var_D.TYPE_SERIES)
    #   input: string
    'type_var_D',

    # this is the mode of series calculation
    #   input: 'default', 'totalize', 'mean'
    'calculation_mode_series_D',

    # limits below and above for dependence variable
    #   input: 'default', none or float (below; above)
    #   access: {'below','above'}
    'limits_var_D',

    # threshold for dependence variable
    # the number of input values depend of class_category_analysis, thus:
    # if is 3 categories should be 2 thresholds
    # if is 7 categories should be 6 thresholds
    #   input: 'default', pNN, sdN or float
    #      float: (below;above) or (below3;below2;below1;above1;above2;above3)
    #   access: {'below','above'} or {'below3','below2','below1','above1','above2','above3'}
    'thresholds_var_D',

    ## VAR I OPTIONS

    # type for independence variable (jaziku used this only input, USE: env.var_I.TYPE_SERIES)
    #   input: string
    'type_var_I',

    # this is the mode of series calculation
    #   input: 'default', 'totalize', 'mean'
    'calculation_mode_series_I',

    # path
    #   input: string or 'internal'
    'path_to_file_var_I',

    # limits below and above for independence variable
    #   input: 'default', none or float (below; above)
    #   access: {'below','above'}
    'limits_var_I',

    # threshold for independence variable
    # the number of input values depend of class_category_analysis, thus:
    # if is 3 categories should be 2 thresholds
    # if is 7 categories should be 6 thresholds
    #   input: 'default', pNN, sdN or float
    #      float: (below;above) or (below3;below2;below1;above1;above2;above3)
    #   access: {'below','above'} or {'below3','below2','below1','above1','above2','above3'}
    'thresholds_var_I',

    ## FORECAST OPTIONS

    # date for forecast
    #   input: month or month;day
    #   access: {'month': int, 'day': int, 'text':str} or {'month': int, 'text':str}
    'forecast_date',

    # values for forecast process
    #   input: (float, float, float)
    #   access: {'below','normal','above'} or {'below3','below2','below1','normal','above1','above2','above3'}
    'forecast_var_I_lag_0',
    'forecast_var_I_lag_1',
    'forecast_var_I_lag_2',

    ## MAPS OPTIONS

    # set overlapping solution when jaziku make interpolation for maps
    #   input: default, average, maximum, minimum or neither
    'overlapping',

    # set if jaziku cut boundary of shape in maps
    #   input: boolean (disable, enable or default)
    "shape_boundary",

    # put marks of stations in maps
    #   input: boolean (disable, enable or default)
    'marks_stations'
]

def init():
    """
    Initialize all settings variables in None
    """
    for settings_item in list_of_all_settings:
        settings[settings_item] = None


#def gett(config_name):
#    return all[config_name].value
#
#def set(config_name, value):
#    if config_name in settings:
#        all[config_name].value = value
#    else:
#        raise ValueError("not in standard configurations")
