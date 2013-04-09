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

from jaziku.env import config_run

#==============================================================================
# types and units for internal VAR D

# globals vars for all var I
TYPE_SERIES = None
FREQUENCY_DATA = None

# Valid input types for dependent variable, known for jaziku
INTERNAL_TYPES = [
    'PPT',          # precipitation
    'NDPPT',        # number of days with rain
    'TMIN',         # minimum temperature
    'TMAX',         # maximum temperature
    'TEMP',         # medium temperature
    'PATM',         # atmosphere pressure
    'RH',           # % of relative humidity
    'RUNOFF'        # Runoff
]

# Units for types of dependent variable, known for jaziku
INTERNAL_UNITS = {
    'PPT':          'mm',
    'NDPPT':        '#',
    'TMIN':         'Celsius',
    'TMAX':         'Celsius',
    'TEMP':         'Celsius',
    'PATM':         'mb',
    'RH':           '%',
    'RUNOFF':       'm^3/s'
}

# available mode calculation series for internal dependent variable
# the fist element is by default (options: ['mean', 'accumulate'],)
MODE_CALCULATION_SERIES = {
    'PPT':          ['mean', 'accumulate'],
    'NDPPT':        ['mean', 'accumulate'],
    'TMIN':         ['mean'],
    'TMAX':         ['mean'],
    'TEMP':         ['mean'],
    'PATM':         ['mean'],
    'RH':           ['mean'],
    'RUNOFF':       ['mean'],
}

# variable use for set units for var D, known and unknown for jaziku
# for particular units set it in runfile, please read jaziku's manual
units = None

# Internal limits for var_D (dependent variable)
#
# If inputs are monthly:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=3500mm
#  Num. of days
#   with rain------------NDPPT        -     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=50°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=50°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=50°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          -                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300
#
# If inputs are daily:
#
#     Variable        Abbreviation   Units          Range of variation
#  Precipitation----------PPT         mm             0mm<=Ppt<=200mm
#  Num. of days
#   with rain------------NDPPT        #     (0 or num of days valid for month/year)
#  Temp. min-------------TMIN        °C             -15°C<=Tmin<=22°C
#  Temp. max-------------TMAX        °C             -15°C<=Tmin<=34°C
#  Temp. medium----------TEMP        °C             -15°C<=Tmin<=34°C
#  Atmosfere pressure----PATM        mb              400mb<=P<=1100mb
#  % relative humidity----RH          %                0%<=RH<=100%
#  Runoff---------------RUNOFF      m^3/s                0 to 3300

INTERNAL_LIMITS = {
    'PPT':          {'daily':   [0,200],       'monthly': [0,3500]},
    'NDPPT':        {'daily':   None,          'monthly': [0,31]},
    'TMIN':         {'daily':   [-15,22],      'monthly': [-15,50]},
    'TMAX':         {'daily':   [-15,34],      'monthly': [-15,50]},
    'TEMP':         {'daily':   [-15,34],      'monthly': [-15,50]},
    'PATM':         {'daily':   [400,1100],    'monthly': [400,1100]},
    'RH':           {'daily':   [0,100],       'monthly': [0,100]},
    'RUNOFF':       {'daily':   [0,3300],      'monthly': [0,3300]},
}

# When the 'normal_inclusive' is True this mean that for the normal values the thresholds
# are inclusive:
#
# if 'normal_inclusive' == True:
#   threshold_below* <= normal <= threshold_above*
# if 'normal_inclusive' == False:
#   threshold_below* < normal < threshold_above*

# thresholds when class_category_analysis is 3
THRESHOLDS_3_CATEGORIES = {
    ## thresholds by default
    'default':      {'daily': ['p33','p66'], 'monthly': ['p33','p66'], 'normal_inclusive': True},
    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'TMIN':         {'daily': [-1,1], 'monthly': [-1,1], 'normal_inclusive': True},
    'TMAX':         {'daily': [-1,1], 'monthly': [-1,1], 'normal_inclusive': True},
    'TEMP':         {'daily': [-1,1], 'monthly': [-1,1], 'normal_inclusive': True},
}

