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

    # enable/disable data analysis process
    #   values: boolean
    'data_analysis',

    # enable/disable climate process
    #   values: boolean
    'climate_process',

    # enable/disable forecasting process
    #   values: boolean
    'forecasting_process',

    # analysis interval for process
    #   values: "5days", "10days", "15days" or "trimester"
    'analysis_interval',

    # start-end period to process
    #   values: {'start': int, 'end': int}
    'process_period',

    # process with analog year
    #   values: int
    'analog_year',

    # lags for process
    #   values: [0, 1 and/or 2]
    'lags',

    # languages
    #   values: string (e.g 'es', 'en')
    'language',

    # type for dependence variable
    #   values: string
    'type_var_D',

    # limit by below for dependence variable
    #   values: 'default', none or float
    'limit_var_D_below',

    # limit by above for dependence variable
    #   values: 'default', none or float
    'limit_var_D_above',

    # threshold by below for dependence variable
    #   values: 'default', pNN, sdN or float
    'threshold_below_var_D',

    # threshold by above for dependence variable
    #   values: 'default', pNN, sdN or float
    'threshold_above_var_D',

    # type for independence variable
    #   values: string
    'type_var_I',

    # path
    #   values: string
    'path_to_file_var_I',

    # limit by below for independence variable
    #   values: 'default', none or float
    'limit_var_I_below',

    # limit by above for independence variable
    #   values: 'default', none or float
    'limit_var_I_above',

    # threshold by below for independence variable
    #   values: 'default', pNN, sdN or float
    'threshold_below_var_I',

    # threshold by above for independence variable
    #   values: 'default', pNN, sdN or float
    'threshold_above_var_I',

    # check consistent data
    #   values: boolean
    'consistent_data',

    # do or not risk analysis
    #   values: boolean
    'risk_analysis',

    # do or not graphics
    #   values: boolean
    'graphics',

    # label phenomenon
    #   values: string
    'phen_below_label',
    'phen_normal_label',
    'phen_above_label',

    # 9 values for forecasting
    #   values: float
    'lag_0_phen_below',
    'lag_0_phen_normal',
    'lag_0_phen_above',
    'lag_1_phen_below',
    'lag_1_phen_normal',
    'lag_1_phen_above',
    'lag_2_phen_below',
    'lag_2_phen_normal',
    'lag_2_phen_above',

    # date for forecasting
    #   values: string
    'forecasting_date',

    # defined, after read runfile configuration, what run
    #   values: {'climate': boolean, 'forecasting': boolean, 'correlation': boolean}
    'maps',

    # put marks of stations in maps
    #   values: boolean (disable, enable or default)
    'marks_stations',

    # set overlapping solution when jaziku make interpolation for maps
    #   values: default, average, maximum, minimum or neither
    'overlapping',

    # set if jaziku cut boundary of shape in maps
    #   values: boolean (disable, enable or default)
    "shape_boundary"
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