# thresholds when class_category_analysis is 7
THRESHOLDS_7_CATEGORIES = {
    ## thresholds by default
    'default':      {'daily': ['p11','p22','p33','p66','p77','p88'], 'monthly': ['p11','p22','p33','p66','p77','p88'], 'normal_inclusive': True},
    ## thresholds by type of internal series  (if was not defined here, will use thresholds by default)
    'PPT':          {'daily': ['30%','60%','90%','110%','140%','170%'], 'monthly': ['30%','60%','90%','110%','140%','170%'], 'normal_inclusive': True},
    'TMIN':         {'daily': [-2,-1.5,-1,1,1.5,2], 'monthly': [-2,-1.5,-1,1,1.5,2], 'normal_inclusive': True},
    'TMAX':         {'daily': [-2,-1.5,-1,1,1.5,2], 'monthly': [-2,-1.5,-1,1,1.5,2], 'normal_inclusive': True},
    'TEMP':         {'daily': [-2,-1.5,-1,1,1.5,2], 'monthly': [-2,-1.5,-1,1,1.5,2], 'normal_inclusive': True},
}


#==============================================================================
# functions

def get_internal_limits():
    global FREQUENCY_DATA
    global TYPE_SERIES

    if TYPE_SERIES in INTERNAL_LIMITS:
        return INTERNAL_LIMITS[TYPE_SERIES][FREQUENCY_DATA]
    else:
        return [None,None]

def get_default_thresholds():
    from jaziku.env import config_run
    global FREQUENCY_DATA
    global TYPE_SERIES

    thresholds_by_category = {3:THRESHOLDS_3_CATEGORIES,
                              7:THRESHOLDS_7_CATEGORIES}

    THRESHOLDS = thresholds_by_category[config_run.settings['class_category_analysis']]

    if TYPE_SERIES in THRESHOLDS and \
       THRESHOLDS[TYPE_SERIES][FREQUENCY_DATA] != 'default':
        return THRESHOLDS[TYPE_SERIES][FREQUENCY_DATA]
    else:
        return THRESHOLDS['default'][FREQUENCY_DATA]

def is_daily():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'daily':
        return True
    else:
        return False

def is_monthly():
    global FREQUENCY_DATA
    if FREQUENCY_DATA == 'monthly':
        return True
    else:
        return False

def is_normal_inclusive():
    global TYPE_SERIES
    from jaziku.env import config_run

    if TYPE_SERIES in INTERNAL_LIMITS:
        if config_run.settings['class_category_analysis'] == 3:
            return THRESHOLDS_3_CATEGORIES[TYPE_SERIES]['normal_inclusive']
        if config_run.settings['class_category_analysis'] == 7:
            return THRESHOLDS_7_CATEGORIES[TYPE_SERIES]['normal_inclusive']
    else:
        return True # default case when the type series is particular

def set_FREQUENCY_DATA(new_freq_data, check=True):
    global FREQUENCY_DATA
    global TYPE_SERIES

    if new_freq_data not in ['daily','monthly']:
        raise

    if FREQUENCY_DATA is None or check is False:
        FREQUENCY_DATA = new_freq_data
    else:
        if not FREQUENCY_DATA == new_freq_data:
            raise ValueError(_("The frequency data '{0}' for the var D is different\n"
                               "for the others stations before assigned as '{2}'.\n\n"
                               "Jaziku requires that all stations for var D\n"
                               "have identical frequency data.")
            .format(new_freq_data, TYPE_SERIES, FREQUENCY_DATA))

def get_generic_labels(upper=False):
    # generic labels for var D
    LABELS_3_CATEGORIES = [_('var D below'), _('var D normal'), _('var D above')]
    LABELS_7_CATEGORIES = [_('var D strong below'), _('var D moderate below'), _('var D weak below'), _('var D normal'),
                           _('var D weak above'), _('var D moderate above'), _('var D strong above')]

    if config_run.settings['class_category_analysis'] == 3:
        if upper:
            return [label.upper() for label in LABELS_3_CATEGORIES]
        else:
            return LABELS_3_CATEGORIES
    if config_run.settings['class_category_analysis'] == 7:
        if upper:
            return [label.upper() for label in LABELS_7_CATEGORIES]
        else:
            return LABELS_7_CATEGORIES